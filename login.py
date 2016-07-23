import requests
import json
import time
import os
import threading


class pan_115:
    session = None
    sign = ''
    uid_time = 0
    uid = ''
    session_id = ''
    tsign = None
    ttime = None
    userid = None
    headers = {}

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }

    def __get_info(self):
        params = {'ct': 'login',
                  'ac': 'qrcode_token',
                  'is_ssl': '1'}
        response_json = self._get_request('http://passport.115.com/', params)
        self.uid = response_json['uid']
        self.uid_time = response_json['time']
        self.sign = response_json['sign']
        url = 'http://msg.115.com/proapi/anonymous.php'
        params = {
            'ac': 'signin',
            'user_id': self.uid,
            'sign': self.sign,
            'time': self.uid_time,
            '_': str(int(time.time() * 1000)),
        }
        response_json = self._get_request(url, params)
        self.session_id = response_json['session_id']

    def _get_request(self, url, params, check_flag=True, json_flag=True):  # check_flag用来判断是否需要做登录验证,下同
        if check_flag:
            pass  # 做一次登录验证
        response = self.session.get(url, params=params, headers=self.headers)
        if not json_flag:
            return response
        response_json = json.loads(response.text)
        return response_json

    def _post_request(self, url, data, check_flag=True, json_flag=True):
        if check_flag:
            pass  # 做一次登录验证
        response_text = self.session.post(url, data=data, headers=self.headers).text
        if not json_flag:
            return response_text
        response_json = json.loads(response_text)
        return response_json

    def get_code(self, path=''):
        self.__get_info()
        params = {'qrfrom': '1', 'uid': self.uid, '_t': str(int(time.time() * 1000)), '_' + str(self.uid_time): ''}
        r = self._get_request('http://dgqrcode.115.com/api/qrcode.php', params=params, json_flag=False)
        f = open(os.path.join(os.getcwd(), path + 'test.jpg'), 'wb')
        f.write(r.content)
        f.close()

    def wait_login(self):
        while True:
            url = 'http://im37.115.com/chat/r'
            params = {
                'VER': '2',
                'c': 'b0',
                's': self.session_id,
                '_t': str(int(time.time() * 1000)),
            }
            r = self._get_request(url, params, json_flag=False)
            try:
                status = json.loads(r.text)[0]['p'][0]['status']
                if status == 1001:
                    print(u"请点击登录")
                elif status == 1002:
                    print(u"登录成功")
                    return
                else:
                    return
            except Exception:
                print(u"超时，请重试")
            time.sleep(5)

    def login(self):  # 触发登陆
        url = 'http://passport.115.com/'
        params = {
            'ct': 'login',
            'ac': 'qrcode',
            'key': self.uid,
            'v': 'android',
            'goto': 'http%3A%2F%2Fwww.J3n5en.com'
        }
        r = self._get_request(url, params, json_flag=False)

    def get_task_sign(self):  # 获取登陆后的sign
        url = 'http://115.com/'
        params = {
            'ct': 'offline',
            'ac': 'space',
            '_': str(int(time.time() * 1000)),
        }
        response_json = self._get_request(url, params)
        self.tsign = response_json['sign']
        self.ttime = response_json['time']

    def keep_login(self):
        while True:
            url = 'http://im37.115.com/chat/r'
            params = {
                'VER': '2',
                'c': 'b0',
                's': self.session_id,
                '_t': str(int(time.time() * 1000)),
            }
            self._get_request(url, params, json_flag=False)
            time.sleep(60)

    def get_user_info(self):
        self.get_task_sign()
        url = 'http://passport.115.com/'
        params = {
            'ct': 'ajax',
            'ac': 'islogin',
            'is_ssl': '1',
            '_' + str(int(time.time() * 1000)): '',
        }
        uinfos = self._get_request(url, params)
        self.userid = uinfos['data']['USER_ID']

        print("====================")
        print(u"用户ID：" + self.userid)
        print(u"用户名：" + uinfos['data']['USER_NAME'])
        if uinfos['data']['IS_VIP'] == 1:
            print("会员")
            url = 'http://115.com/web/lixian/?ct=lixian&ac=task_lists'
            data = {
                'page': '1',
                'uid': self.userid,
                'sign': self.tsign,
                'time': self.ttime,
            }
            response_json = self._post_request(url, data)
            quota = response_json['quota']
            total = response_json['total']
            print(u"本月离线配额：" + str(quota) + u"个，总共" + str(total) + u"个。")
        else:
            print(u"非会员")
        print("===================")

    def add_task(self, task_url):
        url = 'http://115.com/web/lixian/?ct=lixian&ac=add_task_url'
        data = {
            'url': task_url,
            'uid': self.userid,
            'sign': self.tsign,
            'time': self.ttime
        }
        response_json = self._post_request(url, data)
        if (response_json.get('errcode') == 0):
            return [True, '下载成功']
        else:
            return [False, response_json.get('error_msg')]

    def get_task_list(self, page):
        url = 'http://115.com/web/lixian/?ct=lixian&ac=task_lists'
        data = {
            'page': page,
            'uid': self.userid,
            'sign': self.tsign,
            'time': self.ttime
        }
        response_json = self._post_request(url, data)
        print(json.dumps(response_json))
        return response_json.get('tasks')

    def get_files_by_cid(self, cid=0, type=0):  # 4为视频
        url = 'http://web.api.115.com/files'
        params = {
            'aid': 1,
            'cid': cid,
            'o': 'user_ptime',
            'asc': 0,
            'offset': 0,
            'show_dir': 1,
            'limit': 32,
            'code': '',
            'scid': '',
            'snap': 0,
            'natsort': 1,
            'source': '',
            'format': 'json',
            'type': type
        }
        response_json = self._get_request(url, params)
        print(json.dumps(response_json))
        return response_json.get('data')

    def get_download_url(self, pick_code):
        url = 'http://web.api.115.com/files/download'
        params = {
            'pickcode': pick_code,
            '_': str(int(time.time() * 1000))
        }
        response_json = self._get_request(url, params)
        print(json.dumps(response_json))
        return response_json


test = pan_115()
test.get_code()
test.wait_login()
test.login()
threading.Thread(target=test.keep_login)
test.get_user_info()
test.get_task_list(1)
test.get_task_list(2)
test.get_task_list(3)
test.get_files_by_cid()
