# app.py
import streamlit as st
import pandas as pd
import requests
import os
import time

# --- Configuration ---
# Set the API endpoint. The os.getenv call allows this to be configured via
# an environment variable, with a fallback to a default localhost URL.
METADATA_API_URL = os.getenv("METADATA_API_URL", "http://localhost:8000/api/v1")

# --- Custom CSS for a professional, uniform dark theme and new layout ---
st.markdown(
    """
    <style>
    /* Make the main content area wider */
    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Adjust font sizes and colors for a clean look on a dark background */
    body {
        font-family: Arial, sans-serif;
        color: #e9ecef; /* Light gray for main text */
        font-size: 0.95rem; /* Smaller body font size */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f8f9fa; /* Lighter text for headers */
        font-weight: 600;
    }
    h1 {
        font-size: 2rem; /* Smaller h1 font size */
        border-bottom: 2px solid #495057; /* Subtle gray border */
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    h2 { font-size: 1.75rem; } /* Smaller h2 font size */
    h3 { font-size: 1.5rem; }  /* Smaller h3 font size */
    h4 { font-size: 1.25rem; } /* Smaller h4 font size */
    
    /* General body background and container styling for dark theme */
    .main {
        background-color: #212529; /* Dark background */
        color: #e9ecef;
    }
    .stApp {
        background-color: #212529;
    }
    
    /* Streamlit-specific element styling for dark theme */
    .stMarkdown, .stText, .stButton, .st-bh, .st-bj {
        color: #e9ecef;
    }
    .stSelectbox label, .stTextArea label {
        color: #ced4da !important;
    }
    
    /* Style for info boxes (like current glossary) */
    .stAlert {
        background-color: #343a40; /* Darker gray background */
        border-left: 5px solid #6c757d; /* Dark gray border */
        color: #e9ecef;
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 5px;
        font-size: 0.9em;
    }
    
    /* General style for our new table-like layout */
    .table-container {
        border: 1px solid #495057;
        border-radius: 8px;
        background-color: #2c3138;
        padding: 0;
        margin-bottom: 20px;
    }

    .table-header {
        display: flex;
        font-weight: bold;
        background-color: #343a40;
        padding: 15px;
        border-bottom: 1px solid #495057;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    
    /* Small adjustment to the header to account for the new column */
    .table-header.datasets {
        display: grid;
        grid-template-columns: 1fr 2fr 0.8fr;
        align-items: center;
    }
    
    .table-header.domains {
        display: grid;
        grid-template-columns: 1fr 2fr 0.8fr;
        align-items: center;
    }
    
    .table-row-clickable {
        position: relative;
        padding: 15px;
        border-bottom: 1px solid #495057;
        cursor: pointer;
        transition: background-color 0.2s;
        display: grid;
        grid-template-columns: 1fr 2fr 0.8fr;
        align-items: center;
    }
    .table-row-clickable:hover {
        background-color: #343a40; /* Hover color */
    }

    /* Remove the bottom border for the last row */
    .table-container .table-row-clickable:last-child {
        border-bottom: none;
    }

    /* Style for the invisible button that covers the entire row */
    .table-row-clickable .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        z-index: 1; /* Place button on top of the card content */
        cursor: pointer;
    }

    /* Adjust padding for columns inside the row */
    .table-row-clickable .st-emotion-cache-16txte9 { /* Streamlit column class */
        padding-left: 0;
        padding-right: 0;
    }
    
    /* Adjust text areas within our custom table */
    .stTextArea [data-baseweb="textarea"] {
        background-color: #495057; /* Dark gray input background */
        border: 1px solid #6c757d; /* Light gray border */
        border-radius: 5px;
        padding: 5px 10px;
        color: #e9ecef;
    }
    .stTextArea [data-baseweb="textarea"]:focus-within {
        border-color: #adb5bd; /* Lighter gray on focus */
        box-shadow: 0 0 0 0.1rem rgba(173, 181, 189, 0.25);
    }
    
    /* Fix for text area padding causing misalignment */
    .stTextArea div[data-baseweb="base-input"] {
        margin: 0;
        padding: 0;
    }
    .stTextArea textarea {
        min-height: 20px !important;
        height: 20px !important;
        font-size: 14px;
    }
    
    /* Input field styling (for search box) */
    .stTextInput [data-baseweb="base-input"] {
        background-color: #495057; /* Dark gray input background */
        border: 1px solid #6c757d;
        border-radius: 5px;
        padding: 5px 10px;
        color: #e9ecef;
    }
    .stTextInput [data-baseweb="base-input"]:focus-within {
        border-color: #adb5bd;
        box-shadow: 0 0 0 0.1rem rgba(173, 181, 189, 0.25);
    }

    /* Button styling for a professional, uniform look */
    .stButton>button {
        background-color: #495057; /* Dark gray */
        color: #e9ecef; /* Light gray text */
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        transition: background-color 0.2s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    /* Specific styling for the 'Back to Home' button to make it stand out */
    .stButton>button[kind="secondary"] {
        background-color: #6c757d; /* A more visible gray for the back button */
        color: #f8f9fa; /* Lighter text */
    }
    .stButton>button:hover {
        background-color: #6c757d; /* Slightly lighter gray on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API Client Functions ---
# Functions to interact with the FastAPI backend.
def get_domains():
    try:
        response = requests.get(f"{METADATA_API_URL}/domains")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching domains: {e}")
        return []

def get_datasets_by_domain(domain_id):
    try:
        response = requests.get(f"{METADATA_API_URL}/datasets/by-domain/{domain_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching datasets for domain {domain_id}: {e}")
        return []

def get_dataset_metadata(dataset_id):
    try:
        response = requests.get(f"{METADATA_API_URL}/datasets/{dataset_id}/metadata")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching metadata for dataset {dataset_id}: {e}")
        return None

def submit_feedback(feedback_data):
    try:
        response = requests.post(f"{METADATA_API_URL}/feedback", json=feedback_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error submitting feedback for '{feedback_data.get('column_name', 'Unknown')}': {e}")
        return None

def get_all_feedback():
    try:
        response = requests.get(f"{METADATA_API_URL}/feedback")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching feedback list: {e}")
        return []

# --- State Management ---
# Initialize session state variables for navigation and data.
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'
if 'selected_domain_id' not in st.session_state:
    st.session_state.selected_domain_id = None
if 'selected_dataset_id' not in st.session_state:
    st.session_state.selected_dataset_id = None


# --- Sidebar Navigation and Search ---
with st.sidebar:
    st.header("Navigation")
    if st.button("🏠 Home", key="nav_home"):
        st.session_state.current_view = 'home'
        st.session_state.selected_domain_id = None
        st.session_state.selected_dataset_id = None
        st.rerun()
    if st.button("💬 View Feedback", key="nav_feedback"):
        st.session_state.current_view = 'feedback_list'
        st.session_state.selected_domain_id = None
        st.session_state.selected_dataset_id = None
        st.rerun()
    
    st.markdown("---")
    st.header("Search Data")
    search_query = st.text_input("Search domains, products, datasets...", key="search_bar").lower()

    # Fetch data for search filtering
    all_domains = get_domains()
    all_datasets = []
    for domain in all_domains:
        all_datasets.extend(get_datasets_by_domain(domain['domain_id']))

    # Filter domains and datasets based on search query
    filtered_domains = [
        d for d in all_domains
        if search_query in d['domain_name'].lower() or search_query in d['description'].lower()
    ]

    filtered_datasets = [
        ds for ds in all_datasets
        if search_query in ds['table_name'].lower() or search_query in ds['description'].lower()
    ]

    st.subheader("Search Results")
    if not search_query:
        st.info("Start typing to search.")
    elif not filtered_domains and not filtered_datasets:
        st.warning("No matching domains or datasets found.")
    else:
        if filtered_domains:
            st.markdown("#### Domains")
            for d in filtered_domains:
                if st.button(f"🌐 {d['domain_name']}", key=f"search_domain_{d['domain_id']}"):
                    st.session_state.current_view = 'home'
                    st.rerun()
        if filtered_datasets:
            st.markdown("#### Datasets")
            for ds in filtered_datasets:
                domain_name = next((d['domain_name'] for d in all_domains if d['domain_id'] == ds['domain_id']), "Unknown")
                if st.button(f"📊 {ds['table_name']} ({domain_name})", key=f"search_dataset_{ds['dataset_id']}"):
                    st.session_state.current_view = 'metadata'
                    st.session_state.selected_dataset_id = ds['dataset_id']
                    st.rerun()


# --- UI Functions ---
# A new reusable function to render the table-like list view
def render_list_view(items, item_type):
    """
    Renders a clickable list view for a given list of items (domains or datasets).
    """
    if not items:
        st.info(f"No {item_type} found.")
        return

    # Use a table-like layout
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    
    # Header row
    col1, col2, col3 = st.columns([1, 2, 0.8])
    with col1:
        st.markdown(f'<div class="table-header {item_type}">Name</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="table-header {item_type}">Description</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="table-header {item_type}">Last Updated</div>', unsafe_allow_html=True)

    # Data rows
    for item in items:
        st.markdown(f'<div class="table-row-clickable">', unsafe_allow_html=True)
        row_col1, row_col2, row_col3 = st.columns([1, 2, 0.8])
        
        item_name = item.get('domain_name') if item_type == 'domains' else item.get('table_name')
        item_id = item.get('domain_id') if item_type == 'domains' else item.get('dataset_id')
        item_description = item.get('description')
        # Placeholder for last updated time, assuming the API would provide this
        last_updated = item.get('last_updated', '2023-10-27')
        
        with row_col1:
            icon = "🌐" if item_type == 'domains' else "📊"
            st.markdown(f"**{icon} {item_name}**")
        with row_col2:
            st.markdown(item_description)
        with row_col3:
            st.markdown(f"*{last_updated}*")
        
        # This invisible button makes the entire row clickable
        if st.button(" ", key=f"{item_type}_row_{item_id}", use_container_width=True):
            if item_type == 'domains':
                st.session_state.current_view = 'domain_datasets'
                st.session_state.selected_domain_id = item_id
            else: # datasets
                st.session_state.current_view = 'metadata'
                st.session_state.selected_dataset_id = item_id
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def show_home_page():
    st.title("Data Catalog Service")
    st.write("Browse various data domains, data products and datasets available in the data lakehouse.")

    st.subheader("Data Domains")
    domains = get_domains()
    # The get_domains function now returns a list of dictionaries with placeholder last_updated
    # This simulates a real API response.
    domains_with_dates = [
        {**d, 'last_updated': '2023-10-27'} for d in domains
    ]
    render_list_view(domains_with_dates, 'domains')


def show_domain_datasets_page():
    domain_id = st.session_state.selected_domain_id
    if domain_id is None:
        st.error("No domain selected.")
        return

    # Get the domain details from the full list
    domains = get_domains()
    domain = next((d for d in domains if d['domain_id'] == domain_id), None)
    if not domain:
        st.error(f"Domain with ID {domain_id} not found.")
        return

    # Add a Back button
    if st.button("⬅️ Back to Domains", key="back_to_domains", type="secondary"):
        st.session_state.current_view = 'home'
        st.session_state.selected_domain_id = None
        st.rerun()

    st.title(f"Datasets in '{domain['domain_name']}'")
    st.write(domain['description'])
    
    datasets = get_datasets_by_domain(domain_id)
    # Adding placeholder dates for demonstration
    datasets_with_dates = [
        {**ds, 'last_updated': '2023-10-27'} for ds in datasets
    ]
    render_list_view(datasets_with_dates, 'datasets')


def handle_feedback_submit(dataset_id, meta_df):
    feedback_items_to_submit = []
    
    general_notes_key = f"general_feedback_notes_{dataset_id}"
    general_notes = st.session_state.get(general_notes_key, "")

    for _, row in meta_df.iterrows():
        col_name = row['column_name']
        current_glossary = row['business_glossary']
        feedback_key = f"feedback_text_{dataset_id}_{col_name}"
        suggested_glossary = st.session_state.get(feedback_key, "").strip()

        if suggested_glossary:
            feedback_items_to_submit.append({
                "dataset_id": dataset_id,
                "column_name": col_name,
                "current_glossary": current_glossary,
                "suggested_glossary": suggested_glossary,
                "notes": general_notes
            })
    
    if not feedback_items_to_submit:
        st.warning("No feedback was provided for any column. Nothing to submit.")
    else:
        success_count = 0
        for item in feedback_items_to_submit:
            response_data = submit_feedback(item)
            if response_data:
                success_count += 1
        
        if success_count > 0:
            st.success(f"Successfully submitted {success_count} feedback items!")
            st.balloons()
            
            for item in feedback_items_to_submit:
                key = f"feedback_text_{dataset_id}_{item['column_name']}"
                st.session_state[key] = ""
            st.session_state[general_notes_key] = ""
        else:
            st.error("Failed to submit any feedback items.")


def show_metadata_page():
    dataset_id = st.session_state.selected_dataset_id
    if dataset_id is None:
        st.error("No dataset selected. Please go back to Home or use the search bar.")
        return

    metadata = get_dataset_metadata(dataset_id)
    if not metadata:
        st.error(f"Could not retrieve metadata for dataset ID: {dataset_id}")
        return

    # Add a Back button at the top of the page
    if st.button("⬅️ Back to Home", key="back_to_home_button", type="secondary"):
        st.session_state.current_view = 'home'
        st.session_state.selected_dataset_id = None
        st.rerun()

    st.title(f"Metadata for '{metadata['dataset_name']}'")
    st.markdown(f"**Domain:** {metadata['domain_name']}")
    st.markdown(f"**Description:** {metadata['description']}")
    
    meta_df = pd.DataFrame(metadata['columns'])

    st.subheader("Schema and Glossary")
    st.write("Is something incorrect or missing? Please suggest corrections in the table below.")

    if meta_df.empty:
        st.warning("No columns available to provide feedback.")
        return

    with st.form(key='inline_feedback_form'):
        
        col_name_h, data_type_h, tech_desc_h, glossary_h, feedback_h = st.columns([1.5, 0.8, 2, 2.5, 2.5])
        with col_name_h:
            st.markdown("#### Column Name")
        with data_type_h:
            st.markdown("#### Data Type")
        with tech_desc_h:
            st.markdown("#### Technical Description")
        with glossary_h:
            st.markdown("#### Business Glossary")
        with feedback_h:
            st.markdown("#### Your Suggestion")
        
        st.markdown("---")

        for _, row in meta_df.iterrows():
            col_name = row['column_name']
            feedback_key = f"feedback_text_{dataset_id}_{col_name}"
            col_name_c, data_type_c, tech_desc_c, glossary_c, feedback_c = st.columns([1.5, 0.8, 2, 2.5, 2.5])

            with col_name_c:
                st.markdown(f"**{col_name}**")
            with data_type_c:
                st.markdown(f"`{row['data_type']}`")
            with tech_desc_c:
                st.markdown(f"<div style='height: 50px; overflow-y: auto;'>{row['technical_description']}</div>", unsafe_allow_html=True)
            with glossary_c:
                st.markdown(f"<div style='height: 50px; overflow-y: auto;'>{row['business_glossary']}</div>", unsafe_allow_html=True)
            with feedback_c:
                if feedback_key not in st.session_state:
                    st.session_state[feedback_key] = ""
                
                st.text_area(
                    " ",
                    value=st.session_state[feedback_key],
                    height=20,
                    key=feedback_key
                )
        
        st.markdown("---")
        
        general_notes_key = f"general_feedback_notes_{dataset_id}"
        if general_notes_key not in st.session_state:
            st.session_state[general_notes_key] = ""
        st.text_area(
            "Overall Notes for this Feedback Submission (optional):",
            value=st.session_state[general_notes_key],
            key=general_notes_key
        )

        st.form_submit_button(
            "Submit All Feedback", 
            on_click=handle_feedback_submit, 
            args=(dataset_id, meta_df)
        )


def show_feedback_list_page():
    st.title("User Feedback on Glossary")
    st.write("Review submitted suggestions for business glossary corrections.")

    feedback_entries = get_all_feedback()
    if not feedback_entries:
        st.info("No feedback has been submitted yet.")
        return

    feedback_df = pd.DataFrame(feedback_entries)
    
    if 'status' not in feedback_df.columns:
        feedback_df['status'] = "Unknown"
    
    status_filter = st.selectbox(
        "Filter by Status:",
        options=["All"] + sorted(feedback_df['status'].unique().tolist()),
        key="feedback_status_filter"
    )

    if status_filter != "All":
        feedback_df = feedback_df[feedback_df['status'] == status_filter]

    if feedback_df.empty:
        st.info(f"No feedback found with status '{status_filter}'.")
        return

    st.dataframe(feedback_df[[
        'submitted_date', 'dataset_id', 'column_name',
        'current_glossary', 'suggested_glossary', 'status', 'notes', 'submitted_by'
    ]], use_container_width=True)

    st.subheader("Feedback Management Notes:")
    st.info("In a real application, data stewards would have a UI here to update the status of feedback entries (e.g., Approve/Reject), potentially edit the glossary in the backend, and notify the original submitter. This requires dedicated API endpoints for status updates and possibly admin authentication.")


# --- Main App Logic ---
# The main flow of the application, routing based on session state.
if st.session_state.current_view == 'home':
    show_home_page()
elif st.session_state.current_view == 'domain_datasets':
    show_domain_datasets_page()
elif st.session_state.current_view == 'metadata':
    show_metadata_page()
elif st.session_state.current_view == 'feedback_list':
    show_feedback_list_page()
