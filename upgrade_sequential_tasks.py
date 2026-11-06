import subprocess
import time
import sys

REPO = "ShreeyashSolunke08/ApproveHub"

USERS = {
    "Shreeyash": "ShreeyashSolunke08",
    "Shravani": "shravaniborse9",
    "Shreya Sutar": "SHREE7682",
    "Shreya Loya": "loyashreya200408",
}

ALL_MEMBERS = list(USERS.values())

# Map step 1..47 to existing GitHub issue number and full rich details
STEPS_DATA = {
    1: {
        "issue": 50,
        "title": "Step 1: Install development tools and set up local environments",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "3 pts (~3 hours each)",
        "why": "Ensures all four team members share identical runtimes and dependencies, preventing 'works on my machine' defects.",
        "what": "Install core programming languages, IDEs, database browsers, and API testing tools required for each member's specialized role.",
        "how": [
            "Install Python 3.11+ on all machines (ensure 'Add Python to PATH' is checked on Windows).",
            "Install VS Code with recommended extensions: Python, SQLite Viewer, Flutter/Dart, and Live Server.",
            "Install Git and Postman on all laptops.",
            "Shreya Sutar installs Flutter SDK and Android Studio with virtual device/USB debugging enabled.",
            "Shreeyash, Shravani, and Shreya Loya install DB Browser for SQLite to visually inspect database state.",
            "Open terminal and verify: run `python --version`, `git --version`, and `flutter --version` (for Shreya Sutar).",
            "Create or verify GitHub accounts for all four team members and share usernames."
        ],
        "done_when": "All team members successfully run their respective CLI version commands and are verified collaborators on the repository.",
        "references": [
            "[Python Official Download](https://www.python.org/downloads/)",
            "[VS Code Documentation](https://code.visualstudio.com/docs)",
            "[Flutter Install Guide](https://docs.flutter.dev/get-started/install)",
            "[DB Browser for SQLite](https://sqlitebrowser.org/)"
        ],
        "needs": "Starting point (no prerequisites)",
        "unlocks": "Step 2 (Repo creation), Step 3 (Basics study)",
        "parallel_fallback": "If tool downloads are delayed by network, begin studying role-specific documentation (Flask, Dart, or SQL basics).",
        "starter_code": None
    },
    2: {
        "issue": 8,
        "title": "Step 2: Initialize shared GitHub repository and project folder structure",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "3 pts (~3 hours)",
        "why": "Provides a single source of truth for the entire team to collaborate without overwrite conflicts.",
        "what": "Establish the standardized repository directory layout, virtual environment, and dependency requirements file.",
        "how": [
            "Create root directories: `backend/`, `web/`, `mobile/`, `docs/`, `uploads/`, `uploads/assets/`.",
            "Create a clean virtual environment: `python -m venv venv` and activate it.",
            "Install primary backend libraries: `pip install flask flask-sqlalchemy pillow pymupdf reportlab qrcode`.",
            "Export locked dependencies using `pip freeze > requirements.txt`.",
            "Create `.gitignore` ignoring `venv/`, `uploads/`, `*.pyc`, `__pycache__/`, `.env`, and IDE config folders.",
            "Commit initial scaffold and push to GitHub `main` branch.",
            "Help teammates clone the repo and create personal branches: `shravani-web`, `shreya-mobile`, `shreya-qa`."
        ],
        "done_when": "Repository contains standard folder structure, requirements.txt, and each teammate pushes a test commit from their branch.",
        "references": [
            "[GitHub Pro Git Book - Branching](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)",
            "[Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)"
        ],
        "needs": "Step 1",
        "unlocks": "Step 4 (Database design), Step 7 (Sample fixtures)",
        "parallel_fallback": "If waiting for teammates to clone, begin drafting database schema diagrams on draw.io.",
        "starter_code": None
    },
    3: {
        "issue": 51,
        "title": "Step 3: Study week 1 fundamentals and practice role-specific tasks",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "3 pts (~3 hours each)",
        "why": "Equips each team member with essential foundational knowledge before starting production code.",
        "what": "Study HTTP fundamentals, Git branching workflows, and module-specific starter tutorials.",
        "how": [
            "Everyone: Review HTTP methods (GET, POST, PUT, DELETE), status codes (200, 201, 400, 401, 403, 404, 500), and JSON structure.",
            "Shreeyash: Study SQLAlchemy relationships (one-to-many, foreign keys) and SQLite basics.",
            "Shravani: Review Flask routing, request handling, and responsive HTML/CSS Flexbox layouts.",
            "Shreya Sutar: Review Dart language syntax, Flutter widget tree (Stateless vs Stateful), and basic layouts.",
            "Shreya Loya: Review REST API design principles, OpenAPI specifications, and test case drafting.",
            "Everyone: Send a test GET request to a public API (e.g., JSONPlaceholder or GitHub API) using Postman."
        ],
        "done_when": "Each member builds one mini practice script or layout demonstrating their role's core basics.",
        "references": [
            "[MDN - HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)",
            "[Flask Quickstart Guide](https://flask.palletsprojects.com/en/3.0.x/quickstart/)",
            "[Flutter Widget Catalog](https://docs.flutter.dev/ui/widgets)"
        ],
        "needs": "Step 1",
        "unlocks": "Step 6 (UI wireframes), Step 8 (Backend models)",
        "parallel_fallback": "Share helpful tutorials, YouTube links, and cheat sheets in the team chat.",
        "starter_code": None
    },
    4: {
        "issue": 9,
        "title": "Step 4: Design relational database schemas and entity relationships",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "Database design is the backbone of the application. Designing it accurately now prevents costly data refactoring later.",
        "what": "Draft complete relational schemas for Users, Documents, ApprovalSteps, and Timeline tables.",
        "how": [
            "Draw Entity-Relationship (ER) diagram in draw.io with 4 core tables:",
            "1. `users`: `id`, `name`, `email`, `password_hash`, `role` (applicant/approver/admin), `post`, `department`, `signature_path`, `stamp_path`, `seal_path`, `pin_hash`.",
            "2. `documents`: `id`, `title`, `file_path`, `original_hash`, `final_path`, `final_hash`, `applicant_id`, `status`, `current_step`, `created_at`.",
            "3. `approval_steps`: `id`, `document_id`, `approver_id`, `step_order`, `status` (waiting/pending/approved/compliance), `remark`, `approval_no`, `acted_at`.",
            "4. `timeline`: `id`, `document_id`, `event`, `time`.",
            "Define foreign key constraints and cascade rules (e.g., deleting a document deletes associated approval steps and timeline).",
            "Present diagram to teammates to lock attribute names across frontend and backend."
        ],
        "done_when": "ER diagram PNG and draw.io file saved in `docs/architecture/` with team signoff.",
        "references": [
            "[SQLAlchemy 2.0 Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)",
            "[Draw.io Diagramming Tool](https://app.diagrams.net/)"
        ],
        "needs": "Step 2",
        "unlocks": "Step 5 (API list), Step 8 (Database models)",
        "parallel_fallback": "If team review is pending, draft the Python SQLAlchemy model classes in a scratch file.",
        "starter_code": None
    },
    5: {
        "issue": 34,
        "title": "Step 5: Write comprehensive REST API specification catalog",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Establishes a strict contract between backend and client applications (web and mobile), preventing payload format mismatches.",
        "what": "Document all 16+ REST endpoints with HTTP methods, request bodies, query parameters, status codes, and JSON response samples.",
        "how": [
            "Review the database schemas from Step 4.",
            "Create markdown document `docs/api_specifications.md` listing:",
            "• Auth endpoints: `POST /api/register`, `POST /api/login`, `POST /api/pin/set`, `POST /api/pin/verify`.",
            "• Document endpoints: `POST /api/documents/upload`, `GET /api/documents`, `GET /api/documents/{id}/timeline`.",
            "• Workflow endpoints: `POST /api/documents/{id}/chain`, `GET /api/approvals/pending`, `POST /api/steps/{id}/approve`.",
            "• Verification & Admin endpoints: `GET /api/verify/{approval_no}`, `GET /api/admin/users`, `GET /api/admin/audit-logs`.",
            "Review definitions with Shreeyash, Shravani, and Shreya Sutar."
        ],
        "done_when": "`docs/api_specifications.md` is committed and approved by frontend, mobile, and backend developers.",
        "references": [
            "[RESTful API Guidelines](https://restfulapi.net/)",
            "[OpenAPI Specification Guide](https://swagger.io/specification/)"
        ],
        "needs": "Step 4",
        "unlocks": "Step 11 (Web pages), Step 12 (Mobile auth)",
        "parallel_fallback": "If Step 4 schema changes slightly, write standard auth and profile specs first.",
        "starter_code": None
    },
    6: {
        "issue": 26,
        "title": "Step 6: Design full UI/UX wireframes in Figma for web and mobile",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "8 pts (~8 hours)",
        "why": "Visual wireframes ensure visual consistency, intuitive navigation, and prevent rework during frontend development.",
        "what": "Design complete desktop and mobile mockups covering all user roles (Applicant, Approver, Administrator).",
        "how": [
            "Select cohesive design system: color palette (primary blue, emerald approved, amber pending, crimson rejected), typography, button styles.",
            "Design Web screens: Login/Register, Applicant Dashboard, Document Upload & Approver Selection Canvas, Approver Review Screen, Public Verification Portal, Admin Dashboard.",
            "Design Mobile screens: Splash screen, Login, Mobile Feed, Document Action Drawer, Camera QR Scanner, Biometric Authentication Prompt.",
            "Export UI asset pack (SVG icons, logos) into `docs/design_assets/` and share Figma link."
        ],
        "done_when": "All screens are designed in Figma, shared with team members, and agreed upon.",
        "references": [
            "[Figma Best Practices](https://help.figma.com/hc/en-us/articles/360040450173-Figma-for-beginners)",
            "[Material Design Guidelines](https://m3.material.io/)"
        ],
        "needs": "Step 3",
        "unlocks": "Step 11 (Web UI), Step 12 (Flutter UI)",
        "parallel_fallback": "Start with core login and dashboard wireframes while refining secondary pages later.",
        "starter_code": None
    },
    7: {
        "issue": 17,
        "title": "Step 7: Prepare realistic dummy test data and sample file fixtures",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "deadline": "November 9, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "3 pts (~3 hours)",
        "why": "Enables rapid testing of uploads, cryptographic hashing, and approval workflows from Day 1 without waiting for production data.",
        "what": "Generate realistic test users, sample PDF petitions/certificates, and transparent authority stamp PNG fixtures.",
        "how": [
            "Create JSON seed file `backend/seeds/dummy_users.json` with 10 accounts: 3 applicants, 6 approvers (HOD, Dean, Principal, Registrar, Director), 1 admin.",
            "Prepare 5 sample scanned PDF and image documents (e.g., `bonafide_letter.pdf`, `leave_request.pdf`).",
            "Create 3 transparent background PNG images: `sample_signature.png`, `sample_stamp.png`, `sample_seal.png`.",
            "Store all fixtures in `uploads/sample_fixtures/` with clean naming conventions."
        ],
        "done_when": "Sample fixtures folder exists in the repository with valid PDF and transparent PNG files ready for testing.",
        "references": [
            "[Mockaroo Data Generator](https://www.mockaroo.com/)",
            "[Remove.bg for transparent PNGs](https://www.remove.bg/)"
        ],
        "needs": "Step 2",
        "unlocks": "Step 13 (Document upload), Step 26 (Stamping engine)",
        "parallel_fallback": "If database schema is being finalized, create generic image and PDF test files first.",
        "starter_code": None
    },
    8: {
        "issue": 10,
        "title": "Step 8: Implement SQLAlchemy database models in code",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "deadline": "November 16, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "Translates the relational design into Python ORM models, providing database persistence for the whole system.",
        "what": "Code the User, Document, ApprovalStep, and Timeline models with relationships in `backend/models.py`.",
        "how": [
            "In `backend/models.py`, define `User` model with fields for auth, role, and asset paths.",
            "Define `Document` model with foreign key to `User.id` (applicant), status tracking, and hash fields.",
            "Define `ApprovalStep` model linked to `Document` and `User` (approver), order index, and step status.",
            "Define `Timeline` model recording unalterable audit log events.",
            "In `backend/app.py`, initialize Flask-SQLAlchemy with SQLite database URI (`sqlite:///approvehub.db`).",
            "Execute `db.create_all()` and inspect generated SQLite tables using DB Browser for SQLite."
        ],
        "done_when": "Database creates without error and all 4 tables with correct columns and foreign keys are verified.",
        "references": [
            "[Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)",
            "[SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)"
        ],
        "needs": "Step 4",
        "unlocks": "Step 9 (Auth routes), Step 10 (RBAC)",
        "parallel_fallback": "If adjustments to fields are requested, update schema definition and recreate test database.",
        "starter_code": None
    },
    9: {
        "issue": 18,
        "title": "Step 9: Build user registration and login APIs with password hashing",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "deadline": "November 16, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Provides secure identity verification and protects passwords from exposure using industry-standard one-way hashing.",
        "what": "Build `POST /api/register` and `POST /api/login` endpoints returning user session/token and role.",
        "how": [
            "Use `werkzeug.security.generate_password_hash` with `pbkdf2:sha256` or `scrypt` when registering users.",
            "Implement email uniqueness check and validate password strength (min 6 characters).",
            "In `POST /api/login`, verify password using `check_password_hash`.",
            "Return JSON response containing user details, assigned role, and session auth token/JWT.",
            "Verify all success and failure cases (wrong password, unknown email) in Postman."
        ],
        "done_when": "Postman tests verify user registration, successful login with token return, and 401 response on incorrect password.",
        "references": [
            "[Werkzeug Security Utilities](https://werkzeug.palletsprojects.com/en/3.0.x/utils/#module-werkzeug.security)",
            "[PyJWT Documentation](https://pyjwt.readthedocs.io/)"
        ],
        "needs": "Step 8",
        "unlocks": "Step 10 (Role control), Step 11 (Web login)",
        "parallel_fallback": "If database connection is being configured, write standalone hashing test script.",
        "starter_code": None
    },
    10: {
        "issue": 19,
        "title": "Step 10: Implement role-based access control (RBAC) decorators",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "deadline": "November 16, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "Strictly isolates user permissions so applicants cannot approve requests, and approvers can only act on their assigned documents.",
        "what": "Create reusable Python function decorators to guard protected Flask routes by role.",
        "how": [
            "Write `@requires_role(*allowed_roles)` decorator inspecting request header/token.",
            "If user role is not authorized for the endpoint, abort with `403 Forbidden` JSON response.",
            "Write helper `@login_required` verifying active session or valid token.",
            "Write tests asserting applicants cannot access approver or admin routes."
        ],
        "done_when": "Protected endpoint returns 200 for authorized roles and 403 Forbidden for unauthorized requests.",
        "references": [
            "[Python Decorators Guide](https://realpython.com/primer-on-python-decorators/)",
            "[Functools wraps](https://docs.python.org/3/library/functools.html#functools.wraps)"
        ],
        "needs": "Step 9",
        "unlocks": "Step 13 (Upload validation), Step 36 (Admin routes)",
        "parallel_fallback": "If token format is being adjusted, test decorator using simulated request contexts.",
        "starter_code": None
    },
    11: {
        "issue": 20,
        "title": "Step 11: Create base responsive layout, login and registration web pages",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "deadline": "November 16, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "Establishes the visual shell and primary user entry point for all browser-based users.",
        "what": "Code responsive HTML5/CSS3 templates for Navbar, Footer, Login, and Registration with JavaScript fetch calls.",
        "how": [
            "Create `web/base.html` with clean responsive navbar, branding logo, navigation links, and footer.",
            "Build `web/login.html` and `web/register.html` following the Figma color theme.",
            "Write client-side form validation (empty fields, valid email regex, matching password confirmation).",
            "Use `fetch()` to call `POST /api/login` and store the token in browser `localStorage` / `sessionStorage`.",
            "Redirect user to appropriate dashboard upon successful login based on role."
        ],
        "done_when": "Users can register and log in via browser, receiving visual error toasts or redirecting to dashboard.",
        "references": [
            "[MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)",
            "[CSS Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)"
        ],
        "needs": "Step 5, Step 6, Step 9",
        "unlocks": "Step 19 (Web dashboards)",
        "parallel_fallback": "If backend login API is still compiling, test UI against mock JSON endpoints or local variables.",
        "starter_code": None
    },
    12: {
        "issue": 27,
        "title": "Step 12: Initialize Flutter mobile project and build app authentication UI",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "deadline": "November 16, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Validates the cross-platform mobile pipeline early to ensure Android builds and networking function smoothly.",
        "what": "Configure Flutter project structure, dependencies, state handling, and Login/Register mobile screens.",
        "how": [
            "Initialize Flutter application in `mobile/`: `flutter create approvehub_app`.",
            "Add dependencies to `pubspec.yaml`: `http`, `flutter_secure_storage`, `shared_preferences`.",
            "Build mobile authentication screens adhering to Figma designs.",
            "Connect HTTP service calling `POST /api/login` and persist session token securely using `FlutterSecureStorage`.",
            "Test build on Android emulator or physical device via USB debugging."
        ],
        "done_when": "App runs on emulator/phone, submits login form to backend, and stores auth credentials on success.",
        "references": [
            "[Flutter Secure Storage](https://pub.dev/packages/flutter_secure_storage)",
            "[Flutter Networking Tutorial](https://docs.flutter.dev/cookbook/networking/fetch-data)"
        ],
        "needs": "Step 5, Step 6, Step 9",
        "unlocks": "Step 20 (Mobile dashboards)",
        "parallel_fallback": "If emulator setup is slow, build with Flutter desktop/web runner for fast UI iteration.",
        "starter_code": None
    },
    13: {
        "issue": 21,
        "title": "Step 13: Build secure document upload API with file type and size validation",
        "phase": "Phase 1 - Foundation",
        "week": "Week 3",
        "deadline": "November 23, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Prevents unauthorized file execution, server disk saturation, and file path traversal attacks.",
        "what": "Build `POST /api/documents/upload` accepting multipart/form-data for PDF, PNG, and JPG documents under 10MB.",
        "how": [
            "Configure upload directory `uploads/documents/`.",
            "Verify file extension against whitelist: `pdf`, `png`, `jpg`, `jpeg`.",
            "Sanitize filename using `werkzeug.utils.secure_filename` and prefix with unique UUID timestamp.",
            "Check content size limit (max 10MB) and return 413 Payload Too Large if exceeded.",
            "Create initial `Document` record in SQLite with status `in_progress` and step `1`.",
            "Return document ID and saved path in JSON response."
        ],
        "done_when": "Uploading a 5MB PDF creates a row in DB and stores the file; uploading an `.exe` or 15MB file returns 400/413 error.",
        "references": [
            "[Flask Upload Handling](https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/)",
            "[OWASP File Upload Security](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)"
        ],
        "needs": "Step 9, Step 10",
        "unlocks": "Step 14 (SHA-256 fingerprinting)",
        "parallel_fallback": "If client form is not ready, thoroughly test the endpoint using Postman multipart/form-data requests.",
        "starter_code": None
    },
    14: {
        "issue": 11,
        "title": "Step 14: Implement SHA-256 cryptographic fingerprint generation on upload",
        "phase": "Phase 1 - Foundation",
        "week": "Week 3",
        "deadline": "November 23, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "Establishes mathematical proof of document authenticity at the moment of upload for future tamper detection.",
        "what": "Build `utils/hashing.py` with chunk-based SHA-256 calculation and attach hash to uploaded documents.",
        "how": [
            "Write `sha256_file(filepath)` reading file in 8192-byte binary chunks to handle large files efficiently.",
            "Calculate 64-character hexadecimal digest.",
            "Integrate into upload workflow: calculate hash immediately after file write and save in `documents.original_hash`.",
            "Write `verify_file(filepath, stored_hash)` returning boolean match result.",
            "Write automated unit test: modify 1 single character/byte in a test file and confirm `verify_file()` returns `False`."
        ],
        "done_when": "Every uploaded document has a stored 64-character hash; modifying any byte of the file is detected as tamper.",
        "references": [
            "[Python hashlib Documentation](https://docs.python.org/3/library/hashlib.html)",
            "[SHA-256 Cryptographic Standard](https://en.wikipedia.org/wiki/SHA-2)"
        ],
        "needs": "Step 13",
        "unlocks": "Step 16 (Approval chain), Step 24 (Tamper verification)",
        "parallel_fallback": "If upload route is undergoing edits, test hashing against static dummy PDF fixtures from Step 7.",
        "starter_code": None
    },
    15: {
        "issue": 35,
        "title": "Step 15: Build approver profile assets API (signature, stamp, and seal PNGs)",
        "phase": "Phase 1 - Foundation",
        "week": "Week 3",
        "deadline": "November 23, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Provides the official graphical assets (signatures and department seals) required to stamp documents upon approval.",
        "what": "Build `POST /api/profile/assets` and `GET /api/profile` endpoints for approvers to manage signature, stamp, and seal images.",
        "how": [
            "Accept 3 multipart image files: `signature`, `stamp`, `seal`.",
            "Validate format: transparent PNG only, max 2MB per image.",
            "Save assets to dedicated directory `uploads/assets/{user_id}/`.",
            "Update user record with asset file paths in `users` table.",
            "Build `GET /api/profile` returning current user data and asset preview URLs."
        ],
        "done_when": "Approver uploads their 3 PNG assets, paths are recorded in DB, and non-PNG uploads are rejected.",
        "references": [
            "[Flask Request Files](https://flask.palletsprojects.com/en/3.0.x/api/#flask.Request.files)",
            "[Pillow Image Verification](https://pillow.readthedocs.io/en/stable/reference/Image.html)"
        ],
        "needs": "Step 9, Step 10",
        "unlocks": "Step 26 (Document stamping)",
        "parallel_fallback": "If approver dashboard UI is in design, test with sample signatures using Postman.",
        "starter_code": None
    },
    16: {
        "issue": 36,
        "title": "Step 16: Build approver selection and multi-step approval chain API",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Allows applicants to define the exact hierarchy and routing order through which the document must travel.",
        "what": "Build `GET /api/approvers` search API and `POST /api/documents/{id}/chain` routing endpoint.",
        "how": [
            "Build `GET /api/approvers?post=HOD&department=IT` returning filtered list of authorized approver accounts.",
            "Build `POST /api/documents/{id}/chain` receiving an ordered list of approver user IDs.",
            "Validate that selected approvers exist and have `approver` role.",
            "Create sequential `ApprovalStep` records with `step_order = 1, 2, 3...`.",
            "Set step 1 status to `pending`, and all subsequent steps to `waiting`."
        ],
        "done_when": "Submitting a chain of 3 approvers creates 3 rows in DB with step 1 pending and steps 2-3 waiting.",
        "references": [
            "[SQLAlchemy Filtering and Sorting](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html)",
            "[REST Nested Resource Patterns](https://restfulapi.net/resource-naming/)"
        ],
        "needs": "Step 14",
        "unlocks": "Step 17 (Sequence logic)",
        "parallel_fallback": "If upload integration is in progress, test chaining using existing dummy document IDs.",
        "starter_code": None
    },
    17: {
        "issue": 12,
        "title": "Step 17: Implement sequential workflow state machine logic",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "8 pts (~8 hours)",
        "why": "Enforces strict hierarchy: a document must never be accessible to Approver 2 until Approver 1 has officially signed.",
        "what": "Implement the core state transition engine advancing the approval chain step-by-step.",
        "how": [
            "Write `advance_approval_step(document_id, approver_id, remark)` in `backend/services/workflow.py`.",
            "Check that the active step belongs to `approver_id` and has status `pending` (reject all others with 403).",
            "Mark current step `approved` and record action timestamp.",
            "Query next sequential step (`step_order + 1`):",
            "• If next step exists: update its status to `pending` and update `document.current_step`.",
            "• If no steps remain: update `document.status` to `fully_approved`.",
            "Commit database transaction safely with rollback protection."
        ],
        "done_when": "Approver 2 cannot see or act until Approver 1 approves; final approver approval transitions document to `fully_approved`.",
        "references": [
            "[State Pattern in Python](https://refactoring.guru/design-patterns/state/python/example)",
            "[Database Transactions in SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)"
        ],
        "needs": "Step 16",
        "unlocks": "Step 18 (Approver actions)",
        "parallel_fallback": "Sketch the state transition diagram on paper or draw.io to verify all edge cases before coding.",
        "starter_code": None
    },
    18: {
        "issue": 13,
        "title": "Step 18: Build approver action endpoints (Approve, Keep Pending, Request Compliance)",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "7 pts (~7 hours)",
        "why": "Provides authorities with the complete tri-state decision model used in real-world institutional administration.",
        "what": "Build `POST /api/steps/{id}/approve`, `/pending`, and `/compliance` endpoints with remark logging and unique approval numbering.",
        "how": [
            "Implement unique approval number generator: `APH-{year}-{document_id:05d}-{step_order}`.",
            "**Approve:** Assign approval number, mark approved, and trigger `advance_approval_step` (Step 17).",
            "**Pending:** Keep document at current step, store approver's note/remark, and update timestamp.",
            "**Compliance:** Transition step to `compliance_required`, set document status to `compliance_required`, and record requirement note for applicant.",
            "Log all actions into the unalterable `Timeline` table."
        ],
        "done_when": "All three endpoints respond with 200 in Postman, assign unique approval numbers on approve, and update database records.",
        "references": [
            "[REST API Error Handling](https://restfulapi.net/http-status-codes/)",
            "[Python Datetime Formatting](https://docs.python.org/3/library/datetime.html)"
        ],
        "needs": "Step 17",
        "unlocks": "Step 19 (Web dashboards), Step 22 (Compliance flow)",
        "parallel_fallback": "Test endpoints with curl or Postman test scripts while frontend developers finalize UI.",
        "starter_code": None
    },
    19: {
        "issue": 22,
        "title": "Step 19: Build working web dashboards for applicants and approvers",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "9 pts (~9 hours)",
        "why": "Provides the primary everyday interface for users to initiate requests and for authorities to take action.",
        "what": "Develop applicant portal (upload form, approver selector, status badges) and approver action dashboard.",
        "how": [
            "Build `web/applicant_dashboard.html`: list of applicant's documents with colored status pills (Approved, Pending, Compliance).",
            "Add interactive upload dialog with multi-select dropdown for choosing approver chain by department.",
            "Build `web/approver_dashboard.html`: inbox of pending documents awaiting current approver's signature.",
            "Add document preview modal with Approve, Keep Pending, and Send Compliance buttons and remark input textarea.",
            "Wire frontend actions to backend APIs with `fetch()` and display visual feedback toasts."
        ],
        "done_when": "Applicant can upload and select approvers; logged-in approver sees document and executes Approve or Compliance action from browser.",
        "references": [
            "[Bootstrap / Tailwind Badge Components](https://tailwindui.com/components/application-ui/elements/badges)",
            "[JavaScript Async/Await](https://javascript.info/async-await)"
        ],
        "needs": "Step 18",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "If backend actions are undergoing review, use mock JSON responses to finish layout and badge styling.",
        "starter_code": None
    },
    20: {
        "issue": 28,
        "title": "Step 20: Build mobile applicant and approver interface screens in Flutter",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "9 pts (~9 hours)",
        "why": "Enables busy college authorities and students to review and approve documents directly from smartphones.",
        "what": "Build Flutter applicant feeds, document submission flow, and approver review screens with camera/gallery integration.",
        "how": [
            "Integrate `image_picker` package to allow uploading scanned papers via mobile camera or photo gallery.",
            "Build `ApplicantDashboard` with pull-to-refresh `ListView` showing submission statuses.",
            "Build `ApproverInbox` showing pending approvals with badge counts.",
            "Build `DocumentReviewScreen` displaying document image, metadata, and decision buttons (Approve, Pending, Compliance).",
            "Map backend JSON to Dart model classes (`DocumentModel`, `ApprovalStepModel`)."
        ],
        "done_when": "User can upload document via mobile camera and an approver can approve or flag compliance from the Flutter app.",
        "references": [
            "[Flutter Image Picker](https://pub.dev/packages/image_picker)",
            "[Flutter ListView Recipes](https://docs.flutter.dev/cookbook/lists/basic-list)"
        ],
        "needs": "Step 18",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "If backend APIs are on local network, use local mock JSON datasets in Flutter to refine UI transitions.",
        "starter_code": None
    },
    21: {
        "issue": 54,
        "title": "Step 21: Compile and submit Project Report 1 (Mid-Term Project Review)",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shreya Loya & Shreeyash Solunke",
        "assignees": [USERS["Shreya Loya"], USERS["Shreeyash"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Mandatory academic milestone evaluating mid-semester project progress, architectural validity, and team contribution.",
        "what": "Compile, format, and submit the official mid-term project report covering Phase 0 to Phase 2.",
        "how": [
            "Structure report with university standard headers: Problem Definition, Proposed System, Literature Review, System Architecture.",
            "Insert official high-res diagrams: Database ER schema, Sequential Workflow State Machine, and Swimlane Chart.",
            "Include complete REST API documentation table from Step 5 and Postman verification screenshots.",
            "Add Figma UI wireframes and actual working screenshots of Web/Mobile registration and document upload.",
            "Detail equal workload point allocation and module ownership across all four members.",
            "Review draft with project guide and collect formal mid-term evaluation signature."
        ],
        "done_when": "Mid-term report PDF is submitted to college portal and approved by project guide by November 30, 2026.",
        "references": [
            "[IEEE Technical Report Guidelines](https://www.ieee.org/conferences/publishing/templates.html)",
            "[Overleaf / LaTeX Templates](https://www.overleaf.com/)"
        ],
        "needs": "Step 4, Step 5, Step 8, Step 9, Step 18",
        "unlocks": "Phase 3 (Document processing)",
        "parallel_fallback": "Teammates who finish Week 4 coding early write their respective module descriptions and take clean screenshots.",
        "starter_code": None
    },
    22: {
        "issue": 37,
        "title": "Step 22: Implement compliance resolution and resubmission flow",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "deadline": "December 7, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Handles real-world corrections (e.g., missing attachments, fee receipts) without forcing the applicant to restart the entire approval chain.",
        "what": "Build `POST /api/documents/{id}/fulfil` and `POST /api/documents/{id}/withdraw` endpoints.",
        "how": [
            "In `POST /api/documents/{id}/fulfil`, allow applicant to upload a corrected document.",
            "Compute new SHA-256 fingerprint of the updated document and store in `original_hash`.",
            "Preserve previous hash in `Timeline` audit history with timestamp.",
            "Reset current step status back to `pending` so the requesting approver can re-evaluate the corrected file.",
            "In `POST /api/documents/{id}/withdraw`, allow applicant to cancel their submission.",
            "Test full compliance cycle: Approver requests compliance -> Applicant fulfills -> Approver approves."
        ],
        "done_when": "Applicant successfully uploads corrected file, timeline logs fulfillment, and document returns to the same approver.",
        "references": [
            "[Flask File Handling](https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/)",
            "[Audit Trail Principles](https://en.wikipedia.org/wiki/Audit_trail)"
        ],
        "needs": "Step 18",
        "unlocks": "Step 19 (Dashboard compliance views)",
        "parallel_fallback": "Write automated test script simulating compliance request and fulfill cycles.",
        "starter_code": None
    },
    23: {
        "issue": 29,
        "title": "Step 23: Build real-time audit log and document timeline API",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "deadline": "December 7, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "Provides complete transparency, tracking every milestone from initial upload to final stamp with non-repudiation.",
        "what": "Implement centralized `add_timeline_event()` helper and build `GET /api/documents/{id}/timeline`.",
        "how": [
            "Create helper `add_timeline_event(document_id, event_text, actor_name)`.",
            "Call helper at every key event: document uploaded, assigned to approver X, kept pending by Y, compliance raised by Z, approved by W.",
            "Build `GET /api/documents/{id}/timeline` returning sorted chronological list of events with ISO timestamps.",
            "Format timeline events for frontend display (e.g., 'Approved by Prof. Sharma (HOD IT) on 05 Dec 2026, 14:32')."
        ],
        "done_when": "Querying timeline endpoint after an approval sequence returns an unalterable chronological story of all actions.",
        "references": [
            "[SQLAlchemy Ordering](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#order-by)",
            "[ISO 8601 Timestamp Format](https://en.wikipedia.org/wiki/ISO_8601)"
        ],
        "needs": "Step 18",
        "unlocks": "Step 33 (Web status timeline), Step 35 (Mobile timeline)",
        "parallel_fallback": "Test timeline generation using seeded test documents while frontend timeline widget is being built.",
        "starter_code": None
    },
    24: {
        "issue": 14,
        "title": "Step 24: Enforce cryptographic tamper-detection verification before every action",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "deadline": "December 7, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "4 pts (~4 hours)",
        "why": "The signature security feature: prevents unauthorized modification of files on disk during the approval process.",
        "what": "Embed automated SHA-256 integrity verification inside all approval and compliance handlers.",
        "how": [
            "Before processing any approve, pending, or compliance request, read physical file on disk.",
            "Compute fresh SHA-256 hash using `utils.hashing.sha256_file()`.",
            "Compare freshly computed hash against `documents.original_hash` in database.",
            "If hashes match: proceed with approver action normally.",
            "If hashes mismatch: immediately abort action, return 400 Tamper Alert, flag document `tampered = True`, and append 'TAMPER ALERT: File content modified' to timeline.",
            "Test: manually modify 1 byte of a stored test file using a hex editor and verify subsequent approval is blocked."
        ],
        "done_when": "Tampered files trigger an instant 400 security error and timeline alert; authentic files pass seamlessly.",
        "references": [
            "[Data Integrity in Cryptography](https://en.wikipedia.org/wiki/Data_integrity)",
            "[Python Hashlib Security](https://docs.python.org/3/library/hashlib.html)"
        ],
        "needs": "Step 14, Step 18",
        "unlocks": "Step 26 (Document stamping)",
        "parallel_fallback": "Write a dedicated unit test script that injects deliberate file corruption to verify the blocker.",
        "starter_code": None
    },
    25: {
        "issue": 23,
        "title": "Step 25: Build multi-parameter document search and filtering API",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "deadline": "December 7, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Allows users and administrators to instantly search across hundreds of document records by title, status, or date range.",
        "what": "Build `GET /api/documents` supporting dynamic query parameters: `status`, `q`, `from`, `to`, and role scoping.",
        "how": [
            "Parse query parameters: `status` (pending/approved/compliance), `q` (title keyword), `from` and `to` (date filters).",
            "Use SQLAlchemy dynamic query building with `ilike(f'%{q}%')` for case-insensitive keyword searching.",
            "Enforce role isolation: applicants only see their own submissions; approvers only see documents routed to them.",
            "Return paginated JSON results with total record count and page metadata.",
            "Verify search performance with Postman queries."
        ],
        "done_when": "Searching keywords, status filters, and date boundaries returns accurate filtered subsets matching criteria.",
        "references": [
            "[SQLAlchemy Filtering Guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html)",
            "[Postman API Testing](https://learning.postman.com/docs/getting-started/introduction/)"
        ],
        "needs": "Step 9, Step 18",
        "unlocks": "Step 33 (Search & filter UI)",
        "parallel_fallback": "If database has few records, seed additional sample documents from Step 7 to test filter combinations.",
        "starter_code": None
    },
    26: {
        "issue": 15,
        "title": "Step 26: Implement digital stamping engine using PyMuPDF (signatures, stamps, seals)",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "9 pts (~9 hours)",
        "why": "Generates the final official artifact: an authenticated PDF embedded with verified approver signatures, authority stamps, and unique approval codes.",
        "what": "Develop the PDF manipulation engine using PyMuPDF (`fitz`) and Pillow to superimpose graphics and text onto approved documents.",
        "how": [
            "If original upload is an image (PNG/JPG), convert it into a standard A4 PDF using Pillow.",
            "Open target PDF using `fitz.open()` and access final signature page (`pdf[-1]`).",
            "Define approver grid layout (e.g., Approver 1: bottom-left, Approver 2: bottom-center, Approver 3: bottom-right).",
            "Use `page.insert_image(rect, filename=asset_path)` to stamp transparent signature and seal PNGs.",
            "Use `page.insert_text(point, approval_number, fontsize=9)` to print the official approval code below each signature.",
            "Save stamped document as a new file (e.g., `uploads/final/DOC_{id}_signed.pdf`) without modifying the original upload.",
            "Verify visual alignment on sample PDFs."
        ],
        "done_when": "Fully approved document outputs a final PDF clearly showing all approvers' signatures, seals, and approval codes.",
        "references": [
            "[PyMuPDF (fitz) Official Documentation](https://pymupdf.readthedocs.io/en/latest/)",
            "[Pillow (PIL) Image Guide](https://pillow.readthedocs.io/en/stable/)"
        ],
        "needs": "Step 15, Step 18, Step 24",
        "unlocks": "Step 27 (Coordinate stamping), Step 28 (QR stamping), Step 30 (Final hash)",
        "parallel_fallback": "Test coordinate placement and bounding boxes using standalone Python test script on sample dummy PDFs.",
        "starter_code": None
    },
    27: {
        "issue": 42,
        "title": "Step 27: Build dynamic coordinate-based stamping engine",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Enables dynamic placement of signatures and stamps anywhere on custom document templates rather than fixed default positions.",
        "what": "Extend the PyMuPDF engine to stamp signatures at custom `(x, y, page)` coordinates received from frontend.",
        "how": [
            "Extend document processing module to accept coordinate payloads: `[{approver_id: 2, page: 1, x: 120, y: 650}]`.",
            "Convert percentage / canvas pixel coordinates to PyMuPDF 72-dpi point space.",
            "Validate that coordinates lie within printable page boundaries.",
            "Insert signature, stamp, and approval text block centered at the specified target coordinates.",
            "Support fallback to default bottom grid if coordinates are not specified."
        ],
        "done_when": "Signatures render precisely at specified coordinates on both single-page and multi-page documents.",
        "references": [
            "[PyMuPDF Coordinate Mathematics](https://pymupdf.readthedocs.io/en/latest/rect.html)",
            "[PDF Point System Reference](https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdf_reference_archive/pdf_reference_1-7.pdf)"
        ],
        "needs": "Step 26",
        "unlocks": "Step 29 (Drag-and-drop web canvas)",
        "parallel_fallback": "Test coordinate scaling using synthetic coordinate inputs before web canvas integration.",
        "starter_code": None
    },
    28: {
        "issue": 43,
        "title": "Step 28: Implement dynamic QR code PDF generator and document verification API",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Allows instant physical-to-digital authentication. Anyone holding a printed document can scan its QR code to verify validity.",
        "what": "Generate dynamic QR code encoding the verification URL, stamp it onto the PDF header/footer, and build `GET /api/verify/{approval_no}`.",
        "how": [
            "Use Python `qrcode` library to generate QR image containing URL: `https://<deployed-url>/verify/{approval_no}`.",
            "Stamp QR image in the upper or lower corner of the final PDF using PyMuPDF.",
            "Build public endpoint `GET /api/verify/{approval_no}` returning JSON: document validity, title, applicant name, approver names, approval timestamps, and SHA-256 fingerprint.",
            "Return 404 with invalid status if approval number does not exist."
        ],
        "done_when": "Scanning the stamped QR code with any smartphone opens the verification endpoint confirming authentic document credentials.",
        "references": [
            "[Python qrcode Library](https://pypi.org/project/qrcode/)",
            "[PyMuPDF Image Insertion](https://pymupdf.readthedocs.io/en/latest/page.html#Page.insert_image)"
        ],
        "needs": "Step 26",
        "unlocks": "Step 34 (Public verify portal), Step 39 (Mobile QR scanner)",
        "parallel_fallback": "If production domain is not configured yet, use relative verification routes or localhost URLs during testing.",
        "starter_code": None
    },
    29: {
        "issue": 44,
        "title": "Step 29: Build interactive drag-and-drop signature placement canvas on web",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "8 pts (~8 hours)",
        "why": "Provides an intuitive visual interface where applicants can drag approver signature tags directly onto an A4 document preview.",
        "what": "Create an interactive HTML5 canvas or PDF.js preview allowing users to drag and drop approver signature bounding boxes.",
        "how": [
            "Render uploaded document preview on an HTML5 canvas container.",
            "Create draggable approver badge pills (e.g., 'HOD Signature Box', 'Dean Stamp Box').",
            "Allow users to drag and drop badges onto the canvas, capturing normalized coordinates `(x%, y%)` upon release.",
            "Package coordinates with the approver chain payload to send to `POST /api/documents/{id}/chain`.",
            "Provide clear visual bounding boxes showing where signatures will appear."
        ],
        "done_when": "Applicant drags signature boxes on preview and coordinates are successfully submitted to and stored by backend.",
        "references": [
            "[HTML5 Drag and Drop API](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API)",
            "[PDF.js Express / Viewer](https://mozilla.github.io/pdf.js/)"
        ],
        "needs": "Step 19, Step 27",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "If backend coordinate API is being updated, build drag-and-drop interactions against static preview image in browser.",
        "starter_code": None
    },
    30: {
        "issue": 30,
        "title": "Step 30: Implement final document locking and SHA-256 hash re-verification API",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "Locks the finished document so any post-approval tampering or alteration of the signed PDF is detected immediately.",
        "what": "Compute SHA-256 of the stamped PDF, store in `documents.final_hash`, and build secure `GET /api/documents/{id}/download`.",
        "how": [
            "Compute SHA-256 fingerprint of the newly generated stamped PDF file and store in `documents.final_hash` and `final_path`.",
            "Log timeline milestone: 'Final authenticated PDF generated and cryptographically sealed'.",
            "Build secure download endpoint `GET /api/documents/{id}/download`.",
            "Before sending file, re-calculate hash of the stored file on disk and compare against `documents.final_hash`.",
            "If verified, send file via `flask.send_file(as_attachment=True)`; if altered, abort with 403 Tamper Alert."
        ],
        "done_when": "Downloading a signed document works cleanly; modifying a byte of the final PDF causes the download endpoint to reject transmission.",
        "references": [
            "[Flask send_file Guide](https://flask.palletsprojects.com/en/3.0.x/api/#flask.send_file)",
            "[Cryptographic File Seals](https://en.wikipedia.org/wiki/Digital_signature)"
        ],
        "needs": "Step 26",
        "unlocks": "Step 33 (Download page), Step 38 (Integration)",
        "parallel_fallback": "Test download and re-hashing logic with pre-generated sample PDFs.",
        "starter_code": None
    },
    31: {
        "issue": 31,
        "title": "Step 31: Implement security PIN lock logic with brute-force rate limiting",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "Adds a critical second layer of protection before performing sensitive actions like approving a document or changing keys.",
        "what": "Build `POST /api/pin/set` and `POST /api/pin/verify` with hashed storage and 5-attempt rate limiting lock.",
        "how": [
            "Allow users to set a 4 or 6-digit PIN; store only the one-way hash in `users.pin_hash`.",
            "In `POST /api/pin/verify`, check entered PIN against stored hash.",
            "Track failed attempts: if 5 consecutive failed attempts occur, lock PIN verification for 15 minutes.",
            "Return remaining attempt count on incorrect entries.",
            "Use PIN verification as secondary confirmation before approving sensitive documents."
        ],
        "done_when": "PIN sets and verifies correctly; 5 wrong attempts lock the account temporarily with appropriate error message.",
        "references": [
            "[OWASP Authentication Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)",
            "[Rate Limiting Strategies](https://en.wikipedia.org/wiki/Rate_limiting)"
        ],
        "needs": "Step 10",
        "unlocks": "Step 35 (Mobile biometric lock)",
        "parallel_fallback": "Test PIN hashing and rate limiting using Postman automated runner.",
        "starter_code": None
    },
    32: {
        "issue": 46,
        "title": "Step 32: Build real-time notification system (backend API and app alerts)",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Eliminates administrative bottlenecks by alerting authorities immediately when a document arrives in their queue.",
        "what": "Create notification data model, backend notification APIs, and in-app bell counter with unread alert badges.",
        "how": [
            "Create `Notification` model: `id`, `user_id`, `title`, `message`, `is_read`, `created_at`.",
            "Automatically dispatch notifications when: document routed to approver, document approved, compliance requested, or final PDF ready.",
            "Build `GET /api/notifications` and `POST /api/notifications/{id}/read`.",
            "Implement unread counter badge in Flutter app bar and web navbar.",
            "Clicking notification navigates user directly to the relevant document review screen."
        ],
        "done_when": "Approver sees badge counter increment when a document is routed to them; clicking marks it read.",
        "references": [
            "[Flutter Badges Package](https://pub.dev/packages/badges)",
            "[Flask JSON APIs](https://flask.palletsprojects.com/en/3.0.x/api/#flask.json.jsonify)"
        ],
        "needs": "Step 23",
        "unlocks": "Step 35 (Mobile notifications), Step 38 (Integration)",
        "parallel_fallback": "If backend notification triggers are pending, design the Flutter notification drawer with static mock data.",
        "starter_code": None
    },
    33: {
        "issue": 24,
        "title": "Step 33: Build web document status page, search UI, and download center",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "7 pts (~7 hours)",
        "why": "Provides complete self-service tracking and document retrieval for applicants without contacting administrative staff.",
        "what": "Build `status.html`, `search.html`, and `downloads.html` connecting to backend search, timeline, and download APIs.",
        "how": [
            "Build `web/status.html` rendering a visual step-by-step progress stepper (Step 1 -> Step 2 -> Final Approved).",
            "Render chronological audit events from `GET /api/documents/{id}/timeline`.",
            "Build search bar and filter dropdowns in `web/search.html` calling `GET /api/documents?status=&q=`.",
            "Build `web/downloads.html` displaying cards for all fully approved documents with one-click download buttons.",
            "Ensure mobile-responsive styling across all desktop and phone screens."
        ],
        "done_when": "All pages render correctly on mobile and desktop; search filters work and approved files download with correct filenames.",
        "references": [
            "[Tailwind / CSS Stepper Components](https://flowbite.com/docs/components/stepper/)",
            "[Responsive Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries/Using_media_queries)"
        ],
        "needs": "Step 23, Step 25, Step 30",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "Style status stepper using mock status JSON while backend endpoints are finalizing.",
        "starter_code": None
    },
    34: {
        "issue": 45,
        "title": "Step 34: Build public document verification web portal (unauthenticated)",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Enables third parties (employers, partner universities, banks) to verify certificate validity without needing an account.",
        "what": "Build clean public verification portal accessible via `/verify` and `/verify/{approval_no}`.",
        "how": [
            "Build public template `web/verify.html` with prominent search input for approval numbers.",
            "Support direct URL routing: navigating to `/verify/APH-2026-00012-1` triggers automatic lookup.",
            "Call `GET /api/verify/{approval_no}` and display official verification certificate card.",
            "Display green verified shield, document title, applicant name, approver names, timestamps, and SHA-256 fingerprint.",
            "If invalid or tampered, display high-visibility red warning banner."
        ],
        "done_when": "Entering a valid approval number renders a verified certificate; invalid numbers show an untampered alert banner.",
        "references": [
            "[Public Route Security](https://flask.palletsprojects.com/en/3.0.x/security/)",
            "[CSS Certificate Styling Ideas](https://codepen.io/tag/certificate)"
        ],
        "needs": "Step 28",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "Style certificate card using static mock JSON while Step 28 verification API is being deployed.",
        "starter_code": None
    },
    35: {
        "issue": 32,
        "title": "Step 35: Build mobile timeline, approver profile, and biometric app lock in Flutter",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "8 pts (~8 hours)",
        "why": "Completes the smartphone experience with native mobile features like fingerprint authentication and asset uploads.",
        "what": "Build Flutter Timeline screen, Profile asset management screen, and biometric fingerprint/FaceID lock using `local_auth`.",
        "how": [
            "Build `TimelineView` widget displaying interactive step indicators and event cards.",
            "Build `ApproverProfileScreen` enabling approvers to photograph or pick signature and stamp PNGs and upload to API.",
            "Integrate `local_auth` package to prompt for fingerprint or device PIN when opening the app or approving documents.",
            "Add fallback to numeric PIN if device biometric sensor is unavailable.",
            "Test biometric prompts on Android device / emulator."
        ],
        "done_when": "App displays live timeline, approver can upload profile assets, and biometric prompt triggers successfully.",
        "references": [
            "[Flutter local_auth Package](https://pub.dev/packages/local_auth)",
            "[Flutter Timeline Tile](https://pub.dev/packages/timeline_tile)"
        ],
        "needs": "Step 15, Step 23, Step 31",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "If biometric hardware is not supported on emulator, verify logic using device PIN fallback mode.",
        "starter_code": None
    },
    36: {
        "issue": 38,
        "title": "Step 36: Build administrative dashboard and user management CRUD API",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "7 pts (~7 hours)",
        "why": "Gives college administrators master control to onboard authorities, configure departments, and manage system users.",
        "what": "Build `GET`, `POST`, `PUT`, `DELETE /api/admin/users` and admin management web view.",
        "how": [
            "Build admin-only routes guarded by `@requires_role('admin')`.",
            "Support listing all users with role, post, and department filters.",
            "Support creating new approver accounts (e.g., creating Dr. Sharma as HOD Information Technology).",
            "Support deactivating accounts or updating user posts.",
            "Build simple admin UI table with modal dialogs for adding and editing users.",
            "Coordinate with Shravani for CSS theme alignment."
        ],
        "done_when": "Administrator can create a new approver who immediately appears in the applicant's approver selection dropdown.",
        "references": [
            "[Admin CRUD Architecture](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)",
            "[Flask Admin Patterns](https://flask.palletsprojects.com/en/3.0.x/blueprints/)"
        ],
        "needs": "Step 10",
        "unlocks": "Step 37 (Admin audit log), Step 38 (Integration)",
        "parallel_fallback": "Write backend CRUD unit tests in Postman while finalizing the HTML admin layout.",
        "starter_code": None
    },
    37: {
        "issue": 48,
        "title": "Step 37: Build administrative approval audit log and search engine",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Provides institutional governance and inspection capabilities to trace any past approval decision or compliance note.",
        "what": "Build `GET /api/admin/audit-logs` and search engine filtering by approval number, actor, or date.",
        "how": [
            "Build `GET /api/admin/audit-logs` returning full system actions with timestamps, IP address, and actor.",
            "Implement instant search by approval number (`APH-YYYY-XXXXX-X`) returning full timeline history.",
            "Integrate audit table into Admin dashboard with pagination.",
            "Export audit summary report in CSV or JSON."
        ],
        "done_when": "Admin can query any approval number and view the complete sequence of events, approver remarks, and cryptographic hashes.",
        "references": [
            "[Audit Logging Standards](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)",
            "[SQLAlchemy Complex Queries](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html)"
        ],
        "needs": "Step 36",
        "unlocks": "Step 38 (System integration)",
        "parallel_fallback": "Test query performance and JSON serialization using Postman collections.",
        "starter_code": None
    },
    38: {
        "issue": 16,
        "title": "Step 38: Execute end-to-end system integration (connecting web and mobile with live API)",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "Unifies separately developed frontend, mobile, and backend components into a single coherent working ecosystem.",
        "what": "Merge all feature branches into `main`, resolve schema/format mismatches, and verify end-to-end flow.",
        "how": [
            "Review and merge feature branches (`shravani-web`, `shreya-mobile`, `shreya-qa`) into `main` with Git.",
            "Conduct joint integration session with all 4 members testing against one local backend instance.",
            "Replace all mock JSON in web and mobile with live API calls.",
            "Fix field name discrepancies (e.g., camelCase vs snake_case, date formats).",
            "Perform full journey: Upload -> 3-approver chain -> Signatures stamped -> QR generated -> Stamped PDF downloaded."
        ],
        "done_when": "A document runs completely from mobile/web upload through all approvers to final stamped PDF download without errors.",
        "references": [
            "[Git Conflict Resolution](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging#_basic_merge_conflicts)",
            "[System Integration Best Practices](https://en.wikipedia.org/wiki/System_integration)"
        ],
        "needs": "Steps 19, 20, 26, 29, 30, 33, 35, 36",
        "unlocks": "Step 39 (QR scanner), Step 40 (QA testing)",
        "parallel_fallback": "Pair program to resolve any merge conflicts immediately as a team.",
        "starter_code": None
    },
    39: {
        "issue": 47,
        "title": "Step 39: Implement in-app QR camera scanner and real-time mobile verification",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "Enables college proctors, examiners, or gate authorities to point their smartphone at any printed paper and verify validity on the spot.",
        "what": "Integrate camera QR scanning in Flutter and display mobile verification certificate modal.",
        "how": [
            "Add `mobile_scanner` dependency to `pubspec.yaml` with camera permissions.",
            "Build viewfinder screen with aiming target overlay.",
            "Extract approval number from scanned URL and query `GET /api/verify/{approval_no}`.",
            "Display verification certificate modal in Flutter showing green verified badge, signers, timestamps, and SHA-256 hash.",
            "Provide manual text input fallback if camera is unavailable."
        ],
        "done_when": "App camera scans printed/screen QR code and instantly displays digital verification credentials in the app.",
        "references": [
            "[Flutter Mobile Scanner Package](https://pub.dev/packages/mobile_scanner)",
            "[Android Camera Permissions](https://developer.android.com/training/camera)"
        ],
        "needs": "Step 28, Step 38",
        "unlocks": "Step 40 (QA testing)",
        "parallel_fallback": "Test scanner logic by passing mock scanned URLs to verify the modal rendering.",
        "starter_code": None
    },
    40: {
        "issue": 39,
        "title": "Step 40: Execute comprehensive QA testing matrix (40+ manual test cases and edge cases)",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "8 pts (~8 hours)",
        "why": "Systematically identifies defects and security vulnerabilities before the final demo to ensure zero demo failures.",
        "what": "Draft and execute 40+ structured test cases covering positive paths, negative paths, boundary conditions, and security edge cases.",
        "how": [
            "Create Google Sheet or Excel matrix: `Test ID`, `Module`, `Description`, `Steps`, `Expected Result`, `Actual Result`, `Status`, `Severity`.",
            "Test critical scenarios: single approver, 3-approver chain, out-of-order approval attempt, compliance fulfill, withdrawal, tampered file, invalid file type (.exe), oversized upload, wrong password, brute-force PIN lock, public QR verification.",
            "Log all discovered bugs as GitHub issues with reproduction steps.",
            "Retest and close bugs as they are resolved by teammates."
        ],
        "done_when": "All 40+ test cases have executed results, all high/critical severity defects are resolved, and report is summarized.",
        "references": [
            "[Software Testing Fundamentals](https://en.wikipedia.org/wiki/Software_testing)",
            "[Test Case Design Cheatsheet](https://www.guru99.com/test-case.html)"
        ],
        "needs": "Step 38",
        "unlocks": "Step 41 (Pytest CI), Step 42 (Bug fixing)",
        "parallel_fallback": "Draft the test cases in advance during Week 6 so execution begins immediately upon integration.",
        "starter_code": None
    },
    41: {
        "issue": 49,
        "title": "Step 41: Build automated pytest backend test suite and GitHub Actions CI workflow",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Provides automated regression testing and demonstrates professional software engineering practices to college examiners.",
        "what": "Write automated pytest tests in `tests/` and configure GitHub Actions workflow running tests on every pull request.",
        "how": [
            "Set up test client fixtures in `tests/conftest.py` with in-memory SQLite database.",
            "Write tests covering: user registration, login, role restrictions, upload hash calculation, state transitions, tampering detection, and verification API.",
            "Create `.github/workflows/ci.yml` running `pytest` automatically on push and pull requests to `main`.",
            "Add passing CI status badge to `README.md`."
        ],
        "done_when": "GitHub Actions executes on push and shows green checkmark for all passing tests in pull requests.",
        "references": [
            "[Pytest Documentation](https://docs.pytest.org/en/8.0.x/)",
            "[GitHub Actions Python Workflow](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)"
        ],
        "needs": "Step 38, Step 40",
        "unlocks": "Step 43 (Production deployment)",
        "parallel_fallback": "Write local pytest scripts first before committing the GitHub Actions YAML configuration.",
        "starter_code": None
    },
    42: {
        "issue": 52,
        "title": "Step 42: Conduct team-wide bug squashing, OWASP security audit, and hardening",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "4 pts (~4 hours each)",
        "why": "Ensures the application is rock-solid, production-ready, and free of security oversights prior to public deployment.",
        "what": "Each member fixes bugs in their assigned module and executes collective security verification.",
        "how": [
            "Shreeyash: Fix core workflow and PyMuPDF stamping edge cases.",
            "Shravani: Fix web UI glitches and verify role decorators prevent unauthorized access.",
            "Shreya Sutar: Fix mobile app network exceptions and refine camera scanner UX.",
            "Shreya Loya: Verify all QA test cases pass and confirm zero open critical defects.",
            "Security checklist: passwords/PINs hashed, no secret keys committed to GitHub, uploads folder not directly browsable, CORS configured properly."
        ],
        "done_when": "All high-priority bugs are closed, security audit checklist is complete, and system runs flawlessly.",
        "references": [
            "[OWASP Top 10 Security Risks](https://owasp.org/www-project-top-ten/)",
            "[Flask Security Guidelines](https://flask.palletsprojects.com/en/3.0.x/security/)"
        ],
        "needs": "Step 40, Step 41",
        "unlocks": "Step 43 (Production deployment)",
        "parallel_fallback": "Conduct code reviews for each other's pull requests to catch subtle bugs early.",
        "starter_code": None
    },
    43: {
        "issue": 25,
        "title": "Step 43: Deploy backend and web portal to cloud production (Render / PythonAnywhere)",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Provides a live public URL so college evaluators and examiners can interact with ApproveHub on their own phones.",
        "what": "Deploy Flask backend with Gunicorn on Render or PythonAnywhere, configure environment variables, and update client endpoints.",
        "how": [
            "Create production `Procfile` with `web: gunicorn backend.app:app`.",
            "Set environment variables on hosting provider: `SECRET_KEY`, `FLASK_ENV=production`, `DATABASE_URL`.",
            "Deploy to Render / PythonAnywhere and verify live HTTPS domain.",
            "Update web fetch calls and mobile Flutter API base URLs to point to the live cloud server.",
            "Test live document submission, approval, stamping, and QR verification on physical phones using mobile data."
        ],
        "done_when": "Project is accessible via live public URL and a complete approval flow completes successfully on mobile data.",
        "references": [
            "[Deploying Flask on Render](https://render.com/docs/deploy-flask)",
            "[Gunicorn Documentation](https://gunicorn.org/)"
        ],
        "needs": "Step 42",
        "unlocks": "Step 44 (Documentation), Step 45 (Final report)",
        "parallel_fallback": "If Render deployment hits build issues, deploy to PythonAnywhere as immediate fallback.",
        "starter_code": None
    },
    44: {
        "issue": 33,
        "title": "Step 44: Write comprehensive README and interactive API documentation",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "deadline": "December 28, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Demonstrates open-source excellence, provides clear setup instructions, and serves as an impressive portfolio piece for placements.",
        "what": "Write production-grade `README.md` with architectural diagrams, feature showcase, local installation guide, and API docs.",
        "how": [
            "Write project introduction, motivation, key features, and technology stack badges.",
            "Include high-resolution screenshots of Web and Mobile dashboards and sample stamped PDF with QR code.",
            "Provide step-by-step installation instructions for cloning, virtualenv setup, database init, and running servers.",
            "Document API endpoints with curl examples or embed Postman collection link.",
            "Add team credits with GitHub profiles."
        ],
        "done_when": "A new developer can clone the repository, follow the README, and run the complete project locally.",
        "references": [
            "[Make a Readme Guide](https://www.makeareadme.com/)",
            "[Shields.io Badges](https://shields.io/)"
        ],
        "needs": "Step 43",
        "unlocks": "Step 47 (Final submission)",
        "parallel_fallback": "Draft documentation structure early and insert screenshots as features reach completion.",
        "starter_code": None
    },
    45: {
        "issue": 40,
        "title": "Step 45: Compile and submit Project Report 2 (Final Comprehensive College Submission)",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "deadline": "December 28, 2026",
        "owner_name": "Shreya Loya & Shreeyash Solunke",
        "assignees": [USERS["Shreya Loya"], USERS["Shreeyash"]],
        "importance": "High",
        "effort": "8 pts (~8 hours)",
        "why": "The final academic report officially determines semester grades, project credits, and evaluation by external university examiners.",
        "what": "Assemble and publish the final comprehensive project report covering all 8 university-mandated headings.",
        "how": [
            "Complete all 8 college headings: Title, Objectives, Literature Survey, Work Methodology, Features & System Design, Cost & Effort Estimation, Conclusion & Future Scope, References.",
            "Collect individual module writeups and screenshots from all 4 members.",
            "Embed final diagrams: System Architecture, Database ER Diagram, Document State Machine, and Swimlane Flow.",
            "Include summary table of 40+ QA test case results, pytest coverage reports, and live deployment link.",
            "Print/bind report as required by department guidelines and obtain project guide signature."
        ],
        "done_when": "Complete report is compiled into PDF, printed/bound, and approved with guide signature by December 28, 2026.",
        "references": [
            "[Academic Project Report Formatting](https://www.ieee.org/conferences/publishing/templates.html)",
            "[IEEE Citation Guide](https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf)"
        ],
        "needs": "Step 43",
        "unlocks": "Step 46 (Presentation), Step 47 (Final submission)",
        "parallel_fallback": "Write literature survey and methodology sections early so only final screenshots are needed in Week 8.",
        "starter_code": None
    },
    46: {
        "issue": 41,
        "title": "Step 46: Prepare project presentation slide deck and 5-minute synchronized demo script",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "deadline": "December 29, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "A compelling slide deck and polished live demonstration maximize scoring during university viva and panel evaluation.",
        "what": "Create 10-12 slide professional presentation and a timed 5-minute live demonstration script.",
        "how": [
            "Create slides: Problem Statement, Real-World Inefficiencies, ApproveHub Solution, Architecture, Cryptographic Security (SHA-256), Mobile App & QR Verification, Test Results, Future Scope.",
            "Write 5-minute demo script: 1. Applicant uploads document -> 2. Selects approver chain -> 3. Approver reviews and signs -> 4. Compliance resolution demonstrated -> 5. Final PDF stamped with QR code -> 6. Smartphone scans QR code showing instant authenticity verification.",
            "Assign each team member their speaking portion matching their module ownership."
        ],
        "done_when": "Slide deck is finalized and the team conducts a smooth 5-minute rehearsal without exceeding time limits.",
        "references": [
            "[Pitch Deck Best Practices](https://www.sequoiacap.com/article/writing-a-business-plan/)",
            "[Canva Presentation Templates](https://www.canva.com/presentations/templates/)"
        ],
        "needs": "Step 45",
        "unlocks": "Step 47 (Final submission)",
        "parallel_fallback": "Rehearse demo locally using backup video recording if internet connection is unstable.",
        "starter_code": None
    },
    47: {
        "issue": 53,
        "title": "Step 47: Final academic rehearsal, guide evaluation, and university submission",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "deadline": "December 30, 2026",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "3 pts (~3 hours each)",
        "why": "Official project closure, final faculty review, and university submission completion.",
        "what": "Present complete working project to faculty guide, incorporate final feedback, tag release, and submit.",
        "how": [
            "Run live demonstration in front of project guide and panel.",
            "Address any minor presentation feedback.",
            "Tag final release in Git: `git tag -a v1.0.0 -m 'Final Release for Academic Submission' && git push origin --tags`.",
            "Submit final report PDF and GitHub repository link to university examination portal.",
            "Celebrate successful project completion! 🎉"
        ],
        "done_when": "Project evaluation is approved by college guide, final report signed, and GitHub repository officially submitted by Dec 30, 2026.",
        "references": [
            "[Git Tagging Documentation](https://git-scm.com/book/en/v2/Git-Basics-Tagging)",
            "[University Examination Guidelines](https://www.unipune.ac.in/)"
        ],
        "needs": "Step 44, Step 45, Step 46",
        "unlocks": "Semester Graduation & Project Completion! 🚀",
        "parallel_fallback": "Ensure offline backup demo is ready on laptop in case classroom Wi-Fi fails.",
        "starter_code": None
    }
}

def format_issue_markdown(step_num, info):
    assignees_formatted = ", ".join([f"@{a}" for a in info["assignees"]])
    lines = [
        "### 📋 Core Project Task Overview",
        f"- **Step Number:** **Step {step_num}** (Clean Sequential Flow)",
        f"- **Phase:** {info['phase']}",
        f"- **Milestone:** {info['week']} (🎯 **Target Deadline: {info['deadline']}**)",
        f"- **Owner:** {info['owner_name']} ({assignees_formatted})",
        f"- **Importance:** {'🔴 Critical' if info['importance'] == 'Critical' else ('🟠 High' if info['importance'] == 'High' else '🟡 Medium')}",
        f"- **Effort Points:** {info['effort']}",
        "",
        "---",
        "",
        "### 🎯 Why it matters",
        info["why"],
        "",
        "### 📝 What to do",
        info["what"],
        "",
        "### 🛠️ Detailed Step-by-Step Instructions:",
    ]
    for action in info["how"]:
        lines.append(f"1. {action}" if not action.startswith("•") and not action.startswith("1.") else f"   {action}")
        
    lines.extend([
        "",
        "### ✅ Done When (Acceptance Criteria)",
        f"> {info['done_when']}",
        "",
        "### 💡 Helpful References & Documentation",
    ])
    for ref in info["references"]:
        lines.append(f"- 🔗 {ref}")
        
    lines.extend([
        "",
        "### 🔗 Task Dependencies",
        f"- **Prerequisites (`Needs`):** {info['needs']}",
        f"- **Unlocks for Next Steps:** {info['unlocks']}",
        "",
        "### 🔄 Parallel Non-Blocking Fallback",
        f"> **If temporarily blocked by a teammate's task:** {info['parallel_fallback']}",
        "",
        "---",
        "### 📋 Definition of Done Checklist",
        "- [ ] Work on your dedicated feature branch (never push directly to `main`)",
        "- [ ] Implement according to blueprint specifications & step-by-step instructions",
        "- [ ] Verify with Postman / unit tests / local previews",
        "- [ ] Open Pull Request, assign Shreeyash to review and merge before milestone deadline",
    ])
    return "\n".join(lines)

def main():
    print(f"Upgrading all 47 issues on {REPO} to clean sequential Step 1..47...")
    success = 0
    fail = 0

    for step_num in range(1, 48):
        info = STEPS_DATA[step_num]
        issue_id = info["issue"]
        body = format_issue_markdown(step_num, info)
        
        cmd = [
            "gh", "issue", "edit", str(issue_id),
            "--repo", REPO,
            "--title", info["title"],
            "--body", body,
            "--milestone", info["week"],
        ]
        for a in info["assignees"]:
            cmd.extend(["--add-assignee", a])
            
        print(f"Updating Step {step_num:02d} -> Issue #{issue_id} ({info['title'][:40]}...)", end=" ")
        sys.stdout.flush()
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("[OK]")
            success += 1
        else:
            print(f"[FAIL]: {res.stderr.strip()}")
            fail += 1
            
        time.sleep(0.35)

    print(f"\nAll done! Successfully updated: {success}, Failed: {fail}")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
