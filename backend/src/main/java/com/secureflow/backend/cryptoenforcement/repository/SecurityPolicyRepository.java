package com.secureflow.backend.cryptoenforcement.repository;

import com.secureflow.backend.cryptoenforcement.model.SecurityPolicy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SecurityPolicyRepository extends JpaRepository<SecurityPolicy, Long> {

    List<SecurityPolicy> findByIsActiveTrue();

    Optional<SecurityPolicy> findFirstByIsActiveTrueOrderByUpdatedAtDesc();
}
