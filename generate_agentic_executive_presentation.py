from pathlib import Path

from generate_agentic_approach_presentation import (
    AMBER,
    CREAM,
    MUTED,
    NAVY,
    PALE_AMBER,
    PALE_ROSE,
    PALE_SLATE,
    PALE_TEAL,
    ROSE,
    SLATE,
    SLIDE_HEIGHT,
    SLIDE_WIDTH,
    TEAL,
    TEAL_DARK,
    WHITE,
    FONT_HEAD,
    Presentation,
    RGBColor,
    Inches,
    MSO_AUTO_SHAPE_TYPE,
    PP_ALIGN,
    add_background,
    add_brand_badge,
    add_card,
    add_chip,
    add_footer,
    add_paragraphs,
    add_speaker_notes,
    add_textbox,
    set_table_cell,
)


EXECUTIVE_OUTPUT_FILE = Path(__file__).with_name("agentic-approach-executive-brief.pptx")


def build_exec_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_brand_badge(slide, dark=True)
    accent = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(0), Inches(0), Inches(13.333), Inches(0.22)
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = TEAL
    accent.line.fill.background()
    add_chip(slide, 0.6, 0.55, 1.95, "EXECUTIVE BRIEF", PALE_TEAL, TEAL_DARK)
    add_textbox(
        slide,
        0.62,
        1.22,
        8.9,
        1.3,
        "Why this agentic workflow creates real operating value on non-trivial delivery work",
        font_size=28,
        font_name=FONT_HEAD,
        color=WHITE,
        bold=True,
    )
    add_textbox(
        slide,
        0.66,
        2.55,
        8.0,
        0.95,
        "Executive version: less implementation detail, stronger emphasis on cost control, quality control, and repeatable delivery.",
        font_size=18,
        color=RGBColor(226, 232, 240),
    )
    add_card(
        slide,
        0.66,
        4.35,
        3.85,
        1.5,
        WHITE,
        "Cost control",
        ["Stop fuzzy requests before they become expensive multi-step execution chains."],
        title_color=NAVY,
    )
    add_card(
        slide,
        4.75,
        4.35,
        3.85,
        1.5,
        PALE_TEAL,
        "Execution control",
        ["Route work to the minimum valid specialist chain instead of relying on a single broad prompt."],
        title_color=TEAL_DARK,
    )
    add_card(
        slide,
        8.84,
        4.35,
        3.85,
        1.5,
        PALE_AMBER,
        "Quality control",
        ["Separate implementation from testing, review, and durable evidence so results are easier to trust."],
        title_color=AMBER,
    )
    add_footer(slide, "Executive deck generated from the current .claude workflow definitions on 2026-06-20.", dark=True)
    add_speaker_notes(
        slide,
        "Frame the system in leadership terms: this is a control model for AI-assisted delivery.",
        [
            "Open with the idea that the workflow is designed to reduce waste, not simply increase agent activity.",
            "Use the three cards to summarize the ROI story: cost control at the start, execution control in the middle, and quality control at the end.",
            "Tell the audience this version intentionally compresses technical detail into operating-value language.",
        ],
    )


def build_exec_problem_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, CREAM)
    add_brand_badge(slide)
    add_chip(slide, 0.55, 0.45, 1.7, "BUSINESS PROBLEM", PALE_SLATE, NAVY)
    add_textbox(slide, 0.55, 0.95, 8.2, 0.72, "What leaders actually pay for without this structure", font_size=26, font_name=FONT_HEAD, color=NAVY, bold=True)
    add_card(
        slide,
        0.65,
        1.95,
        5.95,
        4.9,
        WHITE,
        "Hidden costs of chat-only execution",
        [
            "- unclear requests convert into implementation work too early",
            "- one generalist workflow makes planning, coding, testing, and review decisions at once",
            "- handoffs restart from scratch because context lives in the conversation rather than in artifacts",
            "- quality checks become inconsistent when delivery pressure rises",
        ],
        title_color=NAVY,
    )
    add_card(
        slide,
        6.78,
        1.95,
        5.9,
        4.9,
        PALE_TEAL,
        "Operational effect",
        [
            "- more rework after assumptions fail",
            "- harder budget discipline on ambiguous tasks",
            "- lower confidence in whether the output was properly validated",
            "- slower recovery when work needs to be resumed by another person or agent",
        ],
        title_color=TEAL_DARK,
    )
    add_footer(slide, "The workflow exists to reduce these operational costs, not because multi-agent execution is fashionable.")
    add_speaker_notes(
        slide,
        "Tie the workflow directly to familiar delivery waste.",
        [
            "This slide is about rework, inconsistent validation, and restart cost rather than about model architecture.",
            "Make clear that the pain is economic: teams lose time both when they start the wrong work and when they cannot trust or resume what was done.",
            "That is the business justification for adding an intake gate, routing logic, and durable evidence.",
        ],
    )


def build_exec_operating_model_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_brand_badge(slide, dark=True)
    add_chip(slide, 0.58, 0.48, 1.95, "OPERATING MODEL", PALE_TEAL, TEAL_DARK)
    add_textbox(slide, 0.6, 0.98, 7.8, 0.72, "The workflow in plain language", font_size=26, font_name=FONT_HEAD, color=WHITE, bold=True)
    steps = [
        ("1. Approve the right work", "Clarify scope, estimate complexity, and stop unclear work before spend rises.", PALE_TEAL, TEAL_DARK),
        ("2. Route to the right specialist", "Send the task to the minimum valid combination of architecture, build, and quality roles.", WHITE, NAVY),
        ("3. Validate independently", "Use dedicated testing and read-only review steps rather than trusting self-validation.", PALE_ROSE, ROSE),
        ("4. Preserve evidence", "Write down the route, decisions, results, and open risks so work can be resumed without rediscovery.", PALE_AMBER, AMBER),
    ]
    left = 0.72
    for title, body, fill, title_color in steps:
        add_card(slide, left, 2.2, 3.0, 3.15, fill, title, [body], title_color=title_color)
        left += 3.08
    add_textbox(slide, 0.64, 5.95, 12.0, 0.55, "The key design choice is conditional depth: the workflow becomes more sophisticated only when the task is ambiguous, risky, or cross-functional.", font_size=17, color=RGBColor(226, 232, 240))
    add_footer(slide, "This model is intentionally selective. It is designed to expand on non-trivial work and stay light on simple work.", dark=True)
    add_speaker_notes(
        slide,
        "Explain the flow as a sequence of business controls.",
        [
            "The first control is whether the work should even proceed in its current form.",
            "The second is specialist fit: route only to the roles the task genuinely needs.",
            "The final controls are independent validation and durable evidence, which improve trust and resumability.",
        ],
    )


def build_exec_roi_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, CREAM)
    add_brand_badge(slide)
    add_chip(slide, 0.55, 0.45, 1.7, "ROI DRIVERS", PALE_SLATE, NAVY)
    add_textbox(slide, 0.55, 0.95, 7.8, 0.72, "Where the measurable value comes from", font_size=26, font_name=FONT_HEAD, color=NAVY, bold=True)
    cards = [
        (0.65, 1.95, PALE_TEAL, "Lower rework", ["Bad assumptions surface earlier, before a long implementation chain is already underway."], TEAL_DARK),
        (4.37, 1.95, WHITE, "Faster restarts", ["Artifacts reduce the cost of resuming work across sessions, people, or agents."], NAVY),
        (8.09, 1.95, PALE_AMBER, "Better quality signal", ["Separate testing and review roles produce a cleaner signal on whether work is ready."], AMBER),
        (0.65, 4.15, WHITE, "Better budget discipline", ["Cost-band estimates and approval gates make it easier to stop or split expensive work."], NAVY),
        (4.37, 4.15, PALE_ROSE, "Scalable expertise", ["Reusable skill packs let specialists apply shared standards without repeating prompt engineering every time."], ROSE),
        (8.09, 4.15, PALE_SLATE, "Lower coordination noise", ["Clear role boundaries and naming reduce routing churn before execution begins."], SLATE),
    ]
    for left, top, fill, title, lines, title_color in cards:
        add_card(slide, left, top, 3.45, 1.7, fill, title, lines, title_color=title_color)
    add_footer(slide, "These gains show up most clearly on cross-stack, ambiguous, or high-confidence work rather than tiny one-step requests.")
    add_speaker_notes(
        slide,
        "Translate technical workflow benefits into operating metrics.",
        [
            "Leaders should hear this slide as a list of performance levers: rework, restart time, confidence, budget discipline, and coordination cost.",
            "The workflow is creating value by reducing uncertainty and making specialist effort more reusable.",
            "Call out that the model is most financially attractive when tasks are large enough for those savings to compound.",
        ],
    )


def build_exec_fit_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, CREAM)
    add_brand_badge(slide)
    add_chip(slide, 0.55, 0.45, 1.95, "WHEN TO USE IT", PALE_SLATE, NAVY)
    add_textbox(slide, 0.55, 0.95, 8.0, 0.72, "Where this model earns its keep and where it does not", font_size=26, font_name=FONT_HEAD, color=NAVY, bold=True)
    table = slide.shapes.add_table(5, 2, Inches(0.75), Inches(1.95), Inches(12.0), Inches(3.85)).table
    table.columns[0].width = Inches(5.8)
    table.columns[1].width = Inches(6.2)
    set_table_cell(table.cell(0, 0), "Use this model when", color=WHITE, size=16, bold=True, fill=NAVY)
    set_table_cell(table.cell(0, 1), "Do not over-apply it when", color=WHITE, size=16, bold=True, fill=NAVY)
    rows = [
        ("The task spans frontend, backend, schema, testing, or review work.", "The task is a tiny one-step edit or a quick factual answer."),
        ("Requirements are vague and need a clarification or approval gate.", "There is no material ambiguity and the path is already obvious."),
        ("You care about auditability, resumability, or strong confidence before shipping.", "The coordination overhead would exceed the value of extra control."),
        ("The work needs to survive beyond one chat or one specialist.", "Speed matters more than repeatability and the risk of rework is low."),
    ]
    for row_index, row in enumerate(rows, start=1):
        fill = WHITE if row_index % 2 else PALE_SLATE
        set_table_cell(table.cell(row_index, 0), row[0], fill=fill)
        set_table_cell(table.cell(row_index, 1), row[1], fill=fill)
    add_card(
        slide,
        0.78,
        6.05,
        11.95,
        0.82,
        PALE_AMBER,
        "Leadership takeaway",
        ["The adoption mistake is not under-using agents. It is applying a heavy coordination model to work that does not need coordination."],
        title_color=AMBER,
    )
    add_footer(slide, "A disciplined trigger policy is part of the ROI model.")
    add_speaker_notes(
        slide,
        "Use this slide to avoid the impression that more orchestration is always better.",
        [
            "The strongest argument for the workflow is selective use on work with enough ambiguity, scale, or validation need to justify the control layer.",
            "That discipline protects both speed and credibility.",
            "If needed, summarize the decision rule as: use the model where rework or restart cost is materially higher than the coordination cost.",
        ],
    )


def build_exec_adoption_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_brand_badge(slide, dark=True)
    add_chip(slide, 0.58, 0.48, 1.8, "ADOPTION GUIDE", PALE_TEAL, TEAL_DARK)
    add_textbox(slide, 0.6, 0.98, 8.5, 0.72, "How to evaluate adoption in practice", font_size=26, font_name=FONT_HEAD, color=WHITE, bold=True)
    add_card(
        slide,
        0.68,
        1.95,
        3.85,
        1.85,
        WHITE,
        "Start here",
        ["Pilot the model on cross-stack features, higher-risk changes, or work that already suffers from poor resumability."],
        title_color=NAVY,
    )
    add_card(
        slide,
        4.74,
        1.95,
        3.85,
        1.85,
        PALE_TEAL,
        "Measure these signals",
        ["Time to approved scope, rework after implementation starts, validation coverage, and resume time after handoff."],
        title_color=TEAL_DARK,
    )
    add_card(
        slide,
        8.8,
        1.95,
        3.85,
        1.85,
        PALE_AMBER,
        "Keep the bar honest",
        ["If the chain is longer than the risk profile requires, trim it. Coordination should pay for itself."],
        title_color=AMBER,
    )
    add_paragraphs(
        slide,
        0.7,
        4.45,
        6.2,
        1.8,
        [
            "Suggested leadership KPIs:",
            "- reduction in restarted work after handoff",
            "- reduction in implementation rework from unclear scope",
            "- improvement in validated completion rate",
            "- time saved when resuming paused tasks",
        ],
        font_size=17,
        color=RGBColor(226, 232, 240),
        line_spacing=1.16,
    )
    add_card(
        slide,
        7.22,
        4.48,
        5.1,
        1.75,
        PALE_ROSE,
        "Bottom line",
        ["Treat the workflow as a governed delivery system for non-trivial AI-assisted work, not as a default pattern for every task."],
        title_color=ROSE,
    )
    add_footer(slide, "The strongest executive story is selective adoption with measurable operating outcomes.", dark=True)
    add_speaker_notes(
        slide,
        "Close with a concrete adoption stance rather than a vague recommendation.",
        [
            "Suggest a pilot on tasks where ambiguity, handoffs, and validation already create visible pain.",
            "Track a small KPI set so the workflow can be evaluated as an operating improvement rather than as an AI experiment.",
            "End by restating the core idea: this model is most useful when control, trust, and resumability matter.",
        ],
    )


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    build_exec_title_slide(prs)
    build_exec_problem_slide(prs)
    build_exec_operating_model_slide(prs)
    build_exec_roi_slide(prs)
    build_exec_fit_slide(prs)
    build_exec_adoption_slide(prs)
    prs.save(EXECUTIVE_OUTPUT_FILE)
    print(f"Created {EXECUTIVE_OUTPUT_FILE.name} with {len(prs.slides)} slides")


if __name__ == "__main__":
    main()