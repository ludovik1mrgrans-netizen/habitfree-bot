import os

from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=data,
        timeout=10
    )


@app.route("/", methods=["GET"])
def home():
    return "HabitFree is running!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    message = update.get("message")

    if not message:
        return "OK", 200

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        keyboard = {
            "keyboard": [
                [{"text": "🚬 Никотин"}],
                [{"text": "🍺 Алкоголь"}],
                [{"text": "🧠 Другая привычка"}]
            ],
            "resize_keyboard": True
        }

        send_message(
            chat_id,
            "👋 <b>Привет! Я HabitFree.</b>\n\n"
            "Я помогу тебе постепенно взять вредную привычку "
            "под контроль и отслеживать свой прогресс.\n\n"
            "Без осуждения. Шаг за шагом. 💚\n\n"
            "<b>С чего хочешь начать?</b>",
            keyboard
        )

    elif text == "🚬 Никотин":
        send_message(
            chat_id,
            "🚬 <b>Начнём с никотина.</b>\n\n"
            "Что ты используешь чаще всего?\n\n"
            "Напиши: сигареты, вейп, снюс или другое."
        )

    elif text == "🍺 Алкоголь":
        send_message(
            chat_id,
            "🍺 <b>Понял.</b>\n\n"
            "Для начала расскажи: как часто ты обычно употребляешь алкоголь?"
        )

    elif text == "🧠 Другая привычка":
        send_message(
            chat_id,
            "🧠 Хорошо. Напиши, от какой привычки ты хотел бы избавиться."
        )

    else:
        send_message(
            chat_id,
            "Я тебя услышал. 💚\n\n"
            "Сейчас HabitFree находится в разработке. "
            "Скоро я смогу продолжить этот разговор."
        )

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
