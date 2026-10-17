package com.secureflow.backend.cryptoenforcement.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * Represents a sensitive entity detected by Layer 3 (AI Engine).
 * start and end define the 0-based character offsets in the raw payload.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record EntitySpan(
        String entityType,
        int start,
        int end,
        String text
) {
    public EntitySpan {
        if (start < 0 || end < start) {
            throw new IllegalArgumentException(
                    "Invalid entity span boundaries: start=" + start + ", end=" + end);
        }
    }
}
