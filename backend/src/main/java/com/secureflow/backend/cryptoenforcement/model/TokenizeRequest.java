package com.secureflow.backend.cryptoenforcement.model;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TokenizeRequest {

    @NotBlank(message = "Sensitive value is required")
    private String sensitiveValue;

    private String entityType;

    private String requestedBy;
}
