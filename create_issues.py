"""
ApproveHub - auto-create GitHub labels, milestones and issues.

Setup (one time):
  1. Install GitHub CLI: https://cli.github.com   then run:  gh auth login
  2. Edit REPO and USERS below.
  3. Test first:   python create_approvehub_issues.py --dry-run
  4. Create all:   python create_approvehub_issues.py
"""
import subprocess
import sys

# ---------- EDIT THESE ----------
REPO = "ShreeyashSolunke08/ApproveHub"      # example: shreeyash/approvehub
USERS = {                              # GitHub usernames (leave "" to skip assigning)
    "Shreeyash": "",
    "Shravani": "",
    "Shreya Sutar": "",
    "Shreya Loya": "",
}
# --------------------------------

DRY = "--dry-run" in sys.argv

PHASE = {1: "P0-Setup", 2: "P1-Foundation", 3: "P1-Foundation",
         4: "P2-Core-Workflow", 5: "P2-Core-Workflow", 6: "P3-Processing",
         7: "P4-Integration", 8: "P5-Submission"}

S, SH, SU, SL = "Shreeyash", "Shravani", "Shreya Sutar", "Shreya Loya"

# (step, title, owner, week, importance, points)
TASKS = [
    # Shreeyash
    ("2", "Create the project and shared GitHub repository", S, 1, "High", 3),
    ("4", "Design the database tables", S, 1, "Critical", 5),
    ("8", "Create the database in code (models)", S, 2, "Critical", 5),
    ("12", "SHA-256 fingerprint at upload", S, 3, "Critical", 5),
    ("17", "Multi-approver sequence logic", S, 4, "Critical", 8),
    ("18", "Approve, pending and compliance actions", S, 4, "Critical", 7),
    ("21", "Hash verification before each action", S, 5, "Critical", 4),
    ("25", "Stamp signatures, stamps, seals and approval number", S, 6, "Critical", 9),
    ("31", "Integrate web and app with the real API", S, 7, "Critical", 5),
    # Shravani
    ("7", "Prepare dummy data and sample files", SH, 1, "Medium", 3),
    ("9", "Registration and login with password hashing", SH, 2, "High", 6),
    ("10", "Role-based access", SH, 2, "High", 4),
    ("13", "Base layout, login and registration pages (web)", SH, 2, "Medium", 5),
    ("11", "Document upload with validation", SH, 3, "High", 5),
    ("22", "Applicant and approver dashboards (web)", SH, 4, "High", 9),
    ("24", "Search and filter API", SH, 5, "Medium", 4),
    ("28", "Status page, search and filter UI, download page (web)", SH, 6, "Medium", 7),
    ("34", "Deploy online", SH, 7, "High", 5),
    # Shreya Sutar
    ("6", "Create UI designs for all screens", SU, 1, "Medium", 8),
    ("14", "Flutter project and login screen", SU, 2, "Medium", 6),
    ("23", "Applicant and approver screens (app)", SU, 4, "High", 9),
    ("20", "Live approval timeline", SU, 5, "High", 4),
    ("26", "Final document and final hash", SU, 6, "High", 4),
    ("27", "PIN lock logic", SU, 6, "High", 4),
    ("29", "Timeline, profile, PIN and biometric lock (app)", SU, 6, "Medium", 8),
    ("35", "README and API documentation", SU, 8, "Medium", 4),
    # Shreya Loya
    ("5", "Write the API list", SL, 1, "Medium", 4),
    ("15", "Approver profile API (signature, stamp, seal)", SL, 3, "High", 5),
    ("16", "Approver selection and approval chain", SL, 4, "High", 6),
    ("19", "Compliance flow (take back or fulfil)", SL, 5, "High", 6),
    ("30", "Admin panel and download center API", SL, 6, "High", 7),
    ("32", "Full testing and bug list (40+ test cases)", SL, 7, "High", 8),
    ("36", "Final report, literature survey and references", SL, 8, "Medium", 8),
    ("37", "Presentation and demo script", SL, 8, "Medium", 5),
    # Extra work (not in the blueprint)
    ("E1", "EXTRA: Coordinate-based stamping at user-chosen positions", S, 6, "High", 5),
    ("E2", "EXTRA: QR code on final PDF + GET /api/verify/{approval_no}", S, 6, "High", 6),
    ("E3", "EXTRA: Drag-and-drop signature block placement on A4 preview (web)", SH, 6, "High", 8),
    ("E4", "EXTRA: Public 'Verify document' web page", SH, 6, "Medium", 4),
    ("E5", "EXTRA: Notifications (API + app)", SU, 6, "Medium", 6),
    ("E6", "EXTRA: QR scanner screen in the app", SU, 7, "Medium", 5),
    ("E7", "EXTRA: Admin search by approval number + audit log", SL, 6, "High", 6),
    ("E8", "EXTRA: Automated pytest tests + GitHub Actions CI", SL, 7, "Medium", 6),
]

# Shared steps: one issue each, assigned to everyone
SHARED = [
    ("1", "Install your tools (everyone)", 1),
    ("3", "Learn your week 1 basics (everyone)", 1),
    ("33", "Fix bugs in your module and run security check (everyone)", 7),
    ("38", "Final review and submission (everyone)", 8),
]


def gh(*args):
    cmd = ["gh", *args]
    if DRY:
        print("DRY:", " ".join(f'"{a}"' if " " in a else a for a in cmd))
        return 0
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 and "already_exists" not in r.stderr and "already exists" not in r.stderr:
        print("  !", r.stderr.strip()[:200])
    return r.returncode


def main():
    if "YOUR-USERNAME" in REPO and not DRY:
        sys.exit("Edit REPO at the top of the script first.")

    # Labels
    labels = {n: "1d76db" for n in USERS}
    labels.update({"Critical": "b60205", "High": "d93f0b", "Medium": "fbca04", "Extra": "5319e7"})
    labels.update({p: "0e8a16" for p in set(PHASE.values())})
    for name, color in labels.items():
        gh("label", "create", name, "--color", color, "--force", "--repo", REPO)

    # Milestones Week 1..8
    for w in range(1, 9):
        gh("api", f"repos/{REPO}/milestones", "-f", f"title=Week {w}")

    # Individual tasks
    for step, title, owner, week, imp, pts in TASKS:
        is_extra = step.startswith("E")
        label_list = [owner, imp, PHASE[week]] + (["Extra"] if is_extra else [])
        body = (f"**Owner:** {owner}\n**Week:** {week}\n**Importance:** {imp}\n"
                f"**Effort:** {pts} points (about {pts} hours)\n\n"
                + ("Extra task added beyond the blueprint.\n" if is_extra
                   else f"See Step {step} in the ApproveHub Flow Blueprint for 'How' and 'Done when'.\n")
                + "\n- [ ] Work on your own branch\n- [ ] Test with Postman / sample data\n"
                  "- [ ] Open a Pull Request, Shreeyash reviews and merges")
        args = ["issue", "create", "--repo", REPO,
                "--title", f"Step {step}: {title}" if not is_extra else f"{step} - {title}",
                "--body", body, "--milestone", f"Week {week}"]
        for lb in label_list:
            args += ["--label", lb]
        if USERS.get(owner):
            args += ["--assignee", USERS[owner]]
        gh(*args)

    # Shared tasks
    for step, title, week in SHARED:
        body = (f"**Owner:** Everyone (each person for their own module)\n**Week:** {week}\n\n"
                f"See Step {step} in the blueprint.")
        args = ["issue", "create", "--repo", REPO, "--title", f"Step {step}: {title}",
                "--body", body, "--milestone", f"Week {week}",
                "--label", "Medium", "--label", PHASE[week]]
        for u in USERS.values():
            if u:
                args += ["--assignee", u]
        gh(*args)

    print("\nDone. Total issues:", len(TASKS) + len(SHARED))


if __name__ == "__main__":
    main()