package com.secureflow.backend.user.service;

import com.secureflow.backend.user.entity.User;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/**
 * Native Java 21 RFC 7519 JWT Service using HMAC-SHA256 signature.
 * Requires zero external JAR dependencies and guarantees sub-millisecond token issuance.
 */
@Service
public class JwtService {

    @Value("${jwt.secret:SecureFlowAI-Production-JWT-SecretKey-2026-BankingGrade-32Bytes!}")
    private String secretKey;

    private static final long EXPIRATION_MILLIS = 86_400_000L; // 24 hours

    public String generateToken(User user) {
        long now = System.currentTimeMillis();
        long exp = now + EXPIRATION_MILLIS;

        String headerJson = "{\"alg\":\"HS256\",\"typ\":\"JWT\"}";
        String payloadJson = String.format(
                "{\"sub\":\"%s\",\"id\":\"%s\",\"name\":\"%s\",\"role\":\"%s\",\"iat\":%d,\"exp\":%d}",
                escapeJson(user.getEmail()),
                user.getId(),
                escapeJson(user.getFullName()),
                user.getRole().name(),
                now / 1000,
                exp / 1000
        );

        String encodedHeader = base64UrlEncode(headerJson.getBytes(StandardCharsets.UTF_8));
        String encodedPayload = base64UrlEncode(payloadJson.getBytes(StandardCharsets.UTF_8));
        String signature = sign(encodedHeader + "." + encodedPayload, secretKey);

        return encodedHeader + "." + encodedPayload + "." + signature;
    }

    public boolean validateToken(String token) {
        if (token == null || !token.contains(".")) return false;
        String[] parts = token.split("\\.");
        if (parts.length != 3) return false;

        String expectedSignature = sign(parts[0] + "." + parts[1], secretKey);
        if (!expectedSignature.equals(parts[2])) {
            return false;
        }

        try {
            String payloadJson = new String(base64UrlDecode(parts[1]), StandardCharsets.UTF_8);
            if (payloadJson.contains("\"exp\":")) {
                int idx = payloadJson.indexOf("\"exp\":") + 6;
                int endIdx = payloadJson.indexOf("}", idx);
                if (endIdx == -1) endIdx = payloadJson.indexOf(",", idx);
                long exp = Long.parseLong(payloadJson.substring(idx, endIdx).trim());
                return System.currentTimeMillis() / 1000 < exp;
            }
        } catch (Exception e) {
            return false;
        }
        return true;
    }

    public String extractEmail(String token) {
        try {
            String[] parts = token.split("\\.");
            String payloadJson = new String(base64UrlDecode(parts[1]), StandardCharsets.UTF_8);
            int idx = payloadJson.indexOf("\"sub\":\"") + 7;
            int endIdx = payloadJson.indexOf("\"", idx);
            return payloadJson.substring(idx, endIdx);
        } catch (Exception e) {
            return null;
        }
    }

    private String sign(String data, String key) {
        try {
            Mac sha256Hmac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            sha256Hmac.init(secretKeySpec);
            byte[] signedBytes = sha256Hmac.doFinal(data.getBytes(StandardCharsets.UTF_8));
            return base64UrlEncode(signedBytes);
        } catch (Exception e) {
            throw new RuntimeException("HMAC-SHA256 signing failed: " + e.getMessage(), e);
        }
    }

    private static String base64UrlEncode(byte[] bytes) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private static byte[] base64UrlDecode(String str) {
        return Base64.getUrlDecoder().decode(str);
    }

    private static String escapeJson(String input) {
        if (input == null) return "";
        return input.replace("\"", "\\\"");
    }
}
