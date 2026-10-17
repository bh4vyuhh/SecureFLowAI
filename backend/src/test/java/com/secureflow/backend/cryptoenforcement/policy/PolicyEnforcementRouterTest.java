package com.secureflow.backend.cryptoenforcement.policy;

import com.secureflow.backend.cryptoenforcement.model.EnforcementAction;
import com.secureflow.backend.cryptoenforcement.model.SecurityPolicy;
import com.secureflow.backend.cryptoenforcement.repository.SecurityPolicyRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@DisplayName("Module 4: Dynamic Policy & Enforcement Router Tests")
class PolicyEnforcementRouterTest {

    @Mock
    private SecurityPolicyRepository policyRepository;

    private PolicyEnforcementRouter policyRouter;

    @BeforeEach
    void setUp() {
        policyRouter = new PolicyEnforcementRouter(policyRepository);

        SecurityPolicy mockPolicy = SecurityPolicy.builder()
                .id(1L)
                .name("Tier-1 Investment Banking DLP Policy")
                .blockThreshold(80)
                .remediateThreshold(45)
                .allowThreshold(0)
                .whitelistedDomains("@visa.com,@mastercard.com,clearinghouse.bank.org,swift.com")
                .defaultRemediationAction(EnforcementAction.MASK)
                .isActive(true)
                .updatedAt(Instant.now())
                .build();

        when(policyRepository.findFirstByIsActiveTrueOrderByUpdatedAtDesc())
                .thenReturn(Optional.of(mockPolicy));

        policyRouter.init();
    }

    @Test
    @DisplayName("Priority Check 1: Whitelisted Partner Destination routes to ENCRYPT or ALLOW instead of BLOCK")
    void testWhitelistedDestinationRouting() {
        // High risk score (88) to an approved clearinghouse partner @visa.com
        PolicyEnforcementRouter.PolicyDecision decision =
                policyRouter.evaluate(88, "settlement@visa.com", null);

        assertTrue(decision.isWhitelistedDestination());
        assertEquals(EnforcementAction.ENCRYPT, decision.action(),
                "High-risk transfer to approved partner must be routed to encrypted channel rather than blocked");
        assertTrue(decision.rationale().contains("approved partner whitelist"));
    }

    @Test
    @DisplayName("Priority Check 2: Risk Score 80-100 to non-whitelisted destination must BLOCK immediately")
    void testCriticalRiskScoreBlocks() {
        PolicyEnforcementRouter.PolicyDecision decision =
                policyRouter.evaluate(85, "external-leaker@gmail.com", null);

        assertFalse(decision.isWhitelistedDestination());
        assertEquals(EnforcementAction.BLOCK, decision.action());
        assertTrue(decision.rationale().contains("Critical threat"));
    }

    @Test
    @DisplayName("Priority Check 2: Risk Score 45-79 must REMEDIATE (default MASK)")
    void testMediumRiskScoreRemediates() {
        PolicyEnforcementRouter.PolicyDecision decision =
                policyRouter.evaluate(60, "vendor@consulting.com", null);

        assertFalse(decision.isWhitelistedDestination());
        assertEquals(EnforcementAction.MASK, decision.action());
    }

    @Test
    @DisplayName("Priority Check 2: Risk Score 0-44 must ALLOW untouched")
    void testLowRiskScoreAllows() {
        PolicyEnforcementRouter.PolicyDecision decision =
                policyRouter.evaluate(25, "colleague@bank.com", null);

        assertFalse(decision.isWhitelistedDestination());
        assertEquals(EnforcementAction.ALLOW, decision.action());
    }

    @Test
    @DisplayName("In-Memory Performance Check: Decision evaluates in under 2 milliseconds")
    void testSubTwoMillisecondPerformance() {
        // Warm up
        for (int i = 0; i < 100; i++) {
            policyRouter.evaluate(75, "test@external.com", null);
        }

        long start = System.nanoTime();
        policyRouter.evaluate(90, "untrusted@yahoo.com", null);
        long durationNano = System.nanoTime() - start;
        long durationMs = durationNano / 1_000_000;

        assertTrue(durationMs <= 2, "In-memory cached policy evaluation must complete in <= 2ms, was: " + durationMs + "ms");
    }
}
