package com.secureflow.backend.cryptoenforcement.service;

import com.secureflow.backend.cryptoenforcement.audit.AsyncAuditPipeline;
import com.secureflow.backend.cryptoenforcement.crypto.CryptographicSubsystem;
import com.secureflow.backend.cryptoenforcement.masking.OffsetSafeMaskingEngine;
import com.secureflow.backend.cryptoenforcement.model.*;
import com.secureflow.backend.cryptoenforcement.policy.PolicyEnforcementRouter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Layer 4: Data & Cryptography Master Architecture
 * System Module: crypto-enforcement
 *
 * Master Orchestrator coordinating all 5 engineering modules:
 * - Module 1: The PostgreSQL Data Vault & Storage Architecture
 * - Module 2: The Offset-Safe Text Masking Engine
 * - Module 3: The Cryptographic Subsystems (Tokenization & Envelope Encryption)
 * - Module 4: The Dynamic Policy & Enforcement Router
 * - Module 5: The Non-Blocking Asynchronous Audit Pipeline
 */
@Slf4j
@Service
public class CryptoEnforcementService {

    private final OffsetSafeMaskingEngine maskingEngine;
    private final CryptographicSubsystem cryptoSubsystem;
    private final PolicyEnforcementRouter policyRouter;
    private final AsyncAuditPipeline auditPipeline;

    public CryptoEnforcementService(
            OffsetSafeMaskingEngine maskingEngine,
            CryptographicSubsystem cryptoSubsystem,
            PolicyEnforcementRouter policyRouter,
            AsyncAuditPipeline auditPipeline) {
        this.maskingEngine = maskingEngine;
        this.cryptoSubsystem = cryptoSubsystem;
        this.policyRouter = policyRouter;
        this.auditPipeline = auditPipeline;
    }

    /**
     * Executes the comprehensive real-time DLP enforcement pipeline.
     * Evaluates policy, remediates sensitive data safely without offset drift,
     * hashes payload, enqueues background audit, and delivers verdict in sub-2ms.
     */
    public EnforcementResponse enforce(EnforcementRequest request) {
        long startNano = System.nanoTime();

        String rawPayload = request.getPayload() != null ? request.getPayload() : "";
        int riskScore = request.getRiskScore();
        String destination = request.getDestination() != null ? request.getDestination() : "unknown";
        String employeeId = request.getEmployeeId() != null ? request.getEmployeeId() : "ANONYMOUS";
        String application = request.getApplication() != null ? request.getApplication() : "BROWSER";
        List<EntitySpan> entities = request.getEntities() != null ? request.getEntities() : Collections.emptyList();

        // Step 1: Dynamic Policy & Enforcement Decision (Module 4)
        PolicyEnforcementRouter.PolicyDecision decision = policyRouter.evaluate(
                riskScore, destination, request.getPreferredRemediation());

        EnforcementAction action = decision.action();
        String sanitizedPayload = rawPayload;
        boolean isBlocked = false;
        boolean isRemediated = false;

        // Step 2: Enforcement Execution
        switch (action) {
            case BLOCK:
                isBlocked = true;
                sanitizedPayload = "[BLOCKED BY DATA LEAKAGE PREVENTION POLICY - CRITICAL RISK SCORE: " + riskScore + "]";
                break;

            case MASK:
                isRemediated = true;
                sanitizedPayload = maskingEngine.mask(rawPayload, entities);
                break;

            case TOKENIZE:
                isRemediated = true;
                sanitizedPayload = tokenizeEntitiesInText(rawPayload, entities, employeeId);
                break;

            case ENCRYPT:
                isRemediated = true;
                CryptographicSubsystem.EncryptedPayload enc = cryptoSubsystem.encryptWithGcm(rawPayload);
                sanitizedPayload = enc.packedPayloadBase64();
                break;

            case ALLOW:
            default:
                sanitizedPayload = rawPayload;
                break;
        }

        // Step 3: Compute SHA-256 Digital Fingerprint (Module 1 & 3)
        // Golden Rule: Never store plain-text customer data in logs.
        String payloadHash = cryptoSubsystem.computeSha256(rawPayload);

        long endNano = System.nanoTime();
        long executionTimeMs = (endNano - startNano) / 1_000_000;

        // Step 4: Construct Audit Log Record (Module 1)
        UUID auditId = UUID.randomUUID();
        String matchedSummary = entities.stream()
                .map(EntitySpan::entityType)
                .distinct()
                .collect(Collectors.joining(", "));

        DlpAuditLog auditLog = DlpAuditLog.builder()
                .id(auditId)
                .timestamp(Instant.now())
                .employeeId(employeeId)
                .application(application)
                .destination(destination)
                .riskScore(riskScore)
                .actionTaken(action)
                .payloadHash(payloadHash)
                .matchedEntities(matchedSummary)
                .executionTimeMs(executionTimeMs)
                .policyIdApplied(decision.policyName())
                .details(decision.rationale())
                .build();

        // Step 5: Asynchronous Non-Blocking Audit Enqueue (Module 5)
        // Guaranteed < 0.1ms latency without blocking response
        auditPipeline.enqueueAuditLog(auditLog);

        return EnforcementResponse.builder()
                .action(action)
                .sanitizedPayload(sanitizedPayload)
                .riskScore(riskScore)
                .isBlocked(isBlocked)
                .isRemediated(isRemediated)
                .payloadHash(payloadHash)
                .executionTimeMs(executionTimeMs)
                .matchedEntities(entities.stream().map(EntitySpan::entityType).distinct().toList())
                .auditEventId(auditId)
                .policyApplied(decision.policyName())
                .reason(decision.rationale())
                .build();
    }

    /**
     * Reversible tokenization across entity spans in text.
     * Uses reverse-order replacement to avoid offset drift.
     */
    private String tokenizeEntitiesInText(String text, List<EntitySpan> spans, String requestedBy) {
        if (text == null || text.isEmpty() || spans == null || spans.isEmpty()) {
            return text;
        }

        List<EntitySpan> sortedSpans = new ArrayList<>(spans);
        // Sort descending by start index to prevent offset drift
        sortedSpans.sort((a, b) -> Integer.compare(b.start(), a.start()));

        StringBuilder sb = new StringBuilder(text);
        int lastStart = Integer.MAX_VALUE;

        for (EntitySpan span : sortedSpans) {
            int start = Math.max(0, span.start());
            int end = Math.min(sb.length(), span.end());
            if (start >= end || end > lastStart) continue;

            String snippet = sb.substring(start, end);
            String token = cryptoSubsystem.tokenize(snippet, span.entityType(), requestedBy);
            sb.replace(start, end, token);
            lastStart = start;
        }

        return sb.toString();
    }
}
