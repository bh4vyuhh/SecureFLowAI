package com.secureflow.backend.cryptoenforcement.masking;

import com.secureflow.backend.cryptoenforcement.model.EntitySpan;
import com.secureflow.backend.cryptoenforcement.model.EntityType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Module 2: Offset-Safe Text Masking Engine Tests")
class OffsetSafeMaskingEngineTest {

    private OffsetSafeMaskingEngine maskingEngine;

    @BeforeEach
    void setUp() {
        maskingEngine = new OffsetSafeMaskingEngine();
    }

    @Test
    @DisplayName("Golden Test: Prevent Offset Drift Trap with Card and SSN")
    void testPreventOffsetDriftTrap() {
        // AI Example: "Pay card 4532-8921-0043-9182 with SSN 123-45-6789 today."
        // Card: index 9 to 28 (length 19)
        // SSN: index 38 to 49 (length 11)
        String input = "Pay card 4532-8921-0043-9182 with SSN 123-45-6789 today.";

        List<EntitySpan> spans = List.of(
                new EntitySpan(EntityType.CREDIT_CARD, 9, 28, "4532-8921-0043-9182"),
                new EntitySpan(EntityType.SSN, 38, 49, "123-45-6789")
        );

        String result = maskingEngine.mask(input, spans);

        // Expected: "Pay card [CARD_****9182] with SSN [SSN_***-**-****] today."
        assertEquals("Pay card [CARD_****9182] with SSN [SSN_***-**-****] today.", result);
        assertFalse(result.contains("4532-8921-0043-9182"), "Raw credit card must not appear in output");
        assertFalse(result.contains("123-45-6789"), "Raw SSN must not appear in output");
        assertTrue(result.startsWith("Pay card "));
        assertTrue(result.endsWith(" today."));
    }

    @Test
    @DisplayName("Reverse order sorting must be preserved even if AI provides spans shuffled")
    void testUnorderedSpansSorting() {
        String input = "Alpha 1111-2222-3333-4444 beta 5555-6666-7777-8888 gamma";
        // Span 2 given before Span 1
        List<EntitySpan> shuffledSpans = List.of(
                new EntitySpan(EntityType.CREDIT_CARD, 31, 50, "5555-6666-7777-8888"),
                new EntitySpan(EntityType.CREDIT_CARD, 6, 25, "1111-2222-3333-4444")
        );

        String result = maskingEngine.mask(input, shuffledSpans);
        assertEquals("Alpha [CARD_****4444] beta [CARD_****8888] gamma", result);
    }

    @Test
    @DisplayName("Banking Standard Masks: IBAN, API Key, Password, Phone, Email")
    void testStandardBankingMasks() {
        String text = "IBAN GB82WEST12345698765432 secret token_prod_secret_998811 email john.doe@bank.com phone 555-123-4567";
        List<EntitySpan> spans = new ArrayList<>();
        spans.add(new EntitySpan(EntityType.IBAN, 5, 27, "GB82WEST12345698765432"));
        spans.add(new EntitySpan(EntityType.API_KEY, 35, 59, "token_prod_secret_998811"));
        spans.add(new EntitySpan(EntityType.EMAIL, 66, 83, "john.doe@bank.com"));
        spans.add(new EntitySpan(EntityType.PHONE, 90, 102, "555-123-4567"));

        String masked = maskingEngine.mask(text, spans);

        assertTrue(masked.contains("[IBAN_GB****5432]"));
        assertTrue(masked.contains("[REDACTED_SECRET]"));
        assertTrue(masked.contains("[REDACTED_EMAIL]"));
        assertTrue(masked.contains("[PHONE_****4567]"));
    }

    @Test
    @DisplayName("Overlapping spans should be handled safely without mangling")
    void testOverlappingSpans() {
        String text = "Sensitive: 1234567890123456";
        // Two overlapping spans for the same region
        List<EntitySpan> spans = List.of(
                new EntitySpan(EntityType.CREDIT_CARD, 11, 27, "1234567890123456"),
                new EntitySpan(EntityType.ACCOUNT_NUMBER, 15, 27, "567890123456")
        );

        String masked = maskingEngine.mask(text, spans);
        assertNotNull(masked);
        assertFalse(masked.contains("1234567890123456"));
    }

    @Test
    @DisplayName("Edge Cases: Empty, null, or out-of-bounds spans")
    void testEdgeCases() {
        assertEquals("", maskingEngine.mask("", List.of()));
        assertEquals("hello", maskingEngine.mask("hello", null));
        assertEquals("hello", maskingEngine.mask("hello", List.of()));

        // Out of bounds span
        String text = "short";
        List<EntitySpan> outOfBounds = List.of(new EntitySpan(EntityType.SSN, 10, 20, "invalid"));
        assertEquals("short", maskingEngine.mask(text, outOfBounds));
    }

    @Test
    @DisplayName("Cross-border European IBANs and high-density entity payloads")
    void testCrossBorderEuropeanIbansAndHighDensityPayloads() {
        String transfer = "Transfer from DE89370400440532013000 to FR1420041010050500013M02606 confirmed.";
        List<EntitySpan> spans = List.of(
                new EntitySpan(EntityType.IBAN, 14, 36, "DE89370400440532013000"),
                new EntitySpan(EntityType.IBAN, 40, 67, "FR1420041010050500013M02606")
        );

        String masked = maskingEngine.mask(transfer, spans);
        assertTrue(masked.contains("[IBAN_DE****3000]"));
        assertTrue(masked.contains("[IBAN_FR****2606]"));
        assertTrue(masked.startsWith("Transfer from "));
        assertTrue(masked.endsWith(" confirmed."));
    }
}
