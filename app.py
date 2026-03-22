import streamlit as st
import time
from score import get_score, ROLE_SOC_MAP

st.set_page_config(
    page_title="Sponsorship Signal",
    page_icon="🎯",
    layout="centered"
)

st.title("Sponsorship Signal")
st.markdown("Find out how likely a company is to sponsor your visa for a specific role, before you spend an hour on your application.")
st.markdown("---")

company_input = st.text_input(
    "Company name",
    placeholder="e.g. Google, Microsoft, Amazon"
)

role_input = st.selectbox(
    "Target role type",
    options=list(ROLE_SOC_MAP.keys())
)

calculate = st.button("Calculate Sponsorship Signal", type="primary")

if calculate:
    if not company_input.strip():
        st.warning("Please enter a company name.")
    else:
        with st.spinner(""):
            steps = [
                "Checking petition history...",
                "Analyzing role type match...",
                "Reviewing trend direction...",
                "Calculating confidence..."
            ]
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) * 25)
                time.sleep(0.6)
            status_text.empty()
            progress_bar.empty()

        result = get_score(company_input.strip(), role_input)

        if not result["found"]:
            st.error(result["message"])
            st.info("Try a shorter search term. For example, search 'Amazon' instead of 'Amazon.com Services LLC'.")
        else:
            score = result["final_score"]
            confidence = result["confidence"]

            if score >= 66:
                color = "#2d9e5f"
                label = "Strong signal"
            elif score >= 35:
                color = "#e0a020"
                label = "Moderate signal"
            else:
                color = "#c0392b"
                label = "Weak signal"

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem;">
                    <div style="
                        width: 140px;
                        height: 140px;
                        border-radius: 50%;
                        background: {color};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto;
                    ">
                        <span style="color: white; font-size: 2.8rem; font-weight: bold;">{score}</span>
                    </div>
                    <p style="font-size: 1.1rem; font-weight: bold; margin-top: 1rem; color: {color};">{label}</p>
                    <p style="color: #888; font-size: 0.85rem;">Confidence: {confidence}%</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"**Company:** {result['company_name']}")
                st.markdown(f"**Role searched:** {result['role']}")
                st.markdown(f"**Total new hire approvals:** {result['total_approvals']:,}")
                st.markdown(f"**Most recent filing year:** {result['most_recent_year']}")
                st.markdown(f"**Typical wage level:** {result['wage_level']}")
                st.markdown(f"**2026 lottery odds:** {result['lottery_text']}")
                st.markdown(f"**Data sources:** USCIS H1B Employer Data Hub and DOL LCA Disclosure Files")

            st.markdown("---")
            st.markdown("### Why this score")

            signals = result["signals"]

            explanations = []

            if signals["recency"] >= 80:
                explanations.append(f"This company filed H1B petitions as recently as {result['most_recent_year']}, which is a strong positive signal.")
            elif signals["recency"] >= 50:
                explanations.append(f"This company has filed petitions in recent years but not in the last 12 months.")
            else:
                explanations.append(f"This company has not filed H1B petitions recently. Their last filing was in {result['most_recent_year']}.")

            if signals["approval_rate"] >= 90:
                explanations.append(f"Their petition approval rate is {signals['approval_rate']}%, meaning they almost always follow through when they sponsor.")
            elif signals["approval_rate"] >= 70:
                explanations.append(f"Their petition approval rate is {signals['approval_rate']}%, which is reasonable.")
            else:
                explanations.append(f"Their petition approval rate is {signals['approval_rate']}%, which is lower than average and may indicate speculative filing.")

            if signals["role_match"] >= 30:
                explanations.append(f"About {signals['role_match']}% of their past filings match the {role_input} role category, which is a reasonable match.")
            elif signals["role_match"] >= 10:
                explanations.append(f"Only {signals['role_match']}% of their filings match the {role_input} role category. They sponsor this type of role less frequently.")
            else:
                explanations.append(f"Very few of their past filings match the {role_input} role category ({signals['role_match']}%). This company may not typically sponsor this role type.")

            if signals["trend"] >= 65:
                explanations.append("Their sponsorship activity has been growing year over year, which is a positive indicator.")
            elif signals["trend"] <= 35:
                explanations.append("Their sponsorship activity has been declining in recent years. This reduces confidence in future sponsorship.")
            else:
                explanations.append("Their sponsorship activity has been relatively flat over the past few years.")

            for explanation in explanations:
                st.markdown(f"- {explanation}")

            st.markdown("---")
            st.caption("This score is based on historical government data and is not a guarantee of future sponsorship decisions. Data sourced from USCIS H1B Employer Data Hub and DOL LCA Disclosure Files. Score reflects patterns in public filings only.")

            st.markdown("### Was this helpful?")
            col_a, col_b, col_c = st.columns([1, 1, 4])
            with col_a:
                if st.button("Yes"):
                    st.success("Thanks for the feedback.")
            with col_b:
                if st.button("No"):
                    feedback = st.text_input("What could be better?")
                    if feedback:
                        st.success("Feedback noted. Thank you.")