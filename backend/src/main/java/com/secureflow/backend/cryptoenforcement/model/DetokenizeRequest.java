package com.secureflow.backend.cryptoenforcement.model;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DetokenizeRequest {

    @NotBlank(message = "Token ID is required")
    private String tokenId;

    @NotBlank(message = "Requester identity is required")
    private String requester;

    /**
     * RBAC role of the caller.
     * Allowed roles: ROLE_COMPLIANCE_OFFICER, ROLE_ADMIN, ROLE_SECURITY_OFFICER
     */
    private String role;
}
