import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def generate_prompt(features):
    """
    Generate a prompt to ask the LLM to name the factor based on its features.
    """
    feature_list = "\n".join([f"- {f['feature']} (loading: {f['loading']:.4f})" for f in features])
    
    prompt = f"""You are an expert data analyst and statistician. 
A factor analysis has been performed on a dataset, and the following features have been grouped together into a single latent factor due to their high correlation (factor loadings are provided in parentheses):

{feature_list}

Your task is to analyze the semantic meaning of these features and provide a single, concise name that best represents this underlying latent factor.

You must respond ONLY with a valid JSON object in the exact following format:
{{
    "factor_name": "The short name you chose",
    "explanation": "A brief 1-2 sentence explanation of why this name represents the features."
}}
Do not include any other text, markdown formatting, or explanations outside the JSON object.
"""
    return prompt

def name_factor_with_llm(features):
    """
    Send the features to the local Ollama LLM and get the suggested name.
    
    Args:
        features (list): List of dicts with 'feature' and 'loading'.
        
    Returns:
        dict: Containing 'factor_name' and 'explanation', or fallback values if it fails.
    """
    if not features:
        return {"factor_name": "Empty Factor", "explanation": "No features met the loading threshold."}
        
    prompt = generate_prompt(features)
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=120)
        response.raise_for_status()
        
        result_json = response.json()
        response_text = result_json.get("response", "{}")
        
        # Parse the inner JSON returned by the model
        try:
            parsed_result = json.loads(response_text)
            factor_name = parsed_result.get("factor_name", "Unknown Factor")
            explanation = parsed_result.get("explanation", "No explanation provided.")
        except json.JSONDecodeError:
            # Fallback if model didn't return strict JSON despite format="json"
            factor_name = "Parsing Error"
            explanation = f"Model returned invalid JSON: {response_text}"
            
        return {
            "factor_name": factor_name,
            "explanation": explanation
        }
        
    except Exception as e:
        print(f"Lỗi khi gọi LLM: {e}")
        return {
            "factor_name": "LLM_Error_Factor",
            "explanation": f"Failed to get name from LLM. Error: {str(e)}"
        }

def name_all_factors(factor_groupings):
    """
    Iterate over all factors and call the LLM for naming.
    """
    named_factors = {}
    for original_name, features in factor_groupings.items():
        print(f"Đang phân tích ngữ nghĩa cho {original_name} với {len(features)} thuộc tính...")
        llm_result = name_factor_with_llm(features)
        
        named_factors[original_name] = {
            "llm_name": llm_result["factor_name"],
            "explanation": llm_result["explanation"],
            "features": features
        }
        
    return named_factors
