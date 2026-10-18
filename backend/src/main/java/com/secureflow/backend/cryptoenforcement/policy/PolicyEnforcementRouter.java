package com.secureflow.backend.cryptoenforcement.policy;

import com.secureflow.backend.cryptoenforcement.model.EnforcementAction;
import com.secureflow.backend.cryptoenforcement.model.SecurityPolicy;
import com.secureflow.backend.cryptoenforcement.repository.SecurityPolicyRepository;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

/**
 * Module 4: The Dynamic Policy & Enforcement Router
 * (The Intelligent Traffic Controller)
 *
 * Implements high-speed (<2ms) in-memory cached policy evaluation following a strict priority checklist:
 * 1. Check Destination Whitelist (approved financial partners like @visa.com, @mastercard.com)
 * 2. Check Risk Score Brackets:
 *    - 80 to 100: BLOCK (Critical Threat, Kill transfer, Alert SOC)
 *    - 45 to 79: REMEDIATE (Medium Risk: Mask or Encrypt/Tokenize)
 *    - 0 to 44: ALLOW (Safe / Low Risk, Pass through untouched)
 */
@Slf4j
@Component
public class PolicyEnforcementRouter {

    private final SecurityPolicyRepository policyRepository;

    private final AtomicReference<SecurityPolicy> activePolicyCache = new AtomicReference<>();
    private final AtomicReference<Set<String>> whitelistedDomainsCache = new AtomicReference<>(Collections.emptySet());
    private final java.util.concurrent.atomic.AtomicLong totalPolicyEvaluations = new java.util.concurrent.atomic.AtomicLong(0);

    public PolicyEnforcementRouter(SecurityPolicyRepository policyRepository) {
        this.policyRepository = policyRepository;
    }

    public long getTotalPolicyEvaluations() {
        return totalPolicyEvaluations.get();
    }

    public record PolicyDecision(
            EnforcementAction action,
            boolean isWhitelistedDestination,
            String policyName,
            String rationale
    ) {}

    @PostConstruct
    public void init() {
        refreshCache();
    }

    /**
     * Refreshes the in-memory policy cache from PostgreSQL once every 60 seconds.
     * Guarantees blazing-fast in-memory evaluations (<2ms) without database I/O overhead.
     */
    @Scheduled(fixedRate = 60000)
    public void scheduledCacheRefresh() {
        refreshCache();
    }

    public synchronized void refreshCache() {
        try {
            Optional<SecurityPolicy> latest = policyRepository.findFirstByIsActiveTrueOrderByUpdatedAtDesc();
            SecurityPolicy policy;
            if (latest.isPresent()) {
                policy = latest.get();
            } else {
                // Fallback default policy if database is empty
                policy = SecurityPolicy.builder()
                        .name("Default Banking DLP Policy")
                        .blockThreshold(80)
                        .remediateThreshold(45)
                        .allowThreshold(0)
                        .whitelistedDomains("@visa.com,@mastercard.com,clearinghouse.bank.org,swift.com")
                        .defaultRemediationAction(EnforcementAction.MASK)
                        .isActive(true)
                        .updatedAt(Instant.now())
                        .build();
                policy = policyRepository.save(policy);
            }

            activePolicyCache.set(policy);
            whitelistedDomainsCache.set(parseWhitelistedDomains(policy.getWhitelistedDomains()));
            log.debug("Policy cache refreshed successfully: {}", policy.getName());
        } catch (Exception e) {
            log.warn("Could not refresh policy cache from DB, using fallback: {}", e.getMessage());
            if (activePolicyCache.get() == null) {
                SecurityPolicy fallback = SecurityPolicy.builder()
                        .name("Emergency Fallback Policy")
                        .blockThreshold(80)
                        .remediateThreshold(45)
                        .allowThreshold(0)
                        .whitelistedDomains("@visa.com,@mastercard.com,clearinghouse.bank.org,swift.com")
                        .defaultRemediationAction(EnforcementAction.MASK)
                        .isActive(true)
                        .updatedAt(Instant.now())
                        .build();
                activePolicyCache.set(fallback);
                whitelistedDomainsCache.set(parseWhitelistedDomains(fallback.getWhitelistedDomains()));
            }
        }
    }

    /**
     * Core decision router executing the banking priority checklist.
     */
    public PolicyDecision evaluate(int riskScore, String destination, EnforcementAction preferredRemediation) {
        totalPolicyEvaluations.incrementAndGet();
        SecurityPolicy policy = activePolicyCache.get();
        if (policy == null) {
            refreshCache();
            policy = activePolicyCache.get();
        }

        // Check 1: Destination Whitelist Check
        boolean isWhitelisted = isDestinationWhitelisted(destination);
        if (isWhitelisted) {
            // Approved clearinghouse or business partner:
            // Route to secure encrypted channel or allow with audit logging rather than hard block
            EnforcementAction action = (riskScore >= policy.getBlockThreshold())
                    ? EnforcementAction.ENCRYPT
                    : (riskScore >= policy.getRemediateThreshold() ? EnforcementAction.MASK : EnforcementAction.ALLOW);

            return new PolicyDecision(
                    action,
                    true,
                    policy.getName(),
                    "Destination is in approved partner whitelist (" + destination + "). Routed to secure channel."
            );
        }

        // Check 2: Risk Score Brackets Check
        if (riskScore >= policy.getBlockThreshold()) {
            return new PolicyDecision(
                    EnforcementAction.BLOCK,
                    false,
                    policy.getName(),
                    "Critical threat (Risk Score: " + riskScore + " >= " + policy.getBlockThreshold() + "). Transfer BLOCKED. SOC alerted."
            );
        } else if (riskScore >= policy.getRemediateThreshold()) {
            EnforcementAction remediation = preferredRemediation != null
                    ? preferredRemediation
                    : policy.getDefaultRemediationAction();

            return new PolicyDecision(
                    remediation,
                    false,
                    policy.getName(),
                    "Medium risk (Risk Score: " + riskScore + "). Remediated via " + remediation + "."
            );
        } else {
            return new PolicyDecision(
                    EnforcementAction.ALLOW,
                    false,
                    policy.getName(),
                    "Low risk (Risk Score: " + riskScore + "). Transfer ALLOWED."
            );
        }
    }

    public boolean isDestinationWhitelisted(String destination) {
        if (destination == null || destination.trim().isEmpty()) {
            return false;
        }

        String destLower = destination.trim().toLowerCase(Locale.ROOT);
        Set<String> whitelist = whitelistedDomainsCache.get();
        if (whitelist == null || whitelist.isEmpty()) {
            return false;
        }

        for (String entry : whitelist) {
            if (entry.startsWith("@")) {
                if (destLower.endsWith(entry)) return true;
            } else if (destLower.contains(entry)) {
                return true;
            }
        }

        return false;
    }

    private Set<String> parseWhitelistedDomains(String raw) {
        if (raw == null || raw.trim().isEmpty()) {
            return Collections.emptySet();
        }
        return Arrays.stream(raw.split(","))
                .map(String::trim)
                .map(s -> s.toLowerCase(Locale.ROOT))
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toUnmodifiableSet());
    }

    public SecurityPolicy getActivePolicy() {
        return activePolicyCache.get();
    }
}
