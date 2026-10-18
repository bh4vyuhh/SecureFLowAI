package com.secureflow.backend.cryptoenforcement.repository;

import com.secureflow.backend.cryptoenforcement.model.DlpAuditLog;
import com.secureflow.backend.cryptoenforcement.model.EnforcementAction;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import java.util.Optional;

@Repository
public interface DlpAuditLogRepository extends JpaRepository<DlpAuditLog, UUID> {

    Optional<DlpAuditLog> findTopByOrderByTimestampDesc();

    Page<DlpAuditLog> findAllByOrderByTimestampDesc(Pageable pageable);

    List<DlpAuditLog> findByEmployeeIdOrderByTimestampDesc(String employeeId);

    List<DlpAuditLog> findByActionTakenOrderByTimestampDesc(EnforcementAction actionTaken);

    List<DlpAuditLog> findByTimestampBetweenOrderByTimestampDesc(Instant start, Instant end);

    @Query("SELECT COUNT(a) FROM DlpAuditLog a WHERE a.riskScore >= :threshold")
    long countByRiskScoreGreaterThanEqual(@Param("threshold") int threshold);

    @Query("SELECT COUNT(a) FROM DlpAuditLog a WHERE a.actionTaken = :action")
    long countByActionTaken(@Param("action") EnforcementAction action);
}
