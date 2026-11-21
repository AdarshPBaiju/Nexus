# Nexus

Nexus is a polyglot modular monolith operating system engineered for high-concurrency multi-tenant venue operations, point-of-sale (POS) environments, double-entry financial ledgers, and compound resource scheduling across web, desktop, and embedded hardware runtimes.

---

## 1. System Abstract & Architectural Subsystems

Nexus provides a single unified platform supporting complex operational hierarchies (Tenant $\rightarrow$ Organization Group $\rightarrow$ Legal Entity $\rightarrow$ Business Unit $\rightarrow$ Branch $\rightarrow$ Physical Zone) with strict cryptographic isolation, sub-50ms data delivery, and native peripheral hardware execution.

### Key Subsystems

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT EXECUTION SURFACES                                      │
│  • Web Application (Next.js 15 App Router, React 19, RSC, 7 Canonical Shells, 19 Custom Inputs)  │
│  • Desktop Runtime (Tauri 2.0 Rust, Raw ESC/POS, RJ11 Kick, EDC Bridges, Encrypted SQLCipher)   │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ HTTP/2 + WebSocket (X-Nexus-* Canonical Headers)
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                       TIER 1 PLATFORM KERNEL & 10-STAGE MIDDLEWARE                               │
│  [1] Security & Host Validation        [6] Multi-Actor Authentication (5 Typed Principals)      │
│  [2] Encrypted Path Unsealing (nx1_*)  [7] 5-Layer Compiled PDP Authorization (p99 < 1.5ms)      │
│  [3] Workspace & Tenant Isolation      [8] Weak/Strong ETag Evaluation (304 Not Modified)       │
│  [4] Tenant RLS Context Binding        [9] RFC 9110 If-Match Optimistic Concurrency             │
│  [5] Idempotency & Replay Protection   [10] RYOW Stickiness & Audit Logging                      │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
┌──────────────────────────────────────────────┐ ┌─────────────────────────────────────────────────┐
│       TIER 2 SHARED BUSINESS ENGINES         │ │         TIER 3 MODULAR FEATURE PLUGINS          │
│ • Ledgers & Multi-Currency Money FX          │ │ • POS Counter & Kitchen Display System (KDS)    │
│ • Omnichannel Notification Orchestrator      │ │ • Cafe QSR Catalog, Modifiers & Recipe BOM      │
│ • Universal SSTI-Proof Template Engine       │ │ • Game Core 10-Dim UTC Monotonic Engine         │
│ • Multi-Rail Payment Gateway Router          │ │ • Compound Venue Scheduler & Floor Canvas       │
│ • Universal Invoice Builder & Spooler        │ │ • Basic Finance (FIN_CORE) & HR (HR_CORE)       │
│ • Dynamic Form Builder & Schema Engine       │ │ • Hardware Drivers (Printers, Scanners, EDC)    │
└──────────────────────┬───────────────────────┘ └────────────────────────┬────────────────────────┘
                       │                                                  │
                       └────────────────────────┬─────────────────────────┘
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             DATA RESIDENCY & PERSISTENCE LAYER                                   │
│ • PostgreSQL 16+ with Forced Row-Level Security (NOBYPASSRLS, Composite Tenant Foreign Keys)     │
│ • Redis 7.4 (Logical DB Separation: Celery, Asynq, Cache L1/L2, Channels, Token Buckets)        │
│ • MinIO S3 Object Storage (SSE-KMS Encryption, 8-Year Statutory WORM Object Lock)               │
│ • Polyglot Heavy Workers (Python Celery 6-Queue Split + Go 1.23 Asynq High-Throughput Engine)    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Specifications

### Cryptographic Multi-Tenancy & Data Isolation
- Tenant boundaries are enforced at the database storage layer via PostgreSQL 16 Forced Row-Level Security (`NOBYPASSRLS`). Every query executes inside an explicit `tenant_transaction` setting `app.current_tenant_id`.
- Sensitive data fields (`CONFIDENTIAL_PII`, `RESTRICTED_SECRET`) are encrypted at rest using `TenantEnvelopeCipher` (AES-256-GCM + per-tenant Regional KMS Data Encryption Keys + Additional Authenticated Data binding).
- Searchable encrypted columns utilize deterministic HMAC-SHA256 blind indexing (`BlindIndexHasher`).

### Five-Layer Fail-Closed Authorization
Access control evaluates through an immutable decision pipeline terminating upon failure at any tier:
1. **Hard Tenant Isolation:** PostgreSQL 16 Forced RLS enforces physical tenant boundaries.
2. **Plugin Capability Gate:** Verifies the owning feature engine is active and enabled for the target execution surface (`WEB_ALL`, `DESKTOP_ONLY`, `HYBRID_WEB_DESKTOP`).
3. **Multi-Dimensional Scoped RBAC:** Evaluates permissions across 6 structural tiers (`TENANT`, `ORGANIZATION_GROUP`, `LEGAL_ENTITY`, `BUSINESS_UNIT`, `BRANCH`, `PHYSICAL_ZONE`). Explicit `DENY` overrides all grants unconditionally.
4. **ABAC & ReBAC Guardrails:** AST-safe runtime expressions (`safe_ast`) evaluate monetary thresholds, active shift windows, trusted device certificates, and time-bounded resource relationships.
5. **Field-Level Security (FLS) & Segregation of Duties (SoD):** Columns are projected as `READ`, `MASKED`, `WRITE`, or `HIDDEN`. Toxic role combinations (e.g. Cashier + Shift Reconciler) are blocked statically and dynamically.

*Compiled PDP SLA:* Bitwise policy snapshots cached in Redis L1/L2 resolve decisions in $p99 < 1.5\text{ ms}$. Cluster-wide role or assignment revocations propagate in $< 1.0\text{ s}$ via `rbac.version.bumped.v1`.

### Zero-Query-String Encrypted Path Envelopes
- To eliminate enumeration attacks, data leakage in access logs, and fragile query parameters, URLs seal all identifiers, filter trees, sort orders, and pagination cursors into binary path tokens (`/resource/nx1_<TOKEN>/`).
- Envelopes utilize canonical CBOR serialization, optional Deflate compression ($> 64\text{ bytes}$), and AES-256-GCM (random nonce for query filters) or AES-256-GCM-SIV (deterministic nonce for cacheable detail entities).
- URLs exceeding 750 bytes automatically transition to server-stored share handles (`nx1s_`) backed by Redis. Raw database UUIDs and unencrypted query parameters (`?`) return uniform `404 Not Found`.

### Universal Plugin Architecture
- All commercial business capabilities are packaged as decoupled, versioned plugins.
- Feature enablement is declarative: installing a plugin in the Web Marketplace (`/owner/marketplace`) activates PostgreSQL configuration rows and updates Redis cache keys in $< 1\text{ ms}$, requiring zero server restarts.
- Plugins declare their execution surface: web browsers attempting to access desktop-restricted routes automatically mount `<DesktopRuntimeGuard>` with 1-click `nexus://` protocol handoff.

### Background Task Execution & Worker Split
- Workloads are strictly divided between Python Celery and Go heavy workers:
  - **Celery 5.4+ (6 Dedicated Queues):** `q.critical` (auth OTPs, payment webhooks), `q.domain` (ledger entries, order routing), `q.channels` (WebSocket push), `q.i18n` (translation chords), `q.beat` (cron sweeps), `q.maintenance` (partitioning, compaction).
  - **Go 1.23 Heavy Worker (`nexus-worker-go`):** Executes CPU-intensive batch jobs on Redis Asynq (`go:batch`) including streaming CSV/XLSX/PDF exports ($> 5,000$ rows), 100,000-row bulk imports, Firebase FCM 500-token multicasts, and bank settlement reconciliation under $< 128\text{ MB}$ RSS.

### Native Desktop Runtime & Hardware Integration
- The desktop shell is compiled using Tauri 2.0 with a native Rust backend:
  - Direct raw ESC/POS thermal printing over TCP port 9100, USB bulk endpoints (`rusb`), and RS-232 serial.
  - Automated 24V solenoid cash-drawer kick pulses (`ESC p 0 25 250`) on tender completion.
  - Local encrypted SQLCipher storage for zero-latency offline counter POS operations during WAN outages, synchronizing via WebSocket outbox upon reconnection.
  - USB/LAN EDC payment terminal bridges (Pine Labs, Verifone, Ingenico).

---

## 3. Monorepo Repository Structure

```
Nexus/
├── clients/
│   ├── web/                    # Next.js 15 (App Router, React 19, Server Components)
│   └── desktop/                # Tauri 2.0 Rust runtime (single-instance, hardware bindings)
├── services/
│   ├── nexus-api/              # Python 3.12 / Django 5.1 / DRF core API and platform services
│   └── nexus-worker-go/        # Go 1.23 background worker (Asynq batch processor)
├── packages/
│   ├── contracts/              # Shared polyglot DTOs, headers, and envelope codecs
│   ├── ui/                     # Design system, 7 Canonical Shells, 19 custom input primitives
│   ├── api-client/             # HTTP client with ETag caching and i18n hydration
│   ├── form-builder/           # Schema-driven visual form designer (JSON Schema 2020-12)
│   ├── schema-forms/           # Dynamic form renderer for JSON Schema forms
│   ├── invoice-builder/        # Visual document designer and 14-format printer compilers
│   ├── template-studio/        # Multi-target template compiler SDK (13 output targets)
│   └── payments-ui/            # Hosted checkout elements and dynamic UPI QR display
├── infra/
│   └── docker/                 # Container definitions, base image digest pins, and compose stacks
├── ops/
│   ├── cli/                    # Cross-platform CLI tooling (`nexus`)
│   ├── migrations/             # Zero-downtime database migration utilities
│   └── audits/                 # Boundary, RLS, and code budget enforcement scripts
├── Makefile                    # Modular GNU Make orchestration (includes mk/*.mk)
├── nexus.ps1                   # Native Windows PowerShell dispatcher
├── pnpm-workspace.yaml         # Node.js workspace configuration
├── pyproject.toml              # Python toolchain and dependency configuration
├── go.work                     # Go workspace definition
└── Cargo.toml                  # Rust workspace definition
```

---

## 4. Code Quality & Structural Ceilings

The repository enforces strict structural ceilings and canonical member layouts:

| Unit / Scope | Target Ceiling | Hard Limit (Fails CI) | Remediation When Exceeded |
| :--- | :---: | :---: | :--- |
| **React Components (`.tsx`)** | 180 lines | 250 lines | Extract presentational child views; move logic to Controller. |
| **TypeScript Controllers (`.ts`)** | 300 lines | 350 lines | Decompose into sub-controllers via delegation. |
| **Django ViewSets (`views.py`)** | 120 lines | 150 lines | Keep as thin coordinators; delegate to command/query handlers. |
| **Django Models (`models.py`)** | 250 lines | 350 lines | Split model module into bounded entity files. |
| **Domain Services (`services.py`)** | 250 lines | 300 lines | Isolate single Command/Query Handlers per file. |
| **Go / Rust Source Files** | 300 lines | 350 lines | Split into submodules or helper packages. |
| **Method / Function Bodies** | 25 lines | 35 lines | Extract private helper methods or strategy objects. |
| **Method Parameters** | $\le 3$ | 4 | Group into typed parameter DTOs. |
| **Cyclomatic Complexity** | $\le 7$ | 10 | Invert conditions with early guard clauses. |
| **Repository Global Ceiling** | — | **400 lines** | Hard ceiling for all non-schema files across runtimes. |

---

## 5. Getting Started

### Prerequisites

- **Python:** 3.12 or newer, with [`uv`](https://github.com/astral-sh/uv)
- **Node.js:** 22 LTS or newer, with [`pnpm`](https://pnpm.io/) (v9+)
- **Go:** 1.23 or newer
- **Rust:** 1.82 or newer, with `cargo`
- **Docker:** Engine 24+ with Buildx and Compose v2

### Setup & Local Development

```bash
# Clone repository
git clone git@github.com:AdarshPBaiju/Nexus.git
cd Nexus

# Install polyglot dependencies
# On Linux / macOS:
make install

# On Windows (PowerShell):
.\nexus.ps1 install

# Start local infrastructure (PostgreSQL 16, Redis, PgBouncer, MinIO, Mailhog)
# On Linux / macOS:
make dev

# On Windows (PowerShell):
.\nexus.ps1 dev
```

Local service ports:
- **Web UI:** `http://localhost:3000`
- **Core API:** `http://localhost:8000`
- **MinIO Console:** `http://localhost:9001`
- **Mailhog:** `http://localhost:8025`

---

## 6. Verification & Automated CI Tooling

```bash
# Code Formatting & Auto-Fixes
nexus format                    # Auto-formats Python (Ruff) and TypeScript (Prettier)
nexus format --check            # CI check asserting zero unformatted files
nexus lint --fix                # Applies safe automated linter fixes

# Architecture & Security Audits
nexus arch code-budget          # Audits file and method line budgets
nexus arch doctor --json        # Validates layer boundaries and import hierarchy
nexus authz audit-coverage      # Asserts 100% of endpoints declare explicit permissions
nexus notif audit-providers     # Audits notification channel adapters and vault credentials
nexus pay audit-gateways        # Verifies payment gateway plugins and webhook handlers
nexus invoice audit-formats     # Validates template compilers across all 14 printer formats

# UI, Theming & Accessibility Audits
nexus fe ui token-audit         # Asserts zero hardcoded color literals across all views
nexus fe ui theme-audit         # Validates WCAG 2.2 AA contrast across Dark and Light themes
nexus fe ui contrast-audit      # Asserts background-aware typography & surface-content pairing
pnpm --filter @nexus/web run test:visual # Executes dual-theme visual regression matrix

# Test Execution
make test-unit                  # Runs backend unit test suites
make test-rls                   # Runs PostgreSQL Row-Level Security isolation tests
make test-concurrency           # Runs financial ledger lock-ordering and concurrency tests
```

---

## 7. 4-Tier Git Branching & Feature Workflow Standards

Project Nexus enforces a strict 4-tier Git branching hierarchy. Direct commits of feature code to `main` are strictly forbidden, and branch names must NEVER start with `phase` or `phase/`.

```
[main] (Production Trunk — Tagged Releases Only)
  ▲
  │ (Release PR & Tagged SemVer)
  │
[development] (Active Polyglot Integration Trunk) ◀────── [Post-Merge Dev Test Gate]
  ▲                                                               ▲
  │ (Milestone Squash-Merge PR)                                   │
  │                                                               │
[feat/<parent-domain-slug>] (Milestone Parent Branches) ──────────┘
  ▲
  │ (Subphase Feature PR)
  │
[feat/<subphase-domain-slug>] (Subphase Feature Branch)
  ▲
  │ (Automated Verification Run)
  │
[test/<subphase-domain-slug>] (Dedicated Subphase Test Branch)
```

### 7.1 Canonical Branch Taxonomy
Every branch MUST match the regular expression:
```regex
^(development|feat\/[a-z0-9\-]+|test\/[a-z0-9\-]+|fix\/[a-z0-9\-]+|perf\/[a-z0-9\-]+|refactor\/[a-z0-9\-]+|chore\/[a-z0-9\-]+)$
```

| Tier / Prefix | Branch Origin | Merge Target | Purpose |
| :--- | :--- | :--- | :--- |
| `development` | `main` | `main` | Primary active polyglot integration trunk |
| `feat/<parent-slug>` | `development` | `development` | Milestone container (e.g. `feat/foundations-monorepo`) |
| `feat/<subphase-slug>` | `feat/<parent>` | `feat/<parent>` | Subphase feature implementation |
| `test/<subphase-slug>` | `feat/<subphase>`| `feat/<parent>` | Dedicated unit, RLS, concurrency & fuzz tests |
| `test/<parent>-integration` | `feat/<parent>` | `feat/<parent>` | Full milestone regression and integration gate |
| `fix/<domain>/<slug>` | `development` | `development` | Targeted bug fix or regression patch |
| `chore/<domain>/<slug>` | `development` | `development` | Toolchain, Docker, or CI workflow updates |

### 7.2 End-to-End Lifecycle & Post-Merge Test Gate
1. **Milestone Container Isolation:** Parent feature branches (e.g. `feat/foundations-monorepo`) branch directly from `development`.
2. **Subphase Branching:** Every subphase todo item branches directly from its parent domain branch (`git checkout -b feat/<subphase-slug> feat/<parent-slug>`).
3. **Dedicated Test Branch:** Test suites are authored on `test/<subphase-slug>` branched from the feature branch.
4. **Milestone Merge & Post-Merge Development Test Gate:** Once all subphases pass their test suites and merge into the parent domain branch, the milestone merges into `development`. A mandatory Post-Merge Test Gate (`make test-all`, `nexus arch doctor --json`, `nexus format --check`) runs on `development` before any release PR is opened to `main`.

---

## 8. License

Proprietary and confidential. All rights reserved.
