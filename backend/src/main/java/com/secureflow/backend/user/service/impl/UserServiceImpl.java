package com.secureflow.backend.user.service.impl;

import com.secureflow.backend.user.dto.AuthDto;
import com.secureflow.backend.user.entity.User;
import com.secureflow.backend.user.enums.Role;
import com.secureflow.backend.user.repo.UserRepo;
import com.secureflow.backend.user.service.JwtService;
import com.secureflow.backend.user.service.UserService;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.LocalDateTime;

@Slf4j
@Service
public class UserServiceImpl implements UserService {

    private final UserRepo userRepo;
    private final JwtService jwtService;

    public UserServiceImpl(UserRepo userRepo, JwtService jwtService) {
        this.userRepo = userRepo;
        this.jwtService = jwtService;
    }

    @PostConstruct
    public void seedDefaultUsers() {
        if (userRepo.count() == 0) {
            log.info("Seeding default enterprise banking accounts into PostgreSQL/H2...");

            createSeedUser("System Administrator", "admin@bank.com", "admin123", Role.ADMIN);
            createSeedUser("Compliance Chief Auditor", "compliance@bank.com", "compliance123", Role.SUPERADMIN);
            createSeedUser("SOC Senior Analyst", "analyst@bank.com", "analyst123", Role.USER);

            log.info("Default banking accounts seeded successfully.");
        }
    }

    private void createSeedUser(String name, String email, String plainPassword, Role role) {
        if (!userRepo.existsByEmail(email)) {
            User user = User.builder()
                    .fullName(name)
                    .email(email)
                    .passwordHash(hashPassword(plainPassword))
                    .role(role)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();
            userRepo.save(user);
        }
    }

    @Override
    public AuthDto.AuthResponse register(AuthDto.RegisterRequest request) {
        if (userRepo.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("User already exists with email: " + request.getEmail());
        }

        Role role = request.getRole() != null ? request.getRole() : Role.USER;

        User user = User.builder()
                .fullName(request.getFullName())
                .email(request.getEmail().toLowerCase().trim())
                .passwordHash(hashPassword(request.getPassword()))
                .role(role)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        User saved = userRepo.save(user);
        String token = jwtService.generateToken(saved);

        return AuthDto.AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .email(saved.getEmail())
                .fullName(saved.getFullName())
                .role(saved.getRole())
                .message("User registered successfully")
                .build();
    }

    @Override
    public AuthDto.AuthResponse authenticate(AuthDto.LoginRequest request) {
        String email = request.getEmail().toLowerCase().trim();
        User user = userRepo.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("Invalid email or password"));

        String inputHash = hashPassword(request.getPassword());
        if (!inputHash.equals(user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid email or password");
        }

        String token = jwtService.generateToken(user);

        return AuthDto.AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .email(user.getEmail())
                .fullName(user.getFullName())
                .role(user.getRole())
                .message("Authentication successful")
                .build();
    }

    @Override
    public User getByEmail(String email) {
        return userRepo.findByEmail(email.toLowerCase().trim())
                .orElseThrow(() -> new IllegalArgumentException("User not found with email: " + email));
    }

    private static String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(("SecureFlowSalt2026:" + password).getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("Password hashing failure", e);
        }
    }
}
