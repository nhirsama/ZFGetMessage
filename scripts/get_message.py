import base64
import os
import sys
import hashlib
import datetime
from pprint import pprint

from scripts.push import check_message_push
from zfn_api import Client


def write_file(words: dict):
    with open("../data/message_num.txt", "w", encoding="utf-8") as file:
        for dict_key,dict_value in words:
            file.write(f"{dict_key}: {dict_value}\n")
def write_file_list(words: list):
    with open("../data/message_num.txt", "w", encoding="utf-8") as file:
        file.write(f"{hashlib.md5(str(words).encode()).hexdigest()}")

cookies = {}
base_url = "https://jwglxxfwpt.hebeu.edu.cn/"  # 此处填写教务系统URL
raspisanie = []
ignore_type = []
detail_category_type = []
timeout = 5
stu = Client(cookies=cookies, base_url=base_url, raspisanie=raspisanie, ignore_type=ignore_type,
             detail_category_type=detail_category_type, timeout=timeout)
id_user = input("请输入学号：")
password_user = input("请输入密码：")
token = input("请输入token")
if cookies == {}:
    lgn = stu.login(id_user, password_user)  # 此处填写账号及密码
    if lgn["code"] == 1001:
        verify_data = lgn["data"]
        with open(os.path.abspath("kaptcha.png"), "wb") as pic:
            pic.write(base64.b64decode(verify_data.pop("kaptcha_pic")))
        verify_data["kaptcha"] = input("输入验证码：")
        ret = stu.login_with_kaptcha(**verify_data)
        if ret["code"] != 1000:
            pprint(ret)
            sys.exit()
        pprint(ret)
    elif lgn["code"] != 1000:
        pprint(lgn)
        sys.exit()

# result = stu.get_info()  # 获取个人信息
# result = stu.get_grade(2024, 1)  # 获取成绩信息，若接口错误请添加 use_personal_info=True，只填年份获取全年
# result = stu.get_exam_schedule(2024, 1)  # 获取考试日程信息，只填年份获取全年
# result = stu.get_schedule(2024, 1)  # 获取课程表信息
# result = stu.get_academia()  # 获取学业生涯数据
result = stu.get_notifications()  # 获取通知消息
# result = stu.get_selected_courses(2024, 1)  # 获取已选课程信息
# result = stu.get_block_courses(2024, 1, 1)  # 获取选课板块课列表
pprint(result, sort_dicts=False)
# other = [], tiao_ke = [], ting_ke = [], bu_ke = []
# message_num = {'调课提醒': 0, '停课提醒': 0, '补课提醒': 0, '其他信息': 0}
# with open("../data/message_num.txt", "r", encoding="utf-8") as file:
#     while True:
#         content = file.readline()
#         if content == "":
#             break
#         key, value = content.split(':')
#         result[key] = int(value)
#
with open("../data/message_num.txt", "r", encoding="utf-8") as file:
    push_hash = file.read()
push_list = []
for i in range(6):  #运行六次，如果第六次仍然无法与文件匹配则直接进行推送
    #将第i个元素信息与message_num.txt文件对比，如果相同则跳出循环，进行推送
    if hashlib.md5(str(result['data'][i]).encode()).hexdigest() == push_hash:
        break
    push_list.append(result['data'][i])
    if i == 5:
        break

#将最新通知的md5值存入文件中
with open("../data/message_num.txt", "w", encoding="utf-8") as file:
    file.write(hashlib.md5(str(result['data'][0]).encode()).hexdigest())
if len(push_list) > 0 :
    print(check_message_push(token, '正方教务管理系统消息通知', push_list),f"于{datetime.datetime.now()}")
else :
    print(f"教务系统未更新新通知，于{datetime.datetime.now()}")
'''
for i in result['data']:

    
    if i['type'] == '调课提醒':
        tiao_ke.append(i)
        if len(tiao_ke) > int(message_num['调课提醒']):
            print(check_message_push(token, '正方教务管理系统调课通知', str(tiao_ke[0])))
            message_num['调课提醒'] += 1
            break
    elif i['type'] == '停课提醒':
        ting_ke.append(i)
        if len(tiao_ke) > int(message_num['停课提醒']):
            print(check_message_push(token, '正方教务管理系统停课通知', tiao_ke[0]))
            message_num['停课提醒'] += 1
            break
    elif i['type'] == '补课提醒':
        bu_ke.append(i)
        if len(bu_ke) > int(message_num['补课提醒']):
            print(check_message_push(token, '正方教务管理系统补课通知', tiao_ke[0]))
            message_num['补课提醒'] += 1
            break
    else:
        other.append(i)
        if len(tiao_ke) > int(message_num['其他信息']):
            print(check_message_push(token, '正方教务管理系统其他通知', tiao_ke[0]))
            message_num['其他信息'] += 1
            break
    '''
# write_file(message_num)
print("message_num.txt更新完毕")
