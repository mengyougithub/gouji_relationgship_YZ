import pandas as pd
import os
import json
import re
import numpy as  np


#替换空格值为0
def rep_empty(l):
    return [0 if i =='' else i for i in l]

 #判断是否是数字
def is_number(target_str):
    try:
        float(target_str)
        return True
    except:
        pass
    if target_str.isnumeric():
        return True
    return False

#判断某数组是否都是数字
def is_number_list(l):
    for i in l:
        if is_number(i)==0:
            return 0
    return 1

def is_number_list_fromdir(l,dir):
    for h in l:
        if is_number_list(dir[h])==0:
            return 0
    return 1
#判断两列表是否相等，此功能也可调用np实现
def isequal(list1,list2):
    # if len(list1)==len(list2):
    #     n=len(list1)
    # else:n=min(len(list1),len(list2))
    if is_number_list(list1) and is_number_list(list2):
        return list2==list1
    else:return -1


#判断列表是否是字典索引列表的子集
def listindir(l,dir):
    for i in l:
        if i not in dir:
            return 0
    return 1

def checklen(l,dir):
    n=len(dir[l[0]])
    for i in l:
        if len(dir[i])!=n:
            return  0
    return n


# 将所有表格数据合并在json_data2大字典中，筛选不一致数据
with open('data_all.json','r',encoding='utf8')as fp:
    json_data = json.load(fp)
    # print('json_data\n',json_data)
    json_data2={}
    chinese = re.compile(u'[\u4e00-\u9fa5]')
    l1=list(json_data.values())
    print('list:',len(l1))
    for i in list(json_data.values()):

        for  k, v  in  i.items():
            if k not in json_data2:
                json_data2[k]=rep_empty(v)
            elif isequal(json_data2[k],v)==0:
                if len(k)>=4 and chinese.search(k):      #此判定是凭经验筛选出真正的重复数据，而不是坏数据
                    print('重复数据：')
                    print('索引：',k)
                    print(json_data2[k])
                    print(v)
                    print('')
    print('data2\n',json_data2)

# 提取规则
path ='规则'       #所有规则表格所在文件夹
excelall=os.listdir(path)

uprule2 =[]
downrule2 =[]
for excel in excelall:
    data_excel={}
    xlsx = pd.ExcelFile('规则\\'+excel)
    sheet1=pd.read_excel(xlsx,'Sheet1',keep_default_na=False)

    # 上勾稽表规则列表
    if 'Unnamed: 3' and 'Unnamed: 5' not in sheet1:
        continue
    uprule1=sheet1['Unnamed: 3']
    print(uprule1[1])
    for i in uprule1:
        if i !='上勾稽表字段' and i!='下勾稽表字段' and i!='':
            uprule2.append(i)
    # 下勾稽表规则列表
    downrule1=sheet1['Unnamed: 5']
    print(uprule1[1])
    for i in downrule1:
        if i !='上勾稽表字段' and i!='下勾稽表字段' and i!='':
            downrule2.append(i)
print('uprule2\n', uprule2)
print('downrule2\n',downrule2)

# 解析勾稽规则，查字典取值并运算，返回校验结果
for i,j in zip(uprule2,downrule2):
    j_split=re.split('[+\-*/]', j)
    j_oper=re.findall('[+\-*/]',j)
    if i in json_data2 and listindir(j_split,json_data2)  :
        # print(json_data2[i])
        if is_number_list(json_data2[i]) and is_number_list_fromdir(j_split,json_data2) and checklen(j_split,json_data2)==len(json_data2[i]):
            total1=np.array(json_data2[i])
            total2=np.array(json_data2[j_split[0]])
            print(i, total1)
            for k in range(len(j_oper)):
                element=np.array(json_data2[j_split[k+1]])
                if len(element)==len(total2):
                    if j_oper[k]=='+':
                        total2= total2 + element
                    elif j_oper[k]=='-':
                        total2= total2 - element
                    elif j_oper[k]=='*':
                        total2= total2 * element
                    elif j_oper[k]=='/':
                        total2 = total2 / element
                        # 粗暴实现运算.无法应对真正的四则运算
            print(j, total2)
            print( '相等判定', abs(total1-total2) < 0.011)
            # print( '相等判定', abs(total1-total2) < 0.011 or abs(total1-total2/10000) < 0.011 or abs(total1 / 10000 - total2) < 0.011)
            print('')

# todo 1、分析数据   2、用超级pdf提取