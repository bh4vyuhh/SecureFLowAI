package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TokenizeResponse {

    private String tokenId;
    private String tokenType;
    private boolean newlyGenerated;
    private long executionTimeMs;
}
