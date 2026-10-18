package com.secureflow.backend.cryptoenforcement.crypto;

import com.secureflow.backend.cryptoenforcement.model.TokenVault;
import com.secureflow.backend.cryptoenforcement.repository.TokenVaultRepository;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Module 3: The Cryptographic Subsystems (Tokenization & Envelope Encryption)
 * (The Mathematical Armor)
 *
 * Implements:
 * 1. Mechanism A: Deterministic HMAC-SHA256 Tokenization with AES-256-GCM backed Data Vault
 * 2. Mechanism B: Authenticated AES-256-GCM Envelope Encryption with strictly unique 12-byte Nonces
 * 3. Strict RBAC Enforcement on Detokenization for compliance audits
 */
@Slf4j
@Service
public class CryptographicSubsystem {

    private final TokenVaultRepository tokenVaultRepository;

    public CryptographicSubsystem(TokenVaultRepository tokenVaultRepository) {
        this.tokenVaultRepository = tokenVaultRepository;
    }

    private static final String AES_ALGORITHM = "AES";
    private static final String AES_GCM_NO_PADDING = "AES/GCM/NoPadding";
    private static final String HMAC_SHA256 = "HmacSHA256";
    private static final int GCM_TAG_LENGTH_BITS = 128;
    private static final int GCM_NONCE_LENGTH_BYTES = 12; // 12-byte standard Nonce

    private static final Set<String> AUTHORIZED_DETOKENIZE_ROLES = Set.of(
            "ROLE_COMPLIANCE_OFFICER",
            "ROLE_ADMIN",
            "ROLE_SECURITY_OFFICER",
            "COMPLIANCE_OFFICER",
            "ADMIN"
    );

    @Value("${crypto.master-key:SecureFlowAI-Production-Banking-Key-32BytesLong!}")
    private String configuredMasterKey;

    @Value("${crypto.hmac-salt:SecureFlowAI-Deterministic-HMAC-Token-Salt-2026}")
    private String configuredHmacSalt;

    private final SecureRandom secureRandom = new SecureRandom();
    private SecretKey aesSecretKey;
    private SecretKey hmacSecretKey;

    @PostConstruct
    public void init() {
        try {
            // Derive 256-bit AES key from master key using SHA-256
            MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
            byte[] aesKeyBytes = sha256.digest(configuredMasterKey.getBytes(StandardCharsets.UTF_8));
            this.aesSecretKey = new SecretKeySpec(aesKeyBytes, AES_ALGORITHM);

            // Derive 256-bit HMAC key
            byte[] hmacKeyBytes = sha256.digest(configuredHmacSalt.getBytes(StandardCharsets.UTF_8));
            this.hmacSecretKey = new SecretKeySpec(hmacKeyBytes, HMAC_SHA256);

            log.info("Cryptographic Subsystem initialized with AES-256-GCM and HMAC-SHA256.");
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("Failed to initialize cryptographic subsystem", e);
        }
    }

    // =========================================================================
    // Mechanism A: Deterministic HMAC-SHA256 Tokenization
    // =========================================================================

    /**
     * Produces a unique 12-character deterministic alphanumeric token: [TOKEN_7a8f9b2c3d4e].
     * The same sensitive value always produces the identical token within the organization,
     * without exposing the raw plaintext to external observers.
     */
    public String generateDeterministicTokenId(String sensitiveValue) {
        if (sensitiveValue == null || sensitiveValue.isEmpty()) {
            return "[TOKEN_EMPTY]";
        }
        try {
            Mac mac = Mac.getInstance(HMAC_SHA256);
            mac.init(hmacSecretKey);
            byte[] digest = mac.doFinal(sensitiveValue.trim().getBytes(StandardCharsets.UTF_8));
            String hex = HexFormat.of().formatHex(digest);
            // 12-character alphanumeric code
            String tokenShort = hex.substring(0, 12);
            return "[TOKEN_" + tokenShort + "]";
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate HMAC token", e);
        }
    }

    /**
     * Tokenizes a sensitive value, storing the reversible link in PostgreSQL token_vault
     * encrypted under AES-256-GCM.
     */
    public String tokenize(String rawValue, String entityType, String requestedBy) {
        if (rawValue == null || rawValue.isEmpty()) {
            return rawValue;
        }

        String tokenId = generateDeterministicTokenId(rawValue);

        // Check if token already exists in vault to avoid redundant inserts
        Optional<TokenVault> existing = tokenVaultRepository.findByTokenId(tokenId);
        if (existing.isEmpty()) {
            // Encrypt rawValue with fresh random Nonce
            EncryptedPayload encrypted = encryptWithGcm(rawValue);

            TokenVault vaultEntry = TokenVault.builder()
                    .id(UUID.randomUUID())
                    .tokenId(tokenId)
                    .encryptedValue(encrypted.cipherTextBase64())
                    .ivNonce(encrypted.nonceBase64())
                    .tokenType(entityType != null ? entityType : "SENSITIVE_DATA")
                    .createdAt(Instant.now())
                    .createdBy(requestedBy != null ? requestedBy : "SYSTEM")
                    .build();

            tokenVaultRepository.save(vaultEntry);
            log.debug("New token registered in Token Vault: {}", tokenId);
        }

        return tokenId;
    }

    /**
     * Detokenizes a token ID back into its original sensitive value.
     * Restricted to authorized compliance officers and security administrators.
     */
    public String detokenize(String tokenId, String callerRole) {
        if (callerRole == null || !AUTHORIZED_DETOKENIZE_ROLES.contains(callerRole.toUpperCase())) {
            log.warn("Unauthorized attempt to detokenize token: {} by role: {}", tokenId, callerRole);
            throw new SecurityException("Detokenization denied: Caller lacks required compliance role privileges.");
        }

        TokenVault vaultEntry = tokenVaultRepository.findByTokenId(tokenId)
                .orElseThrow(() -> new IllegalArgumentException("Token ID not found in vault: " + tokenId));

        return decryptWithGcm(vaultEntry.getEncryptedValue(), vaultEntry.getIvNonce());
    }

    // =========================================================================
    // Mechanism B: AES-256-GCM Envelope Encryption
    // =========================================================================

    public record EncryptedPayload(String cipherTextBase64, String nonceBase64, String packedPayloadBase64) {}

    /**
     * Encrypts plaintext using AES-256 in GCM Mode.
     * Generates a fresh, cryptographically secure 12-byte Nonce for every single encryption.
     * Nonce is never reused.
     */
    public EncryptedPayload encryptWithGcm(String plainText) {
        if (plainText == null) {
            throw new IllegalArgumentException("Plaintext cannot be null");
        }

        try {
            // Generate brand-new 12-byte random Nonce
            byte[] nonce = new byte[GCM_NONCE_LENGTH_BYTES];
            secureRandom.nextBytes(nonce);

            Cipher cipher = Cipher.getInstance(AES_GCM_NO_PADDING);
            GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH_BITS, nonce);
            cipher.init(Cipher.ENCRYPT_MODE, aesSecretKey, spec);

            byte[] cipherTextWithTag = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));

            // Pack Nonce (12 bytes) + CipherText+Tag into a single transport payload
            ByteBuffer byteBuffer = ByteBuffer.allocate(nonce.length + cipherTextWithTag.length);
            byteBuffer.put(nonce);
            byteBuffer.put(cipherTextWithTag);
            byte[] packed = byteBuffer.array();

            String nonceBase64 = Base64.getEncoder().encodeToString(nonce);
            String cipherTextBase64 = Base64.getEncoder().encodeToString(cipherTextWithTag);
            String packedBase64 = Base64.getEncoder().encodeToString(packed);

            return new EncryptedPayload(cipherTextBase64, nonceBase64, packedBase64);
        } catch (Exception e) {
            throw new RuntimeException("AES-256-GCM encryption failed", e);
        }
    }

    /**
     * Decrypts ciphertext using AES-256 in GCM Mode with authentication tag verification.
     * If the payload has been tampered with in transit or storage, verification will fail.
     */
    public String decryptWithGcm(String cipherTextBase64, String nonceBase64) {
        try {
            byte[] nonce = Base64.getDecoder().decode(nonceBase64);
            byte[] cipherBytes = Base64.getDecoder().decode(cipherTextBase64);

            Cipher cipher = Cipher.getInstance(AES_GCM_NO_PADDING);
            GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH_BITS, nonce);
            cipher.init(Cipher.DECRYPT_MODE, aesSecretKey, spec);

            byte[] plainBytes = cipher.doFinal(cipherBytes);
            return new String(plainBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            log.error("Authentication tag verification failed or invalid ciphertext: {}", e.getMessage());
            throw new SecurityException("Cryptographic tamper alert: payload integrity verification failed!", e);
        }
    }

    /**
     * Decrypts a packed Base64 payload containing [Nonce (12 bytes) | CipherText+Tag].
     */
    public String decryptPackedPayload(String packedBase64) {
        try {
            byte[] packed = Base64.getDecoder().decode(packedBase64);
            if (packed.length < GCM_NONCE_LENGTH_BYTES) {
                throw new IllegalArgumentException("Payload too short to contain valid Nonce");
            }

            ByteBuffer bb = ByteBuffer.wrap(packed);
            byte[] nonce = new byte[GCM_NONCE_LENGTH_BYTES];
            bb.get(nonce);

            byte[] cipherBytes = new byte[bb.remaining()];
            bb.get(cipherBytes);

            Cipher cipher = Cipher.getInstance(AES_GCM_NO_PADDING);
            GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH_BITS, nonce);
            cipher.init(Cipher.DECRYPT_MODE, aesSecretKey, spec);

            byte[] plainBytes = cipher.doFinal(cipherBytes);
            return new String(plainBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            throw new SecurityException("Tamper alert: packed envelope authentication failed!", e);
        }
    }

    /**
     * Computes SHA-256 digital fingerprint of a message or payload.
     * Never stores raw sensitive customer data in audit logs.
     */
    public String computeSha256(String text) {
        if (text == null) return "";
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(text.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm unavailable", e);
        }
    }
}
