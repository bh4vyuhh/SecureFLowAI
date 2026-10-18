package com.secureflow.backend.user.service;

import com.secureflow.backend.user.dto.AuthDto;
import com.secureflow.backend.user.entity.User;

public interface UserService {
    AuthDto.AuthResponse register(AuthDto.RegisterRequest request);
    AuthDto.AuthResponse authenticate(AuthDto.LoginRequest request);
    User getByEmail(String email);
}
