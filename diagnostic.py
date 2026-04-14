"""
diagnostic.py — Full app diagnostic for RDT Inc. Fleet Management System.

Tests every page load and every interactive feature end-to-end.
Prints PASS/FAIL for each check with a final summary.

Usage:
    python3 diagnostic.py

Requirements:
    - Frontend dev server running at http://localhost:5173
    - Backend running at http://localhost:8000
"""

import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE = "http://localhost:5173"
TODAY = date.today().isoformat()
FUTURE = (date.today() + timedelta(days=365)).isoformat()
DOC_NUMBER = f"DL-{int(time.time()) % 100000}"  # unique per run
PASS = "✅ PASS"
FAIL = "❌ FAIL"

results = []


def check(label, passed, detail=""):
    status = PASS if passed else FAIL
    msg = f"{status}  {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    results.append(passed)


def login(page, username, password):
    page.goto(BASE)
    page.wait_for_selector("input[placeholder='username']", timeout=8000)
    page.fill("input[placeholder='username']", username)
    page.fill("input[type='password']", password)
    page.click("button[type='submit']")
    page.wait_for_url(lambda url: "/login" not in url, timeout=8000)


def logout(page):
    try:
        page.click("text=Sign out", timeout=5000)
        page.wait_for_url(f"{BASE}/login", timeout=5000)
    except PlaywrightTimeout:
        page.evaluate("localStorage.clear(); sessionStorage.clear();")
        page.goto(f"{BASE}/login")


def run_diagnostic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})

        print("\n" + "=" * 60)
        print("  RDT Inc. Fleet App — Full Diagnostic")
        print("=" * 60 + "\n")

        # ── LOGIN ──────────────────────────────────────────────────
        print("[ LOGIN ]")
        try:
            page.goto(BASE)
            page.wait_for_url(lambda url: url.endswith("/login"), timeout=8000)
            check("/ redirects to /login", True)
        except PlaywrightTimeout as e:
            check("/ redirects to /login", False, str(e))

        try:
            login(page, "manager", "FleetManager2024!")
            check("Manager login succeeds", "/dashboard" in page.url)
        except Exception as e:
            check("Manager login succeeds", False, str(e))
            browser.close()
            return

        # ── MANAGER PAGES — LOAD CHECKS ───────────────────────────
        print("\n[ MANAGER PAGES ]")
        pages_to_check = [
            ("/dashboard",  "text=Total Trucks",           8000),
            ("/trucks",     "text=Fleet",                  8000),
            ("/trucks/1",   "text=T-01",                   8000),
            ("/incidents",  ".rounded-xl",                 8000),
            ("/approvals",  ".rounded-xl",                 8000),
            ("/operations", ".rounded-xl",                 8000),
            ("/scheduling", ".rounded-xl",                 8000),
            ("/hr",         ".rounded-xl",                 8000),
            ("/financials", ".rounded-xl",                 8000),
            ("/drivers",    ".rounded-xl",                 8000),
            ("/ai",         "input",                      12000),
            ("/settings",   "text=Morning Ops Briefing",   8000),
        ]
        for path, selector, timeout in pages_to_check:
            try:
                page.goto(f"{BASE}{path}")
                page.wait_for_selector(selector, timeout=timeout)
                check(path, True, "loaded")
            except PlaywrightTimeout:
                check(path, False, "timeout waiting for content")
            except Exception as e:
                check(path, False, str(e))

        # ── TRUCKS — ADD ───────────────────────────────────────────
        print("\n[ TRUCKS — CRUD ]")
        test_truck = "T-DIAG"
        try:
            page.goto(f"{BASE}/trucks")
            page.wait_for_selector("text=+ Add Truck", timeout=8000)
            page.click("text=+ Add Truck")
            page.wait_for_selector("text=Add New Truck", timeout=5000)
            page.get_by_placeholder("e.g. T-01").fill(test_truck)
            page.get_by_placeholder("e.g. Mack").fill("Mack")
            page.get_by_placeholder("e.g. LR Series").fill("LR")
            # Year and Current Mileage are the two number inputs in the modal
            number_inputs = page.locator(".max-w-md input[type='number']")
            number_inputs.first.fill("2022")
            number_inputs.nth(1).fill("75000")
            page.click("button[type='submit']")
            page.wait_for_selector(f"text={test_truck}", timeout=8000)
            check("/trucks — add truck", True)
        except Exception as e:
            check("/trucks — add truck", False, str(e))

        # ── TRUCKS — EDIT ──────────────────────────────────────────
        try:
            page.goto(f"{BASE}/trucks")
            page.wait_for_selector(f"text={test_truck}", timeout=8000)
            page.locator(f"tr:has-text('{test_truck}')").locator("text=Edit").click()
            page.wait_for_selector(f"text=Edit {test_truck}", timeout=5000)
            # Update mileage
            page.locator(".max-w-md input[type='number']").nth(1).fill("76000")
            page.click("button[type='submit']")
            page.wait_for_selector(f"text={test_truck}", timeout=8000)
            check("/trucks — edit truck", True)
        except Exception as e:
            check("/trucks — edit truck", False, str(e))

        # ── TRUCKS — DELETE ────────────────────────────────────────
        try:
            page.goto(f"{BASE}/trucks")
            page.wait_for_selector(f"text={test_truck}", timeout=8000)
            page.locator(f"tr:has-text('{test_truck}')").locator("text=Delete").click()
            page.wait_for_selector(f"text=Delete {test_truck}?", timeout=5000)
            page.locator(".bg-red-500").click()
            page.wait_for_selector(f"text={test_truck}", timeout=5000, state="detached")
            check("/trucks — delete truck", True)
        except Exception as e:
            check("/trucks — delete truck", False, str(e))

        # ── TRUCK DETAIL — RECORD MAINTENANCE SERVICE ──────────────
        print("\n[ TRUCK DETAIL — MAINTENANCE ]")
        try:
            page.goto(f"{BASE}/trucks/1")
            page.wait_for_selector("text=Record Service", timeout=8000)
            page.locator("text=Record Service").first.click()
            page.wait_for_selector("input[type='date']", timeout=5000)
            page.click("button[type='submit']")
            page.wait_for_selector("input[type='date']", timeout=5000, state="detached")
            check("/trucks/1 — record maintenance service", True)
        except Exception as e:
            check("/trucks/1 — record maintenance service", False, str(e))

        # ── INCIDENTS — VIEW ───────────────────────────────────────
        print("\n[ INCIDENTS ]")
        try:
            page.goto(f"{BASE}/incidents")
            page.wait_for_selector(".rounded-xl", timeout=8000)
            check("/incidents — page loads with content", True)
        except Exception as e:
            check("/incidents — page loads with content", False, str(e))

        # ── OPERATIONS — UPDATE DRIVER STATUS ─────────────────────
        print("\n[ OPERATIONS ]")
        try:
            page.goto(f"{BASE}/operations")
            page.wait_for_selector("text=Driver Availability", timeout=8000)
            page.locator("text=Edit").first.click()
            page.wait_for_selector("select", timeout=5000)
            page.locator("select").select_option("available")
            page.locator("text=Save").click()
            page.wait_for_selector("select", timeout=5000, state="detached")
            check("/operations — update driver availability status", True)
        except Exception as e:
            check("/operations — update driver availability status", False, str(e))

        # ── APPROVALS — VIEW ───────────────────────────────────────
        print("\n[ APPROVALS ]")
        try:
            page.goto(f"{BASE}/approvals")
            page.wait_for_selector(".rounded-xl", timeout=8000)
            check("/approvals — page loads", True)
        except Exception as e:
            check("/approvals — page loads", False, str(e))

        # ── HR — ADD DOCUMENT ──────────────────────────────────────
        print("\n[ HR ]")
        try:
            page.goto(f"{BASE}/hr")
            page.wait_for_selector(".rounded-xl", timeout=8000)
            page.locator("text=+ Add").first.click()
            page.wait_for_selector("input[type='date']", timeout=5000)
            page.locator("input[type='date']").fill(FUTURE)
            page.get_by_placeholder("Optional").fill(DOC_NUMBER)
            page.locator("form button[type='submit']").click()
            page.wait_for_selector(f"text={DOC_NUMBER}", timeout=8000)
            check("/hr — add document", True)
        except Exception as e:
            check("/hr — add document", False, str(e))

        # ── HR — DELETE DOCUMENT ───────────────────────────────────
        try:
            page.once("dialog", lambda d: d.accept())
            page.locator(f"text={DOC_NUMBER}").locator("../..").locator("text=Delete").click()
            page.wait_for_selector(f"text={DOC_NUMBER}", timeout=5000, state="detached")
            check("/hr — delete document", True)
        except Exception as e:
            check("/hr — delete document", False, str(e))

        # ── HR — ADD NOTE ──────────────────────────────────────────
        try:
            page.goto(f"{BASE}/hr")
            page.wait_for_selector(".rounded-xl", timeout=8000)
            page.locator("button:has-text('notes')").click()
            page.wait_for_selector("text=+ Add Note", timeout=5000)
            page.click("text=+ Add Note")
            page.wait_for_selector("textarea", timeout=5000)
            page.fill("textarea", "Diagnostic test note — safe to delete")
            page.locator("form button[type='submit']").click()
            page.wait_for_selector("text=Diagnostic test note", timeout=8000)
            check("/hr — add note", True)
        except Exception as e:
            check("/hr — add note", False, str(e))

        # ── FINANCIALS — ADD REPAIR COST ───────────────────────────
        print("\n[ FINANCIALS ]")
        try:
            page.goto(f"{BASE}/financials")
            page.wait_for_selector("text=Repair Cost Log", timeout=10000)
            # Repair Costs tab is default — click "+ Add"
            page.locator("text=+ Add").first.click()
            page.wait_for_selector("input[placeholder='e.g. Brake replacement']", timeout=5000)
            page.fill("input[placeholder='e.g. Brake replacement']", "Diagnostic test repair")
            page.locator("input[type='date']").first.fill(TODAY)
            page.fill("input[placeholder='0.00']", "99.99")
            page.locator("form button[type='submit']").click()
            page.wait_for_selector("text=Diagnostic test repair", timeout=8000)
            check("/financials — add repair cost", True)
        except Exception as e:
            check("/financials — add repair cost", False, str(e))

        # ── FINANCIALS — ADD FUEL LOG ──────────────────────────────
        try:
            page.goto(f"{BASE}/financials")
            page.wait_for_selector("text=Repair Cost Log", timeout=10000)
            page.locator("button:has-text('Fuel Log')").click()
            page.wait_for_selector("text=+ Log Fill-Up", timeout=5000)
            page.click("text=+ Log Fill-Up")
            page.wait_for_selector("input[type='date']", timeout=5000)
            page.locator("input[type='date']").first.fill(TODAY)
            page.fill("input[placeholder='0.0']", "50.5")
            page.fill("input[placeholder='3.999']", "3.999")
            page.locator("form button[type='submit']").click()
            page.wait_for_selector("text=50.5 gal", timeout=8000)
            check("/financials — add fuel log", True)
        except Exception as e:
            check("/financials — add fuel log", False, str(e))

        # ── FINANCIALS — SCHEDULE REPAIR APPOINTMENT ───────────────
        try:
            page.goto(f"{BASE}/financials")
            page.wait_for_selector("text=Repair Cost Log", timeout=10000)
            page.locator("button:has-text('Appointments')").click()
            page.wait_for_selector("text=+ Schedule", timeout=5000)
            page.click("text=+ Schedule")
            page.wait_for_selector("input[type='date']", timeout=5000)
            page.locator("input[type='date']").first.fill(FUTURE)
            page.locator("form button[type='submit']").click()
            page.wait_for_selector(f"text={FUTURE}", timeout=8000)
            check("/financials — schedule repair appointment", True)
        except Exception as e:
            check("/financials — schedule repair appointment", False, str(e))

        # ── AI CHAT ────────────────────────────────────────────────
        print("\n[ AI CHAT ]")
        try:
            page.goto(f"{BASE}/ai")
            page.wait_for_selector("input", timeout=12000)
            page.fill("input", "How many trucks are in the fleet?")
            page.keyboard.press("Enter")
            # Wait for the loading spinner to appear then disappear
            try:
                page.wait_for_selector(".animate-spin", timeout=3000)
            except PlaywrightTimeout:
                pass  # spinner may appear/disappear quickly
            page.wait_for_selector(".animate-spin", timeout=35000, state="detached")
            # Verify a real response appeared (not an error about ANTHROPIC_API_KEY)
            content = page.content()
            is_error = "ANTHROPIC_API_KEY" in content or "couldn't reach" in content
            check("/ai — chat response received", not is_error,
                  "got error response" if is_error else "")
        except Exception as e:
            check("/ai — chat response received", False, str(e))

        # ── SETTINGS — SAVE (ENABLED ON) ──────────────────────────
        print("\n[ SETTINGS ]")
        try:
            page.goto(f"{BASE}/settings")
            page.wait_for_selector("input[type='email']", timeout=8000)
            page.locator("input[type='email']").fill("noaangilau@gmail.com")
            # Ensure toggle is ON
            toggle = page.locator("button.rounded-full").first
            classes = toggle.get_attribute("class") or ""
            if "bg-gray-200" in classes:
                toggle.click()  # flip to ON
            page.click("text=Save Settings")
            page.wait_for_selector("text=Settings saved", timeout=6000)
            check("/settings — save with daily briefing enabled", True)
        except Exception as e:
            check("/settings — save with daily briefing enabled", False, str(e))

        # ── SETTINGS — SAVE (ENABLED OFF) ─────────────────────────
        try:
            page.goto(f"{BASE}/settings")
            page.wait_for_selector("button.rounded-full", timeout=8000)
            toggle = page.locator("button.rounded-full").first
            classes = toggle.get_attribute("class") or ""
            if "bg-\\[#68ccd1\\]" in classes or "#68ccd1" in classes:
                toggle.click()  # flip to OFF
            page.click("text=Save Settings")
            page.wait_for_selector("text=Settings saved", timeout=6000)
            check("/settings — save with daily briefing disabled", True)
        except Exception as e:
            check("/settings — save with daily briefing disabled", False, str(e))

        # ── SETTINGS — SEND NOW ────────────────────────────────────
        try:
            page.goto(f"{BASE}/settings")
            page.wait_for_selector("text=Send Now", timeout=8000)
            page.click("text=Send Now")
            page.wait_for_selector("text=/Sent|Failed/", timeout=30000)
            check("/settings — Send Now", True, "briefing entry appeared")
        except PlaywrightTimeout:
            check("/settings — Send Now", False, "no briefing entry within 30s")
        except Exception as e:
            check("/settings — Send Now", False, str(e))

        # ── DRIVER FLOW — LOGIN ────────────────────────────────────
        print("\n[ DRIVER PAGES ]")
        try:
            logout(page)
            login(page, "jcooper", "Driver2024!")
            check("Driver login succeeds", "/mileage" in page.url or "/driver" in page.url)
        except Exception as e:
            check("Driver login succeeds", False, str(e))

        driver_pages = [
            ("/driver-home", ".rounded-2xl"),
            ("/mileage",     "text=Log Mileage"),
            ("/checkin",     "text=Check In"),
            ("/incident",    "text=Report Incident"),
        ]
        for path, selector in driver_pages:
            try:
                page.goto(f"{BASE}{path}")
                page.wait_for_selector(selector, timeout=8000)
                check(path, True, "loaded")
            except PlaywrightTimeout:
                check(path, False, "timeout waiting for content")
            except Exception as e:
                check(path, False, str(e))

        # ── DRIVER — SUBMIT MILEAGE ────────────────────────────────
        print("\n[ DRIVER ACTIONS ]")
        try:
            page.goto(f"{BASE}/mileage")
            page.wait_for_selector("select", timeout=8000)
            page.locator("select").select_option(index=1)  # first truck
            page.fill("input[type='number']", "999999")
            page.click("text=Submit Mileage")
            page.wait_for_selector("text=Mileage Updated", timeout=8000)
            check("/mileage — submit odometer reading", True)
        except Exception as e:
            check("/mileage — submit odometer reading", False, str(e))

        # ── DRIVER — CHECK IN ──────────────────────────────────────
        try:
            page.goto(f"{BASE}/checkin")
            page.wait_for_selector("text=On Duty", timeout=8000)
            page.locator("button:has-text('On Duty')").click()
            page.click("text=Update Status")
            page.wait_for_selector("text=Status Updated", timeout=8000)
            check("/checkin — driver check-in", True)
        except Exception as e:
            check("/checkin — driver check-in", False, str(e))

        # ── DRIVER — SUBMIT INCIDENT ───────────────────────────────
        try:
            page.goto(f"{BASE}/incident")
            page.wait_for_selector("select", timeout=8000)
            page.locator("select").select_option(index=1)  # first truck
            page.locator("input[type='date']").fill(TODAY)
            page.locator("button:has-text('medium')").click()
            page.fill("textarea", "Diagnostic test incident — minor scrape on rear bumper")
            page.click("text=Submit Report")
            page.wait_for_selector("text=Report Submitted", timeout=8000)
            check("/incident — submit incident report", True)
        except Exception as e:
            check("/incident — submit incident report", False, str(e))

        # ── SUMMARY ────────────────────────────────────────────────
        print("\n" + "=" * 60)
        passed = sum(results)
        total = len(results)
        failed = total - passed
        print(f"  TOTAL: {passed}/{total} passed", end="")
        if failed:
            print(f"  |  {failed} FAILED ← investigate above")
        else:
            print("  — all clear!")
        print("=" * 60 + "\n")

        browser.close()


if __name__ == "__main__":
    run_diagnostic()
