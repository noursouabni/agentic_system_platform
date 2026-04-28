import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from backend.agents.orchestrator import run_campaign_orchestrator
from backend.tools.storage import load_campaign_runs, save_campaign_run


st.set_page_config(
    page_title="Agentic Campaign Intelligence Platform",
    page_icon="🤖",
    layout="wide"
)

st.sidebar.title("Campaign History")

previous_runs = load_campaign_runs()
selected_saved_run = None

if not previous_runs:
    st.sidebar.info("No saved campaigns yet.")
else:
    st.sidebar.write(f"{len(previous_runs)} saved campaign(s)")

    run_options = {
        f"{run['brief'].get('campaign_name', 'Untitled Campaign')} | {run['run_id']}": run
        for run in reversed(previous_runs)
    }

    selected_label = st.sidebar.selectbox(
        "Open a saved campaign",
        options=["None"] + list(run_options.keys())
    )

    if selected_label != "None":
        selected_saved_run = run_options[selected_label]

        st.sidebar.success(
            f"Loaded {selected_saved_run['brief'].get('campaign_name', 'Untitled Campaign')}"
        )

st.markdown(
    """
    # 🤖 Agentic Campaign Intelligence Platform
    Turn a campaign brief into research, creative assets, media planning,
    and optimization recommendations.
    """
) 
def display_campaign_plan(campaign_plan: dict) -> None:
    """
    Displays a campaign plan using clean tabs.
    Works for both newly generated campaigns and saved campaigns.
    """

    st.markdown("## Campaign Plan Overview")
    st.info(campaign_plan["orchestrator_summary"])

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Research Agent",
            "Creative Agent",
            "Media Buying Agent",
            "Optimization Agent"
        ]
    )

    with tab1:
        research_output = campaign_plan["research"]

        st.markdown("### Audience Profile")
        st.write(research_output["audience_summary"])

        if research_output.get("audience_motivations"):
            st.markdown("### Audience Motivations")
            for item in research_output["audience_motivations"]:
                with st.container(border=True):
                    st.write(item)

        if research_output.get("pain_points"):
            st.markdown("### Pain Points")
            for item in research_output["pain_points"]:
                with st.container(border=True):
                    st.write(item)

        st.markdown("### Competitor Angle")
        st.write(research_output["competitor_angle"])

        st.markdown("### Positioning Angle")
        st.write(research_output["positioning_angle"])

        if research_output.get("messaging_strategy"):
            st.markdown("### Messaging Strategy")
            for item in research_output["messaging_strategy"]:
                with st.container(border=True):
                    st.write(item)

        if research_output.get("raw_llm_output"):
            with st.expander("Show raw Gemini research output"):
                st.text(research_output["raw_llm_output"])

    with tab2:
        creative_output = campaign_plan["creative"]

        st.markdown("### Main Message")
        st.write(creative_output["main_message"])

        if creative_output.get("instagram_captions"):
            st.markdown("### Instagram Captions")
            for item in creative_output["instagram_captions"]:
                with st.container(border=True):
                    st.write(item)

        if creative_output.get("tiktok_hooks"):
            st.markdown("### TikTok Hooks")
            for item in creative_output["tiktok_hooks"]:
                with st.container(border=True):
                    st.write(item)

        if creative_output.get("google_ads_headlines"):
            st.markdown("### Google Ads Headlines")
            for item in creative_output["google_ads_headlines"]:
                with st.container(border=True):
                    st.write(item)

        if creative_output.get("email_subject_lines"):
            st.markdown("### Email Subject Lines")
            for item in creative_output["email_subject_lines"]:
                with st.container(border=True):
                    st.write(item)

        if creative_output.get("linkedin_posts"):
            st.markdown("### LinkedIn Posts")
            for item in creative_output["linkedin_posts"]:
                with st.container(border=True):
                    st.write(item)

        if creative_output.get("website_hero_copy"):
            st.markdown("### Website Hero Copy")
            for item in creative_output["website_hero_copy"]:
                with st.container(border=True):
                    st.write(item)

        if creative_output.get("ctas"):
            st.markdown("### CTAs")
            st.caption(
                "CTA = Call To Action, the short phrase that tells users what to do next."
            )
            for item in creative_output["ctas"]:
                with st.container(border=True):
                    st.write(item)

        st.markdown("### Visual Direction")
        st.write(creative_output["visual_direction"])

        if creative_output.get("image_prompt"):
            st.markdown("### Image Generation Prompt")
            st.caption(
                "This prompt can later be sent to an image generation model to create the campaign poster."
            )
            st.code(creative_output["image_prompt"])

        if creative_output.get("raw_llm_output"):
            with st.expander("Show raw Gemini creative output"):
                st.text(creative_output["raw_llm_output"])

    with tab3:
        st.markdown("### Budget Allocation")

        allocation = campaign_plan["media_plan"]["budget_allocation"]

        allocation_rows = []
        for channel, values in allocation.items():
            allocation_rows.append(
                {
                    "Channel": channel,
                    "Budget": values["budget"],
                    "Percentage": values["percentage"]
                }
            )

        allocation_df = pd.DataFrame(allocation_rows)

        st.dataframe(allocation_df, use_container_width=True)

        fig = px.pie(
            allocation_df,
            names="Channel",
            values="Budget",
            title="Budget Split by Channel"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Recommendation")
        st.write(campaign_plan["media_plan"]["recommendation"])

    with tab4:
        st.markdown("### Simulated Live Campaign Metrics")

        metrics_df = pd.DataFrame(campaign_plan["performance_metrics"])

        if metrics_df.empty:
            st.warning("No metrics available for the selected channels.")
        else:
            display_df = metrics_df.copy()

            percentage_cols = ["ctr", "conversion_rate"]
            money_cols = ["cost", "revenue", "cpc", "cpa", "roas"]

            for col in percentage_cols:
                display_df[col] = (display_df[col] * 100).round(2)

            for col in money_cols:
                display_df[col] = display_df[col].round(2)

            st.dataframe(display_df, use_container_width=True)

            col1, col2, col3, col4 = st.columns(4)

            avg_ctr = metrics_df["ctr"].mean() * 100
            avg_cpa = metrics_df["cpa"].mean()
            total_revenue = metrics_df["revenue"].sum()
            avg_roas = metrics_df["roas"].mean()

            col1.metric("Average CTR", f"{avg_ctr:.2f}%")
            col2.metric("Average CPA", f"{avg_cpa:.2f}")
            col3.metric("Total Revenue", f"{total_revenue:.2f}")
            col4.metric("Average ROAS", f"{avg_roas:.2f}")

            st.markdown("### ROAS by Channel")
            fig_roas = px.bar(
                metrics_df,
                x="channel",
                y="roas",
                title="Return on Ad Spend by Channel"
            )
            st.plotly_chart(fig_roas, use_container_width=True)

            st.markdown("### Conversion Rate by Channel")
            fig_conversion = px.bar(
                metrics_df,
                x="channel",
                y="conversion_rate",
                title="Conversion Rate by Channel"
            )
            st.plotly_chart(fig_conversion, use_container_width=True)

            st.markdown("### Optimization Summary")
            st.info(campaign_plan["optimization"]["summary"])

            st.markdown("### Recommended Actions")
            for rec in campaign_plan["optimization"]["recommendations"]:
                st.markdown(f"- {rec}")
if selected_saved_run:
    st.markdown("## Loaded Saved Campaign")

    st.caption(
        f"{selected_saved_run['run_id']} | {selected_saved_run['created_at']}"
    )

    saved_brief = selected_saved_run["brief"]
    saved_plan = selected_saved_run["campaign_plan"]

    with st.expander("Show saved campaign brief"):
        st.json(saved_brief)

    display_campaign_plan(saved_plan)

    st.stop()
st.subheader("Campaign Brief")

campaign_name = st.text_input("Campaign name")
product = st.text_input("Product or service")

goal = st.selectbox(
    "Campaign goal",
    [
        "Increase brand awareness",
        "Generate leads",
        "Increase sales",
        "Increase event registrations",
        "Improve engagement"
    ]
)

audience = st.text_area("Target audience")

budget = st.number_input(
    "Budget",
    min_value=0,
    step=100
)

channels = st.multiselect(
    "Channels",
    ["Instagram", "TikTok", "Google Ads", "LinkedIn", "Email", "Website"]
)

tone = st.selectbox(
    "Tone of voice",
    ["Professional", "Friendly", "Luxury", "Bold", "Educational", "Emotional"]
)

duration = st.slider(
    "Campaign duration in days",
    1,
    60,
    14
)

if st.button("Generate Campaign Plan"):
    brief_data = {
        "campaign_name": campaign_name,
        "product": product,
        "goal": goal,
        "audience": audience,
        "budget": budget,
        "channels": channels,
        "tone": tone,
        "duration_days": duration
    }

    if not campaign_name or not product or not audience or budget <= 0 or not channels:
        st.error(
            "Please complete the campaign name, product, audience, budget, and channels."
        )
    else:
        with st.spinner("Agents are working on your campaign..."):
            campaign_plan = run_campaign_orchestrator(brief_data)
            saved_run = save_campaign_run(brief_data, campaign_plan)

        st.success("Campaign plan generated by the agent workflow.")
        st.caption(f"Saved as {saved_run['run_id']} at {saved_run['created_at']}")

        display_campaign_plan(campaign_plan)

        with tab1:
            research_output = campaign_plan["research"]

            st.markdown("### Audience Profile")
            st.write(research_output["audience_summary"])

            if research_output.get("audience_motivations"):
                st.markdown("### Audience Motivations")
                for item in research_output["audience_motivations"]:
                    with st.container(border=True):
                        st.write(item)

            if research_output.get("pain_points"):
                st.markdown("### Pain Points")
                for item in research_output["pain_points"]:
                    with st.container(border=True):
                        st.write(item)

            st.markdown("### Competitor Angle")
            st.write(research_output["competitor_angle"])

            st.markdown("### Positioning Angle")
            st.write(research_output["positioning_angle"])

            if research_output.get("messaging_strategy"):
                st.markdown("### Messaging Strategy")
                for item in research_output["messaging_strategy"]:
                    with st.container(border=True):
                        st.write(item)

            with st.expander("Show raw Gemini research output"):
                st.text(research_output["raw_llm_output"])
        with tab2:
            creative_output = campaign_plan["creative"]

            st.markdown("### Main Message")
            st.write(creative_output["main_message"])

            if creative_output.get("instagram_captions"):
                st.markdown("### Instagram Captions")
                for item in creative_output["instagram_captions"]:
                    with st.container(border=True):
                        st.write(item)

            if creative_output.get("tiktok_hooks"):
                st.markdown("### TikTok Hooks")
                for item in creative_output["tiktok_hooks"]:
                    with st.container(border=True):
                        st.write(item)

            if creative_output.get("google_ads_headlines"):
                st.markdown("### Google Ads Headlines")
                for item in creative_output["google_ads_headlines"]:
                    with st.container(border=True):
                        st.write(item)

            if creative_output.get("email_subject_lines"):
                st.markdown("### Email Subject Lines")
                for item in creative_output["email_subject_lines"]:
                    with st.container(border=True):
                        st.write(item)

            if creative_output.get("linkedin_posts"):
                st.markdown("### LinkedIn Posts")
                for item in creative_output["linkedin_posts"]:
                    with st.container(border=True):
                        st.write(item)

            if creative_output.get("website_hero_copy"):
                st.markdown("### Website Hero Copy")
                for item in creative_output["website_hero_copy"]:
                    with st.container(border=True):
                        st.write(item)

            if creative_output.get("ctas"):
                st.markdown("### CTAs")
                st.caption("CTA = Call To Action, the short phrase that tells users what to do next.")
                for item in creative_output["ctas"]:
                    with st.container(border=True):
                        st.write(item)

            st.markdown("### Visual Direction")
            st.write(creative_output["visual_direction"])

            st.markdown("### Image Generation Prompt")
            st.caption("This prompt can later be sent to an image generation model to create the campaign poster.")
            st.code(creative_output["image_prompt"])

            with st.expander("Show raw Gemini output"):
                st.text(creative_output["raw_llm_output"])
        with tab3:
            st.markdown("### Budget Allocation")

            allocation = campaign_plan["media_plan"]["budget_allocation"]

            allocation_rows = []
            for channel, values in allocation.items():
                allocation_rows.append(
                    {
                        "Channel": channel,
                        "Budget": values["budget"],
                        "Percentage": values["percentage"]
                    }
                )

            allocation_df = pd.DataFrame(allocation_rows)

            st.dataframe(allocation_df, use_container_width=True)

            fig = px.pie(
                allocation_df,
                names="Channel",
                values="Budget",
                title="Budget Split by Channel"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Recommendation")
            st.write(campaign_plan["media_plan"]["recommendation"])

        with tab4:
            st.markdown("### Simulated Live Campaign Metrics")

            if "performance_metrics" not in campaign_plan:
                st.error(
                    "The orchestrator did not return performance_metrics. "
                    "Please update backend/agents/orchestrator.py."
                )
                st.stop()

            metrics_df = pd.DataFrame(campaign_plan["performance_metrics"])

            if metrics_df.empty:
                st.warning("No metrics available for the selected channels.")
            else:
                display_df = metrics_df.copy()

                percentage_cols = ["ctr", "conversion_rate"]
                money_cols = ["cost", "revenue", "cpc", "cpa", "roas"]

                for col in percentage_cols:
                    display_df[col] = (display_df[col] * 100).round(2)

                for col in money_cols:
                    display_df[col] = display_df[col].round(2)

                st.dataframe(display_df, use_container_width=True)

                col1, col2, col3, col4 = st.columns(4)

                avg_ctr = metrics_df["ctr"].mean() * 100
                avg_cpa = metrics_df["cpa"].mean()
                total_revenue = metrics_df["revenue"].sum()
                avg_roas = metrics_df["roas"].mean()

                col1.metric("Average CTR", f"{avg_ctr:.2f}%")
                col2.metric("Average CPA", f"{avg_cpa:.2f}")
                col3.metric("Total Revenue", f"{total_revenue:.2f}")
                col4.metric("Average ROAS", f"{avg_roas:.2f}")

                st.markdown("### ROAS by Channel")

                fig_roas = px.bar(
                    metrics_df,
                    x="channel",
                    y="roas",
                    title="Return on Ad Spend by Channel"
                )

                st.plotly_chart(fig_roas, use_container_width=True)

                st.markdown("### Conversion Rate by Channel")

                fig_conversion = px.bar(
                    metrics_df,
                    x="channel",
                    y="conversion_rate",
                    title="Conversion Rate by Channel"
                )

                st.plotly_chart(fig_conversion, use_container_width=True)

                st.markdown("### Optimization Summary")
                st.info(campaign_plan["optimization"]["summary"])

                st.markdown("### Recommended Actions")

                for rec in campaign_plan["optimization"]["recommendations"]:
                    st.markdown(f"- {rec}")