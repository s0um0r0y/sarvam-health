"""Estimate a day's calories and macros from the IIIT-H mess menu using Sarvam AI.
 
Breakfast comes from the Kadamba tab, lunch and dinner from the Yuktahar tab.
 
Setup:
    pip install sarvamai python-dotenv playwright
    playwright install chromium
    # .env must contain SARVAM_API_KEY=...
 
Usage:
    python meal_macros.py                     # today
    python meal_macros.py --date 2026-10-19   # a specific day
    python meal_macros.py --headed            # show the browser (use once to log in if needed)
    python meal_macros.py --menu-file menu.txt --date 2026-10-19   # skip scraping, use pasted text
"""
import argparse
import json
import os
import re
import sys
from datetime import date
 
from dotenv import load_dotenv
from sarvamai import SarvamAI
 
MENU_URL = "https://dining.iiit.ac.in/menu"
MAX_CHARS = 20000  # per tab, keeps the prompt well inside the context window
 
 
# ---------- 1. Get the menu text ----------
 
def click_first(page, pattern):
    """Click a tab/button whose label matches pattern. Returns True if something was clicked."""
    rx = re.compile(pattern, re.I)
    for locator in (page.get_by_role("tab", name=rx), page.get_by_role("button", name=rx), page.get_by_text(rx)):
        try:
            if locator.count():
                locator.first.click(timeout=3000)
                page.wait_for_timeout(1500)
                return True
        except Exception:
            continue
    return False
 
 
def grab_tab_text(page, venue_pattern, day):
    if not click_first(page, venue_pattern):
        print(f"Warning: couldn't find a tab matching '{venue_pattern}'; using the page as-is.")
    # If the page has per-day tabs, try selecting the requested weekday too (harmless if absent).
    click_first(page, rf"^\s*({day:%A}|{day:%a})\s*$")
    return page.inner_text("body")[:MAX_CHARS]
 
 
def fetch_menu_text(day, headed):
    from playwright.sync_api import sync_playwright
 
    with sync_playwright() as p:
        # A persistent profile keeps your login cookies between runs.
        ctx = p.chromium.launch_persistent_context(".browser-profile", headless=not headed)
        page = ctx.new_page()
        page.goto(MENU_URL, wait_until="networkidle")
 
        if re.search(r"login|cas|signin|auth", page.url, re.I):
            if not headed:
                ctx.close()
                sys.exit("The menu page wants a login. Run once with --headed and sign in.")
            input("Sign in in the browser window, then press Enter here...")
            page.goto(MENU_URL, wait_until="networkidle")
 
        kadamba = grab_tab_text(page, r"kadamba", day)
        yuktahar = grab_tab_text(page, r"yukta", day)  # matches Yuktahar / Yuktahaar
        ctx.close()
    return kadamba, yuktahar
 
 
# ---------- 2. Ask Sarvam for macro estimates ----------
 
ITEM = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "serving": {"type": "string"},
        "calories_kcal": {"type": "number"},
        "protein_g": {"type": "number"},
        "carbs_g": {"type": "number"},
        "fat_g": {"type": "number"},
    },
    "required": ["name", "serving", "calories_kcal", "protein_g", "carbs_g", "fat_g"],
    "additionalProperties": False,
}
SCHEMA = {
    "type": "object",
    "properties": {
        "meals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "meal": {"type": "string", "enum": ["breakfast", "lunch", "dinner"]},
                    "venue": {"type": "string"},
                    "found": {"type": "boolean"},
                    "items": {"type": "array", "items": ITEM},
                },
                "required": ["meal", "venue", "found", "items"],
                "additionalProperties": False,
            },
        },
        "notes": {"type": "string"},
    },
    "required": ["meals", "notes"],
    "additionalProperties": False,
}
 
SYSTEM = """You are a nutrition estimator for an Indian university mess.
You get raw text scraped from two menu tabs. Rules:
- Breakfast comes ONLY from the Kadamba text. Lunch and dinner come ONLY from the Yuktahar text.
- Use only the menu for the requested day of the week. Never invent dishes.
- If a meal for that day isn't in the text, set found=false and items=[].
- Assume one typical Indian mess serving per item (e.g. 1 katori dal, 2 rotis, 1 cup rice);
  state the assumed serving. Condiments, pickles and papad get small portions.
- Give realistic per-serving estimates for calories, protein, carbs and fat.
- Use notes for caveats (ambiguous dishes, items you skipped)."""
 
 
def estimate_macros(kadamba, yuktahar, day):
    client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
    user = (
        f"Requested day: {day:%A}, {day.isoformat()}\n\n"
        f"=== KADAMBA TAB TEXT ===\n{kadamba}\n\n"
        f"=== YUKTAHAR TAB TEXT ===\n{yuktahar}"
    )
    resp = client.chat.completions(
        model="sarvam-105b",
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
        response_format={"type": "json_schema", "json_schema": {"name": "day_macros", "strict": True, "schema": SCHEMA}},
        max_tokens=4096,
    )
    content = resp.choices[0].message.content
    if not content:
        sys.exit("Sarvam returned no content (the token budget may have gone to reasoning). Try again.")
    return json.loads(content)
 
 
# ---------- 3. Print the result ----------
 
def print_report(result, day):
    keys = ("calories_kcal", "protein_g", "carbs_g", "fat_g")
    day_total = dict.fromkeys(keys, 0.0)
    print(f"\nMacro estimate for {day:%A, %d %b %Y}\n")
    for meal in result["meals"]:
        print(f"== {meal['meal'].title()} ({meal['venue']}) ==")
        if not meal["found"]:
            print("  Not found in the menu text.\n")
            continue
        meal_total = dict.fromkeys(keys, 0.0)
        for it in meal["items"]:
            print(f"  {it['name']:<28} {it['serving']:<18} {it['calories_kcal']:>5.0f} kcal  "
                  f"P {it['protein_g']:>4.1f}g  C {it['carbs_g']:>5.1f}g  F {it['fat_g']:>4.1f}g")
            for k in keys:
                meal_total[k] += it[k]
        print(f"  {'Meal total':<47} {meal_total['calories_kcal']:>5.0f} kcal  P {meal_total['protein_g']:>4.1f}g  "
              f"C {meal_total['carbs_g']:>5.1f}g  F {meal_total['fat_g']:>4.1f}g\n")
        for k in keys:
            day_total[k] += meal_total[k]
    print(f"DAY TOTAL: {day_total['calories_kcal']:.0f} kcal | protein {day_total['protein_g']:.0f} g | "
          f"carbs {day_total['carbs_g']:.0f} g | fat {day_total['fat_g']:.0f} g")
    if result.get("notes"):
        print(f"\nNotes: {result['notes']}")
    print("\nThese are AI estimates assuming one serving of everything, not measured values.")
 
 
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", type=date.fromisoformat, default=date.today(), help="YYYY-MM-DD (default: today)")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    ap.add_argument("--menu-file", help="text file with the menu pasted from the site (skips scraping)")
    args = ap.parse_args()
 
    load_dotenv()
    if not os.environ.get("SARVAM_API_KEY"):
        sys.exit("SARVAM_API_KEY is not set. Add it to .env first.")
 
    if args.menu_file:
        text = open(args.menu_file, encoding="utf-8").read()[: MAX_CHARS * 2]
        kadamba, yuktahar = text, text
    else:
        kadamba, yuktahar = fetch_menu_text(args.date, args.headed)
 
    print_report(estimate_macros(kadamba, yuktahar, args.date), args.date)
 
 
if __name__ == "__main__":
    main()
