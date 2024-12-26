from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import torch
import os
import uuid
import sys

current_dir = os.path.dirname(__file__)
weights = os.path.join(current_dir, "weights", "transformerocr.pth")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from title_detection.api import predict_from_image


config = Cfg.load_config_from_name('vgg_transformer')
config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
detector = Predictor(config)


def process_image_with_coordinates(image_path, coordinates_list):
    try:
        # Đọc ảnh từ file
        img = Image.open(image_path).convert("RGB")
        original_img = np.array(img)
        enhanced_img_pil = Image.fromarray(original_img)
    except Exception as e:
        print(f"Error loading or processing the image: {str(e)}")
        return [], None, []

    results = []  
    title_results = []  
    annotated_img = original_img.copy()
    overlay = annotated_img.copy()  
    annotated_img_pil = Image.fromarray(annotated_img)
    draw = ImageDraw.Draw(annotated_img_pil)
    font = ImageFont.load_default()

    try:
        with open(image_path, 'rb') as img_file:
            image_bytes = img_file.read()
        predictions_result = predict_from_image(image_bytes)
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return [], None, []

    if "error" in predictions_result:
        print(f"Error during prediction: {predictions_result['error']}")
        return [], None, []

    predictions = predictions_result["predictions"]

    for prediction in predictions:
        if prediction["confidence"] > 0.5:
            box = prediction["bbox"]
            min_x, min_y, max_x, max_y = map(int, box)
            cropped_img = enhanced_img_pil.crop((min_x, min_y, max_x, max_y))

            text, prob = detector.predict(cropped_img, return_prob=True)
            title_results.append({
                "coordinates": [min_x, min_y, max_x, max_y],
                "ocr_text": text,
                "confidence": prob
            })

            cv2.rectangle(overlay, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)

    if title_results:
        print("Title detected. Skipping other cells.")
        overlay_pil = Image.fromarray(overlay)
        final_img_pil = Image.blend(annotated_img_pil, overlay_pil, 0.4)

        output_dir = "image_color"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        random_filename = f"{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(output_dir, random_filename)
        final_img_pil.save(output_path)

        return [], output_path, title_results

    # Xử lý từng tọa độ trong danh sách
    for row_idx, coords in enumerate(coordinates_list):
        if len(coords) != 4:
            print(f"Invalid coordinates format: {coords}")
            continue

        min_x, min_y, max_x, max_y = coords


        # Xử lý các phần tử khác
        cropped_img = enhanced_img_pil.crop((min_x, min_y, max_x, max_y + 1))
        text, prob = detector.predict(cropped_img, return_prob=True)

        if text.lower() == "contraction" or prob < 0.5:
            text = ""  

        results.append({
            "coordinates": coords,
            "text": text,
            "confidence": prob
        })

        color = tuple(np.random.randint(0, 256, size=3).tolist())
        cv2.rectangle(overlay, (min_x, min_y), (max_x, max_y), color, cv2.FILLED)
        draw.text((min_x, min_y - 1), text, font=font, fill=(174, 26, 31))

    overlay_pil = Image.fromarray(overlay)
    final_img_pil = Image.blend(annotated_img_pil, overlay_pil, 0.4 )

    output_dir = "image_color"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    random_filename = f"{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(output_dir, random_filename)
    final_img_pil.save(output_path)

    return results, output_path, title_results

