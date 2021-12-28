from os import replace
import requests
import pyperclip
import json
from bs4 import BeautifulSoup
 
# 以下为GET请求
# url = 'http://exm-mayuan-ans.chaoxing.com/exam/phone/look-detail?courseId=221854860&classId=4640&examId=387760&examAnswerId=953848&protocol_v=1'
while True:
    url : str = input("请输入网页链接：")
    data_object : list = []
    file_data = open("que_data.txt", 'r')
    data_json : str = file_data.read()
    if data_json == '':
            data_object = json.loads("[]")
    else:
        data_object = json.loads(data_json)
    file_data.close()
    if url != "":
        cookie : str = input("请输入 Cookie：")
        headers = {
            "Cookie" : cookie
        }
        req = requests.get(url = url, headers = headers)
        html = req.content.decode('utf-8')
        req.close()
        soup = BeautifulSoup(html,'lxml')
        file_data = open("que_data.txt", 'w')
        ignore = 0
        add = 0
        que_data = soup.find_all(class_ = 'zm_box bgColor') # 题目
        for que_item in que_data:
            ans_str : str = que_item.next_sibling.next_sibling.p.text.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "").replace("正确答案：", "").strip()
            que_item = que_item.div.div
            que_str : str = que_item.span.nextSibling.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "")
            sel_list = que_item.find(class_ = "zm_key") # 选项集合
            if sel_list is None:
                que_str = "（" + ans_str + "）" + que_str
            else:
                first = True
                for sel_item in sel_list:
                    if sel_item.name == "li":
                        sel_id = sel_item.label.em.string.replace(".", "")
                        sel_str = sel_item.label.find("cc").string
                        if ans_str.find(sel_id) != -1:
                            if first:
                                ans_str = ans_str.replace(sel_id, sel_str)
                                first = False
                            else:
                                ans_str = ans_str.replace(sel_id, " || " + sel_str)
                que_str = que_str.replace("（）", "【" + ans_str + "】")
                que_str = que_str.replace("()", "【" + ans_str + "】")
            try:
                data_object.index(que_str)
                ignore += 1
            except:
                data_object.append(que_str)
                add += 1
        data_object.sort()
        print("从网站获取总数据：" + str(add + ignore) + " 条")
        print("已忽略已存在数据：" + str(ignore) + " 条")
        print("正在向数据文件写入 " + str(add) + " 条数据......")
        file_data.write(json.dumps(data_object))
        file_data.close()
        print("写入完成！")
    print("当前数据文件总数：" + str(len(data_object)) + " 条")
    print("正在将数据文件转换为可视化文件......")
    file_view = open("que_view.txt", 'w')
    id = 1
    for item in data_object:
        file_view.write(str(id) + ". " + item.replace(u'\xa0', u'') + "\n\n")
        id += 1
    file_view.close()
    print("转换完成！")
    print("正在分析可视化文件......")
    file_ana = open("que_ana.txt", 'w')
    dic : dict = {}
    for item in data_object:
        item : str = item.replace(u'\xa0', u'')
        if item.find("【") != -1 and item.find("】") != -1:
            item = item[item.index("【") + 1 : item.index("】")]
            if item.find(" || ") == -1:
                item = item.replace(" || ", "\",\"")
                item = "[\"" + item + "\"]"
                item_obj : json = json.loads(item)
                for o in item_obj:
                    if dic.get(o) == None:
                        dic[o] = 1
                    else:
                        dic[o] = dic[o] + 1
    dic = (sorted(dic.items(), key=lambda d:d[1]))
    dic = sorted(dic)
    for i in dic:
        file_ana.write(i[0] + " " + str(i[1]) + "\n")
    file_ana.close()
    print("分析完成！")