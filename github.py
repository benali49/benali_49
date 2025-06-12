import os
from rembg import remove
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from keep_alive import keep_alive


token ="_______________"

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📩 تم استلام رسالة نصية من المستخدم: {update.effective_user.username}")
    await update.message.reply_text("أرسل /start أو /help أو صورة لمعالجة الخلفية.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    print(f"❓ تم طلب المساعدة من المستخدم: {update.effective_user.username}")
    await context.bot.send_message(chat_id = update.effective_chat.id, text="مرحباً، أنا بوت لإزالة خلفيات الصور. للبدء اضغط على /start")

async def star(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    print(f"🚀 تم تشغيل الأمر /start من المستخدم: {update.effective_user.username}")
    await context.bot.send_message(chat_id = update.effective_chat.id, text="لإزالة خلفية الصورة، يرجى إرسال الصورة")

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
    print(f"🖼️ تم استلام صورة من المستخدم: {update.effective_user.username}")

    if not os.path.exists("temp"):
        os.makedirs("temp")
    if not os.path.exists("processed"):
        os.makedirs("processed")

    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        unique_file_id = update.message.photo[-1].file_unique_id
        name_photo = f"{unique_file_id}.jpg"
        file_id = file.file_id
        print(f"📷 معالجة صورة عادية: {name_photo}")
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        file = await update.message.document.get_file()
        _, f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        name_photo = f"{unique_file_id}{f_ext}"
        file_id = file.file_id
        print(f"📎 معالجة ملف صورة: {name_photo}")
    else:
        print("❌ تم إرسال ملف غير صحيح")
        await update.message.reply_text("الرجاء إرسال صورة أو ملف صورة فقط.")
        return

    print("⬇️ بدء تنزيل الصورة...")
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive(custom_path=f"./temp/{name_photo}")
    print("✅ تم تنزيل الصورة بنجاح")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="تم تنزيل الصورة بنجاح. جاري معالجة الخلفية...")

    print("🔄 بدء معالجة إزالة الخلفية...")
    processed_image = process_image(name_photo)
    print("✅ تم الانتهاء من معالجة الصورة")
    
    with open(processed_image, "rb") as img:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=img)
    print("📤 تم إرسال الصورة المعالجة للمستخدم")
    os.remove(processed_image)

async def print_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = f"معلومات المستخدم:\nالرقم التعريفي: {user.id}\nالاسم: {user.full_name}\nاسم المستخدم: {user.username}"
    await update.message.reply_text(info)
    print(f"User info: id={user.id}, name={user.full_name}, username={user.username}")

if __name__ == "__main__":
    try:
        print("🤖 بدء تشغيل البوت...")
        print(f"🔑 التوكن المستخدم: {token[:10]}...")
        
        application = ApplicationBuilder().token(token).build()

        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("start", star))
        application.add_handler(CommandHandler("user_info", print_user_info))
        
        # إضافة معالجات الرسائل
        application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, remove_background))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_message))

        print("✅ تم تحميل جميع المعالجات")
        print("🌐 بدء تشغيل خدمة keep_alive...")
        keep_alive()
        print("📡 البوت متصل ويعمل بنجاح!")
        print("🔄 جاري البحث عن الرسائل...")
        print("=" * 50)
        print("البوت جاهز! يمكنك الآن استخدامه في التليجرام")
        print("=" * 50)
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        print("تأكد من صحة التوكن والاتصال بالإنترنت") 
