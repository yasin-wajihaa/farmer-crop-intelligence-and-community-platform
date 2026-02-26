from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import json
import os

app = FastAPI()

MODEL = None
CLASS_NAMES = None

# -------- LOAD MODEL SAFELY --------
@app.on_event("startup")
def load_model():
    global MODEL, CLASS_NAMES

    model_path = "model/model.keras"
    class_file = "class_indices.json"

    print("Loading AI model... please wait")

    MODEL = tf.keras.models.load_model(model_path)

    with open(class_file, "r") as f:
        CLASS_NAMES = json.load(f)

    # convert dict index->label
    CLASS_NAMES = {int(v): k for k, v in CLASS_NAMES.items()}

    print("Model loaded successfully!")

# -------- HOME PAGE --------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>🌿 Crop Doctor</title>
    </head>
    <body style="font-family: Arial; text-align:center; margin-top:50px;">
        <h1>🌿 AI Crop Doctor</h1>
        <p>Upload a plant leaf image</p>

        <form action="/predict" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <br><br>
            <input type="submit" value="Diagnose">
        </form>
    </body>
    </html>
    """

# -------- PREDICTION --------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image = image.resize((128, 128))

    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = MODEL.predict(img_array)
    class_index = int(np.argmax(predictions))
    confidence = float(np.max(predictions))

    disease = CLASS_NAMES[class_index]

    return JSONResponse({
        "disease": disease,
        "confidence": round(confidence * 100, 2)
    })
