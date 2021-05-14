from .BaseLive import BaseLive
import time


class BiliBiliLive(BaseLive):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id
        self.site_name = 'BiliBili'
        self.site_domain = 'live.bilibili.com'

    def get_room_info(self):
        data = {}
        room_info_url = 'https://api.live.bilibili.com/room/v1/Room/get_info'
        user_info_url = 'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room'
        response = self.common_request('GET', room_info_url, {
            'room_id': self.room_id
        }).json()
        if response['msg'] == 'ok':
            data['roomname'] = response['data']['title']
            data['site_name'] = self.site_name
            data['site_domain'] = self.site_domain
            data['status'] = response['data']['live_status'] == 1
        self.room_id = str(response['data']['room_id'])  # 解析完整 room_id
        response = self.common_request('GET', user_info_url, {
            'roomid': self.room_id
        }).json()
        data['hostname'] = response['data']['info']['uname']
        return data

    def get_live_urls(self, onlyAudio=False, qn=10000):
        live_urls = []
        url = 'https://api.live.bilibili.com/xlive/app-room/v2/index/getRoomPlayInfo'
        stream_info = self.common_request('GET', url, {
            'appkey': 'iVGUTjsxvpLeuDCf',
            'build': 6215200,
            'c_locale': 'zh_CN',
            'channel': 'bili',
            'codec': 0,
            'device': 'android',
            'device_name': 'VTR-AL00',
            'dolby': 1,
            'format': '0,2',
            'free_type': 0,
            'http': 1,
            'mask': 0,
            'mobi_app': 'android',
            'network': 'wifi',
            'no_playurl': 0,
            'only_audio': int(onlyAudio),
            'only_video': 0,
            'platform': 'android',
            'play_type': 0,
            'protocol': '0,1',
            'qn': qn,
            'room_id': self.room_id,
            's_locale': 'zh_CN',
            'statistics': '{"appId":1,"platform":3,"version":"6.21.5","abtest":""}',
            'ts': int(time.time())
        }).json()
        live_urls = []
        streams = stream_info['data']['playurl_info']['playurl']['stream']
        for stream in streams:
            for fmat in stream['format']:
                for codec in fmat['codec']:
                    for url_info in codec['url_info']:
                        live_urls.append(
                            url_info['host'] + codec['base_url'] + url_info['extra'])
        return live_urls
