import os
import html
import random, re
import wikipedia
from typing import Optional, List
from requests import get

from io import BytesIO
from random import randint
import requests as r

from telegram import (
    Message,
    Chat,
    MessageEntity,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ParseMode,
    ChatAction,
    TelegramError,
)

from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from telegram.error import BadRequest

from Shoko import (
    dispatcher,
    OWNER_ID,
    SUDO_USERS,
    SUPPORT_USERS,
    WHITELIST_USERS,
    spamwtc,
)
from Shoko.__main__ import STATS, USER_INFO, GDPR
from Shoko.modules.disable import DisableAbleCommandHandler
from Shoko.modules.helper_funcs.extraction import extract_user, get_user
from Shoko.modules.helper_funcs.filters import CustomFilters
from Shoko.modules.helper_funcs.alternate import typing_action, send_action
from Shoko import client, SUDO_USERS
from telethon import events

TMP_DOWNLOAD_DIRECTORY = "./"

@client.on(events.NewMessage(pattern="^[!/]info(?: |$)(.*)"))
async def who(event):
    """ For .whois command, get info about a user. """
    
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    
    replied_user = await get_user(event)

    caption = await fetch_info(replied_user, event)

    message_id_to_reply = event.message.reply_to_msg_id

    if not message_id_to_reply:
        message_id_to_reply = None

    await event.reply(caption, parse_mode="html",
                      link_preview=False)

async def fetch_info(replied_user, event):
    """ Get details from the User object. """
    user_id = replied_user.user.id
    chat = event.chat_id
    first_name = replied_user.user.first_name
    last_name = replied_user.user.last_name
    username = replied_user.user.username
    user_bio = replied_user.about
    is_bot = replied_user.user.bot
    first_name = first_name.replace(
        "\u2060", "") if first_name else ("This User has no First Name")
    last_name = last_name.replace(
        "\u2060", "") if last_name else ("This User has no Last Name")
    username = "@{}".format(username) if username else (
        "This User has no Username")
    user_bio = "This User has no About" if not user_bio else user_bio

    caption = "<b>User info:</b> \n"
    caption += f"First Name: {first_name} \n"
    caption += f"Last Name: {last_name} \n"
    caption += f"Username: {username} \n"
    caption += f"Is Bot: {is_bot} \n"
    caption += f"ID: <code>{user_id}</code> \n \n"
    caption += f"Bio: \n<code>{user_bio}</code>"
    
    if user_id == OWNER_ID:
        caption += "\n\n<i>Aye this guy is my owner.\nI would never do anything against him!</i>"

    elif user_id in SUDO_USERS:
        caption += (
            "\n\n<i>This person is one of my sudo users! "
            "Nearly as powerful as my owner - so watch it.</i>"
        )

    elif user_id in SUPPORT_USERS:
        caption += (
            "\n\n<i>This person is one of my support users! "
            "Not quite a sudo user, but can still gban you off the map.</i>"
        )

    elif user_id in WHITELIST_USERS:
        caption += (
            "\n\n<i>This person has been whitelisted! "
            "That means I'm not allowed to ban/kick them.</i>"
        )
    
    try:
        sw = spamwtc.get_ban(int(user_id))
        if sw:
            caption += "\n\n<i>This person is banned in Spamwatch!</i>"
            caption += f"\nResason: <i>{sw.reason}</i>"
        else:
            pass
    except:
        pass  # Don't break on exceptions like if api is down?
    
    for mod in USER_INFO:
        try:
            mod_info = mod.__user_info__(user_id).strip()
        except TypeError:
            mod_info = mod.__user_info__(user_id, chat).strip()
        if mod_info:
            caption += "\n\n" + mod_info
        
    
    caption += f"\nPermanent Link To Profile: "
    caption += f"<a href=\"tg://user?id={user_id}\">{first_name}</a>"
    
    return caption

@client.on(events.NewMessage(pattern="^[!/]id(?: |$)(.*)"))
async def useridgetter(target):
    replied_user = await get_user(target)
    user_id = target.from_id
    user_id = replied_user.user.id
    username = replied_user.user.username 
    username = "@{}".format(username) if username else (
        "This User has no Username")
    await target.reply("**Name:** {} \n**User ID:** `{}`\n**Chat ID: `{}`**".format(
        username, user_id, str(target.chat_id)))

@run_async
@typing_action
def echo(update, context):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)
    message.delete()


@run_async
@typing_action
def gdpr(update, context):
    update.effective_message.reply_text("Deleting identifiable data...")
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text(
        "Your personal data has been deleted.\n\nNote that this will not unban "
        "you from any chats, as that is telegram data, not Shoko data. "
        "Flooding, warns, and gbans are also preserved, as of "
        "[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-to-erasure/), "
        "which clearly states that the right to erasure does not apply "
        '"for the performance of a task carried out in the public interest", as is '
        "the case for the aforementioned pieces of data.",
        parse_mode=ParseMode.MARKDOWN,
    )


MARKDOWN_HELP = """
Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>~strike~</code> wrapping text with '~' will produce strikethrough text
- <code>--underline--</code> wrapping text with '--' will produce underline text
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
""".format(
    dispatcher.bot.first_name
)


@run_async
@typing_action
def markdown_help(update, context):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, --underline--, *bold*, `code`, ~strike~ "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


@run_async
@typing_action
def wiki(update, context):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Loading...")
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔧 More Info...", url=wikipedia.page(kueri).url
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=pertama.message_id,
                text=wikipedia.summary(kueri, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}"
            )


@run_async
@typing_action
def ud(update, context):
    msg = update.effective_message
    args = context.args
    text = " ".join(args).lower()
    if not text:
        msg.reply_text("Please enter keywords to search!")
        return
    try:
        results = get(f"http://api.urbandictionary.com/v0/define?term={text}").json()
        reply_text = f'Word: {text}\nDefinition: {results["list"][0]["definition"]}'
        reply_text += f'\n\nExample: {results["list"][0]["example"]}'
    except IndexError:
        reply_text = (
            f"Word: {text}\nResults: Sorry could not find any matching results!"
        )
    ignore_chars = "[]"
    reply = reply_text
    for chars in ignore_chars:
        reply = reply.replace(chars, "")
    if len(reply) >= 4096:
        reply = reply[:4096]  # max msg lenth of tg.
    try:
        msg.reply_text(reply)
    except BadRequest as err:
        msg.reply_text(f"Error! {err.message}")


@run_async
@typing_action
def src(update, context):
    update.effective_message.reply_text(
        "Hey there! You can find what makes me click [here](www.github.com/amTanny/Shokobot).",
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )

@run_async
@typing_action
def getlink(update, context):
    args = context.args
    message = update.effective_message
    if args:
        pattern = re.compile(r"-\d+")
    else:
        message.reply_text("You don't seem to be referring to any chats.")
    links = "Invite link(s):\n"
    for chat_id in pattern.findall(message.text):
        try:
            chat = context.bot.getChat(chat_id)
            bot_member = chat.get_member(context.bot.id)
            if bot_member.can_invite_users:
                invitelink = context.bot.exportChatInviteLink(chat_id)
                links += str(chat_id) + ":\n" + invitelink + "\n"
            else:
                links += (
                    str(chat_id) + ":\nI don't have access to the invite link." + "\n"
                )
        except BadRequest as excp:
            links += str(chat_id) + ":\n" + excp.message + "\n"
        except TelegramError as excp:
            links += str(chat_id) + ":\n" + excp.message + "\n"

    message.reply_text(links)


@run_async
@send_action(ChatAction.UPLOAD_PHOTO)
def rmemes(update, context):
    msg = update.effective_message
    chat = update.effective_chat

    SUBREDS = [
        "meirl",
        "dankmemes",
        "AdviceAnimals",
        "memes",
        "meme",
        "memes_of_the_dank",
        "PornhubComments",
        "teenagers",
        "memesIRL",
        "insanepeoplefacebook",
        "terriblefacebookmemes",
    ]

    subreddit = random.choice(SUBREDS)
    res = r.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200:  # Like if api is down?
        msg.reply_text("Sorry some error occurred :(")
        return
    else:
        res = res.json()

    rpage = res.get(str("subreddit"))  # Subreddit
    title = res.get(str("title"))  # Post title
    memeu = res.get(str("url"))  # meme pic url
    plink = res.get(str("postLink"))

    caps = f"- <b>Title</b>: {title}\n"
    caps += f"- <b>Subreddit:</b> <pre>r/{rpage}</pre>"

    keyb = [[InlineKeyboardButton(text="Subreddit Postlink 🔗", url=plink)]]
    try:
        context.bot.send_photo(
            chat.id,
            photo=memeu,
            caption=(caps),
            reply_markup=InlineKeyboardMarkup(keyb),
            timeout=60,
            parse_mode=ParseMode.HTML,
        )

    except BadRequest as excp:
        return msg.reply_text(f"Error! {excp.message}")


@run_async
def slist(update, context):
    sfile = "List of SUDO & SUPPORT users:\n"
    sfile += f"- SUDO USER IDs; {SUDO_USERS}\n"
    sfile += f"- SUPPORT USER IDs; {SUPPORT_USERS}"
    with BytesIO(str.encode(sfile)) as output:
        output.name = "staff-ids.txt"
        update.effective_message.reply_document(
            document=output,
            filename="staff-ids.txt",
            caption="Here is the list of SUDO & SUPPORTS users.",
        )


@run_async
def stats(update, context):
    stats = "<b>Current Shoko stats:</b>\n" + "\n".join([mod.__stats__() for mod in STATS])
    result = re.sub(r'(\d+)', r'<code>\1</code>', stats)
    update.effective_message.reply_text(result, parse_mode=ParseMode.HTML)


# /ip is for private use
__help__ = """
An "odds and ends" module for small, simple commands which don't really fit anywhere

 - /id: Get the current group id. If used by replying to a message, gets that user's id.
 - /info: Get information about a user.
 - /wiki : Search wikipedia articles.
 - /rmeme: Sends random meme scraped from reddit.
 - /ud <query> : Search stuffs in urban dictionary.
 - /wall <query> : Get random wallpapers directly from bot! 
 - /reverse : Reverse searches image or stickers on google.
 - /gdpr: Deletes your information from the bot's database. Private chats only.
 - /markdownhelp: Quick summary of how markdown works in telegram - can only be called in private chats.
 *Translator*
 - /tr or /tl: - To translate to your language, by default language is set to english, use `/tr <lang code>` for some other language!
 - /splcheck: - As a reply to get grammar corrected text of gibberish message.
 - /tts: - To some message to convert it into audio format!
 *Weather*
  - /weather <city>: Gets weather information of particular place!
  \* To prevent spams weather command and the output will be deleted after 30 seconds
"""

__mod_name__ = "Miscs"

ECHO_HANDLER = CommandHandler("echo", echo, filters=CustomFilters.sudo_filter)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)
STATS_HANDLER = DisableAbleCommandHandler("stats", stats, filters=CustomFilters.sudo_filter)
GDPR_HANDLER = CommandHandler("gdpr", gdpr, filters=Filters.private)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
UD_HANDLER = DisableAbleCommandHandler("ud", ud)
GETLINK_HANDLER = CommandHandler(
    "getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID)
)
STAFFLIST_HANDLER = CommandHandler(
    "slist", slist, filters=Filters.user(OWNER_ID)
)
REDDIT_MEMES_HANDLER = DisableAbleCommandHandler("rmeme", rmemes)
SRC_HANDLER = CommandHandler("source", src, filters=Filters.private)

dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(STAFFLIST_HANDLER)
dispatcher.add_handler(REDDIT_MEMES_HANDLER)
dispatcher.add_handler(SRC_HANDLER)
