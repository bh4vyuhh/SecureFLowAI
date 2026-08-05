package com.secureflow.backend.user.service.impl;

import com.secureflow.backend.user.repo.UserRepo;
import com.secureflow.backend.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepo userRepo;
}
