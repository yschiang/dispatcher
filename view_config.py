import streamlit as st # type: ignore
import yaml
from config_loader import load_and_validate_config

def convert_to_apisix_config(config):
    """Convert the custom input.yaml configuration to APISIX traffic-split config."""
    apisix_config = {
        "routes": [],
        "upstreams": []
    }

    for service in config.get("services", []):
        service_uri = service["uri"]
        default_upstream = service["default_upstream"]

        # Add upstream definitions
        for upstream in service["upstreams"]:
            apisix_config["upstreams"].append({
                "id": upstream["id"],
                "nodes": {f"{upstream['target']}:{upstream['port']}": 1},
                "type": "roundrobin"
            })

        # Handle rollstrategy or fallback to default_upstream
        rollstrategy = service.get("rollstrategy")
        if rollstrategy and "weighted_upstreams" in rollstrategy:
            traffic_rules = []
            for weighted in rollstrategy["weighted_upstreams"]:
                traffic_rules.append({
                    "upstream_id": weighted["upstream_id"],
                    "weight": weighted["weight"]
                })
        else:
            # If no rollstrategy, use default upstream
            traffic_rules = [{
                "upstream_id": default_upstream,
                "weight": 100
            }]

        # Add route for the service with traffic-split plugin
        apisix_config["routes"].append({
            "uri": service_uri,
            "plugins": {
                "traffic-split": {
                    "rules": [
                        {
                            "match": {},  # Match everything for simplicity
                            "weighted_upstreams": traffic_rules
                        }
                    ]
                }
            }
        })

    return apisix_config





st.set_page_config(page_title="Raw Configuration", layout="wide")
st.title("Raw Input Configuration")

config_file = "config/input.yaml"
# Validate and display the config
try:
    config = load_and_validate_config(config_file)
    st.code(yaml.dump(config, default_flow_style=False), language="yaml")
    apisix_config = convert_to_apisix_config(config)
    st.code(yaml.dump(apisix_config, default_flow_style=False), language="yaml")
except Exception as e:
     st.error(e)
     st.stop()  # Stop execution if the config is invalid


