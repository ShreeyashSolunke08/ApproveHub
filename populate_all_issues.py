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

# Issue number -> dict with details
ISSUES_DATA = {
    8: {
        "step": "2",
        "title": "Step 2: Create the project and shared GitHub repository",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "3 pts (~3 hours)",
        "why": "One shared repository is how four people write one project without overwriting each other.",
        "what": "Create the folder structure and put it on GitHub so all four of you can work on it.",
        "how": [
            "Create folders: `backend`, `web`, `mobile`, `docs`, `uploads`.",
            "Create a virtual environment: `python -m venv venv`, then activate it (`venv\\Scripts\\activate` on Windows).",
            "Install the libraries: `pip install flask flask-sqlalchemy pillow pymupdf reportlab`, then run `pip freeze > requirements.txt`.",
            "Run `git init`, make a `.gitignore` (ignore `venv` and `uploads`), commit, create a repo on GitHub and push.",
            "Invite the 3 members (`shravaniborse9`, `SHREE7682`, `loyashreya200408`). Teach them to clone, create their own branch (`git checkout -b shravani-web`) and push it."
        ],
        "done_when": "All three teammates have cloned the repo and pushed one small test file on their own branch.",
        "learn_first": "Git basics: init, add, commit, branch, push, pull, merge.",
        "needs": "Step 1",
        "unlocks": "Steps 4, 7",
        "tip": "Rule for the team: nobody pushes directly to main. Work on your branch, then ask Shreeyash to merge.",
        "starter_code": None
    },
    9: {
        "step": "4",
        "title": "Step 4: Design the database tables",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "The database is the memory of the project. Changing it later breaks everyone's code, so decide now.",
        "what": "Decide exactly what data the system stores before writing any code.",
        "how": [
            "Draw 4 tables on paper or in draw.io:",
            "**`users`**: `id`, `name`, `email`, `password_hash`, `role`, `post`, `department`, `signature_path`, `stamp_path`, `seal_path`, `pin_hash`.",
            "**`documents`**: `id`, `title`, `file_path`, `original_hash`, `final_path`, `final_hash`, `applicant_id`, `status`, `current_step`, `created_at`.",
            "**`approval_steps`**: `id`, `document_id`, `approver_id`, `step_order`, `status`, `remark`, `approval_no`, `acted_at`.",
            "**`timeline`**: `id`, `document_id`, `event`, `time`.",
            "Mark the relationships: one user has many documents; one document has many approval steps and many timeline events."
        ],
        "done_when": "The drawing is shared in the team group and everyone agrees field names will not change without telling the others.",
        "learn_first": "Tables, primary key, foreign key, one-to-many relationship.",
        "needs": "Step 2",
        "unlocks": "Steps 5, 8",
        "tip": "Think of each table as an Excel sheet and each row as one record. A foreign key is just a column that points to a row in another sheet.",
        "starter_code": None
    },
    10: {
        "step": "8",
        "title": "Step 8: Create the database in code (models)",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "This turns your drawing into a real database file the whole team can use.",
        "what": "Turn the table drawing into real Python models.",
        "how": [
            "In `backend/models.py` write four classes (`User`, `Document`, `ApprovalStep`, `Timeline`) using SQLAlchemy. Each class is one table; each variable is one column.",
            "In `app.py` create the Flask app, connect SQLite, and run `db.create_all()` to create the database file.",
            "Open the file with DB Browser for SQLite and check that every table and column exists."
        ],
        "done_when": "The database file has the 4 tables with the right columns.",
        "learn_first": "SQLAlchemy models, Flask-SQLAlchemy setup.",
        "needs": "Step 4",
        "unlocks": "Step 9",
        "tip": None,
        "starter_code": None
    },
    11: {
        "step": "12",
        "title": "Step 12: SHA-256 fingerprint at upload",
        "phase": "Phase 1 - Foundation",
        "week": "Week 3",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "This fingerprint is how the system proves later that nobody edited the file.",
        "what": "Save the file's fingerprint (hash) so tampering can be detected later.",
        "how": [
            "Write `utils/hashing.py` with chunked reading function.",
            "Call it right after saving the upload and store the result in `documents.original_hash`.",
            "Write `verify_file(path, stored_hash)` that returns `True` if the new hash equals the stored one, else `False`.",
            "Test: upload a file, change one byte, and check `verify_file` gives `False`."
        ],
        "done_when": "Uploaded documents have a 64-character hash; changing one byte of the file makes verify_file return False.",
        "learn_first": "What a hash is, hashlib, reading files in chunks.",
        "needs": "Step 11",
        "unlocks": "Steps 16, 21",
        "tip": "A hash is a fingerprint, not a lock. It does not hide the file; it only proves whether the file is still the same.",
        "starter_code": """```python
import hashlib

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()  # 64 characters

def verify_file(path, stored_hash):
    return sha256_file(path) == stored_hash
```"""
    },
    12: {
        "step": "17",
        "title": "Step 17: Multi-approver sequence logic",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "8 pts (~8 hours)",
        "why": "This is the heart of the project: the document must reach approvers strictly one after another.",
        "what": "Make the document move from one approver to the next in order.",
        "how": [
            "Write a function that finds the current step, checks that the logged-in approver owns it, and refuses everyone else.",
            "When the current step is approved, mark it approved, add 1 to `current_step` and set the next step to pending.",
            "When the last step is approved, set the document status to `fully_approved`.",
            "Draw the state diagram (waiting, pending, approved, compliance) before coding."
        ],
        "done_when": "Approver 2 cannot see or act on the document until approver 1 approves; after approver 3 approves the status becomes fully_approved.",
        "learn_first": "State machine thinking, SQLAlchemy queries.",
        "needs": "Step 16",
        "unlocks": "Step 18",
        "tip": "Draw boxes and arrows on paper first. Most bugs in workflow code come from not knowing every possible state.",
        "starter_code": """```python
def approve_step(step, doc):
    step.status = "approved"
    next_step = ApprovalStep.query.filter_by(
        document_id=doc.id, step_order=step.step_order + 1).first()
    if next_step:
        next_step.status = "pending"  # next approver now sees it
        doc.current_step = next_step.step_order
    else:
        doc.status = "fully_approved"  # last approver finished
    db.session.commit()
```"""
    },
    13: {
        "step": "18",
        "title": "Step 18: Approve, pending and compliance actions",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "7 pts (~7 hours)",
        "why": "These three choices are what makes the project a real approval system.",
        "what": "Give approvers their three choices.",
        "how": [
            "Build `POST /api/steps/{id}/approve`, `/pending` and `/compliance`. Each accepts an optional remark.",
            "**Approve:** create a unique approval number and move the sequence forward (Step 17 code).",
            "**Pending:** keep the document at the same step and store the remark.",
            "**Compliance:** set the document to `compliance_required` and store the remark for the applicant."
        ],
        "done_when": "All three actions work in Postman and update the database as expected.",
        "learn_first": "Flask routes, handling request JSON, database updates.",
        "needs": "Step 17",
        "unlocks": "Steps 19, 20, 21, 22, 23, 25",
        "tip": None,
        "starter_code": """```python
from datetime import datetime

def make_approval_no(doc_id, step_order):
    return f"APH-{datetime.now().year}-{doc_id:05d}-{step_order}"
# example: APH-2026-00012-2
```"""
    },
    14: {
        "step": "21",
        "title": "Step 21: Hash verification before each action",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "4 pts (~4 hours)",
        "why": "This is the tamper-detection feature: every action first checks the file is unchanged.",
        "what": "Detect tampering at every stage.",
        "how": [
            "Before any approve, pending or compliance action, run `verify_file` on the current file and compare with the stored hash.",
            "If it fails, block the action, set a tamper flag and add the timeline event 'Tampering detected'.",
            "Test by editing a stored file by hand and trying to approve it."
        ],
        "done_when": "A modified file is refused and flagged; an untouched file works normally.",
        "learn_first": "Reusing verification helper, error response status codes.",
        "needs": "Steps 12, 18",
        "unlocks": "Final project / Step 31",
        "tip": None,
        "starter_code": None
    },
    15: {
        "step": "25",
        "title": "Step 25: Stamp signatures, stamps, seals and approval number",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "9 pts (~9 hours)",
        "why": "This produces the final approved document, the visible result of the project.",
        "what": "Produce the final approved document.",
        "how": [
            "Fix positions in advance: for example approver 1 bottom-left, approver 2 bottom-centre, approver 3 bottom-right, with the approval number under each block.",
            "If the upload is a JPG or PNG, convert it to a PDF first with Pillow.",
            "With PyMuPDF open the PDF and call `insert_image` at the chosen position for each approver's signature, stamp and seal, then `insert_text` for the approval number.",
            "Always save as a new file. Never overwrite the original."
        ],
        "done_when": "A 3-approver test document comes out with all three signature blocks and approval numbers in the right places.",
        "learn_first": "PyMuPDF (fitz), PDF coordinate system, Pillow image resize.",
        "needs": "Steps 15, 18",
        "unlocks": "Step 26",
        "tip": "PDF coordinates start at the top-left corner and are measured in points. Try on one test PDF and adjust the numbers until it looks right.",
        "starter_code": """```python
import fitz # PyMuPDF

pdf = fitz.open("original.pdf")
page = pdf[-1] # last page
rect = fitz.Rect(50, 700, 150, 760) # x0, y0, x1, y1 (points)
page.insert_image(rect, filename="hod_signature.png")
page.insert_text((50, 775), "APH-2026-00012-1", fontsize=9)
pdf.save("final.pdf")
```"""
    },
    16: {
        "step": "31",
        "title": "Step 31: Integrate web and app with the real API",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "Critical",
        "effort": "5 pts (~5 hours)",
        "why": "Parts built separately often do not fit; this step makes them fit.",
        "what": "Replace all fake data with real API calls and fix mismatches.",
        "how": [
            "Merge all branches into main with Git and resolve conflicts together.",
            "Sit with the other three members and run each page and screen against the real backend.",
            "Fix field name or format mismatches either in the API or in the frontend."
        ],
        "done_when": "The complete journey works on both web and app without fake data.",
        "learn_first": "Git conflict resolution, integration debugging.",
        "needs": "Steps 22, 23, 26, 28, 29, 30",
        "unlocks": "Step 32",
        "tip": None,
        "starter_code": None
    },
    17: {
        "step": "7",
        "title": "Step 7: Prepare dummy data and sample files",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "3 pts (~3 hours)",
        "why": "Realistic test data lets everyone test from day one instead of waiting for the full system.",
        "what": "Create realistic test data and sample files.",
        "how": [
            "Make a list of 10 dummy users: 3 applicants, 6 approvers with posts like HOD, Dean, Principal, Professor, Director, and 1 admin.",
            "Prepare 5 sample scanned documents (PDF and image).",
            "Create sample signature, stamp and seal images as PNG files with transparent background.",
            "Save everything in a shared folder and name files clearly (for example `hod_signature.png`)."
        ],
        "done_when": "The sample folder is shared and every file is named clearly.",
        "learn_first": "Image transparency tools, structuring test fixtures.",
        "needs": "Step 2",
        "unlocks": "The final project / testing across all phases",
        "tip": None,
        "starter_code": None
    },
    18: {
        "step": "9",
        "title": "Step 9: Registration and login with password hashing",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Passwords must never be stored as plain text. This is the base of all security.",
        "what": "Let users create accounts and log in safely.",
        "how": [
            "Build `POST /api/register` and `POST /api/login`.",
            "Hash passwords with `generate_password_hash` and check them with `check_password_hash` from `werkzeug.security`.",
            "On successful login return a token (JWT) or start a session, together with the user's role.",
            "Test everything in Postman before any page exists."
        ],
        "done_when": "Postman can register a user and log in and gets a token. A wrong password is rejected.",
        "learn_first": "Flask routes, password hashing, sessions versus JWT.",
        "needs": "Step 8",
        "unlocks": "Steps 10, 11, 13, 14, 15, 24",
        "tip": "Hashing is one-way: you can check a password against a hash but never turn the hash back into the password.",
        "starter_code": None
    },
    19: {
        "step": "10",
        "title": "Step 10: Role-based access",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "Without it, an applicant could approve their own document.",
        "what": "Make sure each role sees and does only what it should.",
        "how": [
            "Write a small decorator that checks the logged-in user's role before running a route.",
            "Protect routes: admin-only routes reject others; an approver sees only documents waiting for them; an applicant sees only their own documents."
        ],
        "done_when": "Calling an approver route with an applicant token returns a clear 403 error.",
        "learn_first": "Python decorators (simple level).",
        "needs": "Step 9",
        "unlocks": "Steps 27, 30",
        "tip": None,
        "starter_code": """```python
from functools import wraps
from flask import jsonify

def requires_role(role):
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            if current_user_role() != role: # read role from token
                return jsonify(error="Forbidden"), 403
            return fn(*args, **kwargs)
        return inner
    return wrapper
```"""
    },
    20: {
        "step": "13",
        "title": "Step 13: Base layout, login and registration pages (web)",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "These are the first pages everyone sees, and they set the design for all later pages.",
        "what": "Build the first web pages.",
        "how": [
            "Create a base template (navbar, footer, CSS) following Shreya Sutar's designs.",
            "Build login and registration pages with form checks in JavaScript (empty fields, email format, password length).",
            "Use `fetch()` to call the login and register endpoints and save the token in the browser."
        ],
        "done_when": "A user can register and log in from the browser and is taken to a dashboard placeholder.",
        "learn_first": "HTML forms, CSS Flexbox, JavaScript fetch and async/await.",
        "needs": "Steps 5, 6, 9",
        "unlocks": "Final project / web dashboard",
        "tip": None,
        "starter_code": None
    },
    21: {
        "step": "11",
        "title": "Step 11: Document upload with validation",
        "phase": "Phase 1 - Foundation",
        "week": "Week 3",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Users can upload anything, so the system must refuse dangerous or oversized files.",
        "what": "Accept scanned documents safely.",
        "how": [
            "Build `POST /api/documents/upload`.",
            "Allow only PDF, JPG and PNG, with a size limit (for example 10 MB). Clean the name with `secure_filename` and save it with a unique name in the uploads folder.",
            "Create a document row with status `in_progress` and `current_step 1`."
        ],
        "done_when": "Uploading a PDF in Postman saves the file and a row; uploading an .exe file is rejected.",
        "learn_first": "Flask file uploads, secure file names, file validation.",
        "needs": "Step 9",
        "unlocks": "Step 12",
        "tip": None,
        "starter_code": None
    },
    22: {
        "step": "22",
        "title": "Step 22: Applicant and approver dashboards (web)",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "9 pts (~9 hours)",
        "why": "These are the pages users actually use every day.",
        "what": "Build the main working pages.",
        "how": [
            "**Applicant dashboard:** upload form, approver selection by post and department, and a list of my documents with coloured status badges.",
            "**Approver dashboard:** pending list with buttons Approve, Keep Pending, Send Compliance and a remark box.",
            "Connect with `fetch()` to the real endpoints. While the backend is not ready, use fake JSON data."
        ],
        "done_when": "An applicant can upload and pick approvers, and an approver can see and act on a document, all from the browser.",
        "learn_first": "DOM manipulation, rendering lists from JSON, CSS for tables and badges.",
        "needs": "Steps 18, 19",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    23: {
        "step": "24",
        "title": "Step 24: Search and filter API",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "With many documents, users need to find one quickly.",
        "what": "Let users find documents quickly.",
        "how": [
            "Build `GET /api/documents?status=&q=&from=&to=` that filters by status, title keyword and date range.",
            "Use SQLAlchemy filters, with `LIKE` for keyword search.",
            "Respect roles: applicants see only their documents, approvers see only theirs."
        ],
        "done_when": "Searching by keyword and filtering by status gives correct results in Postman.",
        "learn_first": "SQL WHERE, LIKE, ORDER BY, SQLAlchemy filtering.",
        "needs": "Step 9",
        "unlocks": "Step 28",
        "tip": None,
        "starter_code": None
    },
    24: {
        "step": "28",
        "title": "Step 28: Status page, search and filter UI, download page (web)",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "7 pts (~7 hours)",
        "why": "This completes the website and makes the timeline visible.",
        "what": "Complete the website.",
        "how": [
            "**Status page:** show the live timeline for one document.",
            "**Search box and filter dropdowns** that call the search API.",
            "**Download center page** listing final documents with download buttons.",
            "**PIN entry page** that calls the PIN API."
        ],
        "done_when": "Every page in the designs exists and works on desktop and on a phone-sized screen.",
        "learn_first": "Responsive CSS and media queries.",
        "needs": "Steps 20, 24, 26",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    25: {
        "step": "34",
        "title": "Step 34: Deploy online",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "A live link lets the guide and examiners try the project on their own phones.",
        "what": "Put the backend online.",
        "how": [
            "Use Render or PythonAnywhere. Add gunicorn and set environment variables for secret keys.",
            "Update the app and web to use the live URL.",
            "Test on a real phone with mobile data."
        ],
        "done_when": "You can open the live link from a phone and complete one full approval.",
        "learn_first": "Environment variables, gunicorn, deploying a Flask app.",
        "needs": "Step 33",
        "unlocks": "Steps 35, 36",
        "tip": None,
        "starter_code": None
    },
    26: {
        "step": "6",
        "title": "Step 6: Create UI designs for all screens",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "8 pts (~8 hours)",
        "why": "Designing first means the code is written once, not rewritten after the team changes its mind.",
        "what": "Design how every web page and app screen looks.",
        "how": [
            "Pick a colour theme (2 main colours), a logo and an icon style.",
            "In Figma or Canva design: login, register, applicant dashboard, upload and approver selection, status timeline, approver dashboard, profile (signature, stamp, seal upload), PIN screen, admin panel, download center.",
            "Make one version for web (wide) and one for the app (narrow).",
            "Export images and share the link with the team."
        ],
        "done_when": "All screens exist as designs and the team has agreed on them. Shravani and Shreya Sutar build from these.",
        "learn_first": "Basic UI/UX, Figma frames and components.",
        "needs": "Step 3",
        "unlocks": "Steps 13, 14",
        "tip": None,
        "starter_code": None
    },
    27: {
        "step": "14",
        "title": "Step 14: Flutter project and login screen",
        "phase": "Phase 1 - Foundation",
        "week": "Week 2",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Starting the app early reveals setup problems while there is still time to fix them.",
        "what": "Start the mobile app.",
        "how": [
            "Create the Flutter project in the `mobile` folder and run it on an emulator or a real phone.",
            "Build login and register screens from the designs.",
            "Use the `http` package to call the login API and store the token with `flutter_secure_storage`."
        ],
        "done_when": "You can log in from the app and a token is stored.",
        "learn_first": "Dart basics, Flutter widgets, http package.",
        "needs": "Steps 5, 6, 9",
        "unlocks": "Final project / mobile dashboards",
        "tip": None,
        "starter_code": None
    },
    28: {
        "step": "23",
        "title": "Step 23: Applicant and approver screens (app)",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "9 pts (~9 hours)",
        "why": "The app is the mobile version of the same journey.",
        "what": "Build the main app screens.",
        "how": [
            "**Applicant:** upload using camera or gallery (`image_picker`), approver selection, document list with status.",
            "**Approver:** pending list and action buttons with a remark.",
            "Convert JSON from the API into Dart model classes."
        ],
        "done_when": "An applicant can upload from the phone and an approver can act on a document in the app.",
        "learn_first": "ListView, forms, navigation, JSON parsing, image_picker.",
        "needs": "Steps 18, 19",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    29: {
        "step": "20",
        "title": "Step 20: Live approval timeline",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "The applicant must see progress at every moment; this also acts as an audit log.",
        "what": "Record every event so progress can be followed.",
        "how": [
            "Write one helper `add_timeline(document_id, text)` and call it at every important point: uploaded, sent to approver, approved by X, compliance by Y, fulfilled, completed.",
            "Build `GET /api/documents/{id}/timeline` returning events in time order."
        ],
        "done_when": "After a full approval run the timeline reads like a story from upload to completion.",
        "learn_first": "Flask routes, SQLAlchemy queries.",
        "needs": "Step 18",
        "unlocks": "Steps 28, 29",
        "tip": None,
        "starter_code": None
    },
    30: {
        "step": "26",
        "title": "Step 26: Final document and final hash",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "Locking the finished document means nobody can change it after approval without detection.",
        "what": "Lock the finished document.",
        "how": [
            "Compute SHA-256 of the stamped file and store it in `documents.final_hash` and `final_path`.",
            "Build `GET /api/documents/{id}/download` that re-checks the final hash before sending the file.",
            "Add the timeline event 'Final document generated'."
        ],
        "done_when": "Downloading a final document works; a modified final file is refused.",
        "learn_first": "Flask send_file, reusing the hashing function from Step 12.",
        "needs": "Step 25",
        "unlocks": "Steps 28, 31",
        "tip": None,
        "starter_code": None
    },
    31: {
        "step": "27",
        "title": "Step 27: PIN lock logic",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "High",
        "effort": "4 pts (~4 hours)",
        "why": "A PIN adds a second layer of protection on web and app.",
        "what": "Support the extra PIN protection.",
        "how": [
            "Build `POST /api/pin/set` and `POST /api/pin/verify`. Store only the hashed PIN (same hashing as passwords).",
            "Limit wrong attempts (for example 5) and then block for a few minutes."
        ],
        "done_when": "A PIN can be set and verified, and 5 wrong tries lock it for a few minutes.",
        "learn_first": "Hashing a PIN (same method as passwords), Flask routes.",
        "needs": "Step 10",
        "unlocks": "Step 29",
        "tip": None,
        "starter_code": None
    },
    32: {
        "step": "29",
        "title": "Step 29: Timeline, profile, PIN and biometric lock (app)",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "8 pts (~8 hours)",
        "why": "These screens complete the app and add its special mobile features.",
        "what": "Complete the app.",
        "how": [
            "Timeline screen showing events from the API.",
            "Profile screen where an approver uploads signature, stamp and seal with the profile API.",
            "PIN screen and fingerprint or face lock using the `local_auth` package.",
            "If Flutter becomes too hard, make the website fully mobile-responsive as a fallback."
        ],
        "done_when": "The app has all screens from the designs and the biometric prompt appears when opening the app.",
        "learn_first": "local_auth package, file picker, Flutter navigation.",
        "needs": "Steps 15, 20, 27",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    33: {
        "step": "35",
        "title": "Step 35: README and API documentation",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Good documentation shows professionalism and helps you in interviews.",
        "what": "Document how to run and use the project.",
        "how": [
            "Write a README with project description, features, tech stack, setup steps and screenshots.",
            "Turn the API list into final documentation with example requests and responses."
        ],
        "done_when": "Someone new can follow the README and run the project.",
        "learn_first": "Markdown formatting, API documentation standards.",
        "needs": "Step 34",
        "unlocks": "Step 38",
        "tip": None,
        "starter_code": None
    },
    34: {
        "step": "5",
        "title": "Step 5: Write the API list",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Shravani and Shreya Sutar cannot build their pages until they know which addresses to call.",
        "what": "List every endpoint so frontend and app builders know what to call and what they get back. Shreeyash reviews it before it is shared.",
        "how": [
            "Make a table with: method (GET or POST), URL, what is sent, what comes back. Example: `POST /api/login` receives email and password, returns token and role.",
            "Use the starter list in Section 10 of the blueprint as your base and fill in the exact fields.",
            "Save it in the docs folder and share it. Explain it to each teammate in 10 minutes."
        ],
        "done_when": "Shreeyash has reviewed the list, and Shravani and Shreya Sutar confirm they understand each endpoint.",
        "learn_first": "REST basics: methods, URLs, JSON request and response.",
        "needs": "Step 4",
        "unlocks": "Steps 13, 14",
        "tip": None,
        "starter_code": None
    },
    35: {
        "step": "15",
        "title": "Step 15: Approver profile API (signature, stamp, seal)",
        "phase": "Phase 1 - Foundation",
        "week": "Week 3",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "The final document needs each approver's own images. This API collects them.",
        "what": "Let each approver upload the three images that will be printed on documents.",
        "how": [
            "Build `POST /api/profile/assets` accepting three PNG images: signature, stamp, seal.",
            "Validate file type and size, save in `uploads/assets/user_id`, and store the paths in the users table.",
            "Build `GET /api/profile` to return what is uploaded.",
            "Agree with Shreeyash on: PNG only, transparent background, fixed folder names."
        ],
        "done_when": "An approver can upload all three images and fetch them again; a non-PNG file is rejected.",
        "learn_first": "Flask file upload and basic validation.",
        "needs": "Step 9",
        "unlocks": "Steps 25, 29",
        "tip": None,
        "starter_code": None
    },
    36: {
        "step": "16",
        "title": "Step 16: Approver selection and approval chain",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "This is where the document gets its route: who approves, and in what order.",
        "what": "Create the ordered list of approvers for a document.",
        "how": [
            "Build `GET /api/approvers?post=HOD&department=IT` so the uploader can search approvers by post.",
            "Build `POST /api/documents/{id}/chain` that receives approver ids in order and creates `approval_steps` rows with `step_order 1, 2, 3`.",
            "Set step 1 to `pending` and all the others to `waiting`."
        ],
        "done_when": "A document with 3 approvers shows step 1 pending and steps 2 and 3 waiting in the database.",
        "learn_first": "SQLAlchemy relationships and queries, Flask routes.",
        "needs": "Step 12",
        "unlocks": "Step 17",
        "tip": None,
        "starter_code": None
    },
    37: {
        "step": "19",
        "title": "Step 19: Compliance flow (take back or fulfil)",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 5",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Real approvers often ask for corrections. Without this the applicant would have to start over.",
        "what": "Let the applicant respond when an approver sends compliance.",
        "how": [
            "Build `POST /api/documents/{id}/fulfil`: the applicant uploads a corrected file, a new hash is stored, and the same approver gets it again.",
            "Build `POST /api/documents/{id}/withdraw` for taking the request back.",
            "Keep the old file's hash in the timeline for history."
        ],
        "done_when": "After compliance, the applicant can fix and resubmit, and the document returns to the same approver.",
        "learn_first": "Flask file upload, SQLAlchemy updates.",
        "needs": "Step 18",
        "unlocks": "Steps 22, 23",
        "tip": None,
        "starter_code": None
    },
    38: {
        "step": "30",
        "title": "Step 30: Admin panel and download center API",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "7 pts (~7 hours)",
        "why": "The admin creates approvers, and users need to fetch their final documents.",
        "what": "Give the admin control and finish the remaining APIs.",
        "how": [
            "**Admin routes:** list users, add or edit a user, set role, post and department, deactivate a user.",
            "**Download center API:** list the final documents of the logged-in user (`GET /api/downloads`).",
            "A simple admin web page for these actions (coordinate with Shravani for styling)."
        ],
        "done_when": "The admin can create an approver with a post and department, and that approver appears in the approver search.",
        "learn_first": "Admin-only routes, CRUD operations.",
        "needs": "Step 10",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    39: {
        "step": "32",
        "title": "Step 32: Full testing and bug list (40+ test cases)",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "8 pts (~8 hours)",
        "why": "Bugs found now cost minutes; bugs found during the demo cost marks.",
        "what": "Find problems before the demo.",
        "how": [
            "Write at least 40 test cases in a sheet: test id, steps, expected result, actual result, status, severity.",
            "Test: single approver, three approvers in order, wrong approver trying to act, compliance and fulfil, withdraw, tampered file, wrong password, wrong file type, large file, PIN lock.",
            "Report each bug to its owner with exact steps to reproduce."
        ],
        "done_when": "Every test case has a result and every serious bug has an owner.",
        "learn_first": "Writing test cases, bug reports.",
        "needs": "Step 31",
        "unlocks": "Step 33",
        "tip": None,
        "starter_code": None
    },
    40: {
        "step": "36",
        "title": "Step 36: Final report, literature survey and references",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "8 pts (~8 hours)",
        "why": "The report is what the college officially evaluates.",
        "what": "Write the college submission.",
        "how": [
            "Follow the 8 headings: title, objectives, literature survey, work methodology, features/hardware/software/cost estimation, expected outcome, conclusion and future scope, references.",
            "Collect a short paragraph from each member about their own module.",
            "Add screenshots, the database diagram and the flow diagram."
        ],
        "done_when": "The report is complete and the guide has reviewed it.",
        "learn_first": "Synopsis format (8 headings), IEEE-style references.",
        "needs": "Step 34",
        "unlocks": "Steps 37, 38",
        "tip": None,
        "starter_code": None
    },
    41: {
        "step": "37",
        "title": "Step 37: Presentation and demo script",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "A good demo makes the project look as strong as it is.",
        "what": "Prepare to present.",
        "how": [
            "Make 10 to 12 slides: problem, solution, features, architecture, database, screens, demo, future scope.",
            "Write a 5-minute demo script: upload, choose 3 approvers, approve in order, compliance case, tamper detection, final stamped document.",
            "Everyone rehearses their own part."
        ],
        "done_when": "The team can run the full demo in 5 minutes without errors.",
        "learn_first": "Presentation structuring, elevator pitch, demo scripting.",
        "needs": "Step 36",
        "unlocks": "Step 38",
        "tip": None,
        "starter_code": None
    },
    42: {
        "step": "E1",
        "title": "E1 - EXTRA: Coordinate-based stamping at user-chosen positions",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Allows dynamic placement of signatures and stamps anywhere on the document instead of fixed slots.",
        "what": "Implement coordinate-based stamping receiving (x, y) coordinates from frontend/uploader.",
        "how": [
            "Extend document processing API to accept dynamic (x, y, page) coordinates for each approver.",
            "Translate UI coordinates to PyMuPDF point coordinates.",
            "Apply signatures and stamps accurately at specified coordinates."
        ],
        "done_when": "Signatures stamp exactly where specified by coordinates in the API request.",
        "learn_first": "PDF coordinate transforms, PyMuPDF page dimensions.",
        "needs": "Step 25",
        "unlocks": "Step 44 (E3)",
        "tip": None,
        "starter_code": None
    },
    43: {
        "step": "E2",
        "title": "E2 - EXTRA: QR code on final PDF + GET /api/verify/{approval_no}",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Allows instant physical-to-digital authenticity verification by scanning the document QR code.",
        "what": "Generate QR code with verification URL pointing to the backend and stamp it on the PDF.",
        "how": [
            "Use `qrcode` library to generate QR code containing verification link: `https://<domain>/verify/<approval_no>`.",
            "Stamp the QR code in the footer/header of the final PDF alongside approval credentials.",
            "Build endpoint `GET /api/verify/{approval_no}` returning validity, signer names, timestamps, and document hash."
        ],
        "done_when": "Scanning the printed/PDF QR code opens verification details confirming document authenticity.",
        "learn_first": "Python qrcode library, PyMuPDF image insertion.",
        "needs": "Step 25",
        "unlocks": "Step 45 (E4)",
        "tip": None,
        "starter_code": None
    },
    44: {
        "step": "E3",
        "title": "E3 - EXTRA: Drag-and-drop signature block placement on A4 preview (web)",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "8 pts (~8 hours)",
        "why": "Gives applicants intuitive visual control over where approvers will sign on their document.",
        "what": "Build an interactive PDF canvas preview allowing drag-and-drop signature zones.",
        "how": [
            "Render PDF page preview using PDF.js or canvas.",
            "Enable drag-and-drop signature boxes assigned to selected approvers.",
            "Capture normalized coordinates (x%, y%) and send them with the approval chain payload."
        ],
        "done_when": "Applicant can drag approver tags on the preview and positions are passed to the backend.",
        "learn_first": "HTML5 Drag and Drop API / interact.js, PDF.js rendering.",
        "needs": "Step 22, Step 42 (E1)",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    45: {
        "step": "E4",
        "title": "E4 - EXTRA: Public 'Verify document' web page",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "Enables third parties (companies, colleges, employers) to verify document legitimacy without logging in.",
        "what": "Build a clean public verification portal.",
        "how": [
            "Build public route `/verify/:approval_no` and `/verify` search bar.",
            "Fetch verification status and approver audit chain from `GET /api/verify/{approval_no}`.",
            "Display green verified badge, approver details, date/time, and original hash."
        ],
        "done_when": "Entering a valid approval number displays verification certificate; invalid numbers show warning.",
        "learn_first": "Public unauthenticated routes in Flask, status display card design.",
        "needs": "Step 43 (E2)",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    46: {
        "step": "E5",
        "title": "E5 - EXTRA: Notifications (API + app)",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Alerts users instantly when an approval is requested or an action is taken.",
        "what": "Implement notification bell and push/in-app alert system.",
        "how": [
            "Create notifications table (`id`, `user_id`, `title`, `message`, `is_read`, `created_at`).",
            "Trigger notifications on: new document pending, approved, compliance requested.",
            "Add notification bell UI in Flutter and web dashboard."
        ],
        "done_when": "Approver receives notification when a document is assigned to them; applicant notified on status changes.",
        "learn_first": "In-app notification badge logic, polling or WebSockets.",
        "needs": "Step 20",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    47: {
        "step": "E6",
        "title": "E6 - EXTRA: QR scanner screen in the app",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "Enables rapid camera verification of printed certificates directly within the mobile app.",
        "what": "Build a camera QR scanner screen in Flutter.",
        "how": [
            "Add `mobile_scanner` or `qr_code_scanner` Flutter package.",
            "Open camera view, scan document QR code, extract approval number.",
            "Navigate to verification result screen showing validity and signatures."
        ],
        "done_when": "App camera scans document QR and displays instant verification results.",
        "learn_first": "Flutter mobile_scanner package, camera permissions.",
        "needs": "Step 43 (E2), Step 23",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    48: {
        "step": "E7",
        "title": "E7 - EXTRA: Admin search by approval number + audit log",
        "phase": "Phase 3 - Document processing and extras",
        "week": "Week 6",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Allows institutional administrators to audit past approvals and track compliance history.",
        "what": "Create audit log viewer and search by approval number in admin panel.",
        "how": [
            "Add `GET /api/admin/audit-logs` returning full system actions with timestamps and IP/user.",
            "Add search filter by approval number (`APH-...`) to look up full approval history.",
            "Create admin view displaying timeline, previous compliance notes, and timestamps."
        ],
        "done_when": "Admin can search any approval number and see the entire unalterable audit log.",
        "learn_first": "Audit logging design, complex query filtering.",
        "needs": "Step 30",
        "unlocks": "Step 31",
        "tip": None,
        "starter_code": None
    },
    49: {
        "step": "E8",
        "title": "E8 - EXTRA: Automated pytest tests + GitHub Actions CI",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Ensures pull requests do not break existing backend logic and demonstrates industry-grade CI practices.",
        "what": "Setup automated test suite and GitHub Actions workflow.",
        "how": [
            "Write pytest unit tests in `tests/` covering: register/login, document upload, hash validation, sequence transitions, tampering detection.",
            "Create `.github/workflows/ci.yml` running pytest on every push and pull request to `main`."
        ],
        "done_when": "GitHub Actions executes and shows green checkmark for all tests on pull requests.",
        "learn_first": "pytest fixtures, GitHub Actions syntax.",
        "needs": "Step 32",
        "unlocks": "Step 34",
        "tip": None,
        "starter_code": None
    },
    50: {
        "step": "1",
        "title": "Step 1: Install your tools (everyone)",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "Equal share (~2-3 hours each)",
        "why": "Without the same tools, code that works on one laptop fails on another.",
        "what": "Get your computer ready for the project.",
        "how": [
            "1. Install **Python 3.11 or newer** (tick 'Add Python to PATH' on Windows), **VS Code**, **Git**, and **Postman**.",
            "2. **Shreya Sutar** also installs **Flutter SDK** and **Android Studio**.",
            "3. **Shreeyash, Shravani and Shreya Loya** also install **DB Browser for SQLite**.",
            "4. Open a terminal and run `python --version` and `git --version`. Both must show a version number.",
            "5. Create a GitHub account if you do not have one. Share your GitHub username in the team group."
        ],
        "done_when": "Every member can run both commands, has their specific role tools installed, and has a GitHub account.",
        "learn_first": "Basic command line / terminal navigation.",
        "needs": "Nothing, this is the starting point.",
        "unlocks": "Steps 2, 3",
        "tip": "Install everything on the same day and help each other. A broken setup is the number one reason beginners lose a week.",
        "starter_code": None
    },
    51: {
        "step": "3",
        "title": "Step 3: Learn your week 1 basics (everyone)",
        "phase": "Phase 0 - Setup and Planning",
        "week": "Week 1",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "Equal share (~3-4 hours each)",
        "why": "You will not understand the later steps without these basics.",
        "what": "Study just enough to start building. Do not try to learn everything at once.",
        "how": [
            "1. **Everyone:** Starts with Git and how HTTP works.",
            "   - **Shreeyash:** Python basics, SQL tables and project structure.",
            "   - **Shravani:** Python and Flask basics, HTML and CSS.",
            "   - **Shreya Sutar:** UI/UX basics, Figma and Dart basics.",
            "   - **Shreya Loya:** Python and Flask basics, REST and API design basics.",
            "2. **Everyone:** Learn how HTTP requests, JSON and APIs work. Watch one short video, then send a request to any public API using Postman.",
            "3. **Everyone:** Practice Git commands from Step 2 (clone, branch, commit, push)."
        ],
        "done_when": "Each person has built one tiny practice program in their own area (see Section 9 in the blueprint for practice tasks).",
        "learn_first": "Core basics for your assigned role.",
        "needs": "Step 1",
        "unlocks": "Step 6",
        "tip": None,
        "starter_code": None
    },
    52: {
        "step": "33",
        "title": "Step 33: Fix bugs in your module and run security check (everyone)",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "Equal share (~3-4 hours each)",
        "why": "A working project must also be a safe one.",
        "what": "Make the project reliable and secure.",
        "how": [
            "1. Each owner fixes bugs found in their own module from Step 32 test cases.",
            "2. Security checks to verify together:",
            "   - Passwords and PINs are securely hashed (never stored plaintext).",
            "   - Routes are properly protected by role checks (403 Forbidden).",
            "   - File types and upload size limits are strictly validated.",
            "   - No secret keys, passwords, or personal credentials pushed to GitHub.",
            "   - Uploads folder is not directly browsable."
        ],
        "done_when": "No serious bug remains in the bug list and all security checks pass.",
        "learn_first": "Basic OWASP security concepts for web & mobile.",
        "needs": "Step 32",
        "unlocks": "Step 34",
        "tip": None,
        "starter_code": None
    },
    53: {
        "step": "38",
        "title": "Step 38: Final review and submission (everyone)",
        "phase": "Phase 5 - Documentation and submission",
        "week": "Week 8",
        "owner_name": "Everyone",
        "assignees": ALL_MEMBERS,
        "importance": "Medium",
        "effort": "Equal share (~3 hours each)",
        "why": "Closing the project properly and ensuring full marks in college evaluation.",
        "what": "Conduct final rehearsal, get guide approval, and submit.",
        "how": [
            "1. Show the complete working project to the project guide, note the feedback and fix any issues.",
            "2. Rehearse the 5-minute live demo script with all four members presenting their own module.",
            "3. Tag the final GitHub version (`git tag v1.0 && git push --tags`).",
            "4. Submit the final printed/digital report with guide signature."
        ],
        "done_when": "Report submitted and demo approved by the guide.",
        "learn_first": "Final presentation delivery.",
        "needs": "Steps 35, 36, 37",
        "unlocks": "Final Project Completion! 🎉",
        "tip": None,
        "starter_code": None
    }
}

def format_issue_body(info):
    assignee_handles = ", ".join([f"@{a}" for a in info["assignees"]])
    
    lines = [
        "### 📋 Task Overview",
        f"- **Step:** {info['step']}",
        f"- **Phase:** {info['phase']}",
        f"- **Week:** {info['week']}",
        f"- **Owner:** {info['owner_name']} ({assignee_handles})",
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
        "### 🛠️ How (Action Steps):",
    ]
    for action in info["how"]:
        lines.append(f"- {action}")
        
    lines.extend([
        "",
        "### ✅ Done when (Acceptance Criteria)",
        info["done_when"],
        "",
        "### 💡 Learn first",
        info["learn_first"],
        "",
        "### 🔗 Dependencies",
        f"- **Needs:** {info['needs']}",
        f"- **Unlocks:** {info['unlocks']}",
    ])
    
    if info.get("tip"):
        lines.extend([
            "",
            "### 📌 Pro Tip",
            f"> {info['tip']}",
        ])
        
    if info.get("starter_code"):
        lines.extend([
            "",
            "### 💻 Starter Code / Example",
            info["starter_code"],
        ])
        
    lines.extend([
        "",
        "---",
        "### 📋 Definition of Done Checklist",
        "- [ ] Work on your dedicated branch",
        "- [ ] Implement according to blueprint specifications",
        "- [ ] Verify with Postman / unit tests / UI preview",
        "- [ ] Open Pull Request for review and merge into main",
    ])
    
    return "\n".join(lines)

def main():
    print(f"Starting update of {len(ISSUES_DATA)} issues on {REPO}...")
    success_count = 0
    fail_count = 0
    
    for issue_num, info in sorted(ISSUES_DATA.items()):
        body = format_issue_body(info)
        cmd = [
            "gh", "issue", "edit", str(issue_num),
            "--repo", REPO,
            "--title", info["title"],
            "--body", body,
        ]
        for a in info["assignees"]:
            cmd.extend(["--add-assignee", a])
            
        print(f"Updating Issue #{issue_num}: {info['title']} -> {info['owner_name']} ...", end=" ")
        sys.stdout.flush()
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("✓ OK")
            success_count += 1
        else:
            print(f"✗ FAILED: {res.stderr.strip()}")
            fail_count += 1
            
        time.sleep(0.4)  # prevent hitting GitHub secondary rate limits
        
    print(f"\nFinished! Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
