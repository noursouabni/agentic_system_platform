import pandas as pd


def load_campaign_metrics(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df["ctr"] = df["clicks"] / df["impressions"]
    df["cpc"] = df["cost"] / df["clicks"]
    df["conversion_rate"] = df["conversions"] / df["clicks"]
    df["cpa"] = df["cost"] / df["conversions"]
    df["roas"] = df["revenue"] / df["cost"]

    return df


def filter_metrics_by_channels(
    metrics_df: pd.DataFrame,
    selected_channels: list[str]
) -> pd.DataFrame:
    return metrics_df[metrics_df["channel"].isin(selected_channels)].copy()