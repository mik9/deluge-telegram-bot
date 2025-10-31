#!/usr/bin/env python
import base64
import logging
import os
import sys

from deluge_client import DelugeRPCClient
from telegram import File, Message, Update
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          MessageHandler, filters, ContextTypes)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

allowed_users = os.getenv('ALLOWED_USERS')
if not allowed_users:
    logging.error('No ALLOWED_USERS set')
    sys.exit(1)

allowed_users = allowed_users.split(',')

torrent_size_limit = 10 * 1024 * 1024  # 10mb


def ensure_allowed(message: Message):
    if message.from_user.username not in allowed_users:
        raise Exception('You are not allowed!')


def deluge_connect() -> DelugeRPCClient:
    host = os.getenv('DELUGE_HOST')
    if not host:
        raise RuntimeError('DELUGE_HOST not set')
    port = os.getenv('DELUGE_PORT')
    if port:
        try:
            port = int(port)
        except ValueError as e:
            raise ValueError('DELUGE_PORT is not int') from e
    else:
        port = 58846

    username = os.getenv('DELUGE_USERNAME')
    if not username:
        raise RuntimeError('DELUGE_USERNAME not set')
    password = os.getenv('DELUGE_PASSWORD')
    if not password:
        raise RuntimeError('DELUGE_PASSWORD not set')

    rpc_client = DelugeRPCClient(host, port, username, password)
    rpc_client.connect()

    return rpc_client


client = deluge_connect()


def log_call(res):
    logging.info("%s, connected = %s", res, client.connected)


def add_torrent(data: bytes):
    client.call('core.add_torrent_file', 'test.torrent',
                base64.b64encode(data), {})
    return True


async def on_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ensure_allowed(update.message)

    if d := update.message.document:
        if d.file_size > torrent_size_limit:
            update.message.reply_text('File too large')
            return

        f: File = d.get_file(timeout=20)
        if add_torrent(f.download_as_bytearray()):
            update.message.reply_text('Added successfully')
            return
    else:
        update.message.reply_text('No torrent file found')


async def stop_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        log_call(client.call('core.pause_session'))
        update.message.reply_text('Paused successfully')
    except Exception as e:
        update.message.reply_text('Error pausing: ' + e)


async def start_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        log_call(client.call('core.resume_session'))
        update.message.reply_text('Resumed successfully')
    except Exception as e:
        update.message.reply_text('Error resuming: ' + e)


def main():
    app = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    app.add_handler(MessageHandler(
        filters.Document.FileExtension("torrent"), on_torrent))
    app.add_handler(CommandHandler('stopall', stop_all))
    app.add_handler(CommandHandler('startall', start_all))

    app.run_polling()


if __name__ == "__main__":
    main()
