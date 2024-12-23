from ultralytics import YOLO
from PIL import Image
import io

# Tải mô hình YOLO
model = YOLO("title_detection/models/best.pt")

# Hàm xử lý ảnh và trả về kết quả
def predict_from_image(image_bytes):
    try:
        # Chuyển đổi bytes thành ảnh
        image = Image.open(io.BytesIO(image_bytes))

        # Chạy mô hình YOLO trên ảnh
        results = model.predict(image, save=False)

        # Trích xuất thông tin từ kết quả
        predictions = []
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()  # Tọa độ bbox (xmin, ymin, xmax, ymax)
            classes = result.boxes.cls.cpu().numpy()  # Nhãn của lớp
            confidences = result.boxes.conf.cpu().numpy()  # Độ tin cậy
            for box, cls, conf in zip(boxes, classes, confidences):
                predictions.append({
                    "label": model.names[int(cls)],  # Lấy tên nhãn từ model.names
                    "confidence": float(conf),      # Độ tin cậy của dự đoán
                    "bbox": [float(x) for x in box] # Tọa độ bbox
                })

        return {"predictions": predictions}
    except Exception as e:
        return {"error": str(e)}


