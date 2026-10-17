package com.secureflow.backend.cryptoenforcement.model;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DecryptRequest {

    @NotBlank(message = "Ciphertext is required")
    private String cipherText;

    private String nonce;
}
