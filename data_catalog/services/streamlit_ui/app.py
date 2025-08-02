import streamlit as st
import requests
import pandas as pd
import json
from shared.database import SessionLocal, engine, Base
from shared.models import TableMetadata, ColumnMetadata, LineageMetadata
from config.config import settings

# Initialize database
Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="Data Catalog System", layout="wide")

# --- UI Layout ---
st.title("📊 Intelligent Data Catalog System")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Catalog", "Ingest Data", "AI Agents", "API Docs"])

# --- Ingest Data Page ---
if page == "Ingest Data":
    st.header("Ingest New Metadata")
    
    # Dynamically generate the data source list from config
    source_options = {source.name: source.type for source in settings.data_sources}
    selected_source_name = st.selectbox("Select Data Source", list(source_options.keys()))
    selected_source_type = source_options.get(selected_source_name)

    if selected_source_type == "excel":
        uploaded_file = st.file_uploader(f"Upload an Excel file (.xlsx) for {selected_source_name}", type=['xlsx'])
        if uploaded_file:
            if st.button("Process Excel"):
                with st.spinner("Processing Excel file..."):
                    files = {'file': uploaded_file.getvalue()}
                    response = requests.post(f"{settings.services.metadata_processor}/process/excel", files=files)
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not process file.')}")
    
    elif selected_source_type == "sql_ddl":
        uploaded_file = st.file_uploader(f"Upload a SQL DDL file (.sql) for {selected_source_name}", type=['sql'])
        if uploaded_file:
            if st.button("Process SQL DDL"):
                with st.spinner("Processing SQL DDL file..."):
                    files = {'file': uploaded_file.getvalue()}
                    response = requests.post(f"{settings.services.metadata_processor}/process/sql-ddl/{selected_source_name}", files=files)
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not process file.')}")

    elif selected_source_type == "starburst":
        if st.button(f"Fetch from {selected_source_name}"):
            with st.spinner(f"Connecting to {selected_source_name} and fetching metadata..."):
                response = requests.post(f"{settings.services.metadata_processor}/process/starburst/{selected_source_name}")
                if response.status_code == 200:
                    st.success(response.json()['message'])
                else:
                    st.error(f"Error: {response.json().get('detail', 'Could not connect to Starburst.')}")
    
    elif selected_source_type == "image_diagram":
        uploaded_file = st.file_uploader(f"Upload a Data Model Diagram (JPEG, PNG, PDF) for {selected_source_name}", type=['jpg', 'jpeg', 'png', 'pdf'])
        if uploaded_file:
            if st.button("Process Diagram"):
                with st.spinner("Processing diagram with AI..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{settings.services.metadata_processor}/process/image-diagram", files=files)
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not process diagram with AI.')}")

    elif selected_source_type in ["sql_lineage", "pyspark_sql"]:
        file_extension = '.sql' if selected_source_type == 'sql_lineage' else '.py'
        uploaded_file = st.file_uploader(f"Upload a {selected_source_type} file ({file_extension}) for lineage analysis", type=[file_extension.strip('.')])
        if uploaded_file:
            if st.button(f"Process Lineage from {selected_source_name}"):
                with st.spinner(f"Analyzing {selected_source_type} code for data lineage..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{settings.services.metadata_processor}/process/lineage-code/{selected_source_type}/{selected_source_name}", files=files)
                    if response.status_code == 200:
                        st.success(response.json()['message'])
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not process lineage.')}")

# --- Catalog Page ---
if page == "Catalog":
    st.header("Search and Explore Catalog")
    search_query = st.text_input("Search for tables or columns...")
    
    if search_query:
        st.write(f"Showing results for: **{search_query}**")
        
    db = SessionLocal()
    try:
        tables = db.query(TableMetadata).all()
        lineage_data = db.query(LineageMetadata).all()
        
        if not tables:
            st.info("No metadata found. Please ingest some data first.")
        else:
            for table in tables:
                st.subheader(f"{table.schema_name}.{table.table_name}")
                if table.business_definition:
                    st.write(f"**Business Definition:** {table.business_definition}")
                
                if table.tags:
                    st.write(f"**Tags:** {', '.join(table.tags)}")

                sources = [lineage.source_table.table_name for lineage in table.target_lineage]
                targets = [lineage.target_table.table_name for lineage in table.source_lineage]
                
                if sources:
                    st.write(f"**Upstream Dependencies:** {', '.join(sources)}")
                if targets:
                    st.write(f"**Downstream Dependencies:** {', '.join(targets)}")

                if st.button(f"View Columns for {table.table_name}", key=f"view_cols_{table.id}"):
                    columns_data = []
                    for col in table.columns:
                        columns_data.append({
                            "Column Name": col.column_name,
                            "Data Type": col.data_type,
                            "Description": col.description
                        })
                    st.table(pd.DataFrame(columns_data))
                    
                st.markdown("---")
    finally:
        db.close()
        
# --- AI Agents Page ---
if page == "AI Agents":
    st.header("Manage AI Agents")
    
    db = SessionLocal()
    tables = db.query(TableMetadata).all()
    if not tables:
        st.info("No tables to process. Please ingest metadata first.")
    else:
        table_options = {f"{t.schema_name}.{t.table_name}": t.id for t in tables}
        selected_table_name = st.selectbox("Select a table to process with AI", list(table_options.keys()))
        selected_table_id = table_options[selected_table_name]
        
        if st.button("Generate Definitions"):
            with st.spinner("Generating business definitions..."):
                selected_table = db.query(TableMetadata).filter_by(id=selected_table_id).first()
                if selected_table:
                    payload = {"table_name": selected_table.table_name, "schema_name": selected_table.schema_name}
                    response = requests.post(f"{settings.services.ai_agent}/generate-definitions", json=payload)
                    if response.status_code == 200:
                        st.success("Definitions generated successfully!")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not generate definitions.')}")
                else:
                    st.error("Selected table not found in database.")

        if st.button("Calculate Data Quality"):
            with st.spinner("Calculating data quality..."):
                selected_table = db.query(TableMetadata).filter_by(id=selected_table_id).first()
                if selected_table:
                    payload = {"table_name": selected_table.table_name, "schema_name": selected_table.schema_name}
                    response = requests.post(f"{settings.services.ai_agent}/calculate-quality", json=payload)
                    if response.status_code == 200:
                        st.success("Data quality score calculated!")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not calculate quality.')}")
                else:
                    st.error("Selected table not found in database.")
                    
        if st.button("Generate Tags"):
            with st.spinner("Generating tags..."):
                selected_table = db.query(TableMetadata).filter_by(id=selected_table_id).first()
                if selected_table:
                    payload = {"table_name": selected_table.table_name, "schema_name": selected_table.schema_name}
                    response = requests.post(f"{settings.services.ai_agent}/generate-tags", json=payload)
                    if response.status_code == 200:
                        st.success("Tags generated successfully!")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Could not generate tags.')}")
                else:
                    st.error("Selected table not found in database.")

    db.close()

# --- API Docs Page ---
if page == "API Docs":
    st.header("API Documentation")
    st.info("The API documentation is available at the `/docs` endpoint for each service.")
    st.markdown(f"- **Metadata Processor**: [{settings.services.metadata_processor}/docs]({settings.services.metadata_processor}/docs)")
    st.markdown(f"- **AI Agent**: [{settings.services.ai_agent}/docs]({settings.services.ai_agent}/docs)")
    st.markdown(f"- **Catalog API**: [{settings.services.catalog_api}/docs]({settings.services.catalog_api}/docs)")

