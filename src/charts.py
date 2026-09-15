"""Reusable chart builders. Every function draws into an existing Axes."""

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Circle, Rectangle

from config import (DARK, DEEP_RED, GOLD, GREY, LIGHT_GREY, NAVY, SPAIN_RED,
                    WC_BLUE, WC_GREEN, WHITE)

STAGE_SHORT = {
    "Group C": "GRP", "Round of 32": "R32", "Round of 16": "R16",
    "Quarter-final": "QF", "Semi-final": "SF", "Final": "FINAL",
}


def _match_labels(matches: pd.DataFrame) -> list[str]:
    return [f"{STAGE_SHORT[s]}\n{o}" for s, o in zip(matches.stage, matches.opponent)]


# ------------------------------------------------------------------ page 2
def road_to_glory(ax: Axes, matches: pd.DataFrame) -> None:
    """Vertical stepper of the eight matches with scores."""
    n = len(matches)
    ys = np.arange(n)[::-1]
    ax.vlines(0, -0.4, n - 0.6, color=LIGHT_GREY, lw=3, zorder=1)
    for y, (_, m) in zip(ys, matches.iterrows()):
        is_final = m.stage == "Final"
        color = GOLD if is_final else (GREY if m.gf == m.ga else SPAIN_RED)
        ax.scatter(0, y, s=170 if is_final else 110, color=color, zorder=3,
                   edgecolor=WHITE, linewidth=1.5)
        ax.text(0.09, y, f"{STAGE_SHORT[m.stage]}  ·  {m.opponent}",
                va="center", fontsize=9.5, fontweight="bold", color=DARK)
        score = f"{m.gf}–{m.ga}" + ("  (aet)" if is_final else "")
        ax.text(0.09, y - 0.31, f"{score}   {'' if pd.isna(m.scorers) else m.scorers}",
                va="center", fontsize=7.6, color=GREY)
    ax.set_xlim(-0.08, 1.0)
    ax.set_ylim(-0.6, n - 0.3)
    ax.axis("off")


def cumulative_goals(ax: Axes, matches: pd.DataFrame) -> None:
    """Cumulative goals for vs against across the tournament."""
    x = matches.match_no
    ax.plot(x, matches.gf.cumsum(), color=SPAIN_RED, lw=2.5, marker="o", ms=5,
            label="Goals scored (cum.)")
    ax.plot(x, matches.ga.cumsum(), color=GREY, lw=2.5, marker="o", ms=5,
            label="Goals conceded (cum.)")
    ax.fill_between(x, matches.ga.cumsum(), matches.gf.cumsum(),
                    color=SPAIN_RED, alpha=0.08)
    ax.annotate("14", (8, 14), xytext=(7.55, 14.3), fontsize=11,
                fontweight="bold", color=SPAIN_RED)
    ax.annotate("1", (8, 1), xytext=(7.7, 1.6), fontsize=11,
                fontweight="bold", color=GREY)
    ax.set_xticks(x)
    ax.set_xticklabels([STAGE_SHORT[s] for s in matches.stage], fontsize=7.5)
    ax.grid(axis="y", color=LIGHT_GREY, lw=0.8)
    ax.legend(frameon=False, fontsize=8, loc="upper left")


def goal_diff_scatter(ax: Axes, teams: pd.DataFrame) -> None:
    """Attack vs defence map: goals scored against goals conceded per match."""
    for _, t in teams.iterrows():
        is_spain = t.team == "Spain"
        gf90, ga90 = t.gf / t.matches, t.ga / t.matches
        ax.scatter(gf90, ga90, s=160 if is_spain else 90,
                   color=SPAIN_RED if is_spain else GREY, zorder=3,
                   edgecolor=WHITE, linewidth=1.2)
        ax.annotate(t.team, (gf90, ga90), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8,
                    fontweight="bold" if is_spain else "normal",
                    color=DEEP_RED if is_spain else DARK)
    ax.invert_yaxis()  # up = better defence
    ax.set_xlabel("Goals scored per match", fontsize=8.5)
    ax.set_ylabel("Goals conceded per match  (inverted)", fontsize=8.5)
    ax.grid(color=LIGHT_GREY, lw=0.8)


# ------------------------------------------------------------------ page 3
def possession_bars(ax: Axes, matches: pd.DataFrame) -> None:
    x = matches.match_no
    colors = [GOLD if s == "Final" else SPAIN_RED for s in matches.stage]
    ax.bar(x, matches.possession, color=colors, width=0.62)
    avg = matches.possession.mean()
    ax.axhline(avg, color=DARK, lw=1, ls="--")
    ax.set_xlim(0.35, 9.55)
    ax.text(8.8, avg - 1, f"avg\n{avg:.0f}%", fontsize=7.5, color=DARK, va="top")
    for xi, v in zip(x, matches.possession):
        ax.text(xi, v + 1.2, f"{v}", ha="center", fontsize=7.5, color=GREY)
    ax.set_xticks(x)
    ax.set_xticklabels([STAGE_SHORT[s] for s in matches.stage], fontsize=7.5)
    ax.set_ylim(0, 85)
    ax.set_ylabel("Possession %", fontsize=8.5)


def xg_vs_goals(ax: Axes, matches: pd.DataFrame) -> None:
    """Chance creation (xG) vs actual goals, match by match."""
    x = matches.match_no
    w = 0.38
    ax.bar(x - w / 2, matches.xg_for, width=w, color=LIGHT_GREY,
           edgecolor=GREY, lw=0.6, label="xG created (est.)")
    ax.bar(x + w / 2, matches.gf, width=w, color=SPAIN_RED, label="Goals")
    ax.set_xticks(x)
    ax.set_xticklabels([STAGE_SHORT[s] for s in matches.stage], fontsize=7.5)
    ax.grid(axis="y", color=LIGHT_GREY, lw=0.8)
    ax.legend(frameon=False, fontsize=8, loc="upper right")


def scorer_spread(ax: Axes, players: pd.DataFrame) -> None:
    """Horizontal bars of goal involvements — the 'no single hero' story."""
    p = players[players.goals + players.assists > 0].sort_values(
        ["goals", "assists"]).reset_index(drop=True)
    ax.barh(p.player, p.goals, color=SPAIN_RED, label="Goals", height=0.55)
    ax.barh(p.player, p.assists, left=p.goals, color=GOLD, label="Assists",
            height=0.55)
    for i, row in p.iterrows():
        ax.text(row.goals + row.assists + 0.12, i, str(row.goals + row.assists),
                va="center", fontsize=7.2, color=GREY)
    ax.set_xlim(0, p.goals.max() + p.assists.max() + 1)
    ax.tick_params(axis="y", labelsize=7.2)
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")


# ------------------------------------------------------------------ page 4
def xga_timeline(ax: Axes, matches: pd.DataFrame) -> None:
    x = matches.match_no
    ax.plot(x, matches.xg_against, color=GREY, lw=2, marker="o", ms=5,
            label="xG conceded (est.)")
    ax.scatter(x, matches.ga, color=SPAIN_RED, s=70, zorder=3,
               label="Goals conceded")
    ax.annotate("only breach:\nBelgium (QF)", (6, 1), xytext=(4.15, 1.28),
                fontsize=8, color=DEEP_RED,
                arrowprops=dict(arrowstyle="-", color=DEEP_RED, lw=0.8))
    ax.set_xticks(x)
    ax.set_xticklabels([STAGE_SHORT[s] for s in matches.stage], fontsize=7.5)
    ax.set_ylim(-0.1, 1.75)
    ax.grid(axis="y", color=LIGHT_GREY, lw=0.8)
    ax.legend(frameon=False, fontsize=8, loc="upper left")


def conceded_ranking(ax: Axes, teams: pd.DataFrame) -> None:
    t = teams.sort_values("ga", ascending=False).reset_index(drop=True)
    colors = [SPAIN_RED if n == "Spain" else LIGHT_GREY for n in t.team]
    ax.barh(t.team, t.ga, color=colors, height=0.6,
            edgecolor=[GREY if c == LIGHT_GREY else "none" for c in colors], lw=0.6)
    for i, row in t.iterrows():
        ax.text(row.ga + 0.15, i, f"{row.ga}  ({row.matches} gms)",
                va="center", fontsize=8,
                color=DEEP_RED if row.team == "Spain" else GREY,
                fontweight="bold" if row.team == "Spain" else "normal")
    ax.set_xlim(0, t.ga.max() + 2.4)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)


def final_dominance(ax: Axes) -> None:
    """The final in one picture: 20-3 shots, 8-1 on target."""
    cats = ["Shots", "Shots on\ntarget", "xG (est.)"]
    spain = [20, 8, 2.4]
    argentina = [3, 1, 0.2]
    y = np.arange(len(cats))[::-1]
    for yi, s, a in zip(y, spain, argentina):
        total = s + a
        ax.barh(yi, s / total, color=SPAIN_RED, height=0.52)
        ax.barh(yi, a / total, left=s / total, color=GREY, height=0.52)
        ax.text(0.02, yi, f"{s}", va="center", color=WHITE, fontsize=10,
                fontweight="bold")
        ax.text(0.98, yi, f"{a}", va="center", ha="right", color=WHITE,
                fontsize=10, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=8.5)
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.text(0.02, len(cats) - 0.28, "SPAIN", color=SPAIN_RED, fontsize=9,
            fontweight="bold")
    ax.text(0.98, len(cats) - 0.28, "ARGENTINA", color=GREY, fontsize=9,
            fontweight="bold", ha="right")
    for s in ax.spines.values():
        s.set_visible(False)


# ------------------------------------------------------------------ page 5
def radar_identity(ax: Axes, matches: pd.DataFrame, teams: pd.DataFrame) -> None:
    """Team identity radar: Spain vs the average of its beaten rivals."""
    rivals = teams[teams.team != "Spain"]
    axes_labels = ["Attack\n(goals/gm)", "Chance\ncreation", "Possession",
                   "Defence\n(inv. GA/gm)", "Efficiency\n(G/xG)"]

    def profile(gf, xg, poss, ga, gms):
        return [gf / gms / 2.5, xg / gms / 2.5, poss / 75,
                1 - (ga / gms / 1.6), (gf / xg) / 1.2]

    sp = profile(14, 17.3, matches.possession.mean(), 1, 8)
    rv = profile(rivals.gf.sum(), rivals.xg_for.sum(),
                 rivals.possession_avg.mean(), rivals.ga.sum(),
                 rivals.matches.sum())
    ang = np.linspace(0, 2 * np.pi, len(axes_labels), endpoint=False).tolist()
    sp, rv, ang2 = sp + sp[:1], rv + rv[:1], ang + ang[:1]
    ax.plot(ang2, rv, color=GREY, lw=1.6)
    ax.fill(ang2, rv, color=GREY, alpha=0.18)
    ax.plot(ang2, sp, color=SPAIN_RED, lw=2.2)
    ax.fill(ang2, sp, color=SPAIN_RED, alpha=0.28)
    ax.set_xticks(ang)
    ax.set_xticklabels(axes_labels, fontsize=7.4)
    ax.set_yticklabels([])
    ax.set_ylim(0, 1.05)
    ax.grid(color=LIGHT_GREY)


# ------------------------------------------------------------------ players
FINAL_XI = {  # 4-2-3-1 vs Argentina — (x, y) on a 100x100 vertical half-ish pitch
    "Simon": (50, 6), "Porro": (85, 24), "Cubarsi": (63, 20),
    "Laporte": (37, 20), "Cucurella": (15, 24), "Rodri": (60, 42),
    "F. Ruiz": (40, 42), "Yamal": (84, 64), "Olmo": (50, 62),
    "Baena": (16, 64), "Oyarzabal": (50, 84),
}


def formation_pitch(ax: Axes) -> None:
    """Spain's 4-2-3-1 from the Final (unchanged from the semi-final)."""
    ax.add_patch(Rectangle((0, 0), 100, 100, facecolor="#EDF3ED",
                           edgecolor=GREY, lw=1))
    ax.plot([0, 100], [50, 50], color=GREY, lw=0.8)
    for y0 in (0, 84):  # penalty boxes
        ax.add_patch(Rectangle((21, y0), 58, 16, fill=False, edgecolor=GREY, lw=0.8))
    ax.add_patch(Circle((50, 50), 9.15, fill=False, edgecolor=GREY, lw=0.8))
    for name, (x, y) in FINAL_XI.items():
        color = GOLD if name == "Oyarzabal" else SPAIN_RED
        ax.scatter(x, y, s=330, color=color, edgecolor=WHITE, lw=1.6, zorder=3)
        ax.text(x, y - 7.5, name, ha="center", fontsize=7.3, fontweight="bold",
                color=NAVY, zorder=3)
    ax.set_xlim(-2, 102)
    ax.set_ylim(-2, 102)
    ax.set_aspect("equal")
    ax.axis("off")


def minutes_bars(ax: Axes, players: pd.DataFrame) -> None:
    """Squad usage: minutes played (est.), starters of the Final highlighted."""
    p = players.sort_values("minutes").reset_index(drop=True)
    colors = [SPAIN_RED if s else LIGHT_GREY for s in p.starter_final]
    edges = ["none" if s else GREY for s in p.starter_final]
    ax.barh(p.player, p.minutes, color=colors, edgecolor=edges, lw=0.6, height=0.62)
    ax.axvline(750, color=GOLD, lw=1.2, ls="--")
    ax.text(738, 1.0, "every minute\n(750')", fontsize=6.8, color=GOLD,
            ha="right", va="center")
    for i, row in p.iterrows():
        ax.text(row.minutes + 10, i, f"{row.minutes}'", va="center", fontsize=6.8,
                color=GREY)
    ax.set_xlim(0, 860)
    ax.tick_params(axis="y", labelsize=7.4)
    ax.set_xticks([0, 250, 500, 750])


def contribution_scatter(ax: Axes, players: pd.DataFrame) -> None:
    """Goal involvements per 90 vs minutes — who produced, who carried."""
    p = players[players.minutes > 0].copy()
    p["gi90"] = (p.goals + p.assists) / p.minutes * 90
    for _, r in p.iterrows():
        big = r.goals + r.assists >= 3
        ax.scatter(r.minutes, r.gi90, s=110 if big else 55,
                   color=SPAIN_RED if big else GREY, zorder=3,
                   edgecolor=WHITE, lw=1)
        if big or r.player in ("Ferran Torres", "Rodri"):
            ax.annotate(r.player, (r.minutes, r.gi90), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=7.2,
                        fontweight="bold" if big else "normal", color=NAVY)
    ax.set_xlabel("Minutes played (est.)", fontsize=8.5)
    ax.set_ylabel("Goals + assists per 90", fontsize=8.5)
    ax.grid(color=LIGHT_GREY, lw=0.8)
    ax.set_ylim(-0.06, 1.2)


def profile_panel(ax: Axes, prof: pd.DataFrame, accent: str) -> None:
    """One player's card: 3 percentile bars vs tournament peers (est.)."""
    rows = prof.reset_index(drop=True)
    n = len(rows)
    for i, r in rows.iterrows():
        y = n - 1 - i
        ax.barh(y, 100, color=LIGHT_GREY, height=0.34, zorder=1)
        ax.barh(y, r.percentile, color=accent, height=0.34, zorder=2)
        ax.text(0, y + 0.42, r.metric, fontsize=7.6, color=DARK, va="center")
        ax.text(100, y + 0.42, r.value_label, fontsize=7.4, color=GREY,
                va="center", ha="right")
        ax.text(r.percentile - 2, y, f"{r.percentile}", fontsize=6.6,
                color=WHITE, va="center", ha="right", fontweight="bold", zorder=3)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, n - 0.1)
    ax.axis("off")
