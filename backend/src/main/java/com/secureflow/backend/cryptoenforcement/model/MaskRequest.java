package com.secureflow.backend.cryptoenforcement.model;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MaskRequest {

    @NotBlank(message = "Text payload is required")
    private String text;

    @Builder.Default
    private List<EntitySpan> entities = new ArrayList<>();
}
