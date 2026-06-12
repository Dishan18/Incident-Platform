"""
Predictions page -- ML-powered incident analysis.
"""

import pandas as pd
import streamlit as st

from backend.ml.predict_incident import predict_incident
from backend.ml.similar_incidents import get_similar_incidents
from backend.incident.create_incident import APP_TEAM_MAP

from frontend.components.cards import render_prediction_card
from frontend.styles.theme import MUTED, TEXT
from backend.ml.explain_prediction import explain_prediction

def render_predictions() -> None:
    """Render the Predictions page."""

    st.markdown(
        f'<div style="font-size:20px; font-weight:600; color:{TEXT};">'
        f"Predictions</div>"
        f'<div style="font-size:14px; color:{MUTED}; margin-top:4px;">'
        f"ML-powered incident analysis and recommendations</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="height:24px;"></div>',
        unsafe_allow_html=True,
    )

    col_form, col_spacer, col_results = st.columns(
        [0.42, 0.04, 0.54]
    )

    with col_form:

        st.markdown(
            '<div class="section-title" style="margin-top:0;">'
            "Input</div>",
            unsafe_allow_html=True,
        )

        description = st.text_area(
            "Incident Description",
            placeholder="Describe the incident symptoms...",
            height=120,
        )

        applications = sorted(APP_TEAM_MAP.keys())

        application = st.selectbox(
            "Application",
            applications,
            key="pred_app",
        )

        col_u, col_s = st.columns(2)

        with col_u:
            affected_users = st.number_input(
                "Affected Users",
                min_value=1,
                value=1,
                step=1,
                key="pred_users",
            )

        with col_s:
            impact_scope = st.selectbox(
                "Impact Scope",
                [
                    "single_user",
                    "department",
                    "site",
                    "enterprise",
                ],
                key="pred_scope",
            )

        st.markdown(
            '<div style="height:16px;"></div>',
            unsafe_allow_html=True,
        )

        analyze_clicked = st.button(
            "Analyze Incident",
            use_container_width=True,
        )

    with col_results:

        st.markdown(
            '<div class="section-title" style="margin-top:0;">'
            "Analysis Results</div>",
            unsafe_allow_html=True,
        )

        if analyze_clicked and description.strip():

            try:

                result = predict_incident(
                    description=description,
                    application=application,
                    affected_users=affected_users,
                    impact_scope=impact_scope,
                )

                similar_incidents = get_similar_incidents(
                    description=description,
                    top_k=5,
                )
            except Exception as e:

                st.error(
                    f"Prediction failed: {str(e)}"
                )

                return

            # Prediction Cards
            r1, r2 = st.columns(2)

            with r1:
                render_prediction_card(
                    "Recommended Team",
                    result["team"],
                    "",
                )

            with r2:
                render_prediction_card(
                    "Predicted Priority",
                    result["priority"],
                    "",
                )

            st.markdown(
                '<div style="height:12px;"></div>',
                unsafe_allow_html=True,
            )

            r3, r4 = st.columns(2)

            with r3:
                render_prediction_card(
                    "Est. Resolution Time",
                    f'{round(result["resolution_time"])} min',
                    "",
                )

            with r4:
                render_prediction_card(
                    "Impact Scope",
                    impact_scope.replace(
                        "_",
                        " ",
                    ).title(),
                    "",
                )

            st.markdown(
                '<div style="height:24px;"></div>',
                unsafe_allow_html=True,
            )

            # Summary
            st.markdown(
                '<div class="section-title">'
                "AI Recommendation Summary"
                "</div>",
                unsafe_allow_html=True,
            )

            st.success(
                f"""
Recommended Team: {result['team']}

Predicted Priority: {result['priority']}

Estimated Resolution Time: {round(result['resolution_time'])} minutes
"""
            )

            st.markdown(
                '<div style="height:16px;"></div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                "### Recommendation Rationale"
            )

            st.write(
                f"""
Based on the incident description,
application **{application}**,
impact scope **{impact_scope.replace('_', ' ').title()}**,
and **{affected_users:,} affected users**,
the system recommends routing the incident to
**{result['team']}** with a predicted priority of
**{result['priority']}**.

The estimated resolution time is
**{round(result['resolution_time'])} minutes**
based on historical incident patterns.
"""
            )

            st.markdown(
                '<div style="height:20px;"></div>',
                unsafe_allow_html=True,
            )

            # Similar Incidents
            st.markdown(
                "### Similar Historical Incidents"
            )

            if similar_incidents:
                explanation = explain_prediction(
                    similar_incidents
                )
                similar_df = pd.DataFrame(
                    similar_incidents
                )[[
                    "description",
                    "team",
                    "priority",
                    "resolution_time",
                    "root_cause",
                    "similarity",
                ]]

                st.dataframe(
                    similar_df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.markdown(
                    '<div style="height:20px;"></div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "### Why This Recommendation?"
                )

                st.info(
                    f"""
                • {explanation['team_support']} of the top 5 similar incidents were assigned to **{explanation['most_common_team']}**

                • Most common priority among similar incidents: **{explanation['most_common_priority']}**

                • Most frequent root cause: **{explanation['common_root_cause']}**

                • Average historical resolution time: **{explanation['avg_resolution_time']} minutes**
                """
                )

            else:

                st.info(
                    "No similar incidents found."
                )

        elif analyze_clicked:
            st.warning(
                "Please provide an incident description."
            )
        else:
            st.markdown(
                f'<div class="empty-state">'
                f"Enter incident details and click "
                f'"Analyze Incident" to see ML predictions.'
                f"</div>",
                unsafe_allow_html=True,
            )