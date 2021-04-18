#!/usr/bin/python3

# -*- coding: utf-8 -*-
#378行和381行自己改变速度，太快会封号
#运用了随机模块，例如378行(4000, 4500)) / 500)意思就是8—9秒随机一个数，而且是浮点数，可以是任意小数，可以自行修改，但不要快于6S
import requests
import json
import time
import random
import re
import hashlib
import os
import platform
import sys
import traceback
import getopt
import base64

VERSION_NAME = "sisipython"
cookie = "_ga=GA1.2." + str(random.randrange(50000000,59999999)) + "." + str(int(time.time())-random.randrange(30000,120000)) + "; _gid=GA1.2." + str(random.randrange(500000000,599999999)) + "." + str(int(time.time())-random.randrange(30000,120000)) + "; tgw_l7_route=" + hashlib.md5(str(random.randrange(10000,99999)).encode('utf8')).hexdigest() + "; _gat=1"
fenshu_all = 0
mubiao = input('输入你想刷的分数（微信公众号：爱送福利的貔貅）:')
answer_dictionary = {}
hit_count = 0
mode_id_list = [
    {"id": "5f71e934bcdbf3a8c3ba51d5", "name": "英雄篇"},
    {"id": "5f71e934bcdbf3a8c3ba51d6", "name": "复兴篇"},
    {"id": "5f71e934bcdbf3a8c3ba51d7", "name": "创新篇"},
    {"id": "5f71e934bcdbf3a8c3ba51d8", "name": "信念篇"},
]
fenshu_all = 0
mode_id = None
random_mode_enabled = True
inform_enabled = False
auto_refresh_token_enabled = False
expire_time = -1
way = "1"


class MyError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "{}({})".format(self.msg, self.code)


def SubmitVerification(header, code=None):
    if code == None:
        if way == "1":
            code = "HD1bhUGI4d/FhRfIX4m972tZ0g3jRHIwH23ajyre9m1Jxyw4CQ1bMKeIG5T/voFOsKLmnazWkPe6yBbr+juVcMkPwqyafu4JCDePPsVEbVSjLt8OsiMgjloG1fPKANShQCHAX6BwpK33pEe8jSx55l3Ruz/HfcSjDLEHCATdKs4="
        elif way == "2":
            code = "BzPdXIQzu5Z2GHMkgWt9iBUQTbo2EWmw7tIuDaIEa4EQSXziGlUmS4aqrzw8Pzo51P+YtbUpAaqKLWF/rG4G41TnHGtItm7NkU90024LysxGUzh4jhy9YO0ivJZ3MSv+WcA8u/1TacORW4cvm9uBejdpTBOdWsDFOjJpTdCkYYE="
    
    submit_data = {
        "activity_id": "5f71e934bcdbf3a8c3ba5061",
        "mode_id": mode_id,
        "way": way,
        "code": code
    }
    url = "https://ssxx.univs.cn/cgi-bin/save/verification/code/"
    response = requests.post(url, json=submit_data, headers=header)
    result = json.loads(response.text)
    if result["code"] != 0:
        raise MyError(result["code"], "提交验证码失败: " + str(result))


def CheckVerification(header, code=None):
    if code == None:
        if way == "1":
            code = "E5ZKeoD8xezW4TVEn20JVHPFVJkBIfPg+zvMGW+kx1s29cUNFfNka1+1Fr7lUWsyUQhjiZXHDcUhbOYJLK4rS5MflFUvwSwd1B+1kul06t1z9x0mfxQZYggbnrJe3PKEk4etwG/rm3s3FFJd/EbFSdanfslt41aULzJzSIJ/HWI="
        elif way == "2":
            code = "caap/GndfVmhoudMEhf1C7vjG5Hyc1gMLPNZAT6yfdx2kt8jOTCzUYsbd1dyqUYRCv4/rLZGf++4HIK/7Q2/ZWlOkQDTV9gxOOHjwkKqkF/oZZIOg0714FXPZj8eet44bp481QRDyjqBzwGAM3xzQut5bLqeTLkayexsu2Q3P9g="
    
    submit_data = {
        "activity_id": "5f71e934bcdbf3a8c3ba5061",
        "mode_id": mode_id,
        "way": way,
        "code": code
    }
    url = "https://ssxx.univs.cn/cgi-bin/check/verification/code/"
    response = requests.post(url, json=submit_data, headers=header)
    result = json.loads(response.text)
    if result["code"] != 0:
        raise MyError(result["code"], "检查验证码失败: " + str(result))

    return result["status"]


def ParseToken(token):
    data = token.split('.')
    user_info = json.loads(str(base64.b64decode(data[1] + "=="), "utf-8"))

    token_info = {
        "name": user_info["name"],
        "uid": user_info["uid"],
        "time": int(user_info["iat"]),
        "expire": int(user_info["exp"])
    }
    return token_info


def RefreshToken(header):
    url = "https://ssxx.univs.cn/cgi-bin/authorize/token/refresh/"
    response = requests.get(url, headers=header)

    result = json.loads(response.text)
    if result["code"] != 0:
        raise MyError(result["code"], "更新token失败: " + str(result["message"]))

    new_token = result["token"]

    detail = ParseToken(new_token)
    print("token更新完成，于 ", time.asctime(time.localtime(detail["time"])), " 生效")
    print("将在 ", time.asctime(time.localtime(detail["expire"])), " 失效")

    return new_token


def SendNotification(msg):
    if not inform_enabled:
        print("[info] ", msg)
        return
    url = "http://localhost:6666"
    payload = {"type": VERSION_NAME, "msg": msg}
    response = requests.post(url, json=payload)
    print(response.text)


def ReadAnswerFromFile():
    global answer_dictionary
    try:
        answer_file = open("answer.txt", "r")
        answer_dictionary = json.loads(answer_file.read())
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        answer_file = open("answer.txt", "w+")
        answer_file.write("{}")
        answer_file.seek(0, 0)
        answer_dictionary = json.loads(answer_file.read())
    finally:
        print("已读取", len(answer_dictionary.items()), "个答案！")
        answer_file.close()



def SaveAnswerToFile():
    global answer_dictionary
    answer_file = open('answer.txt', 'w')
    answer_file.write(json.dumps(answer_dictionary))
    print("已保存", len(answer_dictionary.items()), "个答案！")
    answer_file.close()
    pass



def BuildHeader(token):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'x-requested-with': 'com.tencent.mm',
        'Host': 'ssxx.univs.cn',
        'Referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/' + mode_id,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Authorization': 'Bearer ' + token,
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'cookie': cookie    }

    return headers


def PrintQuizObject(quiz_object):
    print("问题ID列表: ")
    for i in range(0, 20):
        print("问题", i, ": ", quiz_object["question_ids"][i])


def StartQuiz(header):
    global hit_count
    hit_count = 0

    print("尝试开始考试……")

    url = "https://ssxx.univs.cn/cgi-bin/race/beginning/?activity_id=5f71e934bcdbf3a8c3ba5061&mode_id={}&way={}".format(
        mode_id,
        way
    )

    for fail in [0, 1, 2]:    # 最多尝试等待3次
        response = requests.request("GET", url, headers=header)
        quiz_object = json.loads(response.text)
        status_code = quiz_object["code"]

        if status_code == 0:
            print("开始考试成功，本次考试信息如下: ")
            print("race_code", quiz_object["race_code"])

            return quiz_object["question_ids"], quiz_object["race_code"]

        elif status_code == 4832:
            print("答题次数用完，等待10分钟")
            if fail == 0:   # 在开始等待时发送通知
                SendNotification("...")
            time.sleep(500)

        else:
            raise MyError(status_code, "开始考试失败: " + str(quiz_object))


def GetTitleMd5(title):
    title = re.sub(
        r"<(\w+)[^>]+?(?:display: {0,}none;).*?>.*?<\/\1>", "", title)
    title = re.sub("<.*?>", "", title)
    result = hashlib.md5(title.encode(encoding='UTF-8')).hexdigest()
    print(title, ", hash:", result)
    return result


def GetQuestionDetail(question_id, header):
    url = "https://ssxx.univs.cn/cgi-bin/race/question/?activity_id=5f71e934bcdbf3a8c3ba5061&question_id={}&mode_id={}&way={}".format(
        question_id,
        mode_id,
        way
    )

    response = requests.request("GET", url, headers=header)

    if response.status_code != 200:
        raise MyError(response.status_code, "获取题目信息失败")

    question_detail_object = json.loads(response.text)
    if question_detail_object["code"] != 0:
        raise MyError(question_detail_object["code"], "获取题目信息失败。问题ID: " +
                      question_id + "错误信息: " + str(question_detail_object))

    print("获取题目信息成功。")

    question = {}
    question["id"] = question_detail_object["data"]["id"]
    question["title"] = GetTitleMd5(question_detail_object["data"]["title"])
    question["answer_list"] = []
    for i in question_detail_object["data"]["options"]:
        question["answer_list"].append((i["id"], GetTitleMd5(i["title"])))

    return question


def BuildAnswerObject(question):
    global answer_dictionary
    global hit_count

    print("正在尝试寻找答案……")

    answer_object = {
        "activity_id": "5f71e934bcdbf3a8c3ba5061",
        "question_id": question["id"],
        "answer": None,
        "mode_id": mode_id,
        "way": way
    }

    if answer_dictionary.__contains__(question["title"]):
        hit_count += 1
        print("答案库中存在该题答案")
        answer_object["answer"] = []
        for i in question["answer_list"]:
            if i[1] in answer_dictionary[question["title"]]:
                answer_object["answer"].append(i[0])
    else:
        print("答案库中不存在该题答案，蒙一个A选项吧")
        answer_object["answer"] = [question["answer_list"][0][0]]

    return answer_object, question


def SubmitAnswer(answer_object, header):
    global answer_dictionary

    url = "https://ssxx.univs.cn/cgi-bin/race/answer/"

    header["Content-Type"] = "application/json;charset=utf-8"

    response = requests.request(
        "POST", url, headers=header, data=json.dumps(answer_object[0]))

    if response.status_code != 200:
        raise MyError(response.status_code, "提交答案失败")

    result_object = json.loads(response.text)

    if not result_object["data"]["correct"] and answer_dictionary.__contains__(answer_object[1]["title"]):
        print("答案库中已有答案但不正确！")
    elif result_object["data"]["correct"] and answer_dictionary.__contains__(answer_object[1]["title"]):
        return True
    elif result_object["data"]["correct"] and not answer_dictionary.__contains__(answer_object[1]["title"]):
        SaveAnswerToFile()
        print("运气不错，居然蒙对了，保存答案")
    elif not result_object["data"]["correct"] and not answer_dictionary.__contains__(answer_object[1]["title"]):
        SaveAnswerToFile()
        print("答案错误，更新答案")

    if not answer_dictionary.__contains__(answer_object[1]["title"]):
        answer_dictionary[answer_object[1]["title"]] = []

    for i in result_object["data"]["correct_ids"]:
        print("服务器返回的正确答案: ", i)
        for j in answer_object[1]["answer_list"]:
            if i == j[0]:
                print("已在问题列表中找到该答案，元组为", j)
                answer_dictionary[answer_object[1]["title"]].append(j[1])
                break

    return result_object["data"]["correct"]


def FinishQuiz(race_code, header):
    global fenshu_all
    global mubiao
    url = "https://ssxx.univs.cn/cgi-bin/race/finish/"

    header["Content-Type"] = "application/json;charset=utf-8"
    payload = "{\"race_code\":\"" + race_code + "\"}"

    result = json.loads(requests.request(
        "POST", url, headers=header, data=payload).text)
    print("回答完毕，本次得分: ", result["data"]["owner"]
          ["correct_amount"], "答案库命中数: ", hit_count)
    fenshu_all = fenshu_all + int(result['data']['owner']['correct_amount'])
    print('已经得了', fenshu_all, ' 这么多分，几万分你怎么敢的呀，嗷，才这么点分啊，那没事了')
    if int(fenshu_all) >= int(mubiao):
        print('刷完了，但是完全没有刷完，按任意键退出')
        sys.exit()
    print()
    fail = 0
    while result["code"] != 0:
        print("完成考试时出错，错误代码: ", result)
        err_code = result["code"]
        if err_code == 1001 or err_code == 1002:
            raise MyError(err_code, "请重新登录")
        fail += 1
        if fail > 5:
            raise MyError(err_code, "完成时出错: " + str(result))
        time.sleep(3)
        result = json.loads(requests.request(
            "POST", url, headers=header, data=payload).text)

    print("回答完毕，本次得分: ", result["data"]["owner"]
          ["correct_amount"], "答案库命中数: ", hit_count)


def Pause():
    if platform.system() == "Windows":
        os.system("pause")


def Start(token):
    global mode_id
    global expire_time

    ReadAnswerFromFile()

    try:
        while True:
            if random_mode_enabled:
                mode = mode_id_list[random.randrange(0, 4)]
                mode_id = mode["id"]
                print("这一轮，这一轮是", mode["name"])
                time.sleep(6)#选择哪个篇章的等待时间

            header = BuildHeader(token)

            question_list, race_code = StartQuiz(header)
            for i in range(0, 20):
                try:
                    if SubmitAnswer(BuildAnswerObject(GetQuestionDetail(question_list[i], header)), header):
                        print("第", i + 1, "题回答正确！")
                        time.sleep(float(random.randint(4000, 4500)) / 500)#每隔一题速度
                    else:
                        print("第", i + 1, "题回答错误，答案已更新！")
                        time.sleep(float(random.randrange(3000, 4000)) / 1500)#答题错误反应速度
                except MyError as err:
                    if err.code == 2104: # 2104: Question not exist
                        SendNotification("问题不存在，已跳过: " + question_list[i])
                        pass
                    else:
                        raise err

                if i == 10:
                    if CheckVerification(header):
                        print("验证码已通过")
                    else:
                        SubmitVerification(header)
                        print("验证码状态: ", CheckVerification(header))

            FinishQuiz(race_code, header)
            time.sleep(float(random.randrange(3000, 4000)) / 1500)#完成篇章等待时间

            if auto_refresh_token_enabled and expire_time - time.time() < 500:
                new_token = RefreshToken(header)
                expire_time = ParseToken(new_token)["expire"]
                token = new_token
                SendNotification(new_token)
                SendNotification(
                    "token已更新至 " + time.asctime(time.localtime(expire_time)))
                time.sleep(5)

    except MyError as err:
        tag = "[{}] ".format(time.asctime(time.localtime(time.time())))

        if err.code == 1001 or err.code == 1002:
            print(tag, "不要开网络代理，例如vpn，所以登录无效，通知重新登录")
            SendNotification("请重新登录（代码: {}）".format(err.code))
        elif err.code == 1005:
            print(tag, "token过期了，当前token已退出登录，请重新获取")
        else:
            msg = "已停止，原因就是你网速不行，换流量: " + str(err)
            print(tag, msg)
            SendNotification(msg)
    except Exception as err:
        tag = "[{}] ".format(time.asctime(time.localtime(time.time())))
        print(tag, traceback.format_exc())
    finally:
        SaveAnswerToFile()
        SendNotification("awsl")   # 程序退出时发送通知
        Pause()


def PrintHelp():

    print(sys.argv[0])
    print()
    print("    -a, --auto         自动更新token  （默认关）")
    print("    -h, --help         显示此帮助信息")
    print("    -i, --inform       启用webhook通知（默认关）")
    print("    -m, --mode [index] 选择题目分类，默认0:随机")
    print("                       1:英雄篇, 2:复兴篇, 3:创新篇, 4:信念篇")
    print("    -v, --version      显示版本号")
    print()
    print("https://github.com/wmxerni/sisipython")


if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(
            argv, "ahim:v", ["auto", "help", "inform", "mode=", "version"])
    except getopt.GetoptError:
        PrintHelp()
        Pause()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ['-a', '--auto']:
            auto_refresh_token_enabled = True
        elif opt in ['-h', '--help']:
            PrintHelp()
            Pause()
            sys.exit()
        elif opt in ['-i', '--inform']:
            inform_enabled = True
        elif opt in ['-m', '--mode']:
            try:
                mode = int(arg)
                if mode not in range(0, 5):
                    raise ValueError()
                if mode == 0:
                    random_mode_enabled = True
                else:
                    random_mode_enabled = False
                    mode_id = mode_id_list[mode - 1]["id"]
            except ValueError:
                PrintHelp()
                Pause()
                sys.exit()
        elif opt in ['-v', '--version']:
            print(VERSION_NAME)
            Pause()
            sys.exit()



    token = input("请输入token(输入token后直接回车即可): ").strip()
    try:
        if token.find("token:") == 0:
            token = token[6:]
        token = token.strip("\" ")

        token_info = ParseToken(token)
        expire_time = token_info["expire"]
        print(token_info["name"], "，李在赣神魔，又偷偷摸摸地刷题")
        print('群主马上开学了，以后也不会在这上面花费功夫了，望见谅，普普通通的python小白罢了')

        print("token有效期剩余: ", time.strftime(
            "%Hh %Mm %Ss", time.gmtime(expire_time - time.time())))





    except Exception as err:
        print(traceback.format_exc())
        Pause()
        sys.exit(1)

    time.sleep(2.0)
    Start(token)