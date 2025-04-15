# # app/captcha_selector.py
# import random
# from app import dcgan_captcha, contour_captcha

# def generate_random_captcha():
#     """
#     여러 CAPTCHA 문제 생성 방법 중 하나를 랜덤 선택하여 실행  
#     반환값은 각 모듈에서 반환하는 dict (최종 이미지 포함)
#     """
#     captcha_methods = [
#         dcgan_captcha.generate_dcgan_captcha,
#         contour_captcha.generate_contour_captcha,
#         # 향후 추가 모듈 등록 가능
#     ]
#     chosen_method = random.choice(captcha_methods)
#     result = chosen_method()  # 결과 dict에 "image" 키로 최종 PIL.Image 객체 포함
#     return result

from app.dcgan_captcha import generate_dcgan_captcha

def generate_random_captcha():
    # 현재는 DCGAN 방식만 있으므로 그냥 호출
    return generate_dcgan_captcha()
