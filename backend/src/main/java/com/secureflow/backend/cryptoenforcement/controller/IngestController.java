package com.secureflow.backend.cryptoenforcement.controller;

import com.secureflow.backend.cryptoenforcement.audit.AsyncAuditPipeline;
import com.secureflow.backend.cryptoenforcement.masking.OffsetSafeMaskingEngine;
import com.secureflow.backend.cryptoenforcement.model.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Tier 2 Central Ingestion Gateway Controller (Spring Boot Gateway on Port 9090)
 * ==============================================================================
 * Provides the single unified ingestion endpoint POST /api/v1/events/ingest
 * for the Browser Extension, Desktop Clipboard Agent, and Email Connector.
 *
 * Implements high-throughput asynchronous Layer 4 enforcement with zero-latency
 * queue dispatch and fallback self-sufficient checksum inspection.
 */
@Slf4j
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
public class IngestController {

    private final AsyncAuditPipeline auditPipeline;
    private final OffsetSafeMaskingEngine maskingEngine;

    public IngestController(AsyncAuditPipeline auditPipeline, OffsetSafeMaskingEngine maskingEngine) {
        this.auditPipeline = auditPipeline;
        this.maskingEngine = maskingEngine;
    }

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    private static final Pattern CARD_PATTERN = Pattern.compile("\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\\b");
    private static final Pattern API_KEY_PATTERN = Pattern.compile("(?i)(ghp_[a-zA-Z0-9]{36}|sk_live_[a-zA-Z0-9]{24,}|sec_live_[a-zA-Z0-9]{24,}|AKIA[0-9A-Z]{16})");
    private static final Pattern SSN_PATTERN = Pattern.compile("\\b(?!000|666|9\\d{2})\\d{3}[- ]?(?!00)\\d{2}[- ]?(?!0000)\\d{4}\\b");
    private static final Pattern IBAN_PATTERN = Pattern.compile("\\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\\b");

    @PostMapping("/events/ingest")
    public ResponseEntity<IngestEventResponse> ingestEvent(@RequestBody IngestEventRequest request) {
        long t0 = System.currentTimeMillis();
        String content = request.getContent() != null ? request.getContent().trim() : "";

        // 1. Fast Path: Empty Content
        if (content.isEmpty()) {
            return ResponseEntity.ok(IngestEventResponse.builder()
                    .eventId(request.getEventId())
                    .status("PROCESSED")
                    .riskScore(0)
                    .actionTaken("ALLOW")
                    .tier("SAFE")
                    .sanitizedContent("")
                    .flags(Collections.emptyList())
                    .entityCount(0)
                    .threatCategory("BENIGN_DATA")
                    .explanation("Safe transmission: empty or benign payload.")
                    .complianceImpact(List.of("SOC2-Baseline-Compliance"))
                    .remediationAdvice("No remediation needed.")
                    .latencyMs((double) (System.currentTimeMillis() - t0))
                    .build());
        }

        // 2. Try Upstream AI Microservice Bridge
        try {
            RestClient restClient = RestClient.builder().baseUrl(aiServiceUrl).build();
            IngestEventResponse aiResponse = restClient.post()
                    .uri("/api/v1/events/ingest")
                    .body(request)
                    .retrieve()
                    .body(IngestEventResponse.class);

            if (aiResponse != null) {
                // Record in Spring Boot Layer 4 Audit Pipeline
                recordAuditLog(request, aiResponse);
                return ResponseEntity.ok(aiResponse);
            }
        } catch (Exception ex) {
            log.info("AI Service at {} unreachable or busy ({}). Executing standalone Spring Boot Layer 4 Enforcement.",
                    aiServiceUrl, ex.getMessage());
        }

        // 3. Standalone Layer 4 Local Inspection & Masking
        List<EntitySpan> detectedEntities = new ArrayList<>();
        List<String> flags = new ArrayList<>();

        // Match Credit Cards
        Matcher cardMatcher = CARD_PATTERN.matcher(content);
        while (cardMatcher.find()) {
            String val = cardMatcher.group().replaceAll("[- ]", "");
            if (passesLuhn(val)) {
                detectedEntities.add(new EntitySpan("CREDIT_CARD", cardMatcher.start(), cardMatcher.end()));
                if (!flags.contains("CREDIT_CARD")) flags.add("CREDIT_CARD");
            }
        }

        // Match API Keys / Secrets
        Matcher keyMatcher = API_KEY_PATTERN.matcher(content);
        while (keyMatcher.find()) {
            detectedEntities.add(new EntitySpan("API_KEY", keyMatcher.start(), keyMatcher.end()));
            if (!flags.contains("API_KEY")) flags.add("API_KEY");
        }

        // Match SSNs
        Matcher ssnMatcher = SSN_PATTERN.matcher(content);
        while (ssnMatcher.find()) {
            detectedEntities.add(new EntitySpan("US_SSN", ssnMatcher.start(), ssnMatcher.end()));
            if (!flags.contains("US_SSN")) flags.add("US_SSN");
        }

        // Match IBANs
        Matcher ibanMatcher = IBAN_PATTERN.matcher(content);
        while (ibanMatcher.find()) {
            detectedEntities.add(new EntitySpan("IBAN", ibanMatcher.start(), ibanMatcher.end()));
            if (!flags.contains("IBAN")) flags.add("IBAN");
        }

        // 4. Policy Action Decision
        int riskScore;
        String actionTaken;
        String tier;
        String category;
        String explanation;
        List<String> compliance;
        String remediation;

        boolean hasCritical = flags.contains("CREDIT_CARD") || flags.contains("API_KEY") || flags.contains("US_SSN");
        boolean hasFinancial = flags.contains("IBAN");

        if (hasCritical) {
            riskScore = 100;
            actionTaken = "BLOCK";
            tier = "RESTRICTED";
            category = flags.contains("CREDIT_CARD") ? "PCI_DSS_PAYMENT_CARD_EXPOSURE" : "SECRET_KEY_CREDENTIAL_EXFILTRATION";
            explanation = "Critical DLP policy violation: Raw sensitive credentials intercepted. Inline BLOCK enforced.";
            compliance = List.of("PCI-DSS-v4.0-Req-3.4", "SOC2-CC6.1-Access-Control", "GDPR-Art-9");
            remediation = "Immediate quarantine enforced. Clipboard cleared on client endpoint.";
        } else if (hasFinancial) {
            riskScore = 65;
            actionTaken = "ENCRYPT";
            tier = "CONFIDENTIAL";
            category = "BANKING_WIRE_TRANSFER_COORDINATES";
            explanation = "Confidential banking account coordinates intercepted. Masking/Tokenization required.";
            compliance = List.of("SWIFT-Customer-Security-Programme", "RBI-Cyber-Security-DLP");
            remediation = "Mask wire coordinates before external transfer.";
        } else {
            riskScore = 15;
            actionTaken = "ALLOW";
            tier = "SAFE";
            category = "BENIGN_BUSINESS_DATA";
            explanation = "Verified safe communication. No sensitive payment cards or credentials detected.";
            compliance = List.of("SOC2-Baseline-Compliance");
            remediation = "Standard transfer authorized.";
        }

        // 5. Offset-Safe Masking
        String sanitizedText = detectedEntities.isEmpty() ? content : maskingEngine.mask(content, detectedEntities);
        double durationMs = (double) (System.currentTimeMillis() - t0);

        IngestEventResponse response = IngestEventResponse.builder()
                .eventId(request.getEventId())
                .status("PROCESSED")
                .riskScore(riskScore)
                .actionTaken(actionTaken)
                .tier(tier)
                .sanitizedContent(sanitizedText)
                .flags(flags)
                .entityCount(detectedEntities.size())
                .threatCategory(category)
                .explanation(explanation)
                .complianceImpact(compliance)
                .remediationAdvice(remediation)
                .latencyMs(durationMs)
                .build();

        // 6. Asynchronous Tamper-Evident Audit Logging
        recordAuditLog(request, response);

        return ResponseEntity.ok(response);
    }

    private void recordAuditLog(IngestEventRequest req, IngestEventResponse resp) {
        try {
            String payloadHash = sha256Hex(req.getContent() != null ? req.getContent() : "");
            Map<String, Object> meta = req.getMetadata() != null ? req.getMetadata() : Collections.emptyMap();
            String destination = String.valueOf(meta.getOrDefault("hostname", meta.getOrDefault("url", "external_endpoint")));
            String employeeId = String.valueOf(meta.getOrDefault("user", req.getSource() != null ? req.getSource() : "anonymous"));

            EnforcementAction actionEnum = "BLOCK".equalsIgnoreCase(resp.getActionTaken()) ? EnforcementAction.BLOCK
                    : ("ENCRYPT".equalsIgnoreCase(resp.getActionTaken()) || "MASK".equalsIgnoreCase(resp.getActionTaken()))
                    ? EnforcementAction.MASK : EnforcementAction.ALLOW;

            DlpAuditLog auditLog = DlpAuditLog.builder()
                    .id(UUID.randomUUID())
                    .timestamp(Instant.now())
                    .employeeId(employeeId)
                    .application(req.getSource() != null ? req.getSource() : "DESKTOP_CAPTURE")
                    .destination(destination)
                    .riskScore(resp.getRiskScore() != null ? resp.getRiskScore() : 0)
                    .actionTaken(actionEnum)
                    .payloadHash(payloadHash)
                    .matchedEntities(resp.getFlags() != null ? String.join(",", resp.getFlags()) : "")
                    .executionTimeMs(resp.getLatencyMs() != null ? resp.getLatencyMs().longValue() : 5L)
                    .policyIdApplied("DEFAULT_BANKING_DLP_V1")
                    .threatCategory(resp.getThreatCategory())
                    .explanation(resp.getExplanation())
                    .complianceTags(resp.getComplianceImpact() != null ? String.join(",", resp.getComplianceImpact()) : "SOC2")
                    .details("Ingestion event: " + req.getEventId())
                    .build();

            auditPipeline.enqueueAuditLog(auditLog);
        } catch (Exception e) {
            log.error("Failed to enqueue audit log in IngestController: {}", e.getMessage());
        }
    }

    private static boolean passesLuhn(String cardNum) {
        int sum = 0;
        boolean alternate = false;
        for (int i = cardNum.length() - 1; i >= 0; i--) {
            int n = Integer.parseInt(cardNum.substring(i, i + 1));
            if (alternate) {
                n *= 2;
                if (n > 9) n = (n % 10) + 1;
            }
            sum += n;
            alternate = !alternate;
        }
        return (sum % 10 == 0);
    }

    private static String sha256Hex(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return Integer.toHexString(input.hashCode());
        }
    }
}
