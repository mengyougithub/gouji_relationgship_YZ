import json
import re
import numpy as  np
from fun_extractrule import extractrule

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
            return 0
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
with open('data_all_v2.json', 'r', encoding='utf8')as fp:
    json_data = json.load(fp)
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
                    if v==[]:
                        continue
                    if  unequalnum==0 :
                        # if len(k)>=4 and chinese_count(k)>3:      #此判定是凭经验筛选出真正的重复数据，而不是坏数据 todo 此种判定较粗暴，应该建立财会项名数据库，从中匹配
                            count_display = count_display + 1
                            print('跨表一致数据：')
                            print('索引：',k)
                            print(each)
                            print(v)
                            print('')
                            equal_exist_flag = 1
                            break
                    elif unequalnum==1:
                        # if len(k) >= 4 and chinese_count(k) > 3:
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
ruledic=extractrule('规则')

def judgeandprint(total1, total2):
    unequalnum = unequal_num(total1, total2)
    if unequalnum == 1:  # 两个列表不等数目为1，判定为不一致数据 todo 此处假设不一致数据全部错误的可能性较小，不一定符合事实
        result = []
        for t1, t2 in zip(total1, total2):
            if abs(t1 - t2) < 0.011 or abs(t1 - t2 / 10000) < 0.011 or abs(t1 / 10000 - t2) < 0.011:
                result.append(True)
            else:
                result.append(False)
        print(xsltype+'不一致数据：')
        print(total1)
        print(total2)
        print('相等判定', result)
        print('')
    if unequalnum == 0:
        print(xsltype+'一致数据：')
        print(total1)
        print(total2)
        print('')

for xsltype,rule2 in ruledic.items():
    uprule2,downrule2=rule2['uprule'],rule2['downrule']
        # 解析勾稽规则，查字典取值并运算，返回校验结果
    for i,j in zip(uprule2,downrule2):
        if j==i:
            continue
        j_split = re.split(' [+\-*/] ', j)
        j_oper=re.findall('[+\-*/]',j)
        if i in json_data2 and listindir(j_split,json_data2):
            total2 = np.array(json_data2[j_split[0]][0])
            len_j_dirvalue=checklen(j_split, json_data2)
            if len_j_dirvalue<=0:
                continue
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
                            total2 = total2 / element       # 粗暴实现运算.无法应对真正的四则运算
                    unequalnum = unequal_num(total1, total2)
                    if unequalnum < 2:
                        print(i,'=','+'.join(j_split))
                        judgeandprint(total1,total2)
