import datetime
from queue import Queue

from locust import task, between, HttpUser

# 初始化队列并填充数据
data_queue = Queue()


def logger(info):
    print(f'{datetime.datetime.now()} {info}')


def add_que():
    data = ['暴力', '攻击', '斗殴', '谋杀', '血腥', '色情', '裸体', '性爱', '色情图片', '成人内容',
            '侮辱', '辱骂', '歧视', '诽谤', '仇恨言论', '犯罪', '诈骗', '盗窃', '贩毒', '洗钱', '政治敏感',
            '政变', '叛乱', '独裁', '颠覆', '恐怖主义', '恐怖袭击', '炸弹', '自杀式袭击', '极端主义', '恶意软件',
            '病毒', '木马', '勒索软件', '黑客攻击', '非法活动', '走私', '偷渡', '非法交易', '赌博', '虚假广告',
            '虚假宣传', '夸大其词', '误导消费者', '违禁品', '毒品', '违禁药物', '管制刀具', '野生动物', '公户政治类',
            '国家领导人', '政治体制', '革命', '反动', '宗教类', '宗教领袖', '宗教仪式', '邪教', '拜神', '暴力与犯罪类',
            '枪支', '毒品', '爆炸', '绑架', '色情与低俗类', '色情', '裸体', '性器官', '低俗内容', '虚假与误导类',
            '最佳', '药品', '性别', '测试', '最强', '无副作用', '夸大宣传', '侮辱与诽谤类', '歧视', '辱骂', '偏见',
            '诽谤法律与道德类', '非法', '走私', '欺诈', '盗窃'
            ]
    for k in data:
        data_queue.put(k)


def get_que():
    if data_queue.empty():
        add_que()
    return data_queue.get()


class GPTTaskSet(HttpUser):
    wait_time = between(1, 2)
    host = "http://10.10.100.11"

    def _login(self):
        """
            登录方法 获取header信息 token
            """
        self.header = {
            "Content-Type": "application/json",
            "Authorization": "whpskyv14t0Fa3ezNN3XyNJBQilFvDyX3oF3y1pLVDxNBWmkNDQJbfXIfuSHeqQBtKvvmAUtUmJb7HVB4dRa2h3+JsAmXs8f/eJLT9SHNEYkBS+uSeAoRuMO2HuD2DIeicfe9EysKCAkwK+81Wk4vNRSy9yd1GdN3yLTJmpAqayIBvDT74v5rg02Qk9fkxPh+phkM835A64epZT+JpzhCQ=="
        }
        return self.header

    def on_start(self):
        """
            任务开始准备工作：只登录一次
            """
        logger("----- Test Start -----")
        self._login()

    def on_stop(self):
        logger("----- Test over -----")

    @task(3)
    def chat(self):
        """
            gpt 聊天
        """
        payload = {"text": get_que()}  # 使用队列返回参数
        logger(f"parameter: {payload}")
        with self.client.post("/gpt/safe_detect", json=payload, headers=self.header) as response:
            # 检查状态码
            if response.status_code == 200:
                print(response.text)
            else:
                print('fail')
