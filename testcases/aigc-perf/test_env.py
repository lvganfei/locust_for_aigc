import time
import random
import pandas as pd
from locust import HttpUser, task, between
class TestUser(HttpUser):
    #每个任务执行完等待时间,1-5s
    wait_time = between(1, 5)
    #任务函数,通过task装饰器调用,括号里的3代表权重,他也被调用的概率是3,不是固定3次的意思,
    @task(3)
    def chat(self):
        headers = {"content-type": "application/json", "Authorization": self.token}
        data = {
            "task_history":[],
            "query": self.query,
            "query_type":"1",
            "model_id": self.model_id,
            "patient_id": self.patientid,
            "model": self.model
            }
        
        print(data)
        with self.client.post('/gpt/chat', json=data, headers=headers, cookies={ "token": self.token}, stream = True) as response:
            print(response.url)
            decoded_data = b''.join(chunk for chunk in response.iter_content(chunk_size=None) if chunk)
            print(decoded_data.decode("utf-8"))

    #初始化函数,主要获取常用50个问题
    def on_start(self):
        self.model = 1
        self.model_id = "D1.0"
        self.token = "whpskyv14t0Fa3ezNN3XyNJBQilFvDyX3oF3y1pLVDzbFGzmQM2xsfXIfuSHeqQBtKvvmAUtUmJvA/MubnaUPRgG0rA2hvpiXuExVpNTHwu7c6RhO1oh+11UdNCjr/9x/pkFLSVw4ZsvF2hdoCmsvvoWrkmSJeDWAdP7zjZZqmGxq8G4uldadA=="
        self.patientid = "1823553602402713601"
        self.query = self.get_faq_from_xlsx("data/aigc-faq-raw.xlsx")
        
        
        print(self.query)
    
    def get_faq_from_xlsx(self, path:str):
        
        raw_faq = pd.read_excel(path)
        print(raw_faq)

        return raw_faq.sample(n=1).question.values[0]

