# Конфигурация, отвечающая за доступы (логины, пароли и т.д.) 
DB_USER = "postgres_library"
DB_PASSWORD = "1234567890"
DB_HOST = "172.18.0.1"
# DB_HOST = "library_db"
DB_PORT = "6000"
DB_NAME = "postgres_library"
DB_SESSION_ECHO = True # Используется при создании engine


SECRET_KEY = "VX0KvQRUTNOJRJJyAVntIsTUiJ+h4uvg+lcpJtB7elI="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30