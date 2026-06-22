from pathlib import Path

from generate_agentic_approach_presentation import (
    AMBER,
    CREAM,
    FONT_HEAD,
    MUTED,
    NAVY,
    PALE_AMBER,
    PALE_ROSE,
    PALE_SLATE,
    PALE_TEAL,
    Presentation,
    RGBColor,
    ROSE,
    SLATE,
    SLIDE_HEIGHT,
    SLIDE_WIDTH,
    TEAL,
    TEAL_DARK,
    WHITE,
    Inches,
    MSO_AUTO_SHAPE_TYPE,
    add_background,
    add_brand_badge,
    add_card,
    add_chip,
    add_footer,
    add_speaker_notes,
    add_textbox,
)


HANDOUT_OUTPUT_FILE = Path(__file__).with_name("agentic-approach-executive-handout.pptx")


def add_divider(slide, left, top, width, color):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(0.04),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def build_handout_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, CREAM)
    add_brand_badge(slide)
    add_chip(slide, 0.55, 0.42, 2.2, "ONE-PAGE EXECUTIVE HANDOUT", PALE_TEAL, TEAL_DARK)

    add_textbox(
        slide,
        0.55,
        0.9,
        8.6,
        0.58,
        "Agentic workflow summary: how it works and why it creates value",
        font_size=24,
        font_name=FONT_HEAD,
        color=NAVY,
        bold=True,
    )
    add_textbox(
        slide,
        0.58,
        1.42,
        9.4,
        0.46,
        "This .claude setup uses intake, routing, specialist execution, independent validation, and durable artifacts to control non-trivial AI-assisted delivery work.",
        font_size=15,
        color=MUTED,
    )

    add_card(
        slide,
        0.6,
        2.0,
        4.0,
        1.45,
        WHITE,
        "What it does",
        ["Turns ambiguous requests into a governed delivery flow instead of one long chat-driven implementation attempt."],
        title_color=NAVY,
    )
    add_card(
        slide,
        4.72,
        2.0,
        4.0,
        1.45,
        PALE_TEAL,
        "Why it matters",
        ["It lowers wasted work, improves specialist fit, and makes validation and handoffs more reliable."],
        title_color=TEAL_DARK,
    )
    add_card(
        slide,
        8.84,
        2.0,
        3.88,
        1.45,
        PALE_AMBER,
        "Best fit",
        ["Cross-stack, ambiguous, or higher-confidence work where rework and resume cost are material."],
        title_color=AMBER,
    )

    add_divider(slide, 0.6, 3.72, 12.1, TEAL)

    add_textbox(
        slide,
        0.6,
        3.86,
        3.0,
        0.36,
        "Operating model",
        font_size=18,
        font_name=FONT_HEAD,
        color=NAVY,
        bold=True,
    )
    add_card(
        slide,
        0.6,
        4.24,
        2.9,
        1.4,
        PALE_TEAL,
        "1. Intake",
        ["Clarify scope, estimate cost band, and require approval when needed."],
        title_color=TEAL_DARK,
    )
    add_card(
        slide,
        3.7,
        4.24,
        2.9,
        1.4,
        WHITE,
        "2. Route",
        ["Select the minimum valid specialist chain for the task."],
        title_color=NAVY,
    )
    add_card(
        slide,
        6.8,
        4.24,
        2.9,
        1.4,
        PALE_ROSE,
        "3. Validate",
        ["Use separate testers and read-only reviewers for an independent quality signal."],
        title_color=ROSE,
    )
    add_card(
        slide,
        9.9,
        4.24,
        2.82,
        1.4,
        PALE_AMBER,
        "4. Preserve",
        ["Capture routing, handoff, review, and test evidence so work can resume cleanly."],
        title_color=AMBER,
    )

    add_textbox(
        slide,
        0.6,
        5.94,
        3.3,
        0.36,
        "Value drivers",
        font_size=18,
        font_name=FONT_HEAD,
        color=NAVY,
        bold=True,
    )
    add_card(
        slide,
        0.6,
        6.28,
        3.0,
        0.82,
        WHITE,
        "Lower rework",
        ["Bad assumptions are surfaced earlier."],
        title_color=NAVY,
    )
    add_card(
        slide,
        3.8,
        6.28,
        3.0,
        0.82,
        PALE_TEAL,
        "Faster restarts",
        ["Artifacts cut resume time after handoff."],
        title_color=TEAL_DARK,
    )
    add_card(
        slide,
        7.0,
        6.28,
        2.8,
        0.82,
        PALE_AMBER,
        "Better budget discipline",
        ["Expensive work can be split or stopped sooner."],
        title_color=AMBER,
    )
    add_card(
        slide,
        10.0,
        6.28,
        2.72,
        0.82,
        PALE_ROSE,
        "Stronger trust",
        ["Validation is explicit instead of implied."],
        title_color=ROSE,
    )

    add_footer(slide, "Use this model selectively for non-trivial work. For tiny one-step tasks, the coordination overhead is usually not worth it.")
    add_speaker_notes(
        slide,
        "This handout is meant to stand alone as a one-page executive summary.",
        [
            "The core message is that the workflow adds control where ambiguity, handoffs, and validation risk are expensive.",
            "Use the top row to summarize what it is, why it matters, and when it is the right fit.",
            "Use the middle and bottom rows to explain the operating flow and the specific ROI levers it creates.",
        ],
    )


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    build_handout_slide(prs)
    prs.save(HANDOUT_OUTPUT_FILE)
    print(f"Created {HANDOUT_OUTPUT_FILE.name} with {len(prs.slides)} slide")


if __name__ == "__main__":
    main()