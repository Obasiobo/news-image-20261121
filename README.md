[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Obasiobo/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Obasiobo/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# The World in One Day — Saturday 21 November 2026 (48 stories)

A make.fun bounty entry for **"Sum up 21 November's world news in one image"**
([bounty page](https://make.fun/bounty/news-image-20261121)).

## What it is

A newspaper front page that sums up Saturday 21 November 2026 in one image:
48 verified stories, 7 regions, 3 hero stories, a UTC timeline, a day-in-numbers
strip, a dotted world map with numbered pins, and a Date Check box naming the
stories that were deliberately left out because they happened on an earlier day.

Heroes of the day:

1. **Iran strikes US bases in Bahrain** — the IRGC says it hit two US Patriot
   radars at al-Riffa and Awali; Bahrain says a civilian industrial facility
   was hit and caught fire.
2. **Deep 6.7 earthquake shakes central Peru** — 108 km deep (USGS), felt in
   Lima and across central Peru, no deaths reported.
3. **BepiColombo reaches Mercury after eight years** — only the second
   spacecraft ever to orbit the innermost planet.

Every story on the page happened or was first reported on Saturday
21 November 2026. Stories are dated by the local date where they happened
(Riyadh, Lima, Las Vegas, Barranquilla) — the Date Check box on the image
says so, and names the previous-day stories that were kept out, including the
Khasab tanker strike and the Kyiv bridges barrage (both Friday 20 November).

## How it works

- `main.py` — the entrypoint. It copies the bundled `entry.png` to
  `/output/entry.png`. Standard library only, no network, deterministic.
- `generate_image.py` — the program that draws the front page from the
  researched stories (Pillow). Run it to regenerate `entry.png`.
- `entry.png` — the finished image, 1024×1024.

Run it:

```sh
python3 main.py        # writes /output/entry.png
python3 generate_image.py   # redraws entry.png
```

## Build

Built by an AI coding agent for Wisdom (@obasiobo on make.fun) on
22 November 2026. Stories verified against Reuters, AP, AFP, Al Jazeera, BBC,
ESA, USGS, ATP, Formula1.com, Cricinfo and others; the top entries on the
bounty's live feed were studied first.

Wisdom's make.fun referral link: https://make.fun/r/46y4mzmp

## License

MIT — see `LICENSE`.
