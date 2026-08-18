import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import openai

# ========== SETUP ==========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
CHANNEL_ID = "@MisaqInternational"  # CHANGE THIS TO YOUR CHANNEL!

if not TOKEN or not OPENAI_KEY:
    print("❌ Missing keys!")
    exit(1)

openai.api_key = OPENAI_KEY
logging.basicConfig(level=logging.INFO)

# ========== CHECK IF USER JOINED CHANNEL ==========
async def is_member(user_id):
    try:
        member = await app.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ========== START COMMAND ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if user joined channel
    if not await is_member(user.id):
        keyboard = [[InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/yourchannel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n\n"
            "🎯 **Misaq Test Bot** - Free TOEFL & IELTS Practice!\n\n"
            "⚠️ Please join our channel first to unlock all features:\n"
            "👉 @yourchannel\n\n"
            "After joining, click /start again.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return
    
    # If they joined, show main menu
    keyboard = [
        [InlineKeyboardButton("📚 TOEFL", callback_data="toefl")],
        [InlineKeyboardButton("🌍 IELTS", callback_data="ielts")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎉 Welcome to **Misaq Test Bot**!\n\n"
        "Select an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ========== MAIN MENU BUTTONS ==========
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "toefl":
        keyboard = [
            [InlineKeyboardButton("📝 Build a Sentence", callback_data="toefl_sentence")],
            [InlineKeyboardButton("✉️ Write an Email", callback_data="toefl_email")],
            [InlineKeyboardButton("💬 Academic Discussion", callback_data="toefl_discussion")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📚 **TOEFL Writing Tasks**\n\n"
            "Choose a task to practice:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif query.data == "toefl_email":
        context.user_data['task'] = "email"
        await query.edit_message_text(
            "✉️ **Write an Email**\n\n"
            "📌 Task: Write an email (100-150 words) to your professor requesting an extension on your assignment.\n\n"
            "✍️ Type your email below:",
            parse_mode="Markdown"
        )
    
    elif query.data == "toefl_discussion":
        context.user_data['task'] = "discussion"
        await query.edit_message_text(
            "💬 **Academic Discussion**\n\n"
            "📌 Task: Write a response (100-120 words) to the professor's question:\n"
            "'Should schools require students to wear uniforms? Give reasons.'\n\n"
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
    
    elif query.data in ["ielts", "help", "contact"]:
        await query.edit_message_text(
            f"🔄 **Coming Soon!**\n\nThe {query.data.upper()} section is under development.\n\nStay tuned! 🚀",
            parse_mode="Markdown"
        )

# ========== GET USER'S ESSAY AND GRADE IT ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'task' not in context.user_data:
        await update.message.reply_text("Please select a task from the menu first!")
        return
    
    user_text = update.message.text
    task_type = context.user_data['task']
    
    await update.message.reply_text("⏳ Grading your work... Please wait!")
    
    # Create the prompt based on task type
    if task_type == "email":
        prompt = f"""
You are an expert TOEFL writing evaluator. Grade this email on 5 points for:
1. Grammar
2. Spelling
3. Clarity
4. Sentence Variety
5. Overall Score

Also provide:
- A revised 5/5 version
- Short feedback

User's Email:
{user_text}

Return in this exact format:
📊 **Score Breakdown:**
Grammar: X/5
Spelling: X/5
Clarity: X/5
Sentence Variety: X/5
Overall: X/5

✅ **5/5 Revised Version:**
[Write the improved version]

💡 **Feedback:**
[Write 2-3 sentences]
"""
    
    else:  # discussion
        prompt = f"""
You are an expert TOEFL writing evaluator. Grade this discussion response on 5 points for:
1. Grammar
2. Spelling
3. Clarity
4. Sentence Variety
5. Overall Score

Also provide:
- A revised 5/5 version
- Short feedback

User's Response:
{user_text}

Return in this exact format:
📊 **Score Breakdown:**
Grammar: X/5
Spelling: X/5
Clarity: X/5
Sentence Variety: X/5
Overall: X/5

✅ **5/5 Revised Version:**
[Write the improved version]

💡 **Feedback:**
[Write 2-3 sentences]
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        reply = response.choices[0].message.content
        await update.message.reply_text(reply, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ========== RUN THE BOT ==========
def main():
    global app
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
