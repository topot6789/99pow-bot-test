import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv('TOKEN')
app = Flask(__name__)

# 创建 Telegram 应用
telegram_app = Application.builder().token(TOKEN).build()

@app.route('/')
def health_check():
    return "🤖 Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理 Telegram Webhook 更新"""
    update = Update.de_json(request.get_json(), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return 'OK'

def main():
    """设置 Webhook 并启动 Flask 应用"""
    # 获取 Railway 提供的 URL（需要设置环境变量）
    webhook_url = os.getenv('RAILWAY_STATIC_URL', 'https://your-app.railway.app')
    
    # 设置 Webhook
    telegram_app.bot.set_webhook(f"{webhook_url}/webhook")
    
    # 添加命令处理器
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("info", info_command))
    telegram_app.add_handler(CommandHandler("dice", dice_command))
    telegram_app.add_handler(CommandHandler("joke", joke_command))
    telegram_app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Webhook 机器人已启动!")
    
    # Flask 应用会在 Railway 的环境中自动处理请求

if __name__ == "__main__":
    main()
    # Railway 会处理 Flask 应用的运行
