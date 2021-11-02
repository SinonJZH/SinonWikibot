from datetime import date
from requests.adapters import Response
import requests
import sys
import time


import wiki_lib as wb
import works
import config

# 信息确认
print('----------Confirm------------')
print('Api Adress:' + config.api_url)
print('Bot Name:' + config.bot_username)
print('-----------------------------')
confirm = input('Confirm?(Y/N)')
# 不确认则直接结束
if confirm != "Y":
    print("Aborted, no changes have been made.")
    sys.exit()

# 执行操作时共用Session
Session = requests.Session()

# 执行操作
wb.login(Session)

works.uma_music_update(Session)

# 结束操作
print("Task Finished!")
