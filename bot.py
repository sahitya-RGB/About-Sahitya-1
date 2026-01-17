import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatMemberStatus

from config import *
from database import *

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ================= KEYBOARDS =================

def join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Paid Channel", url=PAID_CHANNEL)],
        [
            InlineKeyboardButton(text="Must Join", url="https://t.me/channel1"),
            InlineKeyboardButton(text="Must Join", url="https://t.me/channel2")
        ],
        [
            InlineKeyboardButton(text="Must Join", url="https://t.me/channel3"),
            InlineKeyboardButton(text="Must Join", url="https://t.me/channel4")
        ],
        [InlineKeyboardButton(text="Must Folder", url=FOLDER_LINK)],
        [InlineKeyboardButton(text="💡 Joined 💡", callback_data="check_join")]
    ])

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Profile"), KeyboardButton(text="🎯 Referral")],
        [KeyboardButton(text="📞 Support")]
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Stats"), KeyboardButton(text="📢 Broadcast")],
        [KeyboardButton(text="👤 User Info"), KeyboardButton(text="📡 Channels")],
        [KeyboardButton(text="❌ Exit Admin")]
    ],
    resize_keyboard=True
)

# ================= HELPERS =================

async def check_all_channels(user_id):
    for channel in CHANNEL_IDS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]:
                return False
        except:
            return False
    return True

# ================= START =================

@dp.message(CommandStart())
async def start(message: Message):
    args = message.text.split()
    ref = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    add_user(message.from_user.id, message.from_user.full_name, ref)

    await message.answer_photo(
        photo="https://i.imgur.com/6XJbN9n.jpg",
        caption="⏳ Join All Channels And Click On Joined To Start Our Bot",
        reply_markup=join_keyboard()
    )

# ================= JOIN CHECK =================

@dp.callback_query(F.data == "check_join")
async def verify_join(call: CallbackQuery):
    ok = await check_all_channels(call.from_user.id)
    if not ok:
        await call.answer("⚠️ Pehle sab channels join karo", show_alert=True)
        return

    await call.message.answer(
        "✅ Access Granted!",
        reply_markup=main_menu
    )
    await call.answer()

# ================= USER MENU =================

@dp.message(F.text == "👤 Profile")
async def profile(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        return

    await message.answer(
        f"👤 Name: {user[1]}\n"
        f"🆔 ID: {user[0]}\n"
        f"📅 Joined: {user[2]}\n"
        f"👥 Referrals: {user[4]}"
    )

@dp.message(F.text == "🎯 Referral")
async def referral(message: Message):
    link = f"https://t.me/{(await bot.me()).username}?start={message.from_user.id}"
    await message.answer(f"🔗 Your Referral Link:\n{link}")

@dp.message(F.text == "📞 Support")
async def support(message: Message):
    await message.answer(f"📩 Support: {SUPPORT_LINK}")

# ================= ADMIN PANEL =================

@dp.message(Command("admin"))
async def admin_entry(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🔐 Admin Panel", reply_markup=admin_menu)

@dp.message(F.text == "📊 Stats")
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(referrals) FROM users")
    refs = cursor.fetchone()[0] or 0

    await message.answer(
        f"📊 BOT STATS\n\n"
        f"👥 Users: {users}\n"
        f"🔗 Referrals: {refs}"
    )

@dp.message(F.text == "📢 Broadcast")
async def broadcast_prompt(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("📢 Send broadcast message:")

@dp.message(F.text & ~F.text.startswith("/"))
async def broadcast_send(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    sent = 0

    for uid in users:
        try:
            await bot.send_message(uid[0], message.text)
            sent += 1
        except:
            pass

    await message.answer(f"✅ Broadcast sent to {sent} users")

@dp.message(F.text == "👤 User Info")
async def user_info_prompt(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🆔 Send User ID:")

@dp.message(F.text.regexp(r"^\d+$"))
async def user_info(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    user = get_user(int(message.text))
    if not user:
        await message.answer("❌ User not found")
        return

    await message.answer(
        f"👤 Name: {user[1]}\n"
        f"🆔 ID: {user[0]}\n"
        f"📅 Joined: {user[2]}\n"
        f"👥 Referrals: {user[4]}"
    )

@dp.message(F.text == "📡 Channels")
async def admin_channels(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = "📡 Required Channels:\n\n"
    for ch in CHANNEL_IDS:
        text += f"{ch}\n"

    await message.answer(text)

@dp.message(F.text == "❌ Exit Admin")
async def exit_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Exited Admin Panel", reply_markup=main_menu)

# ================= RUN =================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())