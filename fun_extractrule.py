import os
from pprint import pprint

import pandas as pd

def extractrule(path):
    excelall = os.listdir(path)
    for excel in excelall:
        xlsx = pd.ExcelFile(path+'\\' + excel)
        sheet1 = pd.read_excel(xlsx, 'Sheet1', keep_default_na=False)
        if 'Unnamed: 3' and 'Unnamed: 5' not in sheet1:
            continue
        rulejson={'表内':{'uprule':[],'downrule':[]},'跨表':{'uprule':[],'downrule':[]}}
        upxslname= sheet1['Unnamed: 2']
        downxslname= sheet1['Unnamed: 4']
        uprule1 = sheet1['Unnamed: 3']
        downrule1 = sheet1['Unnamed: 5']

        maxl= len(uprule1)
        for i in range(maxl):
            if uprule1[i] != '上勾稽表字段' and uprule1[i] != '下勾稽表字段' and uprule1[i] != '':
                if upxslname[i]== downxslname[i]:
                    rulejson['表内']['uprule'].append(uprule1[i])
                else:
                    rulejson['跨表']['uprule'].append(uprule1[i])
            if downrule1[i] != '上勾稽表字段' and downrule1[i] != '下勾稽表字段' and downrule1[i] != '':
                if upxslname[i] == downxslname[i]:
                    rulejson['表内']['downrule'].append(downrule1[i])
                else:
                    rulejson['跨表']['downrule'].append(downrule1[i])
    return rulejson
    # return uprule2,downrule2
# uprule2,downrule2=extractrule('规则')
# pprint(extractrule('规则'))
# print(downrule2)