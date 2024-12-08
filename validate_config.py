import os
import yaml
import streamlit as st # type: ignore
from config_loader import load_and_validate_config, ConfigValidationError

def list_yaml_files(directory):
    """List all YAML files in a given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.yaml')]

def validation_page():
    st.title("Configuration Validation")

    config_directory = "./config"
    yaml_files = list_yaml_files(config_directory)

    if not yaml_files:
        st.error("No YAML files found in the /config directory.")
        return

    # Step 1: Select file
    st.header("Select Configuration File")
    selected_file = st.selectbox("Choose a file to validate:", yaml_files)

    if st.button("Validate Configuration"):
        file_path = os.path.join(config_directory, selected_file)

        # Step 3: Validate and Show Results
        st.header("Validation Results")
        try:
            config = load_and_validate_config(file_path)
            st.success("PASS: Configuration is valid.")
            st.code(yaml.dump(config, default_flow_style=False), language="yaml")
        except ConfigValidationError as e:
            st.error("FAILED: Configuration Validation Error.")
            st.code(str(e))
        except Exception as e:
            st.error("FAILED: Unexpected Error.")
            st.code(str(e))

validation_page()