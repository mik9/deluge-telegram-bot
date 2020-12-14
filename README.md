Telegram bot for Deluge torrent client
---

Supported features:
- Accept torrent file and add to Deluge
- Pause all torrents (`/stopall`)
- Resume all torrents (`/startall`)

Configuration
---

Use next environment variables to configure bot:
- `TOKEN` - telegram bot token. Obtain one from https://t.me/BotFather
- `ALLOWED_USERS` - nickname list of users allowed to interact with your bot
- `DELUGE_HOST` - host/ip of your deluge daemon
- `DELUGE_PORT` - port of your deluge daemon. Default: 58846
- `DELUGE_USERNAME` - username of your deluge daemon
- `DELUGE_PASSWORD` password of your deluge daemon

Run with Docker
---

```yml
version: '2'

services:
  deluge_telegram_bot:
    image: mik9/deluge-telegram-bot
    environment:
    - TOKEN=<token>
    - ALLOWED_USERS=my_nickname
    - DELUGE_HOST=127.0.0.1
    - DELUGE_PORT=58846
    - DELUGE_USERNAME=localclient
    - DELUGE_PASSWORD=<password>
    restart: unless-stopped
```