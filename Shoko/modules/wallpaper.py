from bs4 import BeautifulSoup
import aiohttp
import os
from random import randint
import asyncio
from PIL import Image
from pySmartDL import SmartDL
from os import remove
from telegram import ChatAction
from telegram.ext import Filters, run_async
from Shoko.modules.disable import DisableAbleCommandHandler
from Shoko.modules.helper_funcs.alternate import typing_action, send_action
from Shoko import dispatcher

down_p = './'

async def soup(SELECTED_DL):
    async with aiohttp.ClientSession() as session:
        async with session.get(SELECTED_DL) as respe:
            text = await respe.read()
            D = str(respe._real_url)
    return [BeautifulSoup(text.decode('utf-8'), 'html5lib'),D]

async def walld(strin):
    if len(strin.split()) > 1:
        strin = '+'.join(strin.split())
    url = 'https://wall.alphacoders.com/search.php?search='
    none_got = ['https://wall.alphacoders.com/finding_wallpapers.php']
    none_got.append('https://wall.alphacoders.com/search-no-results.php')
    page_link = 'https://wall.alphacoders.com/search.php?search={}&page={}'
    resp = await soup(f'{url}{strin}')
    if resp[1] in none_got:
        return False
    if 'by_category.php' in resp[1]:
        page_link = str(resp[1]).replace('&amp;', '') + '&page={}'
        check_link = True
    else:
        check_link = False
    resp = resp[0]
    try:
        wall_num = list(resp.find('h1',{'class':'center title'}).text.split(' '))
        
        for i in wall_num:
            try:
                wall_num = int(i)
            except ValueError:
                pass
        
        page_num = resp.find('div', {'class': 'visible-xs'})
        page_num = page_num.find('input', {'class': 'form-control'})
        page_num = int(page_num['placeholder'].split(' ')[-1])
    except Exception:
        page_num = 1
    n = randint(1, page_num)
    if page_num != 1:
        if check_link:
            resp = await soup(page_link.format(n))
        else:
            resp = await soup(page_link.format(strin, n))
        resp = resp[0]
    a_s = resp.find_all('a')
    list_a_s = []
    tit_links = []
    r = ['thumb', '350', 'img', 'big.php?i', 'src', 'title']
    for a_tag in a_s:
        if all(d in str(a_tag) for d in r):
            list_a_s.append(a_tag)
    try:
        for df in list_a_s:
            imgi = df.find('img')
            li = str(imgi['src']).replace('thumb-350-', '')
            titl = str(df['title']).replace('|', '')
            titl = titl.replace('Image', '')
            titl = titl.replace('HD', '')
            titl = titl.replace('Wallpaper', '')
            titl = titl.replace('Background', '')
            if len(titl.split()) > 5:
                titl = ''.join(titl.split()[:5])
            p = (li,titl)
            tit_links.append(p)
    except Exception:
        pass
    if len(tit_links) ==  0:
        return False
    else:
        return tit_links


@run_async
def wall(update, context):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    q = " ".join(args)
    if not q:
        msg.reply_text("Give Some to Search!")
        return
    else:
        try:
            wall_list = asyncio.run(walld(q))
        except:
            msg.reply_text("Error Occured!")
            return 
        if not wall_list:
            msg.reply_text("No results found! Check your query.")
            return
        else:
            index = randint(0, len(wall_list) - 1) 
            wallpaper = wall_list[index]
            url_w = wallpaper[0]
            context.bot.send_photo(
                    chat_id,
                    photo=url_w,
                    caption=wallpaper[1],
                    reply_to_message_id=msg_id,
                    timeout=60,
                )
            context.bot.send_document(
                    chat_id,
                    document=url_w,
                    filename=q,
                    caption=wallpaper[1],
                    reply_to_message_id=msg_id,
                    timeout=60,
                )

WALL_HANDLER = DisableAbleCommandHandler("wall", wall)
dispatcher.add_handler(WALL_HANDLER)