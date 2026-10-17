package com.secureflow.backend.cryptoenforcement.masking;

import com.secureflow.backend.cryptoenforcement.model.EntitySpan;
import com.secureflow.backend.cryptoenforcement.model.EntityType;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Module 2: The Offset-Safe Text Masking Engine
 * (Surgical Data De-Identification)
 *
 * Prevents the Offset Drift Trap by sorting all detected entity spans in reverse
 * order (descending start index) before replacement. This ensures indices to the
 * left remain stable throughout mutations.
 */
@Slf4j
@Component
public class OffsetSafeMaskingEngine {

    private static final Pattern DIGITS_ONLY = Pattern.compile("\\d");
    private static final Pattern IBAN_COUNTRY_CODE = Pattern.compile("^[A-Za-z]{2}");

    /**
     * Applies surgical banking-grade masking to the given text using the provided entity spans.
     * Guaranteed offset-safe with zero corruption of surrounding greetings and text.
     *
     * Mathematical Proof of Invariance:
     * Let entities E = {e_1, e_2, ..., e_n} where start(e_i) < start(e_j) for i < j.
     * When mutations are executed in descending order of start index (e_n, e_{n-1}, ..., e_1),
     * any delta in string length ΔL_j = length(replacement_j) - (end_j - start_j) only alters
     * indices k > start(e_j). Because start(e_i) < start(e_j) for all i < j,
     * index(start(e_i)) remains strictly invariant: Δstart(e_i) = 0.
     *
     * @param text Original raw text
     * @param spans List of detected entity spans from Layer 3 AI Engine
     * @return Sanitized text with standard banking masks
     */
    public String mask(String text, List<EntitySpan> spans) {
        if (text == null || text.isEmpty() || spans == null || spans.isEmpty()) {
            return text == null ? "" : text;
        }

        int textLength = text.length();

        // Filter and sanitize spans to valid ranges
        List<EntitySpan> validSpans = new ArrayList<>();
        for (EntitySpan span : spans) {
            if (span == null) continue;
            int start = Math.max(0, span.start());
            int end = Math.min(textLength, span.end());
            if (start < end && start < textLength) {
                validSpans.add(new EntitySpan(span.entityType(), start, end, span.text()));
            }
        }

        if (validSpans.isEmpty()) {
            return text;
        }

        // CRITICAL: Sort entities in REVERSE order (largest start index first).
        // This solves the Offset Drift Trap.
        validSpans.sort((a, b) -> {
            int cmp = Integer.compare(b.start(), a.start());
            if (cmp != 0) return cmp;
            return Integer.compare(b.end(), a.end());
        });

        StringBuilder sb = new StringBuilder(text);
        int lastProcessedStart = Integer.MAX_VALUE;

        for (EntitySpan span : validSpans) {
            // Check for overlap: If this span's end exceeds the previous span's start,
            // they overlap. Skip the overlapping entity to prevent mangled tags.
            if (span.end() > lastProcessedStart) {
                log.debug("Skipping overlapping entity span [{}-{}]", span.start(), span.end());
                continue;
            }

            String entitySnippet = sb.substring(span.start(), span.end());
            String maskTag = generateBankingMask(span.entityType(), entitySnippet);

            sb.replace(span.start(), span.end(), maskTag);
            lastProcessedStart = span.start();
        }

        return sb.toString();
    }

    /**
     * Generates a compliant banking mask according to standard regulatory formats:
     * - Credit Cards: Keep last 4 digits -> [CARD_****9182]
     * - IBANs: Keep country code & last 4 digits -> [IBAN_GB****6819]
     * - Social Security Numbers: Complete mask -> [SSN_***-**-****]
     * - API Keys & Passwords: Total redaction -> [REDACTED_SECRET]
     */
    public String generateBankingMask(String entityType, String snippet) {
        if (entityType == null) {
            return "[REDACTED_SENSITIVE]";
        }

        String typeUpper = entityType.trim().toUpperCase(Locale.ROOT);

        switch (typeUpper) {
            case EntityType.CREDIT_CARD:
            case EntityType.CARD:
                return formatCreditCardMask(snippet);

            case EntityType.IBAN:
            case EntityType.ACCOUNT_NUMBER:
                return formatIbanMask(snippet);

            case EntityType.SSN:
            case EntityType.SOCIAL_SECURITY_NUMBER:
                return "[SSN_***-**-****]";

            case EntityType.API_KEY:
            case EntityType.PASSWORD:
            case EntityType.SECRET:
                return "[REDACTED_SECRET]";

            case EntityType.EMAIL:
                return "[REDACTED_EMAIL]";

            case EntityType.PHONE:
            case EntityType.PHONE_NUMBER:
                return formatPhoneMask(snippet);

            default:
                return "[REDACTED_" + typeUpper + "]";
        }
    }

    private String formatCreditCardMask(String snippet) {
        String digits = extractDigits(snippet);
        if (digits.length() >= 4) {
            String last4 = digits.substring(digits.length() - 4);
            return "[CARD_****" + last4 + "]";
        }
        return "[CARD_****]";
    }

    private String formatIbanMask(String snippet) {
        String cleaned = snippet.replaceAll("\\s+", "").toUpperCase(Locale.ROOT);
        String countryCode = "";
        Matcher countryMatcher = IBAN_COUNTRY_CODE.matcher(cleaned);
        if (countryMatcher.find()) {
            countryCode = countryMatcher.group();
        }

        String digits = extractDigits(cleaned);
        String last4 = digits.length() >= 4 ? digits.substring(digits.length() - 4) : "";

        if (!countryCode.isEmpty() && !last4.isEmpty()) {
            return "[IBAN_" + countryCode + "****" + last4 + "]";
        } else if (!last4.isEmpty()) {
            return "[IBAN_****" + last4 + "]";
        } else {
            return "[IBAN_REDACTED]";
        }
    }

    private String formatPhoneMask(String snippet) {
        String digits = extractDigits(snippet);
        if (digits.length() >= 4) {
            String last4 = digits.substring(digits.length() - 4);
            return "[PHONE_****" + last4 + "]";
        }
        return "[PHONE_REDACTED]";
    }

    private String extractDigits(String text) {
        if (text == null) return "";
        StringBuilder sb = new StringBuilder();
        Matcher m = DIGITS_ONLY.matcher(text);
        while (m.find()) {
            sb.append(m.group());
        }
        return sb.toString();
    }
}
