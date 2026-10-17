package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

import java.util.List;
import java.util.UUID;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnforcementResponse {

    private EnforcementAction action;

    private String sanitizedPayload;

    private int riskScore;

    private boolean isBlocked;

    private boolean isRemediated;

    private String payloadHash;

    private long executionTimeMs;

    private List<String> matchedEntities;

    private UUID auditEventId;

    private String policyApplied;

    private String reason;
}
