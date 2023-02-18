import json
import re
import numpy as np

#todo 重构两份代码：1、print模块化，2、try pass 3、功能合并（四对） 4、考虑接口问题 5、
#todo 继续完善表内勾稽
def unequal_num(list1,list2):           #两个列表元素逐个对比，返回不等数目
    unequal_num=0
    for i, j in zip(list1,list2):
        if not(abs(i-j) < 0.011 or abs(i-j/10000) < 0.011 or abs(i / 10000 - j) < 0.011):
            unequal_num =unequal_num+1
    return unequal_num


def list_sum(input_list, start_index, end_index):
    if end_index < start_index:
        return "End index cannot be lower than the start index"
    else:
        return np.sum(np.array(input_list[start_index:end_index+1]),axis=0)

def sum_according_indexlist(indexlist,input_list,name_list):
    m=0
    while m<len(indexlist)-1:
        total1=input_list[indexlist[m+1]]
        total2=list_sum(input_list,indexlist[m]+1,indexlist[m+1]-1)
        if unequal_num(total1,total2)<2:
            print(name_list[indexlist[m+1]])
            print('+'.join(name_list[indexlist[m]+1:indexlist[m+1]]))
            judgeandprint(total1, total2)
        m += 1


def judgeandprint(total1, total2):
    unequalnum = unequal_num(total1, total2)
    if unequalnum == 1:  # 两个列表不等数目为1，判定为不一致数据 todo 此处假设不一致数据全部错误的可能性较小，不一定符合事实
        result = []
        for t1, t2 in zip(total1, total2):
            if abs(t1 - t2) < 0.011 or abs(t1 - t2 / 10000) < 0.011 or abs(t1 / 10000 - t2) < 0.011:
                result.append(True)
            else:
                result.append(False)
        print('表内不一致数据：')
        print(total1)
        print(total2)
        print('相等判定', result)
        print('')
    if unequalnum == 0:
        # count_display = count_display + 1
        print('表内一致数据：')
        print(total1)
        print(total2)
        # print( '相等判定', result)
        print('')

def iseverylist_leneaual(l):
    for i in range(len(l)-1):
        if len(l[i])!=len(l[i+1]):
            return 0
    return 1

with open('data_all_v2.json', 'r', encoding='utf8')as fp:
    json_data = json.load(fp)
    for k,v in json_data.items():
        try:
            # if k!= 'Table 110.xlsx':
            #     continue
            l1=list(v.keys())
            if iseverylist_leneaual(list(v.values()))==0:
                continue
            leni=0
            for i in list(v.values()):
                if len(i) != 0:
                    leni= len(i)
                    break
            l2 = list(map(lambda x:[0]*leni if x==[] else x, list(v.values())))
            indexlist = [-1]
            flag = 0  # 是否含有小计
            for ind, val in enumerate(l1):
                if '合计' in val:
                    indexlist.append(ind)
                elif '小计' in val :
                    indexlist.append(ind)
                    flag = 1
            if flag==1 and '合计' not in l1[-1]:
                flag = 0
            if indexlist!=[-1]:
                if flag==0:
                    sum_according_indexlist(indexlist,l2,l1)

                elif len(indexlist)>2:
                    sum_according_indexlist(indexlist[0:-1],l2,l1)
                    total2=0
                    total1=np.array(l2[indexlist[-1]])
                    for each in indexlist[0:-1]:
                       total2+= np.array(l2[each])
                    judgeandprint(total1, total2)
        except:
            print(indexlist)
            pass

#todo 预处理：存在


    #
    # # print('json_data\n',json_data)
    # json_data2={}
    # chinese = re.compile(u'[\u4e00-\u9fa5]')
    # l1=list(json_data.values())
    # print('list:',len(l1))
    # for i in list(json_data.values()):
    #
    #     for  k, v  in  i.items():
    #         if k not in json_data2:
    #             json_data2[k]=rep_empty(v)
    #         elif isequal(json_data2[k],v)==0:
    #             if len(k)>=4 and chinese.search(k):      #此判定是凭经验筛选出真正的重复数据，而不是坏数据
    #                 print('重复数据：')
    #                 print('索引：',k)
    #                 print(json_data2[k])
    #                 print(v)
    #                 print('')
    # print('data2\n',json_data2)
