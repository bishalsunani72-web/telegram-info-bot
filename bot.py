import requests
import json
import time
import os

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ================== FUNCTIONS ==================

def get_updates(offset=None):
    url = BASE_URL + "/getUpdates"
    params = {
        "timeout": 30,
        "offset": offset
    }
    response = requests.get(url, params=params)
    return response.json()


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = BASE_URL + "/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    if parse_mode:
        data["parse_mode"] = parse_mode

    requests.post(url, data=data)


def phone_lookup(number):
    try:
        response = requests.get(API_URL + number)
        return response.json()
    except:
        return None


# ================== MAIN LOOP ==================

def main():
    print("Bot started...")
    offset = None

    while True:
        try:
            updates = get_updates(offset)

            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]

                        if "text" in message:
                            text = message["text"]

                            # ===== START =====
                            if text == "/start":
                                keyboard = {
                                    "keyboard": [["📱 Phone Lookup"]],
                                    "resize_keyboard": True
                                }

                                send_message(
                                    chat_id,
                                    "👋 Welcome!\n\nSelect an option:",
                                    reply_markup=keyboard
                                )

                            # ===== BUTTON =====
                            elif text == "📱 Phone Lookup":
                                send_message(
                                    chat_id,
                                    "📞 Send 10 digit mobile number:"
                                )

                            # ===== VALID NUMBER =====
                            elif text.isdigit() and len(text) == 10:
                                send_message(chat_id, "🔍 Checking...")

                                api_response = phone_lookup(text)

                                if api_response:
                                    formatted = "<pre>" + json.dumps(api_response, indent=4) + "</pre>"

                                    send_message(
                                        chat_id,
                                        formatted,
                                        parse_mode="HTML"
                                    )
                                else:
                                    send_message(
                                        chat_id,
                                        "❌ API error."
                                    )

                            # ===== INVALID =====
                            else:
                                send_message(
                                    chat_id,
                                    "⚠️ Invalid input.\nSend valid 10 digit number."
                                )

            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
