package com.secureflow.backend.infrastucture.health;

import com.secureflow.backend.common.constants.ApiConstants;
import com.secureflow.backend.common.dto.HealthStatus;
import com.secureflow.backend.common.response.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthController {

//    @GetMapping("/api/v1/health")
//    public ApiResponse<HealthStatus> health(){
//        HealthStatus status = new HealthStatus(
//                "UP",
//                "0.0.1"
//        );
//        return new ApiResponse<>(
//                true,
//                "SecureFlow Backend is runnign",
//                status
//        );
//    }
    @GetMapping(ApiConstants.API_V1 + ApiConstants.HEALTH)
    public ApiResponse<HealthStatus> health() {

        throw new RuntimeException("Testing Global Exception Handler");
    }
}
