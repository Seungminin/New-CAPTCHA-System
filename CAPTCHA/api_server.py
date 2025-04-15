# api_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS   # CORS 임포트
from app.dcgan_captcha import generate_dcgan_captcha, check_dcgan_answer
import uuid
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)  # Flask 앱에 CORS 적용


# CAPTCHA 정보를 저장하는 글로벌 딕셔너리 (테스트용; 운영 환경에서는 Redis 등 사용 권장)
CAPTCHA_STORE = {}

def pil_image_to_base64(pil_image):
    """
    PIL.Image 객체를 PNG 형식 base64 문자열로 변환하는 헬퍼 함수.
    """
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    encoded_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded_str

@app.route('/')
def index():
    return "캡차 API 서버입니다. /captcha/create 또는 /captcha/verify 엔드포인트를 사용하세요."

@app.route('/captcha/create', methods=['GET'])
def captcha_create():
    """
    GET 요청으로 CAPTCHA 문제를 생성하여 클라이언트에 전달합니다.
    - dcgan_captcha.generate_dcgan_captcha()를 사용해 문제 및 후보 이미지를 생성.
    - question_image와 후보(candidate) 이미지들은 base64 문자열로 변환됨.
    - 내부 검증에 필요한 정보는 CAPTCHA_STORE에 captcha_id 키로 저장됨.
    """
    try:
        # DCGAN CAPTCHA 데이터를 생성 (문제 이미지, 후보 9장, 정답 정보 등 포함)
        captcha_data = generate_dcgan_captcha()
    except Exception as e:
        return jsonify({"result": False, "message": str(e)}), 500

    captcha_id = str(uuid.uuid4())
    # 생성된 captcha_data를 저장 (검증 시 사용)
    CAPTCHA_STORE[captcha_id] = captcha_data

    # 문제 이미지를 base64 문자열로 변환
    question_image_b64 = pil_image_to_base64(captcha_data["question_image"])

    # 후보 이미지들을 base64 문자열로 변환하여, id와 함께 클라이언트에 전달 (category 등 내부 정보는 제외)
    candidates_output = []
    for candidate in captcha_data["candidates"]:
        candidate_b64 = pil_image_to_base64(candidate["image"])
        candidates_output.append({
            "id": candidate["id"],
            "image": candidate_b64
        })

    response = {
        "captcha_id": captcha_id,
        "type": captcha_data["type"],
        "question_image": question_image_b64,
        "candidates": candidates_output
    }

    return jsonify(response), 200

@app.route('/captcha/verify', methods=['POST'])
def captcha_verify():
    """
    POST 요청으로 전달된 사용자 선택(candidate id 리스트)을 검증합니다.
    요청 JSON 예시:
    {
        "captcha_id": "생성된-uuid",
        "selected_ids": ["img1", "img4", ...]
    }
    dcgan_captcha.check_dcgan_answer() 함수를 통해 정답 여부를 판단하며,
    검증 후 해당 captcha 정보는 CAPTCHA_STORE에서 삭제합니다.
    """
    data = request.get_json()
    if not data:
        return jsonify({"result": False, "message": "JSON 데이터를 전달해주세요."}), 400

    captcha_id = data.get("captcha_id")
    selected_ids = data.get("selected_ids")  # 사용자가 선택한 후보 id 목록

    if not captcha_id or not selected_ids:
        return jsonify({"result": False, "message": "captcha_id와 selected_ids 필드는 필수입니다."}), 400

    captcha_data = CAPTCHA_STORE.get(captcha_id)
    if not captcha_data:
        return jsonify({"result": False, "message": "유효하지 않은 또는 만료된 captcha_id입니다."}), 400

    # dcgan_captcha에 정의된 검증 함수 호출
    verified = check_dcgan_answer(selected_ids, captcha_data)

    # 한 번 사용한 CAPTCHA는 삭제 (보안상)
    del CAPTCHA_STORE[captcha_id]

    if verified:
        return jsonify({"result": True, "message": "CAPTCHA 인증에 성공했습니다."}), 200
    else:
        return jsonify({"result": False, "message": "CAPTCHA 인증에 실패했습니다."}), 200

if __name__ == '__main__':
    app.run(debug=True)
