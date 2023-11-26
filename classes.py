from email.header import decode_header
import email
import imaplib
from config import *
import inspect
import re
import pandas as pd
import sqlite3
from typing import Union


class NoConnection(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class Mobile:

    @staticmethod
    def __extract_all_digits(text: str) -> (bool, str):
        digits_list = re.findall(r'\d+', text)
        all_digits = ''.join(digits_list)
        if len(all_digits) == 11:
            all_digits = '8' + all_digits[1:]
            return all_digits
        elif len(all_digits) > 11:
            print(f'Incorrect mobile {all_digits}: MORE then 11 digits')
        else:
            print(f'Incorrect mobile {all_digits}: LESS then 11 digits')
        return

    @classmethod
    def extract11digits(cls, mobile: str) -> str:
        cleared_mobile = cls.__extract_all_digits(str(mobile))
        return cleared_mobile

    @classmethod
    def extract10digits(cls, mobile: str) -> str:
        cleared_mobile = cls.__extract_all_digits(str(mobile))
        if cleared_mobile:
            return cleared_mobile[1:]


class DefCodes:

    region_msg = "Регион не определен"
    timezone_msg = "MSK---"

    @classmethod
    def get_region(cls, mobile: str) -> (str, str):
        if len(mobile) != 10:
            print(f'Incorrect number format: {mobile}')
            return

        num = int(mobile)

        def_codes_file_path = Path(__file__).parent / 'tel_codes_tz.csv'

        if def_codes_file_path.is_file():
            types = {'Timezone': "int", 'DEF': "int", 'Region': 'str', 'From': 'str', 'To': 'str'}
            df = pd.read_csv(def_codes_file_path, sep=';', header=0, dtype=types)

            df['Start'] = (df['DEF'].astype(str) + df['From'].astype(str)).astype(int)
            df['End'] = (df['DEF'].astype(str) + df['To'].astype(str)).astype(int)
            df['Timezone'] = df['Timezone'].astype(int)
            DEF = int(str(num)[:3])
            newdf = df.query('Start < @num & End > @num & DEF == @DEF')

            timezone = region = None
            try:
                region = newdf['Region'].values[0]
            except:
                print('Error in getting values from pandas df in Region')
                region = cls.region_msg

            try:
                timezone = newdf['Timezone'].values[0]
            except:
                print('Error in getting values from pandas df in Timezone')
                timezone = 99

            cls.timezone_msg = 'MSK+' + str(timezone) if timezone >= 0 else 'MSK' + str(timezone)
            cls.region_msg = region

            return cls.region_msg, cls.timezone_msg


class Mail:

    def __init__(self):
        self.subject = self.body = self.date = self.sender = ''
        self.letters_uids_list: list = []
        self.__imap = None

    def connect(self, server: str = 'mdvs.ttk.ru', mail_user: str = MAIL_USER, mail_pass: str = MAIL_PASS) -> None:
        self.__imap = imaplib.IMAP4_SSL(server)
        self.__imap.login(mail_user, mail_pass )
        self.__imap.select("inbox", readonly=True)
        print(f'Initial imap-class from CONNECT-method {self.__imap}')

    def get_letters_uids(self, subject: str = 'заявка', sender: str = '') -> None:

        if not isinstance(self.__imap, imaplib.IMAP4_SSL):
            raise NoConnection('You need launch CONNECT() method before')
            # print(f'Launch CONNECT-method from {inspect.currentframe().f_code.co_name.upper()} function')
            # self.connect()

        self.__imap.literal = subject.encode('utf-8')
        subj_command = ' SUBJECT' if subject else ''
        from_command = f'HEADER FROM "{sender}"' if sender else ''
        search_string = from_command + subj_command
        print('Mail query parameters: ' + (search_string + f' {subject}').strip())

        _, email_uids_list = self.__imap.uid('SEARCH', 'CHARSET', 'UTF-8', search_string)
        uids_list = email_uids_list[0].split()
        uids_int_list = [int(x.decode()) for x in uids_list]
        print(f'Mail uids: {uids_int_list}')
        self.letters_uids_list = uids_int_list
        # return uids_int_list

    def get_letter(self, uid: Union[int, bytes]) -> None:
        if isinstance(uid, int):
            uid = str(uid).encode()

        if not isinstance(self.__imap, imaplib.IMAP4_SSL):
            raise NoConnection('You need launch CONNECT() method before')
            # print(f'Launch CONNECT class-method from {inspect.currentframe().f_code.co_name.upper()} function')
            # self.connect()

        _, byte_msg = self.__imap.uid('fetch', uid, '(RFC822)')

        raw_message = email.message_from_bytes(byte_msg[0][1])

        subject = decode_header(raw_message['Subject'])[0][0].decode()
        body = raw_message.get_payload()
        date = raw_message["Date"]  # email.utils.parsedate_tz(raw_message["Date"])
        sender = raw_message["Return-path"]   # email.utils.parseaddr(raw_message['From'])

        if isinstance(body, list):
            for i in body:
                if not i.is_multipart():
                    body = i.get_payload(decode=True).decode('utf-8').strip()

        self.body, self.date, self.sender, self.subject = body, date, sender, subject
        # return subject, body, date, sender

    def parse_body(self):
        if not self.body:
            print('Letter body is empty. Perhaps, you need to run GET_LETTER() method before')
            return ''

        name = re.search('Name:.*<br>', self.body)
        name = name[0].split(':')[1][:-4].strip() if name else "==No name=="
        mobile = re.search('Phone:.*<br>', self.body)
        mobile = mobile[0].split(':')[1][:-4].strip() if mobile else "==No mobile=="
        body_text = re.search('Textarea:.*<br>', self.body)
        body_text = body_text[0].split(':')[1][:-4].strip() if body_text else "==No text=="

        if mobile:
            num = Mobile.extract10digits(mobile)
            print(f'Parsed mobile: {num}')
            DefCodes.get_region(num)

        reg, timezone = DefCodes.region_msg, DefCodes.timezone_msg

        text = '\n'.join((name, mobile, body_text, reg, "Время региона: " + timezone, self.date))

        return(text)


class SendedUIDs:
    db_name = DB_NAME
    sended_uids_list = []

    @classmethod
    def get_sended_uids(cls):
        if cls.db_name.is_file():
            print("Database exsists")
            con = sqlite3.connect(cls.db_name)
            cur = con.cursor()
            res = cur.execute(f"SELECT * from  uids")

            res_list = res.fetchall()

            uids_list = []
            for i in res_list:
                uids_list.append(i[0])

            con.close()
            print(f'Sended uids: {uids_list}')
            cls.sended_uids_list = uids_list
            # return uids_list
        else:
            print("New database")
            con = sqlite3.connect(cls.db_name)
            cur = con.cursor()
            cur.execute("CREATE TABLE uids(uid INTEGER)")
            con.commit()
            con.close()
            cls.sended_uids_list = []
            # return []

    @classmethod
    def add_uid(cls, uid: int) -> None:
        con = sqlite3.connect(cls.db_name)
        cur = con.cursor()
        cur.execute(f"INSERT INTO uids(uid) VALUES ({uid})")
        con.commit()
        con.close()
        print(f'New uid {uid} added')
        return

    @classmethod
    def del_uid(cls, uid: int) -> None:
        con = sqlite3.connect(cls.db_name)
        cur = con.cursor()
        cur.execute(f"DELETE FROM uids WHERE uid={uid}")
        con.commit()
        con.close()
        print(f'Sended uid {uid} deleted')
        return
