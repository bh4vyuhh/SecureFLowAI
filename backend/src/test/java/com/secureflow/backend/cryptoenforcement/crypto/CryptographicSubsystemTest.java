package com.secureflow.backend.cryptoenforcement.crypto;

import com.secureflow.backend.cryptoenforcement.model.TokenVault;
import com.secureflow.backend.cryptoenforcement.repository.TokenVaultRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.Instant;
import java.util.Base64;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Module 3: Cryptographic Subsystems Tests (Tokenization & Envelope Encryption)")
class CryptographicSubsystemTest {

    @Mock
    private TokenVaultRepository tokenVaultRepository;

    private CryptographicSubsystem cryptoSubsystem;

    @BeforeEach
    void setUp() {
        cryptoSubsystem = new CryptographicSubsystem(tokenVaultRepository);
        ReflectionTestUtils.setField(cryptoSubsystem, "configuredMasterKey", "MasterTestKeyForUnitTests-32BytesLong!!");
        ReflectionTestUtils.setField(cryptoSubsystem, "configuredHmacSalt", "DeterministicHmacSaltForUnitTests2026!!");
        cryptoSubsystem.init();
    }

    @Test
    @DisplayName("Deterministic HMAC-SHA256: Same account produces identical token every time")
    void testDeterministicHmacTokenization() {
        String accountNumber = "ACCT-9876-5432-1000";
        String token1 = cryptoSubsystem.generateDeterministicTokenId(accountNumber);
        String token2 = cryptoSubsystem.generateDeterministicTokenId(accountNumber);

        assertNotNull(token1);
        assertEquals(token1, token2, "HMAC tokenization must be deterministic");
        assertTrue(token1.startsWith("[TOKEN_"));
        assertTrue(token1.endsWith("]"));
        assertEquals(20, token1.length(), "Token format must be [TOKEN_ + 12 hex chars + ] (7 + 12 + 1 = 20 chars)");

        // Different account must produce different token
        String tokenDifferent = cryptoSubsystem.generateDeterministicTokenId("ACCT-1111-2222-3333");
        assertNotEquals(token1, tokenDifferent);
    }

    @Test
    @DisplayName("AES-256-GCM Envelope Encryption: Unique 12-byte Nonce per encryption")
    void testUniqueNoncePerEncryption() {
        String secretData = "Confidential Bank Loan Application for Customer ID #4492";

        CryptographicSubsystem.EncryptedPayload enc1 = cryptoSubsystem.encryptWithGcm(secretData);
        CryptographicSubsystem.EncryptedPayload enc2 = cryptoSubsystem.encryptWithGcm(secretData);

        assertNotEquals(enc1.nonceBase64(), enc2.nonceBase64(),
                "CRITICAL GOLDEN RULE: Nonce must NEVER be reused across encryptions");
        assertNotEquals(enc1.cipherTextBase64(), enc2.cipherTextBase64(),
                "Different nonces must yield different ciphertexts for identical plaintext");

        // Verify decryption recovers original text
        String decrypted1 = cryptoSubsystem.decryptWithGcm(enc1.cipherTextBase64(), enc1.nonceBase64());
        String decrypted2 = cryptoSubsystem.decryptWithGcm(enc2.cipherTextBase64(), enc2.nonceBase64());

        assertEquals(secretData, decrypted1);
        assertEquals(secretData, decrypted2);
    }

    @Test
    @DisplayName("Tamper Detection: Wax seal breaks when even 1 bit of ciphertext is altered")
    void testTamperDetectionWithGcmAuthenticationTag() {
        String sensitivePayload = "Transfer $1,000,000 from Account A to Account B";
        CryptographicSubsystem.EncryptedPayload enc = cryptoSubsystem.encryptWithGcm(sensitivePayload);

        // Tamper with ciphertext bytes
        byte[] cipherBytes = Base64.getDecoder().decode(enc.cipherTextBase64());
        cipherBytes[cipherBytes.length / 2] ^= 0x01; // flip one bit
        String tamperedCipherBase64 = Base64.getEncoder().encodeToString(cipherBytes);

        assertThrows(SecurityException.class, () ->
                cryptoSubsystem.decryptWithGcm(tamperedCipherBase64, enc.nonceBase64()),
                "Altered ciphertext must trigger authentication tag verification failure");
    }

    @Test
    @DisplayName("RBAC Detokenization: Authorized compliance role succeeds")
    void testAuthorizedDetokenization() {
        String rawCard = "4532-0000-1111-2222";
        CryptographicSubsystem.EncryptedPayload enc = cryptoSubsystem.encryptWithGcm(rawCard);

        String tokenId = cryptoSubsystem.generateDeterministicTokenId(rawCard);

        TokenVault vaultEntry = TokenVault.builder()
                .id(UUID.randomUUID())
                .tokenId(tokenId)
                .encryptedValue(enc.cipherTextBase64())
                .ivNonce(enc.nonceBase64())
                .tokenType("CREDIT_CARD")
                .createdAt(Instant.now())
                .createdBy("OFFICER_01")
                .build();

        when(tokenVaultRepository.findByTokenId(tokenId)).thenReturn(Optional.of(vaultEntry));

        String detokenized = cryptoSubsystem.detokenize(tokenId, "ROLE_COMPLIANCE_OFFICER");
        assertEquals(rawCard, detokenized);
    }

    @Test
    @DisplayName("RBAC Detokenization: Unauthorized role is rejected")
    void testUnauthorizedDetokenization() {
        String tokenId = "[TOKEN_7a8f9b2c3d4e]";

        assertThrows(SecurityException.class, () ->
                cryptoSubsystem.detokenize(tokenId, "ROLE_USER"),
                "Unauthorized roles must be denied detokenization privileges");
    }

    @Test
    @DisplayName("SHA-256 Digital Fingerprint calculation")
    void testSha256Fingerprint() {
        String data = "Sample banking message";
        String hash1 = cryptoSubsystem.computeSha256(data);
        String hash2 = cryptoSubsystem.computeSha256(data);

        assertEquals(64, hash1.length());
        assertEquals(hash1, hash2);
        assertNotEquals(hash1, cryptoSubsystem.computeSha256("Different message"));
    }
}
