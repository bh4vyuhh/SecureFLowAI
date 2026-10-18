package com.secureflow.backend.cryptoenforcement.audit;

import com.secureflow.backend.cryptoenforcement.model.DlpAuditLog;
import com.secureflow.backend.cryptoenforcement.model.EnforcementAction;
import com.secureflow.backend.cryptoenforcement.repository.DlpAuditLogRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Module 5: Non-Blocking Asynchronous Audit Pipeline Tests")
class AsyncAuditPipelineTest {

    @Mock
    private DlpAuditLogRepository auditLogRepository;

    private AsyncAuditPipeline auditPipeline;

    @BeforeEach
    void setUp() {
        auditPipeline = new AsyncAuditPipeline(auditLogRepository);
    }

    @Test
    @DisplayName("Producer: Enqueue is instantaneous and non-blocking")
    void testNonBlockingEnqueue() {
        DlpAuditLog log = DlpAuditLog.builder()
                .id(UUID.randomUUID())
                .timestamp(Instant.now())
                .employeeId("EMP_9981")
                .application("OUTLOOK")
                .destination("external@gmail.com")
                .riskScore(88)
                .actionTaken(EnforcementAction.BLOCK)
                .payloadHash("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
                .executionTimeMs(1L)
                .build();

        // Warm-up JIT and classloading
        auditPipeline.enqueueAuditLog(DlpAuditLog.builder()
                .id(UUID.randomUUID())
                .timestamp(Instant.now())
                .employeeId("WARMUP")
                .application("WARMUP")
                .destination("warmup@test.com")
                .riskScore(0)
                .actionTaken(EnforcementAction.ALLOW)
                .payloadHash("warmup")
                .build());

        long start = System.nanoTime();
        boolean enqueued = auditPipeline.enqueueAuditLog(log);
        long durationNano = System.nanoTime() - start;
        long durationMs = durationNano / 1_000_000;

        assertTrue(enqueued);
        assertEquals(2, auditPipeline.getQueueSize());
        assertEquals(2, auditPipeline.getTotalEnqueued());
        assertTrue(durationMs <= 10, "Enqueue latency must be sub-millisecond or fast under load, was: " + durationMs + "ms");
    }

    @Test
    @DisplayName("Consumer: Batches audit events and writes to repository")
    void testConsumerBatchProcessing() {
        for (int i = 0; i < 5; i++) {
            auditPipeline.enqueueAuditLog(DlpAuditLog.builder()
                    .id(UUID.randomUUID())
                    .timestamp(Instant.now())
                    .employeeId("EMP_" + i)
                    .application("BROWSER")
                    .destination("dest" + i + "@company.com")
                    .riskScore(50)
                    .actionTaken(EnforcementAction.MASK)
                    .payloadHash("hash" + i)
                    .build());
        }

        assertEquals(5, auditPipeline.getQueueSize());

        auditPipeline.processAuditBatch();

        @SuppressWarnings("unchecked")
        ArgumentCaptor<List<DlpAuditLog>> captor = ArgumentCaptor.forClass(List.class);
        verify(auditLogRepository, times(1)).saveAll(captor.capture());

        List<DlpAuditLog> savedBatch = captor.getValue();
        assertEquals(5, savedBatch.size());
        assertEquals(0, auditPipeline.getQueueSize());
        assertEquals(5, auditPipeline.getTotalPersisted());
    }

    @Test
    @DisplayName("Shutdown Flush: Remaining queue records must be saved before shutdown")
    void testFlushOnShutdown() {
        for (int i = 0; i < 3; i++) {
            auditPipeline.enqueueAuditLog(DlpAuditLog.builder()
                    .id(UUID.randomUUID())
                    .timestamp(Instant.now())
                    .employeeId("SHUTDOWN_EMP_" + i)
                    .application("SLACK")
                    .destination("partner@bank.org")
                    .riskScore(10)
                    .actionTaken(EnforcementAction.ALLOW)
                    .payloadHash("shutdown_hash" + i)
                    .build());
        }

        auditPipeline.flushOnShutdown();

        verify(auditLogRepository, times(1)).saveAll(any());
        assertEquals(0, auditPipeline.getQueueSize());
        assertEquals(3, auditPipeline.getTotalPersisted());
    }
}
