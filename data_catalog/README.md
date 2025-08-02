Intelligent Data Catalog Service
This guide provides step-by-step instructions to set up and run the Intelligent Data Catalog Service locally on your Mac.

Prerequisites

Python 3.9+: The project requires a recent version of Python.

Gemini API Key: You must have a Gemini API key to enable the AI functionalities.

1. Setup and Installation

Follow these steps to prepare your environment and install the necessary dependencies.

Navigate to the project directory where you saved all the files.

Create a virtual environment: It's best practice to use a virtual environment to manage project dependencies.

python3 -m venv venv

Activate the virtual environment:

source venv/bin/activate

Install dependencies: Use the requirements.txt file to install everything the project needs.

pip install -r requirements.txt

Configure the service:

Rename the example configuration file:

mv config/config.yaml.example config/config.yaml

Open config/config.yaml in a text editor.

Find the line gemini_api_key: "your-gemini-api-key-here" and replace the placeholder with your actual API key.

2. Running the Services

The project is composed of several microservices that need to be run concurrently. Open three separate terminal windows and follow these instructions. Make sure your virtual environment is active in each one.

Terminal 1: Run the AI Agent

This service handles all interactions with the Gemini API.

cd data_catalog

PYTHONPATH=$PWD

uvicorn services.ai_agent.app:app --host 0.0.0.0 --port 8002 --reload

Terminal 2: Run the Metadata Processor

This service handles all data ingestion and storage logic.

cd data_catalog

PYTHONPATH=$PWD

uvicorn services.metadata_processor.app:app --host 0.0.0.0 --port 8001 --reload

Terminal 3: Run the Streamlit UI

This is the front-end application that you will interact with.

cd data_catalog

PYTHONPATH=$PWD

streamlit run services/streamlit_ui/app.py

After running the Streamlit command, your default web browser should automatically open a new tab with the UI. If not, open your browser and go to http://localhost:8501.

3. Using the Application

Once the UI is open, you can start using the data catalog:

Ingest Data: Go to the Ingest Data page and use the dropdown menu to select a data source. Upload a file or click a button to begin the ingestion process.

Explore Catalog: The Catalog page allows you to search for and view the metadata of your ingested data, including AI-generated definitions and tags.

Run AI Agents: The AI Agents page allows you to manually trigger the AI to enrich your data, generating definitions, quality scores, and tags for the tables.

