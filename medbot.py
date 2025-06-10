import os
from rembg import remove
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters




async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل /start أو /help أو صورة لمعالجة الخلفية.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    await context.bot.send_message(chat_id = update.effective_chat.id, text="Hi ,I am a background remval bot.To start click in /start")

async def star(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    await context.bot.send_message(chat_id = update.effective_chat.id, text="To remove a background from in an image, please send the image ")

def process_image(name_photo: str):
    name, _ = os.path.splitext(name_photo)
    output_photo_path = f"./processed/{name}.jpg"
    input = Image.open(f"./temp/{name_photo}")
    output = remove(input)
    # تحويل الصورة من RGBA إلى RGB (إزالة الشفافية)
    if output.mode == "RGBA":
        output = output.convert("RGB")
    output.save(output_photo_path)
    os.remove(f"./temp/{name_photo}")
    return output_photo_path





async def remove_background(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not os.path.exists("temp"):
        os.makedirs("temp")

    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        unique_file_id = update.message.photo[-1].file_unique_id
        name_photo = f"{unique_file_id}.jpg"
        file_id = file.file_id
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        file = await update.message.document.get_file()
        _, f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        name_photo = f"{unique_file_id}{f_ext}"
        file_id = file.file_id
    else:
        await update.message.reply_text("الرجاء إرسال صورة أو ملف صورة فقط.")
        return

    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive(custom_path=f"./temp/{name_photo}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="تم تنزيل الصورة بنجاح. الآن يمكنك استخدام أي خدمة لإزالة الخلفية من الصورة.")

    processed_image = process_image(name_photo)
    with open(processed_image, "rb") as img:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=img)
    os.remove(processed_image)

async def message_updetes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = update)



if __name__ == "__main__":
    application = ApplicationBuilder().token(token).build()


    help_handler = CommandHandler("help", help)
    star_handler = CommandHandler("start", star)
    
    message_updete = MessageHandler(filters.ALL, message_updetes)
    remove_background_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, remove_background)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), reply_message)

    application.add_handler(help_handler)
    application.add_handler(star_handler)
    application.add_handler(message_handler)
    application.add_handler(remove_background_handler)
    application.add_handler(message_updete)



    
    print("is working...")
    def print_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        print(f"User info: id={user.id}, name={user.full_name}, username={user.username}")
        return f"User info: id={user.id}, name={user.full_name}, username={user.username}"
    application.add_handler(CommandHandler("user_info", print_user_info))
    # Start the bot
    application.run_polling()