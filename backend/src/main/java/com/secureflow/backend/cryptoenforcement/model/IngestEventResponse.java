package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

import java.util.List;
import java.util.Map;

/**
 * Universal Ingestion Response Contract returning inline enforcement decisions,
 * threat explanations, and regulatory compliance mapping.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IngestEventResponse {
    private String eventId;
    private String status;
    private Integer riskScore;
    private String actionTaken;
    private String tier;
    private String sanitizedContent;
    private List<String> flags;
    private Integer entityCount;
    private String threatCategory;
    private String explanation;
    private List<String> complianceImpact;
    private String remediationAdvice;
    private Double latencyMs;
    private Map<String, Object> latencyBreakdown;

    // Explicit Getters and Setters for IDE resilience
    public String getEventId() { return eventId; }
    public void setEventId(String eventId) { this.eventId = eventId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public String getActionTaken() { return actionTaken; }
    public void setActionTaken(String actionTaken) { this.actionTaken = actionTaken; }

    public String getTier() { return tier; }
    public void setTier(String tier) { this.tier = tier; }

    public String getSanitizedContent() { return sanitizedContent; }
    public void setSanitizedContent(String sanitizedContent) { this.sanitizedContent = sanitizedContent; }

    public List<String> getFlags() { return flags; }
    public void setFlags(List<String> flags) { this.flags = flags; }

    public Integer getEntityCount() { return entityCount; }
    public void setEntityCount(Integer entityCount) { this.entityCount = entityCount; }

    public String getThreatCategory() { return threatCategory; }
    public void setThreatCategory(String threatCategory) { this.threatCategory = threatCategory; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public List<String> getComplianceImpact() { return complianceImpact; }
    public void setComplianceImpact(List<String> complianceImpact) { this.complianceImpact = complianceImpact; }

    public String getRemediationAdvice() { return remediationAdvice; }
    public void setRemediationAdvice(String remediationAdvice) { this.remediationAdvice = remediationAdvice; }

    public Double getLatencyMs() { return latencyMs; }
    public void setLatencyMs(Double latencyMs) { this.latencyMs = latencyMs; }

    public Map<String, Object> getLatencyBreakdown() { return latencyBreakdown; }
    public void setLatencyBreakdown(Map<String, Object> latencyBreakdown) { this.latencyBreakdown = latencyBreakdown; }
}
