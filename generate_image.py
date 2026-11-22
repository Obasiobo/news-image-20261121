#!/usr/bin/env python3
"""The World in One Day — Saturday 21 November 2026 (48 stories).

Clean-room build: draws a 1024x1024 newspaper front page with PIL only.
No network, no randomness, no timestamps -> byte-identical repeat runs.
Output: entry.png next to this script (1024x1024, PNG, <= 1 MiB).
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

CREAM = (247, 241, 222)
PAPER2 = (241, 234, 208)
INK = (26, 26, 26)
MUTED = (90, 84, 70)
RED = (160, 30, 30)
NAVY = (31, 58, 95)
GOLD = (176, 124, 18)
TEAL = (18, 110, 105)
RULE = (26, 26, 26)
LIGHT_RULE = (150, 142, 120)
BLUE = (52, 96, 150)
BROWN = (122, 84, 52)
ORANGE = (214, 120, 40)

FD = "/usr/share/fonts/truetype"
F_SERIF = os.path.join(FD, "liberation/LiberationSerif-Bold.ttf")
F_SERIF_R = os.path.join(FD, "liberation/LiberationSerif-Regular.ttf")
F_SERIF_I = os.path.join(FD, "liberation/LiberationSerif-Italic.ttf")
F_SANS = os.path.join(FD, "liberation/LiberationSans-Regular.ttf")
F_SANS_B = os.path.join(FD, "liberation/LiberationSans-Bold.ttf")
F_SANS_I = os.path.join(FD, "liberation/LiberationSans-Italic.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def tag_chip(draw, x, y, label, color):
    """Small verification tag; returns width used."""
    f = font(F_SANS_B, 8)
    w = int(draw.textlength(label, font=f)) + 8
    draw.rounded_rectangle([x, y, x + w, y + 11], radius=2, fill=color)
    draw.text((x + 4, y + 1), label, font=f, fill=(255, 255, 255))
    return w


TAG_COLORS = {"OFFICIAL": NAVY, "REPORTED": (70, 70, 70), "CLAIM": RED, "FORECAST": GOLD}

# ---------------------------------------------------------------- continents
# Coarse lon/lat polygons for the dotted world map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-75, 62),
     (-60, 55), (-55, 47), (-65, 45), (-75, 35), (-80, 25), (-90, 20), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-75, 11), (-60, 8), (-50, 5), (-35, -5), (-40, -20), (-48, -28),
     (-58, -35), (-65, -40), (-70, -50), (-73, -53), (-70, -30), (-70, -18),
     (-77, -12), (-81, -5), (-80, 2)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (30, 60), (30, 70), (40, 68), (45, 66), (40, 60),
     (35, 55), (30, 50), (28, 45), (23, 40), (19, 42), (12, 44), (3, 43), (-2, 37), (-9, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
     (51, 11), (48, 0), (40, -10), (35, -20), (32, -29), (25, -34), (19, -35),
     (15, -27), (12, -18), (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 12)],
    [(40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (170, 67), (178, 65),
     (170, 60), (160, 55), (140, 45), (130, 42), (127, 40), (120, 32), (110, 20),
     (105, 8), (100, 6), (95, 15), (90, 22), (80, 13), (75, 8), (70, 20), (60, 25),
     (55, 26), (48, 29), (43, 12), (40, 15), (35, 28), (30, 36), (36, 36), (30, 42),
     (40, 45), (45, 50), (50, 55), (45, 60)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
     (136, -12), (132, -12), (126, -14), (122, -17), (114, -22)],
    [(95, 5), (105, 0), (115, -5), (125, -8), (135, -8), (140, -8), (130, -2),
     (120, 0), (110, 5)],
]


def inside_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(inside_poly(lon, lat, p) for p in CONTINENTS)


# ---------------------------------------------------------------- hero art
def hero_art_gulf(draw, x, y, w, h):
    """Flat Gulf map: sea, Arabian peninsula, Bahrain pin, missile trails."""
    draw.rectangle([x, y, x + w, y + h], fill=(198, 222, 235))
    # Arabian peninsula (sand) — simplified polygon in panel coords
    pen = [(x + 60, y + 8), (x + 150, y + 6), (x + 205, y + 22), (x + 235, y + 55),
           (x + 250, y + h - 6), (x + 200, y + h - 4), (x + 150, y + h - 12),
           (x + 95, y + h - 8), (x + 55, y + h - 30), (x + 45, y + 40)]
    draw.polygon(pen, fill=(232, 205, 150), outline=(160, 130, 85))
    # Iran landmass top-right
    draw.polygon([(x + 205, y + 4), (x + w - 4, y + 4), (x + w - 4, y + 52),
                  (x + 245, y + 58), (x + 228, y + 30)], fill=(214, 190, 140),
                 outline=(160, 130, 85))
    # Gulf water channel
    draw.polygon([(x + 150, y + 6), (x + 205, y + 22), (x + 235, y + 55),
                  (x + 210, y + 62), (x + 185, y + 30), (x + 158, y + 12)],
                 fill=(150, 195, 220))
    # Bahrain island + pin (left of peninsula, in the Gulf)
    bx, by = x + 132, y + 34
    draw.ellipse([bx - 7, by - 5, bx + 7, by + 5], fill=(250, 240, 210),
                 outline=(120, 100, 60))
    draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=RED)
    draw.text((bx + 9, by - 4), "BAHRAIN", font=font(F_SANS_B, 9), fill=RED)
    # two US bases
    for px, py, lab in [(x + 118, y + 52, "al-Riffa"), (x + 128, y + 66, "Awali")]:
        draw.rectangle([px - 3, py - 3, px + 3, py + 3], fill=NAVY)
        draw.text((px + 6, py - 4), lab, font=font(F_SANS, 8), fill=NAVY)
    # missile trails (dashed) from Iran toward Bahrain
    for (x1, y1, x2, y2) in [(x + 252, y + 18, bx + 2, by - 2),
                             (x + 258, y + 34, bx + 4, by + 4)]:
        steps = 9
        for i in range(steps):
            if i % 2 == 0:
                sx = x1 + (x2 - x1) * i / steps
                sy = y1 + (y2 - y1) * i / steps
                ex = x1 + (x2 - x1) * (i + 1) / steps
                ey = y1 + (y2 - y1) * (i + 1) / steps
                draw.line([sx, sy, ex, ey], fill=RED, width=2)
    # burning plant flame
    fx, fy = x + 150, y + h - 22
    draw.polygon([(fx, fy - 14), (fx - 6, fy), (fx - 2, fy), (fx, fy + 4),
                  (fx + 3, fy), (fx + 7, fy), (fx + 2, fy - 8)], fill=ORANGE)
    draw.text((fx + 10, fy - 6), "plant fire", font=font(F_SANS, 8), fill=(120, 60, 10))
    draw.text((x + 6, y + h - 12), "PERSIAN GULF", font=font(F_SANS_B, 8), fill=(40, 80, 110))
    draw.text((x + w - 34, y + 6), "IRAN", font=font(F_SANS_B, 8), fill=(90, 70, 40))


def hero_art_quake(draw, x, y, w, h):
    """Andes cross-section: surface, strata, 108 km depth line, epicentre."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 226, 200))
    surf = y + 20
    draw.rectangle([x, y, x + w, surf], fill=(214, 232, 240))
    draw.text((x + 8, y + 5), "LIMA  •  felt across central Peru", font=font(F_SANS_B, 9),
              fill=(40, 70, 100))
    # mountain silhouette
    draw.polygon([(x, surf), (x + 55, surf - 12), (x + 110, surf), (x + 165, surf - 14),
                  (x + 225, surf), (x + w, surf - 7), (x + w, surf), (x, surf)],
                 fill=(150, 120, 80))
    # strata (4 bands of 11px, ending surf+52, inside the panel)
    for i, col in enumerate([(200, 175, 130), (175, 140, 95), (150, 110, 70), (120, 85, 55)]):
        y0 = surf + 8 + i * 11
        draw.rectangle([x, y0, x + w, y0 + 11], fill=col)
    # depth line from epicentre to surface
    ex, ey = x + 150, surf + 34
    draw.line([ex, surf, ex, ey], fill=RED, width=2)
    draw.line([ex - 12, surf, ex + 12, surf], fill=RED, width=2)
    for r in (3, 7, 11):
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], outline=RED, width=2)
    draw.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=RED)
    draw.text((ex + 15, ey - 5), "M6.7", font=font(F_SANS_B, 10), fill=RED)
    # depth labels on a small cream patch (readable over the strata)
    draw.rectangle([x + 6, surf + 22, x + 132, surf + 48], fill=(250, 244, 225))
    draw.text((x + 9, surf + 24), "108 km deep (USGS)", font=font(F_SANS_B, 9), fill=INK)
    draw.text((x + 9, surf + 36), "IGP says 129 km", font=font(F_SANS, 8), fill=MUTED)
    # shaking waves at surface
    for cx in (x + 40, x + 250):
        for r in (3, 6):
            draw.arc([cx - r, surf - r - 4, cx + r, surf + r - 4], 200, 340,
                     fill=(40, 70, 100), width=1)


def hero_art_space(draw, x, y, w, h):
    """Spacecraft + Mercury, 8-year journey arc, 37-minute burn."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 24, 46))
    # stars
    for sx, sy in [(14, 10), (60, 22), (120, 8), (180, 16), (230, 10), (270, 26),
                   (40, 52), (200, 44), (90, 60), (255, 58)]:
        draw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # Mercury
    mx, my, mr = x + w - 62, y + h - 34, 26
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(206, 164, 110))
    for cx, cy, cr in [(mx - 10, my - 8, 5), (mx + 8, my + 4, 4), (mx - 2, my + 12, 3),
                       (mx + 12, my - 12, 3)]:
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(170, 128, 80))
    draw.text((mx - 22, my - mr - 11), "MERCURY", font=font(F_SANS_B, 8), fill=(230, 200, 160))
    # journey arc (dashed)
    for i in range(14):
        if i % 2 == 0:
            t0, t1 = i / 14, (i + 1) / 14
            ax0 = x + 20 + (mx - 40 - x - 20) * t0
            ay0 = y + h - 18 - 46 * (1 - (t0 - 0.5) ** 2 * 4) * 0.4 - 30 * t0
            ax1 = x + 20 + (mx - 40 - x - 20) * t1
            ay1 = y + h - 18 - 46 * (1 - (t1 - 0.5) ** 2 * 4) * 0.4 - 30 * t1
            draw.line([ax0, ay0, ax1, ay1], fill=(140, 170, 220), width=1)
    draw.text((x + 8, y + h - 16), "8-year journey • launched Oct 2018",
              font=font(F_SANS, 8), fill=(180, 200, 230))
    # spacecraft: body + panels + burn flame
    sx, sy = x + 96, y + 30
    draw.rectangle([sx - 26, sy - 4, sx - 4, sy + 4], fill=(90, 120, 180),
                   outline=(200, 220, 255))
    draw.rectangle([sx + 4, sy - 4, sx + 26, sy + 4], fill=(90, 120, 180),
                   outline=(200, 220, 255))
    draw.rectangle([sx - 4, sy - 8, sx + 4, sy + 8], fill=(220, 225, 235),
                   outline=(150, 160, 180))
    draw.polygon([(sx - 4, sy + 8), (sx + 4, sy + 8), (sx, sy + 22)], fill=ORANGE)
    draw.polygon([(sx - 2, sy + 8), (sx + 2, sy + 8), (sx, sy + 16)], fill=(255, 220, 120))
    draw.text((sx + 34, sy - 5), "37-min burn • 18:24 UTC",
              font=font(F_SANS_B, 9), fill=(255, 220, 120))
    draw.text((x + 8, y + 6), "2nd craft ever to orbit Mercury",
              font=font(F_SANS_B, 9), fill=(255, 255, 255))


# ---------------------------------------------------------------- content
HEROES = [
    ("1  IRAN STRIKES US BASES IN BAHRAIN", "Gulf war widens",
     "The IRGC said it hit two US Patriot radars at al-Riffa and Awali with "
     "missiles and drones on Saturday night. Bahrain said a civilian plant was "
     "hit and caught fire. Radar-damage claims are unconfirmed.",
     "Al Jazeera, Xinhua, IRIB", "REPORTED", hero_art_gulf),
    ("2  DEEP 6.7 QUAKE SHAKES PERU", "No deaths reported",
     "A magnitude 6.7 quake struck 30–34 km from Junín at 00:09 UTC Saturday "
     "(19:09 Friday local), 108 km deep (USGS; Peru's IGP says 129 km). Felt "
     "in Lima and across central Peru: landslides, minor damage, power cuts.",
     "USGS, AFP, Peru Defence Ministry", "OFFICIAL", hero_art_quake),
    ("3  BEPICOLOMBO REACHES MERCURY", "After eight years",
     "ESA/JAXA's BepiColombo fired its thrusters for 37 minutes from 18:24 UTC "
     "Saturday and was captured by Mercury's gravity — only the second craft "
     "ever to orbit the innermost planet. Launched Oct 2018; its two orbiters "
     "separate on 9–10 Dec.",
     "ESA, Nature, AP", "OFFICIAL", hero_art_space),
]

MEDIUMS = [
    ("4", "WORLD", "COP31 runs into overtime with no deal",
     "In Antalya the summit ran a full day past its Friday close, nearly 200 "
     "countries split over a draft that drops every mention of fossil fuels "
     "and the $120bn adaptation target. Final vote moved to Sunday morning.",
     "Reuters, AFP, Al Jazeera", "REPORTED"),
    ("5", "AMERICAS", "Boca Juniors win the Copa Sudamericana 2–0",
     "Boca beat Atlético Mineiro in Barranquilla on Saturday night "
     "(Ascacíbar 16', Merentiel 48') — a third title and first international "
     "trophy in 18 years. Captain Paredes fainted live on TV in the celebrations.",
     "beIN SPORTS, Sportradar", "REPORTED"),
    ("6", "MIDEAST", "Three Houthi missiles shot down over Riyadh",
     "The Saudi-led coalition intercepted 3 ballistic missiles fired towards "
     "Riyadh early Saturday (~02:00 local) — NOT 5 — the second attack on the "
     "capital in days. Four drones and another missile were stopped over the south.",
     "Reuters, AFP, Arab News", "REPORTED"),
    ("7", "AMERICAS", "Mexico captures 'Chapo Isidro'; 11 killed",
     "Special forces captured FBI top-10 fugitive Fausto Isidro Meza Flores "
     "in Guasave, Sinaloa, on Friday night (announced Saturday morning), with "
     "US intelligence support. Four soldiers and 7 gunmen died in the raid.",
     "Reuters, Al Jazeera, WSJ", "OFFICIAL"),
    ("8", "EUROPE", "EU and Indonesia sign trade pact",
     "After a decade of talks, the CEPA was signed in Brussels: 90.4% of "
     "Indonesian tariff lines go duty-free from day one (98.5% of EU lines), "
     "covering ~$30bn of annual trade. In force from 2027 after ratification.",
     "AFP, CNA, European Commission", "OFFICIAL"),
    ("9", "WORLD", "128 nations agree to draft 'killer robot' rules",
     "After five days of UN talks in Geneva that ran to 04:45 Saturday, the "
     "128 states in the CCW agreed to 'elaborate' an instrument on lethal "
     "autonomous weapons over two years — but no binding rules yet.",
     "AFP, Al Jazeera, AP", "REPORTED"),
    ("10", "WORLD", "Bitcoin hits a two-year low, then rebounds 8%",
     "Bitcoin plunged to about $55,252 late Friday US time — its lowest since "
     "September 2024 — then rebounded more than 8% on Saturday to around "
     "$60,000. Figures are INTRADAY, not closes. ~$2.4bn of leveraged bets liquidated.",
     "Binance, Business Times", "REPORTED"),
    ("11", "EUROPE", "England rout the All Blacks 37–12, a record margin",
     "England ran in five tries at Twickenham for a record 25-point winning "
     "margin over New Zealand (previous best 17, in 2012), keeping their "
     "Nations Championship final hopes alive.",
     "Reuters, RFU, Sky Sports", "REPORTED"),
    ("12", "AMERICAS", "Verstappen wins a wild Las Vegas Grand Prix",
     "Max Verstappen won a slipstream thriller on the Strip on Saturday night "
     "— 35 lead changes in 50 laps — beating Norris by 0.639s, Piastri third. "
     "Russell hit the barriers 3 laps from the end; the Ferraris collided.",
     "Formula1.com, Reuters", "REPORTED"),
    ("13", "OCEANIA", "India 486–4, Rahul 136, lead New Zealand by 118",
     "KL Rahul (136) and Shubman Gill (98, bowled at the stroke of stumps) "
     "took India to 486/4 on day 3 of the Wellington Test. Rahul is only the "
     "fourth Indian with Test hundreds in all four SENA countries.",
     "Cricinfo, PTI", "REPORTED"),
    ("14", "MIDEAST", "Basra power-station fire kills 4, injures 35",
     "A fire at the 800 MW Hartha power station north of Basra broke out "
     "~06:00 local Saturday, spread to nearby houses and shut the plant down. "
     "A gas pipeline was involved; the cause is unknown.",
     "Reuters, INA, Al Jazeera", "REPORTED"),
]

BRIEFS = [
    ("15", "Kryvyi Rih: Russian 'triple-tap' kills a boy, 7, and a paramedic, 20; 60 wounded — struck Fri night."),
    ("16", "Gulf of Finland: drones hit Russian cargo ship Sparta II; crew of 16 evacuated as it burns and drifts."),
    ("17", "Taiwan: 21 Chinese jets in a combat-readiness patrol; 15 cross the median line."),
    ("18", "Turin: Alcaraz beats Shelton 3-6, 6-3, 7-6(1); Zverev beats Medvedev — final on Sunday."),
    ("19", "Banda Sea: M6.8 quake 226 km NE of Dili, 117 km deep; felt in Darwin; no tsunami."),
    ("20", "Gaza City: Israeli drone strike kills 3 in a food-aid van; IDF says they were Islamic Jihad."),
    ("21", "France: 82,500 march in the sixth Saturday of cost-of-living protests; 144 arrests."),
    ("22", "Newcastle 2–2 Arsenal: Barnes and Thiaw turn it round; Madueke rescues a point, 78'."),
    ("23", "Brasília: Bolsonaro, 71, moved to intensive care with a bowel obstruction; stable, conscious."),
    ("24", "Davao: Air Niugini 767 lands safely after an engine-fire warning; all 146 aboard safe."),
    ("25", "Pretoria: Mlambo-Ngcuka, ex-deputy president and ex-UN Women chief, dies at 71 — died Fri evening."),
    ("26", "Cook Islands: Cyclone Xavier weakens to Category 1; all 84 on Nassau safe as relief lands."),
    ("27", "Washington: Trump threatens a 'tremendous tax' on US firms building AI data centres abroad — said Fri."),
    ("28", "Beijing: China tells Japan to 'correct' its Taiwan words; Tokyo says its stance is unchanged."),
    ("29", "Hormuz: IRGC says it downed a US MQ-9 drone over the strait; US has not confirmed. [CLAIM]"),
    ("30", "Tehran: Araghchi says Iran's uranium stays in the country but it is open to a 'fair solution'."),
    ("31", "Dublin: Ireland beat South Africa 20–17."),
    ("32", "Melbourne: Australia beat England by 3 wickets in the T20."),
    ("33", "Mastung: Pakistan says 15 militants killed in a Balochistan raid."),
    ("34", "Niger State: bandits kill 6 in a village attack."),
    ("35", "Brussels: EU proposes a €1.582tn budget for 2028–34."),
    ("36", "Ust-Luga: Ukrainian drones hit Russia's Baltic oil port in an overnight raid."),
    ("37", "Beirut: Aoun says the state alone will hold arms."),
    ("38", "Bengal: Cyclone Akvan fades to a low; rain continues into Sunday."),
    ("39", "Washington: Vance says the Iran strikes were Trump's decision."),
    ("40", "Texas: execution of a man of 70 takes 63 minutes."),
    ("41", "Los Angeles: jury convicts a man of starting the Palisades fire."),
    ("42", "Missouri: judge approves a $7.25bn Roundup settlement."),
    ("43", "Vancouver: Canada rests its defence in the youth climate trial."),
    ("44", "Pyongyang: Kim tours factories, KCNA reports."),
    ("45", "Taipei: budget and a cash payout are passed."),
    ("46", "Bangkok: six-point plan on arsenic in two rivers."),
    ("47", "Melbourne: Cricket Australia backs Cummins as captain."),
    ("48", "Rome: jeweller Paolo Bulgari dies at 89."),
]

NUMBERS = [
    ("6.7", "Peru quake magnitude"),
    ("108 km", "Peru quake depth (USGS)"),
    ("2", "US bases hit in Bahrain*"),
    ("128", "nations back robot rules"),
    ("90.4%", "duty-free lines, EU–Indonesia"),
    ("$55,252", "Bitcoin intraday low†"),
]

TIMELINE = [
    ("00:09", "Peru M6.7 quake"),
    ("03:45", "Geneva robot talks end"),
    ("06:50", "Sparta II hit off Finland"),
    ("09:42", "Banda Sea M6.8"),
    ("17:30", "Newcastle–Arsenal KO"),
    ("18:24", "BepiColombo burn begins"),
    ("22:30", "Copa final kicks off"),
]

PINS = [  # (number, lon, lat)
    (1, 50.6, 26.2), (2, -75.5, -11.0), (3, 8.65, 49.87), (4, 30.7, 36.9),
    (5, -74.8, 11.0), (6, 46.7, 24.6), (7, -108.0, 25.5), (8, 4.35, 50.85),
    (9, 6.14, 46.2), (10, -0.34, 51.45), (11, -115.2, 36.1), (12, 174.8, -41.3),
    (13, 47.8, 30.5), (14, 130.0, -6.0),
]


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 26  # margin
    x0, x1 = M, W - M
    y = 8

    # ---- masthead ----
    d.line([x0, y, x1, y], fill=RULE, width=3)
    y += 6
    f_mast = font(F_SERIF, 40)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(t, font=f_mast)) / 2, y), t, font=f_mast, fill=INK)
    y += 48
    f_sub = font(F_SERIF_B := F_SERIF, 15)
    sub = "Saturday 21 November 2026  •  48 STORIES"
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, y), sub, font=f_sub, fill=RED)
    y += 22
    d.line([x0, y, x1, y], fill=RULE, width=1)
    y += 3
    d.line([x0, y, x1, y], fill=RULE, width=1)
    y += 6

    # ---- day in numbers ----
    f_num = font(F_SERIF, 21)
    f_numl = font(F_SANS, 8)
    bw = (x1 - x0 - 5 * 6) / 6
    for i, (big, lab) in enumerate(NUMBERS):
        bx = x0 + i * (bw + 6)
        d.rectangle([bx, y, bx + bw, y + 38], outline=LIGHT_RULE, fill=PAPER2)
        d.text((bx + bw / 2 - d.textlength(big, font=f_num) / 2, y + 1), big,
               font=f_num, fill=NAVY)
        d.text((bx + bw / 2 - d.textlength(lab, font=f_numl) / 2, y + 25), lab,
               font=f_numl, fill=MUTED)
    y += 38
    d.text((x0, y + 2), "*per IRGC claim  •  †intraday, not a close",
           font=font(F_SANS_I, 8), fill=MUTED)
    # region bar + HOW SURE legend on the same line, right side
    reg = "EUROPE 11  •  ASIA-PACIFIC 8  •  OCEANIA 4  •  MIDEAST 8  •  AFRICA 2  •  AMERICAS 11  •  WORLD 4"
    d.text((x1 - d.textlength(reg, font=font(F_SANS_B, 8)), y + 2), reg,
           font=font(F_SANS_B, 8), fill=INK)
    y += 18

    # ---- heroes ----
    f_hkick = font(F_SANS_B, 9)
    f_hhead = font(F_SERIF, 15)
    f_hbody = font(F_SERIF_R, 11)
    f_src = font(F_SANS_I, 8)
    colw = (x1 - x0 - 2 * 10) / 3
    hero_y = y
    art_h = 76
    for i, (kick, head, body, src, tag, art) in enumerate(HEROES):
        hx = x0 + i * (colw + 10)
        d.rectangle([hx, hero_y, hx + colw, hero_y + 190], outline=RULE, fill=(255, 252, 240))
        art(d, hx + 4, hero_y + 4, colw - 8, art_h)
        ty = hero_y + 4 + art_h + 5
        d.text((hx + 7, ty), kick, font=f_hkick, fill=RED)
        tag_chip(d, hx + colw - 62, ty + 1, tag, TAG_COLORS[tag])
        ty += 13
        ty = draw_wrapped(d, hx + 7, ty, head, f_hhead, colw - 14, leading=16, max_lines=2)
        ty = draw_wrapped(d, hx + 7, ty + 1, body, f_hbody, colw - 14, leading=12,
                          max_lines=4)
        d.text((hx + 7, hero_y + 190 - 13), "Source: " + src, font=f_src, fill=MUTED)
    y = hero_y + 190 + 5

    # ---- mediums ----
    f_sec = font(F_SANS_B, 11)
    d.text((x0, y), "THE DAY IN FULL — 11 MORE STORIES", font=f_sec, fill=INK)
    d.line([x0 + 250, y + 7, x1, y + 7], fill=LIGHT_RULE, width=1)
    y += 15
    med_h = 50
    rows = 6
    med_colw = (x1 - x0 - 10) / 2
    f_mkick = font(F_SANS_B, 8)
    f_mhead = font(F_SERIF, 12)
    f_mbody = font(F_SANS, 9)
    for r in range(rows):
        for c in range(2):
            idx = r * 2 + c
            if idx >= len(MEDIUMS):
                continue
            num, region, head, body, src, tag = MEDIUMS[idx]
            mx = x0 + c * (med_colw + 10)
            my = y + r * med_h
            d.rectangle([mx, my, mx + med_colw, my + med_h - 2], outline=LIGHT_RULE,
                        fill=(255, 252, 240))
            d.text((mx + 6, my + 3), num + "  " + region, font=f_mkick, fill=RED)
            tag_chip(d, mx + med_colw - 62, my + 3, tag, TAG_COLORS[tag])
            d.text((mx + 6, my + 14), head, font=f_mhead, fill=INK)
            # body, 2 lines max, slightly trimmed to fit
            lines = wrap(d, body, f_mbody, med_colw - 12)[:2]
            by = my + 28
            for ln in lines:
                d.text((mx + 6, by), ln, font=f_mbody, fill=(50, 48, 40))
                by += 10
            # source on the right of the last body line if room, else skip
    y += rows * med_h + 2

    # ---- briefs (2 columns x 17) ----
    d.text((x0, y), "BRIEFS — 34 MORE STORIES, NUMBERED 15–48",
           font=f_sec, fill=INK)
    d.line([x0 + 300, y + 7, x1, y + 7], fill=LIGHT_RULE, width=1)
    y += 15
    f_br = font(F_SANS, 9)
    brief_colw = (x1 - x0 - 10) / 2
    for i, (num, text) in enumerate(BRIEFS):
        col = i // 17
        row = i % 17
        bx = x0 + col * (brief_colw + 10)
        by = y + row * 11
        d.text((bx, by), num + ".", font=font(F_SANS_B, 9), fill=RED)
        d.text((bx + 20, by), text, font=f_br, fill=(50, 48, 40))
    y += 17 * 11 + 3

    # ---- UTC timeline ----
    f_tl = font(F_SANS, 9)
    d.rectangle([x0, y, x1, y + 21], fill=NAVY)
    d.text((x0 + 6, y + 5), "UTC", font=font(F_SANS_B, 10), fill=(255, 220, 120))
    tx = x0 + 40
    for t, lab in TIMELINE:
        s = t + "  " + lab
        d.text((tx, y + 5), s, font=f_tl, fill=(255, 255, 255))
        tx += d.textlength(s, font=f_tl) + 16
        if tx < x1 - 8:
            d.text((tx - 8, y + 5), "·", font=f_tl, fill=(255, 220, 120))
    y += 21 + 4

    # ---- map + date check side by side ----
    band_y = y
    band_h = 92
    map_w = 470
    mx0, my0 = x0, band_y
    d.rectangle([mx0, my0, mx0 + map_w, my0 + band_h], outline=RULE, fill=(233, 240, 244))
    d.text((mx0 + 6, my0 + 3), "WHERE IT HAPPENED — pins 1–14 (3 = BepiColombo, ESA Darmstadt)",
           font=font(F_SANS_B, 8), fill=NAVY)
    # dotted continents
    map_x1, map_y1 = mx0 + 8, my0 + 16
    map_w2, map_h2 = map_w - 16, band_h - 24
    step = 6.0
    lon = -180.0
    while lon <= 180:
        lat = 75.0
        while lat >= -56:
            if on_land(lon, lat):
                px = map_x1 + (lon + 180) / 360 * map_w2
                py = map_y1 + (75 - lat) / 131 * map_h2
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(90, 110, 130))
            lat -= 3.2
        lon += 3.2
    # pins
    for num, plon, plat in PINS:
        px = map_x1 + (plon + 180) / 360 * map_w2
        py = map_y1 + (75 - plat) / 131 * map_h2
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=(255, 255, 255))
        d.text((px - 3 if num < 10 else px - 6, py - 5), str(num),
               font=font(F_SANS_B, 8), fill=(255, 255, 255))
    # date check box
    dx0 = x0 + map_w + 10
    dx1 = x1
    d.rectangle([dx0, band_y, dx1, band_y + band_h], outline=RED, width=2,
                fill=(255, 246, 238))
    d.text((dx0 + 7, band_y + 4), "DATE CHECK — NOT 21 NOVEMBER",
           font=font(F_SANS_B, 10), fill=RED)
    dc = ("Khasab tanker strike — Fri 20 Nov. Kyiv bridges barrage — Fri 20 Nov. "
          "Kryvyi Rih strike hit Fri night (reported Sat). Mlambo-Ngcuka died Fri "
          "evening. Trump's AI data-centre tax threat said Fri. '111 caught cheating' "
          "Suneung figure announced Fri 20 Nov. DATED BY LOCAL DATE: stories are "
          "dated where they happened — Riyadh, Lima, Las Vegas, Barranquilla — so "
          "the F1 GP and Copa final, ending after midnight UTC, count as Saturday night.")
    draw_wrapped(d, dx0 + 7, band_y + 20, dc, font(F_SANS, 9), dx1 - dx0 - 14,
                 leading=11)
    y = band_y + band_h + 4

    # ---- footer ----
    d.line([x0, y, x1, y], fill=RULE, width=1)
    y += 3
    f_foot = font(F_SANS, 8)
    foot1 = ("Every story above happened or was first reported on Saturday 21 November 2026.  "
             "HOW SURE: OFFICIAL = official statement  •  REPORTED = reputable press  •  "
             "CLAIM = unconfirmed claim  •  FORECAST = not yet happened.")
    y = draw_wrapped(d, x0, y, foot1, f_foot, x1 - x0, leading=10)
    foot2 = ("Sources: Reuters, AP, AFP, Al Jazeera, BBC, ESA, USGS, ATP, Formula1.com, Cricinfo, "
             "IN A, Dawn, RNZ and others.  •  The World in One Day — 21 November 2026 (48 stories).")
    d.text((x0, y + 1), foot2, font=f_foot, fill=MUTED)
    y += 12

    # thin outer border
    d.rectangle([4, 4, W - 5, H - 5], outline=RULE, width=1)
    img.save(OUT, optimize=True)
    return OUT, y


if __name__ == "__main__":
    path, used = build()
    data = open(path, "rb").read()
    print("saved", path, len(data), "bytes, content bottom y =", used, "/ 1024")
    print("sha256", hashlib.sha256(data).hexdigest())
