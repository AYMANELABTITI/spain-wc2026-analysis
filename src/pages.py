"""Page builders — each function returns one finished 16:9 Figure."""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

import charts
from config import (CREAM, DARK, DEEP_RED, DPI, GOLD, GREY, LIGHT_GREY,
                    PAGE_H, PAGE_W, SERIF, SPAIN_RED, WHITE)

SECTIONS = ["The Road", "In Possession", "Out of Possession", "Identity & Players"]


# ------------------------------------------------------------------ furniture
def _new_page() -> Figure:
    return plt.figure(figsize=(PAGE_W, PAGE_H), dpi=DPI)

def _header(fig: Figure, title: str, active: int | None = None) -> None:
    """Deep-red title band + section navigation, like the reference report."""
    fig.patches.append(plt.Rectangle((0, 0.925), 1, 0.075, transform=fig.transFigure,
                                     facecolor=DEEP_RED, zorder=2))
    fig.text(0.035, 0.955, title, fontsize=19, family=SERIF, fontweight="bold",
             color=WHITE, va="center", zorder=3)
    fig.text(0.965, 0.955, "ESP · WC26", fontsize=9, color=GOLD, va="center",
             ha="right", family=SERIF, zorder=3)
    if active is not None:
        for i, s in enumerate(SECTIONS):
            fig.text(0.06 + i * 0.24, 0.895, s, fontsize=10.5, family=SERIF,
                     color=SPAIN_RED if i == active else GREY,
                     fontweight="bold" if i == active else "normal")

def _footer(fig: Figure, note: str) -> None:
    fig.patches.append(plt.Rectangle((0, 0), 1, 0.032, transform=fig.transFigure,
                                     facecolor=DEEP_RED, zorder=2))
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
def title_page(_: dict) -> Figure:
    fig = _new_page()
    grad = np.linspace(0, 1, 512)[None, :]
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(grad, aspect="auto", cmap=plt.cm.colors.LinearSegmentedColormap
              .from_list("bg", ["#B3181F", "#4A0D11"]), extent=[0, 1, 0, 1])
    ax.axis("off")
    fig.text(0.5, 0.60, "Why Spain Won The 2026 World Cup",
             fontsize=30, family=SERIF, fontweight="bold", color="#FDF6EE",
             ha="center")
    fig.text(0.5, 0.52, "A tournament told through data  ·  Canada / Mexico / USA 2026",
             fontsize=12.5, family=SERIF, color=GOLD, ha="center")
    stats = [("8", "matches"), ("7", "wins, 1 draw"), ("14 – 1", "goals for–against"),
             ("7", "clean sheets")]
    for i, (v, l) in enumerate(stats):
        x = 0.245 + i * 0.17
        fig.text(x, 0.36, v, fontsize=21, family=SERIF, fontweight="bold",
                 color="#FDF6EE", ha="center")
        fig.text(x, 0.315, l, fontsize=9.5, color="#E8B9BB", ha="center")
    fig.text(0.5, 0.14, "CREATED BY", fontsize=9, color="#E8B9BB", ha="center")
    fig.text(0.5, 0.11, "Aymane Labtiti", fontsize=11, family=SERIF,
             color="#FDF6EE", ha="center")
    fig.text(0.5, 0.05, "Built end-to-end in Python  ·  pandas + matplotlib",
             fontsize=8, color="#E8B9BB", ha="center")
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

    ax3 = fig.add_axes([0.73, 0.44, 0.24, 0.38])
    _chart_title(fig, 0.85, 0.855, [("Nine scorers", True), (" — no single hero", False)])
    charts.scorer_spread(ax3, p)
    _source(fig, 0.85, 0.385, "Source FIFA :", " goal involvements")

    _commentary(fig, 0.05, 0.33,
        "Spain suffocated opponents with the ball before beating them with it. Possession never dipped "
        "below 55% — even against France and Argentina — and peaked at 74% in the opener. That control "
        "is a defensive weapon as much as an attacking one: opponents averaged fewer than four shots per "
        "game simply because they rarely had the ball.", width=105)
    _commentary(fig, 0.05, 0.215,
        "The chance-creation engine was remarkably steady: roughly 2.2 expected goals per match, every "
        "match, regardless of opponent quality. Early wastefulness (0 goals from ~2.1 xG vs Cape Verde) "
        "corrected itself as the tournament progressed. And crucially, the load was shared: Oyarzabal's five "
        "goals led the way, but nine different players contributed goals or assists — full-back Porro and "
        "midfielder Merino chipping in from deep. Take away any one attacker and Spain still scores.", width=105)
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


def identity_page(d: dict) -> Figure:
    m, t = d["matches"], d["teams"]
    fig = _new_page()
    _header(fig, "Identity, Key Men & Five Reasons Spain Won", active=3)

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
        ("2. Shared goals", "Nine scorers, four knockout game-winners from four different players."),
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


PAGES = [title_page, road_page, possession_page, defence_page, identity_page]
