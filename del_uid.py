from classes import SendedUIDs

SendedUIDs.get_sended_uids()
num = int(input("Enter uid-number for deleting from db: "))
if num:
    SendedUIDs.del_uid(num)
else:
    print("Nothing to delete")
