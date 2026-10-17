package com.secureflow.backend.cryptoenforcement.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

/**
 * Module 1 & 4: Security Policies Table
 * Table: security_policies
 *
 * Configurable DLP enforcement rules:
 * - Risk score thresholds: Block (80-100), Remediate (45-79), Allow (0-44)
 * - Approved partner domain whitelists (e.g., @visa.com, @mastercard.com)
 * - Allows instantaneous policy modifications without service redeployment.
 */
@Entity
@Table(name = "security_policies")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SecurityPolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false, length = 120)
    private String name;

    @Column(name = "block_threshold", nullable = false)
    @Builder.Default
    private int blockThreshold = 80;

    @Column(name = "remediate_threshold", nullable = false)
    @Builder.Default
    private int remediateThreshold = 45;

    @Column(name = "allow_threshold", nullable = false)
    @Builder.Default
    private int allowThreshold = 0;

    /**
     * Comma-separated list of whitelisted recipient domains or emails.
     * Example: "@visa.com,@mastercard.com,clearinghouse.bank.org,swift.com"
     */
    @Column(name = "whitelisted_domains", columnDefinition = "TEXT")
    @Builder.Default
    private String whitelistedDomains = "@visa.com,@mastercard.com,clearinghouse.bank.org,swift.com";

    @Enumerated(EnumType.STRING)
    @Column(name = "default_remediation_action", nullable = false, length = 32)
    @Builder.Default
    private EnforcementAction defaultRemediationAction = EnforcementAction.MASK;

    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private boolean isActive = true;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
}
