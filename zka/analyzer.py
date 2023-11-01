import os
import time
import zka.sqlite_data_editor_thread as sqlite_data_editor_thread
import requests
import asyncio
import aiohttp
import pickle
import yaml

main_path = os.path.abspath(__file__)
main_path = main_path.replace("\\","/")
main_path = f"{main_path}./../"

typeIDs_path = main_path + "eveDatas/typeIDs.pkl"
systems_path = main_path + "eveDatas/systems.pkl"
# iconIDs_path = main_path + "eveDatas/iconIDs.pkl"
iconIDs_path = main_path + "eveDatas/iconIDs.yaml"
charge_id_list = [ 83, 85, 86, 87, 88, 89, 90, 92, 372, 373, 374, 375, 376, 377, 384, 385, 386, 387, 394, 395, 396, 425, 476, 479, 482, 492, 497, 498, 500, 548, 648, 653, 654, 655, 656, 657, 663, 772, 863, 864, 892, 907, 908, 909, 910, 911, 916, 972, 1010, 1019, 1153, 1158, 1400, 1546, 1547, 1548, 1549, 1550, 1551, 1559, 1569, 1677, 1678, 1701, 1702, 1769, 1771, 1772, 1773, 1774, 1976, 1987, 1989, 4061, 4062, 4088, 4186 ]

class zKillBoard():

    def __init__(self, character_id):
        base_url = "https://zkillboard.com/api/stats/characterID/"
        self.character_id = str(character_id)
        self.response: dict = requests.get(base_url + self.character_id + "/", headers={"User-Agent": "('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')"}, verify=False).json()
        self.loc_kills = {}
        self.most_use = {}

    def get_info(self):
        self.info = {}
        # print(self.response["topLists"])
        try:
            self.info["character_id"] = self.response["info"]["id"]
        except:
            self.info["character_id"] = ""
        try:
            self.info["캐릭터"] = self.response["info"]["name"]
        except:
            self.info["캐릭터"] = ""
        try:
            self.info["corp_id"] = self.response["topLists"]["corporation_id"]
        except:
            self.info["corp_id"] = ""
        try:
            self.info["alliance_id"] = self.response["topLists"]["alliance_id"]
        except:
            self.info["alliance_id"] = ""
        return self.info
    
    def get_week_activity(self):
        activity = self.response["activity"]
        _list = []

        for i in range(0,24):
            sum = 0
            for j in range(1,7):
                try:
                    sum += int(activity[f"{j}"][f"{i}"])
                except:
                    pass
            _list.append(int(sum / 7))
        return _list
    
    def get_danger_ratio(self):
        return self.response["dangerRatio"]



class Analyze():
    def __init__(self):
        self.sql = sqlite_data_editor_thread.SqliteData()
        with open(typeIDs_path, 'rb') as f:
            self.typeIDs = pickle.load(f)
        with open(systems_path, 'rb') as f:
            self.systems = pickle.load(f)
        with open(iconIDs_path, encoding='utf-8') as f:
            self.iconIDs = yaml.load(f, Loader=yaml.FullLoader)



    def set_zk(self, character_id):
        base_url = "https://zkillboard.com/api/stats/characterID/"
        self.character_id = str(character_id)
        self.response: dict = requests.get(base_url + self.character_id + "/", headers={"User-Agent": "('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')"}, verify=False).json()

    def get_ids(self):
        self.ids = {}
        # print(self.response["topLists"])
        self.ids["characters"] = self.response["info"]["id"]
        self.ids["corporations"] = self.response["info"]["corporation_id"]
        self.ids["alliances"] = self.response["info"].get("alliance_id", "None")
        return self.ids
    
    def get_week_activity(self):
        activity = self.response["activity"]
        _list = []

        for i in range(0,24):
            sum = 0
            for j in range(1,7):
                try:
                    sum += int(activity[f"{j}"][f"{i}"])
                except:
                    pass
            _list.append(int(sum / 7))
        return _list
    
    def get_danger_ratio(self):
        return self.response["dangerRatio"]
    





    def check_CharacterID(self, ID: int):
        return self.sql.check_CharacterID(ID)

    def get_attakers(self, ID: int, WEEK = 5, NUM = 0):
        self.ID = ID
        self.WEEK = WEEK
        self.NUM = NUM
        self.attakers_data = self.sql.get_attakers_from_CharacterID(self.ID, self.WEEK, self.NUM)
        return self.attakers_data
    
    def get_killmails(self, ID: int, WEEK = 13, NUM = 20):
        datas = self.sql.get_killmail_from_CharacterID(ID, WEEK, NUM)
        self.killmails_data = datas
        return self.killmails_data

    def get_weapon_id(self):
        weapon_list = []
        for data in self.attakers_data:
            attakers = eval(data[8])
            for attaker in attakers:
                if attaker.get("character_id", None) == self.ID:
                    weapon_list.append(self.typeIDs[attaker.get("weapon_type_id")]["name"]["en"])
        return weapon_list
    
    def get_friend(self):
        friend_dict = {}
        for data in self.attakers_data:
            check_list = []
            attakers = eval(data[8])
            # print(attakers)
            for attaker in attakers:
                # friend_list.append(attaker.get("corporation_id"))
                corp_id = attaker.get("corporation_id")
                if corp_id != None:
                    if corp_id not in check_list:
                        if corp_id in friend_dict:
                            friend_dict[corp_id] += 1
                        else:
                            friend_dict[corp_id] = 1
                        check_list.append(corp_id)
        self.friend_dict = friend_dict
        return self.friend_dict
    
    def get_main_loc(self):
        locs = {"Wormhole": 0,
                "Null Sec": 0,
                "Low Sec": 0,
                "High Sec": 0}
        for data in self.attakers_data:
            attakers = eval(data[8])
            # print(attakers)
            for attaker in attakers:
                if attaker.get("character_id") == self.ID:
                    system = self.systems[data[4]]
                    if system.get("id") > 31000000:
                        locs["Wormhole"] += 1
                    elif system.get("sec") < 0:
                        locs["Null Sec"] += 1
                    elif system.get("sec") < 0.5:
                        locs["Low Sec"] += 1
                    else:
                        locs["High Sec"] += 1
        return max(locs, key=locs.get)


    def get_most_use(self):
        most_use_dict = {}
        for data in self.attakers_data:
            attakers = eval(data[8])
            for attaker in attakers:
                if attaker.get("character_id") == self.ID:
                    ship_id = attaker.get("ship_type_id")
                    # print(ship_id)
                    # print(self.typeIDs[ship_id]["name"]["en"])
                    if ship_id != None:
                        ship_name = self.typeIDs[ship_id]["name"]["en"]
                        if ship_name in most_use_dict:
                            most_use_dict[ship_name] += 1
                        else:
                            most_use_dict[ship_name] = 1
        # print(most_use_dict)
        return most_use_dict

    def get_active_loc_id(self):
        # active_loc_dict = {
        #     "high": 0,
        #     "low": 0,
        #     "null": 0,
        #     "w": 0
        # }/
        active_loc_dict = {}
        for data in self.attakers_data:
            if data[4] in active_loc_dict:
                active_loc_dict[data[4]] += 1
            else:
                active_loc_dict[data[4]] = 1
        return active_loc_dict

    def get_fittings_from_killmails(self):
        killmails_data = []
        for data in self.killmails_data:
            killmail_data = list(data)
            items = eval(killmail_data[6])
            fitting = {
                        "HIGH SLOT MODULES": [],
                        "MED SLOT MODULES": [],
                        "LOW SLOT MODULES": [],
                        "RIG SLOT MODULES": [],
                        "DRONE": [],
                        "BOOSTER": [],
                        "IMPLANT": [],
                        "SHIP HANGER": [],
                        }
            
# self.typeIDs[item["item_type_id"]]["iconID"]

            for item in items:

                slot = None
                if 11 <= item["flag"] and 18 >= item["flag"]:
                    if self.typeIDs[item["item_type_id"]]["groupID"] in charge_id_list:
                        continue
                    slot = "LOW SLOT MODULES"
                elif 19 <= item["flag"] and 26 >= item["flag"]:
                    if self.typeIDs[item["item_type_id"]]["groupID"] in charge_id_list:
                        continue
                    slot = "MED SLOT MODULES"
                elif 27 <= item["flag"] and 34 >= item["flag"]:
                    if self.typeIDs[item["item_type_id"]]["groupID"] in charge_id_list:
                        continue
                    slot = "HIGH SLOT MODULES"
                elif 92 <= item["flag"] and 98 >= item["flag"]:
                    if self.typeIDs[item["item_type_id"]]["groupID"] in charge_id_list:
                        continue
                    slot = "RIG SLOT MODULES"
                elif item["flag"] == 87:
                    slot = "DRONE"
                elif item["flag"] == 88:
                    slot = "BOOSTER"
                elif item["flag"] == 89:
                    slot = "IMPLANT"
                elif item["flag"] == 90:
                    slot = "SHIP HANGER"

                if slot:
                    try:
                        icon_path = self.iconIDs[self.typeIDs[item["item_type_id"]]["iconID"]]["iconFile"]
                    except:
                        # icon_path = "items/dust_icon_inst_default.png"
                        icon_path = "items/scv.png"

                    fitting[slot].append({"name": self.typeIDs[item["item_type_id"]]["name"]["en"], "icon_path": icon_path, "meta_group_ID": str(self.typeIDs[item["item_type_id"]].get("metaGroupID"))})
            
            killmail_data[6] = fitting
            killmail_data[3] = self.typeIDs[killmail_data[3]]["name"]["en"]
            killmail_data[4] = self.systems[killmail_data[4]]
            killmails_data.append(killmail_data)
        self.killmails_data = killmails_data
        return self.killmails_data





    # ESI
    def get_info_from_name(self, name: str):
        info = requests.post("https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en", headers={"User-Agent": "lan..turn(Discord)"}, json=[name]).json()
        # print(info)
        return info

    def get_tasks(self, session):
        tasks = []
        for corp_id in self.friend_dict:
            tasks.append(session.get(f"https://esi.evetech.net/latest/corporations/{corp_id}/?datasource=tranquility", headers={"User-Agent": "lan._.turn(Discord)"}))
        # for data in self.killmails_data:
        #     tasks.append(session.get(f"https://esi.evetech.net/latest/universe/systems/{data[4]}/?datasource=tranquility&language=en", headers={"User-Agent": "lan..turn(Discord)"}))
        for data in self.ids:
            if self.ids[data] != "None":
                tasks.append(session.get(f"https://esi.evetech.net/latest/{data}/{self.ids[data]}/?datasource=tranquility", headers={"User-Agent": "lan._.turn(Discord)"}))
        return tasks
    
    async def run_tasks(self):
        start = time.time()
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        tasks = self.get_tasks(session)
        responses = await asyncio.gather(*tasks)
        friend_dict = {}
        self.info = {}
        for response, num in zip(responses, range(len(responses))):
            res = await response.json()
            if num < len(self.friend_dict):
                if len(res.get("name")) > 29:
                    friend_dict[res.get("name")[:26] + "..."] = {"count": self.friend_dict[list(self.friend_dict.keys())[num]], "id": list(self.friend_dict.keys())[num]}
                else:
                    friend_dict[res.get("name")] = {"count": self.friend_dict[list(self.friend_dict.keys())[num]], "id": list(self.friend_dict.keys())[num]}
            # elif num < len(self.friend_dict) + len(self.killmails_data):
            #     self.killmails_data[num - len(self.friend_dict)][4] = {"name": res.get("name"), "sec": round(res.get("security_status"), 1)}
            else:
                self.info[list(self.ids.keys())[num - len(self.friend_dict)]] = {"name": res.get("name"), "ticker": res.get("ticker")}
        await session.close()
        # print(self.info)
        self.friend_dict = friend_dict
        # print(time.time() - start)
    def trans_datas(self):
        asyncio.run(self.run_tasks())




# a = Analyze()

# print(len(a.get_attakers(2115891724, 2)))
# a.get_weapon_id()
# a.get_friend()
# print(a.get_weapon_id())
# print(a.get_most_use())
# a.get_active_loc_id()

# a.get_killmails(2115891724, 10)
# a.get_fittings_from_killmails()

# a.get_info_from_name("HARUSARI")
# # print(a.trans_datas())

# # print(a.killmails_data)