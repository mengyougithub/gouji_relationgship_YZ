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
def is_number_list_list(l):
    for i in l:
        for j in i:
            if is_number(j)==0:
                return 0
    return 1
def is_number_listfromdir(l,dir):
    for h in l:
        if is_number_list(dir[h])==0:
            return 0
    return 1
#判断两列表是否相等，此功能也可调用np实现
def isequal(list1,list2):
    if is_number_list(list1) and is_number_list(list2):
        for i, j in zip(list1,list2):
            if not(abs(i-j) < 0.011 or abs(i-j/10000) < 0.011 or abs(i / 10000 - j) < 0.011):
                return 0
        return 1
    else:return -1

#判断列表是否是字典索引列表的子集
def listindir(l,dir):
    for i in l:
        if i not in dir:
            return 0
    return 1

def checklen(l,dir):
    n = len(dir[l[0]][0])
    for i  in l :
        if len(dir[i])!=1:
            return -1
        if len(dir[i][0])!=n:
            return  -1
    return n

def chinese_count(str):
    count=0
    for s in str:
        if '\u4e00' <= s <= '\u9fff':    # 中文字符范围
            count=count+1
    return count


def unequal_num(list1,list2):           #两个列表元素逐个对比，返回不等数目
    unequal_num=0
    for i, j in zip(list1,list2):
        if not(abs(i-j) < 0.011 or abs(i-j/10000) < 0.011 or abs(i / 10000 - j) < 0.011):
            unequal_num =unequal_num+1
    return unequal_num

# 将所有表格数据合并在json_data2大字典中，同时校验跨表同索引数据的一致性
count_display=0
with open('data_all2.json','r',encoding='utf8')as fp:
    json_data = json.load(fp)
    # print('json_data\n',json_data)
    json_data2={}
    chinese = re.compile(u'[\u4e00-\u9fa5]')
    l1=list(json_data.values())

    for i in l1:
        for  k, v  in  i.items():
            if is_number_list(v)==0:
                continue
            if k not in json_data2:
                json_data2[k]=[]
                json_data2[k].append(v)
            else:
                unequalnum=99
                equal_exist_flag=0
                for each in json_data2[k]:
                    if len(each) == len(v) :                    #长度判定解决数据穿插百分比问题
                        unequalnum=unequal_num(each,v)
                    elif len(each) == len(v) * 2 :
                        unequalnum = unequal_num(each[0:-1:2], v)
                    elif len(each) == len(v) / 2 :
                        unequalnum = unequal_num(each,v[0:-1:2])
                    if  unequalnum==0:
                        if len(k)>=4 and chinese_count(k)>3:      #此判定是凭经验筛选出真正的重复数据，而不是坏数据 todo 此种判定较粗暴，应该建立财会项名数据库，从中匹配
                            count_display = count_display + 1
                            print('跨表一致数据：')
                            print('索引：',k)
                            print(each)
                            print(v)
                            print('')
                            equal_exist_flag = 1
                            break
                    elif unequalnum==1:
                        if len(k) >= 4 and chinese_count(k) > 3:
                            count_display = count_display + 1
                            print('跨表不一致数据：')
                            print('索引：', k)
                            print(each)
                            print(v)
                            print('')
                            equal_exist_flag = 1
                            break
                if equal_exist_flag==0:
                    json_data2[k].append(v)
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

    for i in uprule1:
        if i !='上勾稽表字段' and i!='下勾稽表字段' and i!='':
            uprule2.append(i)
    # 下勾稽表规则列表
    downrule1=sheet1['Unnamed: 5']
    for i in downrule1:
        if i !='上勾稽表字段' and i!='下勾稽表字段' and i!='':
            downrule2.append(i)
print(len(uprule2))
print(len(downrule2))
print('uprule2\n', uprule2)
print('downrule2\n',downrule2)


# 解析勾稽规则，查字典取值并运算，返回校验结果
for i,j in zip(uprule2,downrule2):
    if j==i:
        continue
    j_split = re.split('[+\-*/]', j)
    j_oper=re.findall('[+\-*/]',j)
    if i in json_data2 and listindir(j_split,json_data2)  :
        # print(json_data2[i])
        # if is_number_list_list(json_data2[i]) and is_number_listfromdir(j_split,json_data2) and checklen(j_split,json_data2)==len(json_data2[i]):

        total2 = np.array(json_data2[j_split[0]][0])
        len_j_dirvalue=checklen(j_split, json_data2)

        for each in json_data2[i]:
            total1 = np.array(each)
            if   len_j_dirvalue== len(each):
                for k in range(len(j_oper)):
                    element=np.array(json_data2[j_split[k+1]][0])
                    if j_oper[k]=='+':
                        total2= total2 + element
                    elif j_oper[k]=='-':
                        total2= total2 - element
                    elif j_oper[k]=='*':
                        total2= total2 * element
                    elif j_oper[k]=='/':
                        total2 = total2 / element
                            # 粗暴实现运算.无法应对真正的四则运算
                unequalnum=unequal_num(total1,total2)
                if i == '合计':                                   #todo 此处把底层表的具体规则也等同于通用规则，不合理
                    if unequalnum==0 :
                        # for m, n in zip(total1,total2):
                        #     if  abs(m-n) < 0.011 or abs(m-n/10000)<0.011 or abs(m/10000-n)<0.011:
                        #         result.append(True)
                        #     else:result.append(False)
                        count_display=count_display+1
                        print('表内一致数据：')
                        print(i, total1)
                        print(j, total2)
                        # print( '相等判定', result)
                        print('')
                    if unequalnum==1:                           #两个列表不等数目为1，判定为不一致数据 todo 此处假设不一致数据全部错误的可能性较小，不一定符合事实
                        result = []
                        for m, n in zip(total1, total2):
                            if abs(m - n) < 0.011 or abs(m - n / 10000) < 0.011 or abs(m / 10000 - n) < 0.011:
                                result.append(True)
                            else:
                                result.append(False)
                        count_display=count_display+1
                        print('跨表勾稽：')
                        print(i, total1)
                        print(j, total2)
                        print('相等判定', result)
                        print('')
                else:
                    if unequalnum==0 :
                        count_display=count_display+1
                        print('跨表一致数据：')
                        print(i, total1)
                        print(j, total2)
                        # print( '相等判定', result)
                        print('')
                    if unequalnum==1:
                        count_display=count_display+1
                        result = []
                        for m, n in zip(total1, total2):
                            if abs(m - n) < 0.011 or abs(m - n / 10000) < 0.011 or abs(m / 10000 - n) < 0.011:         #粗暴解决单位不一致问题 todo 目前只能处理万级单位之间
                                result.append(True)
                            else:
                                result.append(False)
                        print('跨表不一致数据：')
                        print(i, total1)
                        print(j, total2)
                        print('相等判定', result)
                        print('')
print('count_display:',count_display)
