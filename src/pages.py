"""Page builders — each function returns one finished 16:9 Figure."""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse, FancyBboxPatch

import matplotlib.image as mpimg

import charts
from config import (ASSETS_DIR, CREAM, DARK, DEEP_RED, DPI, GOLD, GREY,
                    LIGHT_GREY, NAVY, NAVY_DEEP, PAGE_H, PAGE_W, SERIF,
                    SPAIN_RED, TRI, WHITE)

SECTIONS = ["The Road", "In Possession", "Out of Possession", "The Squad", "Key Players"]


def _tri_stripe(fig: Figure, y: float, h: float = 0.006) -> None:
    """The WC26 host-nation stripe: Canada red / Mexico green / USA blue."""
    for i, c in enumerate(TRI):
        fig.patches.append(plt.Rectangle((i / 3, y), 1 / 3, h,
                                         transform=fig.transFigure,
                                         facecolor=c, zorder=3))


# ------------------------------------------------------------------ furniture
def _new_page() -> Figure:
    return plt.figure(figsize=(PAGE_W, PAGE_H), dpi=DPI)

def _header(fig: Figure, title: str, active: int | None = None) -> None:
    """Deep-red title band + section navigation, like the reference report."""
    fig.patches.append(plt.Rectangle((0, 0.925), 1, 0.075, transform=fig.transFigure,
                                     facecolor=NAVY, zorder=2))
    _tri_stripe(fig, 0.919)
    fig.text(0.035, 0.955, title, fontsize=19, family=SERIF, fontweight="bold",
             color=WHITE, va="center", zorder=3)
    fig.text(0.965, 0.955, "FIFA WORLD CUP 26™ · ESPAÑA", fontsize=8.5, color=GOLD,
             va="center", ha="right", family=SERIF, zorder=3)
    if active is not None:
        for i, s in enumerate(SECTIONS):
            fig.text(0.05 + i * 0.19, 0.888, s, fontsize=10.5, family=SERIF,
                     color=SPAIN_RED if i == active else GREY,
                     fontweight="bold" if i == active else "normal")

def _footer(fig: Figure, note: str) -> None:
    fig.patches.append(plt.Rectangle((0, 0), 1, 0.032, transform=fig.transFigure,
                                     facecolor=NAVY, zorder=2))
    _tri_stripe(fig, 0.032)
    fig.text(0.035, 0.016, note, fontsize=7, color=WHITE, va="center", zorder=3)

def _chart_title(fig: Figure, x: float, y: float, rich: list[tuple[str, bool]],
                 fontsize: float = 10.5) -> None:
    """A centred one-line title mixing regular and bold spans."""
    text = "".join(t for t, _ in rich)
    est_w = len(text) * fontsize * 0.00062          # rough width estimate
    cx = x - est_w / 2
    for t, bold in rich:
        fig.text(cx, y, t, fontsize=fontsize, color=DARK,
                 fontweight="bold" if bold else "normal")
        cx += len(t) * fontsize * 0.00062

def _source(fig: Figure, x: float, y: float, src: str, rest: str) -> None:
    fig.text(x, y, src, fontsize=7.2, color=DEEP_RED, ha="right",
             fontweight="bold")
    fig.text(x + 0.004, y, rest, fontsize=7.2, color=GREY)

def _commentary(fig: Figure, x: float, y: float, text: str, width: int = 95,
                fontsize: float = 8.6) -> None:
    fig.text(x, y, textwrap.fill(text, width), fontsize=fontsize, color=DARK,
             va="top", linespacing=1.55)

def _stat_card(fig: Figure, x: float, y: float, w: float, h: float,
               value: str, label: str, accent: str = SPAIN_RED) -> None:
    fig.patches.append(FancyBboxPatch((x, y), w, h, transform=fig.transFigure,
                                      boxstyle="round,pad=0.008",
                                      facecolor=WHITE, edgecolor=accent,
                                      linewidth=1.4, zorder=2))
    fig.text(x + w / 2, y + h * 0.60, value, fontsize=17, family=SERIF,
             fontweight="bold", color=accent, ha="center", va="center", zorder=3)
    fig.text(x + w / 2, y + h * 0.22, label, fontsize=7.6, color=GREY,
             ha="center", va="center", zorder=3)


# ------------------------------------------------------------------ pages
def _load_emblem() -> np.ndarray:
    """Official WC26 emblem; near-black background made transparent so it
    sits on the navy gradient."""
    img = mpimg.imread(ASSETS_DIR / "wc26_emblem.png")
    if img.shape[2] == 3:
        img = np.dstack([img, np.ones(img.shape[:2], dtype=img.dtype)])
    dark = img[..., :3].max(axis=2) < 0.10
    img = img.copy()
    img[dark, 3] = 0.0
    return img


def title_page(_: dict) -> Figure:
    fig = _new_page()
    # --- backdrop: vertical navy gradient + soft gold glow behind the trophy
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    grad = np.linspace(0, 1, 512)[:, None]
    ax.imshow(grad, aspect="auto", cmap=plt.cm.colors.LinearSegmentedColormap
              .from_list("bg", ["#132C52", NAVY_DEEP]), extent=[0, 1, 0, 1],
              zorder=0)
    yy, xx = np.mgrid[0:1:220j, 0:1:220j]
    glow = np.exp(-(((xx - 0.5) * 1.55) ** 2 + ((yy - 0.76) * 2.6) ** 2) * 6)
    ax.imshow(glow, extent=[0, 1, 0, 1], aspect="auto", zorder=1,
              cmap=plt.cm.colors.LinearSegmentedColormap.from_list(
                  "glow", [(0, 0, 0, 0), (0.79, 0.64, 0.15, 0.30)]))
    # faint pitch line-art rising from the bottom edge
    pitch_c = (1, 1, 1, 0.09)
    theta = np.linspace(0, np.pi, 120)
    ax.plot(0.5 + 0.16 * np.cos(theta), 0.20 * np.sin(theta) ** 1.4,
            color=pitch_c, lw=1.6, zorder=1)
    ax.plot([0.035, 0.965], [0.0035, 0.0035], color=pitch_c, lw=1.6, zorder=1)
    ax.scatter([0.5], [0.012], s=14, color=pitch_c, zorder=1)

    # --- emblem (official file, black matte keyed out)
    emblem = _load_emblem()
    h_img, w_img = emblem.shape[:2]
    box_h = 0.335
    box_w = box_h * (w_img / h_img) * (PAGE_H / PAGE_W)
    ax_img = fig.add_axes([0.5 - box_w / 2, 0.575, box_w, box_h], zorder=2)
    ax_img.imshow(emblem)
    ax_img.axis("off")

    # --- wordmark block
    fig.text(0.5, 0.535, "C A N A D A   ·   M E X I C O   ·   U S A",
             fontsize=9.5, color=GOLD, ha="center", family=SERIF)
    fig.text(0.5, 0.44, "Why Spain Won The 2026 World Cup",
             fontsize=31, family=SERIF, fontweight="bold", color="#F5F8FC",
             ha="center")
    fig.text(0.5, 0.385, "A  T O U R N A M E N T  T O L D  T H R O U G H  D A T A",
             fontsize=10, color="#8FA6C9", ha="center")
    # champions chip
    chip_w = 0.185
    fig.patches.append(FancyBboxPatch((0.5 - chip_w / 2, 0.318), chip_w, 0.038,
                                      transform=fig.transFigure,
                                      boxstyle="round,pad=0.006,rounding_size=0.012",
                                      facecolor=SPAIN_RED, edgecolor="none",
                                      zorder=3))
    fig.text(0.5, 0.337, "C A M P E O N E S  D E L  M U N D O", fontsize=8.5,
             color=WHITE, ha="center", va="center", fontweight="bold", zorder=4)

    # --- stat cards
    stats = [("8", "matches", TRI[0]), ("7", "wins  ·  1 draw", TRI[1]),
             ("14 – 1", "goals for – against", GOLD), ("7", "clean sheets", TRI[2])]
    cw, ch = 0.142, 0.115
    for i, (v, l, c) in enumerate(stats):
        x = 0.172 + i * 0.172
        fig.patches.append(FancyBboxPatch((x, 0.155), cw, ch,
                                          transform=fig.transFigure,
                                          boxstyle="round,pad=0.004,rounding_size=0.01",
                                          facecolor="#16345E", edgecolor="#28497A",
                                          linewidth=0.8, zorder=2))
        fig.patches.append(plt.Rectangle((x + 0.028, 0.155 + ch - 0.006),
                                         cw - 0.056, 0.0045,
                                         transform=fig.transFigure, facecolor=c,
                                         zorder=3))
        fig.text(x + cw / 2, 0.222, v, fontsize=19, family=SERIF,
                 fontweight="bold", color="#F5F8FC", ha="center", zorder=3)
        fig.text(x + cw / 2, 0.183, l, fontsize=8.5, color="#8FA6C9",
                 ha="center", zorder=3)

    # --- footer credits
    fig.text(0.035, 0.055, "CREATED BY", fontsize=7.5, color="#8FA6C9")
    fig.text(0.035, 0.028, "Aymane Labtiti", fontsize=10.5, family=SERIF,
             color="#F5F8FC")
    fig.text(0.965, 0.028, "Built end-to-end in Python  ·  pandas + matplotlib",
             fontsize=8, color="#8FA6C9", ha="right")
    _tri_stripe(fig, 0.0, h=0.008)
    return fig


def road_page(d: dict) -> Figure:
    m, t = d["matches"], d["teams"]
    fig = _new_page()
    _header(fig, "Tournament Landscape : The Road To A Second Star", active=0)

    ax1 = fig.add_axes([0.03, 0.13, 0.27, 0.70])
    _chart_title(fig, 0.165, 0.855, [("Eight games, ", False), ("zero defeats", True)])
    charts.road_to_glory(ax1, m)

    ax2 = fig.add_axes([0.38, 0.47, 0.27, 0.36])
    _chart_title(fig, 0.515, 0.855, [("Scored ", False), ("14", True),
                                     (", conceded ", False), ("1", True)])
    charts.cumulative_goals(ax2, m)
    _source(fig, 0.475, 0.415, "Source FIFA / ESPN :", " cumulative goals across the 8 matches")

    ax3 = fig.add_axes([0.71, 0.47, 0.26, 0.36])
    _chart_title(fig, 0.84, 0.855, [("Best ", False), ("attack–defence balance", True),
                                    (" of the deep runners", False)], fontsize=9.5)
    charts.goal_diff_scatter(ax3, t)
    _source(fig, 0.815, 0.392, "Source FotMob :", " per-match rates, Spain + the other deep runners")

    _commentary(fig, 0.375, 0.365,
        "Spain's route was anything but soft: Uruguay in the group, then Portugal, Belgium, "
        "France and Argentina back-to-back in the knockouts — four top-10 sides eliminated in a row. "
        "The scoreline pattern is the story of the campaign: after a wasteful 0-0 against Cape Verde, "
        "Spain never dropped another point and never trailed at any moment of the tournament.", width=108)
    _commentary(fig, 0.375, 0.24,
        "The attack-defence map on the right isolates why. Among every side that reached the last eight, "
        "Spain is alone in the top-right quadrant of the balance: 1.75 goals per game scored with just "
        "0.13 conceded. Argentina and France matched the attacking rate — nobody came close to combining "
        "it with Spain's defensive record of a single goal in 750+ minutes.", width=108)
    _footer(fig, "Results & scorers: FotMob match events  ·  all match metrics: FotMob (Opta-sourced), cached in data/fotmob/")
    return fig


def possession_page(d: dict) -> Figure:
    m, p = d["matches"], d["players"]
    fig = _new_page()
    _header(fig, "In Possession : Control First, Efficiency When It Counts", active=1)

    ax1 = fig.add_axes([0.05, 0.44, 0.27, 0.38])
    _chart_title(fig, 0.185, 0.855, [("Possession ", True), ("never below ", False),
                                     ("51%", True)])
    charts.possession_bars(ax1, m)
    _source(fig, 0.17, 0.385, "Source FotMob :", " possession share per match")

    ax2 = fig.add_axes([0.38, 0.44, 0.27, 0.38])
    _chart_title(fig, 0.515, 0.855, [("Creating ", False), ("~2 xG", True),
                                     (" every game", False)])
    charts.xg_vs_goals(ax2, m)
    _source(fig, 0.50, 0.385, "Source FotMob :", " xG vs goals per match")

    ax3 = fig.add_axes([0.73, 0.42, 0.24, 0.40])
    _chart_title(fig, 0.85, 0.855, [("11 players", True), (" with a goal or assist", False)])
    charts.scorer_spread(ax3, p)
    _source(fig, 0.85, 0.375, "Source FotMob :", " goals + assists per player")

    _commentary(fig, 0.05, 0.33,
        "Spain suffocated opponents with the ball before beating them with it. Possession never dipped "
        "below 51% — the semi-final against France was the only time it fell under 64% — and peaked at "
        "74% in the opener. That control is a defensive weapon as much as an attacking one: FotMob's "
        "numbers show opponents never generated more than 0.63 xG in a match.", width=105)
    _commentary(fig, 0.05, 0.215,
        "The chance-creation engine was remarkably steady: 15.6 expected goals across eight matches, "
        "roughly two per game regardless of opponent quality. Early wastefulness (0 goals from 2.1 xG vs "
        "Cape Verde) corrected itself as the tournament progressed. And crucially, the load was shared: "
        "Oyarzabal's five goals led the way, but eleven different players contributed a goal or an assist "
        "— full-back Porro and midfielder Merino chipping in from deep.", width=105)
    _footer(fig, "Match metrics: FotMob (Opta-based) via public API — raw JSON cached in data/fotmob/")
    return fig


def defence_page(d: dict) -> Figure:
    m, t = d["matches"], d["teams"]
    fig = _new_page()
    _header(fig, "Out Of Possession : The One-Goal Fortress", active=2)

    ax1 = fig.add_axes([0.05, 0.44, 0.27, 0.38])
    _chart_title(fig, 0.185, 0.855, [("xG conceded ", False), ("under 0.7", True),
                                     (" in every game", False)], fontsize=9.8)
    charts.xga_timeline(ax1, m)
    _source(fig, 0.17, 0.385, "Source FotMob :", " xG against & goals conceded")

    ax2 = fig.add_axes([0.40, 0.44, 0.25, 0.38])
    _chart_title(fig, 0.515, 0.855, [("1 goal conceded", True),
                                     (" — nobody was close", False)], fontsize=9.8)
    charts.conceded_ranking(ax2, t)
    _source(fig, 0.50, 0.385, "Source FIFA :", " goals conceded, Spain + beaten rivals")

    ax3 = fig.add_axes([0.72, 0.47, 0.25, 0.33])
    _chart_title(fig, 0.845, 0.855, [("The Final: ", False), ("total suffocation", True)])
    charts.final_dominance(ax3)
    _source(fig, 0.845, 0.415, "Source FotMob :", " Spain 1-0 Argentina (aet), Jul 19 2026")

    _commentary(fig, 0.05, 0.33,
        "One goal against in eight matches — over 750 minutes of football — is one of the great defensive "
        "campaigns in World Cup history, and FotMob's data shows it was no accident of luck: xG conceded "
        "never reached 0.7 in any match, just 2.4 across the whole tournament. The only breach was De "
        "Ketelaere's header for Belgium in the quarter-final — answered by Merino within the same match. "
        "Unai Simon's seven clean sheets earned him the Golden Glove; 19-year-old Pau Cubarsi, the "
        "tournament's Best Young Player, anchored the back line throughout.", width=105)
    _commentary(fig, 0.05, 0.195,
        "The final distilled the whole identity. Spain out-shot Argentina 20-2 with twelve efforts on "
        "target to Argentina's none in regulation — Messi's side did not manage a single attempt until "
        "the 117th minute. Enzo Fernandez was sent off in second-half stoppage time, and Ferran Torres "
        "struck the winner in the 106th. 0.22 xG conceded in a World Cup final is domination in its "
        "purest form.", width=105)
    _footer(fig, "Match data: FotMob  ·  Awards: FIFA official — Golden Glove: U. Simon, Best Young Player: P. Cubarsi")
    return fig


def structure_page(d: dict) -> Figure:
    m = d["matches"]
    fig = _new_page()
    _header(fig, "In Possession : Team Shape & Where The Threat Came From",
            active=1)

    ax1 = fig.add_axes([0.035, 0.30, 0.31, 0.52])
    _chart_title(fig, 0.19, 0.855, [("Average touch positions ", True),
                                    ("— Rodri is the hub", False)], fontsize=9.6)
    charts.average_positions(ax1, d["positions"])
    _source(fig, 0.19, 0.285, "Source FotMob :", " 7,724 real touches; node size = touch volume")

    ax2 = fig.add_axes([0.40, 0.46, 0.26, 0.33])
    _chart_title(fig, 0.53, 0.855, [("Both flanks, ", True), ("rarely the middle", False)])
    charts.attacking_zones_chart(ax2, d["zones"])
    _source(fig, 0.53, 0.425, "Source FotMob :", " attack distribution per match")

    ax3 = fig.add_axes([0.715, 0.46, 0.25, 0.33])
    _chart_title(fig, 0.84, 0.855, [("The game played ", False),
                                    ("in their half", True)])
    charts.territory_chart(ax3, m)
    _source(fig, 0.84, 0.425, "Source FotMob :", " passes in the opposition half")

    ax4 = fig.add_axes([0.735, 0.10, 0.115, 0.27])
    charts.donut(ax4, list(d["goal_types"].type), list(d["goal_types"]["count"]),
                 [SPAIN_RED, GOLD, NAVY, "#4A6FA5", GREY], "14", "goals")
    _chart_title(fig, 0.855, 0.385, [("How the goals came", True)], fontsize=9)

    _commentary(fig, 0.40, 0.375,
        "The shape map is built from every touch Spain played: Rodri sits deepest "
        "and central with 984 of them, more than any teammate — the hub the whole "
        "structure turns through. Behind him Cubarsi and Laporte took 854 and 818, "
        "proof that the build-up genuinely started at the back; ahead, Cucurella and "
        "Porro push so high they sit level with the midfield.", width=60, fontsize=8.2)
    _commentary(fig, 0.40, 0.22,
        "The zone split kills a lazy assumption: this was not a left-sided team. "
        "Attacks were almost perfectly balanced — 37% left, 36% right, just 27% "
        "through the middle — and the emphasis moved with the opponent, swinging "
        "to 46% left against Austria and 44% against France. Territory tells the "
        "rest: in six of eight matches more than half of Spain's passes were played "
        "inside the opponent's half.", width=60, fontsize=8.2)
    _footer(fig, "All figures from FotMob (Opta-sourced)  ·  goal types from FotMob situation tags: 11 open play, 1 corner, 1 penalty, 1 own goal won")
    return fig


def press_page(d: dict) -> Figure:
    m = d["matches"]
    fig = _new_page()
    _header(fig, "Out Of Possession : Winning The Ball Where It Hurts", active=2)

    ax1 = fig.add_axes([0.05, 0.44, 0.27, 0.36])
    _chart_title(fig, 0.185, 0.855, [("No team won it high ", False),
                                     ("more often", True)], fontsize=9.8)
    charts.poss_won_ranking(ax1, d["league"])
    _source(fig, 0.185, 0.40, "Source FotMob :", " possessions won in the attacking third, per match")

    ax2 = fig.add_axes([0.40, 0.44, 0.26, 0.36])
    _chart_title(fig, 0.53, 0.855, [("Pressing intensity ", True),
                                    ("match by match", False)], fontsize=9.8)
    charts.ppda_per_match(ax2, m)
    _source(fig, 0.53, 0.40, "Source FotMob :", " opponent passes ÷ tackles + interceptions")

    ax3 = fig.add_axes([0.715, 0.44, 0.25, 0.36])
    _chart_title(fig, 0.84, 0.855, [("Turning pressure into ", False),
                                    ("the box", True)], fontsize=9.8)
    charts.touches_box_chart(ax3, m)
    _source(fig, 0.84, 0.40, "Source FotMob :", " Spain's touches in the opposition box")

    _commentary(fig, 0.05, 0.35,
        "Spain finished the tournament first of the 32 ranked sides for possessions won in the attacking "
        "third — 6.1 per match, a third more than the France side they beat in the semi-final and more "
        "than double Argentina's 2.9. That is the clearest number in this report: the champions did their "
        "defending in the opponent's territory, not their own.", width=108)
    _commentary(fig, 0.05, 0.245,
        "The intensity was deliberately variable. Uruguay were pressed hardest — 11.6 opponent passes per "
        "Spanish tackle or interception, the fiercest squeeze of the campaign — while against Belgium, the "
        "one side to score against them, Spain sat off at 19.5 and paid for it. And the pressure converted "
        "into territory that mattered: 51 touches in the opposition box against both Cape Verde and Austria, "
        "and 32 in the Final, which turned into four big chances on a night Argentina created none.", width=108)
    _footer(fig, "Every figure on this page is real FotMob (Opta-sourced) data — raw JSON cached in data/fotmob/")
    return fig


def _photo(fig: Figure, box: list[float], path: str, circle: bool = False,
           border: str = GOLD) -> None:
    """Place a photo; optionally cropped to a circle with a coloured ring."""
    img = mpimg.imread(ASSETS_DIR / "photos" / path)
    ax = fig.add_axes(box, zorder=3)
    if circle:
        h, w = img.shape[:2]
        s = min(h, w)
        img = img[(h - s) // 2:(h + s) // 2, (w - s) // 2:(w + s) // 2]
        im = ax.imshow(img)
        clip = plt.Circle((0.5, 0.5), 0.5, transform=ax.transAxes)
        im.set_clip_path(clip)
        ax.add_patch(plt.Circle((0.5, 0.5), 0.492, transform=ax.transAxes,
                                fill=False, edgecolor=border, lw=2))
    else:
        ax.imshow(img)
    ax.axis("off")


GOAL_TITLES = [
    "4-0 Saudi Arabia  ·  wide overload",
    "1-0 Uruguay  ·  switch & cut inside",
    "1-0 Portugal  ·  counter-press strike, 90'",
    "2-0 France  ·  regain to far post",
    "2-0 France  ·  Yamal wins the pen",
    "1-0 Argentina  ·  the patient kill, 106'",
]


def goal_dna_page(d: dict) -> Figure:
    chains = d["chains"]
    fig = _new_page()
    _header(fig, "Goal DNA : The Build-Up Patterns Behind The Title", active=1)

    for gid in range(1, 7):
        col, row = (gid - 1) % 3, (gid - 1) // 3
        x0, y0 = 0.03 + col * 0.215, 0.475 - row * 0.36
        fig.text(x0 + 0.1, y0 + 0.315, GOAL_TITLES[gid - 1], fontsize=8,
                 color=NAVY, ha="center", fontweight="bold")
        ax = fig.add_axes([x0, y0, 0.2, 0.30])
        charts.goal_chain(ax, chains[chains.goal_id == gid])

    ax_map = fig.add_axes([0.685, 0.50, 0.29, 0.31])
    _chart_title(fig, 0.83, 0.845, [("Where they actually shot ", True),
                                    ("— all 8 games", False)], fontsize=9.4)
    charts.goals_map(ax_map, d["all_shots"])
    _source(fig, 0.83, 0.475, "Source FotMob :", " every Spain shot, real coordinates")

    _commentary(fig, 0.685, 0.435,
        "Six goals, four signatures — the wide overload and cutback, the "
        "switch to the weak side, the strike seconds after a regain, and "
        "the patient kill that decided the Final.", width=50, fontsize=8.2)
    _commentary(fig, 0.685, 0.315,
        "The real shot map behind them is just as revealing: 140 attempts "
        "worth 15.6 xG, almost all inside or on the edge of the box, and "
        "barely a speculative effort from distance. Eleven of the fourteen "
        "goals came from open play — one corner, one penalty, one own goal "
        "forced — and the highest-value open-play chance of the campaign was "
        "Merino's 0.69 xG winner against Belgium.", width=50, fontsize=8.2)
    _footer(fig, "Shot map: real FotMob coordinates & xG  ·  the six chains are tactical reconstructions from match reports — solid = pass, dashed = dribble, gold = cross, red = strike")
    return fig


def organisation_page(_: dict) -> Figure:
    fig = _new_page()
    _header(fig, "Organisation On The Pitch : Three Principles", active=2)

    boards = [(charts.board_build, "IN POSSESSION — the 3-2-5 build"),
              (charts.board_press, "OUT OF POSSESSION — the curve press"),
              (charts.board_counterpress, "TRANSITION — the 5-second rule")]
    for i, (draw, title) in enumerate(boards):
        x0 = 0.035 + i * 0.225
        fig.text(x0 + 0.1, 0.845, title, fontsize=8.2, color=NAVY,
                 ha="center", fontweight="bold")
        ax = fig.add_axes([x0, 0.44, 0.2, 0.38])
        draw(ax)

    cams = [(charts.cam_build, "The camera view: the overload forms far side"),
            (charts.cam_press, "The camera view: the 9 curves, the trap waits"),
            (charts.cam_counter, "The camera view: four shirts, five seconds")]
    for i, (draw, cap) in enumerate(cams):
        ax = fig.add_axes([0.035 + i * 0.225, 0.075, 0.2, 0.33])
        draw(ax)
        fig.text(0.135 + i * 0.225, 0.052, cap, fontsize=6.8, color=GREY,
                 ha="center")

    _commentary(fig, 0.725, 0.80,
        "Three principles, each shown twice: the analyst's plan view "
        "on top, and the same moment through a virtual tactical "
        "camera below — the broadcast angle, reconstructed in code.", width=44,
        fontsize=8.2)
    _commentary(fig, 0.725, 0.645,
        "With the ball, Spain build a 3-2-5 that pins opponents in "
        "their own half — Cucurella releases while Porro tucks in.", width=44,
        fontsize=8.2)
    _commentary(fig, 0.725, 0.525,
        "Without it, Oyarzabal's curved run hides the centre and "
        "shows the touchline, where the trap springs shut on the "
        "ringed full-back.", width=44, fontsize=8.2)
    _commentary(fig, 0.725, 0.385,
        "And in the moment between, the nearest four collapse on the "
        "ball inside five seconds — the engine behind 71 high "
        "regains. Every phase is a territorial argument; Spain won "
        "it in all eight matches.", width=44, fontsize=8.2)
    _footer(fig, "Plan boards and tactical-camera frames are reconstructions from match reports & broadcast analysis — rendered entirely in matplotlib")
    return fig


# photo key -> (display name, role, real-data caption, name in touch dataset)
GALLERY = {
    "rodri": [("Rodri", "DM  ·  Golden Ball"),
              "984 touches, most in the squad  ·  93.7 accurate passes per 90",
              "Rodri"],
    "yamal": [("Lamine Yamal", "RW  ·  19 years old"),
              "4.0 successful dribbles per 90  ·  1.5 xA, 7 chances created",
              "Lamine Yamal"],
    "oyarzabal": [("Mikel Oyarzabal", "ST  ·  top scorer"),
                  "5 goals from 4.0 xG  ·  scored in four different matches",
                  "Mikel Oyarzabal"],
    "simon": [("Unai Simon", "GK  ·  Golden Glove"),
              "7 clean sheets in 8  ·  10.4 recoveries per 90, 2nd at WC26",
              "Unai Simón"],
    "cubarsi": [("Pau Cubarsi", "CB  ·  Best Young Player"),
                "854 touches at 19  ·  more than any defender in the squad",
                "Pau Cubarsí"],
    "olmo": [("Dani Olmo", "AM  ·  the pocket finder"),
             "10 chances created  ·  92nd percentile among WC26 attackers",
             "Dani Olmo"],
}


def gallery_page(d: dict) -> Figure:
    touches = d["touches"]
    fig = _new_page()
    _header(fig, "Some Of Their Key Players", active=4)
    for i, (k, ((name, role), caption, data_name)) in enumerate(GALLERY.items()):
        col, row = i % 3, i // 3
        x0, y0 = 0.045 + col * 0.325, 0.47 - row * 0.385
        mine = touches[touches.player == data_name]
        _photo(fig, [x0, y0 + 0.145, 0.078, 0.14], f"{k}.jpg", circle=True,
               border=GOLD if k in ("rodri", "simon", "cubarsi") else SPAIN_RED)
        fig.text(x0 + 0.095, y0 + 0.245, name, fontsize=11.5, family=SERIF,
                 fontweight="bold", color=NAVY)
        fig.text(x0 + 0.095, y0 + 0.215, role, fontsize=7.8, color=GREY)
        ax = fig.add_axes([x0 + 0.095, y0, 0.165, 0.20])
        charts.player_heatmap(ax, mine)
        fig.text(x0 + 0.13, y0 - 0.012, caption, fontsize=7.0, color=DARK)
        fig.text(x0 + 0.095, y0 - 0.036,
                 f"Heatmap computed from {len(mine)} real touches (FotMob match heatmaps)",
                 fontsize=5.8, color=GREY)
    _footer(fig, "Player photos: Bryan Berlin, Wikimedia Commons, CC BY-SA 4.0 (WC26 semi-final & final)  ·  heatmaps built from 7,724 real touch coordinates")
    return fig


def final_micro_page(d: dict) -> Figure:
    shots = d["final_shots"]
    fig = _new_page()
    _header(fig, "The Final Under The Microscope : Spain 1-0 Argentina (aet)",
            active=None)
    fig.text(0.5, 0.885, "MetLife Stadium, July 19 2026  ·  real shot-by-shot "
             "data from FotMob: 20-2 shots, 12-0 on target, 2.29-0.22 xG",
             fontsize=9.5, family=SERIF, color=GREY, ha="center")

    ax1 = fig.add_axes([0.035, 0.42, 0.30, 0.40])
    _chart_title(fig, 0.185, 0.845, [("Every shot ", True), ("of the Final", False)])
    charts.final_shot_map(ax1, shots)
    _source(fig, 0.185, 0.395, "Source FotMob :", " shotmap — real coordinates & per-shot xG")

    ax2 = fig.add_axes([0.39, 0.46, 0.27, 0.355])
    _chart_title(fig, 0.525, 0.845, [("The xG race ", True), ("— one-way traffic", False)])
    charts.xg_race(ax2, shots)
    _source(fig, 0.525, 0.415, "Source FotMob :", " cumulative xG, 120 minutes")

    ax3 = fig.add_axes([0.715, 0.46, 0.255, 0.355])
    _chart_title(fig, 0.845, 0.845, [("Shots per ", False), ("15-minute window", True)])
    charts.shots_by_window(ax3, shots)
    _source(fig, 0.845, 0.415, "Source FotMob :", " shot volume by window")

    ax4 = fig.add_axes([0.545, 0.115, 0.42, 0.155])
    _chart_title(fig, 0.755, 0.30, [("Match momentum ", True),
                                    ("— Spain on top almost throughout", False)],
                 fontsize=9.6)
    charts.momentum_chart(ax4, d["momentum"])
    _source(fig, 0.965, 0.075, "Source FotMob :", "")

    _commentary(fig, 0.035, 0.34,
        "The map shows a siege: Spain's twenty attempts ring the Argentine box, twelve on target, while "
        "Argentina did not attempt a single shot until the 117th minute — Messi's effort and a Simeone "
        "strike in the last seconds were all they mustered.", width=62)
    _commentary(fig, 0.035, 0.225,
        "The xG race only ever climbs in red: 2.29 expected goals to 0.22. Then the dam broke twice in "
        "thirteen minutes — Enzo Fernandez's second yellow in stoppage time, and Ferran Torres finishing "
        "in the 106th the move the whole final had been building toward.", width=62)
    _footer(fig, "All match data: FotMob (Opta-based), fetched by scripts/fetch_fotmob.py — raw JSON cached in data/fotmob/")
    return fig


def context_page(d: dict) -> Figure:
    hist, players = d["history"], d["players"]
    fig = _new_page()
    _header(fig, "A Champion In Context : History Says This Was Special",
            active=None)

    ax1 = fig.add_axes([0.05, 0.42, 0.40, 0.38])
    _chart_title(fig, 0.25, 0.845, [("The stingiest champion ", True),
                                    ("of the modern era", False)])
    charts.champions_ga(ax1, hist)
    _source(fig, 0.25, 0.365, "Source FIFA archives :", " goals conceded by each World Cup winner")

    ax2 = fig.add_axes([0.53, 0.42, 0.29, 0.38])
    _chart_title(fig, 0.675, 0.845, [("Two generations, ", False), ("one core", True)])
    charts.age_minutes(ax2, players)
    _source(fig, 0.675, 0.345, "Source FotMob :", " age at the Final vs minutes played")

    avg_age = (players.age * players.minutes).sum() / players.minutes.sum()
    _stat_card(fig, 0.865, 0.62, 0.115, 0.14, f"{avg_age:.1f}",
               "minutes-weighted\naverage age", SPAIN_RED)
    _stat_card(fig, 0.865, 0.44, 0.115, 0.14, "19", "age of Cubarsi & Yamal\n— both starters", GOLD)

    _commentary(fig, 0.05, 0.29,
        "One goal conceded is not just this tournament's best defence — it is the best defensive campaign "
        "by any World Cup winner in the modern era, and Spain did it across eight matches where every "
        "champion before them played seven. Italy 2006 and Spain 2010, the previous benchmarks, conceded "
        "two; the last two champions before 2026 conceded six and eight.", width=108)
    _commentary(fig, 0.05, 0.19,
        "The squad structure explains why this may only be the beginning. The minutes were carried by two "
        "generations at once: a prime core aged 26-30 (Rodri, Oyarzabal, Simon, Cucurella) and a teenage "
        "spine — Cubarsi and Yamal, both 19, both starters in the Final. A minutes-weighted average age "
        "of 26.4 with the two youngest players locked into the XI is the profile of a team built to defend "
        "this title in 2030.", width=108)
    _footer(fig, "Champions' records: FIFA tournament archives (2006-2022 winners each played 7 matches; the expanded 2026 format required 8)")
    return fig


def squad_page(d: dict) -> Figure:
    p = d["players"]
    fig = _new_page()
    _header(fig, "The Squad : One XI, Sixteen Contributors", active=3)

    ax1 = fig.add_axes([0.045, 0.12, 0.255, 0.70])
    _chart_title(fig, 0.172, 0.855, [("The Final XI ", True), ("(4-2-3-1)", False)])
    charts.formation_pitch(ax1)
    _source(fig, 0.172, 0.095, "Source SI / beIN :", " unchanged from the semi-final")

    ax2 = fig.add_axes([0.40, 0.16, 0.25, 0.66])
    _chart_title(fig, 0.515, 0.855, [("Minutes", True), (" — a settled spine, a deep bench", False)],
                 fontsize=9.8)
    charts.minutes_bars(ax2, p)
    _source(fig, 0.515, 0.10, "Source FotMob :", " real minutes incl. extra time")

    ax3 = fig.add_axes([0.72, 0.47, 0.25, 0.35])
    _chart_title(fig, 0.845, 0.855, [("Production ", False), ("vs minutes played", True)])
    charts.contribution_scatter(ax3, p)
    _source(fig, 0.845, 0.40, "Source FotMob :", " goal involvements per 90")

    _commentary(fig, 0.70, 0.345,
        "De la Fuente found his best XI by the semi-final and never touched it again — the same "
        "eleven started against France and Argentina. Four men were on the pitch for all or almost "
        "all of the 750+ minutes: Simon, Cubarsi, Cucurella and Laporte.", width=52)
    _commentary(fig, 0.70, 0.205,
        "The scatter shows the two kinds of contributor: the volume producer (Oyarzabal, 6 goal "
        "involvements) and the surgical substitutes — Merino's two knockout winners came in just "
        "193 minutes, a goal involvement rate no starter matched.", width=52)
    _footer(fig, "Final XI: Simon; Porro, Cubarsi, Laporte, Cucurella; Rodri, F. Ruiz; Yamal, Olmo, Baena; Oyarzabal  ·  Coach: Luis de la Fuente")
    return fig


def profiles_page(d: dict) -> Figure:
    prof = d["profiles"]
    fig = _new_page()
    _header(fig, "Key Players Under The Microscope", active=4)

    order = ["Rodri", "Unai Simon", "Mikel Oyarzabal",
             "Lamine Yamal", "Pau Cubarsi", "Dani Olmo"]
    accents = {"Rodri": GOLD, "Unai Simon": GOLD, "Mikel Oyarzabal": SPAIN_RED,
               "Lamine Yamal": SPAIN_RED, "Pau Cubarsi": GOLD, "Dani Olmo": SPAIN_RED}
    for i, name in enumerate(order):
        col, row = i % 3, i // 3
        x0, y0 = 0.055 + col * 0.325, 0.50 - row * 0.36
        rows = prof[prof.player == name]
        fig.text(x0, y0 + 0.30, name, fontsize=13, family=SERIF,
                 fontweight="bold", color=NAVY)
        fig.text(x0, y0 + 0.272, rows.role_line.iloc[0], fontsize=8.2, color=GREY)
        ax = fig.add_axes([x0, y0, 0.26, 0.24])
        charts.profile_panel(ax, rows, accents[name])

    fig.text(0.5, 0.085,
             "Every value is real FotMob data. Each bar is the player's true percentile against "
             "WC26 players in the same position group who played 180+ minutes (gold = award winner).",
             fontsize=8, color=GREY, ha="center")
    _footer(fig, "Awards: Golden Ball — Rodri  ·  Golden Glove — U. Simon  ·  Best Young Player — P. Cubarsi  ·  percentile peer groups: 27 GKs, 109 DFs, 90 MFs, 105-152 ATTs")
    return fig


def england_page(d: dict) -> Figure:
    eng = d["england"]
    fig = _new_page()
    _header(fig, "The One That Got Away : England, The Champion Spain Never Met",
            active=None)
    fig.text(0.5, 0.885, "Third place  ·  the only heavyweight missing from Spain's route  ·  "
             "eliminated by Argentina at 90+2 in the semi-final",
             fontsize=10, family=SERIF, color=GREY, ha="center")

    ax1 = fig.add_axes([0.03, 0.10, 0.27, 0.70])
    _chart_title(fig, 0.165, 0.845, [("6W 1D 1L", True), (" — 20 scored, 12 conceded", False)])
    charts.england_route(ax1, eng)
    _source(fig, 0.165, 0.075, "Source FIFA / ESPN / Olympics.com :", " England's eight matches")

    ax2 = fig.add_axes([0.36, 0.55, 0.29, 0.26])
    _chart_title(fig, 0.505, 0.845, [("Two ways to build ", False), ("an attack", True)])
    charts.duo_dependency(ax2)
    _source(fig, 0.505, 0.525, "Source beIN / englandfootball.com :", " Kane 6 + Bellingham 7, first 6+6 duo in WC history")

    t = d["teams"].set_index("team")
    esp, eng = t.loc["Spain"], t.loc["England"]
    ax3 = fig.add_axes([0.70, 0.42, 0.27, 0.40])
    _chart_title(fig, 0.835, 0.845, [("Head to head ", True), ("by the numbers", False)])
    charts.butterfly(ax3, [
        ("Goals per match", eng.gf / eng.matches, esp.gf / esp.matches,
         f"{eng.gf / eng.matches:.2f}", f"{esp.gf / esp.matches:.2f}", 0),
        ("Goals conceded per match", eng.ga / eng.matches, esp.ga / esp.matches,
         f"{eng.ga / eng.matches:.2f}", f"{esp.ga / esp.matches:.2f}", 1),
        ("xG conceded (tournament)", eng.xg_against, esp.xg_against,
         f"{eng.xg_against:.1f}", f"{esp.xg_against:.1f}", 1),
        ("Clean sheets", eng.clean_sheets, esp.clean_sheets,
         f"{eng.clean_sheets:.0f}", f"{esp.clean_sheets:.0f}", 1),
        ("Ball won in attacking third /match", eng.poss_won_final_third,
         esp.poss_won_final_third, f"{eng.poss_won_final_third:.1f}",
         f"{esp.poss_won_final_third:.1f}", 1),
    ])
    _source(fig, 0.835, 0.395, "Source FotMob :", " both teams, 8 matches each")

    _commentary(fig, 0.36, 0.46,
        "England were the tournament's heaviest scorers — 20 goals, more than Spain — powered by the "
        "deadliest partnership a World Cup has ever seen: Kane and Bellingham became the first teammates "
        "to reach six goals each in a single edition. On raw firepower, they were the one side that could "
        "out-gun anyone, and their 6-4 bronze-final win over France showed it.", width=64)
    _commentary(fig, 0.36, 0.30,
        "But the numbers also explain why Spain would have been favourites in the final that never was. "
        "England conceded 12 goals from 9.3 expected; Spain conceded one from 2.4. England kept two clean "
        "sheets to Spain's seven. And England's goals ran through two men (65%), a dependency Spain's "
        "system is built to break — a press that won the ball in the attacking third 6.1 times a match "
        "against England's 3.4, starving the supply line long before it reaches the finisher.", width=64)
    _footer(fig, "England route: Croatia 4-2, Ghana 0-0, Panama 2-0, DR Congo 2-1, Mexico 3-2, Norway 2-1, Argentina 1-2, France 6-4  ·  Coach: Thomas Tuchel")
    return fig


def identity_page(d: dict) -> Figure:
    m, t = d["matches"], d["teams"]
    fig = _new_page()
    _header(fig, "Identity & Five Reasons Spain Won", active=None)

    ax1 = fig.add_axes([0.045, 0.40, 0.24, 0.42], polar=True)
    _chart_title(fig, 0.165, 0.855, [("Spain ", True), ("vs beaten rivals (avg)", False)])
    charts.radar_identity(ax1, m, t)
    _source(fig, 0.165, 0.345, "Source FotMob :", " normalised per-match profile")

    cards = [("RODRI", "Golden Ball — best player", GOLD),
             ("U. SIMON", "Golden Glove — 7 clean sheets", SPAIN_RED),
             ("P. CUBARSI", "Best Young Player — age 19", SPAIN_RED),
             ("M. OYARZABAL", "5 goals — Spain top scorer", SPAIN_RED),
             ("L. YAMAL", "4.0 dribbles per 90 — 98th percentile", SPAIN_RED),
             ("F. TORRES", "Scored the Final winner, 106'", GOLD)]
    for i, (v, l, accent) in enumerate(cards):
        x, y = 0.335 + (i % 3) * 0.222, 0.63 - (i // 3) * 0.155
        _stat_card(fig, x, y, 0.195, 0.115, v, l, accent)

    reasons = [
        ("1. Elite defence", "One goal conceded in eight games; xG against never above 0.7 (FotMob)."),
        ("2. Shared goals", "Eleven players with a goal or assist; four knockout winners from four scorers."),
        ("3. Midfield control", "51%+ possession in every match (avg 64%), run by Golden Ball winner Rodri."),
        ("4. Squad depth", "Merino scored two knockout winners in just 193 minutes off the bench."),
        ("5. Big-game nerve", "Portugal, Belgium, France, Argentina beaten in succession."),
    ]
    fig.text(0.335, 0.415, "Five reasons Spain won", fontsize=12.5,
             family=SERIF, fontweight="bold", color=DEEP_RED)
    for i, (head, body) in enumerate(reasons):
        y = 0.365 - i * 0.058
        fig.text(0.335, y, head, fontsize=9.6, fontweight="bold", color=SPAIN_RED)
        fig.text(0.475, y, body, fontsize=9.2, color=DARK)
    _footer(fig, "Report generated 100% in Python (pandas + matplotlib)  ·  github.com — Spain WC26 analysis project")
    return fig


PAGES = [title_page, road_page, possession_page, structure_page, goal_dna_page,
         defence_page, press_page, organisation_page, final_micro_page,
         squad_page, profiles_page, gallery_page, england_page, context_page,
         identity_page]
