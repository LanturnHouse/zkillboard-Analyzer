import requests
import json
import os
import pickle
import time
import asyncio
import aiohttp
import datetime
import urllib3
from time import sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

main_path = os.path.abspath(__file__)
main_path = main_path.replace("\\","/")
main_path = f"{main_path}./../"

typeIDs_path = main_path + "eveDatas/typeIDs.pickle"

aio_timeout = aiohttp.ClientTimeout(total=5)

class zKillBoard():

    def __init__(self, character_id):
        base_url = "https://zkillboard.com/api/stats/characterID/"
        self.character_id = str(character_id)
        self.response: dict = requests.get(base_url + self.character_id + "/", headers={"User-Agent": "lan._.turn(Discord)"}, verify=False).json()
        self.loc_kills = {}
        self.most_use = {}

    def get_info(self):
        info = {}
        info["character_id"] = self.response["topLists"][0]["values"][0]["characterID"]
        info["character_name"] = self.response["topLists"][0]["values"][0]["characterName"]
        info["corp_id"] = self.response["topLists"][1]["values"][0]["corporationID"]
        info["corp_name"] = self.response["topLists"][1]["values"][0]["corporationName"]
        info["corp_ticker"] = self.response["topLists"][1]["values"][0]["cticker"]
        info["alliance_id"] = self.response["topLists"][2]["values"][0]["allianceID"]
        info["alliance_name"] = self.response["topLists"][2]["values"][0]["allianceName"]
        info["alliance_ticker"] = self.response["topLists"][2]["values"][0]["aticker"]
        return info
    
    def get_week_active_pvp(self):
        return self.response["activepvp"]

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
    
    def get_loc_kills(self):
        self.loc_kills["high"] = self.response["labels"]["loc:highsec"].get("shipsLost", 0) + self.response["labels"]["loc:highsec"].get("shipsDestroyed", 0)
        self.loc_kills["low"] = self.response["labels"]["loc:lowsec"].get("shipsLost", 0) + self.response["labels"]["loc:lowsec"].get("shipsDestroyed", 0)
        self.loc_kills["null"] = self.response["labels"]["loc:nullsec"].get("shipsLost", 0) + self.response["labels"]["loc:nullsec"].get("shipsDestroyed", 0)
        self.loc_kills["hole"] = self.response["labels"]["loc:w-space"].get("shipsLost", 0) + self.response["labels"]["loc:w-space"].get("shipsDestroyed", 0)
        return self.loc_kills

    def get_most_use(self):
        for i in range(0, len(self.response["topLists"][3]["values"])):
            self.most_use[f'{self.response["topLists"][3]["values"][i]["shipTypeID"]}'] = {"kill_count": self.response["topLists"][3]["values"][i]["kills"], "ship_name": self.response["topLists"][3]["values"][i]["shipName"]}
        return self.most_use

    def get_w_loss_mail(self):
        # url = f"https://zkillboard.com/api/w-space/losses/characterID/{self.character_id}/"
        url = f"https://zkillboard.com/api/losses/characterID/{self.character_id}/"
        return requests.get(url, headers={"User-Agent": "lan._.turn(Discord)"}, verify=False).json()

    def get_w_kill_mail(self):
        url = f'https://zkillboard.com/api/w-space/kills/characterID/{self.response["topLists"][0]["values"][0]["characterID"]}/'
        res = requests.get(url, headers={"User-Agent": "lan._.turn(Discord)"}, verify=False).json()
        if len(res) > 100:
            res = res[:100]
        return res
    
    def get_danger_ratio(self):
        return self.response["dangerRatio"]


class Esi():

    def __init__(self):
        with open(typeIDs_path, 'rb') as f:
            self.typeIDs = pickle.load(f)
        # self.zk_loss_mails = {}
        # self.zk_kill_mails = {}
        

        self.fittings = {}

        self.loss_mails = []
        self.corps = {}

        # print(f"zk killmails{self.get_corp_kill_mails()}")
        # self.get_loss_mails()

    async def get_fittings_from_killmails(self, kill_mail):
        items = kill_mail["victim"]["items"]
        fitting = {
                    "info": {},
                    "fitting": {
                        "high": [],
                        "med": [],
                        "low": [],
                        "rig": [],
                        "drone": [],
                        "booster": [],
                        "implant": [],
                        "shipHangar": [],
                        }
                    }
        fitting["info"]["ship_name"] = self.typeIDs[kill_mail["victim"]["ship_type_id"]]["name"]["en"]
        fitting["info"]["kill_time"] = kill_mail["killmail_time"]
        session  = aiohttp.ClientSession(timeout=aio_timeout)
        # system = requests.get(f"https://esi.evetech.net/latest/universe/systems/{kill_mail['solar_system_id']}/?datasource=tranquility&language=en", headers={"User-Agent": "lan..turn(Discord)"}).json()
        async with session.get(f"https://esi.evetech.net/latest/universe/systems/{kill_mail['solar_system_id']}/?datasource=tranquility&language=en", headers={"User-Agent": "lan..turn(Discord)"}) as response:
            system = await response.json()
        await session.close()
        # print(system)
        fitting["info"]["system"] = system.get("name")
        fitting["info"]["system_security"] = round(system.get("security_status"), 1)

        for item in items:
            if 11 <= item["flag"] and 18 >= item["flag"]:
                fitting["fitting"]["low"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if 19 <= item["flag"] and 26 >= item["flag"]:
                fitting["fitting"]["med"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if 27 <= item["flag"] and 34 >= item["flag"]:
                fitting["fitting"]["high"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if 92 <= item["flag"] and 98 >= item["flag"]:
                fitting["fitting"]["rig"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if item["flag"] == 87:
                fitting["fitting"]["drone"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if item["flag"] == 88:
                fitting["fitting"]["booster"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if item["flag"] == 89:
                fitting["fitting"]["implant"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if item["flag"] == 90:
                fitting["fitting"]["shipHangar"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
            if item["flag"] == 88:
                fitting["fitting"]["booster"].append(self.typeIDs[item["item_type_id"]]["name"]["en"])
        self.fittings[kill_mail["killmail_id"]] = fitting

    def print_fitting(self):
        for kill_id in self.fittings:
            print(f"\n\n━━━ info ━━━")
            print(f"ship_name: {self.fittings[kill_id]['info']['ship_name']}")
            print(f"kill_id: {kill_id}")
            print(f"kill_time: {self.fittings[kill_id]['info']['kill_time']}")
            for item in self.fittings[kill_id]:
                if self.fittings[kill_id]["fitting"][item] != []:
                    print(f"\n━━━ {item} ━━━")
                    for item in self.fittings[kill_id][item]:
                        print(item)
                


    def get_tasks(self, session, zk_mails: dict):
        tasks = []
        for zk_mail in zk_mails:
            tasks.append(session.get(f"https://esi.evetech.net/latest/killmails/{zk_mail['killmail_id']}/{zk_mail['zkb']['hash']}/?datasource=tranquility", headers={"User-Agent": "lan._.turn(Discord)"}))
        return tasks
    
    async def run_tasks(self, most_use, zk_loss_mails):
        start = time.time()
        session = aiohttp.ClientSession(timeout=aio_timeout)
        tasks = self.get_tasks(session, zk_loss_mails)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            res = await response.json()
            # 이 부분에서 가장 자주 쓰는 함선을 거름
            if str(res["victim"]["ship_type_id"]) in list(most_use.keys()):
                # res["killmail_time"] = datetime.datetime.strptime(res["killmail_time"], "%Y-%m-%dT%H:%M:%SZ")
                res["killmail_time"] = str(res["killmail_time"]).replace("T", " ").replace("Z", "")
                self.loss_mails.append(res)
        await session.close()
        print(time.time() - start)
    def get_most_use_loss_mails(self, most_use, zk_loss_mails):
        asyncio.run(self.run_tasks(most_use, zk_loss_mails))
        return self.loss_mails


    async def _run_tasks(self, zk_kill_mails, main_corp_id):
        start = time.time()
        session = aiohttp.ClientSession(timeout=aio_timeout)
        tasks = self.get_tasks(session, zk_kill_mails)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            res = await response.json()
            for attackers in res["attackers"]:
                # print(attackers)corporation_id
                if "corporation_id" in attackers:
                    if attackers["corporation_id"] != main_corp_id:
                        if attackers["corporation_id"] not in self.corps:
                            self.corps[attackers["corporation_id"]] = 1
                        else:
                            self.corps[attackers["corporation_id"]] += 1
        await session.close()
        print(time.time() - start)
    def get_corp_kill_mails(self, zk_kill_mails, main_corp_id):
        asyncio.run(self._run_tasks(zk_kill_mails, main_corp_id))
        return self.corps

    def get_info_from_name(self, name: str):
        info = requests.post("https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en", headers={"User-Agent": "lan..turn(Discord)"}, json=[name]).json()
        # print(info)
        return info
    
    def get_character_portrait(self, id, size = 256):
        portrait = requests.get(f"https://esi.evetech.net/latest/characters/{id}/portrait/?datasource=tranquility", headers={"User-Agent": "lan..turn(Discord)"}).json()
        # print(portrait)
        return portrait[f"px{size}x{size}"]
    


    def _get_tasks(self, session, corp_ids: dict):
        tasks = []
        for corp_id in corp_ids:
            tasks.append(session.get(f"https://esi.evetech.net/latest/corporations/{corp_id}/?datasource=tranquility", headers={"User-Agent": "lan._.turn(Discord)"}))
        return tasks
    async def __run_tasks(self, corp_ids):
        start = time.time()
        corps = {}
        session = aiohttp.ClientSession(timeout=aio_timeout)
        tasks = self._get_tasks(session, corp_ids)
        responses = await asyncio.gather(*tasks)
        for response, id in zip(responses, corp_ids):
            res = await response.json()
            corps[id] = res["name"]
            # print(corps[id])
            # corps.append(res)
            # print(res["name"])
        await session.close()
        print(time.time() - start)
        return corps
    def get_corp_from_ids(self, corp_ids):
        return asyncio.run(self.__run_tasks(corp_ids))
    
        
    # def get_corp_from_id(self, id):
    #     corp = requests.get(f"https://esi.evetech.net/latest/corporations/{id}/?datasource=tranquility", headers={"User-Agent": "lan..turn(Discord)"}).json()
    #     # print(portrait)
    #     return corp



_start = time.time()

user_id = 2115063295

zk = zKillBoard(user_id)
# print(zk.get_danger_ratio())
most_use = zk.get_most_use()
loss_mails = zk.get_w_loss_mail()
kill_mails = zk.get_w_kill_mail()
# print(loss_mails)
# print(kill_mails)
zk_time = time.time() - _start

start = time.time()
esi = Esi()
esi.get_corp_from_ids(esi.get_corp_kill_mails(kill_mails, 0))
loss_mails = esi.get_most_use_loss_mails(most_use, loss_mails)
esi_time = time.time() - start

start = time.time()

async def process_async():
    start = time.time()
    fts = [asyncio.ensure_future(esi.get_fittings_from_killmails(task)) for task in loss_mails]
    print("gather")
    await asyncio.gather(*fts)
    end = time.time()
    print(f'>>> 비동기 처리 총 소요 시간: {end - start}')
asyncio.run(process_async())
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(process_async())
# loop.close
# print(esi.get_fittings_from_killmails(esi.get_most_use_loss_mails(most_use, loss_mails)))
fitting_time = time.time() - start

print(f"zk: {zk_time}")
print(f"esi: {esi_time}")
print(f"fitting_time: {fitting_time}")
print(f"total time: {time.time() - _start}")

# esi.print_fitting()


# print(len(esi.fittings))
# print(esi.get_corp_kill_mails(kill_mails))



# print(time.time() - start)

# active_time = 18
# active_time = active_time + 9 if active_time + 9 < 25 else active_time - 15
# print(active_time)