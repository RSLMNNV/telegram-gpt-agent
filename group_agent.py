{\rtf1\ansi\ansicpg1251\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import logging\
import asyncio\
from datetime import datetime\
\
from telegram import Update, Chat, ChatAction\
from telegram.ext import (\
    ApplicationBuilder, ContextTypes,\
    CommandHandler, MessageHandler, filters\
)\
\
# --- \uc0\u1051 \u1086 \u1075 \u1080  ---\
logging.basicConfig(\
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",\
    level=logging.INFO\
)\
log = logging.getLogger("group-agent")\
\
# --- \uc0\u1050 \u1086 \u1085 \u1092 \u1080 \u1075  \u1080 \u1079  \u1087 \u1077 \u1088 \u1077 \u1084 \u1077 \u1085 \u1085 \u1099 \u1093  \u1086 \u1082 \u1088 \u1091 \u1078 \u1077 \u1085 \u1080 \u1103  ---\
BOT_TOKEN = os.environ["BOT_TOKEN"]\
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]\
MODEL = os.environ.get("MODEL", "gpt-4o-mini")\
MENTION_ONLY = os.environ.get("MENTION_ONLY", "true").lower() in ("1","true","yes","on")\
\
# --- OpenAI SDK v1 ---\
from openai import OpenAI\
oai = OpenAI(api_key=OPENAI_API_KEY)\
\
# --- \uc0\u1057 \u1080 \u1089 \u1090 \u1077 \u1084 \u1085 \u1099 \u1081  \u1089 \u1090 \u1080 \u1083 \u1100  (\u1087 \u1086 \u1076  \u1090 \u1077 \u1073 \u1103 ) ---\
SYSTEM_PROMPT = (\
    "\uc0\u1058 \u1099  \'97 \u1086 \u1089 \u1090 \u1088 \u1099 \u1081 , \u1087 \u1088 \u1103 \u1084 \u1086 \u1081  \u1080  \u1087 \u1086 \u1083 \u1077 \u1079 \u1085 \u1099 \u1081  \u1089 \u1086 \u1073 \u1077 \u1089 \u1077 \u1076 \u1085 \u1080 \u1082 . \u1050 \u1086 \u1088 \u1086 \u1090 \u1082 \u1086  \u1087 \u1086  \u1076 \u1077 \u1083 \u1091 , \u1073 \u1077 \u1079  \u1074 \u1086 \u1076 \u1099 , "\
    "\uc0\u1076 \u1088 \u1091 \u1078 \u1077 \u1083 \u1102 \u1073 \u1085 \u1086 -\u1080 \u1088 \u1086 \u1085 \u1080 \u1095 \u1085 \u1099 \u1081 . \u1056 \u1091 \u1089 \u1089 \u1082 \u1080 \u1081  \u1103 \u1079 \u1099 \u1082 , \u1089 \u1090 \u1080 \u1083 \u1100  \'97 \u1088 \u1072 \u1079 \u1075 \u1086 \u1074 \u1086 \u1088 \u1085 \u1099 \u1081 , \u1082 \u1088 \u1077 \u1087 \u1082 \u1080 \u1081 , \u1085 \u1086  \u1073 \u1077 \u1079  \u1086 \u1089 \u1082 \u1086 \u1088 \u1073 \u1083 \u1077 \u1085 \u1080 \u1081 . "\
    "\uc0\u1045 \u1089 \u1083 \u1080  \u1074 \u1086 \u1087 \u1088 \u1086 \u1089  \u1090 \u1077 \u1093 \u1085 \u1080 \u1095 \u1077 \u1089 \u1082 \u1080 \u1081  \'97 \u1076 \u1072 \u1074 \u1072 \u1081  \u1095 \u1105 \u1090 \u1082 \u1080 \u1077  \u1096 \u1072 \u1075 \u1080 . \u1045 \u1089 \u1083 \u1080  \u1087 \u1088 \u1086  \u1086 \u1088 \u1075 \u1072 \u1085 \u1080 \u1079 \u1072 \u1094 \u1080 \u1102  \'97 \u1082 \u1088 \u1072 \u1090 \u1082 \u1080 \u1081  \u1087 \u1083 \u1072 \u1085 . "\
    "\uc0\u1045 \u1089 \u1083 \u1080  \u1087 \u1088 \u1086 \u1074 \u1086 \u1094 \u1080 \u1088 \u1091 \u1102 \u1090  \'97 \u1089 \u1086 \u1093 \u1088 \u1072 \u1085 \u1103 \u1081  \u1089 \u1087 \u1086 \u1082 \u1086 \u1081 \u1089 \u1090 \u1074 \u1080 \u1077 , \u1086 \u1090 \u1074 \u1077 \u1095 \u1072 \u1081  \u1092 \u1072 \u1082 \u1090 \u1072 \u1084 \u1080 ."\
)\
\
# \uc0\u1043 \u1083 \u1086 \u1073 \u1072 \u1083 \u1100 \u1085 \u1099 \u1081  \u1092 \u1083 \u1072 \u1075  \u1088 \u1077 \u1078 \u1080 \u1084 \u1072 \
reply_all = not MENTION_ONLY\
\
def should_reply(update: Update, bot_username: str) -> bool:\
    """\uc0\u1042  \u1075 \u1088 \u1091 \u1087 \u1087 \u1077  \u1086 \u1090 \u1074 \u1077 \u1095 \u1072 \u1077 \u1084  \u1090 \u1086 \u1083 \u1100 \u1082 \u1086  \u1077 \u1089 \u1083 \u1080 :\
       - reply_all = True, \uc0\u1080 \u1083 \u1080 \
       - \uc0\u1073 \u1086 \u1090 \u1072  \u1091 \u1087 \u1086 \u1084 \u1103 \u1085 \u1091 \u1083 \u1080  @username, \u1080 \u1083 \u1080 \
       - \uc0\u1086 \u1090 \u1074 \u1077 \u1090 \u1080 \u1083 \u1080  \u1085 \u1072  \u1089 \u1086 \u1086 \u1073 \u1097 \u1077 \u1085 \u1080 \u1077  \u1073 \u1086 \u1090 \u1072 , \u1080 \u1083 \u1080 \
       - \uc0\u1101 \u1090 \u1086  \u1083 \u1080 \u1095 \u1085 \u1099 \u1081  \u1095 \u1072 \u1090 ."""\
    msg = update.effective_message\
    chat: Chat = update.effective_chat\
\
    if chat.type in ("private", "unknown"):\
        return True\
\
    if reply_all:\
        return True\
\
    # \uc0\u1059 \u1087 \u1086 \u1084 \u1080 \u1085 \u1072 \u1085 \u1080 \u1077 ?\
    if msg and msg.entities:\
        for ent in msg.entities:\
            if ent.type == "mention":\
                mention = msg.text[ent.offset: ent.offset + ent.length]\
                if mention.lower().strip("@") == bot_username.lower():\
                    return True\
\
    # \uc0\u1054 \u1090 \u1074 \u1077 \u1090  \u1085 \u1072  \u1073 \u1086 \u1090 \u1072 ?\
    if msg and msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_bot:\
        return True\
\
    return False\
\
async def set_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    try:\
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)\
    except Exception:\
        pass\
\
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    await update.message.reply_text(\
        "\uc0\u1071  \u1085 \u1072  \u1089 \u1074 \u1103 \u1079 \u1080 . \u1055 \u1080 \u1096 \u1080  \u1087 \u1086  \u1076 \u1077 \u1083 \u1091 . \u1042  \u1075 \u1088 \u1091 \u1087 \u1087 \u1077  \u1086 \u1090 \u1074 \u1077 \u1095 \u1072 \u1102  "\
        + ("\uc0\u1085 \u1072  \u1074 \u1089 \u1105  \u1087 \u1086 \u1076 \u1088 \u1103 \u1076 ." if reply_all else "\u1087 \u1086  \u1091 \u1087 \u1086 \u1084 \u1080 \u1085 \u1072 \u1085 \u1080 \u1102  @ \u1080  \u1074  \u1086 \u1090 \u1074 \u1077 \u1090 \u1072 \u1093 .")\
    )\
\
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    await update.message.reply_text(\
        "/start \'97 \uc0\u1087 \u1088 \u1086 \u1074 \u1077 \u1088 \u1080 \u1090 \u1100 , \u1095 \u1090 \u1086  \u1103  \u1078 \u1080 \u1074 \u1086 \u1081 \\n"\
        "/mode \'97 \uc0\u1087 \u1077 \u1088 \u1077 \u1082 \u1083 \u1102 \u1095 \u1080 \u1090 \u1100  \u1088 \u1077 \u1078 \u1080 \u1084  \u1086 \u1090 \u1074 \u1077 \u1090 \u1086 \u1074  (\u1091 \u1087 \u1086 \u1084 \u1080 \u1085 \u1072 \u1085 \u1080 \u1103 /\u1074 \u1089 \u1105 )\\n"\
        "\uc0\u1057 \u1086 \u1074 \u1077 \u1090 : \u1074  \u1075 \u1088 \u1091 \u1087 \u1087 \u1077  \u1079 \u1086 \u1074 \u1080  \u1084 \u1077 \u1085 \u1103  \u1095 \u1077 \u1088 \u1077 \u1079  @, \u1095 \u1090 \u1086 \u1073 \u1099  \u1086 \u1090 \u1074 \u1077 \u1090  \u1087 \u1088 \u1080 \u1096 \u1105 \u1083  \u1090 \u1077 \u1073 \u1077 ."\
    )\
\
async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    global reply_all\
    reply_all = not reply_all\
    await update.message.reply_text(\
        "\uc0\u1056 \u1077 \u1078 \u1080 \u1084  \u1087 \u1077 \u1088 \u1077 \u1082 \u1083 \u1102 \u1095 \u1105 \u1085 : " + ("\u1086 \u1090 \u1074 \u1077 \u1095 \u1072 \u1102  \u1085 \u1072  \u1074 \u1089 \u1105 " if reply_all else "\u1086 \u1090 \u1074 \u1077 \u1095 \u1072 \u1102  \u1090 \u1086 \u1083 \u1100 \u1082 \u1086  \u1087 \u1086  \u1091 \u1087 \u1086 \u1084 \u1080 \u1085 \u1072 \u1085 \u1080 \u1102 /\u1074  \u1086 \u1090 \u1074 \u1077 \u1090 \u1072 \u1093 ")\
    )\
\
async def generate_reply(user_text: str, username: str) -> str:\
    """\
    \uc0\u1042 \u1099 \u1079 \u1086 \u1074  OpenAI. \u1050 \u1086 \u1088 \u1086 \u1090 \u1082 \u1080 \u1081 , \u1087 \u1086  \u1076 \u1077 \u1083 \u1091 , \u1090 \u1074 \u1086 \u1081  \u1090 \u1086 \u1085 .\
    """\
    try:\
        resp = oai.chat.completions.create(\
            model=MODEL,\
            temperature=0.6,\
            max_tokens=350,\
            messages=[\
                \{"role": "system", "content": SYSTEM_PROMPT\},\
                \{"role": "user", "content": user_text\}\
            ]\
        )\
        return resp.choices[0].message.content.strip()\
    except Exception as e:\
        log.exception("OpenAI error: %s", e)\
        return "\uc0\u1057 \u1077 \u1088 \u1074 \u1080 \u1089  \u1084 \u1099 \u1096 \u1083 \u1077 \u1085 \u1080 \u1103  \u1074 \u1088 \u1077 \u1084 \u1077 \u1085 \u1085 \u1086  \u1090 \u1091 \u1087 \u1080 \u1090 . \u1055 \u1086 \u1074 \u1090 \u1086 \u1088 \u1080  \u1087 \u1086 \u1079 \u1078 \u1077 ."\
\
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    # \uc0\u1048 \u1075 \u1085 \u1086 \u1088  \u1073 \u1086 \u1090 \u1086 \u1074 \
    if update.effective_user and update.effective_user.is_bot:\
        return\
\
    bot = await context.bot.get_me()\
    if not should_reply(update, bot.username):\
        return\
\
    text = (update.message.text or "").strip()\
    if not text:\
        return\
\
    await set_typing(update, context)\
\
    # \uc0\u1053 \u1077 \u1073 \u1086 \u1083 \u1100 \u1096 \u1072 \u1103  \u1079 \u1072 \u1097 \u1080 \u1090 \u1072  \u1086 \u1090  \u1076 \u1091 \u1073 \u1083 \u1080 -\u1089 \u1087 \u1072 \u1084 \u1072 \
    await asyncio.sleep(0.2)\
\
    answer = await generate_reply(text, update.effective_user.username or "user")\
    if not answer:\
        answer = "\uc0\u1054 \u1082 ."\
\
    try:\
        await update.message.reply_text(answer)\
    except Exception as e:\
        log.exception("Send message error: %s", e)\
\
async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):\
    log.exception("Update error: %s", context.error)\
\
def main():\
    app = ApplicationBuilder().token(BOT_TOKEN).build()\
\
    app.add_handler(CommandHandler("start", cmd_start))\
    app.add_handler(CommandHandler("help", cmd_help))\
    app.add_handler(CommandHandler("mode", cmd_mode))\
\
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))\
\
    app.add_error_handler(on_error)\
\
    log.info("Bot started at %s", datetime.utcnow().isoformat())\
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)\
\
if __name__ == "__main__":\
    main()}