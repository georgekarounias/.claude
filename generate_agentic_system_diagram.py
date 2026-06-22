"""
generate_agentic_system_diagram.py
Generates a PNG diagram of the full agentic system (Claude + Copilot agents,
skills, coordination artifacts, and execution flow).

Run:
    python generate_agentic_system_diagram.py
Output:
    agentic-system-diagram.png
"""

from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

OUTPUT = Path(__file__).with_name("agentic-system-diagram.png")

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY       = "#0F172A"
SLATE      = "#1E293B"
SLATE_MID  = "#334155"
MUTED      = "#64748B"
CREAM      = "#F8FAFC"
WHITE      = "#FFFFFF"

TEAL       = "#0D9488"
TEAL_LIGHT = "#CCFBF1"
AMBER      = "#D97706"
AMBER_LIGHT= "#FEF3C7"
ROSE       = "#BE185D"
ROSE_LIGHT = "#FBCFE8"
VIOLET     = "#7C3AED"
VIOLET_LIGHT="#EDE9FE"
BLUE       = "#1D4ED8"
BLUE_LIGHT = "#DBEAFE"
GREEN      = "#15803D"
GREEN_LIGHT= "#DCFCE7"
SLATE_LIGHT= "#E2E8F0"


# ── Helpers ────────────────────────────────────────────────────────────────────

def rounded_box(ax, x, y, w, h, color, label, label_color=NAVY,
                fontsize=8.5, bold=False, radius=0.015, alpha=1.0,
                sublabel=None, sublabel_color=MUTED):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=0,
        facecolor=color,
        alpha=alpha,
        zorder=3,
    )
    ax.add_patch(box)
    cy = y + h / 2 + (0.008 if sublabel else 0)
    ax.text(
        x + w / 2, cy, label,
        ha="center", va="center",
        fontsize=fontsize, fontweight="bold" if bold else "normal",
        color=label_color, zorder=4,
        wrap=True,
    )
    if sublabel:
        ax.text(
            x + w / 2, y + h / 2 - 0.018, sublabel,
            ha="center", va="center",
            fontsize=6.5, color=sublabel_color, zorder=4,
        )
    return box


def arrow(ax, x0, y0, x1, y1, color=MUTED, lw=1.2, style="->"):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle=style,
            color=color,
            lw=lw,
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=5,
    )


def section_label(ax, x, y, text, color=MUTED):
    ax.text(x, y, text, fontsize=7, color=color, va="center",
            fontstyle="italic", zorder=4)


# ── Main diagram ───────────────────────────────────────────────────────────────

def build():
    fig, ax = plt.subplots(figsize=(18, 11))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # ── Title bar ──────────────────────────────────────────────────────────────
    title_bg = FancyBboxPatch(
        (0, 0.935), 1, 0.065,
        boxstyle="square,pad=0",
        facecolor=NAVY, linewidth=0, zorder=2,
    )
    ax.add_patch(title_bg)
    # Teal accent strip
    ax.add_patch(FancyBboxPatch((0, 0.935), 1, 0.007,
                                boxstyle="square,pad=0",
                                facecolor=TEAL, linewidth=0, zorder=3))
    ax.text(0.5, 0.968, "Agentic System — Agent & Skill Architecture",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=WHITE, zorder=4)
    ax.text(0.5, 0.951, "Claude (.claude/agents/)  ·  Copilot (.github/agents/)  ·  Shared Skills (.claude/skills/)",
            ha="center", va="center", fontsize=8, color=SLATE_LIGHT, zorder=4)

    # ── USER ──────────────────────────────────────────────────────────────────
    rounded_box(ax, 0.41, 0.874, 0.18, 0.042,
                TEAL, "User / Developer", label_color=WHITE,
                fontsize=9, bold=True, radius=0.012)

    # ── ORCHESTRATION LAYER ───────────────────────────────────────────────────
    section_label(ax, 0.01, 0.833, "① ORCHESTRATION")

    rounded_box(ax, 0.12, 0.806, 0.25, 0.044,
                NAVY, "orchestrator", label_color=WHITE,
                sublabel="autonomous end-to-end driver (agent tool)",
                fontsize=8.5, bold=True, radius=0.01)

    rounded_box(ax, 0.63, 0.806, 0.25, 0.044,
                SLATE_MID, "task-router", label_color=WHITE,
                sublabel="planning only → writes task-routing.md",
                fontsize=8.5, bold=True, radius=0.01)

    ax.text(0.5, 0.825, "or", ha="center", va="center",
            fontsize=9, color=MUTED, fontstyle="italic")

    # Arrows user → orch/router
    arrow(ax, 0.50, 0.874, 0.245, 0.851, color=TEAL, lw=1.5)
    arrow(ax, 0.50, 0.874, 0.755, 0.851, color=TEAL, lw=1.5)

    # ── INTAKE / ARCHITECTURE ─────────────────────────────────────────────────
    section_label(ax, 0.01, 0.755, "② SEQUENTIAL GATES  (must run in order when applicable)")

    gates = [
        (0.02,  "feature-intake-reviewer",     AMBER_LIGHT,  AMBER,  "scope · cost-band · approval"),
        (0.255, "react-dotnet-solution-architect", VIOLET_LIGHT, VIOLET, "arch plan · ADR · API contracts"),
        (0.49,  "dotnet-efcore-schema-designer",   BLUE_LIGHT,   BLUE,   "entity design · SQL DDL"),
        (0.725, "dotnet-efcore-migrations",         GREEN_LIGHT,  GREEN,  "migration generation"),
    ]

    gate_centers = []
    for gx, glabel, gbg, gfg, gsub in gates:
        rounded_box(ax, gx, 0.718, 0.215, 0.055,
                    gbg, glabel, label_color=gfg,
                    sublabel=gsub, sublabel_color=gfg,
                    fontsize=7.5, bold=True, radius=0.009)
        gate_centers.append(gx + 0.1075)

    # Arrows between gates
    for i in range(len(gate_centers) - 1):
        arrow(ax, gate_centers[i] + 0.1075, 0.745,
              gate_centers[i + 1] - 0.1075, 0.745,
              color=AMBER, lw=1.0)

    # Arrow orchestrator → gates
    arrow(ax, 0.245, 0.806, gate_centers[0], 0.773, color=NAVY, lw=1.2)

    # ── PARALLEL IMPLEMENTATION ───────────────────────────────────────────────
    section_label(ax, 0.01, 0.665, "③ PARALLEL IMPLEMENTATION  (run simultaneously after architecture)")

    impl_agents = [
        (0.02,  "dotnet-backend-developer",    TEAL_LIGHT,   TEAL,   ".NET Web API"),
        (0.265, "react-frontend-developer",    ROSE_LIGHT,   ROSE,   "React + TypeScript"),
        (0.51,  "python-fastapi-developer",    AMBER_LIGHT,  AMBER,  "Python FastAPI"),
        (0.755, "react-dotnet-refactor-specialist", SLATE_LIGHT, SLATE_MID, "refactor (no new features)"),
    ]

    impl_centers = []
    for ix, ilabel, ibg, ifg, isub in impl_agents:
        rounded_box(ax, ix, 0.630, 0.215, 0.050,
                    ibg, ilabel, label_color=ifg,
                    sublabel=isub, sublabel_color=ifg,
                    fontsize=7.5, bold=True, radius=0.009)
        impl_centers.append(ix + 0.1075)

    # Bracket indicating parallel
    ax.annotate("", xy=(0.975, 0.690), xytext=(0.015, 0.690),
                arrowprops=dict(arrowstyle="-", color=TEAL, lw=1.2,
                                connectionstyle="arc3,rad=0"))
    arrow(ax, gate_centers[1], 0.718, impl_centers[0], 0.680, color=VIOLET, lw=1.2)

    # ── PARALLEL TESTING ──────────────────────────────────────────────────────
    section_label(ax, 0.01, 0.590, "④ PARALLEL TESTING")

    testers = [
        (0.02,  "dotnet-backend-unit-tester",  TEAL_LIGHT,  TEAL,  ".NET xUnit"),
        (0.36,  "react-frontend-unit-tester",  ROSE_LIGHT,  ROSE,  "Vitest / RTL"),
        (0.70,  "python-fastapi-unit-tester",  AMBER_LIGHT, AMBER, "pytest + httpx"),
    ]

    tester_centers = []
    for tx, tlabel, tbg, tfg, tsub in testers:
        rounded_box(ax, tx, 0.557, 0.27, 0.048,
                    tbg, tlabel, label_color=tfg,
                    sublabel=tsub, sublabel_color=tfg,
                    fontsize=7.5, bold=True, radius=0.009)
        tester_centers.append(tx + 0.135)

    arrow(ax, impl_centers[0], 0.630, tester_centers[0], 0.605, color=TEAL, lw=1.2)

    # ── PARALLEL REVIEW ───────────────────────────────────────────────────────
    section_label(ax, 0.01, 0.513, "⑤ PARALLEL REVIEW  (read-only, writes review-findings.md)")

    reviewers = [
        (0.02,  "dotnet-backend-code-reviewer",  TEAL_LIGHT,  TEAL,  ".NET backend"),
        (0.36,  "react-frontend-code-reviewer",  ROSE_LIGHT,  ROSE,  "React frontend"),
        (0.70,  "python-fastapi-code-reviewer",  AMBER_LIGHT, AMBER, "FastAPI backend"),
    ]

    reviewer_centers = []
    for rx, rlabel, rbg, rfg, rsub in reviewers:
        rounded_box(ax, rx, 0.480, 0.27, 0.048,
                    rbg, rlabel, label_color=rfg,
                    sublabel=rsub, sublabel_color=rfg,
                    fontsize=7.5, bold=True, radius=0.009)
        reviewer_centers.append(rx + 0.135)

    for tc, rc in zip(tester_centers, reviewer_centers):
        arrow(ax, tc, 0.557, rc, 0.528, color=MUTED, lw=1.1)

    # ── SKILLS ────────────────────────────────────────────────────────────────
    section_label(ax, 0.01, 0.433, "SKILLS  (.claude/skills/ — shared by Claude & Copilot, loaded on demand)")

    skills = [
        "dotnet-backend-architecture-best-practices",
        "dotnet-csharp-standards",
        "dotnet-efcore-schema-design",
        "dotnet-efcore-migration-best-practices",
        "dotnet-webapi-security-best-practices",
        "dotnet-redis-caching-best-practices",
        "dotnet-rabbitmq-message-queue-best-practices",
        "react-component-best-practices",
        "react-state-management-best-practices",
        "react-tailwind-ui-best-practices",
        "react-typescript-standards",
        "react-browser-api-best-practices",
        "react-web-security-best-practices",
        "react-dotnet-unit-testing-best-practices",
        "python-standards",
        "python-fastapi-best-practices",
        "python-fastapi-testing-best-practices",
        "agent-handoff-evidence-best-practices",
    ]

    skill_w = 0.215
    skill_h = 0.036
    skill_gap_x = 0.008
    skill_gap_y = 0.006
    cols = 4
    skill_x_start = 0.015
    skill_y_start = 0.395

    for i, skill in enumerate(skills):
        col = i % cols
        row = i // cols
        sx = skill_x_start + col * (skill_w + skill_gap_x)
        sy = skill_y_start - row * (skill_h + skill_gap_y)
        bg = TEAL_LIGHT if "dotnet" in skill else \
             ROSE_LIGHT if "react" in skill else \
             AMBER_LIGHT if "python" in skill else \
             SLATE_LIGHT
        fg = TEAL if "dotnet" in skill else \
             ROSE if "react" in skill else \
             AMBER if "python" in skill else \
             SLATE_MID
        rounded_box(ax, sx, sy, skill_w, skill_h,
                    bg, skill, label_color=fg,
                    fontsize=6.8, radius=0.007)

    # ── DURABLE ARTIFACTS ─────────────────────────────────────────────────────
    section_label(ax, 0.01, 0.112, "DURABLE ARTIFACTS  (written at repo root, persist across agents)")

    artifacts = [
        ("feature-intake.md",       AMBER_LIGHT, AMBER),
        ("task-routing.md",         SLATE_LIGHT, SLATE_MID),
        ("architecture-plan.md",    VIOLET_LIGHT, VIOLET),
        ("task-handoff.md",         BLUE_LIGHT,  BLUE),
        ("review-findings.md",      ROSE_LIGHT,  ROSE),
        ("test-report.md",          GREEN_LIGHT, GREEN),
        ("orchestration-summary.md",TEAL_LIGHT,  TEAL),
    ]

    art_w = (0.97 - 0.015 - 6 * 0.008) / 7
    for i, (alabel, abg, afg) in enumerate(artifacts):
        ax = plt.gca()
        ax_x = 0.015 + i * (art_w + 0.008)
        rounded_box(ax, ax_x, 0.078, art_w, 0.040,
                    abg, alabel, label_color=afg,
                    fontsize=7.2, bold=True, radius=0.008)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(facecolor=TEAL_LIGHT,  edgecolor=TEAL,      label=".NET stack"),
        mpatches.Patch(facecolor=ROSE_LIGHT,  edgecolor=ROSE,      label="React stack"),
        mpatches.Patch(facecolor=AMBER_LIGHT, edgecolor=AMBER,     label="Python / FastAPI stack"),
        mpatches.Patch(facecolor=VIOLET_LIGHT,edgecolor=VIOLET,    label="Architecture"),
        mpatches.Patch(facecolor=SLATE_LIGHT, edgecolor=SLATE_MID, label="Cross-stack / coordination"),
        mpatches.Patch(facecolor=NAVY,        edgecolor=NAVY,      label="Orchestration"),
    ]
    plt.legend(
        handles=legend_items,
        loc="lower right",
        bbox_to_anchor=(0.995, 0.01),
        fontsize=7.5,
        framealpha=0.9,
        edgecolor=SLATE_LIGHT,
        ncol=2,
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    ax = plt.gca()
    ax.text(0.015, 0.028,
            "Claude agents → .claude/agents/*.md  ·  Copilot agents → .github/agents/*.agent.md  ·  Skills → .claude/skills/<name>/SKILL.md",
            fontsize=6.8, color=MUTED, va="center")
    ax.text(0.985, 0.028,
            "generated by generate_agentic_system_diagram.py",
            fontsize=6.8, color=MUTED, va="center", ha="right")

    # ── Save ──────────────────────────────────────────────────────────────────
    plt.tight_layout(pad=0)
    plt.savefig(OUTPUT, dpi=180, bbox_inches="tight",
                facecolor=CREAM, edgecolor="none")
    plt.close()
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    build()
