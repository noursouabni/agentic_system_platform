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


def build_channel_sections(channels: list[str]) -> str:
    """
    Builds the requested output sections based only on selected channels.
    """

    sections = ["MAIN MESSAGE"]

    if "Instagram" in channels:
        sections.append("INSTAGRAM CAPTIONS")

    if "TikTok" in channels:
        sections.append("TIKTOK HOOKS")

    if "Google Ads" in channels:
        sections.append("GOOGLE ADS HEADLINES")

    if "Email" in channels:
        sections.append("EMAIL SUBJECT LINES")

    if "LinkedIn" in channels:
        sections.append("LINKEDIN POSTS")

    if "Website" in channels:
        sections.append("WEBSITE HERO COPY")

    sections.append("CTAS")
    sections.append("VISUAL DIRECTION")
    sections.append("IMAGE_PROMPT")

    return "\n".join([f"{section}:\n..." for section in sections])


def get_next_label(current_label: str, labels: list[str]) -> str | None:
    """
    Returns the label that comes after the current section.
    """
    index = labels.index(current_label)

    if index + 1 < len(labels):
        return labels[index + 1]

    return None


def run_creative_agent(brief: CampaignBrief) -> dict:
    """
    Generates campaign creative assets using Gemini.
    The output is adapted to the selected channels only.
    """

    selected_channels = brief.channels
    output_structure = build_channel_sections(selected_channels)

    prompt = f"""
You are a senior marketing creative strategist.

Create campaign assets based on this brief:

Campaign name: {brief.campaign_name}
Product or service: {brief.product}
Goal: {brief.goal}
Target audience: {brief.audience}
Selected channels: {", ".join(selected_channels)}
Tone of voice: {brief.tone}
Campaign duration: {brief.duration_days} days

Rules:
- Generate content only for the selected channels.
- Do not generate sections for channels that were not selected.
- Be specific to the audience and product.
- Avoid generic phrases.
- Keep the output clear and usable by a marketing team.
- Write in English.
- Do not mention that you are an AI.
- Keep each item concise and directly usable.
- For each selected channel, generate exactly 3 items.
- CTAS means Call To Action. Generate 3 short action phrases.
- IMAGE_PROMPT should describe a poster or campaign visual that could be sent to an image generation model.

Return the result using exactly this structure and no extra sections:

{output_structure}
"""

    llm_output = generate_text(prompt)

    labels = ["MAIN MESSAGE"]

    if "Instagram" in selected_channels:
        labels.append("INSTAGRAM CAPTIONS")

    if "TikTok" in selected_channels:
        labels.append("TIKTOK HOOKS")

    if "Google Ads" in selected_channels:
        labels.append("GOOGLE ADS HEADLINES")

    if "Email" in selected_channels:
        labels.append("EMAIL SUBJECT LINES")

    if "LinkedIn" in selected_channels:
        labels.append("LINKEDIN POSTS")

    if "Website" in selected_channels:
        labels.append("WEBSITE HERO COPY")

    labels.append("CTAS")
    labels.append("VISUAL DIRECTION")
    labels.append("IMAGE_PROMPT")

    parsed = {}

    for label in labels:
        next_label = get_next_label(label, labels)
        parsed[label] = extract_section(llm_output, label, next_label)

    return {
        "agent": "Creative Agent",
        "main_message": parsed.get("MAIN MESSAGE", ""),
        "instagram_captions": split_numbered_items(
            parsed.get("INSTAGRAM CAPTIONS", "")
        ),
        "tiktok_hooks": split_numbered_items(
            parsed.get("TIKTOK HOOKS", "")
        ),
        "google_ads_headlines": split_numbered_items(
            parsed.get("GOOGLE ADS HEADLINES", "")
        ),
        "email_subject_lines": split_numbered_items(
            parsed.get("EMAIL SUBJECT LINES", "")
        ),
        "linkedin_posts": split_numbered_items(
            parsed.get("LINKEDIN POSTS", "")
        ),
        "website_hero_copy": split_numbered_items(
            parsed.get("WEBSITE HERO COPY", "")
        ),
        "ctas": split_numbered_items(parsed.get("CTAS", "")),
        "visual_direction": parsed.get("VISUAL DIRECTION", ""),
        "image_prompt": parsed.get("IMAGE_PROMPT", ""),
        "raw_llm_output": llm_output,
    }