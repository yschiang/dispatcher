import extra_streamlit_components as stx



val = stx.stepper_bar(steps=["Ready", "Get Set", "Go"])
st.info(f"Phase #{val}")