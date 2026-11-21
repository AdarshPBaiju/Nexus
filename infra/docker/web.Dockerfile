# ==============================================================================
# Project Nexus Web Client Dockerfile (PNX-REPO-ARCH-004 §5)
# Runtimes: Node 20 / TypeScript 5.6 | Framework: Next.js 15 (App Router / RSC)
# Multi-Stage, Standalone Output, Non-Root (UID 10001)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Base Stage: Node Alpine with pnpm
# ------------------------------------------------------------------------------
FROM node:20.18.1-alpine@sha256:f70da57f6d538e1a690e8e6ab2323e0ec0e599e691ec55ad7d3c015b3c3b0bbd AS base

ENV PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@9.15.4 --activate

WORKDIR /app

# ------------------------------------------------------------------------------
# 2. Dependencies Stage
# ------------------------------------------------------------------------------
FROM base AS deps

COPY pnpm-workspace.yaml package.json pnpm-lock.yaml* ./
COPY packages/contracts/package.json ./packages/contracts/
COPY packages/ui/package.json ./packages/ui/
COPY clients/web/package.json ./clients/web/

RUN pnpm install --frozen-lockfile --ignore-scripts || pnpm install

# ------------------------------------------------------------------------------
# 3. Builder Stage
# ------------------------------------------------------------------------------
FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages ./packages
COPY --from=deps /app/clients ./clients
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

RUN pnpm turbo run build --filter=@nexus/web...

# ------------------------------------------------------------------------------
# 4. Runner Stage: Hardened, Non-Root Runtime
# ------------------------------------------------------------------------------
FROM node:20.18.1-alpine@sha256:f70da57f6d538e1a690e8e6ab2323e0ec0e599e691ec55ad7d3c015b3c3b0bbd AS runner

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

WORKDIR /app

RUN addgroup --system --gid 10001 nodejs && \
    adduser --system --uid 10001 nextjs

# Copy Next.js standalone build artifacts
COPY --from=builder --chown=nextjs:nodejs /app/clients/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/clients/web/.next/static ./clients/web/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/clients/web/public ./clients/web/public

USER 10001:10001

EXPOSE 3000

CMD ["node", "clients/web/server.js"]
