from classes import Mail, SendedUIDs
from config import *
import telebot


def main():
    mail = Mail(mail_user=MAIL_USER, mail_pass=MAIL_PASS)
    sended = SendedUIDs(db_name=DB_NAME)
    bot = telebot.TeleBot(token=BOT_TOKEN)

    mail.get_letters_uids(subject='заявка')
    sended.get_sended_uids()

    new_uids = set(mail.letters_uids_list).difference(set(sended.sended_uids_list))
    print(f'New uids: {new_uids}')

    for uid in new_uids:
        mail.get_letter(uid)
        text = mail.parse_body()
        sended.add_uid(uid)
        bot.send_message(chat_id=CHAT_ID, text=text)


if __name__ == '__main__':
    main()
