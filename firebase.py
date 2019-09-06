import copy
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import threading

class Firebase:
    def __init__(self):
        self.line_user_data = {}
        self.trash_box_data = {}
        self.thread = None

        self.cred = credentials.Certificate('./procon30-tbm-firebase-adminsdk.json')
        firebase_admin.initialize_app(self.cred,{
            'databaseURL': 'https://procon30-tbm.firebaseio.com/'
        })
        
        self.line_user_ref = db.reference('line/')
        self.trash_box_ref = db.reference('datas/')

        self.get_line_user_data()
        self.get_trash_box_data()

        self.__thread_init()
    
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
            'state': 100
        }

    def update_db(self):
        print(self.line_user_data)
        self.line_user_ref.update(self.line_user_data)
    
    def get_trash_box_data(self):
        self.trash_box_data = copy.deepcopy(self.trash_box_ref.get())
        return self.trash_box_data
    
    def get_line_user_data(self):
        self.line_user_data = copy.deepcopy(self.line_user_ref.get())
        return self.line_user_data
    
    def __run_firebase(self):
        last_time = 0
        while True:
            if time.time() - last_time > 30:
                last_time = time.time()
                self.update_db()
                self.get_line_user_data()
                self.get_trash_box_data()
                print('done')

if __name__ == '__main__':
    firebase = Firebase()
    firebase.insert_user_data('11 45 14 19 19')
    uid = '11 45 14 19 19'
    firebase.line_user_data[uid]['state'] = 10
    while True:
        pass

