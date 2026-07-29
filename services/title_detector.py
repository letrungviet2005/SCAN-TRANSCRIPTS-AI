import io

from PIL import Image
from ultralytics import YOLO


model = YOLO("title_detection/models/best.pt")


def predict_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        results = model.predict(image, save=False)
        predictions = []
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, cls, conf in zip(boxes, classes, confidences):
                predictions.append({
                    "label": model.names[int(cls)],
                    "confidence": float(conf),
                    "bbox": [float(x) for x in box],
                })
        return {"predictions": predictions}
    except Exception as exc:
        return {"error": str(exc)}
