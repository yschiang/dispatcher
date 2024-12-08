import os
import streamlit as st # type: ignore
from config_loader import load_and_validate_config, ConfigValidationError
import yaml
from deepdiff import DeepDiff # type: ignore

def list_yaml_files(directory):
    """List all YAML files in a given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.yaml')]

def diff_yaml_files(file1, file2):
    """Diff two YAML files and return the differences."""
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            yaml1 = yaml.safe_load(f1)
            yaml2 = yaml.safe_load(f2)
            diff = DeepDiff(yaml1, yaml2, ignore_order=True, report_repetition=True)
            return diff
    except Exception as e:
        raise ConfigValidationError(f"Error diffing files: {str(e)}")

def categorize_diffs_by_object_and_type(diff):
    """Organize differences by object types and categorize them as added, removed, or changed."""
    categorized = {
        "Added": {},
        "Removed": {},
        "Changed": {}
    }

    if 'dictionary_item_added' in diff:
        for item in diff['dictionary_item_added']:
            path = str(item)
            category = extract_object_type(path)
            if category not in categorized["Added"]:
                categorized["Added"][category] = []
            categorized["Added"][category].append(path)

    if 'dictionary_item_removed' in diff:
        for item in diff['dictionary_item_removed']:
            path = str(item)
            category = extract_object_type(path)
            if category not in categorized["Removed"]:
                categorized["Removed"][category] = []
            categorized["Removed"][category].append(path)

    if 'values_changed' in diff:
        for key, value in diff['values_changed'].items():
            path = str(key)
            category = extract_object_type(path)
            if category not in categorized["Changed"]:
                categorized["Changed"][category] = []
            categorized["Changed"][category].append({
                "property": path.split(".")[-1],  # Extract only the last part of the path
                "old_value": value['old_value'],
                "new_value": value['new_value']
            })

    return categorized

def extract_object_type(path):
    """Extract the object type (e.g., services, matches, rollstrategy) from the path."""
    if "services" in path:
        return "services"
    if "matches" in path:
        return "matches"
    if "rollstrategy" in path:
        return "rollstrategy"
    if "rules" in path:
        return "rules"
    if "upstreams" in path:
        return "upstreams"
    return "unknown"

def format_diff_for_humans(categorized):
    """Create a human-readable format of the categorized differences."""
    lines = []

    for change_type, objects in categorized.items():
        lines.append(f"### {change_type}:")
        for obj_type, changes in objects.items():
            lines.append(f"- {obj_type.capitalize()}:")
            for change in changes:
                if isinstance(change, dict):  # For changed values
                    lines.append(f"  - Property `{change['property']}`: {change['old_value']} -> {change['new_value']}")
                else:
                    lines.append(f"  - {change}")

    return "\n".join(lines)

def diff_page():
    st.title("Configuration Diff Tool")

    config_directory = "./config"
    yaml_files = list_yaml_files(config_directory)

    if not yaml_files:
        st.error("No YAML files found in the /config directory.")
        return

    # Step 1: Select two files to compare
    st.header("Step 1: Select Files to Compare")
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.selectbox("Select the first file:", yaml_files, key="file1")
    with col2:
        file2 = st.selectbox("Select the second file:", yaml_files, key="file2")

    # Step 2: Compare and show results
    if st.button("Compare Files"):
        file1_path = os.path.join(config_directory, file1)
        file2_path = os.path.join(config_directory, file2)

        try:
            diff = diff_yaml_files(file1_path, file2_path)
            if not diff:
                st.success("The files are identical.")
            else:
                st.warning("Differences found between the files:")

                # Categorize and display differences
                categorized = categorize_diffs_by_object_and_type(diff)
                human_readable_diff = format_diff_for_humans(categorized)
                st.text_area("Human-Readable Differences by Object and Type:", human_readable_diff, height=300)

                # Display JSON output for API use
                st.subheader("API JSON Output by Object and Type")
                st.json(categorized)
        except ConfigValidationError as e:
            st.error("Error comparing files.")
            st.code(str(e))
        except Exception as e:
            st.error("Unexpected Error during file comparison.")
            st.code(str(e))

diff_page()
