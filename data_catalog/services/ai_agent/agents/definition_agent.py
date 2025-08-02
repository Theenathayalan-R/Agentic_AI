import google.generativeai as genai
import json

from config.config import settings

def generate_business_definition(table):
    """
    Uses the Gemini API to generate a business definition for a table.
    """
    if not settings.ai.gemini_api_key:
        return "Mock business definition for the table."

    prompt = f"""
    You are an expert data analyst. Based on the following table schema and column descriptions,
    provide a concise and clear business definition for the table. The definition should be 1-2 sentences.
    
    Table Name: {table.table_name}
    Schema: {table.schema_name}
    
    Columns:
    {json.dumps([{"name": col.column_name, "data_type": col.data_type, "description": col.description} for col in table.columns], indent=2)}
    
    Business Definition:
    """
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating definition: {e}")
        return "Could not generate business definition."
