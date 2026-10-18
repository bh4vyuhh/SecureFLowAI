package com.secureflow.backend.gateway;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import com.secureflow.backend.cryptoenforcement.model.IngestEventRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class IngestControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("Ingest benign text returns ALLOW and SAFE tier")
    void testIngestBenignEvent() throws Exception {
        IngestEventRequest request = IngestEventRequest.builder()
                .eventId("EVT_TEST_1")
                .source("CHROME")
                .eventType("clipboard")
                .content("Regular bank quarterly review notes without sensitive data.")
                .metadata(Map.of("user_id", "EMP_TEST_1", "destination_domain", "internal.bank.net"))
                .build();

        mockMvc.perform(post("/api/v1/events/ingest")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.actionTaken", is("ALLOW")))
                .andExpect(jsonPath("$.riskScore", lessThan(45)))
                .andExpect(jsonPath("$.sanitizedContent", containsString("quarterly review")));
    }

    @Test
    @DisplayName("Ingest credit card text returns BLOCK and RESTRICTED tier")
    void testIngestCardLeakBlocked() throws Exception {
        IngestEventRequest request = IngestEventRequest.builder()
                .eventId("EVT_TEST_2")
                .source("OUTLOOK")
                .eventType("paste")
                .content("Wire transfer to 4532015112830366 card verification.")
                .metadata(Map.of("user_id", "EMP_TEST_2", "destination_domain", "attacker@gmail.com"))
                .build();

        mockMvc.perform(post("/api/v1/events/ingest")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.actionTaken", is("BLOCK")))
                .andExpect(jsonPath("$.riskScore", greaterThanOrEqualTo(80)))
                .andExpect(jsonPath("$.threatCategory", notNullValue()));
    }
}
