import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import json
import matplotlib.pyplot as plt
import requests
from matplotlib import rcParams
from collections import defaultdict

# 设置字体
rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置支持中文的字体，例如黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def decrypt_aes_ecb(encrypted_data: str) -> str:
    key = encrypted_data[:16].encode('utf-8')
    encrypted_data = encrypted_data[16:]
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data_bytes), AES.block_size)

    return decrypted_data.decode('utf-8')

def save_horizontal_bar_chart(data, file_path, start_date, end_date):
    plt.figure(figsize=(12, len(data) / 66 * 18))
    plt.barh(list(data.keys()), list(data.values()))
    for index, value in enumerate(list(data.values())):
        plt.text(value + 0.01 * max(data.values()),
                 index,
                 f"{value:.2f}",
                 va='center')
    
    # 添加标题、标签和标注信息
    plt.xlim(0, 1.2 * max(data.values()))
    plt.title(f"华清大学食堂消费情况\n日期范围：{start_date} 至 {end_date}")
    plt.xlabel("消费金额（元）")
    plt.figtext(0.5, 0.03, "项目地址：https://github.com/stardustLi/THU-Annual-Eat", horizontalalignment='center', fontsize=14)
    plt.savefig(file_path)
    plt.close()

def save_pie_chart(data, file_path, start_date, end_date, threshold=0.03):
    total = sum(data.values())
    others_value = 0
    new_data = {}
    for name, value in data.items():
        if value / total < threshold:
            others_value += value
        else:
            new_data[name] = value
    
    if others_value > 0:
        new_data["其它"] = others_value

    labels = list(new_data.keys())
    values = list(new_data.values())
    plt.figure(figsize=(10, 10))

    # 绘制饼图并设置字体
    wedges, texts, autotexts = plt.pie(
        values,
        labels=labels,
        autopct=lambda pct: '',
        startangle=90
    )

    # 手动调整前三名的字体大小
    sorted_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
    for i, idx in enumerate(sorted_indices):
        fontsize = 16 - 2 * i if i < 3 else 10  # 前三名字体较大
        value_percentage = values[idx] / total * 100
        autotexts[idx].set_fontsize(fontsize)
        autotexts[idx].set_text(f"{value_percentage:.2f}%\n({values[idx]:.2f}元)")

    # 设置标题和项目地址
    plt.title(f"C(an)T(een) Ranking\nDuration：{start_date} 至 {end_date}")
    plt.figtext(0.5, 0.03, "https://github.com/stardustLi/THU-Annual-Eat", horizontalalignment='center', fontsize=14)
    plt.savefig(file_path)
    plt.close()

idserial = ""
servicehall = ""
all_data = defaultdict(float)

if __name__ == "__main__":
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    # 提示用户修改日期
    print(f"当前查询的默认起止日期为：{start_date} 至 {end_date}")
    modify_dates = input("是否需要修改查询日期？(y/n): ").strip().lower()
    if modify_dates == 'y':
        start_date = input("请输入新的起始日期 (格式：YYYY-MM-DD): ").strip()
        end_date = input("请输入新的结束日期 (格式：YYYY-MM-DD): ").strip()

    try:
        with open("config.json", "r", encoding='utf-8') as f:
            account = json.load(f)
            idserial = account["idserial"]
            servicehall = account["servicehall"]
    except Exception as e:
        print("账户信息读取失败，请重新输入")
        idserial = input("请输入学号: ")
        servicehall = input("请输入服务代码: ")
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump({"idserial": idserial, "servicehall": servicehall}, f, indent=4)
    
    url = f"https://card.tsinghua.edu.cn/business/querySelfTradeList?pageNumber=0&pageSize=5000&starttime={start_date}&endtime={end_date}&idserial={idserial}&tradetype=-1"
    cookie = {
        "servicehall": servicehall,
    }
    response = requests.post(url, cookies=cookie)

    encrypted_string = json.loads(response.text)["data"]
    decrypted_string = decrypt_aes_ecb(encrypted_string)

    data = json.loads(decrypted_string)
    for item in data["resultData"]["rows"]:
        try:
            all_data[item["mername"]] += item["txamt"]
        except Exception as e:
            pass

    all_data = {k: round(v / 100, 2) for k, v in all_data.items()}  # 将分转换为元，并保留两位小数

    results_folder = "results"
    os.makedirs(results_folder, exist_ok=True)

    sorted_all_data = dict(sorted(all_data.items(), key=lambda x: x[1], reverse=False))
    save_horizontal_bar_chart(sorted_all_data, os.path.join(results_folder, "consumption_bar_chart.png"), start_date, end_date)

    canteen_data = defaultdict(float)
    for name, amount in all_data.items():
        canteen_name = name[:2]  # 获取前两位汉字
        canteen_data[canteen_name] += amount

    # 保存饼图，合并低于 3% 的食堂为 "其它"
    sorted_canteen_data = dict(sorted(canteen_data.items(), key=lambda x: x[1], reverse=True))
    save_pie_chart(sorted_canteen_data, os.path.join(results_folder, "consumption_pie_chart.png"), start_date, end_date, threshold=0.03)