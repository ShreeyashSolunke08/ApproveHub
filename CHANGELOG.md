# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-11-06

### Added
- **Sequential Multi-Tier Approval Engine** — Configurable approval chains with strict order enforcement across Faculty, HOD, and Principal tiers.
- **Smartphone QR Finger Signing** — Zero-install mobile signing bridge with dynamic QR session relay and HTML5 touch canvas.
- **PyMuPDF Vector Stamping Engine** — Embeds digital signatures, department seals, and verification QR codes directly onto PDF pages.
- **SHA-256 Cryptographic Integrity** — Immutable file hashing with tamper detection on every download and preview operation.
- **Public Verification Portal** — Approval code lookup and file upload hash verification accessible without authentication.
- **Institutional Account System** — Registration, login, password reset (email token), profile management with avatar upload.
- **Bank-Grade PIN Security** — bcrypt-hashed 4-digit PINs with automatic lockout after 5 failed attempts.
- **Admin Dashboard** — System overview, document management, user administration, hierarchy builder, audit log with CSV export.
- **14 Document Type Templates** — 7 student document types and 7 staff/faculty document types pre-configured.
- **Progressive Web App (PWA)** — Service worker with network-first caching, web app manifest, and installability on all platforms.
- **Native Android Application** — Capacitor-compiled APK with GitHub Actions CI/CD automated builds.
- **Direct APK Download** — `/download-apk` endpoint serving the compiled Android application.
- **Transactional Email System** — Async email dispatch for password resets, approval notifications, and pending review alerts.
- **Per-IP Rate Limiting** — In-memory rate limiting on authentication and PIN verification endpoints.
- **Comprehensive SEO** — robots.txt, XML sitemap, Schema.org JSON-LD structured data, Open Graph and Twitter Card meta tags.
- **Cloud Deployment Blueprint** — Render.yaml with managed PostgreSQL provisioning and automated initialisation.
- **Homepage Portal** — Institutional landing page with direct login console, demo credential switcher, and project architect profile.
- **Tamper-Evident Audit Trail** — Complete event logging with timestamps, IP addresses, and user identity tracking.
- **Batch Approval Operations** — Faculty can approve multiple pending documents simultaneously with single PIN verification.
- **Compliance Resubmission Workflow** — Rejected documents can be corrected and resubmitted by applicants.
- **11 Automated Tests** — End-to-end approval pipeline, authentication flows, PWA assets, and production feature validation.

### Security
- Werkzeug PBKDF2-SHA256 password hashing with per-user salts.
- PDF magic-byte validation and 10 MB file size enforcement.
- Session-based authentication with configurable expiry.
- Automatic account lockout with 15-minute cooldown periods.

---

## [0.1.0] — 2026-11-03

### Added
- Initial project scaffolding and database schema design.
- Basic Flask application factory with SQLAlchemy ORM integration.
- Core document upload and approval step creation.
