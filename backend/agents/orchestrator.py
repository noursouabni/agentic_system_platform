from pathlib import Path

from backend.schemas import CampaignBrief
from backend.agents.research_agent import run_research_agent
from backend.agents.creative_agent import run_creative_agent
from backend.agents.media_buying_agent import run_media_buying_agent
from backend.agents.optimization_agent import run_optimization_agent
from backend.tools.analytics import (
    load_campaign_metrics,
    filter_metrics_by_channels,
)


BASE_DIR = Path(__file__).resolve().parents[1]
METRICS_PATH = BASE_DIR / "data" / "mock_campaign_metrics.csv"


def run_campaign_orchestrator(brief_data: dict) -> dict:
    """
    Main orchestrator agent.
    It receives the campaign brief, delegates work to sub-agents,
    loads simulated campaign metrics, and asks the optimization agent
    to recommend budget actions.
    """

    brief = CampaignBrief(**brief_data)

    research_output = run_research_agent(brief)
    creative_output = run_creative_agent(brief)
    media_plan_output = run_media_buying_agent(brief)

    all_metrics_df = load_campaign_metrics(str(METRICS_PATH))

    selected_metrics_df = filter_metrics_by_channels(
        all_metrics_df,
        brief.channels,
    )

    optimization_output = run_optimization_agent(selected_metrics_df)

    return {
        "campaign_name": brief.campaign_name,
        "orchestrator_summary": (
            "The campaign orchestrator received the brief, delegated tasks to "
            "specialized agents, loaded simulated campaign metrics, and asked "
            "the optimization agent to recommend budget actions."
        ),
        "research": research_output,
        "creative": creative_output,
        "media_plan": media_plan_output,
        "performance_metrics": selected_metrics_df.to_dict(orient="records"),
        "optimization": optimization_output,
    }