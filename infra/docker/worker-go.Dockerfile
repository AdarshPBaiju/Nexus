# ==============================================================================
# Project Nexus Heavy Worker Go Dockerfile (PNX-REPO-ARCH-004 §5)
# High-concurrency streaming, batch processing, outbox webhook dispatcher
# Multi-Stage, Static Distroless, Non-Root (UID 65532)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Builder Stage: Statically Linked Binary Compilation
# ------------------------------------------------------------------------------
FROM golang:1.23.4-bookworm@sha256:c925d7ef17dfa74d28cfb8e051c50e26dd9c9b46df5b9e59d997d91e3e78e470 AS builder

WORKDIR /src

# Copy go module manifests
COPY go.work ./
COPY services/nexus-worker-go/go.mod services/nexus-worker-go/go.sum* ./services/nexus-worker-go/

WORKDIR /src/services/nexus-worker-go

RUN go mod download

# Copy worker application source
COPY services/nexus-worker-go/ ./

# Statically link and strip debug symbols
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -trimpath -ldflags="-s -w" -o /bin/nexus-worker ./cmd/worker

# ------------------------------------------------------------------------------
# 2. Runner Stage: Google Distroless Static Non-Root
# ------------------------------------------------------------------------------
FROM gcr.io/distroless/static-debian12:nonroot@sha256:8dd8d4a2c9fa8ab088d47053e18a8b13d2f95ab9e224e77dd7143924ef08f4cb AS runner

WORKDIR /app

COPY --from=builder /bin/nexus-worker /bin/nexus-worker

USER 65532:65532

ENTRYPOINT ["/bin/nexus-worker"]
