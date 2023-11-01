from django.shortcuts import render
from .forms import CharacterNameForm
import datetime
import zka.analyzer as analyzer
import time

def index(request):
    return render(request, 'zka/base.html')

def analyze(request):
    start = time.time()
    form = CharacterNameForm(request.GET)
    print(request.GET)
    if form.is_valid():
        a = analyzer.Analyze()
        # 2.4초
        esi_info = a.get_info_from_name(request.GET["character_name"].strip())
        try:
            character_id = esi_info["characters"][0]["id"]
            # if a.check_CharacterID(character_id) == 0:
            #     raise
        except Exception as e:
            content = {"warning_message": "해당 캐릭터를 찾을 수 없습니다."}
            return render(request, 'zka/warning.html', content)
        
        # print(time.time() - start)
        start = time.time()
        # 1초
        a.set_zk(character_id)
        # print(time.time() - start)
        # start = time.time()
        # 3초
        a.get_attakers(character_id, 2)
        # print(time.time() - start)

        # a.get_weapon_id()
        # a.get_active_loc_id()

        # zk = analyzer.zKillBoard(character_id)

        # start = time.time()
        most_use = a.get_most_use()
        # print(time.time() - start)

        # start = time.time()
        danger_ratio = a.get_danger_ratio()
        # print(time.time() - start)

    
        # start = time.time()
        ids = a.get_ids()
        # print(time.time() - start)
        # main_loc = max(zk.get_loc_kills(),key=zk.get_loc_kills().get)

        # start = time.time()
        a.get_killmails(character_id, 100)
        # print(time.time() - start)
        # start = time.time()
        a.get_fittings_from_killmails()
        # print(time.time() - start)
        # start = time.time()
        a.get_friend()
        # print(time.time() - start)
        # start = time.time()
        a.trans_datas()
        # print(time.time() - start)
        # start = time.time()
        # 1초
        main_loc = a.get_main_loc()
        # print(time.time() - start)

        friends_ = a.friend_dict

        active_time = a.get_week_activity().index(max(a.get_week_activity())) 
        active_time = active_time + 9 if active_time + 9 < 25 else active_time - 15
        if active_time < 10:
            active_time = "0" + str(active_time)

        if a.info["corporations"]["name"] in friends_:
            del friends_[a.info["corporations"]["name"]]
        # friends = dict(sorted(friends.items(), reverse=True, key=lambda item: item[1])[:5])
        f = {}
        for friend in friends_:
            f[friend] = friends_[friend]["count"]
        f = dict(sorted(f.items(), reverse=True, key=lambda item: item[1])[:5])
        friends = {}
        for friend in f:
            friends[friend] = {"count": f[friend], "id": friends_[friend]["id"]}

        most_use = dict(sorted(most_use.items(), reverse=True, key=lambda item: item[1])[:5])

        lossmails = {}
        for data in a.killmails_data:
            if data[3] in most_use.keys():
                # print(data)
                lossmails[data[0]] = {"fitting": data[6],
                                        "info": {
                                            "ship_name": data[3],
                                            "system": data[4]["name"],
                                            "system_security": data[4]["sec"],
                                            # "kill_time": data[5]}}
                                            "kill_time": (datetime.datetime.strptime(data[5], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")}}

        urls = {
            "character_portrait": f"https://images.evetech.net/characters/{character_id}/portrait?tenant=tranquility&size=256",
            "character_zkillboard": f"https://zkillboard.com/character/{ids['characters']}/",
            "corp_zkillboard": f"https://zkillboard.com/corporation/{ids['corporations']}/",
            "alliance_zkillboard": f"https://zkillboard.com/alliance/{ids['alliances']}/"
        }

        info = {
            "danger_ratio": danger_ratio,
            "snuggly_ratio": 100 - danger_ratio,
            "friends": friends,
            "active_time": active_time,
            "most_use": most_use,
            "main_loc": main_loc,
            "character_name": a.info["characters"]["name"],
            "corp_name": a.info["corporations"]["name"],
            "alliance_name": a.info["alliances"]["name"],
            "corp_ticker": a.info["corporations"]["ticker"],
            "alliance_ticker": a.info["alliances"].get("ticker"),
            "time": round(time.time() - start, 3)
        }

        print(time.time() - start)
        content = {"lossmails": lossmails, "urls": urls, "info": info}
        return render(request, 'zka/result.html', content)
    
    else:
        content = {"warning_message": "캐릭터 이름을 입력해주세요!"}
        return render(request, 'zka/warning.html', content)