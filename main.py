import os
import csv
import boto3
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from datetime import datetime, time
from io import StringIO

# Dictionary to store registration data for each chat
registrations = {}

# Dictionary to store settings for each chat
settings = {}

def load_settings():
    # Example settings for each chat
    settings[123456789] = [
        {
            "header": "Morning session 7:00am-9:00am",
            "open_time": "18:00",
            "close_time": "04:00",
            "max_players": 6
        },
        {
            "header": "Afternoon session 4:00pm-6:00pm",
            "open_time": "04:00",
            "close_time": "14:00",
            "max_players": 10
        }
    ]

def load_registrations():
    use_s3 = os.getenv("USE_S3")
    if use_s3:
        s3 = boto3.client('s3')
        bucket_name = os.getenv("S3_BUCKET_NAME")
        object_key = os.getenv("S3_OBJECT_KEY")
        try:
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            csv_data = response['Body'].read().decode('utf-8')
            csv_reader = csv.reader(StringIO(csv_data))
            for row in csv_reader:
                chat_id, users = row[0], row[1:]
                registrations[int(chat_id)] = users
        except Exception as e:
            print(f"Error loading from S3: {e}")
    else:
        try:
            with open('registrations.csv', mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    chat_id, users = row[0], row[1:]
                    registrations[int(chat_id)] = users
        except FileNotFoundError:
            print("Local CSV file not found. Starting with empty registrations.")

def save_registrations():
    use_s3 = os.getenv("USE_S3")
    output = StringIO()
    csv_writer = csv.writer(output)
    for chat_id, users in registrations.items():
        csv_writer.writerow([chat_id] + users)

    if use_s3:
        s3 = boto3.client('s3')
        bucket_name = os.getenv("S3_BUCKET_NAME")
        object_key = os.getenv("S3_OBJECT_KEY")
        try:
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=output.getvalue())
        except Exception as e:
            print(f"Error saving to S3: {e}")
    else:
        with open('registrations.csv', mode='w') as file:
            file.write(output.getvalue())

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Beach Volleyball Registration Bot!')

def add(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user = ' '.join(context.args) if context.args else update.effective_user.full_name

    if chat_id not in registrations:
        registrations[chat_id] = []

    if user not in registrations[chat_id]:
        registrations[chat_id].append(user)
        update.message.reply_text(f'{user} added to the registration list.')
    else:
        update.message.reply_text(f'{user} is already in the registration list.')

    post_registration_list(update, context)
    save_registrations()

def remove(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user = ' '.join(context.args) if context.args else update.effective_user.full_name

    if chat_id in registrations and user in registrations[chat_id]:
        registrations[chat_id].remove(user)
        update.message.reply_text(f'{user} removed from the registration list.')
    else:
        update.message.reply_text(f'{user} is not in the registration list.')

    post_registration_list(update, context)
    save_registrations()

def post_registration_list(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id in registrations:
        registration_list = '\n'.join(registrations[chat_id])
        update.message.reply_text(f'Current Registration List:\n{registration_list}', parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('The registration list is currently empty.', parse_mode=ParseMode.MARKDOWN)

def open_registration(context: CallbackContext) -> None:
    chat_id = context.job.context['chat_id']
    session = context.job.context['session']
    context.bot.send_message(chat_id=chat_id, text=f"Registration open for: {session['header']}")

def close_registration(context: CallbackContext) -> None:
    chat_id = context.job.context['chat_id']
    session = context.job.context['session']
    registered_players = registrations.get(chat_id, [])
    registration_list = '\n'.join(registered_players)
    context.bot.send_message(chat_id=chat_id, text=f"Registration closed for: {session['header']}\n{registration_list}")
    registrations[chat_id] = []  # Clear the registration list
    save_registrations()

def schedule_jobs(job_queue: JobQueue):
    for chat_id, sessions in settings.items():
        for session in sessions:
            open_time = datetime.strptime(session['open_time'], "%H:%M").time()
            close_time = datetime.strptime(session['close_time'], "%H:%M").time()

            # Schedule open registration
            job_queue.run_daily(open_registration, open_time, context={'chat_id': chat_id, 'session': session})

            # Schedule close registration
            job_queue.run_daily(close_registration, close_time, context={'chat_id': chat_id, 'session': session})

def main():
    load_settings()
    load_registrations()
    token = os.getenv("TG_BOT_TOKEN")
    if not token:
        raise ValueError("No TG_BOT_TOKEN provided in environment variables")

    updater = Updater(token)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("remove", remove))

    schedule_jobs(job_queue)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()