package com.secureflow.backend.user.repo;

import com.secureflow.backend.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface UserRepo extends JpaRepository<User, UUID> {

}
