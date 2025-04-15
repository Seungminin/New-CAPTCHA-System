import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 질문 및 정답 이미지가 있는 폴더
QUESTIONS_PATH = os.path.join(BASE_DIR, "Image", "DCGANs", "questions")
ANSWERS_PATH   = os.path.join(BASE_DIR, "Image", "DCGANs", "answers")
