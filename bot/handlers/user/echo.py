import os

import requests
from aiogram.types import Message
from aiogram import types, F
import tempfile
from loader import bot, dp

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

CLASS_NAMES = {
    -1: "O‘simlik topilmadi",
    0: "Kasallik aniqlanmadi yoki bazada yo‘q",
    1: "Olma — Qora dog‘ (Apple Scab)",
    2: "Olma — Qora chirish (Black Rot)",
    3: "Olma — Sedir zang kasalligi",
    4: "Olma — Sog‘lom",
    5: "Ko‘k meva (Blueberry) — Sog‘lom",
    6: "Gilos — Oqqurt (chang) kasalligi",
    7: "Gilos — Sog‘lom",
    8: "Makkajo‘xori — Oddiy zang",
    9: "Makkajo‘xori — Shimoliy chirish (Northern Blight)",
    10: "Makkajo‘xori — Sog‘lom",
    11: "Uzum — Qora chirish",
    12: "Uzum — Eskamezli (measles) kasalligi",
    13: "Uzum — Barg dog‘lanishi",
    14: "Uzum — Sog‘lom",
    15: "Apelsin — Greening (yashillik) kasalligi",
    16: "Shaftoli — Bakterial dog‘",
    17: "Bulgar qalampiri — Bakterial dog‘",
    18: "Bulgar qalampiri — Sog‘lom",
    19: "Kartoshka — Erta chirish (Early Blight)",
    20: "Kartoshka — Kech chirish (Late Blight)",
    21: "Kartoshka — Sog‘lom",
    22: "Malina — Sog‘lom",
    23: "Soya — Sog‘lom",
    24: "Qovoq — Oqqurt (chang) kasalligi",
    25: "Qulupnay — Barg kuyishi (Leaf Scorch)",
    26: "Qulupnay — Sog‘lom",
    27: "Pomidor — Bakterial dog‘",
    28: "Pomidor — Erta chirish (Early Blight)",
    29: "Pomidor — Kech chirish (Late Blight)",
    30: "Pomidor — Bargda mog‘or (Leaf Mold)",
    31: "Pomidor — Septoriya dog‘i (Septoria Spot)",
    32: "Pomidor — O‘rgimchak kanasi zarari (Spider Mites)",
    33: "Pomidor — Maqsadli dog‘ (Target Spot)",
    34: "Pomidor — Sariq barg burilishi virusi",
    35: "Pomidor — Mozaika virusi",
    36: "Pomidor — Sog‘lom"
}

async def get_plant_advice(class_name):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"O‘simlik kasalligi: {class_name}. "
        "Ushbu kasallik haqida qisqacha ma'lumot bering, qanday davolash usullari mavjud, "
        "qaysi o‘g‘itlar va kimyoviy moddalar tavsiya etiladi, shuningdek, o‘simlikni saqlab qolish uchun qanday choralar ko‘rish kerak."
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return "❌ OpenRouter AI'dan javob olishda xatolik yuz berdi."


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("♻️ Rasm tahlilga yuborilmoqda...")

    # Rasmni eng kattasini olish
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    file_data = await bot.download_file(file_path)

    # Rasmni vaqtincha faylga saqlash
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(file_data.read())
        temp_file_path = temp_file.name

    # Endpointga rasmni yuborish
    try:
        url = "http://localhost:8000/predict/"
        files = [
            ('file', ('rasm.jpg', open(temp_file_path, 'rb'), 'image/jpeg'))
        ]
        response = requests.post(url, files=files)

        if response.status_code == 200:
            try:
                response_data = response.json()  # JSON formatdagi javob
                plant_id = int(response_data.get("message", -99))  # message ni o‘qish
                class_name = CLASS_NAMES.get(plant_id, "Noma'lum ID")

                await message.reply(f"Aniqlangan holat: {class_name}")

                if plant_id > 0:
                    advice = await get_plant_advice(class_name)
                    await message.reply(advice)
                elif plant_id == -1:
                    await message.reply("Rasmda o‘simlik topilmadi. Iltimos, aniqroq rasm yuboring.")
                elif plant_id == 0:
                    await message.reply("Kasallik bazada topilmadi. Mutaxassisga murojaat qiling.")
            except Exception as e:
                await message.reply(f"❗️ Endpoint'dan noto‘g‘ri javob: {str(e)}")
        else:
            await message.reply("❌ API tahlilda muammo yuz berdi.")
    finally:
        os.remove(temp_file_path)


@dp.message()
async def fallback_handler(message: Message):
    await message.answer("Iltimos, o‘simlikning rasmini yuboring.")