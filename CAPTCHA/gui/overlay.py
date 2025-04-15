# gui/overlay.py
import os
from PIL import Image

def load_image_as_image(image_path, size=None):
    """
    주어진 이미지 파일(PNG 또는 JPEG)을 PIL.Image 객체로 로드합니다.
    size가 지정되면 해당 크기로 리사이즈합니다.
    """
    img = Image.open(image_path).convert("RGBA")
    if size:
        img = img.resize(size)
    return img

def overlay_checkmark(base_img, check_icon_path, position="center", icon_size=(1000, 1000)):
    """
    base_img 위에 체크 아이콘(주어진 PNG/JPEG 파일)을 오버레이하여 
    새로운 PIL.Image 객체를 반환합니다.

    Parameters:
      - base_img: 후보 이미지의 원본 PIL.Image
      - check_icon_path: 체크 아이콘(투명 PNG 권장) 파일 경로
      - position: 체크 아이콘을 붙일 위치 ("top-left", "top-right", "bottom-left", "bottom-right", "center")
      - icon_size: 체크 아이콘의 크기 (기본값: (100, 100) → 더 크게 보이도록 설정)
    """
    check_img = load_image_as_image(check_icon_path, size=icon_size)
    base_rgba = base_img.convert("RGBA")
    
    bw, bh = base_rgba.size
    iw, ih = check_img.size
    
    if position == "top-left":
        x, y = 0, 0
    elif position == "top-right":
        x, y = bw - iw, 0
    elif position == "bottom-left":
        x, y = 0, bh - ih
    elif position == "bottom-right":
        x, y = bw - iw, bh - ih
    elif position == "center":
        x = (bw - iw) // 2
        y = (bh - ih) // 2
    else:
        x, y = 0, 0
        
    base_rgba.paste(check_img, (x, y), check_img)
    return base_rgba
