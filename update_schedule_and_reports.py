import subprocess
import json
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

# 1. Update Milestones with exact deadlines
MILESTONES = {
    2: {"title": "Week 1", "due_on": "2026-11-09T18:29:59Z", "desc": "Deadline: Nov 9, 2026 - Setup, DB Architecture, Tooling, UI Wireframes & API Contracts"},
    3: {"title": "Week 2", "due_on": "2026-11-16T18:29:59Z", "desc": "Deadline: Nov 16, 2026 - Foundation: Auth, Password Hashing, RBAC, Flutter Setup & Web Layouts"},
    4: {"title": "Week 3", "due_on": "2026-11-23T18:29:59Z", "desc": "Deadline: Nov 23, 2026 - Secure Uploads, SHA-256 Hashing, Approver Profiles & Asset Management"},
    5: {"title": "Week 4", "due_on": "2026-11-30T18:29:59Z", "desc": "Deadline: Nov 30, 2026 - Core Approval Engine, Approver Chains, Dashboards & REPORT 1 (Mid-Term Submission)"},
    6: {"title": "Week 5", "due_on": "2026-12-07T18:29:59Z", "desc": "Deadline: Dec 7, 2026 - Tamper Verification, Compliance Flow, Filter APIs & Live Timeline"},
    7: {"title": "Week 6", "due_on": "2026-12-14T18:29:59Z", "desc": "Deadline: Dec 14, 2026 - PDF Stamping, QR Codes, Drag-and-Drop Placement, Public Verify Portal, PIN & Biometrics, Audit Logs"},
    8: {"title": "Week 7", "due_on": "2026-12-21T18:29:59Z", "desc": "Deadline: Dec 21, 2026 - System-Wide Integration, CI Pipeline, QR Scanner, 40+ QA Test Cases, Online Deployment"},
    9: {"title": "Week 8", "due_on": "2026-12-30T18:29:59Z", "desc": "Deadline: Dec 30, 2026 - Final Project Documentation, REPORT 2 (Final Submission), Slide Deck & Demo -> Final Guide Signoff"},
}

def update_milestones():
    print("Updating milestones with deadlines...")
    for ms_num, data in MILESTONES.items():
        cmd = [
            "gh", "api", "-X", "PATCH", f"repos/{REPO}/milestones/{ms_num}",
            "-f", f"title={data['title']}",
            "-f", f"due_on={data['due_on']}",
            "-f", f"description={data['desc']}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [OK] Milestone {data['title']} -> {data['due_on'][:10]}")
        else:
            print(f"  [ERR] Milestone {ms_num}: {res.stderr.strip()}")

# 2. Re-integrate E1-E8 into the core sequence and rename them
UPDATED_EXTRA_ISSUES = {
    42: {
        "title": "Step 25B: Dynamic coordinate-based stamping engine",
        "step": "25B",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "5 pts (~5 hours)",
        "why": "Enables dynamic placement of signatures and stamps anywhere on uploaded forms, petitions, or applications according to custom document templates.",
        "what": "Extend the PyMuPDF stamping engine to receive coordinate payloads (x, y, page) from the frontend or approval route.",
        "how": [
            "Extend document processing module to accept dynamic `(x, y, page)` coordinate tuples per approver.",
            "Map frontend coordinate space (percentage or canvas pixels) to standard PyMuPDF point coordinates (72 points/inch).",
            "Insert approver signatures, authority stamps, and unique approval numbers exactly at the designated coordinates.",
            "Verify output on multi-page and various standard paper sizes (A4, Letter)."
        ],
        "done_when": "Signatures and stamps are accurately rendered on the PDF at the coordinates supplied in the approval request payload.",
        "learn_first": "PyMuPDF coordinate systems, point scaling, Pillow transparent overlays.",
        "needs": "Step 25 (Base Stamping)",
        "unlocks": "Step 22B (Drag-and-Drop Placement)",
        "parallel_fallback": "If waiting for coordinate inputs from frontend, implement coordinate validation and unit test cases with mock (x, y) coordinates.",
    },
    43: {
        "title": "Step 25C: QR code PDF stamping & verification API",
        "step": "25C",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreeyash Solunke",
        "assignees": [USERS["Shreeyash"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Bridges physical printouts with online verification. Anyone holding a printed approved letter can scan the QR code to verify its authenticity instantly.",
        "what": "Generate dynamic QR code pointing to the live verification endpoint, stamp it on the PDF, and provide the verification API.",
        "how": [
            "Integrate Python `qrcode` library to generate a QR image encoding: `https://<deployed-url>/verify/<approval_no>`.",
            "Use PyMuPDF to stamp the QR code image neatly on the header or footer margin of the final PDF.",
            "Build public verification endpoint `GET /api/verify/{approval_no}` returning document status, original hash, approver chain, and sign timestamps."
        ],
        "done_when": "Scanning the stamped QR code opens the verification API returning JSON confirming document legitimacy.",
        "learn_first": "Python qrcode library, PyMuPDF image insertion.",
        "needs": "Step 25 (Base Stamping)",
        "unlocks": "Step 28B (Public Verify Web Page), Step 29B (App QR Scanner)",
        "parallel_fallback": "If the live deployed domain is not finalized, use localhost / relative path configuration and test QR generation with dummy approval numbers.",
    },
    44: {
        "title": "Step 22B: Interactive drag-and-drop signature placement canvas (web)",
        "step": "22B",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "High",
        "effort": "8 pts (~8 hours)",
        "why": "Gives applicants a seamless visual interface to decide where each approver should sign on their uploaded document.",
        "what": "Build an interactive web canvas previewing the uploaded PDF/image where users can drag and drop approver signature badges.",
        "how": [
            "Render PDF pages on HTML5 canvas using PDF.js or rendered image preview.",
            "Create draggable approver badge components (HOD, Dean, Principal) with HTML Drag & Drop or interact.js.",
            "Calculate normalized percentage coordinates `(x%, y%)` relative to canvas width/height upon drop.",
            "Submit the coordinate array along with the approver chain payload to the backend."
        ],
        "done_when": "Applicant can drag approver tags onto document preview and submit their relative positions to the backend.",
        "learn_first": "PDF.js canvas rendering, HTML5 drag and drop events.",
        "needs": "Step 22 (Applicant Dashboard), Step 25B (Coordinate Engine)",
        "unlocks": "Step 31 (Full Integration)",
        "parallel_fallback": "If Step 25B backend is in progress, build the canvas UI and drag-and-drop interaction using static mock image files in browser.",
    },
    45: {
        "title": "Step 28B: Public document verification web portal",
        "step": "28B",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shravani",
        "assignees": [USERS["Shravani"]],
        "importance": "Medium",
        "effort": "4 pts (~4 hours)",
        "why": "External verifiers (college authorities, employers, third-party reviewers) need an intuitive portal to confirm document authenticity without requiring a login account.",
        "what": "Build an unauthenticated public verification page with search bar and certificate viewer.",
        "how": [
            "Build route `/verify` with search bar accepting an approval number (`APH-2026-XXXXX-X`).",
            "Support direct route `/verify/{approval_no}` that queries `GET /api/verify/{approval_no}`.",
            "Display clean verification certificate with green shield badge, document title, applicant name, approver audit timeline, and SHA-256 fingerprint.",
            "Show clear red warning banner if approval number is invalid or hash check fails."
        ],
        "done_when": "Entering a valid approval number renders a verified certificate badge; invalid input shows an untampered warning.",
        "learn_first": "Public Flask routes, clean certificate UI design with CSS.",
        "needs": "Step 25C (Verification API)",
        "unlocks": "Step 31 (Full Integration)",
        "parallel_fallback": "If Step 25C backend API is in progress, style the verification page using sample mock JSON responses.",
    },
    46: {
        "title": "Step 20B: Real-time notification system (backend API & mobile alerts)",
        "step": "20B",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Eliminates approval delays by immediately notifying approvers when a file reaches their turn, and notifying applicants when actions are taken.",
        "what": "Implement notification database table, backend notification endpoints, and in-app alert badges.",
        "how": [
            "Add `Notification` model: `id`, `user_id`, `title`, `message`, `is_read`, `created_at`.",
            "Trigger notifications when: document reaches approver, approver signs, or compliance is requested.",
            "Build `GET /api/notifications` and `POST /api/notifications/{id}/read`.",
            "Add notification bell icon with unread count badge in Flutter app bar and web navbar."
        ],
        "done_when": "Approvers see immediate in-app notifications when a document is assigned to them; clicking marks it read.",
        "learn_first": "Notification polling in Flutter, badge counter widgets.",
        "needs": "Step 20 (Approval Timeline)",
        "unlocks": "Step 31 (Full Integration)",
        "parallel_fallback": "If backend notification model is being finalized, design the notification UI drawer and badge widgets in Flutter.",
    },
    47: {
        "title": "Step 29B: In-app QR camera scanner & instant mobile verification",
        "step": "29B",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shreya Sutar",
        "assignees": [USERS["Shreya Sutar"]],
        "importance": "Medium",
        "effort": "5 pts (~5 hours)",
        "why": "Allows mobile users or examiners to point their smartphone camera at any printed document and verify authenticity in real time.",
        "what": "Integrate camera QR scanning in Flutter and display mobile verification results.",
        "how": [
            "Add `mobile_scanner` or `qr_code_scanner` dependency to `pubspec.yaml` with camera permissions.",
            "Build camera viewfinder screen with target overlay bounding box.",
            "Parse scanned URL, extract approval number, and call `GET /api/verify/{approval_no}`.",
            "Show modal bottom sheet or verification screen with digital approval stamps and validity badge."
        ],
        "done_when": "Scanning a document QR code with the phone camera opens the verification details screen in the app.",
        "learn_first": "Flutter mobile_scanner package, Android camera permissions in AndroidManifest.xml.",
        "needs": "Step 25C (QR Code Stamping), Step 23 (App Screens)",
        "unlocks": "Step 31 (Full Integration)",
        "parallel_fallback": "If device camera is unavailable during emulator testing, provide a manual approval number input fallback field on the scanner screen.",
    },
    48: {
        "title": "Step 30B: Administrative approval audit log & search engine",
        "step": "30B",
        "phase": "Phase 3 - Document processing",
        "week": "Week 6",
        "deadline": "December 14, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Provides complete transparency and regulatory compliance for administrators to inspect the full immutable history of any document.",
        "what": "Create administrative audit log endpoints and search filters by approval number.",
        "how": [
            "Build `GET /api/admin/audit-logs` supporting filters by date, action type (approved, rejected, compliance), and user.",
            "Support instant search by exact approval number (`APH-YYYY-XXXXX-X`) returning full timeline history.",
            "Integrate audit table into the Admin dashboard with pagination.",
            "Export audit summary report in CSV or JSON."
        ],
        "done_when": "Admin can query any approval number and view the complete sequence of events, approver remarks, and cryptographic hashes.",
        "learn_first": "Audit trail design patterns, advanced SQLAlchemy queries with joins.",
        "needs": "Step 30 (Admin Panel)",
        "unlocks": "Step 31 (Full Integration)",
        "parallel_fallback": "If admin frontend is still in design, write and test the audit log query functions and Postman test requests.",
    },
    49: {
        "title": "Step 32B: Automated pytest test suite & GitHub Actions CI pipeline",
        "step": "32B",
        "phase": "Phase 4 - Integration, testing and deployment",
        "week": "Week 7",
        "deadline": "December 21, 2026",
        "owner_name": "Shreya Loya",
        "assignees": [USERS["Shreya Loya"]],
        "importance": "Medium",
        "effort": "6 pts (~6 hours)",
        "why": "Protects the codebase from regressions and proves industry-grade quality assurance to college examiners.",
        "what": "Develop an automated backend test suite with pytest and configure GitHub Actions CI.",
        "how": [
            "Write unit and integration tests in `tests/`: auth routes, file upload, SHA-256 tamper detection, sequence transitions, and approval logic.",
            "Set up test client fixtures with SQLite in-memory database.",
            "Create `.github/workflows/ci.yml` running pytest on every push and pull request to `main`.",
            "Add build status badge to `README.md`."
        ],
        "done_when": "GitHub Actions executes automated tests on every PR and displays a passing green checkmark.",
        "learn_first": "pytest fixtures, Flask test client, GitHub Actions workflow YAML.",
        "needs": "Step 32 (Testing & Bug List)",
        "unlocks": "Step 34 (Online Deployment)",
        "parallel_fallback": "Write local pytest scripts for existing models and auth routes while waiting for newer endpoints to be merged.",
    }
}

# 3. Update Step 36 (Issue #40) for Final Report (Report 2)
REPORT_2_DATA = {
    "title": "Project Report 2: Final Comprehensive Project Report & College Submission",
    "step": "36",
    "phase": "Phase 5 - Documentation and submission",
    "week": "Week 8",
    "deadline": "December 28, 2026",
    "owner_name": "Shreya Loya & Shreeyash Solunke",
    "assignees": [USERS["Shreya Loya"], USERS["Shreeyash"]],
    "importance": "High",
    "effort": "8 pts (~8 hours)",
    "why": "The final report is the primary academic document evaluated by external examiners and college authorities for the semester grade.",
    "what": "Assemble and publish the final comprehensive project report covering all 8 university-mandated headings.",
    "how": [
        "1. Complete the 8 college headings: Title, Objectives, Literature Survey, Work Methodology, Features/System Design, Cost & Effort Estimation, Conclusion & Future Scope, References.",
        "2. Collect detailed module writeups and screenshots from each member (Shreeyash: Core & Stamping, Shravani: Web & Auth, Shreya Sutar: Mobile & Biometrics, Shreya Loya: QA & Admin).",
        "3. Include high-resolution diagrams: System Architecture, Database ER Diagram, Document State Machine, and Swimlane Flow.",
        "4. Document the complete test suite results (40+ test cases and pytest results).",
        "5. Conduct final review with the project guide and obtain physical/digital signoff."
    ],
    "done_when": "Complete report is compiled into PDF, printed/bound as required, and approved with guide signature by Dec 28, 2026.",
    "learn_first": "Academic documentation, IEEE citation standards.",
    "needs": "Step 34 (Deployment)",
    "unlocks": "Step 37, Step 38 (Final Review & Submission)",
    "parallel_fallback": "Write literature survey and methodology sections early during development so only screenshots and test results are needed in Week 8.",
}

def format_enriched_body(info):
    assignee_handles = ", ".join([f"@{a}" for a in info["assignees"]])
    lines = [
        "### 📋 Core Project Task Overview",
        f"- **Task Step:** {info['step']}",
        f"- **Phase:** {info['phase']}",
        f"- **Timeline:** {info['week']} (🎯 **Target Deadline: {info['deadline']}**)",
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
        "",
        "### 🔄 Parallel Work & Non-Blocking Fallback",
        f"> **If blocked by dependencies:** {info['parallel_fallback']}",
        "",
        "---",
        "### 📋 Definition of Done Checklist",
        "- [ ] Work on your dedicated branch (no direct commits to main)",
        "- [ ] Implement according to blueprint specifications",
        "- [ ] Verify with Postman / unit tests / UI preview",
        "- [ ] Submit Pull Request for review by Shreeyash before deadline",
    ])
    return "\n".join(lines)

def update_extra_and_report_issues():
    print("\nUpdating E1-E8 tasks into core project tasks...")
    # Remove Extra label from repository if it exists
    subprocess.run(["gh", "label", "delete", "Extra", "--repo", REPO, "--yes"], capture_output=True)

    for issue_num, data in UPDATED_EXTRA_ISSUES.items():
        body = format_enriched_body(data)
        cmd = [
            "gh", "issue", "edit", str(issue_num),
            "--repo", REPO,
            "--title", data["title"],
            "--body", body,
            "--milestone", data["week"],
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [OK] #{issue_num} -> {data['title']}")
        else:
            print(f"  [ERR] #{issue_num}: {res.stderr.strip()}")
        time.sleep(0.3)

    # Update Step 36 (Report 2)
    print("\nUpdating Issue #40 for Project Report 2...")
    body_r2 = format_enriched_body(REPORT_2_DATA)
    cmd = [
        "gh", "issue", "edit", "40",
        "--repo", REPO,
        "--title", REPORT_2_DATA["title"],
        "--body", body_r2,
        "--milestone", "Week 8",
    ]
    for a in REPORT_2_DATA["assignees"]:
        cmd.extend(["--add-assignee", a])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("  [OK] #40 -> Project Report 2")
    else:
        print(f"  [ERR] #40: {res.stderr.strip()}")

def create_report_1_issue():
    print("\nChecking / Creating Project Report 1 (Mid-Term Submission)...")
    # Check if already created
    chk = subprocess.run(["gh", "issue", "list", "--repo", REPO, "--search", "Mid-Term Project Report", "--json", "number"], capture_output=True, text=True)
    if chk.returncode == 0 and len(json.loads(chk.stdout or "[]")) > 0:
        print("  [INFO] Report 1 issue already exists.")
        return

    r1_data = {
        "step": "Mid-Term Report",
        "title": "Project Report 1: Mid-Term Project Report & System Architecture Submission",
        "phase": "Phase 2 - Core approval workflow",
        "week": "Week 4",
        "deadline": "November 30, 2026",
        "owner_name": "Shreya Loya & Shreeyash Solunke",
        "assignees": [USERS["Shreya Loya"], USERS["Shreeyash"]],
        "importance": "High",
        "effort": "6 pts (~6 hours)",
        "why": "Academic mid-term evaluation requires submission of preliminary project progress, architectural design, database schemas, and initial workflow demonstrations.",
        "what": "Prepare and submit the first official project report covering project inception through the core approval workflow.",
        "how": [
            "1. Consolidate Section 1-5 documentation: Problem Definition, Literature Survey, System Architecture, and Module Specifications.",
            "2. Include complete Database ER diagram and table schemas (Users, Documents, ApprovalSteps, Timeline).",
            "3. Document all REST API contracts and Postman test evidence from Phase 0 and Phase 1.",
            "4. Include UI wireframes (Figma) and working screenshots of Web/Mobile registration and document upload.",
            "5. Summarize workload split and milestones achieved by all 4 team members.",
            "6. Present draft to project guide for mid-term review and signoff."
        ],
        "done_when": "Mid-term report PDF submitted to guide and approved with feedback by November 30, 2026.",
        "learn_first": "Technical report compilation, LaTeX/Word formatting.",
        "needs": "Step 4 (DB Design), Step 5 (API list), Step 8 (Models), Step 9 (Auth)",
        "unlocks": "Phase 3 (Document Processing)",
        "parallel_fallback": "Teammates who finish their Week 4 coding tasks early contribute their respective module writeups and screenshots directly.",
    }
    body = format_enriched_body(r1_data)
    cmd = [
        "gh", "issue", "create",
        "--repo", REPO,
        "--title", r1_data["title"],
        "--body", body,
        "--milestone", "Week 4",
        "--label", "High",
        "--label", "P2-Core-Workflow"
    ]
    for a in r1_data["assignees"]:
        cmd.extend(["--assignee", a])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"  [OK] Created Report 1 Issue: {res.stdout.strip()}")
    else:
        print(f"  [ERR] Failed to create Report 1 issue: {res.stderr.strip()}")

def main():
    update_milestones()
    update_extra_and_report_issues()
    create_report_1_issue()
    print("\nAll updates completed successfully!")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
