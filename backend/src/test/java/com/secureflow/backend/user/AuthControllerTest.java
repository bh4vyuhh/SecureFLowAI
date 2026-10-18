package com.secureflow.backend.user;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.secureflow.backend.user.dto.AuthDto;
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
public class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("Login with valid seeded credentials returns JWT token")
    void testLoginSuccess() throws Exception {
        AuthDto.LoginRequest request = AuthDto.LoginRequest.builder()
                .email("admin@bank.com")
                .password("admin123")
                .build();

        mockMvc.perform(post("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.token", notNullValue()))
                .andExpect(jsonPath("$.data.email", is("admin@bank.com")))
                .andExpect(jsonPath("$.data.role", is("ADMIN")));
    }

    @Test
    @DisplayName("Login with invalid credentials returns 401 Unauthorized")
    void testLoginInvalidCredentials() throws Exception {
        AuthDto.LoginRequest request = AuthDto.LoginRequest.builder()
                .email("admin@bank.com")
                .password("wrongpassword")
                .build();

        mockMvc.perform(post("/api/v1/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized());
    }
}
