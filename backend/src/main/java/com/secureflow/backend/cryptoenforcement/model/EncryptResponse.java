package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EncryptResponse {

    private String cipherText;
    private String nonce;
    private String algorithm;
    private long executionTimeMs;
}
