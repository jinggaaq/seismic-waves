import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": {
            "ssl": {
                "ca": os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "certs",
                    "isrgrootx1.pem"
                )
            }
        }
    }

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "seismic-waves-production-secret"
    )