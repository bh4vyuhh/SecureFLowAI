package com.secureflow.backend.cryptoenforcement.model;

import jakarta.persistence.*;
import lombok.*;

import org.springframework.data.domain.Persistable;

import java.time.Instant;
import java.util.UUID;

/**
 * Module 1 & 3: The PostgreSQL Data Vault - Token Vault Table
 * Table: token_vault
 *
 * Golden Rule of Banking Storage:
 * Never store plain-text customer data. Real credit cards, IBANs, or SSNs are always
 * strongly encrypted using AES-256-GCM with a dedicated random 12-byte Nonce prior to persistence.
 */
@Entity
@Table(name = "token_vault", indexes = {
        @Index(name = "idx_token_id", columnList = "token_id", unique = true),
        @Index(name = "idx_token_type", columnList = "token_type"),
        @Index(name = "idx_token_created_at", columnList = "created_at")
})
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TokenVault implements Persistable<UUID> {

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

    @Column(name = "token_id", nullable = false, unique = true, length = 64)
    private String tokenId;

    @Column(name = "encrypted_value", nullable = false, columnDefinition = "TEXT")
    private String encryptedValue;

    @Column(name = "iv_nonce", nullable = false, length = 64)
    private String ivNonce;

    @Column(name = "token_type", nullable = false, length = 50)
    private String tokenType;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "created_by", nullable = false, length = 120)
    private String createdBy;
}
