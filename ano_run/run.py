import sys
import os

# 添加项目的根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
