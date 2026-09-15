"""Page builders — each function returns one finished 16:9 Figure."""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

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
    _source(fig, 0.815, 0.392, "Source compiled data :", " per-match rates, Spain + beaten rivals")

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
    _footer(fig, "Scores & scorers: FIFA / ESPN / Striker Report  ·  xG and possession are estimates compiled from public match reports")
    return fig


def possession_page(d: dict) -> Figure:
    m, p = d["matches"], d["players"]
    fig = _new_page()
    _header(fig, "In Possession : Control First, Efficiency When It Counts", active=1)

    ax1 = fig.add_axes([0.05, 0.44, 0.27, 0.38])
    _chart_title(fig, 0.185, 0.855, [("Possession ", True), ("never below ", False),
                                     ("55%", True)])
    charts.possession_bars(ax1, m)
    _source(fig, 0.17, 0.385, "Source compiled data :", " possession share per match (est.)")

    ax2 = fig.add_axes([0.38, 0.44, 0.27, 0.38])
    _chart_title(fig, 0.515, 0.855, [("Creating ", False), ("~2.2 xG", True),
                                     (" every game", False)])
    charts.xg_vs_goals(ax2, m)
    _source(fig, 0.50, 0.385, "Source compiled data :", " est. xG vs goals per match")

    ax3 = fig.add_axes([0.73, 0.42, 0.24, 0.40])
    _chart_title(fig, 0.85, 0.855, [("11 players", True), (" with a goal or assist", False)])
    charts.scorer_spread(ax3, p)
    _source(fig, 0.85, 0.375, "Source FIFA :", " goal involvements (assists est.)")

    _commentary(fig, 0.05, 0.33,
        "Spain suffocated opponents with the ball before beating them with it. Possession never dipped "
        "below 55% — even against France and Argentina — and peaked at 74% in the opener. That control "
        "is a defensive weapon as much as an attacking one: opponents averaged fewer than four shots per "
        "game simply because they rarely had the ball.", width=105)
    _commentary(fig, 0.05, 0.215,
        "The chance-creation engine was remarkably steady: roughly 2.2 expected goals per match, every "
        "match, regardless of opponent quality. Early wastefulness (0 goals from ~2.1 xG vs Cape Verde) "
        "corrected itself as the tournament progressed. And crucially, the load was shared: Oyarzabal's five "
        "goals led the way, but eleven different players contributed a goal or an assist — full-back Porro "
        "and midfielder Merino chipping in from deep. Take away any one attacker and Spain still scores.", width=105)
    _footer(fig, "Advanced metrics are estimates compiled from public match reports — see README for data provenance")
    return fig


def defence_page(d: dict) -> Figure:
    m, t = d["matches"], d["teams"]
    fig = _new_page()
    _header(fig, "Out Of Possession : The One-Goal Fortress", active=2)

    ax1 = fig.add_axes([0.05, 0.44, 0.27, 0.38])
    _chart_title(fig, 0.185, 0.855, [("xG conceded ", False), ("under 1.1", True),
                                     (" in every game", False)], fontsize=9.8)
    charts.xga_timeline(ax1, m)
    _source(fig, 0.17, 0.385, "Source compiled data :", " est. xG against & goals conceded")

    ax2 = fig.add_axes([0.40, 0.44, 0.25, 0.38])
    _chart_title(fig, 0.515, 0.855, [("1 goal conceded", True),
                                     (" — nobody was close", False)], fontsize=9.8)
    charts.conceded_ranking(ax2, t)
    _source(fig, 0.50, 0.385, "Source FIFA :", " goals conceded, Spain + beaten rivals")

    ax3 = fig.add_axes([0.72, 0.47, 0.25, 0.33])
    _chart_title(fig, 0.845, 0.855, [("The Final: ", False), ("total suffocation", True)])
    charts.final_dominance(ax3)
    _source(fig, 0.845, 0.415, "Source CBS / ESPN :", " Spain 1-0 Argentina (aet), Jul 19 2026")

    _commentary(fig, 0.05, 0.33,
        "One goal against in eight matches — over 750 minutes of football — is one of the great defensive "
        "campaigns in World Cup history, and it was no accident of luck: estimated xG conceded stayed near "
        "or below one in every single game. The only breach came from Belgium in the quarter-final, and it "
        "was answered within the same match. Unai Simon's seven clean sheets earned him the Golden Glove; "
        "19-year-old Pau Cubarsi, the tournament's Best Young Player, anchored the back line throughout.", width=105)
    _commentary(fig, 0.05, 0.20,
        "The final distilled the whole identity. Spain out-shot Argentina 20-3 and held Messi's side to a "
        "single shot on target across 120 minutes — a suffocating display capped when Enzo Fernandez was "
        "sent off in second-half stoppage time and Ferran Torres struck the winner in the 106th minute. "
        "An estimated 0.2 xG conceded in a World Cup final is domination in its purest form.", width=105)
    _footer(fig, "Awards: FIFA official — Golden Glove: U. Simon, Best Young Player: P. Cubarsi")
    return fig


def structure_page(d: dict) -> Figure:
    fig = _new_page()
    _header(fig, "In Possession : Structure, Networks & The High Block", active=1)

    ax1 = fig.add_axes([0.035, 0.12, 0.27, 0.70])
    _chart_title(fig, 0.17, 0.855, [("Passing network ", True), ("— everything through Rodri", False)],
                 fontsize=9.6)
    charts.pass_network(ax1, d["network"])
    _source(fig, 0.17, 0.095, "Source compiled data :", " Final XI combinations (est.), node = involvement")

    ax2 = fig.add_axes([0.345, 0.30, 0.30, 0.52])
    _chart_title(fig, 0.50, 0.855, [("A block living ", False), ("7 m higher", True),
                                    (" than the tournament", False)], fontsize=9.6)
    charts.team_lines(ax2, d["lines"])
    _source(fig, 0.50, 0.285, "Source compiled data :", " avg line heights from own goal (est.)")

    ax3 = fig.add_axes([0.71, 0.52, 0.26, 0.30])
    _chart_title(fig, 0.84, 0.855, [("Line discipline ", True), ("match by match", False)])
    charts.def_line_trend(ax3, d["lines"])
    _source(fig, 0.84, 0.455, "Source compiled data :", " def. line height per match (est.)")

    ax4 = fig.add_axes([0.725, 0.115, 0.115, 0.27])
    charts.donut(ax4, list(d["goal_types"].type), list(d["goal_types"]["count"]),
                 [SPAIN_RED, GOLD, NAVY, GREY], "14", "goals")
    _chart_title(fig, 0.845, 0.415, [("How the goals came", True)], fontsize=9)

    _commentary(fig, 0.345, 0.22,
        "The network shows a team wired through its No. 6: Rodri is the only node "
        "touching every layer — back line, double pivot and front four. The strongest "
        "links run down the flanks (Porro-Yamal, Cucurella-Baena), the launchpads for "
        "Spain's wide overloads.", width=60, fontsize=8.2)
    _commentary(fig, 0.345, 0.098,
        "Structurally, the block was brave: a defensive line ~41 m out, seven metres "
        "above the tournament norm — and disciplined, dropping only against the "
        "fastest front lines (France, Argentina).", width=60, fontsize=8.2)
    _footer(fig, "Line heights and pass volumes are estimates compiled from public match reports  ·  goal types: 8 open play, 3 counter-press, 2 set piece, 1 penalty")
    return fig


def press_page(d: dict) -> Figure:
    fig = _new_page()
    _header(fig, "Out Of Possession : Winning The Ball Where It Hurts", active=2)

    ax1 = fig.add_axes([0.035, 0.32, 0.30, 0.50])
    _chart_title(fig, 0.185, 0.855, [("Defensive actions ", True),
                                     ("cluster past halfway", False)], fontsize=9.6)
    charts.pressing_heatmap(ax1, d["press_zones"])
    _source(fig, 0.185, 0.30, "Source compiled data :", " pressures + recoveries by zone, all 8 games (est.)")

    ax2 = fig.add_axes([0.355, 0.32, 0.30, 0.50])
    _chart_title(fig, 0.505, 0.855, [("71 high regains", True), (" — 19 became shots", False)],
                 fontsize=9.6)
    charts.high_regains_map(ax2, d["regains"])
    _source(fig, 0.505, 0.30, "Source compiled data :", " regains in the last 40 m (illustrative layer)")

    ax3 = fig.add_axes([0.72, 0.48, 0.25, 0.34])
    _chart_title(fig, 0.845, 0.855, [("The fiercest press", True),
                                     (" of the deep runners", False)], fontsize=9.6)
    charts.ppda_bars(ax3, d["teams"])
    _source(fig, 0.845, 0.41, "Source compiled data :", " passes allowed per defensive action (est.)")

    _commentary(fig, 0.035, 0.235,
        "The heat map gives the press its shape: the busiest zones sit just past halfway and in the "
        "central corridor — Spain rarely defended deep because the ball rarely got that far. Olmo and "
        "Oyarzabal screened the opponent's pivot while the winger and near-side eight jumped, funnelling "
        "play into the crowded middle.", width=108)
    _commentary(fig, 0.035, 0.135,
        "And the press paid in goals, not just territory. Of 71 regains inside the opponent's final 40 m, "
        "19 turned into a shot within fifteen seconds and five ended in the net — counter-press strikes "
        "account for 3 of Spain's 14 goals. An estimated PPDA of 8.9 made it the most aggressive press of "
        "any quarter-finalist, pairing a 65% possession game with instant ball-winning: the double grip "
        "that defined this champion.", width=108)
    _footer(fig, "Event locations are an illustrative synthetic layer (seeded generator in scripts/) consistent with the aggregate estimates — see README")
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
    _source(fig, 0.515, 0.10, "Source compiled data :", " est. minutes incl. extra time")

    ax3 = fig.add_axes([0.72, 0.47, 0.25, 0.35])
    _chart_title(fig, 0.845, 0.855, [("Production ", False), ("vs minutes played", True)])
    charts.contribution_scatter(ax3, p)
    _source(fig, 0.845, 0.40, "Source compiled data :", " goal involvements per 90")

    _commentary(fig, 0.70, 0.345,
        "De la Fuente found his best XI by the semi-final and never touched it again — the same "
        "eleven started against France and Argentina. Around that settled spine, rotation was real: "
        "sixteen players logged 250+ minutes.", width=52)
    _commentary(fig, 0.70, 0.205,
        "The scatter shows the two kinds of contributor: high-volume producers like Oyarzabal and "
        "Yamal, and high-efficiency substitutes — Merino and Torres delivered a goal involvement "
        "roughly every hour of pitch time, the definition of bench impact.", width=52)
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
             "Percentile bars rank each player against positional peers at WC26 "
             "(estimates compiled from public reports — gold = individual award winner).",
             fontsize=8, color=GREY, ha="center")
    _footer(fig, "Awards: Golden Ball — Rodri  ·  Golden Glove — U. Simon  ·  Best Young Player — P. Cubarsi  ·  Yamal: 3.5 dribbles/game, best at WC26")
    return fig


def identity_page(d: dict) -> Figure:
    m, t = d["matches"], d["teams"]
    fig = _new_page()
    _header(fig, "Identity & Five Reasons Spain Won", active=None)

    ax1 = fig.add_axes([0.045, 0.40, 0.24, 0.42], polar=True)
    _chart_title(fig, 0.165, 0.855, [("Spain ", True), ("vs beaten rivals (avg)", False)])
    charts.radar_identity(ax1, m, t)
    _source(fig, 0.165, 0.345, "Source compiled data :", " normalised per-match profile")

    cards = [("RODRI", "Golden Ball — best player", GOLD),
             ("U. SIMON", "Golden Glove — 7 clean sheets", SPAIN_RED),
             ("P. CUBARSI", "Best Young Player — age 19", SPAIN_RED),
             ("M. OYARZABAL", "5 goals — Spain top scorer", SPAIN_RED),
             ("L. YAMAL", "3.5 dribbles per game — best at WC26", SPAIN_RED),
             ("F. TORRES", "Scored the Final winner, 106'", GOLD)]
    for i, (v, l, accent) in enumerate(cards):
        x, y = 0.335 + (i % 3) * 0.222, 0.63 - (i // 3) * 0.155
        _stat_card(fig, x, y, 0.195, 0.115, v, l, accent)

    reasons = [
        ("1. Elite defence", "One goal conceded in eight games; est. xGA never above 1.1."),
        ("2. Shared goals", "Eleven players with a goal or assist; four knockout winners from four scorers."),
        ("3. Midfield control", "55%+ possession in every match, run by Golden Ball winner Rodri."),
        ("4. Squad depth", "Oyarzabal & Torres delivered while Yamal worked back from injury."),
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


PAGES = [title_page, road_page, possession_page, structure_page, defence_page,
         press_page, squad_page, profiles_page, identity_page]
