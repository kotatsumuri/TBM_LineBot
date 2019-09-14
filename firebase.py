import copy
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import threading
from pyproj import Geod

class Firebase:
    def __init__(self):
        self.line_user_data = {}
        self.trash_box_data = {}
        self.thread = None
        self.geod = Geod(ellps = 'WGS84')

        self.cred = credentials.Certificate('./procon30-tbm-firebase-adminsdk.json')
        firebase_admin.initialize_app(self.cred,{
            'databaseURL': 'https://procon30-tbm.firebaseio.com/'
        })
        
        self.line_user_ref = db.reference('line/')
        self.trash_box_ref = db.reference('datas/')

        self.get_line_user_data()
        self.get_trash_box_data()

        self.__thread_init()

    def __del__(self):
        self.update_db()
    
    def __thread_init(self):
        self.thread = threading.Thread(target = self.__run_firebase)
        self.thread.daemon = True
        self.thread.start()

    def insert_user_data(self, uid):
        self.line_user_data[uid] = {
            'location': {
                'lat': 0,
                'lng': 0
            },
            'state': 100,
            'timestamp': 0
        }

    def update_db(self):
        self.line_user_ref.update(self.line_user_data)
    
    def get_trash_box_data(self):
        self.trash_box_data = copy.deepcopy(self.trash_box_ref.get())
        return self.trash_box_data
    
    def get_things_list(self):
        return self.trash_box_data['thingsList']
    
    def get_data_list(self):
        return self.trash_box_data['dataList']
    
    def get_trash_box_keys(self):
        return self.get_data_list().keys()
    
    def get_line_user_data(self):
        self.line_user_data = copy.deepcopy(self.line_user_ref.get())
        return self.line_user_data
    
    def get_much_thing_keys(self, thing):
        keys = []
        for key in self.get_trash_box_keys():
            if thing in self.get_data_list()[key]['things']:
                keys.append(key)
        return keys

    def get_nearest_trash_box(self, uid, keys):
        nearest_distance = 1145141919810114514
        nearest_key = '0'

        for key in keys:
            if self.get_data_list()[key]['space'] >= 90:
                continue
            
            distance = self.calc_distance(uid, key)
            if nearest_distance >= distance:
                nearest_distance = distance
                nearest_key = key
            
        return nearest_key, nearest_distance

    def set_state(self, uid, state):
        self.line_user_data[uid]['state'] = state
    
    def set_location(self, uid, lat, lng):
        self.line_user_data[uid]['location'] = {
            'lat': lat,
            'lng': lng
        }

    def calc_distance(self, uid, key):
        distance = self.geod.inv(self.line_user_data[uid]['location']['lng'],
                              self.line_user_data[uid]['location']['lat'],
                              self.get_data_list()[key]['position']['lng'],
                              self.get_data_list()[key]['position']['lat'])[2]
        return int(round(distance, -(len(str(int(distance))) - 2)))

        return self.trash_box_data
    
    def __run_firebase(self):
        last_time = 0
        while True:
            if time.time() - last_time > 60:
                last_time = time.time()
                self.update_db()
                self.get_line_user_data()
                self.get_trash_box_data()

if __name__ == '__main__':
    firebase = Firebase()
    firebase.insert_user_data('11 45 14 19 19')
    uid = '11 45 14 19 19'
    firebase.line_user_data[uid]['state'] = 10
    while True:
        pass

