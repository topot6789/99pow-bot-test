import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, CallbackQueryHandler
)

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从环境变量获取 Token
TOKEN = os.getenv('TOKEN')

if not TOKEN:
    logger.error("❌ 未找到 TOKEN 环境变量！")
    exit(1)

# 存储用户数据（生产环境建议用数据库）
user_data = {}

# ========== 命令处理函数 ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    user = update.effective_user
    welcome_text = f"""
👋 你好 {user.first_name}！

我是多功能机器人，支持以下功能：

📝 **任务管理**
  /add <任务> - 添加任务
  /list - 查看任务列表
  /done <编号> - 标记任务完成

🎮 **娱乐功能**
  /dice - 掷骰子
  /joke - 讲个笑话
  /quote - 随机名言

🔧 **实用工具**
  /weather <城市> - 查询天气（示例）
  /calc <表达式> - 简单计算

📊 **信息**
  /info - 用户信息
  /help - 显示帮助
    """
    
    keyboard = [
        [InlineKeyboardButton("📝 添加任务", callback_data="add_task"),
         InlineKeyboardButton("📋 查看任务", callback_data="list_tasks")],
        [InlineKeyboardButton("🎲 掷骰子", callback_data="roll_dice"),
         InlineKeyboardButton("😂 讲笑话", callback_data="tell_joke")],
        [InlineKeyboardButton("ℹ️ 帮助", callback_data="show_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help 命令"""
    help_text = """
🤖 **机器人命令列表**

📝 **任务管理**
  /add <任务> - 添加新任务
  /list - 显示所有任务
  /done <编号> - 标记任务完成
  /clear - 清空所有任务

🎮 **娱乐功能**
  /dice - 掷骰子 (1-6)
  /dice <数字> - 自定义范围掷骰子
  /joke - 随机笑话
  /quote - 励志名言

🔧 **实用工具**
  /weather <城市> - 查询天气（模拟）
  /calc <表达式> - 计算器
  /info - 用户信息

📊 **其他**
  /start - 开始使用
  /help - 显示此帮助
    """
    await update.message.reply_text(help_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /info 命令"""
    user = update.effective_user
    chat = update.effective_chat
    
    info_text = f"""
📊 **用户信息**

👤 用户名: {user.first_name} {user.last_name or ''}
🆔 User ID: {user.id}
💬 Chat ID: {chat.id}
📅 语言: {user.language_code or '未知'}
    """
    await update.message.reply_text(info_text)

# ========== 任务管理功能 ==========

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """添加任务"""
    if not context.args:
        await update.message.reply_text("❌ 请提供任务内容，例如：/add 学习Python")
        return
    
    task_text = ' '.join(context.args)
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {'tasks': []}
    
    user_data[user_id]['tasks'].append({
        'text': task_text,
        'completed': False
    })
    
    await update.message.reply_text(f"✅ 已添加任务: {task_text}")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """列出任务"""
    user_id = update.effective_user.id
    
    if user_id not in user_data or not user_data[user_id]['tasks']:
        await update.message.reply_text("📝 你的任务列表是空的！")
        return
    
    tasks = user_data[user_id]['tasks']
    task_list = ""
    for i, task in enumerate(tasks, 1):
        status = "✅" if task['completed'] else "⭕"
        task_list += f"{i}. {status} {task['text']}\n"
    
    await update.message.reply_text(f"📋 你的任务列表:\n{task_list}")

async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """标记任务完成"""
    user_id = update.effective_user.id
    
    if user_id not in user_data or not user_data[user_id]['tasks']:
        await update.message.reply_text("❌ 没有任务可标记完成")
        return
    
    try:
        task_num = int(context.args[0]) - 1
        tasks = user_data[user_id]['tasks']
        
        if 0 <= task_num < len(tasks):
            tasks[task_num]['completed'] = True
            await update.message.reply_text(f"✅ 已标记任务完成: {tasks[task_num]['text']}")
        else:
            await update.message.reply_text("❌ 无效的任务编号")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ 请提供任务编号，例如：/done 1")

# ========== 娱乐功能 ==========

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """掷骰子"""
    try:
        if context.args:
            max_num = int(context.args[0])
            result = random.randint(1, max_num)
            await update.message.reply_text(f"🎲 你掷出了: {result} (1-{max_num})")
        else:
            result = random.randint(1, 6)
            await update.message.reply_text(f"🎲 你掷出了: {result}")
    except ValueError:
        await update.message.reply_text("❌ 请提供有效的数字，例如：/dice 100")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """讲笑话"""
    jokes = [
        "为什么程序员不喜欢大自然？因为里面有太多bug！",
        "为什么计算机永远不会感冒？因为它有Windows！",
        "我写代码的速度比光速还快，但bug出现的速度更快！",
        "程序员最讨厌的单词：『这个功能很简单』",
        "我有个代码笑话要说给你听，但只有Python 3.5以上版本才能理解！"
    ]
    joke = random.choice(jokes)
    await update.message.reply_text(f"😂 {joke}")

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """随机名言"""
    quotes = [
        "「代码就像幽默，如果你需要解释，那就不够好」- Cory House",
        "「首先，解决问题。然后，写代码」- John Johnson",
        "「编程不是在打字，而是在思考」- Rich Hickey",
        "「最好的错误信息是没有错误信息」- Unknown",
        "「不要评论糟糕的代码，重写它」- Brian Kernighan"
    ]
    quote = random.choice(quotes)
    await update.message.reply_text(f"💡 {quote}")

# ========== 实用工具 ==========

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """模拟天气查询"""
    if not context.args:
        await update.message.reply_text("❌ 请提供城市名称，例如：/weather 北京")
        return
    
    city = ' '.join(context.args)
    weather_conditions = ["晴", "多云", "小雨", "阴天", "大雪", "暴雨"]
    temperature = random.randint(-10, 35)
    condition = random.choice(weather_conditions)
    
    await update.message.reply_text(
        f"🌤️ {city}的天气：\n"
        f"🌡️ 温度：{temperature}°C\n"
        f"☁️ 天气：{condition}\n"
        f"💡 提示：这是模拟数据"
    )

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """简单计算器"""
    if not context.args:
        await update.message.reply_text("❌ 请提供计算表达式，例如：/calc 2+2")
        return
    
    try:
        expression = ' '.join(context.args)
        # 安全评估表达式
        result = eval(expression, {"__builtins__": None}, {})
        await update.message.reply_text(f"🧮 {expression} = {result}")
    except:
        await update.message.reply_text("❌ 无效的数学表达式")

# ========== 按钮回调处理 ==========

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理内联按钮回调"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "add_task":
        await query.edit_message_text("点击这里添加任务： /add <任务内容>")
    elif callback_data == "list_tasks":
        user_id = query.from_user.id
        if user_id not in user_data or not user_data[user_id]['tasks']:
            await query.edit_message_text("📝 你的任务列表是空的！")
        else:
            tasks = user_data[user_id]['tasks']
            task_list = "".join([f"{i+1}. {'✅' if t['completed'] else '⭕'} {t['text']}\n" 
                               for i, t in enumerate(tasks)])
            await query.edit_message_text(f"📋 你的任务列表:\n{task_list}")
    elif callback_data == "roll_dice":
        result = random.randint(1, 6)
        await query.edit_message_text(f"🎲 你掷出了: {result}")
    elif callback_data == "tell_joke":
        jokes = ["为什么程序员分不清万圣节和圣诞节？因为 Oct 31 == Dec 25！"]
        await query.edit_message_text(f"😂 {random.choice(jokes)}")
    elif callback_data == "show_help":
        await query.edit_message_text("输入 /help 查看所有可用命令")

# ========== 错误处理 ==========

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理错误"""
    logger.error(f"更新 {update} 导致错误: {context.error}")

# ========== 主函数 ==========

def main() -> None:
    """启动机器人"""
    # 创建 Application
    application = Application.builder().token(TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    
    # 任务管理命令
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("done", done_task))
    
    # 娱乐命令
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("quote", quote_command))
    
    # 工具命令
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("calc", calc_command))
    
    # 按钮回调处理器
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # 错误处理
    application.add_error_handler(error_handler)
    
    # 启动机器人
    print("🤖 机器人正在启动...")
    application.run_polling()
    print("✅ 机器人已启动！")

if __name__ == "__main__":
    main()
