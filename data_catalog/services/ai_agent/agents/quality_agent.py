import random
import google.generativeai as genai
from config.config import settings
import json

def calculate_data_quality(table):
    """
    Uses the Gemini API or a mock function to calculate a data quality score (0-100).
    For the mock version, a random score is returned.
    """
    if not settings.ai.gemini_api_key:
        return random.randint(50, 100) # Mock response
    
    prompt = f"""
    You are an expert data quality analyst. Based on the following table and column metadata,
    provide a data quality score from 0-100. Consider factors like completeness (e.g., nullable fields),
    consistency, and descriptive column names. Provide only the integer score, nothing else.
    
    Table Name: {table.table_name}
    Schema: {table.schema_name}
    
    Columns:
    {json.dumps([{"name": col.column_name, "data_type": col.data_type, "description": col.description} for col in table.columns], indent=2)}
    
    Data Quality Score (0-100):
    """

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        score_text = response.text.strip()
        return int(score_text) if score_text.isdigit() else 0
    except Exception as e:
        print(f"Error calculating data quality: {e}")
        return 0
