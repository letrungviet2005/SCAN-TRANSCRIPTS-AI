import cv2
import numpy as np

def enhance_text_image(image):
    img = np.array(image)

    if len(img.shape) == 2:
        gray = img
    elif img.shape[2] == 1:
        gray = img[:, :, 0]
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced_contrast = clahe.apply(gray)

    denoised = cv2.GaussianBlur(enhanced_contrast, (3, 3), 0)

    sharp = cv2.addWeighted(denoised, 1.7, cv2.GaussianBlur(denoised, (0, 0), 3), -0.3, 0)

    gamma = 1.3
    gamma_correction = np.array(255 * (sharp / 255) ** gamma, dtype="uint8")

    gamma_correction = cv2.resize(gamma_correction, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    return gamma_correction
