import os
from dotenv import load_dotenv
os.system(f"python manage.py runserver 127.0.0.1:{os.getenv('PORT', '8001')}")