import streamlit as st # type: ignore
from config_loader import load_and_validate_config, ConfigValidationError


pages = {
    "View": [
        st.Page("view_services.py", title="View Services"),
        st.Page("view_config.py", title="View Configuration YAML"),
    ],
    "Configurations": [
        #st.Page("config.py", title="Configure Service"),
    ],
    "Troubleshoot": [
        st.Page("validate_config.py", title="Validate Configuration YAML"),
        st.Page("diff_config.py", title="Diff Configuration YAML"),
    ]
}

pg = st.navigation(pages)
pg.run()
