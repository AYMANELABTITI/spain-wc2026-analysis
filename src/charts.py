"""Reusable chart builders. Every function draws into an existing Axes."""

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
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


def _pitch_100(ax: Axes, face: str = "#EDF3ED") -> None:
    """Vertical 100x100 pitch canvas (attacking upward)."""
    ax.add_patch(Rectangle((0, 0), 100, 100, facecolor=face,
                           edgecolor=GREY, lw=1))
    ax.plot([0, 100], [50, 50], color=GREY, lw=0.8)
    for y0 in (0, 84):  # penalty boxes
        ax.add_patch(Rectangle((21, y0), 58, 16, fill=False, edgecolor=GREY, lw=0.8))
    ax.add_patch(Circle((50, 50), 9.15, fill=False, edgecolor=GREY, lw=0.8))
    ax.set_xlim(-2, 102)
    ax.set_ylim(-2, 102)
    ax.set_aspect("equal")
    ax.axis("off")


def draw_pitch_h(ax: Axes, line_color: str = GREY, face: str = "none") -> None:
    """Horizontal 105x68 pitch (attacking to the right)."""
    ax.add_patch(Rectangle((0, 0), 105, 68, facecolor=face,
                           edgecolor=line_color, lw=1, zorder=4, fill=face != "none"))
    ax.plot([52.5, 52.5], [0, 68], color=line_color, lw=0.8, zorder=4)
    for x0 in (0, 105 - 16.5):  # penalty areas
        ax.add_patch(Rectangle((x0, 13.85), 16.5, 40.3, fill=False,
                               edgecolor=line_color, lw=0.8, zorder=4))
    ax.add_patch(Circle((52.5, 34), 9.15, fill=False, edgecolor=line_color,
                        lw=0.8, zorder=4))
    ax.set_xlim(-2, 107)
    ax.set_ylim(-2, 70)
    ax.set_aspect("equal")
    ax.axis("off")


def formation_pitch(ax: Axes) -> None:
    """Spain's 4-2-3-1 from the Final (unchanged from the semi-final)."""
    _pitch_100(ax)
    for name, (x, y) in FINAL_XI.items():
        color = GOLD if name == "Oyarzabal" else SPAIN_RED
        ax.scatter(x, y, s=330, color=color, edgecolor=WHITE, lw=1.6, zorder=3)
        ax.text(x, y - 7.5, name, ha="center", fontsize=7.3, fontweight="bold",
                color=NAVY, zorder=3)


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


# ------------------------------------------------------------------ structure
def pass_network(ax: Axes, edges: pd.DataFrame) -> None:
    """Passing network of the Final XI: edge width = combination volume,
    node size = total pass involvement."""
    _pitch_100(ax, face="#F1F4F8")
    involvement = {}
    for _, e in edges.iterrows():
        for p in (e.p1, e.p2):
            involvement[p] = involvement.get(p, 0) + e.passes
    for _, e in edges.iterrows():
        (x1, y1), (x2, y2) = FINAL_XI[e.p1], FINAL_XI[e.p2]
        ax.plot([x1, x2], [y1, y2], color=SPAIN_RED,
                lw=0.25 + e.passes / 11, alpha=0.30 + 0.5 * e.passes / 62,
                zorder=2, solid_capstyle="round")
    top = max(involvement.values())
    for name, (x, y) in FINAL_XI.items():
        inv = involvement.get(name, 0)
        ax.scatter(x, y, s=120 + 340 * inv / top,
                   color=NAVY if inv < 0.75 * top else SPAIN_RED,
                   edgecolor=WHITE, lw=1.4, zorder=3)
        ax.text(x, y - 7.2, name, ha="center", fontsize=6.8, fontweight="bold",
                color=NAVY, zorder=3)


def team_lines(ax: Axes, lines: pd.DataFrame) -> None:
    """Average height of the defensive and midfield lines vs tournament norm."""
    draw_pitch_h(ax, face="#F1F4F8")
    d, m = lines.def_line.mean(), lines.mid_line.mean()
    for x, c, lbl, ha in [(d, WC_GREEN, f"defensive line {d:.0f} m ", "right"),
                          (m, SPAIN_RED, f" midfield line {m:.0f} m", "left")]:
        ax.plot([x, x], [1, 67], color=c, lw=2.6, zorder=5)
        ax.text(x, 70.5, lbl, ha=ha, fontsize=7.4, color=c, fontweight="bold")
    for x, lbl, ha in [(34, "avg 34 m ", "right"), (48, " avg 48 m", "left")]:
        ax.plot([x, x], [1, 67], color=GREY, lw=1.2, ls="--", zorder=5)
        ax.text(x, -5.5, lbl, ha=ha, fontsize=6.6, color=GREY)
    ax.text(41, -12, "tournament averages (est.)", ha="center", fontsize=6.2,
            color=GREY)
    ax.annotate("", xy=(d, 8), xytext=(34, 8),
                arrowprops=dict(arrowstyle="->", color=WC_GREEN, lw=1.4))
    ax.text((d + 34) / 2, 11, "+7 m", ha="center", fontsize=7.4,
            color=WC_GREEN, fontweight="bold")
    ax.set_ylim(-15, 76)


def def_line_trend(ax: Axes, lines: pd.DataFrame) -> None:
    """Defensive line height per match — discipline against the elite."""
    ax.plot(lines.match_no, lines.def_line, color=WC_GREEN, lw=2.2,
            marker="o", ms=5)
    ax.axhline(34, color=GREY, lw=1, ls="--")
    ax.text(1.0, 34.6, "tournament avg", fontsize=6.8, color=GREY)
    for m in (7, 8):  # France, Argentina
        row = lines[lines.match_no == m].iloc[0]
        ax.annotate(row.stage, (m, row.def_line), xytext=(0, -13),
                    textcoords="offset points", ha="center", fontsize=6.8,
                    color=NAVY)
    ax.set_xticks(lines.match_no)
    ax.set_xticklabels(lines.stage, fontsize=6.6)
    ax.set_ylim(30, 48)
    ax.set_ylabel("Def. line height (m, est.)", fontsize=7.6)
    ax.grid(axis="y", color=LIGHT_GREY, lw=0.8)


def donut(ax: Axes, labels: list[str], values: list[float], colors: list[str],
          center_top: str, center_sub: str) -> None:
    """Generic donut with a headline number in the hole."""
    wedges, _ = ax.pie(values, colors=colors, startangle=90,
                       counterclock=False,
                       wedgeprops=dict(width=0.40, edgecolor=WHITE, lw=1.5))
    for w, lbl, v in zip(wedges, labels, values):
        angle = np.deg2rad((w.theta1 + w.theta2) / 2)
        x, y = 1.22 * np.cos(angle), 1.22 * np.sin(angle)
        ax.text(x, y, f"{lbl}\n{v}", ha="center", va="center", fontsize=7.2,
                color=DARK, linespacing=1.3)
    ax.text(0, 0.10, center_top, ha="center", va="center", fontsize=15,
            fontweight="bold", color=NAVY)
    ax.text(0, -0.22, center_sub, ha="center", va="center", fontsize=7,
            color=GREY)


# ------------------------------------------------------------------ pressing
def pressing_heatmap(ax: Axes, zones: pd.DataFrame) -> None:
    """Zonal map of defensive actions (pressures + recoveries), est."""
    grid = zones.pivot(index="y_bin", columns="x_bin", values="actions").values
    cmap = LinearSegmentedColormap.from_list("press", ["#F5F0EE", SPAIN_RED])
    xe = np.linspace(0, 105, grid.shape[1] + 1)
    ye = np.linspace(0, 68, grid.shape[0] + 1)
    ax.pcolormesh(xe, ye, grid, cmap=cmap, alpha=0.92, zorder=1,
                  edgecolors=WHITE, lw=1.2)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            frac = grid[i, j] / grid.max()
            ax.text((xe[j] + xe[j + 1]) / 2, (ye[i] + ye[i + 1]) / 2,
                    f"{grid[i, j]}", ha="center", va="center", fontsize=6.6,
                    color=WHITE if frac > 0.55 else GREY, zorder=5,
                    fontweight="bold" if frac > 0.55 else "normal")
    draw_pitch_h(ax, line_color=NAVY)
    ax.annotate("attacking direction", xy=(76, -6.5), xytext=(30, -6.5),
                fontsize=6.8, color=GREY, annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1))
    ax.set_ylim(-10, 70)


def high_regains_map(ax: Axes, regains: pd.DataFrame) -> None:
    """Where Spain won the ball back high — and what happened next."""
    draw_pitch_h(ax, face="#F1F4F8")
    ax.plot([65, 65], [0, 68], color=GOLD, lw=1.4, ls="--", zorder=5)
    ax.text(65, 70.5, "last 40 m", ha="center", fontsize=7, color=GOLD,
            fontweight="bold")
    styles = {"regain": dict(s=26, facecolor=WHITE, edgecolor=GREY, lw=0.9),
              "shot": dict(s=48, facecolor=NAVY, edgecolor=WHITE, lw=0.8),
              "goal": dict(s=85, facecolor=SPAIN_RED, edgecolor=WHITE, lw=1.2)}
    for kind, st in styles.items():
        sub = regains[regains.outcome == kind]
        ax.scatter(sub.x, sub.y, zorder=6, **st)
    for i, (kind, lbl) in enumerate([("regain", "high regain"),
                                     ("shot", "shot within 15 s"),
                                     ("goal", "goal within 15 s")]):
        st = styles[kind]
        ax.scatter(4 + i * 38, -6.5, zorder=6, clip_on=False, **st)
        ax.text(7.5 + i * 38, -6.5, lbl, fontsize=6.8, color=DARK, va="center")
    ax.set_ylim(-10, 74)


def ppda_bars(ax: Axes, teams: pd.DataFrame) -> None:
    """PPDA (passes allowed per defensive action) — lower = fiercer press."""
    t = teams.sort_values("ppda", ascending=False).reset_index(drop=True)
    colors = [SPAIN_RED if n == "Spain" else LIGHT_GREY for n in t.team]
    ax.barh(t.team, t.ppda, color=colors, height=0.6,
            edgecolor=[GREY if c == LIGHT_GREY else "none" for c in colors],
            lw=0.6)
    for i, row in t.iterrows():
        ax.text(row.ppda + 0.15, i, f"{row.ppda}", va="center", fontsize=7.6,
                color=NAVY if row.team == "Spain" else GREY,
                fontweight="bold" if row.team == "Spain" else "normal")
    ax.set_xlim(0, t.ppda.max() + 2.2)
    ax.tick_params(axis="y", labelsize=7.6)
    ax.set_xlabel("PPDA (est.) — lower = more intense press", fontsize=7.6)


# ------------------------------------------------------------------ england
def england_route(ax: Axes, eng: pd.DataFrame) -> None:
    """England's eight matches — the run that ended one game short of Spain."""
    n = len(eng)
    ys = np.arange(n)[::-1]
    ax.vlines(0, -0.4, n - 0.6, color=LIGHT_GREY, lw=3, zorder=1)
    res_color = {"W": WC_BLUE, "D": GREY, "L": SPAIN_RED}
    for y, (_, m) in zip(ys, eng.iterrows()):
        ax.scatter(0, y, s=150 if m.result == "L" else 110,
                   color=res_color[m.result], zorder=3, edgecolor=WHITE,
                   linewidth=1.5)
        ax.text(0.09, y, f"{m.stage_short}  ·  {m.opponent}", va="center",
                fontsize=9.2, fontweight="bold", color=DARK)
        note = "" if pd.isna(m.note) else m.note
        ax.text(0.09, y - 0.31, f"{m.gf}–{m.ga}   {note}", va="center",
                fontsize=7.4, color=GREY)
    ax.set_xlim(-0.08, 1.0)
    ax.set_ylim(-0.6, n - 0.3)
    ax.axis("off")


def duo_dependency(ax: Axes) -> None:
    """Where the goals come from: England's duo vs Spain's collective."""
    rows = [("ENGLAND  ·  20 goals",
             [("Kane 6", 6, WC_BLUE), ("Bellingham 7", 7, "#3E7BD6"),
              ("others 7", 7, LIGHT_GREY)]),
            ("SPAIN  ·  14 goals",
             [("Oyarzabal 5", 5, SPAIN_RED), ("Porro 2", 2, "#E4536F"),
              ("others 7", 7, GOLD)])]
    for i, (team, parts) in enumerate(rows):
        y = 1 - i
        total = sum(v for _, v, _ in parts)
        left = 0.0
        for lbl, v, c in parts:
            w = v / total
            ax.barh(y, w, left=left, color=c, height=0.42,
                    edgecolor=WHITE, lw=1.2)
            txt_c = DARK if c in (LIGHT_GREY, GOLD) else WHITE
            ax.text(left + w / 2, y, lbl, ha="center", va="center",
                    fontsize=7.0, color=txt_c, fontweight="bold")
            left += w
        ax.text(0, y + 0.34, team, fontsize=8.2, color=NAVY,
                fontweight="bold")
    ax.text(0.65, 1.62, "65% from two men", fontsize=7.6, color=WC_BLUE,
            fontweight="bold", ha="center")
    ax.text(0.5, -0.62, "50% from two men — and 11 contributors in total",
            fontsize=7.6, color=SPAIN_RED, fontweight="bold", ha="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.9, 1.9)
    ax.axis("off")


def butterfly(ax: Axes, metrics: list[tuple[str, float, float, str, str, int]]) -> None:
    """Head-to-head diverging bars: England (left, blue) vs Spain (right, red).

    metrics rows: (label, eng_value, esp_value, eng_label, esp_label, winner)
    winner: 0 = England side highlighted, 1 = Spain side.
    """
    n = len(metrics)
    for i, (label, ev, sv, el, sl, winner) in enumerate(metrics):
        y = n - 1 - i
        scale = max(ev, sv) or 1
        ax.barh(y, -0.92 * ev / scale, color=WC_BLUE,
                alpha=1.0 if winner == 0 else 0.35, height=0.5)
        ax.barh(y, 0.92 * sv / scale, color=SPAIN_RED,
                alpha=1.0 if winner == 1 else 0.35, height=0.5)
        ax.text(0, y + 0.42, label, ha="center", fontsize=7.8, color=DARK,
                fontweight="bold")
        ax.text(-0.97, y, el, ha="right", va="center", fontsize=7.6,
                color=NAVY, fontweight="bold" if winner == 0 else "normal")
        ax.text(0.97, y, sl, ha="left", va="center", fontsize=7.6,
                color=SPAIN_RED if winner == 1 else GREY,
                fontweight="bold" if winner == 1 else "normal")
    ax.axvline(0, color=WHITE, lw=2)
    ax.text(-0.55, n - 0.25, "ENGLAND", fontsize=9, color=WC_BLUE,
            fontweight="bold", ha="center")
    ax.text(0.55, n - 0.25, "SPAIN", fontsize=9, color=SPAIN_RED,
            fontweight="bold", ha="center")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-0.6, n + 0.1)
    ax.axis("off")


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
