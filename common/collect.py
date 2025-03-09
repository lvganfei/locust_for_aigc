import json
import os

import numpy as np
import requests
import statistics


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
        mean = int(np.mean(data_np))
    except:
        mean = 0
    try:
        # 计算中位数
        median = int(statistics.median(test_data))
    except:
        median = 0
    try:
        # 计算最大值
        max_val = int(np.max(data_np))
    except:
        max_val = 0
    try:
        # 计算最小值
        min_val = int(np.min(data_np))
    except:
        min_val = 0
    try:
        # 计算中位数
        percentile_90 = int(np.percentile(data_np, 90))
    except:
        percentile_90 = 0
    try:
        percentile_95 = int(np.percentile(data_np, 95))
    except:
        percentile_95 = 0
    try:
        percentile_99 = int(np.percentile(data_np, 99))
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
    return {
        "total": total,
        "min": min_val,
        "mean": mean,
        "median": median,
        "max": max_val,
        "90th": percentile_90,
        "95th": percentile_95,
        "99th": percentile_99,
        "variance": sample_variance
    }, content


def get_log_detail(log_path, title):
    def filter_valid_data():
        """
        检查行是否匹配
        如果匹配，则打印该行（或执行其他操作）
        """
        try:
            if 'First Time' in line:
                first_time = float(line.split('First Time:', 1)[1])
                first_time_list.append(first_time)
            elif 'Received Time' in line:
                received_time = float(line.split('Received Time:', 1)[1])
                received_time_list.append(received_time)
            elif 'First Word Count' in line:
                first_word = float(line.split('First Word Count:', 1)[1])
                first_word_total_list.append(first_word)
            elif 'Word Count' in line:
                word_count = float(line.split('Word Count:', 1)[1])
                word_total_list.append(word_count)
            elif 'Response Time' in line:
                response_time = float(line.split('Response Time:', 1)[1])
                response_time_list.append(response_time)
            elif 'Time Per Word' in line:
                time_per_word = float(line.split('Per Word:', 1)[1])
                time_per_word_list.append(time_per_word)
            elif 'Streaming POST Failed' in line:
                fail_code = float(line.split('code:', 1)[1])
                fail_list.append(fail_code)
        except Exception as e:
            print(e)

    parent_dir = os.getcwd()  # 获取目录
    data_path = os.path.join(parent_dir, log_path)
    print(data_path)
    first_time_list = []
    received_time_list = []
    first_word_total_list = []
    word_total_list = []
    time_per_word_list = []
    response_time_list = []
    fail_list = []
    send_content = f"<font color=\"warning\">【{title}】</font>\n>"
    # 打开日志文件
    with open(data_path, 'r') as log_file:
        # 遍历文件的每一行
        for line in log_file:
            # 去除行尾的换行符
            line = line.strip()
            filter_valid_data()

    statistics_dict = {
        '首次响应时间': first_time_list,
        '非首次响应时间': received_time_list
    }

    for k, v in statistics_dict.items():
        statistics_list, content = data_statistics(v, k)
        send_content += content
        print(statistics_list)
    print(fail_list)
    first_word_total = sum(first_word_total_list)

    word_total = sum(word_total_list)
    received_total = word_total - first_word_total

    total_time = sum(response_time_list) / 1000
    first_all_time = sum(first_time_list) / 1000
    received_all_time = sum(received_time_list) / 1000
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
    <font color=\"warning\"> ALL时间: {total_time}</font>\n
    <font color=\"warning\"> 失败数量: {len(fail_list)}</font>\n
    <font color=\"comment\"> 首次返回字数: {first_word_total}</font>\n
    <font color=\"comment\"> 返回总字数: {word_total}</font>\n
    <font color=\"warning\"> 响应字数/秒(首次): {first_rate}</font>\n
    <font color=\"warning\"> 响应字数/秒(包含首次): {word_total / all_time}</font>\n
    <font color=\"comment\"> 响应字数/秒(不包含首次): {received_total / received_all_time}</font>\n
    """
    message(send_content)
