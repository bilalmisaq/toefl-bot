import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import openai

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
CHANNEL_ID = "@MisaqInternational"  # ← CHANGE TO YOUR CHANNEL!

if not TOKEN or not OPENAI_KEY:
    print("❌ Missing keys!")
    exit(1)

openai.api_key = OPENAI_KEY

async def is_member(user_id):
    try:
        member = await app.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # CHECK if user joined
    if not await is_member(user_id):
        # User hasn't joined - show join button AND check button
        keyboard = [
            [InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/MisaqInternational")],
            [InlineKeyboardButton("✅ Check Membership", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n\n"
            "⚠️ Please join our channel FIRST to use this bot:\n"
            "👉 @MisaqInternational\n\n"
            "1️⃣ Click 'Join Our Channel'\n"
            "2️⃣ Join the channel\n"
            "3️⃣ Come back and click 'Check Membership'",
            reply_markup=reply_markup
        )
        return
    
    # USER JOINED! Show MAIN MENU
    keyboard = [
        [InlineKeyboardButton("📚 TOEFL", callback_data="toefl")],
        [InlineKeyboardButton("🌍 IELTS", callback_data="ielts")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎉 **Welcome to Misaq Test Bot!**\n\n"
        "✅ You've joined our channel!\n"
        "Now select an option:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # CHECK MEMBERSHIP BUTTON
    if query.data == "check_membership":
        user_id = query.from_user.id
        
        if await is_member(user_id):
            # They joined! Show menu
            keyboard = [
                [InlineKeyboardButton("📚 TOEFL", callback_data="toefl")],
                [InlineKeyboardButton("🌍 IELTS", callback_data="ielts")],
                [InlineKeyboardButton("❓ Help", callback_data="help")],
                [InlineKeyboardButton("📞 Contact", callback_data="contact")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "✅ **You've joined!** 🎉\n\n"
                "Welcome to Misaq Test Bot!\n"
                "Select an option below:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # Still not joined
            keyboard = [
                [InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/MisaqInternational")],
                [InlineKeyboardButton("✅ Check Again", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ **You haven't joined yet!**\n\n"
                "Please join @MisaqInternational first:\n"
                "1️⃣ Click 'Join Our Channel'\n"
                "2️⃣ Join the channel\n"
                "3️⃣ Click 'Check Again'",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        return
    
    # TOEFL MENU
    if query.data == "toefl":
        keyboard = [
            [InlineKeyboardButton("✉️ Write an Email", callback_data="toefl_email")],
            [InlineKeyboardButton("💬 Academic Discussion", callback_data="toefl_discussion")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📚 **TOEFL Writing Tasks**\n\nChoose a task:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif query.data == "toefl_email":
        context.user_data['task'] = "email"
        await query.edit_message_text(
            "✉️ **Write an Email**\n\n"
            "📌 Task: Write an email (100-150 words) to your professor requesting an extension.\n\n"
            "✍️ Type your email below:",
            parse_mode="Markdown"
        )
    
    elif query.data == "toefl_discussion":
        context.user_data['task'] = "discussion"
        await query.edit_message_text(
            "💬 **Academic Discussion**\n\n"
            "📌 Task: Respond to: 'Should schools require uniforms? Give reasons.'\n\n"
            "✍️ Type your response below:",
            parse_mode="Markdown"
        )
    
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("📚 TOEFL", callback_data="toefl")],
            [InlineKeyboardButton("🌍 IELTS", callback_data="ielts")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
            [InlineKeyboardButton("📞 Contact", callback_data="contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎯 **Main Menu**\n\nSelect an option:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    else:
        await query.edit_message_text(
            f"🔄 {query.data.upper()} section coming soon! 🚀",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'task' not in context.user_data:
        await update.message.reply_text("⚠️ Please select a task from the menu first!")
        return
    
    user_text = update.message.text
    task_type = context.user_data['task']
    
    await update.message.reply_text("⏳ Grading...")
    
    if task_type == "email":
        prompt = f"Grade this email on Grammar, Spelling, Clarity, Sentence Variety (out of 5). Give overall score. Provide improved version. Email: {user_text}"
    else:
        prompt = f"Grade this discussion response on Grammar, Spelling, Clarity, Sentence Variety (out of 5). Give overall score. Provide improved version. Response: {user_text}"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    global app
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot running!")
    app.run_polling()

if __name__ == "__main__":
    main()
