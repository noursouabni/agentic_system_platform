from backend.schemas import CampaignBrief


def run_media_buying_agent(brief: CampaignBrief) -> dict:
    """
    Creates a simple budget allocation across selected channels.
    Later, this can connect to ad platforms or optimization models.
    """

    if not brief.channels:
        return {
            "agent": "Media Buying Agent",
            "budget_allocation": {},
            "recommendation": "No channels selected. Please choose at least one channel."
        }

    budget_per_channel = round(brief.budget / len(brief.channels), 2)

    allocation = {
        channel: {
            "budget": budget_per_channel,
            "percentage": round(100 / len(brief.channels), 2)
        }
        for channel in brief.channels
    }

    return {
        "agent": "Media Buying Agent",
        "budget_allocation": allocation,
        "recommendation": (
            "Start with an equal budget split during the testing phase, then "
            "reallocate budget based on CTR, conversion rate, and CPA."
        )
    }