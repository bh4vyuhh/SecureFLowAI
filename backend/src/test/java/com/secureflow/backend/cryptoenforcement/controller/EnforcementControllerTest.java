package com.secureflow.backend.cryptoenforcement.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.secureflow.backend.cryptoenforcement.model.EnforcementAction;
import com.secureflow.backend.cryptoenforcement.model.EnforcementRequest;
import com.secureflow.backend.cryptoenforcement.model.EntitySpan;
import com.secureflow.backend.cryptoenforcement.model.EntityType;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@DisplayName("Layer 4 REST Controller Integration Tests")
class EnforcementControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("POST /api/v1/enforcement/evaluate: Block high risk payload")
    void testEvaluateBlock() throws Exception {
        EnforcementRequest req = EnforcementRequest.builder()
                .payload("Exfiltrating SSN: 123-45-6789")
                .destination("leak@external.com")
                .employeeId("EMP_ROUGE")
                .application("CHROME")
                .riskScore(95)
                .entities(List.of(new EntitySpan(EntityType.SSN, 18, 29, "123-45-6789")))
                .build();

        mockMvc.perform(post("/api/v1/enforcement/evaluate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.action").value("BLOCK"))
                .andExpect(jsonPath("$.data.blocked").value(true))
                .andExpect(jsonPath("$.data.payloadHash").isNotEmpty());
    }

    @Test
    @DisplayName("POST /api/v1/enforcement/evaluate: Mask medium risk payload without offset drift")
    void testEvaluateMask() throws Exception {
        EnforcementRequest req = EnforcementRequest.builder()
                .payload("Customer card 4532-8921-0043-9182 verified.")
                .destination("support@partner.org")
                .employeeId("EMP_AGENT")
                .application("DESKTOP")
                .riskScore(55)
                .entities(List.of(new EntitySpan(EntityType.CREDIT_CARD, 14, 33, "4532-8921-0043-9182")))
                .build();

        mockMvc.perform(post("/api/v1/enforcement/evaluate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.action").value("MASK"))
                .andExpect(jsonPath("$.data.sanitizedPayload").value("Customer card [CARD_****9182] verified."))
                .andExpect(jsonPath("$.data.remediated").value(true));
    }

    @Test
    @DisplayName("POST /api/v1/crypto/tokenize and /api/v1/crypto/detokenize workflow")
    void testTokenizeAndDetokenize() throws Exception {
        // 1. Tokenize
        String card = "5412-7512-3412-3456";
        String tokenResponse = mockMvc.perform(post("/api/v1/crypto/tokenize")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"sensitiveValue\": \"" + card + "\", \"entityType\": \"CREDIT_CARD\", \"requestedBy\": \"OFFICER_01\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.tokenId", startsWith("[TOKEN_")))
                .andReturn().getResponse().getContentAsString();

        String tokenId = objectMapper.readTree(tokenResponse).get("data").get("tokenId").asText();

        // 2. Detokenize with authorized role
        mockMvc.perform(post("/api/v1/crypto/detokenize")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"tokenId\": \"" + tokenId + "\", \"requester\": \"OFFICER_01\", \"role\": \"ROLE_COMPLIANCE_OFFICER\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.originalValue").value(card));
    }

    @Test
    @DisplayName("POST /api/v1/crypto/encrypt and /api/v1/crypto/decrypt with GCM")
    void testEncryptAndDecrypt() throws Exception {
        String secretMessage = "Top Secret Mergers & Acquisitions Banking Dossier";

        String encryptResponse = mockMvc.perform(post("/api/v1/crypto/encrypt")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"plainText\": \"" + secretMessage + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.cipherText").isNotEmpty())
                .andReturn().getResponse().getContentAsString();

        String cipherText = objectMapper.readTree(encryptResponse).get("data").get("cipherText").asText();

        mockMvc.perform(post("/api/v1/crypto/decrypt")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"cipherText\": \"" + cipherText + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.plainText").value(secretMessage))
                .andExpect(jsonPath("$.data.authentic").value(true));
    }

    @Test
    @DisplayName("GET /api/v1/audit/stats: Telemetry stats")
    void testAuditStats() throws Exception {
        mockMvc.perform(get("/api/v1/audit/stats"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.totalEnqueued").isNumber());
    }
}
