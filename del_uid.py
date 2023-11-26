from classes import SendedUIDs
from config import DB_NAME

sended = SendedUIDs(DB_NAME)
sended.get_sended_uids()
print(sended.sended_uids_list)
num = input("Enter uid-number for deleting from db: ")
if num:
    SendedUIDs.del_uid(int(num))
else:
    print("Nothing to delete")
