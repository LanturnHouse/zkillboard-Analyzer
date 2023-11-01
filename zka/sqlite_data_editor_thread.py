# # 컬럼
# # kill_mail_id / user_id / kill_time / SystemID / fitting(json2str) / attakers(json2str)
# import sqlite3
# con = sqlite3.connect('./everef_killmails_data.db')
# cur = con.cursor()

# try:
#     # 테이블 생성 쿼리
#     cur.execute("CREATE TABLE EverefKillmails(KillmailID INTEGER, CharacterID INTEGER, CorporationID INTEGER, ShipID INTEGER, SystemID INTEGER, KillTime TEXT, Fitting TEXT, AttakersID TEXT, Attakers TEXT);")
# except:
#     pass


# =======================
# killmails 데이터 insert

def insert_killmails_datas():
    import threading
    import json
    import os
    from tqdm import tqdm
    import time
    import sqlite3

    con = sqlite3.connect('./everef_killmails_data.db')
    cur = con.cursor()

    try:
    # 테이블 생성 쿼리
        cur.execute("CREATE TABLE EverefKillmails(KillmailID INTEGER, CharacterID INTEGER, CorporationID INTEGER, ShipID INTEGER, SystemID INTEGER, KillTime TEXT, Fitting TEXT, AttakersIDs TEXT, Attakers TEXT);")
        cur.execute("create index CharacterID_index on EverefKillmails (CharacterID ASC);")
        cur.execute("CREATE INDEX GetCharacterIDByTime_index ON EverefKillmails (CharacterID ASC, KillTime DESC);")
    except:
        pass

    killmails_data_list = []

    def insert_datas(file_name):

        json_files = os.listdir(merge_target_folder + f"/{file_name}/killmails")
        for json_file_name in tqdm(json_files):
            try:
                with open(merge_target_folder + f"/{file_name}/killmails/" + json_file_name, "r",  encoding='utf-8') as f:
                    data = json.load(f)
                    f.close()
                attakers_id = []
                # attakers_id = str([i["character_id"] for i in data["attackers"]])
                for i in data["attackers"]:
                    try:
                        attakers_id.append(i["character_id"])
                    except:
                        pass
                killmails_data_list.append((data["killmail_id"],
                                data["victim"]["character_id"],
                                data["victim"]["corporation_id"],
                                data["victim"]["ship_type_id"],
                                data["solar_system_id"],
                                str(data["killmail_time"]),
                                str(data["victim"]["items"]),
                                str(attakers_id),
                                str(data["attackers"])))
                
                del data, attakers_id
            except:
                pass


    merge_target_folder = r"C:\python\zka_web\zka_web\everef_killmails"
    file_list = os.listdir(merge_target_folder)
    _file_list = []
    # print(f"files: {file_list}")
    for file_name in file_list:
        if file_name.startswith("10-") or file_name.startswith("09-") or file_name.startswith("08-"):
            if file_name.endswith(".bz2") == False:
                _file_list.append(file_name)
    print(f"files: {_file_list}")
    ths = []
    for file_name in _file_list:
        th = threading.Thread(target=insert_datas, args=(file_name,))
        th.start()
        ths.append(th)


    # th = threading.Thread(target=insert_datas, args=(_file_list,))
    # th.start()
    # ths.append(th)


    while True:
        ths_end = True
        for th in ths:
            if th.is_alive():
                ths_end = False
                continue
        if ths_end:
            break
        time.sleep(1)


    cur.executemany('INSERT INTO EverefKillmails VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);', killmails_data_list)

    con.commit()
    con.close()

    print("done!")


# ==================================


if __name__ == "__main__":
    insert_killmails_datas()



# import time

# start = time.time()

# # db 불러오기
# import sqlite3
# con = sqlite3.connect('./everef_killmails_data.db')
# cur = con.cursor()


# # cur.execute(f"SELECT * FROM EverefKillmails WHERE EverefKillmails.CharacterID = {2115063295}")

# # like: 문자열 비교
# cur.execute(f"SELECT * FROM EverefKillmails WHERE EverefKillmails.AttakersIDs like '%{2115063295}%'")

# # result = cur.fetchall()
# result = cur.fetchmany(30)
# print(result)
# print(len(result))
# end = time.time()
# print(end - start)



import sqlite3
import datetime
class SqliteData():
    def __init__(self):
        self.con = sqlite3.connect(r'C:\python\zka_web\everef_killmails_data.db')
        self.cur = self.con.cursor()

    def get_killmail_from_CharacterID(self, id: int, week: int, num: int):
        time = (datetime.datetime.now() - datetime.timedelta(weeks=week)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if num == 0:
            # data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE AttakersIDs like '%{id}%' AND KillTime < '2023-10-01T00:00:47Z'").fetchall()
            data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE CharacterID = {id} AND KillTime > '{time}'").fetchall()
        else:
            data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE CharacterID = {id} AND KillTime > '{time}'").fetchmany(num)
        return data
        # data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE CharacterID = {id}").fetchall()
        # return data

    def get_killmail_from_KillmailID(self, id: int, week: int, num: int):
        time = (datetime.datetime.now() - datetime.timedelta(weeks=week)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if num == 0:
            # data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE AttakersIDs like '%{id}%' AND KillTime < '2023-10-01T00:00:47Z'").fetchall()
            data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE KillmailID = {id} AND KillTime > '{time}'").fetchall()
        else:
            data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE KillmailID = {id} AND KillTime > '{time}'").fetchmany(num)
        return data
        # data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE KillmailID = {id}").fetchall()
        # return data

    def get_attakers_from_CharacterID(self, id: int, week: int, num: int):
        time = (datetime.datetime.now() - datetime.timedelta(weeks=week)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if num == 0:
            # data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE AttakersIDs like '%{id}%' AND KillTime < '2023-10-01T00:00:47Z'").fetchall()
            data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE AttakersIDs like '%{id}%' AND KillTime > '{time}'").fetchall()
        else:
            data = self.cur.execute(f"SELECT * FROM EverefKillmails WHERE AttakersIDs like '%{id}%' AND KillTime > '{time}'").fetchmany(num)
        return data

    def check_CharacterID(self, ID: int):
        return self.cur.execute(f"SELECT EXISTS (SELECT * FROM EverefKillmails WHERE CharacterID = {ID});").fetchall()[0][0]

# result = SqliteData().get_attakers_from_CharacterID(2116016649)
# print(result)
# print(len(result))
# for i in result:
#     print(f"{i[0]} / {i[5]}")

# result = SqliteData().get_killmail_from_CharacterID(2116016649, 10)
# print(result)

# print(SqliteData().check_CharacterID(2116000016649))