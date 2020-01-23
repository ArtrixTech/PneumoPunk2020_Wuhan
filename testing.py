import sys
import time
from threading import Thread

from utils.database import CSGODatabase
from utils.item_class import Weapon

sys.path.append('../')

dbf = CSGODatabase("mysql.artrix.tech", "csgo", "csgo",
                   "CSGO", charset='utf8', port=33066)

# weapons_id = db.get_outdated_weapon_id(37500)
weapons_id = dbf.get_outdated_weapon_id(3600)

print(len(weapons_id))


def start(buff_id, t):
    db = CSGODatabase("mysql.artrix.tech", "csgo", "csgo",
                      "CSGO", charset='utf8', port=33066)
    m = Weapon(buff_id, db, t)
    print('saved:' + m.metadata.item_name)


for i in weapons_id:
    tr = Thread(target=start, args=(i, 3600))
    tr.start()
    time.sleep(0.4)
    # m = Weapon(i, db, 3600)
