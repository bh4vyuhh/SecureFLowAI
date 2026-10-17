package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DecryptResponse {

    private String plainText;
    private boolean authentic;
    private long executionTimeMs;
}
