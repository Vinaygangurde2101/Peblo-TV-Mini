# Peblo TV Mini — OTT Media Platform & Publishing Engine

[![CI/CD Pipeline](https://github.com/Vinaygangurde2101/Peblo-TV-Mini/actions/workflows/ci.yml/badge.svg)](https://github.com/Vinaygangurde2101/Peblo-TV-Mini/actions)

Hi there! Welcome to my implementation of **Peblo TV Mini**. This project is a complete end-to-end miniature OTT media platform built for Peblo's Full-Stack Platform Engineer take-home challenge.

The solution consists of three core application layers and an underlying automated pipeline:
1. **Backend API (FastAPI + PostgreSQL + SQLAlchemy)**: Manages editorial data, enforces artwork specifications, runs content validation audits, and builds published static catalogue snapshots.
2. **Internal CMS (React + TypeScript + Vite)**: A dedicated content management dashboard for editors and admins to manage shows, seasons, episodes, upload artwork with live validation, preview dry-run diffs, and execute catalog publishes.
3. **Viewer UI (React + TypeScript + Vite)**: A responsive, Netflix-style web app for end-users that reads *exclusively* from the published static catalogue read-model.
4. **Pipeline & Operability**: Fully containerized using `docker compose`, covered by automated Pytest suites, and integrated with GitHub Actions CI/CD workflows.

---

## ⏱️ Time Spent Breakdown

| Component / Task | Time Spent | Focus Areas |
| :--- | :--- | :--- |
| **Part A — Backend API & DB Schema** | ~4 hours | PostgreSQL schema, SQLAlchemy models, JWT auth, RBAC guards, PIL artwork validation, publishing engine, and API routes. |
| **Part B — Internal CMS Dashboard** | ~3.5 hours | Show/episode CRUD, 3-slot artwork uploaders with live aspect ratio validation, validation report view, dry-run diff modal. |
| **Part C — Netflix-Style Viewer UI** | ~3 hours | Hero banner, horizontal section carousels, Season 0 trailer isolation, search/filter, shimmer skeleton loaders. |
| **Part D — Pipeline & Operability** | ~2 hours | `docker-compose.yml`, environment configuration, health endpoints, GitHub Actions CI workflow setup. |
| **Part E — Written Engineering & Trade-offs** | ~1.5 hours | Deep-dive documentation on atomic file replacement, storage abstraction, search scaling, and pre-published static read-models. |
| **Optional Stretch Features** | ~2 hours | Implemented catalogue versioning, one-click rollback engine, and publish dry-run diff generator. |
| **Total** | **~16 hours** | |

---

## 🚀 Quick Start (Docker Compose)

The entire platform can be brought up with a single command using Docker Compose:

```bash
# 1. Clone the repository
git clone https://github.com/Vinaygangurde2101/Peblo-TV-Mini.git
cd Peblo-TV-Mini

# 2. Build and start all services
docker compose up --build
```

### Accessing the Applications:
* **Admin CMS**: [http://localhost:3000](http://localhost:3000)
* **Public Viewer UI**: [http://localhost:3001](http://localhost:3001)
* **FastAPI Backend & Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### Default Test Credentials:
* **Admin Account** (Full CRUD + Publishing Rights + Rollback + Dry-Run):
  * **Email**: `admin@peblo.tv`
  * **Password**: `admin123`
* **Editor Account** (Content CRUD + Artwork Uploads; restricted from publishing):
  * **Email**: `editor@peblo.tv`
  * **Password**: `editor123`

---

## 🏗️ Architecture & Key System Design Decisions

### 1. Separation of Editorial DB vs. Public Read Model
Instead of querying PostgreSQL directly on every public viewer request, I separated the system into two distinct storage tiers:
* **Editorial Database (PostgreSQL 16)**: Serves as the source of truth for internal content editors. It supports draft states, validation flags, multi-language variants, and audit trails.
* **Published Read Model (`storage/catalogue.json`)**: An optimized, static JSON document created by the publishing engine. The public Viewer UI reads *only* this file (or via the `/api/v1/catalog` endpoint), ensuring that viewer traffic spikes can never lock database rows or slow down internal CMS editing.

```
┌──────────────────────────┐          REST / JWT
│ Admin / Content Editor   ├──────────────────────────────┐
└────────────┬─────────────┘                              │
             │                                            ▼
             │                                 ┌────────────────────┐
             │                                 │   CMS React App    │
             │                                 │    (Port 3000)     │
             │                                 └──────────┬─────────┘
             │                                            │ REST API
             ▼                                            ▼
┌──────────────────────────┐                   ┌────────────────────┐
│  FastAPI Backend Engine  │◄──────────────────┤ PostgreSQL 16 DB   │
│       (Port 8000)        │                   │  (Editorial State) │
└────────────┬─────────────┘                   └────────────────────┘
             │
             │ Atomic Publish (os.replace)
             ▼
┌──────────────────────────┐                   ┌────────────────────┐
│     storage/             │◄──────────────────┤  Viewer React App  │
│   catalogue.json         │   Reads Snapshot  │    (Port 3001)     │
└──────────────────────────┘                   └────────────────────┘
```

---

## 🎨 Artwork Validation Specification

Per the `reference.json` specification provided in the challenge, the backend enforces strict dimension, aspect ratio, and file size limits on artwork uploads using Python's `PIL` (Pillow) library:

| Artwork Surface | Dimension Spec | Allowed Aspect Ratio | Max File Size | Allowed Formats |
| :--- | :--- | :--- | :--- | :--- |
| **Poster** | ~600 × 900 px | 2:3 (±5% tolerance) | 200 KB | JPEG, PNG, WebP |
| **Banner** | ~1280 × 720 px | 16:9 (±5% tolerance) | 200 KB | JPEG, PNG, WebP |
| **Thumbnail** | ~640 × 360 px | 16:9 (±5% tolerance) | 200 KB | JPEG, PNG, WebP |

If an image fails validation, the API returns a human-readable HTTP 400 error targeted at non-technical editors (e.g. *"Poster image must be approximately 600x900 (2:3 aspect ratio). Uploaded image is 800x400 with 2.00 aspect ratio."*).

---

## 🛡️ Security & Role-Based Access Control (RBAC)

I implemented JWT-based authentication (`HS256`) with strict role enforcement:
* **`editor` Role**: Can read and mutate shows, seasons, episodes, and upload artwork files.
* **`admin` Role**: Inherits all editor permissions and is uniquely authorized to execute `POST /admin/catalog/publish`, perform dry-run diffs, and invoke snapshot rollbacks.
* Role checking is enforced via FastAPI security dependencies (`require_roles([UserRole.ADMIN])`), returning `HTTP 403 Forbidden` if an editor attempts administrative operations.

---

## 🌟 Optional Stretch Features Implemented (Section 8)

I had sufficient development time remaining and implemented all 3 optional stretch features:

1. **Versioned Catalogue & One-Click Rollback (`POST /admin/catalog/rollback/{run_id}`)**:
   - Every publish run writes an immutable historical copy to `storage/history/catalogue_run_<id>.json`.
   - Admins can instantly restore any historical version live with a single click in the CMS or via API.
2. **Publish Dry-Run Diff Preview (`POST /admin/catalog/publish/dry-run`)**:
   - Before publishing, admins can run a dry-run diff. The engine compares the current valid database state with the active `catalogue.json` snapshot and returns a detailed diff showing added, modified, and removed shows.
3. **Netflix-Style Image Skeleton Loaders**:
   - Built custom CSS `@keyframes shimmer` skeleton loading states into the Viewer UI to maintain a smooth visual layout during slow image loads.

---

## 📝 Part E — Written Engineering Responses & Technical Decisions

### 1. How Publishing Was Made Atomic (and Crash Resilience)
* **Implementation**: Writing directly to `storage/catalogue.json` while readers (viewers) are pulling data risks serving truncated or corrupted JSON. To prevent this, my publishing engine writes the candidate catalogue JSON payload to a temporary file (`catalogue.json.tmp.<uuid>`) inside the storage directory first. Once the payload is completely written and flushed to disk, the engine invokes `os.replace(temp_path, final_path)`.
* **Crash Resilience**: `os.replace` maps directly to the POSIX `rename()` syscall (and `MoveFileEx` on Windows), which is atomic at the filesystem level. If the process, container, or server dies mid-publish *before* `os.replace` executes, the temporary file is abandoned, and the live `catalogue.json` file remains completely untouched. Concurrent readers will strictly see either the previous complete catalogue or the new complete catalogue — never an incomplete state.

### 2. Storage Abstraction (Local Disk to Cloudflare R2 / AWS S3)
* **Current Abstraction**: All storage interactions pass through an abstract base class `BaseStorageService` defined in `app/storage/base.py`:
  ```python
  class BaseStorageService(ABC):
      @abstractmethod
      def save(self, file_data: BinaryIO, filename: str, subfolder: str = "artwork") -> str: pass
      @abstractmethod
      def get(self, relative_path: str) -> Optional[bytes]: pass
      @abstractmethod
      def delete(self, relative_path: str) -> bool: pass
      @abstractmethod
      def exists(self, relative_path: str) -> bool: pass
  ```
* **Migrating to Cloudflare R2**:
  1. Create a `CloudStorageService(BaseStorageService)` class in `app/storage/cloud.py` using `boto3` (since Cloudflare R2 provides an S3-compatible API).
  2. Implement `save` to call `s3_client.upload_fileobj()` and return the public R2 CDN URL.
  3. Update `get_storage_service()` in `app/storage/factory.py` to instantiate `CloudStorageService` when `STORAGE_TYPE == "r2"`.
  4. Zero changes are needed in API controllers (`artwork.py`, `publishing.py`, etc.) because they depend strictly on the `BaseStorageService` interface.

### 3. Search Implementation & Scaling Limits
* **Current Implementation**: `GET /catalog/search?q=&category=&language=&section=` performs in-memory filtering over the loaded published catalogue data structure. It filters show titles, episode titles, categories, sections, and languages using case-insensitive substring matching.
* **Scale Limits**:
  * **0 - 10,000 items**: Sub-10ms response times with negligible CPU overhead.
  * **10,000 - 50,000 items**: Linear scanning (`O(N)`) introduces measurable latency (~50-150ms) and memory pressure on single-threaded workers.
  * **100,000+ items**: In-memory JSON iteration breaks down due to high memory footprint and CPU throttling.
* **Next Steps for Scale**:
  1. **PostgreSQL Trigram Search**: Move search to the database using PostgreSQL's `pg_trgm` extension and GIN indexes (`CREATE INDEX idx_shows_title_trgm ON shows USING gin (title gin_trgm_ops);`).
  2. **Elasticsearch / OpenSearch**: At true OTT streaming scale (1M+ catalogue items), index published catalogue snapshots into Elasticsearch. Use multi-match fuzzy queries and dynamic aggregations for fast faceted search.

### 4. Serving Pre-Published Static Catalogue vs. Direct DB Queries Per Request
* **Why Pre-Publish?**:
  * **Massive Scale & Resilience**: Static JSON files can be served directly from CDN edge locations (Cloudflare, CloudFront) with sub-10ms response times globally. Database CPU/memory is protected from public traffic spikes during popular show releases.
  * **Guaranteed Content Integrity**: Only content that has passed validation audits (duration present, valid artwork, complete language groups) gets published. Viewers never encounter broken episodes mid-edit.
* **Where it Bites You (Trade-offs)**:
  * **Eventual Consistency**: Content edited in the CMS is not immediately visible to viewers until an Admin triggers a publish run.
  * **Monolithic File Size**: As the catalogue grows to tens of thousands of shows, downloading a single `catalogue.json` payload becomes heavy. To fix this at scale, the publisher should generate paginated or section-based static JSON files (e.g. `catalogue/sections/trending.json`).

### 5. What Was Left Out & AI Usage Disclosure
* **What I Left Out & Why**:
  * *Live Video Transcoding / Streaming*: Transcoding MP4s into HLS/DASH streams was out of scope for a platform engineering take-home focused on metadata management and catalogue publishing.
  * *Live Cloudflare R2 Provisioning*: Used local disk storage wrapped behind `BaseStorageService` to keep setup friction-free for reviewers running `docker compose up`.
* **AI Tool Usage Disclosure**:
  * I used AI pair-programming assistants (Gemini 3.6 Flash / Antigravity) to speed up repetitive boilerplate (FastAPI Pydantic schemas, SQLAlchemy model definitions, initial unit test stubs, and Markdown formatting).
  * **Where I Accepted Output**: Data model typings, standard Pydantic validation schemas, basic CSS shimmer keyframes, and initial test fixture structure.
  * **Where I Rejected / Refactored Output**:
    * AI initially proposed direct file writes (`open('w')`) for publishing; I rejected this and implemented temporary file writing + `os.replace` for atomic guarantees.
    * AI generated generic error messages for image validation; I refactored them to include exact uploaded dimensions vs expected dimensions so non-technical editors can fix errors easily.
    * AI omitted transaction safety in Pytest fixtures; I added explicit transaction rollbacks and isolated SQLite runner databases to prevent test pollution.

---

## 🧪 Automated Testing

I wrote 18 Pytest unit and integration tests covering all critical paths:

```bash
# Run backend tests inside Docker
docker compose exec backend python -m pytest -v
```

### Test Suite Highlights (18/18 Passing):
* `test_auth.py`: JWT login, password hashing, and role guard enforcement.
* `test_artwork_validation.py`: Pillow dimension, aspect ratio, file size ceilings, and path traversal security.
* `test_crud_apis.py`: Show/episode CRUD operations and unique constraint enforcement.
* `test_publishing_engine.py`: Atomic `os.replace` publishing, Season 0 exclusion, language grouping, dry-run diff preview, and version rollback.
* `test_validation_report.py`: Pre-flight audit detection for un-publishable items.
* `test_e2e_integration.py`: Complete lifecycle from CMS show creation to viewer static catalog ingestion.

---

## 📽️ Demo Video Checklist for Evaluators

When reviewing the submission or watching the video demo:
1. **CMS Editor Flow**: Log in as `editor@peblo.tv` -> Create show -> Upload artwork -> See dimension error callout -> Correct artwork.
2. **Permission Guard**: Try accessing `/publish` as Editor -> View permission denied alert.
3. **Admin Flow**: Log in as `admin@peblo.tv` -> View `/validation` readiness report -> Preview Dry-Run Diff -> Click **Publish Catalogue Now**.
4. **Rollback**: Open Publish History -> Click **Rollback** on a past run -> Verify catalogue state restored.
5. **Viewer UI**: Open `http://localhost:3001` -> Browse hero banner, section rows, trailer section isolation, search filters, and language variant selectors.
