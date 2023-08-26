<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="src\stickerinator.jpg" alt="Logo" width="80" height="80">

  <h3 align="center">Sticker-Inator</h3>

  <p align="center">
    An awesome telegram bot that helps you format and create stickers from <br> images, videos and video notes (telegram bubbles)
    <br />
    <a href="https://t.me/StickerinatorBot"><strong>Try out the bot »</strong></a>
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-bot">About The Bot</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#features">Features</a></li>
  </ol>
</details>



<!-- ABOUT THE BOT -->
## About The Bot

Sticker-Inator is a user-friendly Telegram bot designed to streamline the creation of stickers using images, videos, and video notes. Unlike the conventional @Stickers bot on Telegram, we've simplified the process for you, eliminating the need to manually format your media files.

### Why Choose Sticker-Inator? 
1. <b>Hassle-Free Sticker Creation</b>
With Sticker-Inator, you can say goodbye to the hassle of converting your files into the right format every time you want to create a sticker. We take care of the technicalities for you, ensuring a smooth and efficient sticker creation process. 
 
2. <b>Quick and Easy</b> 
Creating stickers has never been easier! Our bot condenses the task into just a few simple steps, saving you time and effort. Whether you're a seasoned sticker creator or a newcomer, you'll find our bot incredibly user-friendly. 
 
3. <b>Versatile Media Support</b>  
Sticker-Inator supports a wide range of media types, including images, videos, and video notes. Note: Animated type stickers are currently not supported.
 
4. <b>Seamless Integration with Telegram</b>
Our bot seamlessly integrates with Telegram, making it easy to share your stickers with friends and family directly through the bot. No need to switch between apps or deal with complex external tools.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

These are the tools we built Sticker-Inator with.

* [![Telegram]][Tele-url]
* [![Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

The following are steps you can take to run the telegram bot locally. 

### Installation

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
   BOT_TOKEN="YOUR_BOT_TOKEN"
   BOT_NAME="YOUR_BOT_NAME"
   ```
4. Run the following command to get the bot up locally
   ```js
   python main.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- Features EXAMPLES -->
## Features

Here are the commands that Sticker-Inator has currently:

```
/newpack - Creates a new stickerpack
/addsticker - Adds a sticker
/delsticker - Deletes a sticker
/delpack - Deletes a stickerpack
/help - Gets info on the bot
/cancel - Cancels current operation
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[Telegram]: https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
[Tele-url]: https://python-telegram-bot.org/
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://docs.python.org/3/