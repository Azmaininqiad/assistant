from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import base64
import cv2
import os
import google.generativeai as genai

# Configure Gemini model
API_KEY = "AIzaSyANaYZ8rmgmGJrTIQYUTECoVvQYXc0Gbyo"  # Replace with your Gemini API key
os.environ["API_KEY"] = API_KEY
genai.configure(api_key=os.environ["API_KEY"])
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)

def query_gemini(prompt):
    """
    Query the Gemini model and return its response.
    """
    try:
        response = gemini_model.generate_content([prompt])
        return response[0].text.strip() if response else None
    except Exception as e:
        print(f"Error querying Gemini model: {e}")
        return None

@app.route("/chat", methods=["POST"])
def chat():
    query = request.json["query"]
    gemini_response = query_gemini(query)
    if gemini_response:
        return jsonify({"answer": gemini_response})
    else:
        return jsonify({"error": "Failed to get a response from the Gemini model."}), 500

@app.route("/screenshot", methods=["POST"])
def screenshot():
    data = request.json["screenshot"]
    screenshot_data = base64.b64decode(data.split(",")[1])

    with open("screenshot.png", "wb") as f:
        f.write(screenshot_data)

    # Process the screenshot
    image = cv2.imread("screenshot.png")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    custom_config = r"--oem 3 --psm 6"
    ocr_data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)

    bounding_boxes = []
    for i in range(len(ocr_data["text"])):
        if int(ocr_data["conf"][i]) > 50:  # Confidence threshold
            (x, y, w, h) = (ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i])
            bounding_boxes.append({"text": ocr_data["text"][i], "x": x, "y": y, "w": w, "h": h})

    return jsonify({"bounding_boxes": bounding_boxes})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    screenshot_path = "screenshot.png"
    bounding_boxes = data.get("bounding_boxes", [])
    instruction = data.get("instruction", "")

    # Prepare the prompt for Gemini
    prompt = f"""
    Screenshot OCR Data: {bounding_boxes}
    Instruction: {instruction}
    Question: Which button should the user click to perform this action? Provide x, y, w, h for the button and a brief explanation.
    """
    gemini_response = query_gemini(prompt)
    if gemini_response:
        return jsonify({"gemini_output": gemini_response})
    else:
        return jsonify({"error": "Failed to get a response from the Gemini model."}), 500

if __name__ == "__main__":
    app.run(debug=True)
