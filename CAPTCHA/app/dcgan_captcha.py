# app/dcgan_captcha.py
import os
import random
from PIL import Image
from config import QUESTIONS_PATH, ANSWERS_PATH

def generate_dcgan_captcha():
    """
    DCGAN 기반 CAPTCHA 문제 생성 함수
      - 문제(Question) 1장, 후보(Candidate) 9장 개별 PIL.Image 객체를 반환
      - 각 후보에는 "id"(파일명), "image"(PIL.Image), "category"(카테고리) 정보 포함
    """
    # 1) 문제 카테고리 랜덤 선택
    categories = [d for d in os.listdir(QUESTIONS_PATH)
                  if os.path.isdir(os.path.join(QUESTIONS_PATH, d))]
    if not categories:
        raise FileNotFoundError("Questions 폴더 내에 카테고리가 없습니다.")
    chosen_category = random.choice(categories)
    question_dir = os.path.join(QUESTIONS_PATH, chosen_category)

    # 2) 문제 이미지 선택
    question_files = [os.path.join(question_dir, f)
                      for f in os.listdir(question_dir)
                      if f.lower().endswith('.png')]
    if not question_files:
        raise FileNotFoundError(f"'{chosen_category}' 카테고리에 문제 이미지가 없습니다.")
    question_path = random.choice(question_files)
    question_image = Image.open(question_path)

    # 3) 정답 후보(같은 카테고리) 2~5장
    correct_dir = os.path.join(ANSWERS_PATH, chosen_category)
    correct_files = [os.path.join(correct_dir, f)
                     for f in os.listdir(correct_dir)
                     if f.lower().endswith('.png')]
    if not correct_files:
        raise FileNotFoundError(f"'{chosen_category}' 카테고리에 정답 이미지가 없습니다.")
    num_correct = random.randint(2, min(5, len(correct_files)))
    selected_correct = random.sample(correct_files, num_correct)

    # 4) 오답 후보(다른 카테고리) → 나머지 수(총 9장 후보 중 정답 수 제외)
    total_candidates = 9
    num_fake = total_candidates - num_correct
    other_categories = [d for d in os.listdir(ANSWERS_PATH)
                        if os.path.isdir(os.path.join(ANSWERS_PATH, d)) and d != chosen_category]
    fake_pool = []
    for cat in other_categories:
        fake_dir = os.path.join(ANSWERS_PATH, cat)
        fake_files = [os.path.join(fake_dir, f) for f in os.listdir(fake_dir) if f.lower().endswith('.png')]
        fake_pool.extend([(path, cat) for path in fake_files])
    if len(fake_pool) < num_fake:
        num_fake = len(fake_pool)
    selected_fake = random.sample(fake_pool, num_fake) if fake_pool else []

    # 5) 후보 이미지(정답 + 오답) → PIL Image로 로드 (150×150)
    candidate_size = (150, 150)
    candidates = []
    # 정답 후보
    for path in selected_correct:
        img = Image.open(path).resize(candidate_size)
        candidates.append({
            "id": os.path.basename(path),  # 파일명
            "image": img,
            "category": chosen_category
        })
    # 오답 후보
    for (path, cat) in selected_fake:
        img = Image.open(path).resize(candidate_size)
        candidates.append({
            "id": os.path.basename(path),
            "image": img,
            "category": cat
        })
    random.shuffle(candidates)

    return {
        "type": "dcgan",
        "chosen_category": chosen_category,
        "question_image": question_image,
        "candidates": candidates,
        "num_correct": num_correct
    }

def check_dcgan_answer(user_selected_ids, captcha_data):
    """
    사용자가 선택한 후보 id(user_selected_ids)와, captcha_data 내 정보(문제의 chosen_category 등)를 비교.
    - 모든 선택된 후보의 category가 chosen_category와 같아야 정답 처리.
    - 정답 후보 수(num_correct)와 선택된 개수가 일치하는지도 확인할 수 있음.
    """
    chosen_category = captcha_data["chosen_category"]
    candidates = captcha_data["candidates"]  # 9장 후보 정보
    num_correct = captcha_data["num_correct"]

    # 1) 선택된 것이 없는 경우
    if not user_selected_ids:
        return False

    # 2) 선택된 후보 중 카테고리가 문제와 다른 것이 하나라도 있으면 오답
    selected_candidates = [c for c in candidates if c["id"] in user_selected_ids]
    for sc in selected_candidates:
        if sc["category"] != chosen_category:
            return False

    # 3) 만약 “정확히 num_correct개”를 골라야 한다고 하면:
    if len(selected_candidates) != num_correct:
        return False

    return True
