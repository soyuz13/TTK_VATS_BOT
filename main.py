#!/usr/bin/env python
# coding: utf-8

from email.header import decode_header
import email
import imaplib
import sqlite3
from pathlib import Path
import re

import telebot
from config import *


mail = imaplib.IMAP4_SSL('mdvs.ttk.ru')
mail.login(MAIL_USER, MAIL_PASS )
mail.select("inbox", readonly=True)

bot = telebot.TeleBot(token=BOT_TOKEN)


def get_sended_uids(db_name: str) -> list:

    if Path(db_name).is_file():
        print("Database exsists")
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        res = cur.execute(f"SELECT * from  uids")

        res_list = res.fetchall()

        uids_list = []
        for i in res_list:
            uids_list.append(i[0])

        con.close()
        return uids_list
    else:
        print("New database")
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("CREATE TABLE uids(uid INTEGER)")
        con.commit()
        con.close()
        return []


def check_uid_in_uids_list(uids_list: list, uid: int) -> bool:
    if uid in uids_list:
        return True
    else:
        return False


def get_letter(uid):
    _, byte_msg = mail.uid('fetch', uid, '(RFC822)')

    raw_message=email.message_from_bytes(byte_msg[0][1])

    msg_subject = decode_header(raw_message['Subject'])[0][0].decode()
    msg_body = raw_message.get_payload()
    msg_date = raw_message["Date"]  #email.utils.parsedate_tz(raw_message["Date"])
    #print(raw_message['Date'])
    msg_from = raw_message["Return-path"]

    if isinstance(msg_body, list):
        for i in msg_body:
            #print(i.get_content_type())
            if not i.is_multipart():
                msg_body = i.get_payload(decode=True).decode('utf-8').strip()

    return msg_subject, msg_body, msg_date, msg_from


def add_uid(uid: int) -> str:
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(f"INSERT INTO uids(uid) VALUES ({uid})")
    con.commit()
    con.close()
    return f'uid {uid} added'


def del_uid(uid):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(f"DELETE FROM uids WHERE uid={uid}")
    con.commit()
    con.close()
    return f'uid {uid} deleted'


def get_mail_uids() -> list:
    mail.literal = u"Заявка с сайта [b2b.ttk.ru]".encode('utf-8')
    #mail.literal = u"Дальний".encode('utf-8')
    _, email_uids_list = mail.uid('SEARCH', 'CHARSET', 'UTF-8', 'SUBJECT')

    uids_list = email_uids_list[0].split()
    email_uid = uids_list[-1]
    uids_int_list = [int(x.decode()) for x in uids_list]
    uids_int_list.sort()

    return uids_int_list


def main():

    sended_uids_list = get_sended_uids(DB_NAME)
    mail_uids = get_mail_uids()

    new_uids = set(mail_uids).difference(set(sended_uids_list))

    # print(sended_uids_list)
    # print(mail_uids)
    # print(new_uids)


    for uid in new_uids:
        msg_subject, msg_text, msg_date, msg_from = get_letter(str(uid).encode())
        # num = input(f'{get_mail_uids()}: ')

        name = re.search('Name:.*<br>', msg_text)
        name = name[0].split(':')[1][:-4].strip() if name else "=No name="

        mobile = re.search('Phone:.*<br>', msg_text)
        mobile = mobile[0].split(':')[1][:-4].strip() if mobile else "=No mobile="

        body = re.search('Textarea:.*<br>', msg_text)
        body = body[0].split(':')[1][:-4].strip() if body else "=No text="

        text = '\n'.join((name, mobile, body, msg_date))

        bot.send_message(chat_id=CHAT_ID, text=text)
        add_uid(uid)

        # print(name)
        # print(mobile)
        # print(text)
        # print('========================')


if __name__ == '__main__':
    main()
    # del_uid(376)


# #email.utils.parseaddr(raw_message['From'])
