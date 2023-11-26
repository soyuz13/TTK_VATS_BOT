from classes import SendedUIDs

SendedUIDs.get_sended_uids()
num = input("Enter uid-number for deleting from db: ")
if num:
    SendedUIDs.del_uid(int(num))
else:
    print("Nothing to delete")
