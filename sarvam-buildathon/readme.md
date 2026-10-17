# Estimate a day's calories and macros from the IIIT-H mess menu using Sarvam>
 
- Breakfast comes from the Kadamba tab, lunch and dinner from the Yuktahar tab.
 
Setup:
```
    pip install sarvamai python-dotenv playwright
    playwright install chromium
    # .env must contain SARVAM_API_KEY=...
```
``` 
Usage:
    python meal_macros.py                     # today
    python meal_macros.py --date 2026-10-19   # a specific day
    python meal_macros.py --headed            # show the browser (use once to >
    python meal_macros.py --menu-file menu.txt --date 2026-10-19   # skip scra>
```
