# app/__init__.py
# 예: Flask 앱 인스턴스 생성 (필요 시)
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)