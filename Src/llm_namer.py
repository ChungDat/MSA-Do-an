import json
import os

import requests
from dotenv import load_dotenv


load_dotenv()

OLLAMA_ENDPOINT = os.getenv(
    "OLLAMA_ENDPOINT", "http://localhost:11434/api/generate"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def generate_prompt(features):
    feature_list = "\n".join(
        f"- {item['feature']} (loading: {item['loading']:.4f})"
        for item in features
    )
    return f"""You are an expert data analyst and statistician.
Name the latent factor represented by these features:

{feature_list}

Respond ONLY with a valid JSON object:
{{
  "factor_name": "A concise factor name",
  "explanation": "A brief 1-2 sentence explanation."
}}"""


def name_factor_with_llm(features):
    if not features:
        return {
            "factor_name": "Empty Factor",
            "explanation": "No features met the loading threshold.",
        }

    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            json={
                "model": OLLAMA_MODEL,
                "prompt": generate_prompt(features),
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )
        response.raise_for_status()
        result = json.loads(response.json().get("response", "{}"))
        return {
            "factor_name": result.get("factor_name", "Unknown Factor"),
            "explanation": result.get("explanation", "No explanation provided."),
        }
    except Exception as exc:
        print(f"Lỗi khi gọi LLM: {exc}")
        return {
            "factor_name": "LLM_Error_Factor",
            "explanation": f"Failed to get name from LLM. Error: {exc}",
        }


def name_all_factors(factor_groupings):
    named_factors = {}
    for original_name, features in factor_groupings.items():
        print(
            f"Đang phân tích ngữ nghĩa cho {original_name} "
            f"với {len(features)} thuộc tính..."
        )
        llm_result = name_factor_with_llm(features)
        named_factors[original_name] = {
            "llm_name": llm_result["factor_name"],
            "explanation": llm_result["explanation"],
            "features": features,
        }
    return named_factors
