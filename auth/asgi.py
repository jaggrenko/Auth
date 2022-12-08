import os
import sys

import uvicorn
from asgiref.wsgi import WsgiToAsgi

from app import create_app
from core.settings import FlaskSettings
from core.logger import LOGGING


SOURCE_DIR = os.path.dirname(__file__)
if SOURCE_DIR not in sys.path:
    sys.path.append(SOURCE_DIR)

wsgi = WsgiToAsgi(create_app())
flask_settings = FlaskSettings()

if __name__ == "__main__":
    uvicorn.run(
        "asgi:wsgi",
        host=flask_settings.FLASK_HOST,
        port=flask_settings.FLASK_PORT,
        log_config=LOGGING
    )
