<p align="center">
  <img src="web/static/img/brand-logo.png" alt="ApproveHub — Verified Digital Approvals" width="420">
</p>

<p align="center">
  <strong>Next-Gen Institutional Document Approval &amp; Cryptographic Verification Platform</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white" alt="Flask 3.0+"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="https://github.com/ShreeyashSolunke08/ApproveHub/actions"><img src="https://img.shields.io/github/actions/workflow/status/ShreeyashSolunke08/ApproveHub/build-apk.yml?label=Android%20APK%20Build&logo=android" alt="APK Build"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-deployment">Deployment</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-mobile-app">Mobile App</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 📋 Overview

**ApproveHub** is a production-grade institutional document approval and verification platform engineered to replace physical paperwork with a secure, tamper-evident digital workflow. The system automates multi-tier sequential approvals, smartphone-based QR signing, cryptographic PDF stamping via PyMuPDF, and instant public document verification — all accessible from any device, anywhere.

Developed as an **EDI Capstone Project** at the **Department of Information Technology, Vishwakarma Institute of Technology (VIT), Pune** by **Shreeyash Solunke**.

---

## ✨ Features

### Core Workflow Engine
- **Sequential Multi-Tier Approval Pipeline** — Documents flow through configurable approval chains (e.g., Faculty Guide → HOD → Principal) with strict order enforcement.
- **Role-Based Access Control** — Three distinct roles: Applicant (students/staff), Approver (faculty/HOD/principal), and Administrator.
- **14 Institutional Document Types** — Pre-configured templates for bonafide certificates, leave applications, NOC letters, railway concession forms, scholarship verification, LORs, purchase indents, budget approvals, and more.

### Digital Signing & Stamping
- **Smartphone QR Finger Signing** — Approvers scan a dynamic QR code with their phone camera and sign on a touch canvas with their finger. Zero app installation required on the signing device.
- **PyMuPDF Vector Stamping Engine** — Digitally embeds signatures, department seals, and verification QR codes directly onto PDF pages with sub-pixel resolution.
- **SHA-256 Cryptographic Integrity** — Every document receives an immutable cryptographic hash. Any post-approval modification is instantly detected.

### Security & Compliance
- **Bank-Grade PIN Authentication** — 4-digit secure PIN with bcrypt hashing, automatic lockout after 5 failed attempts, and configurable cooldown periods.
- **Tamper-Evident Audit Trail** — Every action (submission, review, approval, rejection, resubmission) is permanently logged with timestamps, IP addresses, and user identity.
- **Per-IP Rate Limiting** — Prevents brute-force attacks on authentication and PIN verification endpoints.
- **Session-Based Authentication** — Secure server-side sessions with configurable expiry and remember-me functionality.

### Public Verification Portal
- **Instant Document Verification** — Anyone (employers, universities, embassies) can verify an approved document by entering its unique approval code (e.g., `AH-26-IT-0412-9LM4`) or scanning the embedded QR code.
- **File Upload Hash Verification** — Upload a PDF to cryptographically verify it matches the original approved document.

### Platform & Accessibility
- **Progressive Web App (PWA)** — Installable on any device (Android, iOS, Windows, macOS) directly from the browser with offline capability.
- **Native Android Application (.APK)** — Compiled via Capacitor and GitHub Actions CI/CD; downloadable directly from the platform.
- **Cloud-Ready Architecture** — One-click deployment to Render with managed PostgreSQL, or any WSGI-compatible hosting platform.
- **Responsive Design** — Optimised for desktop, tablet, and mobile viewports with a frosted-glass modern UI.

---

## 🏗 Architecture

```
ApproveHub/
├── app.py                          # Application factory & Flask initialisation
├── wsgi.py                         # WSGI entry point for production servers
├── init_db.py                      # Database initialisation & seed script
├── backend/
│   ├── __init__.py
│   ├── config.py                   # Configuration (env vars, paths, security params)
│   ├── models.py                   # SQLAlchemy ORM models (5 tables)
│   ├── fixtures.py                 # Institutional seed data & demo accounts
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication (login, register, password reset, PIN)
│   │   ├── documents.py            # Document CRUD, upload, dashboard, APK download
│   │   ├── approvals.py            # Approval workflow, QR signing, batch operations
│   │   ├── verification.py         # Public verification portal & API
│   │   └── admin.py                # Admin dashboard, audit log, settings, user mgmt
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py              # SHA-256 file & record hashing
│       ├── mailer.py               # Async transactional email dispatch
│       ├── rate_limiter.py         # Per-IP rate limiting decorator
│       ├── security.py             # Session management, auth decorators, helpers
│       ├── signature_bridge.py     # Mobile QR signing bridge (LAN session relay)
│       ├── stamping.py             # PyMuPDF PDF stamping engine
│       └── validators.py           # File validation (PDF magic bytes, size limits)
├── web/
│   ├── static/
│   │   ├── css/style.css           # Design system (21 KB, frosted-glass light mode)
│   │   ├── js/app.js               # Client-side logic (cascading selects, canvas, PIN)
│   │   ├── img/                    # App logo, brand logo, favicons, PWA icons
│   │   ├── downloads/              # Compiled Android APK
│   │   ├── manifest.json           # PWA Web App Manifest
│   │   ├── sw.js                   # Service Worker (network-first + cache fallback)
│   │   ├── robots.txt              # Search engine directives
│   │   └── sitemap.xml             # XML Sitemap for Google indexing
│   └── templates/                  # 24 Jinja2 HTML templates
├── uploads/                        # User-uploaded documents & generated assets
│   ├── docs/                       # Original submitted PDFs
│   ├── final/                      # Stamped & approved PDFs
│   ├── assets/                     # Signature PNGs & seal images
│   └── qr/                        # Generated QR code images
├── .github/workflows/
│   └── build-apk.yml              # GitHub Actions CI/CD for Android APK compilation
├── render.yaml                     # Render Blueprint (web service + PostgreSQL)
├── Procfile                        # Heroku/Render process declaration
├── requirements.txt                # Python dependencies
├── capacitor.config.json           # Capacitor native app configuration
└── package.json                    # Node.js dependencies (Capacitor)
```

### Database Schema

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ institutions │────<│    users      │────<│   documents     │
│              │     │              │     │                 │
│ id           │     │ id           │     │ id              │
│ name         │     │ institution_id│    │ institution_id  │
│ code         │     │ name         │     │ applicant_id    │
│ sequential   │     │ email        │     │ title           │
│ require_pin  │     │ role         │     │ document_type   │
│ auto_expire  │     │ department   │     │ file_path       │
└──────────────┘     │ pin_hash     │     │ original_hash   │
                     │ signature    │     │ final_path      │
                     │ stamp_path   │     │ status          │
                     └──────────────┘     │ current_step    │
                                          │ total_steps     │
                           ┌──────────────┴─────────────────┘
                           │
              ┌────────────┴───────┐     ┌──────────────────┐
              │  approval_steps    │     │    timeline       │
              │                    │     │                   │
              │ id                 │     │ id                │
              │ document_id        │     │ document_id       │
              │ approver_id        │     │ user_id           │
              │ step_order         │     │ event             │
              │ status             │     │ details           │
              │ approval_no        │     │ ip_address        │
              │ record_hash        │     │ timestamp         │
              └────────────────────┘     └───────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology |
|:---|:---|
| **Backend** | Python 3.11+, Flask 3.0, SQLAlchemy 2.0, Gunicorn |
| **Database** | PostgreSQL 15+ (production), SQLite (development) |
| **PDF Engine** | PyMuPDF (fitz) — vector stamping, signature embedding, QR overlay |
| **Cryptography** | SHA-256 file hashing, bcrypt password hashing, PBKDF2 PIN hashing |
| **Frontend** | Vanilla HTML5/CSS3/JS, Jinja2 templating, frosted-glass design system |
| **Mobile** | Progressive Web App (Service Workers), Capacitor 6.x (Android APK) |
| **CI/CD** | GitHub Actions (APK compilation), Render Blueprint (cloud deployment) |
| **SEO** | Schema.org JSON-LD, Open Graph, Twitter Cards, XML Sitemap |

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- PostgreSQL 15+ *(production only; SQLite is used by default in development)*

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/ShreeyashSolunke08/ApproveHub.git
cd ApproveHub

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables (optional)
cp .env.example .env
# Edit .env with your configuration

# 5. Initialise the database with seed data
python init_db.py

# 6. Start the development server
python app.py
```

The application will be available at `http://localhost:5000`.

### Demo Credentials

| Role | Username | Password | PIN |
|:---|:---|:---|:---|
| Student (Applicant) | `shreeyash@vit.edu` | `password123` | `1234` |
| Faculty Guide (Approver) | `prof.kulkarni@vit.edu` | `password123` | `1234` |
| HOD IT (Approver) | `dr.patil@vit.edu` | `password123` | `1234` |
| Principal (Approver) | `dr.rao@vit.edu` | `password123` | `1234` |
| Administrator | `admin@vit.edu` | `password123` | `1234` |

> **Note:** These are demonstration credentials seeded by `fixtures.py`. In production, users register with unique institutional email addresses and set their own secure passwords and PINs.

---

## ☁️ Deployment

### Render (Recommended — One-Click Blueprint)

1. Fork or connect `ShreeyashSolunke08/ApproveHub` to your Render account.
2. Navigate to **Dashboard → New → Blueprint**.
3. Select the repository. Render reads `render.yaml` and automatically:
   - Provisions a free managed PostgreSQL database.
   - Installs Python dependencies.
   - Runs `init_db.py` to seed institutional data.
   - Launches a Gunicorn production server with HTTPS.

### Manual Deployment (Any WSGI Host)

```bash
# Set required environment variables
export SECRET_KEY="your-secure-random-key"
export DATABASE_URL="postgresql://user:pass@host:5432/approvehub"

# Install dependencies
pip install -r requirements.txt

# Initialise the database
python init_db.py

# Start with Gunicorn
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

### Environment Variables

| Variable | Required | Description |
|:---|:---|:---|
| `SECRET_KEY` | Yes | Flask session encryption key |
| `DATABASE_URL` | No | PostgreSQL connection string (defaults to SQLite) |
| `GOOGLE_SITE_VERIFICATION` | No | Google Search Console verification token |
| `SMTP_HOST` | No | SMTP server for transactional emails |
| `SMTP_PORT` | No | SMTP port (default: 587) |
| `SMTP_USER` | No | SMTP authentication username |
| `SMTP_PASS` | No | SMTP authentication password |
| `SMTP_SENDER` | No | Sender email address for outbound emails |

---

## 📱 Mobile App

### Android APK

A pre-compiled Android APK is available for direct download from the platform homepage. The APK is built automatically via GitHub Actions CI/CD on every push to `main`.

**Manual Installation:**
1. Download `ApproveHub.apk` from the homepage or the `/download-apk` endpoint.
2. Enable "Install from Unknown Sources" on your Android device.
3. Open the downloaded APK and tap "Install".

### Progressive Web App (PWA)

On any device (Android, iOS, Windows, macOS):
1. Open the application in Chrome, Edge, or Safari.
2. Tap the browser menu → "Add to Home Screen" or "Install App".
3. ApproveHub appears as a standalone app in your application launcher.

---

## 📡 API Reference

### Authentication

| Endpoint | Method | Description |
|:---|:---|:---|
| `/login` | `POST` | Authenticate with email/username and password |
| `/register` | `POST` | Create a new institutional account |
| `/forgot-password` | `POST` | Request password reset email |
| `/reset-password/<token>` | `POST` | Reset password with valid token |
| `/api/pin/verify` | `POST` | Verify 4-digit signing PIN |
| `/api/pin/set` | `POST` | Set or update signing PIN |

### Documents

| Endpoint | Method | Description |
|:---|:---|:---|
| `/documents/upload` | `POST` | Submit a new document for approval |
| `/documents/<id>` | `GET` | View document details and approval status |
| `/documents/<id>/download` | `GET` | Download document with tamper verification |
| `/documents/<id>/preview` | `GET` | Inline PDF preview |

### Verification (Public — No Authentication Required)

| Endpoint | Method | Description |
|:---|:---|:---|
| `/verify/<approval_no>` | `GET` | Public verification page for an approval code |
| `/api/verify/check` | `POST` | JSON API: verify approval code programmatically |
| `/api/verify/upload-hash` | `POST` | Upload PDF to verify cryptographic integrity |

### Administration

| Endpoint | Method | Description |
|:---|:---|:---|
| `/admin` | `GET` | Admin dashboard with system overview |
| `/admin/audit` | `GET` | Full audit log of all system events |
| `/admin/audit/export` | `GET` | Export audit log as CSV |
| `/admin/settings` | `POST` | Update institutional configuration |

---

## 🔒 Security

- **Password Hashing:** Werkzeug PBKDF2-SHA256 with per-user salts.
- **PIN Hashing:** bcrypt with automatic salt generation.
- **File Integrity:** SHA-256 checksums computed at upload and verified before every download/preview.
- **Rate Limiting:** Per-IP throttling on authentication and PIN endpoints.
- **Account Lockout:** Automatic 15-minute lockout after 5 consecutive failed PIN attempts.
- **CSRF Protection:** Flask session-based CSRF tokens on all state-changing forms.
- **Content Security:** PDF magic-byte validation, 10 MB file size limit, extension whitelist.

---

## 🧪 Testing

```bash
# Run the complete test suite
python -m unittest test_system_flow.py test_auth_and_pwa.py test_production_features.py

# Expected output: Ran 11 tests in ~7s — OK
```

| Test Module | Coverage |
|:---|:---|
| `test_system_flow.py` | End-to-end approval pipeline (submit → approve → stamp → verify) |
| `test_auth_and_pwa.py` | Authentication flows, PWA manifest, service worker, icons |
| `test_production_features.py` | SEO endpoints, error handlers, production configuration |

---

## 👨‍💻 Author

<table>
  <tr>
    <td align="center" width="200">
      <strong>Shreeyash Solunke</strong><br>
      <sub>Project Architect &amp; Lead Full-Stack Developer</sub><br>
      <sub>Department of Information Technology</sub><br>
      <sub>Vishwakarma Institute of Technology (VIT), Pune</sub><br><br>
      <a href="https://github.com/ShreeyashSolunke08">GitHub</a>
    </td>
  </tr>
</table>

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **Vishwakarma Institute of Technology, Pune** — Department of Information Technology
- **EDI Capstone Programme 2026** — Entrepreneurship Development & Innovation
- **PyMuPDF** — High-performance PDF manipulation library
- **Capacitor by Ionic** — Native mobile app runtime
- **Render** — Cloud hosting platform with managed PostgreSQL
