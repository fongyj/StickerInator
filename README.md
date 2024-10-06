<p align="center"><b>Sticker-Inator is a telegram sticker bot that creates stickers from images, videos and video notes</b></p>
<p align="center"><a href="https://t.me/StickerinatorBot">Try out the bot »</a></p>

---
### About The Bot

Sticker-Inator is a user-friendly Telegram bot designed to streamline the creation of stickers using images, videos, and video notes. Unlike the conventional @Stickers bot on Telegram, we've simplified the process for you, eliminating the need to manually format your media files.

#### Why Sticker-Inator? 

1. <b>Quick and Easy</b> 
Creating stickers has never been easier! Our bot condenses the task into just a few simple steps, saving you time and effort. Whether you're a seasoned sticker creator or a newcomer, you'll find our bot incredibly user-friendly. 
 
2. <b>Versatile Media Support</b>  
Sticker-Inator supports a wide range of media types, including images, videos, and video notes. Note: Animated type stickers are currently not supported.
 
3. <b>Seamless Integration with Telegram</b>
Our bot seamlessly integrates with Telegram, making it easy to share your stickers with friends and family directly through the bot. No need to switch between apps or deal with complex external tools.


#### Built With

These are the tools we built Sticker-Inator with.

* [![Telegram]][Tele-url]
* [![Python]][Python-url]


### Getting Started

The following are steps you can take to run the telegram bot locally. 

#### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/fongyj/StickerInator.git
   ```
2. Install requirements.txt
   ```sh
   pip install -r requirements.txt
   ```
3. Prepare a <i>.env</i> file with the following configuration. The field BOT_NAME will be appended to your sticker packs created.
   ```js
   BOT_TOKEN_STICKERINATOR="YOUR_BOT_TOKEN"
   BOT_NAME="YOUR_BOT_NAME"
   ```
4. Run the following command to get the bot up locally
   ```js
   python main.py
   ```

### Features

Here are the commands that Sticker-Inator has currently:

```
/newpack - Creates a new stickerpack
/addsticker - Adds a sticker
/delsticker - Deletes a sticker
/delpack - Deletes a stickerpack
/help - Gets info on the bot
/cancel - Cancels current operation
```

<!-- MARKDOWN LINKS & IMAGES -->
[Telegram]: https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
[Tele-url]: https://python-telegram-bot.org/
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://docs.python.org/3/