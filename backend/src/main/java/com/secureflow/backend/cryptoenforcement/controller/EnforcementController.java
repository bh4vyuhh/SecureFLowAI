package com.secureflow.backend.cryptoenforcement.controller;

import com.secureflow.backend.common.response.ApiResponse;
import com.secureflow.backend.cryptoenforcement.audit.AsyncAuditPipeline;
import com.secureflow.backend.cryptoenforcement.crypto.CryptographicSubsystem;
import com.secureflow.backend.cryptoenforcement.masking.OffsetSafeMaskingEngine;
import com.secureflow.backend.cryptoenforcement.model.*;
import com.secureflow.backend.cryptoenforcement.policy.PolicyEnforcementRouter;
import com.secureflow.backend.cryptoenforcement.repository.DlpAuditLogRepository;
import com.secureflow.backend.cryptoenforcement.repository.SecurityPolicyRepository;
import com.secureflow.backend.cryptoenforcement.service.CryptoEnforcementService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST API for Layer 4: Data & Cryptography Master Architecture
 * System Module: crypto-enforcement
 */
@Slf4j
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
public class EnforcementController {

    private final CryptoEnforcementService enforcementService;
    private final OffsetSafeMaskingEngine maskingEngine;
    private final CryptographicSubsystem cryptoSubsystem;
    private final PolicyEnforcementRouter policyRouter;
    private final AsyncAuditPipeline auditPipeline;
    private final DlpAuditLogRepository auditLogRepository;
    private final SecurityPolicyRepository policyRepository;

    public EnforcementController(
            CryptoEnforcementService enforcementService,
            OffsetSafeMaskingEngine maskingEngine,
            CryptographicSubsystem cryptoSubsystem,
            PolicyEnforcementRouter policyRouter,
            AsyncAuditPipeline auditPipeline,
            DlpAuditLogRepository auditLogRepository,
            SecurityPolicyRepository policyRepository) {
        this.enforcementService = enforcementService;
        this.maskingEngine = maskingEngine;
        this.cryptoSubsystem = cryptoSubsystem;
        this.policyRouter = policyRouter;
        this.auditPipeline = auditPipeline;
        this.auditLogRepository = auditLogRepository;
        this.policyRepository = policyRepository;
    }

    // =========================================================================
    // 1. Real-Time DLP Enforcement Pipeline (Module 4 & 5 Orchestrator)
    // =========================================================================

    @PostMapping("/enforcement/evaluate")
    public ResponseEntity<ApiResponse<EnforcementResponse>> evaluateEnforcement(
            @Valid @RequestBody EnforcementRequest request) {
        EnforcementResponse response = enforcementService.enforce(request);
        return ResponseEntity.ok(ApiResponse.success("Enforcement evaluation completed", response));
    }

    // =========================================================================
    // 2. Module 2: Offset-Safe Text Masking Endpoint
    // =========================================================================

    @PostMapping("/crypto/mask")
    public ResponseEntity<ApiResponse<MaskResponse>> maskText(@Valid @RequestBody MaskRequest request) {
        long start = System.currentTimeMillis();
        String masked = maskingEngine.mask(request.getText(), request.getEntities());
        long duration = System.currentTimeMillis() - start;

        List<String> entityTypes = request.getEntities().stream()
                .map(EntitySpan::entityType)
                .distinct()
                .toList();

        MaskResponse response = MaskResponse.builder()
                .maskedText(masked)
                .replacementsCount(request.getEntities().size())
                .maskedEntityTypes(entityTypes)
                .executionTimeMs(duration)
                .build();

        return ResponseEntity.ok(ApiResponse.success("Text masked safely without offset drift", response));
    }

    // =========================================================================
    // 3. Module 3: Deterministic HMAC Tokenization & Detokenization
    // =========================================================================

    @PostMapping("/crypto/tokenize")
    public ResponseEntity<ApiResponse<TokenizeResponse>> tokenizeValue(
            @Valid @RequestBody TokenizeRequest request) {
        long start = System.currentTimeMillis();
        String token = cryptoSubsystem.tokenize(
                request.getSensitiveValue(), request.getEntityType(), request.getRequestedBy());
        long duration = System.currentTimeMillis() - start;

        TokenizeResponse response = TokenizeResponse.builder()
                .tokenId(token)
                .tokenType(request.getEntityType() != null ? request.getEntityType() : "GENERIC")
                .newlyGenerated(true)
                .executionTimeMs(duration)
                .build();

        return ResponseEntity.ok(ApiResponse.success(
                "Deterministic HMAC token generated and encrypted in Data Vault", response));
    }

    @PostMapping("/crypto/detokenize")
    public ResponseEntity<ApiResponse<DetokenizeResponse>> detokenizeValue(
            @Valid @RequestBody DetokenizeRequest request) {
        long start = System.currentTimeMillis();
        String plainValue = cryptoSubsystem.detokenize(request.getTokenId(), request.getRole());
        long duration = System.currentTimeMillis() - start;

        DetokenizeResponse response = DetokenizeResponse.builder()
                .tokenId(request.getTokenId())
                .originalValue(plainValue)
                .tokenType("DETOKENIZED")
                .executionTimeMs(duration)
                .build();

        return ResponseEntity.ok(ApiResponse.success("Authorized detokenization successful", response));
    }

    // =========================================================================
    // 4. Module 3: Authenticated AES-256-GCM Envelope Encryption & Decryption
    // =========================================================================

    @PostMapping("/crypto/encrypt")
    public ResponseEntity<ApiResponse<EncryptResponse>> encryptPayload(
            @Valid @RequestBody EncryptRequest request) {
        long start = System.currentTimeMillis();
        CryptographicSubsystem.EncryptedPayload enc = cryptoSubsystem.encryptWithGcm(request.getPlainText());
        long duration = System.currentTimeMillis() - start;

        EncryptResponse response = EncryptResponse.builder()
                .cipherText(enc.packedPayloadBase64())
                .nonce(enc.nonceBase64())
                .algorithm("AES-256-GCM")
                .executionTimeMs(duration)
                .build();

        return ResponseEntity.ok(ApiResponse.success(
                "Payload encrypted with AES-256-GCM using unique 12-byte Nonce", response));
    }

    @PostMapping("/crypto/decrypt")
    public ResponseEntity<ApiResponse<DecryptResponse>> decryptPayload(
            @Valid @RequestBody DecryptRequest request) {
        long start = System.currentTimeMillis();
        String plain;
        if (request.getNonce() != null && !request.getNonce().isEmpty()) {
            plain = cryptoSubsystem.decryptWithGcm(request.getCipherText(), request.getNonce());
        } else {
            plain = cryptoSubsystem.decryptPackedPayload(request.getCipherText());
        }
        long duration = System.currentTimeMillis() - start;

        DecryptResponse response = DecryptResponse.builder()
                .plainText(plain)
                .authentic(true)
                .executionTimeMs(duration)
                .build();

        return ResponseEntity.ok(ApiResponse.success(
                "Payload decrypted and authentication tag verified successfully", response));
    }

    // =========================================================================
    // 5. Module 1 & 5: Audit Log Queries & Diagnostics
    // =========================================================================

    @GetMapping("/audit/logs")
    public ResponseEntity<ApiResponse<Page<DlpAuditLog>>> getAuditLogs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<DlpAuditLog> logs = auditLogRepository.findAllByOrderByTimestampDesc(
                PageRequest.of(page, size, Sort.by("timestamp").descending()));
        return ResponseEntity.ok(ApiResponse.success("Audit logs retrieved", logs));
    }

    @GetMapping("/audit/stats")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getAuditStats() {
        long blockedCount = auditLogRepository.countByActionTaken(EnforcementAction.BLOCK);
        long maskedCount = auditLogRepository.countByActionTaken(EnforcementAction.MASK);
        long allowedCount = auditLogRepository.countByActionTaken(EnforcementAction.ALLOW);
        long criticalCount = auditLogRepository.countByRiskScoreGreaterThanEqual(80);

        Map<String, Object> stats = Map.of(
                "totalEnqueued", auditPipeline.getTotalEnqueued(),
                "totalPersisted", auditPipeline.getTotalPersisted(),
                "currentQueueSize", auditPipeline.getQueueSize(),
                "totalDropped", auditPipeline.getTotalDropped(),
                "dbBlockedCount", blockedCount,
                "dbMaskedCount", maskedCount,
                "dbAllowedCount", allowedCount,
                "dbCriticalCount", criticalCount
        );

        return ResponseEntity.ok(ApiResponse.success("Audit pipeline telemetry retrieved", stats));
    }

    // =========================================================================
    // 6. Security Policies Management
    // =========================================================================

    @GetMapping("/policies")
    public ResponseEntity<ApiResponse<List<SecurityPolicy>>> getPolicies() {
        List<SecurityPolicy> policies = policyRepository.findAll();
        return ResponseEntity.ok(ApiResponse.success("Security policies retrieved", policies));
    }

    @PutMapping("/policies/{id}")
    public ResponseEntity<ApiResponse<SecurityPolicy>> updatePolicy(
            @PathVariable Long id, @RequestBody SecurityPolicy updated) {
        SecurityPolicy existing = policyRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Policy not found with id: " + id));

        existing.setName(updated.getName());
        existing.setBlockThreshold(updated.getBlockThreshold());
        existing.setRemediateThreshold(updated.getRemediateThreshold());
        existing.setAllowThreshold(updated.getAllowThreshold());
        existing.setWhitelistedDomains(updated.getWhitelistedDomains());
        existing.setDefaultRemediationAction(updated.getDefaultRemediationAction());
        existing.setActive(updated.isActive());
        existing.setUpdatedAt(Instant.now());

        SecurityPolicy saved = policyRepository.save(existing);
        policyRouter.refreshCache(); // Immediate cache invalidation and refresh

        return ResponseEntity.ok(ApiResponse.success("Policy updated and in-memory cache refreshed", saved));
    }

    // =========================================================================
    // 7. Objective 4: Cryptographic Audit Ledger Integrity Verification
    // =========================================================================

    @GetMapping("/audit/verify-integrity")
    public ResponseEntity<ApiResponse<Map<String, Object>>> verifyAuditIntegrity() {
        boolean valid = auditPipeline.verifyLedgerIntegrity();
        long totalRecords = auditLogRepository.count();
        Map<String, Object> report = Map.of(
                "tamperProofLedgerValid", valid,
                "totalRecordsVerified", totalRecords,
                "verificationStandard", "ISO-42001 & SOC2 Trust Services Criteria",
                "verifiedAt", Instant.now().toString(),
                "status", valid ? "VERIFIED_UNTOUCHED" : "INTEGRITY_COMPROMISED"
        );
        return ResponseEntity.ok(ApiResponse.success(
                valid ? "Cryptographic ledger integrity verified. Zero unauthorized tampering detected."
                        : "WARNING: Cryptographic ledger signature mismatch detected!", report));
    }
}
