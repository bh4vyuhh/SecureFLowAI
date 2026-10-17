package com.secureflow.backend.cryptoenforcement.model;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnforcementRequest {

    @NotBlank(message = "Payload content is required")
    private String payload;

    private String destination;

    private String employeeId;

    private String application;

    @Min(0)
    @Max(100)
    private int riskScore;

    @Builder.Default
    private List<EntitySpan> entities = new ArrayList<>();

    private Long policyId;

    /**
     * Optional override: if specified, force a particular remediation action
     * (e.g. MASK, ENCRYPT, TOKENIZE) when remediation threshold is met.
     */
    private EnforcementAction preferredRemediation;
}
