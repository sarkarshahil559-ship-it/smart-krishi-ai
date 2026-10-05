import base64
import io
import json
import os

from PIL import Image
from openai import OpenAI


# ============================================================
# SMART KRISHI AI
# OpenAI Vision Crop Analysis
# ============================================================

ALLOWED_CROPS = [
    "onion",
    "brinjal",
    "carrot",
    "chilli",
    "cucumber",
    "potato",
    "tomato",
    "maize",
    "rice",
    "wheat"
]


PROMPT = """
You are the crop-image analysis system for SMART KRISHI AI,
an agriculture assistant designed for farmers in India,
especially West Bengal.

Analyze the uploaded image carefully.

IMPORTANT:
- Identify the crop/product visible in the image.
- Do NOT guess from background alone.
- Consider shape, colour, texture, size, leaves, stem,
  fruit, vegetable, grain, cob and plant structure.
- The image may show a harvested crop OR a crop plant.
- Lighting and background may be different.
- If the image is unclear, reduce confidence.

Allowed crop names ONLY:
onion, brinjal, carrot, chilli, cucumber,
potato, tomato, maize, rice, wheat

West Bengal visual guidance:

ONION:
- Round/bulb-shaped
- Medium to large
- Golden-brown outer skin
- White interior when cut

BRINJAL:
- Oval or round
- Medium sized
- Usually dark purple
- Green stem/calyx

CARROT:
- Long cylindrical/conical shape
- Slightly tapered
- Usually orange
- Medium to large

CHILLI:
- Long, slender, cylindrical/conical
- Small to medium
- Usually green

CUCUMBER:
- Cylindrical/oblong
- Medium to large
- Deep green outer skin

POTATO:
- Irregular oval/round tuber
- Brown, yellowish or reddish skin depending on variety
- Eyes on the surface
- White/yellow interior when cut

TOMATO:
- Round/oval fruit
- Usually red when ripe
- Green when unripe
- Green leafy calyx

MAIZE:
- Long cylindrical cob
- Rows of tightly packed kernels
- Yellow/golden kernels are common
- May have green husk

RICE:
- Slender elongated grains
- Usually white/translucent when harvested
- If plant is visible, look for rice panicle and narrow leaves

WHEAT:
- Slender elongated grains
- Wheat ear/spike may be visible
- Mature plant can have green to yellowish-brown colour

Also estimate:
- freshness from 0 to 100
- visible defect percentage from 0 to 100
- dark spots percentage from 0 to 100
- discoloration percentage from 0 to 100
- overall quality: A, B, C, or Unknown

Do NOT claim a confirmed plant disease.
Only report visible visual symptoms.

Return ONLY valid JSON.
No markdown.
No explanation outside JSON.

Use exactly this structure:

{
  "crop_name": "onion",
  "confidence": 95,
  "freshness": 90,
  "defect": 5,
  "quality": "A",
  "spots": 2,
  "discoloration": 3,
  "action": [
    "Store in a cool and dry place",
    "Remove visibly damaged pieces"
  ],
  "note": "Visual analysis only. Disease diagnosis is not confirmed."
}

Rules:
- crop_name must be one of the allowed crops or "Unknown"
- confidence must be 0-100
- freshness must be 0-100
- defect must be 0-100
- spots must be 0-100
- discoloration must be 0-100
- quality must be A, B, C, or Unknown
- action must be a JSON list of short strings
"""


def _image_to_data_url(image_bytes: bytes) -> str:
    """
    Convert uploaded image bytes into a base64 data URL.
    """

    image = Image.open(io.BytesIO(image_bytes))

    # Convert unsupported formats safely
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    output = io.BytesIO()

    # JPEG is reliable for vision input
    if image.mode == "RGBA":
        image = image.convert("RGB")

    image.save(output, format="JPEG", quality=90)

    encoded = base64.b64encode(output.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


def _extract_json(text: str) -> dict:
    """
    Safely extract JSON from model output.
    """

    text = text.strip()

    # Direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try extracting JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        possible_json = text[start:end + 1]

        try:
            return json.loads(possible_json)
        except Exception:
            pass

    raise ValueError("Model did not return valid JSON.")


def _clean_result(result: dict) -> dict:
    """
    Validate and clean model output so that
    main.py and image_result.html continue working.
    """

    crop_name = str(result.get("crop_name", "Unknown")).lower().strip()

    if crop_name not in ALLOWED_CROPS:
        crop_name = "Unknown"

    def percentage(value, default=0):
        try:
            value = float(value)
            value = max(0, min(100, value))
            return round(value, 1)
        except Exception:
            return default

    confidence = percentage(result.get("confidence", 0))
    freshness = percentage(result.get("freshness", 0))
    defect = percentage(result.get("defect", 0))
    spots = percentage(result.get("spots", 0))
    discoloration = percentage(result.get("discoloration", 0))

    quality = str(
        result.get("quality", "Unknown")
    ).strip().upper()

    if quality not in ["A", "B", "C"]:
        quality = "Unknown"

    action = result.get("action", [])

    if not isinstance(action, list):
        action = [str(action)]

    action = [
        str(item).strip()
        for item in action
        if str(item).strip()
    ]

    if not action:
        action = [
            "Check the crop visually before storage or sale."
        ]

    note = str(
        result.get(
            "note",
            "Visual analysis only. Disease diagnosis is not confirmed."
        )
    ).strip()

    return {
        "crop_name": crop_name.capitalize()
        if crop_name != "Unknown"
        else "Unknown",

        "confidence": confidence,
        "freshness": freshness,
        "defect": defect,
        "quality": quality,
        "spots": spots,
        "discoloration": discoloration,
        "action": action,
        "note": note
    }


def analyze_crop_image(image_bytes: bytes):
    """
    Main function called by main.py.

    Input:
        image_bytes -> uploaded crop image

    Output:
        dictionary used by image_result.html
    """

    if not image_bytes:
        raise ValueError("Empty image received.")

    # Check that uploaded file is actually an image
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        raise ValueError("Uploaded file is not a valid image.")

    # Create OpenAI client
    client = OpenAI()

    # Convert image to data URL
    image_data_url = _image_to_data_url(image_bytes)

    # Send image + agriculture analysis prompt
    response = client.responses.create(
        model="gpt-5.6-luna",

        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": PROMPT
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_url
                    }
                ]
            }
        ]
    )

    # Get model text output
    output_text = response.output_text

    if not output_text:
        raise ValueError("OpenAI returned an empty response.")

    # Convert JSON text to Python dictionary
    result = _extract_json(output_text)

    # Validate result
    result = _clean_result(result)

    return result