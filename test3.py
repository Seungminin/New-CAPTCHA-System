from flask import Flask, jsonify, request, send_file, make_response
import numpy as np
import json
import os
from PIL import Image
import cv2
from flask_cors import CORS
import random
import base64
import io
from flask import make_response

app = Flask(__name__)
CORS(app)

GENERATED_IMAGES_PATH = os.path.abspath(r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/generated_images')
FAKE_ANSWER_PATH = os.path.abspath(r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/fake_answer')
CORRECT_ANSWER_PATH = os.path.abspath(r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/correct_answer')
CAPTCHA_PATH = os.path.abspath(r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static/generated_captcha.png')

selected_method_global = None
current_contour_correct_image_path = None
cloud_mask = None
contour_dims = None

def analyze_drawing_pattern(drawing_data):
    drawing_data = sorted(drawing_data, key=lambda d: d['time'])
    speeds = []
    for i in range(1, len(drawing_data)):
        dx = drawing_data[i]['x'] - drawing_data[i-1]['x']
        dy = drawing_data[i]['y'] - drawing_data[i-1]['y']
        dt = (drawing_data[i]['time'] - drawing_data[i-1]['time']) / 1000.0
        if dt > 0:
            speed = ((dx**2 + dy**2)**0.5) / dt
            speeds.append(speed)

    std_speed = np.std(speeds)
    avg_speed = np.mean(speeds)
    return std_speed, avg_speed

def is_bot(std_speed, avg_speed):
    if std_speed < 3.0 and 30 < avg_speed < 70:
        return True
    else:
        return False
    
def calculate_iou(user_mask, cloud_mask):
    intersection = cv2.bitwise_and(user_mask, cloud_mask)
    intersection_area = np.count_nonzero(intersection)
    user_area = np.count_nonzero(user_mask)
    cloud_area = np.count_nonzero(cloud_mask)
    union_area = user_area + cloud_area - intersection_area
    iou_ratio = intersection_area / union_area if union_area > 0 else 0
    return iou_ratio

def generate_captcha_and_answer():
    global selected_method_global, current_contour_correct_image_path, cloud_mask, contour_dims
    try:
        selected_method = random.choice(['DCGANs', 'Diffusion', 'Contour'])
        selected_method_global = selected_method

        static_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static'
        for file in os.listdir(static_dir):
            if file.startswith("answer_captcha"):
                os.remove(os.path.join(static_dir, file))

        if selected_method == 'Contour':
            generated_images_path = os.path.join(GENERATED_IMAGES_PATH, selected_method)
            image_files = [os.path.join(root, filename)
                           for root, _, files in os.walk(generated_images_path)
                           for filename in files if filename.endswith('.png')]
            contour_correct_dir = os.path.join(CORRECT_ANSWER_PATH, 'Contour')
            correct_images = [os.path.join(contour_correct_dir, filename)
                              for filename in os.listdir(contour_correct_dir) if filename.endswith('.png')]
            
            if not correct_images or not image_files:
                raise FileNotFoundError("No Contour images found.")
            
            chosen_top = random.choice(image_files)
            captcha_img = Image.open(chosen_top)
            captcha_img.save(CAPTCHA_PATH, format='PNG')

            selected_correct = random.choice(correct_images)
            current_contour_correct_image_path = selected_correct

            Image.open(selected_correct).save(os.path.join(static_dir, 'answer_captcha_1_correct.png'), format='PNG')

            label_img_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/correct_answer/Contour/Contour_json'
            label_path = os.path.join(label_img_dir, 'label.png')
            label_img = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)
            if label_img is None:
                raise ValueError(f"Failed to load image: {label_path}")
            
            label_img = cv2.resize(label_img, (300, 270), interpolation=cv2.INTER_NEAREST)

            h0, w0 = label_img.shape
            contour_dims = (w0, h0)

            _, cloud_mask = cv2.threshold(label_img, 127, 255, cv2.THRESH_BINARY)
            
            print(f"[DEBUG] cloud_mask shape: {cloud_mask.shape}")
            cv2.imwrite(os.path.join(static_dir, 'cloud_mask.png'), cloud_mask)

        else:
            generated_images_path = os.path.join(GENERATED_IMAGES_PATH, selected_method)
            image_files = [os.path.join(root, filename)
                           for root, _, files in os.walk(generated_images_path)
                           for filename in files if filename.endswith('.png')]
            if not image_files:
                raise FileNotFoundError("No CAPTCHA images found.")

            chosen_top = random.choice(image_files)
            captcha_img = Image.open(chosen_top)
            captcha_img.save(CAPTCHA_PATH, format='PNG')

            chosen_dir_name = os.path.basename(os.path.dirname(chosen_top))
            correct_dir_path = os.path.join(CORRECT_ANSWER_PATH, selected_method, chosen_dir_name)
            fake_dir_path = os.path.join(FAKE_ANSWER_PATH, selected_method, chosen_dir_name)

            if not os.path.exists(correct_dir_path) or not os.path.exists(fake_dir_path):
                raise FileNotFoundError(f"No matching directory.")

            correct_images = [os.path.join(correct_dir_path, filename)
                              for filename in os.listdir(correct_dir_path) if filename.endswith('.png')]
            correct_count = random.randint(3, min(5, len(correct_images)))
            selected_correct = random.sample(correct_images, correct_count)

            fake_images = [os.path.join(fake_dir_path, filename)
                           for filename in os.listdir(fake_dir_path) if filename.endswith('.png')]
            fake_count = 9 - correct_count
            selected_fake = random.sample(fake_images, fake_count)

            combined_images = selected_fake + selected_correct
            random.shuffle(combined_images)

            for idx, img_path in enumerate(combined_images):
                filename = f"answer_captcha_{idx + 1}_"
                filename += "correct.png" if img_path in selected_correct else "fake.png"
                Image.open(img_path).save(os.path.join(static_dir, filename), format='PNG')

    except Exception as e:
        print(f"Error in generate_captcha_and_answer: {e}")
        raise

@app.route('/generate_captcha_metadata', methods=['GET'])
def generate_captcha_metadata():
    try:
        if selected_method_global is None:
            generate_captcha_and_answer()
        return jsonify({'method': selected_method_global})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generated_captcha.png', methods=['GET'])
def get_captcha_question():
    return send_file(CAPTCHA_PATH, mimetype='image/png')

@app.route('/get_captcha_files', methods=['GET'])
def get_captcha_files():
    try:
        files = []
        static_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static'
        for file in os.listdir(static_dir):
            if file.startswith('answer_captcha') and file.endswith('.png'):
                files.append(file)
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer_captcha_<int:index>_<status>.png', methods=['GET'])
def get_captcha_answer(index, status):
    try:
        if 1 <= index <= 9 and status in ["correct", "fake"]:
            static_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static'
            file_name = f'answer_captcha_{index}_{status}.png'
            file_path = os.path.join(static_dir, file_name)
            if os.path.exists(file_path):
                return send_file(file_path, mimetype='image/png')
            return jsonify({'error': f'File not found: {file_name}'}), 404
        return jsonify({'error': 'Invalid index or status'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/answer_captcha_1_correct.png', methods=['GET'])
def get_contour_correct_image():
    try:
        static_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static'
        file_path = os.path.join(static_dir, 'answer_captcha_1_correct.png')
        if os.path.exists(file_path):
            response = make_response(send_file(file_path, mimetype='image/png'))
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = '*'
            return response
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit_path():
    global cloud_mask, contour_dims
    try:
        data = request.json
        name = data.get('name', '')
        dob = data.get('dob', '')
        username = data.get('username', '')
        password = data.get('password', '')
        email = data.get('email', '')
        selected_images = data.get('selected_images', [])
        drawing_data_url = data.get('drawing_data_url', None)

        if selected_method_global == 'Contour':
            drawing_data_url = data.get('drawing_data_url')
            if not drawing_data_url:
                return jsonify({'message': '드로잉 이미지가 없습니다.', 'success': False}), 400

            # Decode drawing data
            header, encoded = drawing_data_url.split(',', 1)
            binary_data = base64.b64decode(encoded)
            image = Image.open(io.BytesIO(binary_data)).convert("RGBA")
            user_mask = np.array(image)

            # Resize and threshold user_mask
            w0, h0 = contour_dims
            user_mask = user_mask[:, :, 3]
            user_mask = cv2.resize(user_mask, (w0, h0), interpolation=cv2.INTER_NEAREST)
            _, user_mask = cv2.threshold(user_mask, 1, 255, cv2.THRESH_BINARY)

            static_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static'
            cv2.imwrite(os.path.join(static_dir, 'user_mask.png'), user_mask)

            #kernel = np.ones((3, 3), np.uint8)
            #user_mask = cv2.morphologyEx(user_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

            if cloud_mask is None:
                return jsonify({'message': 'Cloud mask not initialized.', 'success': False}), 500
            
            intersection = cv2.bitwise_and(user_mask, cloud_mask)
            inter_area = np.count_nonzero(intersection)
            cloud_area = np.count_nonzero(cloud_mask)

            coverage = inter_area / cloud_area if cloud_area > 0 else 0
            print(f"[DEBUG] Coverage: {coverage:.4f}", flush=True)
            is_correct = (coverage >= 0.5)

        else:
            if not selected_images:
                return jsonify({'message': 'No images selected.', 'success': False}), 400

            static_dir = r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/static'
            correct_image_names = [f for f in os.listdir(static_dir) if f.endswith('correct.png')]
            is_correct = (all(image_name in correct_image_names for image_name in selected_images) and
                         len(selected_images) == len(correct_image_names))

        if is_correct:
            user_data = {
                'name': name,
                'dob': dob,
                'username': username,
                'original_password': password,
                'email': email,
                'selected_images': selected_images if selected_method_global != 'Contour' else 'Contour_drawing'
            }

            user_data_dir = os.path.abspath(r'/Users/kim-yoohyun/Desktop/School/4-1/Graduation Project/venv/user_data')
            os.makedirs(user_data_dir, exist_ok=True)
            user_file_path = os.path.join(user_data_dir, f"{name}.json")

            with open(user_file_path, 'w') as user_file:
                json.dump(user_data, user_file, indent=4)

            generate_captcha_and_answer()
            return jsonify({'message': '가입이 완료되었습니다!', 'success': True})

        generate_captcha_and_answer()
        return jsonify({'message': '사람이 아닙니다!', 'success': False}), 400

    except Exception as e:
        print(f"[ERROR] submit_path: {e}")
        return jsonify({'message': '오류입니다', 'success': False}), 500

if __name__ == '__main__':
    generate_captcha_and_answer()
    app.run(debug=True, port=5000)