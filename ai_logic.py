import google.generativeai as genai
from data_models import MaterialOrder


def parse_request_with_ai(request_text: str, api_key: str) -> MaterialOrder:
    genai.configure(api_key=api_key)

    model_name = "gemini-2.5-flash"

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": MaterialOrder
        }
    )

    prompt = f"""
    Jsi expert na kovovýrobu. Extrahuj data pro nářezový plán do JSONu.

    Pravidla:
    1. Převáděj všechny jednotky na milimetry.
    2. Hledej informace o tom, jaké tyče mám SKLADEM (k dispozici). Pokud uživatel zmíní více délek, dej je do seznamu.
    3. DŮLEŽITÉ: Pokud uživatel neuvede žádnou skladovou délku, MUSÍŠ do 'stock_lengths_mm' dát [6000].
    4. DŮLEŽITÉ: Pokud chybí název (label), vyplň 'label' jako "Bez názvu".
    5. DŮLEŽITÉ: Pokud chybí typ materiálu, vyplň 'material_type' jako "Neznámý materiál".

    Zadání: "{request_text}"
    """

    response = model.generate_content(prompt)
    return MaterialOrder.model_validate_json(response.text)


def list_available_models(api_key: str):
    genai.configure(api_key=api_key)
    return genai.list_models()