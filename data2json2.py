import datetime
import pandas
import pandas as pd
import os
import json

def is_number(str):
        try:
            float(str)
            return True
        except:
            pass
        if str.isnumeric():
            return True
        return False

# 将所有表格以行名为索引记录到字典里，输出json文件
path ='超级pdf表格'       #表格所在文件夹
excelall=os.listdir(path)
data_all={}
for excel in excelall:
    data_excel={}
    xlsx = pd.ExcelFile(path+'\\'+excel)
    sheet1=pd.read_excel(xlsx,excel.replace('.xlsx',''),keep_default_na=False)
    list1 =sheet1.values.tolist()
    for i in list1: #格式处理
        if type(i[0]) == str:
            i[0] = i[0].replace('\n', '')
        j=len(i)-1
        while j>0:
            if type(i[j]) == datetime.datetime or type(i[j]) == pandas.Timestamp:
                i[j]=str(i[j])
            # if type(i[j]) == str:
            #     i[j]=i[j].replace(',', '')
            if i[j]=='-':
                i[j]=''
            if i[j] == '':
                i[j]=0
            if (is_number(i[j])):
                i[j]=float(i[j])
            j=j-1
        inloc=0
        while inloc+1<len(i) and i[inloc+1]!='' and type(i[inloc+1]) == str:
            inloc = inloc + 1

        data_excel[str(i[inloc])] = i[inloc+1:len(i)]
        # data_excel[str(i[0])] = i[1:len(i)]
    # print(data_excel)
    data_all[excel]=data_excel
with open('data_all2.json', 'w+',encoding='utf-8') as fp:
    json.dump(data_all,fp, indent=2,ensure_ascii=False)

# d = []
# for r in range(sheet1.nrows): #将表中数据按行逐步添加到列表中，最后转换为list结构
#     data1 = []
#     for c in range(sheet1.ncols):
#         data1.append(sheet1.cell_value(r,c))
#     d.append(list(data1))

# print(d)
#print(sheet1.loc[0])

# print(pd.read_excel(xlsx, 'Sheet1'))
# print(sheet1.columns)
# print(sheet1[sheet1.columns[0]].loc[0])
#
# # print(xlsx)
# print(xlsx)
# # print(type(xlsx))


# # 打开刚才我们写入的 test_w.xls 文件
# wb = xlrd.open("测试1.xlsx")
#
# # 获取并打印 sheet 数量
# print( "sheet 数量:", wb.nsheets)
#
# # 获取并打印 sheet 名称
# print( "sheet 名称:", wb.sheet_names())
#
# # 根据 sheet 索引获取内容
# sh1 = wb.sheet_by_index(0)
# # 或者
# # 也可根据 sheet 名称获取内容
# # sh = wb.sheet_by_name('成绩')
#
# # 获取并打印该 sheet 行数和列数
# print( u"sheet %s 共 %d 行 %d 列" % (sh1.name, sh1.nrows, sh1.ncols))
#
# # 获取并打印某个单元格的值
# print( "第一行第二列的值为:", sh1.cell_value(0, 1))
#
# # 获取整行或整列的值
# rows = sh1.row_values(0) # 获取第一行内容
# cols = sh1.col_values(1) # 获取第二列内容
#
# # 打印获取的行列值
# print( "第一行的值为:", rows)
# print( "第二列的值为:", cols)
#
# # 获取单元格内容的数据类型
# print( "第二行第一列的值类型为:", sh1.cell(1, 0).ctype)
#
# # 遍历所有表单内容
# for sh in wb.sheets():
#     for r in range(sh.nrows):
#         # 输出指定行
#         print( sh.row(r))