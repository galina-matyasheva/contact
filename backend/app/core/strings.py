# === API Responses ===
CONTACT_SUCCESS_MESSAGE = "Обращение успешно отправлено"

# === Errors ===
RATE_LIMIT_MESSAGE = "Слишком много запросов. Пожалуйста, подождите."
AI_UNAVAILABLE_MESSAGE = "AI-сервис временно недоступен"
EMAIL_FAILED_MESSAGE = "Не удалось отправить email"
FORBIDDEN_MESSAGE = "Доступ запрещён"
FORBIDDEN_API_KEY_MESSAGE = "Доступ запрещён. Требуется X-Api-Key заголовок."
VALIDATION_ERROR_MESSAGE = "Ошибка валидации данных"
INTERNAL_ERROR_MESSAGE = "Внутренняя ошибка сервера"

# === Validation ===
PHONE_INVALID_MESSAGE = (
    "Некорректный формат телефона. Допустимы цифры, +, -, (), пробелы"
)

# === OpenAPI (Swagger) ===
SUMMARY_CONTACT = "Отправка формы обратной связи"
SUMMARY_HEALTH = "Проверка статуса сервиса"
SUMMARY_METRICS = "Статистика обращений"
APP_DESCRIPTION = "API для лендинг-презентации разработчика с AI-интеграцией"

# === Schema Descriptions ===
DESC_NAME = "Имя пользователя"
DESC_PHONE = "Телефон пользователя"
DESC_EMAIL = "Email пользователя"
DESC_COMMENT = "Комментарий или сообщение"
DESC_SENTIMENT = "Тональность: positive / negative / neutral"
DESC_CATEGORY = "Категория: partnership / support / feedback / other"
DESC_AUTO_REPLY = "Сгенерированный ответ"
