from classes import Mail, SendedUIDs
from config import CHAT_ID, BOT_TOKEN
import telebot


def main():
    mail = Mail()
    sended = SendedUIDs()
    bot = telebot.TeleBot(token=BOT_TOKEN)

    mail.connect()
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
