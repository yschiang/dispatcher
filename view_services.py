import streamlit as st # type: ignore
import yaml
import pandas as pd
from config_loader import load_and_validate_config


def render_navigation():
    navigation_items = {
        "Service Configuration": "Service Configuration",
        "Show Raw Input Config": "Show Raw Input Config",
        "Show APISIX Config": "Show APISIX Config",
    }
    st.sidebar.title("Navigation")
    selected = st.sidebar.selectbox("Menu", options=navigation_items.keys())
    return navigation_items[selected]

def display_service_summary(service):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### General Info")
        st.write(f"**Service Name:** {service['name']}")
        st.write(f"**URI:** {service.get('uri', '')}")
        st.write(f"**Default Upstream:** {service.get('default_upstream', '')}")

    with col2:
        st.markdown("### Rollout Strategy")
        rollstrategy = service.get("rollstrategy", None)
        if rollstrategy:
            st.write(f"**Status:** ✅ Enabled")
        else:
            st.write("**Status:** ❌ Disabled (No Rollout Strategy Configured)")

    st.markdown("### Statistics")
    st.write(f"- **Total Matches:** {len(service.get('matches', []))}")
    st.write(f"- **Total Upstreams:** {len(service.get('upstreams', []))}")
    st.write(f"- **Total Rules:** {len(service.get('rules', []))}")

def render_service_config(config):
    st.title("Service Configuration")

    service_names = [s["name"] for s in config.get("services", [])]
    selected_service = st.selectbox("Select Service", service_names)

    service = next((s for s in config["services"] if s["name"] == selected_service), None)
    if service:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Matches", "Upstreams", "Rollout Strategy", "Selected Configuration"])

        with tab1:
            st.header("Service Overview")
            display_service_summary(service)

            st.header("Rules")
            rows = []
            for rule in service.get("rules", []):
                matches = ", ".join(rule.get("matches", []))
                rows.append({
                    "Rule ID": rule["id"],
                    "Matches": matches,
                    "Upstream": rule.get("upstream_id", service.get('default_upstream', ''))
                })
            if rows:
                st.dataframe(pd.DataFrame(rows))
            else:
                st.write("No rules defined.")

        with tab2:
            st.header("Matches")

            # Editable matches table
            matches = service.get("matches", [])
            if matches:
                for i, match in enumerate(matches):
                    st.markdown(f"#### Match {i+1}")
                    match["header_name"] = st.text_input(f"Header Name ({i+1})", match["header_name"], key=f"header_name_{i}")
                    match["operator"] = st.selectbox(f"Operator ({i+1})", ["==", "~="], index=["==", "~="].index(match["operator"]), key=f"operator_{i}")
                    match["value"] = st.text_input(f"Value ({i+1})", match["value"], key=f"value_{i}")

                if st.button("Save Matches"):
                    config_file = "input.yaml"
                    save_config(config_file, config)
                    st.success("Matches updated successfully!")
            else:
                st.write("No matches defined.")

        with tab3:
            st.header("Upstreams")
            df_upstreams = pd.DataFrame(service.get("upstreams", []))
            if not df_upstreams.empty:
                st.dataframe(df_upstreams)
            else:
                st.write("No upstreams defined.")

        with tab4:
            st.header("Rollout Strategy")
            rollstrategy = service.get("rollstrategy", None)
            if rollstrategy:
                st.write(f"**Strategy Name:** {rollstrategy.get('name', 'default')}")

                weighted_upstreams = rollstrategy.get("groups", [])
                if weighted_upstreams:
                    graphviz_dot = "digraph G {\n" + "\n".join(
                        f'  "{service["name"]}" -> "{upstream["upstream_id"]}" [label="{upstream["weight"]}%"]'
                        for upstream in weighted_upstreams
                    ) + "\n}"

                    st.graphviz_chart(graphviz_dot)
                else:
                    st.write("No weighted upstreams defined. Using default upstream.")
            else:
                st.write("No rollout strategy configured. Using default upstream.")

        with tab5:
            st.header("Selected Service Configuration")
            st.code(yaml.dump(service, default_flow_style=False), language="yaml")


st.set_page_config(page_title="Service Configuration", layout="wide")
config_file = "config/input.yaml"
# Validate and display the config
try:
    config = load_and_validate_config(config_file)
    render_service_config(config)
except Exception as e:
     st.error(e)
     st.stop()  # Stop execution if the config is invalid