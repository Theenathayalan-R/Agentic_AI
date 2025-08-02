import google.generativeai as genai
import json
import re

from config.config import settings

def generate_tags(table):
    """
    Uses the Gemini API to generate a list of tags for a table.
    """
    if not settings.ai.gemini_api_key:
        return ["mock_tag", "example_data"]

    prompt = f"""
    You are a data cataloging specialist. Based on the following table schema and column descriptions,
    provide a comma-separated list of up to 5 relevant tags. The tags should be in snake_case.
    Do not include any other text, just the tags.
    
    Table Name: {table.table_name}
    Schema: {table.schema_name}
    
    Columns:
    {json.dumps([{"name": col.column_name, "data_type": col.data_type, "description": col.description} for col in table.columns], indent=2)}
    
    Tags:
    """
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        tags_text = response.text.strip()
        tags_list = re.split(r', ?', tags_text)
        return [tag.strip().replace(' ', '_').lower() for tag in tags_list if tag]
    except Exception as e:
        print(f"Error generating tags: {e}")
        return []
