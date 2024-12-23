from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import torch
import os
from character_recognition.imageprocessing import enhance_text_image
import uuid
import sys


# Thêm thư mục gốc vào Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from title_detection.api import predict_from_image


config = Cfg.load_config_from_name('vgg_transformer')
config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'

detector = Predictor(config)

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image
import numpy as np
import cv2
import uuid
import os

# Cấu hình cho mô hình VietOCR
config = Cfg.load_config_from_name('vgg_transformer')
config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
ocr_predictor = Predictor(config)

def process_image_with_coordinates(image_path, coordinates_list):
    try:
        # Đọc ảnh từ file
        img = Image.open(image_path).convert("RGB")
        original_img = np.array(img)
        enhanced_img_pil = Image.fromarray(original_img)
    except Exception as e:
        print(f"Error loading or processing the image: {str(e)}")
        return [], None

    results = []  # Danh sách kết quả nhận diện

    annotated_img = original_img.copy()
    overlay = annotated_img.copy()  # Lớp phủ để vẽ các vùng tô màu
    annotated_img_pil = Image.fromarray(annotated_img)
    draw = ImageDraw.Draw(annotated_img_pil)

    font_path = "./fonts/NotoSans-Regular.ttf"
    try:
        font = ImageFont.truetype(font_path, 24)
    except OSError:
        print("Font not found or cannot be loaded. Using default font.")
        font = ImageFont.load_default()

    # Lấy kết quả từ hàm predict_from_image
    with open(image_path, 'rb') as img_file:
        image_bytes = img_file.read()
    predictions_result = predict_from_image(image_bytes)  # Gọi hàm predict_from_image

    # Kiểm tra xem có trả về lỗi không
    if "error" in predictions_result:
        print(f"Error during prediction: {predictions_result['error']}")
        return [], None

    # Lấy danh sách các predictions từ kết quả trả về
    predictions = predictions_result["predictions"]

    # Duyệt qua từng tọa độ và thực hiện OCR
    for idx, coords in enumerate(coordinates_list):
        if len(coords) != 4:
            print(f"Invalid coordinates format: {coords}")
            continue

        min_x, min_y, max_x, max_y = coords

        cropped_img = enhanced_img_pil.crop((min_x, min_y, max_x, max_y))

        # Thực hiện OCR để nhận diện văn bản
        text, prob = detector.predict(cropped_img, return_prob=True)

        if text.lower() == "contraction":
            text = ""  # Bỏ qua từ "contraction"

        results.append({
            "coordinates": coords,
            "text": text,
            "confidence": prob
        })

        if prob < 0.5:
            color = (255, 0, 0)  # Màu đỏ cho độ tin cậy thấp
        else:
            color = tuple(np.random.randint(0, 256, size=3).tolist())

        alpha = 0.4  # Độ mờ (0.0 đến 1.0)
        cv2.rectangle(overlay, (min_x, min_y), (max_x, max_y), color, cv2.FILLED)

        draw.text((min_x, min_y-1), text, font=font, fill=(174, 26, 31))

    # Lấy thông tin title và thực hiện OCR
    title_results = []  
    for prediction in predictions:
        if prediction["confidence"] > 0.5 :
            box = prediction["bbox"]
            min_x, min_y, max_x, max_y = map(int, box)
            cropped_img = enhanced_img_pil.crop((min_x, min_y, max_x, max_y))

            # Sử dụng OCR VietOCR để nhận diện văn bản trong vùng này
            text, prob = ocr_predictor.predict(cropped_img, return_prob=True)
            
            title_results.append({
                "coordinates": [min_x, min_y, max_x, max_y],
                "ocr_text": text,
                "confidence": prob
            })

            # Vẽ ô quanh title
            cv2.rectangle(overlay, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)  # Ô đỏ
            

    overlay_pil = Image.fromarray(overlay)
    final_img_pil = Image.blend(annotated_img_pil, overlay_pil, alpha)

    output_dir = "image_color"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    random_filename = f"{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(output_dir, random_filename)
    final_img_pil.save(output_path)  

    return results, output_path,title_results

