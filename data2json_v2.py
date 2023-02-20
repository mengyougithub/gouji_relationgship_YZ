from functools import reduce

import pandas as pd
import os
import json


def is_number(target_str):
    try:
        float(target_str)
        return True
    except:
        pass
    if target_str.isnumeric():
        return True
    return False


def is_number_list(l):
    for i in l:
        if is_number(i) == 0:
            return 0
    return 1


def getTitle(inloc, Elecount, list1):
    for j in range(inloc + 1, len(list1[0])):
        if list1[0][j] == "":
            list1[0][j] = list1[0][j - 1]

    for j in range(inloc + 1, len(i)):
        titley = ''
        for x in range(0, Elecount + 1):
            titley = titley + str(list1[x][j])
            titley = titley.replace('\n', '')
        titlelist.append(titley)
    return titlelist


# 将所有表格以行名为索引记录到字典里，输出json文件
path = 'xk师兄表格'  # 表格所在文件夹
excelall = os.listdir(path)
data_all = {}
for excel in excelall:
    data_excel = {}
    xlsx = pd.ExcelFile('xk师兄表格\\' + excel)
    sheet1 = pd.read_excel(xlsx, 'Sheet1', header=None, keep_default_na=False)
    list1 = sheet1.values.tolist()
    a = -1
    Elecount = 0
    inlocList = []
    titlelist = []
    flag = True
    for i in list1:  # 格式处理
        a = a + 1
        if a == 0:
            title = str(i[0])
            continue
        else:
            if i[0] == "":
                i[0] = list1[a - 1][0]
            if flag:
                if str(i[0]) == title and a + 1 < len(list1) and str(list1[a + 1][0]) != title and str(
                        list1[a - 1][0]) == title:
                    Elecount = Elecount + 1
                else:
                    flag = False
        if len(i) < 5 and i[-1] == '':
            continue
        if type(i[0]) == str:
            i[0] = i[0].replace('\n', '')
        j = len(i) - 1
        while j > 0:
            if type(i[j]) == str:
                i[j] = i[j].replace(',', '')
            if i[j] == '未披露':
                i[j] = float(-1)
            if i[j] == '-':
                i[j] = 0
            if (is_number(i[j])):
                i[j] = float(i[j])
            j = j - 1
        inloc = 0
        while inloc + 1 < len(i) and i[inloc + 1] != '' and i[inloc + 1] != '-' and type(i[inloc + 1]) == str:
            inloc = inloc + 1
        if inloc == len(i) - 1:
            continue
        if inloc > 0:
            i[inloc] = reduce(lambda x, y: str(x) + str(y), i[0:inloc + 1])
        # if isinstance(i[inloc] ,str):
        i[inloc] = i[inloc].replace('\n', '')
        if isinstance(i[inloc], str) and is_number_list(i[inloc + 1:len(i)]):
            data_excel[i[inloc]] = i[inloc + 1:len(i)]
            inlocList.append(inloc)

    if data_excel:
        data_excel['title'] = getTitle(inloc=min(inlocList), Elecount=Elecount, list1=list1)
        data_all[excel] = data_excel

with open('data_all_v2.json', 'w+', encoding='utf-8') as fp:
    json.dump(data_all, fp, indent=2, ensure_ascii=False)


