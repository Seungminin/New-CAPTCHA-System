import tkinter as tk
from PIL import ImageTk, Image
import os

from app.dcgan_captcha import generate_dcgan_captcha, check_dcgan_answer
from gui.overlay import overlay_checkmark

captcha_data = {}
user_selected = set()

# CHECK_ICON_PATH: 체크 아이콘 PNG 파일의 절대경로 (여기서는 gui/icon/check.png)
CHECK_ICON_PATH = os.path.join(os.path.dirname(__file__), "icon", "check.png")

def toggle_select(button, candidate_id, candidate):
    if candidate_id in user_selected:
        user_selected.remove(candidate_id)
        button.config(image=candidate["original_tk_img"])
    else:
        user_selected.add(candidate_id)
        button.config(image=candidate["checked_tk_img"])

def start_gui():
    global captcha_data, user_selected
    user_selected = set()
    captcha_data = generate_dcgan_captcha()

    root = tk.Tk()
    root.title("CAPTCHA")

    # 문제 이미지 로드
    question_img = captcha_data["question_image"]
    
    # side_by_side 여부: 문제 이미지의 폭 또는 높이가 400 이상이면 옆으로 배치
    side_by_side = (question_img.width > 400 or question_img.height > 400)

    # 문제 이미지 리사이즈 (폭 450px 기준)
    w_target = 450
    h_target = int(question_img.height * (w_target / question_img.width))
    tk_question = ImageTk.PhotoImage(question_img.resize((w_target, h_target)))

    # 메인 프레임 생성
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    if side_by_side:
        # 수평 레이아웃: 왼쪽(문제, 정보, 컨트롤 패널), 오른쪽(후보 이미지 그리드)
        left_frame = tk.Frame(main_frame)
        right_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 왼쪽 프레임: 문제 이미지, 정보, 그리고 컨트롤 패널(결과 메시지와 버튼)
        question_label = tk.Label(left_frame, image=tk_question)
        question_label.image = tk_question
        question_label.pack(pady=5)

        info_str = (
            f"문제 유형: {captcha_data['type']}\n"
            f"정답 카테고리: {captcha_data['chosen_category']}\n"
            f"정답 이미지 개수: {captcha_data['num_correct']}"
        )
        info_label = tk.Label(left_frame, text=info_str, font=("Arial", 12), fg="blue")
        info_label.pack(pady=5)

        # 컨트롤 패널 (정보 바로 밑)
        control_frame = tk.Frame(left_frame)
        control_frame.pack(pady=5)
        result_label = tk.Label(control_frame, text="", font=("Arial", 12))
        result_label.pack(pady=5, fill="x")
        submit_btn = tk.Button(control_frame, text="제출", command=lambda: submit(result_label))
        submit_btn.pack(side="left", padx=5)
        new_btn = tk.Button(control_frame, text="새 CAPTCHA 생성", command=lambda: new_captcha(root))
        new_btn.pack(side="left", padx=5)

        # 오른쪽 프레임: 후보 이미지 그리드
        candidates_frame = tk.Frame(right_frame)
        candidates_frame.pack(padx=10, pady=10)
    else:
        # 수직 레이아웃: 상단(문제 이미지, 정보, 컨트롤 패널), 하단(후보 이미지 그리드)
        top_frame = tk.Frame(main_frame)
        bottom_frame = tk.Frame(main_frame)
        top_frame.pack(side="top", fill="both", padx=10, pady=10)
        bottom_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

        question_label = tk.Label(top_frame, image=tk_question)
        question_label.image = tk_question
        question_label.pack(pady=5)

        info_str = (
            f"문제 유형: {captcha_data['type']}\n"
            f"정답 카테고리: {captcha_data['chosen_category']}\n"
            f"정답 이미지 개수: {captcha_data['num_correct']}"
        )
        info_label = tk.Label(top_frame, text=info_str, font=("Arial", 12), fg="blue")
        info_label.pack(pady=5)

        # 컨트롤 패널 (정보 바로 밑)
        control_frame = tk.Frame(top_frame)
        control_frame.pack(pady=5)
        result_label = tk.Label(control_frame, text="", font=("Arial", 12))
        result_label.pack(pady=5, fill="x")
        submit_btn = tk.Button(control_frame, text="제출", command=lambda: submit(result_label))
        submit_btn.pack(side="left", padx=5)
        new_btn = tk.Button(control_frame, text="새 CAPTCHA 생성", command=lambda: new_captcha(root))
        new_btn.pack(side="left", padx=5)

        # 후보 이미지 그리드는 아래쪽 프레임에
        candidates_frame = tk.Frame(bottom_frame)
        candidates_frame.pack(padx=10, pady=10)

    # 후보 이미지 버튼 생성 (후보는 9장)
    candidate_list = captcha_data["candidates"]
    columns = 3
    for idx, cand in enumerate(candidate_list):
        base_img = cand["image"]
        # 오버레이: 체크 아이콘이 후보 이미지의 정중앙에 크기 60×60으로 표시됨
        overlaid_img = overlay_checkmark(base_img.copy(), CHECK_ICON_PATH, position="center", icon_size=(60, 60))
        cand["original_tk_img"] = ImageTk.PhotoImage(base_img)
        cand["checked_tk_img"] = ImageTk.PhotoImage(overlaid_img)
        
        btn = tk.Button(candidates_frame, image=cand["original_tk_img"], relief="raised", borderwidth=2)
        # 람다에서 매개변수 기본값을 이용해 늦은 바인딩 문제 해결
        btn.config(command=lambda b=btn, cid=cand["id"], c=cand: toggle_select(b, cid, c))
        row = idx // columns
        col = idx % columns
        btn.grid(row=row, column=col, padx=5, pady=5)

    root.mainloop()

def submit(result_label):
    if check_dcgan_answer(user_selected, captcha_data):
        result_label.config(text="정답입니다! 인증 완료!", fg="green")
    else:
        result_label.config(text="오답입니다. 다시 시도하세요.", fg="red")

def new_captcha(root):
    root.destroy()
    start_gui()
