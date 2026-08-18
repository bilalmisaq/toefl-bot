import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import openai

# Get tokens from Railway environment variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

if not TOKEN or not OPENAI_KEY:
    print("❌ Missing environment variables!")
    print("TELEGRAM_TOKEN:", "✅" if TOKEN else "❌")
    print("OPENAI_API_KEY:", "✅" if OPENAI_KEY else "❌")
    exit(1)

openai.api_key = OPENAI_KEY

async def handle_message(update: Update, context):
    try:
        user_text = update.message.text
        print(f"📩 Received: {user_text[:50]}...")
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a TOEFL essay grader. Score 0-6. Give feedback."},
                {"role": "user", "content": f"Grade this essay: {user_text}"}
            ]
        )
        
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
        print("✅ Sent response")
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        await update.message.reply_text(error_msg)

def main():
    print("🚀 TOEFL Bot starting on Railway...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running! Waiting for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
