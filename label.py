import os
import json
import cv2
import numpy as np
from PIL import Image

# ====== 설정: contour.json 경로 ======
json_path = "/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/correct_answer/Contour/Contour.json"
output_dir = json_path.replace(".json", "_json")
os.makedirs(output_dir, exist_ok=True)

# 1) JSON 로드
with open(json_path, 'r') as f:
    data = json.load(f)

# 2) 원본 이미지 불러와 해상도 추출
img_file = os.path.join(os.path.dirname(json_path), data.get('imagePath', ''))
img = cv2.imread(img_file)
if img is None:
    raise FileNotFoundError(f"Image file not found: {img_file}")
h, w = img.shape[:2]

# 3) 빈 마스크 생성 (0=background)
mask = np.zeros((h, w), dtype=np.uint8)

# 4) 폴리곤 좌표를 int로 변환하여 채우기
for shape in data.get('shapes', []):
    if shape.get('label') == 'cloud' and shape.get('points'):
        pts = np.array(
            [[int(round(x)), int(round(y))] for x, y in shape['points']],
            dtype=np.int32
        ).reshape(-1, 1, 2)
        # 이진 마스크: cloud 영역을 255로 채움
        cv2.fillPoly(mask, [pts], 255)

# 5) label.png 저장
label_path = os.path.join(output_dir, 'label.png')
Image.fromarray(mask).save(label_path)
print(f"✅ label.png 생성 완료: {label_path}")

