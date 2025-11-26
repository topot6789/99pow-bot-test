import os
import logging
import time
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TOKEN')

async def start(update, context):
    await update.message.reply_text("🤖 机器人正常运行！")

def main():
    # 等待旧实例关闭
    time.sleep(15)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("🤖 机器人启动中...")
    application.run_polling()

if __name__ == "__main__":
    main()
