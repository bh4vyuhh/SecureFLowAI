package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MaskResponse {

    private String maskedText;
    private int replacementsCount;
    private List<String> maskedEntityTypes;
    private long executionTimeMs;
}
