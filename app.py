import streamlit as st # type: ignore
from config_loader import load_and_validate_config, ConfigValidationError


pages = {
    "Task": [
        #st.Page("config.py", title="Configure Service"),
        st.Page("new_upstream.py", title="Configure Upstream"),
    ],

    "View": [
        st.Page("view_services.py", title="View Services"),
        st.Page("view_config.py", title="View Configuration YAML"),
    ],
    "Troubleshoot": [
        st.Page("validate_config.py", title="Validate Configuration YAML"),
        st.Page("diff_config.py", title="Diff Configuration YAML"),
    ]
}

pg = st.navigation(pages)
pg.run()
