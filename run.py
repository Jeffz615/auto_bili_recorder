from Live import BiliBiliLive
import os
import requests
import time
import config
import utils
import re
import multiprocessing
import urllib3
from bypy import ByPy
urllib3.disable_warnings()


class BiliBiliLiveRecorder(BiliBiliLive):
    def __init__(self, room_id, queue, onlyAudio=False, qn=10000,  check_interval=1 * 60):
        super().__init__(room_id)
        self.inform = utils.inform
        self.print = utils.print_log
        self.check_interval = check_interval
        self.onlyAudio = onlyAudio
        self.qn = qn
        self.queue = queue

    def check(self, interval):
        while True:
            try:
                room_info = self.get_room_info()
                if room_info['status']:
                    self.inform(room_id=self.room_id,
                                desp=room_info['roomname'])
                    self.print(self.room_id, room_info['roomname'])
                    break
            except Exception as e:
                self.print(self.room_id, 'Error:' + str(e))
            time.sleep(interval)
        return self.get_live_urls(onlyAudio=self.onlyAudio, qn=self.qn)

    def record(self, record_urls, output_filename):
        self.print(self.room_id, '√ 正在录制...' + self.room_id)
        headers = dict()
        headers['Accept-Encoding'] = 'identity'
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
        for record_url in record_urls:
            try:
                flag = False
                headers['Referer'] = re.findall(
                    r'(http://.*\/).*\.flv',
                    record_url)[0]
                self.print(self.room_id, record_url)
                resp = requests.get(record_url, stream=True, headers=headers)
                with open(output_filename, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024):
                        f.write(chunk) if chunk else None
                        flag = True
                if flag and os.path.getsize(output_filename)>256:
                    self.queue.put(output_filename)
                else:
                    os.remove(output_filename)
                break
            except Exception as e:
                self.print(self.room_id, 'Error while recording:' + str(e))
                continue

    def run(self):
        while True:
            try:
                self.print(self.room_id, '等待开播')
                urls = self.check(interval=self.check_interval)
                filename = utils.generate_filename(self.room_id)
                self.record(urls, filename)
                self.print(self.room_id, '录制完成' + filename)
            except Exception as e:
                self.print(self.room_id,
                           'Error while checking or recording:' + str(e))


class autoUpload():
    def __init__(self, queue, delAfterUpload):
        self.queue = queue
        self.delAfterUpload = delAfterUpload

    def uploadApi(self, uploadFilepath):
        uploadFilename = os.path.basename(
            uploadFilepath)
        uploadFilenameSplit = os.path.basename(
            uploadFilepath).rstrip('.flv').split('_')
        roomid = uploadFilenameSplit[-1]
        recordDate = uploadFilenameSplit[0]
        bp = ByPy(verify=False)
        if bp.upload(uploadFilepath, f'{roomid}/{recordDate}/{uploadFilename}')!=0:
            raise Exception('upload fail.')

    def run(self):
        while True:
            try:
                utils.print_log('uploader', '等待录制完成')
                while self.queue.empty():
                    time.sleep(60)
                uploadFilepath = self.queue.get(True)
                fsize = os.path.getsize(uploadFilepath)
                utils.print_log(
                    'uploader', f'获取录制文件 {uploadFilepath} ({fsize})')
                if fsize > 256:
                    utils.print_log('uploader', '文件上传中')
                    self.uploadApi(uploadFilepath)
                    utils.print_log('uploader', '文件上传完成')
                else:
                    os.remove(uploadFilepath)
                if self.delAfterUpload:
                    os.remove(uploadFilepath)
            except Exception as e:
                utils.print_log('uploader', 'Error while upload:' + str(e))


if __name__ == '__main__':
    input_id = config.rooms
    onlyAudio = config.onlyAudio
    qn = config.qn
    delAfterUpload = config.delAfterUpload
    mp = multiprocessing.Process
    q = multiprocessing.Queue()
    tasks = [
        mp(target=BiliBiliLiveRecorder(str(room_id), queue=q, onlyAudio=onlyAudio, qn=qn).run) for room_id in input_id
    ]
    tasks.append(mp(target=autoUpload(
        queue=q, delAfterUpload=delAfterUpload).run))
    for i in tasks:
        i.start()
    for i in tasks:
        i.join()
