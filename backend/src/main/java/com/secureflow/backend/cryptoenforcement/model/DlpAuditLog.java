package com.secureflow.backend.cryptoenforcement.model;

import jakarta.persistence.*;
import lombok.*;

import org.springframework.data.domain.Persistable;

import java.time.Instant;
import java.util.UUID;

/**
 * Module 1: The PostgreSQL Data Vault & Storage Architecture
 * Table: dlp_audit_logs
 *
 * Implements tamper-evident audit ledger required by PCI-DSS and GDPR.
 * Stores digital fingerprint (SHA-256) of payload without persisting raw customer plain text.
 */
@Entity
@Table(name = "dlp_audit_logs", indexes = {
        @Index(name = "idx_audit_timestamp", columnList = "timestamp"),
        @Index(name = "idx_audit_employee_id", columnList = "employee_id"),
        @Index(name = "idx_audit_action_taken", columnList = "action_taken"),
        @Index(name = "idx_audit_payload_hash", columnList = "payload_hash")
})
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DlpAuditLog implements Persistable<UUID> {

    @Id
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @Transient
    @Builder.Default
    private boolean isNewRecord = true;

    @Override
    public boolean isNew() {
        return isNewRecord;
    }

    @PostPersist
    @PostLoad
    void markNotNew() {
        this.isNewRecord = false;
    }

    @Column(name = "timestamp", nullable = false)
    private Instant timestamp;

    @Column(name = "employee_id", nullable = false, length = 120)
    private String employeeId;

    @Column(name = "application", nullable = false, length = 100)
    private String application;

    @Column(name = "destination", nullable = false, length = 255)
    private String destination;

    @Column(name = "risk_score", nullable = false)
    private Integer riskScore;

    @Enumerated(EnumType.STRING)
    @Column(name = "action_taken", nullable = false, length = 32)
    private EnforcementAction actionTaken;

    @Column(name = "payload_hash", nullable = false, length = 64)
    private String payloadHash;

    @Column(name = "matched_entities", length = 500)
    private String matchedEntities;

    @Column(name = "execution_time_ms")
    private Long executionTimeMs;

    @Column(name = "policy_id_applied", length = 100)
    private String policyIdApplied;

    @Column(name = "prev_hash", length = 128)
    private String prevHash;

    @Column(name = "audit_hash", length = 128)
    private String auditHash;

    @Column(name = "threat_category", length = 120)
    private String threatCategory;

    @Column(name = "explanation", columnDefinition = "TEXT")
    private String explanation;

    @Column(name = "compliance_tags", length = 255)
    private String complianceTags;

    @Column(name = "details", columnDefinition = "TEXT")
    private String details;
}
