import subprocess
import json
import re
import time
import sys

PROJECT_ID = "PVT_kwHOESXkEM4BpWUo"
START_DATE_FIELD_ID = "PVTF_lAHOESXkEM4BpWUozhnyYS4"
TARGET_DATE_FIELD_ID = "PVTF_lAHOESXkEM4BpWUozhnyYTE"
ITERATION_FIELD_ID = "PVTIF_lAHOESXkEM4BpWUozhnyYSw"

ITERATIONS = {
    1: "94958def",  # Iteration 1 (Oct 29 - Nov 12)
    2: "f0bd0057",  # Iteration 2 (Nov 12 - Nov 26)
    3: "b2245528",  # Iteration 3 (Nov 26 - Dec 10)
}

def get_step_dates(step_num):
    if 1 <= step_num <= 7:
        return "2026-11-03", "2026-11-09", ITERATIONS[1]
    elif 8 <= step_num <= 12:
        return "2026-11-10", "2026-11-16", ITERATIONS[1]
    elif 13 <= step_num <= 15:
        return "2026-11-17", "2026-11-23", ITERATIONS[2]
    elif 16 <= step_num <= 21:
        return "2026-11-24", "2026-11-30", ITERATIONS[2]
    elif 22 <= step_num <= 25:
        return "2026-12-01", "2026-12-07", ITERATIONS[3]
    elif 26 <= step_num <= 37:
        return "2026-12-08", "2026-12-14", ITERATIONS[3]
    elif 38 <= step_num <= 43:
        return "2026-12-15", "2026-12-21", ITERATIONS[3]
    elif 44 <= step_num <= 47:
        return "2026-12-22", "2026-12-30", ITERATIONS[3]
    else:
        return "2026-11-03", "2026-12-30", ITERATIONS[1]

def main():
    print("Fetching all items from ApproveHub project 3...")
    res = subprocess.run(
        ["gh", "project", "item-list", "3", "--owner", "ShreeyashSolunke08", "--format", "json", "--limit", "100"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if res.returncode != 0:
        print(f"Error fetching items: {res.stderr}")
        return

    data = json.loads(res.stdout)
    items = data.get("items", [])
    print(f"Found {len(items)} items in project. Updating dates for each item...")

    success = 0
    fail = 0

    for item in items:
        item_id = item["id"]
        title = item.get("title", "")
        
        # Match "Step X:"
        m = re.search(r"Step\s+(\d+)", title, re.IGNORECASE)
        if not m:
            print(f"Skipping non-step item: {title}")
            continue

        step_num = int(m.group(1))
        start_date, target_date, iter_id = get_step_dates(step_num)

        print(f"Updating Step {step_num:02d} ({start_date} to {target_date})...", end=" ")
        sys.stdout.flush()

        # Set Start date
        cmd1 = [
            "gh", "project", "item-edit",
            "--id", item_id,
            "--field-id", START_DATE_FIELD_ID,
            "--project-id", PROJECT_ID,
            "--date", start_date
        ]
        r1 = subprocess.run(cmd1, capture_output=True, text=True)

        # Set Target date
        cmd2 = [
            "gh", "project", "item-edit",
            "--id", item_id,
            "--field-id", TARGET_DATE_FIELD_ID,
            "--project-id", PROJECT_ID,
            "--date", target_date
        ]
        r2 = subprocess.run(cmd2, capture_output=True, text=True)

        # Set Iteration
        cmd3 = [
            "gh", "project", "item-edit",
            "--id", item_id,
            "--field-id", ITERATION_FIELD_ID,
            "--project-id", PROJECT_ID,
            "--iteration-id", iter_id
        ]
        r3 = subprocess.run(cmd3, capture_output=True, text=True)

        if r1.returncode == 0 and r2.returncode == 0:
            print("[OK]")
            success += 1
        else:
            print(f"[FAIL]: {r1.stderr or r2.stderr}")
            fail += 1

        time.sleep(0.2)

    print(f"\nCompleted! Successfully updated: {success}, Failed: {fail}")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
