import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, TypeHandler

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 初始化 Flask 应用
app = Flask(__name__)

# 从环境变量获取配置
TOKEN = os.getenv('TOKEN')
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL', '')

if not TOKEN:
    logger.error("❌ 未找到 TOKEN 环境变量！")
    exit(1)

# 创建 Telegram 应用
application = Application.builder().token(TOKEN).build()

# 存储用户数据（生产环境建议用数据库）
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    user = update.effective_user
    welcome_text = f"""
👋 你好 {user.first_name}！

🤖 我是运行在 Railway 上的 Telegram 机器人！

✅ 状态: Webhook 模式正常运行

可用命令：
/start - 开始使用
/info - 机器人信息
/ping - 测试响应

🚀 部署平台: Railway
    """
    await update.message.reply_text(welcome_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /info 命令"""
    info_text = """
🤖 机器人信息

📍 运行平台: Railway
🔧 模式: Webhook
✅ 状态: 正常运行
🐍 语言: Python
📦 版本: 2.0 (Webhook)

这是一个使用 Webhook 模式的 Telegram 机器人，彻底解决了多实例冲突问题。
    """
    await update.message.reply_text(info_text)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /ping 命令"""
    await update.message.reply_text("🏓 Pong! 机器人正常运行！")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理错误"""
    logger.error(f"更新 {update} 导致错误: {context.error}")

# 添加处理器
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("info", info_command))
application.add_handler(CommandHandler("ping", ping_command))

# 初始化机器人
@app.before_first_request
def initialize_bot():
    """初始化机器人并设置 Webhook"""
    try:
        # 设置 Webhook
        if RAILWAY_STATIC_URL:
            webhook_url = f"{RAILWAY_STATIC_URL}/webhook"
            application.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook 已设置: {webhook_url}")
        else:
            logger.warning("⚠️ 未找到 RAILWAY_STATIC_URL，Webhook 未设置")
        
        logger.info("🤖 机器人初始化完成")
    except Exception as e:
        logger.error(f"❌ 机器人初始化失败: {e}")

@app.route('/')
def home():
    """健康检查端点"""
    return jsonify({
        "status": "running",
        "bot": "online",
        "mode": "webhook",
        "platform": "railway"
    })

@app.route('/webhook', methods=['POST'])
async def webhook():
    """处理 Telegram Webhook 更新"""
    try:
        # 处理更新
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return 'OK'
    except Exception as e:
        logger.error(f"Webhook 处理错误: {e}")
        return 'ERROR', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook_manual():
    """手动设置 Webhook（用于调试）"""
    try:
        if RAILWAY_STATIC_URL:
            webhook_url = f"{RAILWAY_STATIC_URL}/webhook"
            result = application.bot.set_webhook(webhook_url)
            return jsonify({"status": "success", "webhook_url": webhook_url, "result": result})
        else:
            return jsonify({"status": "error", "message": "RAILWAY_STATIC_URL not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    """删除 Webhook（用于调试）"""
    try:
        result = application.bot.delete_webhook()
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # 启动 Flask 应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
