import pandas as pd


def run_optimization_agent(metrics_df: pd.DataFrame) -> dict:
    if metrics_df.empty:
        return {
            "agent": "Optimization Agent",
            "summary": "No performance data available for selected channels.",
            "best_channel": None,
            "weakest_channel": None,
            "recommendations": [
                "Select channels that have available performance data."
            ],
        }

    best_channel_row = metrics_df.sort_values(
        by=["roas", "conversion_rate"],
        ascending=False
    ).iloc[0]

    weakest_channel_row = metrics_df.sort_values(
        by=["roas", "conversion_rate"],
        ascending=True
    ).iloc[0]

    best_channel = best_channel_row["channel"]
    weakest_channel = weakest_channel_row["channel"]

    recommendations = []

    if weakest_channel != best_channel:
        recommendations.append(
            f"Reallocate 15% of the budget from {weakest_channel} "
            f"to {best_channel} because {best_channel} has stronger ROAS "
            f"and conversion performance."
        )

    low_ctr_channels = metrics_df[metrics_df["ctr"] < 0.03]["channel"].tolist()

    for channel in low_ctr_channels:
        recommendations.append(
            f"Improve creative testing on {channel} because CTR is below 3%."
        )

    high_cpa_channels = metrics_df[
        metrics_df["cpa"] > metrics_df["cpa"].mean()
    ]["channel"].tolist()

    for channel in high_cpa_channels:
        recommendations.append(
            f"Review targeting or landing page quality for {channel} because CPA is above average."
        )

    if not recommendations:
        recommendations.append(
            "Campaign performance is balanced. Continue monitoring before major budget changes."
        )

    return {
        "agent": "Optimization Agent",
        "summary": (
            f"{best_channel} is currently the strongest channel, while "
            f"{weakest_channel} needs optimization."
        ),
        "best_channel": best_channel,
        "weakest_channel": weakest_channel,
        "recommendations": recommendations,
    }