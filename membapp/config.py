class Config:
    ADMIN_EMAIL="test@memba.com"
    SECRET_KEY="4p)1SDFJ"

class LiveConfig(Config):
    ADMIN_EMAIL="admin@memba.com"
    SERVER_ADDRESS="https://server.memeba.com"

class TestConfig(Config):
    SERVER_ADDRESS="https://127.0.0.1:5000"