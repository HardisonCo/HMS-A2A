# Build stage
FROM rust:1.70-slim as builder

# Install dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a new empty shell project
WORKDIR /app
COPY . .

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bullseye-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from the build stage
COPY --from=builder /app/target/release/hms-agency-template /usr/local/bin/hms-agency

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV RUST_LOG=info

# Expose the application port
EXPOSE 3000

# Run the application
CMD ["hms-agency"]