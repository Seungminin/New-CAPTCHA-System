# Python 이미지 
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cahce-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# Flask 애플리케이션 실행
CMD ["python", "app.py"]