import requests
import json
import time
import os

# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ================= TELEGRAM FUNCTIONS =================

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

# ================= PHONE LOOKUP FUNCTION =================

def phone_lookup(number):
    try:
        headers = {
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json"
        }

        params = {
            "number": number
        }

        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}

# ================= MAIN LOOP =================

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

                            # START
                            if text == "/start":
                                keyboard = {
                                    "keyboard": [["📱 Phone Lookup"]],
                                    "resize_keyboard": True
                                }

                                send_message(
                                    chat_id,
                                    "👋 Welcome!\nSelect option:",
                                    reply_markup=keyboard
                                )

                            # BUTTON
                            elif text == "📱 Phone Lookup":
                                send_message(chat_id, "📞 Send 10 digit mobile number:")

                            # VALID NUMBER
                            elif text.isdigit() and len(text) == 10:
                                send_message(chat_id, "🔍 Checking...")

                                result = phone_lookup(text)

                                formatted = "<pre>" + json.dumps(result, indent=4) + "</pre>"

                                send_message(
                                    chat_id,
                                    formatted,
                                    parse_mode="HTML"
                                )

                            # INVALID
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
