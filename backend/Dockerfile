# ==============================================================================
# SecureFlow AI - Spring Boot Central Gateway & Layer 4 Dockerfile
# ==============================================================================
# Multi-stage build: compiles with Temurin JDK 21 and runs on a hardened JRE
# ==============================================================================

# Stage 1: Build JAR with Maven
FROM maven:3.9.9-eclipse-temurin-21-alpine AS builder

WORKDIR /build

COPY pom.xml ./
# Pre-fetch dependencies
RUN mvn dependency:go-offline -B || true

COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Hardened Runtime Container
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Add security user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /build/target/*.jar /app/secureflow-backend.jar
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 9090

ENV SPRING_PROFILES_ACTIVE=prod \
    JAVA_OPTS="-Xms256m -Xmx1024m -XX:+UseG1GC"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/secureflow-backend.jar"]
