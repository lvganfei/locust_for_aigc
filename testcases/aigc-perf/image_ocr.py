from locust import task, between, User, events, SequentialTaskSet
from locust.contrib.fasthttp import FastHttpUser, FastResponse
from gevent._semaphore import Semaphore

from queue import Queue
import time
import datetime
import os  
import base64
import json  

  
def image_to_base64(image_path):  
    """  
    将图片文件转换为Base64编码的字符串  
    """  
    with open(image_path, "rb") as image_file:  
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')  
    return encoded_string 


  
def init_data():  
    """  
    遍历指定文件夹中的所有图片，将它们转换为Base64编码  
    """ 
    data = []
    # parent_dir = os.path.dirname(os.getcwd()) 
    parent_dir = os.getcwd()
    json_path = os.path.join(parent_dir, 'data/config.json')
    folder_path = os.path.join(parent_dir, 'data/images/')
    # 打开JSON文件  
    with open(json_path, 'r') as f:  
        # 读取并解析JSON数据  
        config_data = json.load(f)  
    
    print(folder_path)
    for root, dirs, files in os.walk(folder_path):  
        for file in files:  
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):  
                image_path = os.path.join(root, file)  
                base64_str = image_to_base64(image_path)  
                data.append(base64_str)
    return data, config_data['max_loops'], config_data['sleep_time']
  

# 创建集合点，当locust实例产生完成时触发（即用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
# 初始化队列并填充数据
data_queue = Queue()
image_data, max_loops, sleep_time = init_data()

def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()  # 创建钩子方法


events.spawning_complete.add_listener(on_hatch_complete)  # 挂载到locust钩子函数（所有的Locust实例产生完成时触发）

def logger(info):
    print(f'{datetime.datetime.now()} {info}')


def add_que():
    for k in image_data:
        data_queue.put(k)

def get_que():
    if data_queue.empty():
        add_que()
    return data_queue.get()


class GPTTaskSet(FastHttpUser):
    wait_time = between(1, 2)
    # host = "http://api-gpt.shukun.net:80"
    host = "http://124.223.51.150"
    counter = 0 
    max_loops = max_loops

    def _login(self):
        """
            登录方法 获取header信息 token
            """
        self.headers = {
            "Authorization": "whpskyv14t0Fa3ezNN3XyNJBQilFvDyX3oF3y1pLVDxNBWmkNDQJbfXIfuSHeqQBtKvvmAUtUmJb7HVB4dRa2h3+JsAmXs8f/eJLT9SHNEYkBS+uSeAoRuMO2HuD2DIeicfe9EysKCAkwK+81Wk4vNRSy9yd1GdN3yLTJmpAqayIBvDT74v5rg02Qk9fkxPh+phkM835A64epZT+JpzhCQ=="
            }

    def on_start(self):
        """
            任务开始准备工作：只登录一次
            """
        print("----- Test Start -----")
        self._login()

    def on_stop(self):
        print("----- Test over -----")

    @task  # 设置权重值
    def image_text_extraction(self):
        """
        获取报告信息
        """
        payload = {
            "image": str(get_que())
        }  # 使用队列返回参数
        # logger(f"------------------------- -------------------------  parameter  ------------------------- -------------------------")
        # logger(payload)
        # logger(f"-------------------------  parameter over  ------------------------- ")
        
        logger(f"counter:{GPTTaskSet.counter}  max_loops:{GPTTaskSet.max_loops} ")
        if GPTTaskSet.counter < GPTTaskSet.max_loops: 
            GPTTaskSet.counter += 1
            all_locusts_spawned.wait()
            # /ocr/api/v1/image_text_extraction
            response = self.client.post("/gpt/image_text_extraction", json=payload, headers=self.headers)
            if response.status_code == 200:
                data = response.json()

                # print(data)
                # assert 'text' in data.keys() 
                assert 'text' in data['data'].keys() 
            else:
                print(f"error status_code:{response.status_code} content:{response.text}")
        
        

class GptUser(User):
    """
        参数化 数据
    """
    min_wait = 1000
    max_wait = 3000
    tasks = [GPTTaskSet]  # 指向任务集合
    host = "http://124.223.51.150" 
