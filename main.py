from classes import Mail, SendedUIDs
from config import CHAT_ID, BOT_TOKEN
import telebot


def main():
    mail = Mail()
    sended = SendedUIDs()
    bot = telebot.TeleBot(token=BOT_TOKEN)

    new_uids = set(mail.get_letters_uids('заявка')).difference(set(sended.get_sended_uids()))

    for uid in new_uids:
        mail.get_letter(uid)
        text = mail.parse_body()
        bot.send_message(chat_id=CHAT_ID, text=text)


if '__name__' == '__main__':
    main()
