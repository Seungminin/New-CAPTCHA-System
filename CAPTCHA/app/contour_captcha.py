# app/contour_captcha.py
import random
from PIL import Image, ImageDraw

def generate_contour_captcha():
    """
    Contour 기반 CAPTCHA 문제 생성  
    - 간단하게 O 동그라미(또는 기타 도형)를 그려 문제 이미지를 구성하고,  
      후보 이미지는 변형(회전 등)하여 만듭니다.
    - 최종 캡챠 이미지를 PIL.Image 객체로 반환.
    """
    # 문제 이미지 생성 (흰 배경에 검은 원 그리기)
    width, height = 300, 300
    question_img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(question_img)
    # 원의 위치와 크기를 랜덤으로 결정 (여기서 다양한 인지적 차이를 반영하는 로직 가능)
    x0 = random.randint(10, 50)
    y0 = random.randint(10, 50)
    x1 = random.randint(width - 150, width - 10)
    y1 = random.randint(height - 150, height - 10)
    draw.ellipse([x0, y0, x1, y1], outline="black", width=5)
    
    # 후보 이미지 생성 (정답 후보: 변형 없이, 오답 후보: 회전 적용)
    num_candidates = 9
    candidates = []
    for i in range(num_candidates):
        candidate = question_img.copy()
        if i >= 4:  # 4개 이상은 오답 후보 (회전 적용)
            angle = random.randint(-15, 15)
            candidate = candidate.rotate(angle)
        candidates.append(candidate.resize((150, 150)))
    
    # 후보 이미지를 그리드 형태로 배치 (3열)
    import math
    columns = 3
    rows = (num_candidates + columns - 1) // columns
    grid_width = columns * 150
    grid_height = rows * 150
    
    # 문제 이미지를 그리드 폭에 맞춰 리사이즈 (비율 유지)
    question_img = question_img.resize((grid_width, int(height * (grid_width / width))))
    q_height = question_img.height
    
    final_width = grid_width
    final_height = q_height + grid_height
    final_img = Image.new("RGB", (final_width, final_height), (255, 255, 255))
    final_img.paste(question_img, (0, 0))
    
    for idx, candidate in enumerate(candidates):
        row = idx // columns
        col = idx % columns
        x = col * 150
        y = q_height + row * 150
        final_img.paste(candidate, (x, y))
    
    return {
        "type": "contour",
        "info": "Contour 기반 CAPTCHA 생성",
        "image": final_img
    }
