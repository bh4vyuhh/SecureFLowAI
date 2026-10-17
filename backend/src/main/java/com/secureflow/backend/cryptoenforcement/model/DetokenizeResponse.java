package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DetokenizeResponse {

    private String tokenId;
    private String originalValue;
    private String tokenType;
    private long executionTimeMs;
}
