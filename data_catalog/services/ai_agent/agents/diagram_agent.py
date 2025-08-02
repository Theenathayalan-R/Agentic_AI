import google.generativeai as genai
import base64
import json
from config.config import settings

def process_data_diagram(image_data: bytes):
    """
    Uses the Gemini API to analyze a data model diagram (image or PDF)
    and extract structured metadata.
    """
    if not settings.ai.gemini_api_key:
        return {
            "tables": [
                {"table_name": "mock_users", "schema_name": "public", "columns": [
                    {"column_name": "user_id", "data_type": "int"},
                    {"column_name": "username", "data_type": "varchar"}
                ]}
            ]
        }
    
    # Encode image data to base64 for the API
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    prompt = """
    You are an expert at reading data model diagrams. Analyze the provided image and
    extract the table names, schema names, and the columns within each table.
    For each column, identify its name and data type if possible.
    Respond with a single JSON object that contains a list of tables.
    Each table should be an object with 'table_name', 'schema_name', and a list of 'columns'.
    Each column should have 'column_name' and 'data_type'.
    Example JSON format:
    {
      "tables": [
        {
          "table_name": "users",
          "schema_name": "public",
          "columns": [
            {"column_name": "user_id", "data_type": "int"},
            {"column_name": "user_name", "data_type": "varchar"}
          ]
        },
        {
          "table_name": "orders",
          "schema_name": "public",
          "columns": [
            {"column_name": "order_id", "data_type": "int"},
            {"column_name": "user_id", "data_type": "int"}
          ]
        }
      ]
    }
    """
    
    # Using the multi-modal gemini-1.5-flash model
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": base64_image}]
        )
        # Assuming the response is a JSON string
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error processing image with Gemini API: {e}")
        return {"tables": []}
