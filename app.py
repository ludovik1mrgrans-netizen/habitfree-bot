import os
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def save_user(telegram_id, first_name, username=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase variables are missing")
        return False

    url = f"{SUPABASE_URL}/rest/v1/users"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal"
    }

    data = {
        "telegram_id": telegram_id,
        "first_name": first_name,
        "username": username
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code in [200, 201, 204]:
            print(f"Supabase user saved: {telegram_id}")
            return True

        print(
            "Supabase error:",
            response.status_code,
            response.text
        )
        return False

    except Exception as e:
        print("Supabase request error:", str(e))
        return False
# Временно храним данные здесь.
# Позже подключим настоящую БД.
user_states = {}
profiles = {}
def update_user_profile(telegram_id, **fields):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase variables are missing")
        return False

    url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    try:
        response = requests.patch(
            url,
            headers=headers,
            json=fields,
            timeout=10
        )

        if response.status_code in [200, 204]:
            print(f"Supabase profile updated: {telegram_id}")
            return True

        print("Supabase update error:", response.status_code, response.text)
        return False

    except Exception as e:
        print("Supabase update request error:", str(e))
        return False
def load_user_profile(telegram_id):
    url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}&select=*"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            if data:
                return data[0]

        print("Supabase load error:", response.status_code, response.text)
        return None

    except Exception as e:
        print("Supabase load request error:", str(e))
        return None
        
def get_successful_days(telegram_id):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 0

    url = (
        f"{SUPABASE_URL}/rest/v1/checkins"
        f"?telegram_id=eq.{telegram_id}"
        f"&status=eq.success"
        f"&select=id"
    )

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return len(response.json())

    except Exception as e:
        print("Checkins count error:", str(e))

    return 0
    
def success_checkin_exists_today(telegram_id):
    today = datetime.utcnow().date().isoformat()

    url = (
        f"{SUPABASE_URL}/rest/v1/checkins"
        f"?telegram_id=eq.{telegram_id}"
        f"&status=eq.success"
        f"&note=eq.{today}"
        f"&select=id"
        f"&limit=1"
    )

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return len(response.json()) > 0

    except Exception as e:
        print("Checkin lookup error:", str(e))

    return False
    
def save_success_checkin(telegram_id):
    today = datetime.utcnow().date().isoformat()

    url = f"{SUPABASE_URL}/rest/v1/checkins"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "telegram_id": telegram_id,
        "status": "success",
        "note": today
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        return response.status_code in [200, 201]

    except Exception as e:
        print("Checkin save error:", str(e))
        return False
        
def get_relapse_count(telegram_id):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 0

    url = (
        f"{SUPABASE_URL}/rest/v1/checkins"
        f"?telegram_id=eq.{telegram_id}"
        f"&status=eq.relapse"
        f"&select=id"
    )

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return len(response.json())

    except Exception as e:
        print("Relapse count error:", str(e))

    return 0


def get_last_relapse_reason(telegram_id):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    url = (
        f"{SUPABASE_URL}/rest/v1/checkins"
        f"?telegram_id=eq.{telegram_id}"
        f"&status=eq.relapse"
        f"&select=note"
        f"&order=id.desc"
        f"&limit=1"
    )

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            rows = response.json()

            if rows:
                return rows[0].get("note")

    except Exception as e:
        print("Last relapse reason error:", str(e))

    return None 
def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    if keyboard:
        data["reply_markup"] = {
            "keyboard": keyboard,
            "resize_keyboard": True
        }

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=data,
        timeout=10
    )


def main_menu(chat_id):
    keyboard = [
        ["🆘 Мне сейчас хочется"],
        ["📊 Мой прогресс", "✅ Отметить день"],
        ["⚙️ Настройки"]
    ]

    send_message(
        chat_id,
        "🏠 <b>HabitFree</b>\n\n"
        "Что хочешь сделать?",
        keyboard
    )


def start_onboarding(chat_id, first_name):
    profiles[chat_id] = {
        "name": first_name,
        "habit": None,
        "habit_type": None,
        "amount": None,
        "goal": None,
        "start_date": None,
        "successful_days": 0
    }

    user_states[chat_id] = "choose_habit"

    keyboard = [
        ["🚬 Никотин"],
        ["🍺 Алкоголь"],
        ["🧠 Другая привычка"]
    ]

    send_message(
        chat_id,
        f"👋 <b>Привет, {first_name}!</b>\n\n"
        "Я HabitFree — помощник, который помогает постепенно "
        "менять вредные привычки.\n\n"
        "Без осуждения и давления. Мы будем двигаться маленькими шагами.\n\n"
        "<b>С чего хочешь начать?</b>",
        keyboard
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
    first_name = message.get("from", {}).get("first_name", "")
    text = message.get("text", "").strip()
    print("TELEGRAM TEXT:", repr(text), flush=True)
    username = message.get("from", {}).get("username")

        # START
    if text == "/start" or text.startswith("/start@"):
        save_user(chat_id, first_name, username)

        saved_profile = load_user_profile(chat_id)

        if saved_profile and saved_profile.get("goal"):
            profiles[chat_id] = {
                "name": first_name,
                "habit": saved_profile.get("habit_type"),
                "habit_type": saved_profile.get("product_type"),
                "amount": saved_profile.get("daily_amount"),
                "goal": saved_profile.get("goal"),
                "start_date": saved_profile.get("started_at"),
                "successful_days": get_successful_days(chat_id)
            }

            user_states[chat_id] = None
            main_menu(chat_id)
            return "OK", 200

        start_onboarding(chat_id, first_name)
        return "OK", 200

    # MENU
    if text in ["/menu", "🏠 Меню"]:
        main_menu(chat_id)
        return "OK", 200

    # CRAVING / СИЛЬНАЯ ТЯГА
    if text in ["/craving", "🆘 Мне сейчас хочется"]:
        user_states[chat_id] = "craving_level"

        keyboard = [
            ["1", "2", "3", "4", "5"],
            ["6", "7", "8", "9", "10"],
            ["🏠 Меню"]
        ]

        send_message(
            chat_id,
            "🆘 <b>Я рядом.</b>\n\n"
            "Сейчас не нужно решать всё навсегда.\n"
            "Наша задача — пережить ближайшие несколько минут.\n\n"
            "Оцени желание сорваться от <b>1 до 10</b>:",
            keyboard
        )
        return "OK", 200

           # PROGRESS
    print("REACHED PROGRESS CHECK:", repr(text), flush=True)

    if text == "/progress" or "Мой прогресс" in text:
        print("PROGRESS MATCHED", flush=True)

        profile = profiles.get(chat_id)

        if not profile:
            saved_profile = load_user_profile(chat_id)

            if saved_profile and saved_profile.get("goal"):
                profile = {
                    "name": first_name,
                    "habit": saved_profile.get("habit_type"),
                    "habit_type": saved_profile.get("product_type"),
                    "amount": saved_profile.get("daily_amount"),
                    "goal": saved_profile.get("goal"),
                    "start_date": saved_profile.get("started_at"),
                    "successful_days": get_successful_days(chat_id)
                }

                profiles[chat_id] = profile

        if not profile or not profile.get("goal"):
            send_message(
                chat_id,
                "Сначала пройди короткую настройку через /start."
            )
            return "OK", 200

        profile["successful_days"] = get_successful_days(chat_id)
        relapse_count = get_relapse_count(chat_id)
        last_relapse_reason = get_last_relapse_reason(chat_id)

        send_message(
            chat_id,
            "📊 <b>Твой прогресс</b>\n\n"
            f"🎯 Цель: {profile.get('goal', 'Не указана')}\n"
            f"🧠 Привычка: {profile.get('habit_type', 'Не указана')}\n"
            f"🔥 Успешных дней: {profile.get('successful_days', 0)}\n"
            f"⚠️ Срывов: {relapse_count}\n"
            f"📝 Последняя причина: {last_relapse_reason or 'Пока нет'}\n\n"
            "Каждый день — это не экзамен. Главное — "
            "замечать и продолжать движение."
        )

        return "OK", 200

    # DAILY CHECK-IN     

    # DAILY CHECK-IN
    if text == "✅ Отметить день":
        profile = profiles.get(chat_id)

        if not profile:
            send_message(chat_id, "Сначала напиши /start.")
            return "OK", 200

        keyboard = [
            ["✅ Получилось"],
            ["⚠️ Был срыв"],
            ["🏠 Меню"]
        ]

        user_states[chat_id] = "daily_check"

        send_message(
            chat_id,
            "Как прошёл сегодняшний день?",
            keyboard
        )
        return "OK", 200

    if text == "✅ Получилось":
        profile = profiles.get(chat_id)

        if success_checkin_exists_today(chat_id):
            send_message(
                chat_id,
                "✅ Сегодняшний день уже отмечен.\n\n"
                "Следующую отметку можно сделать завтра."
            )
            user_states[chat_id] = None
            main_menu(chat_id)
            return "OK", 200

        if profile:
            if save_success_checkin(chat_id):
                profile["successful_days"] = get_successful_days(chat_id)

                send_message(
                    chat_id,
                    "🔥 <b>Отлично.</b>\n\n"
                    "Сегодняшний день записан.\n"
                    "Не думай сейчас о месяце или годе — "
                    "следующий ориентир просто завтра."
                )
            else:
                send_message(
                    chat_id,
                    "Не удалось записать сегодняшний день. Попробуй ещё раз."
                )

        user_states[chat_id] = None
        main_menu(chat_id)
        return "OK", 200

    if text == "⚠️ Был срыв":
        user_states[chat_id] = "relapse_reason"

        send_message(
            chat_id,
            "Спасибо, что отметил это честно.\n\n"
            "Срыв — это информация о том, где было особенно трудно.\n\n"
            "Что произошло прямо перед этим?\n"
            "Например: стресс, компания, алкоголь, скука, конфликт или сильная тяга."
        )
        return "OK", 200

    state = user_states.get(chat_id)

    if state == "relapse_reason":
        reason = text.strip()
        today = datetime.utcnow().date().isoformat()

        url = f"{SUPABASE_URL}/rest/v1/checkins"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "telegram_id": chat_id,
            "status": "relapse",
            "note": f"{today}: {reason}"
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=10
            )

            print(
                "RELAPSE SAVE:",
                response.status_code,
                response.text,
                flush=True
            )

            if response.status_code not in (200, 201):
                send_message(
                    chat_id,
                    "Не получилось сохранить запись. Попробуй ещё раз."
                )
                return "OK", 200

        except Exception as e:
            print("RELAPSE SAVE ERROR:", str(e), flush=True)

            send_message(
                chat_id,
                "Не получилось сохранить запись. Попробуй ещё раз."
            )
            return "OK", 200

        user_states[chat_id] = None

        send_message(
            chat_id,
            "Записал. Спасибо, что отметил это честно.\n\n"
            f"📝 Причина: {reason}\n\n"
            "Срыв не отменяет предыдущий прогресс. "
            "Следующая задача — просто продолжить."
        )

        main_menu(chat_id)
        return "OK", 200
    # ONBOARDING — HABIT
    if state == "choose_habit":

        if text == "🚬 Никотин":
            profiles[chat_id]["habit"] = "nicotine"
            user_states[chat_id] = "nicotine_type"

            keyboard = [
                ["🚬 Сигареты"],
                ["💨 Вейп"],
                ["🔵 Снюс / никотиновые паучи"],
                ["Другое"]
            ]

            send_message(
                chat_id,
                "🚬 <b>Начнём с никотина.</b>\n\n"
                "Что ты используешь чаще всего?",
                keyboard
            )
            return "OK", 200

        if text == "🍺 Алкоголь":
            profiles[chat_id]["habit"] = "alcohol"
            user_states[chat_id] = "alcohol_frequency"

            keyboard = [
                ["Несколько раз в месяц"],
                ["1–3 раза в неделю"],
                ["4+ раза в неделю"],
                ["Каждый день"]
            ]

            send_message(
                chat_id,
                "🍺 Понял.\n\n"
                "Как часто ты обычно употребляешь алкоголь?",
                keyboard
            )
            return "OK", 200

        if text == "🧠 Другая привычка":
            profiles[chat_id]["habit"] = "other"
            user_states[chat_id] = "other_habit"

            send_message(
                chat_id,
                "Напиши, какую привычку ты хочешь изменить."
            )
            return "OK", 200

    # NICOTINE TYPE
    if state == "nicotine_type":
        profiles[chat_id]["habit_type"] = text
        user_states[chat_id] = "nicotine_amount"

        send_message(
            chat_id,
            "Понял 👍\n\n"
            "Сколько примерно ты используешь в день?\n\n"
            "Например: <b>10 сигарет</b> или <b>один картридж</b>."
        )
        return "OK", 200

    # NICOTINE AMOUNT
    if state == "nicotine_amount":
        profiles[chat_id]["amount"] = text
        user_states[chat_id] = "choose_goal"

        keyboard = [
            ["🚫 Полностью отказаться"],
            ["📉 Постепенно сократить"],
            ["🧠 Пока хочу понять привычку"]
        ]

        send_message(
            chat_id,
            "🎯 <b>Какой результат тебе сейчас ближе?</b>",
            keyboard
        )
        return "OK", 200

    # ALCOHOL FREQUENCY
    if state == "alcohol_frequency":
        profiles[chat_id]["habit_type"] = "Алкоголь"
        profiles[chat_id]["amount"] = text

        if text in ["4+ раза в неделю", "Каждый день"]:
            send_message(
                chat_id,
                "⚠️ <b>Важный момент.</b>\n\n"
                "Если алкоголь употребляется часто или в больших количествах, "
                "резкая самостоятельная отмена иногда может быть небезопасной.\n\n"
                "HabitFree не заменяет врача. При дрожи, судорогах, спутанности "
                "сознания, галлюцинациях или тяжёлом самочувствии нужна срочная "
                "медицинская помощь.\n\n"
                "Мы можем работать над привычкой, но не будем советовать "
                "небезопасную резкую отмену."
            )

        user_states[chat_id] = "choose_goal"

        keyboard = [
            ["🚫 Полностью отказаться"],
            ["📉 Постепенно сократить"],
            ["🧠 Пока хочу понять привычку"]
        ]

        send_message(
            chat_id,
            "🎯 Какой результат тебе сейчас ближе?",
            keyboard
        )
        return "OK", 200

    # OTHER HABIT
    if state == "other_habit":
        profiles[chat_id]["habit_type"] = text
        user_states[chat_id] = "choose_goal"

        keyboard = [
            ["🚫 Полностью отказаться"],
            ["📉 Постепенно сократить"],
            ["🧠 Пока хочу понять привычку"]
        ]

        send_message(
            chat_id,
            "Понял.\n\n🎯 Какой результат тебе сейчас ближе?",
            keyboard
        )
        return "OK", 200

    # GOAL
    if state == "choose_goal":
        profiles[chat_id]["goal"] = text
        profiles[chat_id]["start_date"] = datetime.utcnow().isoformat()
     
        update_user_profile(
        chat_id,
        habit_type=profiles[chat_id].get("habit"),
        product_type=profiles[chat_id].get("habit_type"),
        daily_amount=profiles[chat_id].get("amount"),
        goal=profiles[chat_id].get("goal"),
        started_at=profiles[chat_id]["start_date"]
    )
        user_states[chat_id] = None

        send_message(
            chat_id,
            "✅ <b>Твой профиль HabitFree готов.</b>\n\n"
            f"🎯 Цель: {text}\n"
            f"🧠 Привычка: {profiles[chat_id].get('habit_type')}\n\n"
            "Теперь мы можем отслеживать прогресс и помогать тебе "
            "в моменты сильной тяги."
        )

        main_menu(chat_id)
        return "OK", 200

    # CRAVING LEVEL
    if state == "craving_level" and text.isdigit():
        level = int(text)

        if 1 <= level <= 10:
            user_states[chat_id] = "craving_followup"

            if level >= 8:
                response = (
                    "🆘 <b>Сильная тяга. Действуем прямо сейчас.</b>\n\n"
                    "1️⃣ Отложи действие всего на 5 минут.\n"
                    "2️⃣ Уйди подальше от сигареты, алкоголя или другого триггера.\n"
                    "3️⃣ Выпей воды.\n"
                    "4️⃣ Сделай 5 медленных вдохов.\n\n"
                    "Теперь напиши мне одним словом:\n"
                    "<b>что вызвало тягу?</b>\n\n"
                    "Например: стресс, скука, компания, злость, после еды."
                )
            else:
                response = (
                    f"Понял — сейчас примерно <b>{level}/10</b>.\n\n"
                    "Попробуем не бороться с ощущением, а просто дать ему пройти.\n\n"
                    "Что произошло прямо перед появлением желания?"
                )

            send_message(chat_id, response)
            return "OK", 200

    # CRAVING FOLLOWUP
    if state == "craving_followup":
        user_states[chat_id] = None

        keyboard = [
            ["✅ Стало легче"],
            ["🆘 Всё ещё очень хочется"],
            ["🏠 Меню"]
        ]

        send_message(
            chat_id,
            f"Запомнил триггер: <b>{text}</b>.\n\n"
            "Теперь попробуй изменить ситуацию хотя бы на несколько минут: "
            "встань, смени комнату, выйди на улицу или переключись на другое действие.\n\n"
            "Как сейчас?",
            keyboard
        )
        return "OK", 200

    if text == "✅ Стало легче":
        send_message(
            chat_id,
            "💚 Хорошо.\n\n"
            "Ты только что пережил одну волну тяги, не действуя автоматически. "
            "Именно такие моменты постепенно меняют привычку."
        )
        main_menu(chat_id)
        return "OK", 200

    if text == "🆘 Всё ещё очень хочется":
        send_message(
            chat_id,
            "Тогда ещё не оставайся с этим один на один.\n\n"
            "Отложи решение ещё на 10 минут и постарайся физически удалить "
            "триггер из доступа.\n\n"
            "Если ситуация связана с алкоголем и у тебя появляются тяжёлые "
            "симптомы отмены или резко ухудшается самочувствие — обращайся "
            "за срочной медицинской помощью."
        )
        return "OK", 200

    # RELAPSE
    if state == "relapse_reason":
        user_states[chat_id] = None

        send_message(
            chat_id,
            f"Записал: <b>{text}</b>.\n\n"
            "Теперь мы знаем ещё один твой триггер. Не нужно ждать понедельника "
            "или начинать всё заново — следующий выбор можно сделать уже сегодня."
        )

        main_menu(chat_id)
        return "OK", 200

    # FALLBACK
    send_message(
        chat_id,
        "Не совсем понял сообщение.\n\n"
        "Нажми /start для новой настройки или /menu для главного меню."
    )

    return "OK", 200

print("REACHED APP START", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
