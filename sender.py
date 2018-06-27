#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Bot
from config import *
from time import sleep
from util import generate_message
     
if __name__ == "__main__":     
    bot = Bot(TOKEN)

    while True:     
        try:
            with open("messages.txt", "r") as f:
                updates = f.read().split()
                
            message_text = generate_message()
            
            for message in updates:
                chat_id, message_id = message.split(":")
                try:
                    bot.edit_message_text(
                        chat_id=chat_id, 
                        message_id=message_id, 
                        text=message_text, 
                        parse_mode="Markdown",
                        disable_web_page_preview=True)
                except:
                    pass
        except Exception as e:
            print("Error:", e)
        
        sleep(120)