#!/usr/bin/env python
from deluge_client import DelugeRPCClient
import base64
import logging
import os

from telegram import Update, Message, Document, File
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

allowed_users = os.getenv('ALLOWED_USERS').split(',')

torrent_size_limit = 10 * 1024 * 1024 # 10mb

def ensure_allowed(message: Message):
    if message.from_user.username not in allowed_users:
        raise Exception('You are not allowed!')

torrent_name = '/Users/mik/Downloads/Vognebortsi (Only the Brave) 2017 UHD DV 4K HDR BDRemux (2160p)[Hurtom].torrent'


def deluge_connect() -> DelugeRPCClient:
    host = os.getenv('DELUGE_HOST')
    if not host:
        raise Exception('DELUGE_HOST not set')
    port = os.getenv('DELUGE_PORT')
    if port:
        try:
            port = int(port)
        except Exception as e:
            raise Exception('DELUGE_PORT is not int ' + str(e))
    else:
        port = 58846
    
    username = os.getenv('DELUGE_USERNAME')
    if not username:
        raise Exception('DELUGE_USERNAME not set')
    password = os.getenv('DELUGE_PASSWORD')
    if not password:
        raise Exception('DELUGE_PASSWORD not set')

    client = DelugeRPCClient(host, port, username, password)
    client.connect()

    return client

client = deluge_connect()

def add_torrent(data: bytes):
    client.call('core.add_torrent_file', 'test.torrent', base64.b64encode(data), {})
    return True

def on_message(update: Update, context: CallbackContext) -> None:
    ensure_allowed(update.message)

    if d := update.message.document:
        if d.file_size > torrent_size_limit:
            update.message.reply_text('File too large')
            return

        f: File = d.get_file(timeout=20)
        if add_torrent(f.download_as_bytearray()):
            update.message.reply_text('Added succesfully')
            return
    else:
        update.message.reply_text('No torrent file found')

def stop_all(update: Update, context: CallbackContext) -> None:
    try:
        client.call('core.pause_session')
        update.message.reply_text('Paused succesfully')
    except Exception as e:
        update.message.reply_text('Error pausing: ' + e)

def start_all(update: Update, context: CallbackContext) -> None:
    try:
        client.call('core.resume_session')
        update.message.reply_text('Resumed succesfully')
    except Exception as e:
        update.message.reply_text('Error resuming: ' + e)

def main():
    updater = Updater(os.getenv('TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.document, on_message))
    dispatcher.add_handler(CommandHandler('stopall', stop_all))
    dispatcher.add_handler(CommandHandler('startall', start_all))

    updater.start_polling()
    updater.idle()    


if __name__ == "__main__":
    main()