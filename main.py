import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = ''
SESSIONS = {}

def getId(update: Update): 
    return update.message.chat.id
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=
                                   "👋 О, привет! Я помогу посчитать твой счет в баре, что бы не приходилось высчитывать с калькулятором свои позиции из общего счета. \n"
                                   + "\n 🚀 Будь на шаг впереди своих друзей. Главное - записывай сюда все, что заказываешь. А я все посчитаю за тебя 👌"
                                   + "\n "
                                   + "\n ⚠️ Вот как мной пользоваться:"
                                   + "\n 📔 Создай счет командой /new. "
                                   + "\n 🍺 Пиши мне позиции, которые заказываешь. Например: \"Пиво 200\" или \"Пиво 200.50\" "
                                   + "\n 🗒 Ты можешь сделать предварительный расчет: /pre_bill "
                                   + "\n 🏁 Сделай расчет и закрой счет: /bill")

async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = getId(update)
    if chat_id in SESSIONS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="😅 Рука дрогнула, боец? Сначала закрой существующий счет командой /bill")    
    else:
        SESSIONS[chat_id] = list()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="✍️ Счет открыт")

async def bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = getId(update)
    if chat_id not in SESSIONS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❗️ Ошибка: счет не создан.")
    else:
        bill = SESSIONS[chat_id]
        output = generate_bill_str(chat_id) + "-----\n Итого: " + str(calculate_bill(chat_id)) + " 💰." 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=output)
        del SESSIONS[chat_id]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🏁 Счет закрыт. Отправляемся в следующее место?")

async def pre_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = getId(update)
    if chat_id not in SESSIONS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❗️ Ошибка: счет не создан.")
    else:
        output = generate_bill_str(chat_id) + "-----\n Итого: " + str(calculate_bill(chat_id)) + " 💰." 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=output)

def generate_bill_str(chat_id):
    bill = SESSIONS[chat_id]
    output = ""
    for row in bill: 
        output = output + row["position"] + " " + str(row["price"]) + "\n"
    return output

def calculate_bill(chat_id):
    bill = SESSIONS[chat_id]
    result = 0
    for row in bill:
        result = result + row["price"]
        
    return result
    
def validate_row(message):
    words = message.split()
    if len(words) < 2:
        raise Exception('Uncorrect length')
    if not isinstance(words[0], str) or not isinstance(words[1], str):
        raise Exception('Uncorrect types')
    price = float(len(words) - 1)
            
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = getId(update)
    if chat_id not in SESSIONS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🤌 Для того, что бы добавить в счет позицию - его нужно создать. Воспользуйся командой /new")
    else:
        msg = update.message.text
        
        try:
            validate_row(update.message.text)
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="😞 Некорректный формат. Нужно вот так: \n\n Пиво 200 \n\n или \n\n Пиво 200.50")
            return
        msgs = msg.split()
        price = msgs[len(msgs) - 1]
        position = msg.replace(price, "")
        row = {}
        row["position"] = position
        row["price"] = float(price) 
        SESSIONS[getId(update)].append(row)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="👌 Запись добавлена")
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('new', new))
    application.add_handler(CommandHandler('bill', bill))
    application.add_handler(CommandHandler('pre_bill', pre_bill))
    application.add_handler(MessageHandler(filters.ALL, add))
    application.run_polling()