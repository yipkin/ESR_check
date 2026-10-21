#!/usr/bin/env python3
"""Save the authenticated ESR list page as HTML after manual sign-in.

Credentials are entered in the browser window, never in this script.
"""

import argparse
from pathlib import Path
from shutil import which
from getpass import getpass
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

LIST_URL = "https://esr.bnl.gov/esrlist.aspx"
ERC_LABEL = "ERC"
ESR_LABEL = "PO-089-2025-OCT-3"
OUTPUT = Path("esrlist.html")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Save an authenticated ESR page as HTML."
    )
    parser.add_argument("-user", "--user", dest="username", help="BNL ESR username")
    parser.add_argument("-pass", "--pass", dest="password", help="BNL ESR password")
    parser.add_argument(
        "-l",
        "--label",
        dest="esr_label",
        default=ESR_LABEL,
        help=f"ESR link text to open (default: {ESR_LABEL})",
    )
    parser.add_argument(
        "-v",
        "--auto-save",
        action="store_true",
        help="save immediately and close the browser without waiting for Enter",
    )
    args = parser.parse_args()

    chromium = which("chromium") or which("chromium-browser")
    if not chromium:
        raise SystemExit(
            "Chromium was not found. Install it with: sudo apt install chromium"
        )

    username = args.username or input("BNL ESR username: ")
    password = args.password or getpass("BNL ESR password (input hidden): ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=chromium)
        context = browser.new_context(
            http_credentials={"username": username, "password": password}
        )
        page = context.new_page()
        page.goto(LIST_URL, wait_until="domcontentloaded")
        page.get_by_text(ERC_LABEL, exact=True).first.click()
        page.wait_for_load_state("domcontentloaded")

        # Filter the ERC list by the status pull-down before finding the ESR.
        status_select = page.locator("select").filter(
            has=page.locator("option", has_text="Approved")
        ).first
        status_select.select_option(label="Approved")
        page.wait_for_timeout(500)

        esr = page.get_by_text(args.esr_label, exact=True).first
        try:
            # The Print ESR link may open a separate tab.
            with context.expect_page(timeout=10_000) as new_page:
                esr.click()
            result_page = new_page.value
            result_page.wait_for_load_state("domcontentloaded")
        except PlaywrightTimeoutError:
            # Otherwise it navigates the current tab.
            print("Warning: Timeout!")
            result_page = page
            result_page.wait_for_load_state("domcontentloaded")

        if not args.auto_save:
            input("Confirm the ESR page is visible, then press Enter to save its HTML. ")
        OUTPUT.write_text(result_page.content(), encoding="utf-8")
        print(f"Saved {OUTPUT.resolve()}")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
