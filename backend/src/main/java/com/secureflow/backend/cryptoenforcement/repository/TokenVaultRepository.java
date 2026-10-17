package com.secureflow.backend.cryptoenforcement.repository;

import com.secureflow.backend.cryptoenforcement.model.TokenVault;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface TokenVaultRepository extends JpaRepository<TokenVault, UUID> {

    Optional<TokenVault> findByTokenId(String tokenId);

    boolean existsByTokenId(String tokenId);
}
