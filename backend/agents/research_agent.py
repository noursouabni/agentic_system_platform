import re

from backend.schemas import CampaignBrief
from backend.tools.llm_client import generate_text


def extract_section(text: str, start_label: str, end_label: str | None = None) -> str:
    """
    Extracts text between two section labels.
    """
    if end_label:
        pattern = rf"{start_label}:\s*(.*?)(?=\n{end_label}:)"
    else:
        pattern = rf"{start_label}:\s*(.*)$"

    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def split_numbered_items(section_text: str) -> list[str]:
    """
    Splits numbered or bullet-style LLM output into a clean list.
    """
    if not section_text:
        return []

    lines = section_text.splitlines()
    cleaned_items = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"^\d+[\).\-\s]*", "", line).strip()
        line = re.sub(r"^[•\-]\s*", "", line).strip()

        if line:
            cleaned_items.append(line)

    return cleaned_items


def run_research_agent(brief: CampaignBrief) -> dict:
    """
    Generates audience and positioning research using Gemini.
    """

    prompt = f"""
You are a senior marketing research strategist.

Analyze this campaign brief:

Campaign name: {brief.campaign_name}
Product or service: {brief.product}
Goal: {brief.goal}
Target audience: {brief.audience}
Selected channels: {", ".join(brief.channels)}
Tone of voice: {brief.tone}
Campaign duration: {brief.duration_days} days

Rules:
- Be practical and specific.
- Do not invent real competitors unless they are globally obvious.
- Focus on audience psychology, positioning, and campaign strategy.
- Write in English.
- Keep the output concise and usable by a marketing team.
- Do not mention that you are an AI.

Return the result using exactly this structure:

AUDIENCE PROFILE:
...

AUDIENCE MOTIVATIONS:
1. ...
2. ...
3. ...

PAIN POINTS:
1. ...
2. ...
3. ...

COMPETITOR ANGLE:
...

POSITIONING ANGLE:
...

MESSAGING STRATEGY:
1. ...
2. ...
3. ...
"""

    llm_output = generate_text(prompt)

    audience_profile = extract_section(
        llm_output,
        "AUDIENCE PROFILE",
        "AUDIENCE MOTIVATIONS"
    )
    audience_motivations = extract_section(
        llm_output,
        "AUDIENCE MOTIVATIONS",
        "PAIN POINTS"
    )
    pain_points = extract_section(
        llm_output,
        "PAIN POINTS",
        "COMPETITOR ANGLE"
    )
    competitor_angle = extract_section(
        llm_output,
        "COMPETITOR ANGLE",
        "POSITIONING ANGLE"
    )
    positioning_angle = extract_section(
        llm_output,
        "POSITIONING ANGLE",
        "MESSAGING STRATEGY"
    )
    messaging_strategy = extract_section(
        llm_output,
        "MESSAGING STRATEGY",
        None
    )

    return {
        "agent": "Research Agent",
        "audience_summary": audience_profile,
        "audience_motivations": split_numbered_items(audience_motivations),
        "pain_points": split_numbered_items(pain_points),
        "competitor_angle": competitor_angle,
        "positioning_angle": positioning_angle,
        "messaging_strategy": split_numbered_items(messaging_strategy),
        "raw_llm_output": llm_output,
    }