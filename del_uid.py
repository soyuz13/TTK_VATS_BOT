import main
from config import DB_NAME
main.get_sended_uids(DB_NAME)

num = input("Enter uid-number for deleting from db: ")

if num:
    print(main.del_uid(num))
else:
    print("Nothing to delete")