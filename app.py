import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import openai

# Get secret keys
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# If keys are missing, stop
if not TOKEN or not OPENAI_KEY:
    print("❌ Missing API keys!")
    exit(1)

openai.api_key = OPENAI_KEY

async def handle_message(update: Update, context):
    try:
        # Get the user's message
        user_text = update.message.text
        
        # Send to OpenAI for grading
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a TOEFL essay grader. Grade from 0-6. Give score and feedback."},
                {"role": "user", "content": f"Grade this essay: {user_text}"}
            ]
        )
        
        # Send the response back to the user
        await update.message.reply_text(response.choices[0].message.content)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    print("🤖 Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()