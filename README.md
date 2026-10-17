# Estimate a day's calories and macros from the IIIT-H mess menu using Sarvam
 
- Breakfast comes from the Kadamba tab, lunch and dinner from the Yuktahar tab from https://dining.iiit.ac.in/menu where you can get insights like proteins, carbs and fat from the meals.
 
## Setup:
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

## Output
```
Macro estimate for Monday, 19 Oct 2026

== Breakfast (Kadamba) ==
  Idli                         3 pieces             195 kcal  P  6.0g  C  42.0g  F  0.6g
  Sambar                       1 katori (150 ml)    110 kcal  P  5.0g  C  16.0g  F  3.0g
  Coconut chutney              2 tbsp                70 kcal  P  1.0g  C   3.0g  F  6.0g
  Boiled egg                   1 egg                 78 kcal  P  6.3g  C   0.6g  F  5.3g
  Bread with butter            2 slices             210 kcal  P  5.0g  C  26.0g  F  9.0g
  Tea with milk                1 cup                 90 kcal  P  2.5g  C  12.0g  F  3.0g
  Meal total                                        753 kcal  P 25.8g  C  99.6g  F 26.9g

== Lunch (Yuktahar) ==
  Steamed rice                 1 cup                205 kcal  P  4.3g  C  45.0g  F  0.4g
  Roti                         2 rotis              240 kcal  P  7.0g  C  40.0g  F  6.0g
  Dal tadka                    1 katori             180 kcal  P  9.0g  C  22.0g  F  6.0g
  Aloo gobi                    1 katori             150 kcal  P  3.5g  C  18.0g  F  7.5g
  Curd                         1 small bowl         100 kcal  P  5.0g  C   7.0g  F  5.0g
  Mango pickle                 1 tsp                 30 kcal  P  0.2g  C   1.0g  F  2.8g
  Meal total                                        905 kcal  P 29.0g  C 133.0g  F 27.7g

== Dinner (Yuktahar) ==
  Steamed rice                 1 cup                205 kcal  P  4.3g  C  45.0g  F  0.4g
  Chapati                      2 chapatis           240 kcal  P  7.0g  C  40.0g  F  6.0g
  Paneer butter masala         1 katori             290 kcal  P 11.0g  C  10.0g  F 23.0g
  Rasam                        1 katori              60 kcal  P  2.0g  C   9.0g  F  2.0g
  Gulab jamun                  1 piece              150 kcal  P  2.0g  C  23.0g  F  6.0g
  Meal total                                        945 kcal  P 26.3g  C 127.0g  F 37.4g

DAY TOTAL: 2603 kcal | protein 81 g | carbs 360 g | fat 92 g

Notes: Breakfast had 'Egg/Banana' as an option; assumed egg. Dinner listed 'Dal/Rasam'; assumed rasam. Paneer butter masala fat varies a lot with how much cream and butter the mess uses.

These are AI estimates assuming one serving of everything, not measured values.
```
