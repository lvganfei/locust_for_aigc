import datetime
import json
import os
import time
from queue import Queue
import json
import os

import numpy as np
import requests
import statistics
from gevent._semaphore import Semaphore
from locust import task, between, HttpUser, events

# 初始化队列并填充数据
data_queue = Queue()



fail_list = []
data_list = []
total_time_list = []
start_time = ""
end_time = ""

def logger(info):
    print(f'{datetime.datetime.now()} {info}')


def message(content):
    try:

        ms = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        print(f"----- 推送消息 ----- {ms}")
        requests.post('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=92432185-6335-4759-a460-ab3afcae7e5d',
                      data=json.dumps(ms))
    except Exception as e:
        print("send Message fail :{}".format(e))


def data_statistics(data, title=''):
    # 转换为numpy数组
    test_data = sorted(data)
    data_np = np.array(test_data)
    try:
        # 计算平均值
        mean = int(np.mean(data_np) * 1000) 
    except:
        mean = 0
    try:
        # 计算中位数
        median = int(statistics.median(test_data) * 1000)
    except:
        median = 0
    try:
        # 计算最大值
        max_val = int(np.max(data_np) * 1000)
    except:
        max_val = 0
    try:
        # 计算最小值
        min_val = int(np.min(data_np) * 1000)
    except:
        min_val = 0
    try:
        # 计算中位数
        percentile_90 = int(np.percentile(data_np, 90) * 1000)
    except:
        percentile_90 = 0
    try:
        percentile_95 = int(np.percentile(data_np, 95) * 1000)
    except:
        percentile_95 = 0
    try:
        percentile_99 = int(np.percentile(data_np, 99) * 1000)
    except:
        percentile_99 = 0
    try:
        sample_variance = round(np.var(data_np, ddof=1), 2)
        # variance = np.var(data_np)
    except:
        # variance = 0
        sample_variance = 0

    # 如果你想要计算样本方差（除以 n-1 而不是 n），可以传递参数 ddof=1
    print("Sample Variance:", sample_variance)

    total = len(data)
    content = f"""<font color=\"warning\">【{title}】</font>\n><font color=\"warning\"> 请求数：: {total}</font><font color=\"comment\">
    【最小值】{min_val}【平均值】{mean}【中位数】{median}【最大值】{max_val} 【90%】{percentile_90} 【95%】{percentile_95} </font>
    """
    return content

def get_data_time(chunk_str, sec):
    num = 0
    ons = 0
    try:
        if chunk_str:
            data = json.loads(chunk_str[5:])
            if data['status'] == 'success':
                num = int(len(data['response']))
                ons = num / sec
    except Exception as e:
        logger(f"{chunk_str} 获取字节时间失败:{e}")
    return num, ons

def add_que():
    parent_dir = os.getcwd()  # 获取目录
    data_path = os.path.join(parent_dir, 'data/output.json')
    logger(data_path)
    # 打开json 获取参数变量
    with open(data_path, 'r', encoding='utf-8') as f:
        # 解析JSON数据
        data = json.load(f)
        for k, v in data.items():
            data_queue.put(v)


def get_que():
    if data_queue.empty():
        add_que()
    return data_queue.get()


all_locusts_spawned = Semaphore()


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started")
    print(f"Initial user count: {environment.runner.user_count}")

@events.init.add_listener
def on_locust_init(environment, **kw):
    @environment.web_ui.app.route("/added")
    def my_added_page():
        return "Another page"

@events.spawning_complete.add_listener
def on_hatch_complete(**kwargs):
    # 创建钩子方法
    all_locusts_spawned.release()


# 挂在到locust钩子函数（所有的Locust示例产生完成时触发）



# 监听测试结束事件，并计算统计值  
@events.test_stop.add_listener  
def on_test_stop(**kwargs):
    first_time_list = []
    received_time_list = []
    time_per_word_list = []
    first_word_total = 0
    word_total = 0
    send_content = f"<font color=\"warning\">【模拟 {len(first_time_list)} 用户并发测试】</font>\n>"
    for i in data_list:
        num, ons = get_data_time(i[0], i[1])
        if i[2]:
            first_time_list.append(i[1])
            first_word_total += num
        else:
            received_time_list.append(i[1])
        word_total += num
        time_per_word_list.append(ons)

    statistics_dict = {
            '首次响应时间': first_time_list,
            '非首次响应时间': received_time_list,
            '总响应时间': total_time_list
        }

    for k, v in statistics_dict.items():
        content = data_statistics(v, k)
        send_content += content
    received_total = word_total - first_word_total
    first_all_time = sum(first_time_list) 
    received_all_time = sum(received_time_list)
    all_time = first_all_time + received_all_time
    try:
        first_rate = first_word_total / first_all_time
    except:
        first_rate = 0

    send_content = send_content + f""" 
        <font color=\"warning\"> 失败数量: {len(fail_list)}</font>\n
        <font color=\"warning\"> 首次返回总时间: {first_all_time}</font>\n
        <font color=\"warning\"> 非首次返回总时间: {received_all_time}</font>\n
        <font color=\"warning\"> 总返回时间: {all_time}</font>\n
        <font color=\"warning\"> 失败数量: {len(fail_list)}</font>\n
        <font color=\"comment\"> 首次返回字数: {first_word_total}</font>\n
        <font color=\"comment\"> 返回总字数: {word_total}</font>\n
        <font color=\"warning\"> 响应字数/秒(首次): {first_rate}</font>\n
        <font color=\"warning\"> 响应字数/秒(包含首次): {word_total / all_time}</font>\n
        <font color=\"comment\"> 响应字数/秒(不包含首次): {received_total / received_all_time}</font>\n
        """
    message(send_content)

class GPTTest(HttpUser):
    wait_time = between(1, 2)
    # host = "http://10.20.18.5:30257"
    # host = "http://124.223.51.150"
    host = "https://gpt-test.shukun.net"

    def _login(self):
        """
            登录方法 获取header信息 token
            """
        
        token = "whpskyv14t0Fa3ezNN3XyNJBQilFvDyX3oF3y1pLVDzbFGzmQM2xsfXIfuSHeqQBtKvvmAUtUmJvA/MubnaUPRgG0rA2hvpiXuExVpNTHwu7c6RhO1oh+11UdNCjr/9x/pkFLSVw4ZsvF2hdoCmsvvoWrkmSJeDWAdP7zjZZqmGxq8G4uldadA=="
        self.headers = {"content-type": "application/json", "Authorization": token}
        

    def on_start(self):
        """
            任务开始准备工作：只登录一次,获取payload
        """
        logger(f"----- { datetime.datetime.now() }   Test Start -----")
        self._login()

        self.payload = payload = get_que()

        all_locusts_spawned.acquire()

    def on_stop(self):
        logger(self.payload)
        logger(f"----- { datetime.datetime.now() }    Test finish -----")
        

    @task
    def chat(self):
        """
            gpt 聊天
        """
          # 使用队列返回参数
        logger(f"parameter: {self.payload}")
        # 发送流式 POST 请求
        first_return = True
        
        start_time = time.time()
        tmp_time = start_time


        
        # /api/v1/chat
        with self.client.post("/gpt/chat", json=self.payload, headers=self.headers, stream=True) as response:
            # 注意：如果设置了 stream=True，需要处理响应流
            # 检查状态码
            print(response.url)
            if response.status_code == 200:
                # 确保请求成功
                response.raise_for_status()
                # 读取并处理流式响应
                for chunk in response.iter_content(chunk_size=None):
                    # 处理每个数据块
                    now_time = time.time()
                    ts = now_time - tmp_time
                    tmp_time = now_time
                    chunk_str = chunk.decode('utf-8')
                    data_list.append([chunk_str, ts, first_return ])
                    first_return = False
            else:
                print(response.text)
                fail_list.append(response.status_code)
            total_time = (time.time() - start_time) * 1000
            total_time_list.append(total_time)
            logger(f"Response Time:{total_time}")
            time.sleep(180)
            self.environment.runner.quit()