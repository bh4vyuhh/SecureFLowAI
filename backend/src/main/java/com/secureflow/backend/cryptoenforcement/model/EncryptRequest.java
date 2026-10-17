package com.secureflow.backend.cryptoenforcement.model;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EncryptRequest {

    @NotBlank(message = "Plaintext payload is required")
    private String plainText;

    private String keyAlias;
}
