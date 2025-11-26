import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 获取环境变量
TOKEN = os.getenv('TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 你好 {user.first_name}！\n\n"
        f"我是稳定运行的 Telegram 机器人！\n"
        f"✅ 状态：正常运行\n"
        f"🚀 平台：Railway\n\n"
        f"可用命令：\n"
        f"/start - 开始使用\n"
        f"/help - 帮助信息\n"
        f"/echo - 回声测试"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = """
🤖 机器人帮助信息

这是一个稳定运行的 Telegram 机器人演示。

命令列表：
/start - 开始对话
/help - 显示帮助
/echo - 回声测试（回复你发送的消息）

功能：
- 稳定运行
- 快速响应
- 无冲突设计
    """
    await update.message.reply_text(help_text)

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /echo 命令"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔊 你说：{text}")
    else:
        await update.message.reply_text("请发送 /echo 后面加上你想回声的文字")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通文本消息"""
    text = update.message.text
    await update.message.reply_text(f"📝 收到消息：{text}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理错误"""
    logger.error(f"更新 {update} 导致错误: {context.error}")

def main():
    """主函数"""
    if not TOKEN:
        logger.error("❌ 未找到 TOKEN 环境变量")
        return
    
    # 创建应用
    application = Application.builder().token(TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo_command))
    
    # 添加消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 添加错误处理器
    application.add_error_handler(error_handler)
    
    # 启动机器人
    print("=" * 50)
    print("🤖 Telegram 机器人启动中...")
    print(f"✅ Token 前10位: {TOKEN[:10]}...")
    print("⏳ 开始轮询...")
    print("=" * 50)
    
    application.run_polling(
        drop_pending_updates=True,  # 丢弃挂起的更新，避免冲突
        allowed_updates=['message', 'callback_query']  # 只监听这些类型
    )

if __name__ == '__main__':
    main()
