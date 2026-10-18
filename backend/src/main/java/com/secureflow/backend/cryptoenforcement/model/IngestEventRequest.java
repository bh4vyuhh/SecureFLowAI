package com.secureflow.backend.cryptoenforcement.model;

import lombok.*;

import java.util.Map;

/**
 * Universal Ingestion Contract matching Browser Extension, Desktop Agent, and Email Connector.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IngestEventRequest {
    private String eventId;
    private String timestamp;
    private String source;
    private String eventType;
    private String content;
    private String fileName;
    private String fileBytesBase64;
    private Map<String, Object> metadata;

    // Explicit Getters and Setters for IDEs without Lombok plugin
    public String getEventId() { return eventId; }
    public void setEventId(String eventId) { this.eventId = eventId; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getFileName() { return fileName; }
    public void setFileName(String fileName) { this.fileName = fileName; }

    public String getFileBytesBase64() { return fileBytesBase64; }
    public void setFileBytesBase64(String fileBytesBase64) { this.fileBytesBase64 = fileBytesBase64; }

    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
}
