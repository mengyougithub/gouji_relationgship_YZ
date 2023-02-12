# -*- coding: utf-8 -*-
# Date       ：2023/2/9
# Author     ：Chen Xuekai
# Description：

import pdfplumber
import difflib
import re
import json
import fitz
from fuzzywuzzy import process

punctuation = '[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\uff1f\u300a\u300b]'
float_pattern = "[-+]?[0-9]*\.?[0-9]+"


def rep_empty(l):
    return [0 if i == '' else i for i in l]


def string_similar(s1: str, s2: str) -> float:
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def to_float_list(l):
    return [float(i) for i in l]


# 判断是否是数字
def is_number(target_str):
    try:
        float(target_str)
        return True
    except:
        pass
    if target_str.isnumeric():
        return True
    return False


# 判断某数组是否都是数字
def is_number_list(l):
    for i in l:
        if not is_number(i):
            return False
    return True


def chinese_count(str):
    count = 0
    for s in str:
        if '\u4e00' <= s <= '\u9fff':  # 中文字符范围
            count = count + 1
    return count


def unequal_num(list1, list2):  # 两个列表元素逐个对比，返回不等数目
    unequal_num = 0
    for i, j in zip(list1, list2):
        if not (i == j or i == round(j / 10000, 2) or round(i / 10000, 2) == j):
            unequal_num = unequal_num + 1
    return unequal_num


def equal_check(list1, list2):
    # 解决穿插百分比的列表
    if len(list1) == len(list2) * 2:
        list1 = list1[0:-1:2]
    elif len(list1) == len(list2) / 2:
        list2 = list2[0:-1:2]
    # 等长列表判定元素
    if len(list1) == len(list2):
        # 若序列或逆序相等，则正确
        if unequal_num(list1, list2) == 0 or unequal_num(list1, list2[::-1]) == 0:
            return "文表勾稽正确"
        # 若序列或逆序有一个能部分匹配，则为勾稽错误，TODO：可能存在两列表不相关，但序列/逆序有重合的情况
        elif unequal_num(list1, list2) != len(list1) or unequal_num(list1, list2[::-1]) != len(list1):
            return "勾稽关系错误"
        else:
            return "字段匹配错误"
    else:
        return "字段匹配错误"


def match_strings(a: list, b: list):
    matches = []
    # 依次找出b中与a每个元素最相似的元素
    for string1 in a:
        best_match = process.extractOne(string1, b)
        matches.append((string1, best_match[0], best_match[1]))
    return matches


def get_all_field():
    with open('data_all.json', 'r', encoding='utf8') as fp:
        json_data = json.load(fp)
    json_data2 = {}
    all_field = list(json_data.values())

    # 构建倒排表 {字段：所属表格}
    inverted_list = {}
    for table_name, fields in json_data.items():
        if fields is None:  # 过滤fields为空的表
            continue
        for fields_name in fields.keys():
            if fields_name == "":  # 过滤字段为空的项
                continue
            try:
                inverted_list[fields_name].append(table_name)
            except:
                inverted_list[fields_name] = [table_name]
    # 合并大字典，{所有字段：数值列表}
    for field in all_field:
        if field is None:  # 过滤fields为空的表
            continue
        for field_name, field_num_list in field.items():
            if field_name == "":  # 过滤字段为空的项
                continue
            # 去除非数字或全0列表
            if not is_number_list(field_num_list) or all(i == 0.0 for i in field_num_list):
                continue
            if field_name not in json_data2:
                json_data2[field_name] = rep_empty(field_num_list)
    # print('data2\n', json_data2)
    return json_data2, inverted_list


# 提取页面中的文本待校验项
def extract_unverified_text(path):
    # 读取pdf内容，合并到一个变量中
    pdf = pdfplumber.open(path)
    all_text = ""
    for page in pdf.pages[1:]:
        text = page.extract_text().strip()
        text = text[text.find("\n") + 1:text.rfind("\n")]  # 去除页眉和页尾
        all_text += text

    # 以“分别为”作为关键字，提取文本中待验证的数字序列
    word_articulation_dict = {}
    for target in re.finditer("分别为", all_text):
        # 提取“分别为“前面字段作为键
        field_key = re.split(punctuation, all_text[:target.start()])[-1].replace("\n", "").strip()
        # 提取“分别为”后面数字列表作为值
        field_value = re.split(punctuation, all_text[target.end():])[0].replace("\n", "")
        field_value = to_float_list(re.findall(float_pattern, field_value.replace(",", "")))
        # 去除脏数据，加入字典
        if not (field_key == "" or field_value == []):
            word_articulation_dict[field_key] = field_value
    # print(list(word_articulation_dict.items())[:10])
    print("提取文本校验内容完毕...")
    return word_articulation_dict


def check_word_chart(path, word_dict, chart_dict, match_list, inverted_list):
    doc = fitz.open(path)
    error_dict = {"字段匹配错误": [], "文表勾稽正确": [], "勾稽关系错误": [], "未找到合适匹配项": []}
    for matches in match_list:
        txt_num_list = word_dict[matches[0]]
        chart_num_list = chart_dict[matches[1]]
        if matches[2] >= 90:
            # print(matches[0], "----", matches[1], "----得分：", matches[2])
            # 勾稽校验
            check_result = equal_check(txt_num_list, chart_num_list)
            # 存储，样例：('报告期内公司的研发费用', [1230.59, 2223.38], '研发费用',[1230.59, 2223.38], 90)
            error_dict[check_result].append((matches[0], txt_num_list, matches[1], chart_num_list, matches[2]))
            if check_result != "字段匹配错误":  # 只对正确匹配到内容的字段进行定位
                # 在文本中定位内容
                txt_json = locate_txt_info(doc, matches[0])
                # 在表格中定位内容
                chart_json = locate_chart_info(doc, inverted_list, matches[1])
        else:
            error_dict["未找到合适匹配项"].append((matches[0], txt_num_list, matches[1], chart_num_list, matches[2]))
    doc.save("C:\\Users\\chxue\\Desktop\\招股说明书_景杰生物--高亮.pdf")

    # 输出勾稽校验结果及案例
    print("汇总：")
    for error_type, error_ele in error_dict.items():
        print(error_type, "数目：{}".format(len(error_ele)))
        print(*error_ele[:10], sep="\n")
        print()
    return error_dict


def locate_chart_info(doc, inverted_list, field):
    json_result = {}
    table_names = inverted_list[field]  # 获得表名，建立在字段只对应一个表格的前提下，不然会报错
    for table_name in table_names:
        try:
            # 从表名中提取页码
            chart_start = int(table_name[:-5].split("_")[0].split("-")[0])
            chart_end = int(table_name[:-5].split("_")[-1].split("-")[0])

            for page_num in range(chart_start, chart_end+1):
                page = doc[page_num]
                field_locs = page.search_for(field)  # 位置四元组
                for field_loc in field_locs:
                    bbox = fitz.Rect(field_loc[0], field_loc[1], field_loc[2], field_loc[3])
                    page.add_highlight_annot(bbox)  # highlight
        except:
            print("定位表格失败")
    return json_result


def locate_txt_info(doc, field):  # TODO:还需要文本的页码，在extract_unverified_text中做
    json_result = {}
    return json_result


if __name__ == "__main__":
    path = "预披露 景杰生物 2022-12-02  1-1 招股说明书_景杰生物.pdf"
    field_data, inverted_list = get_all_field()
    field_dict = extract_unverified_text(path)
    best_matches = match_strings(list(field_dict.keys()), list(field_data.keys()))
    print("挖掘到总文表勾稽{}处".format(len(best_matches)))
    print(best_matches[:15])
    report = check_word_chart(path, field_dict, field_data, best_matches, inverted_list)

"""
1、仅判断了以“分别为”作为关键字的文表勾稽，内容能对应上的很少，大概30-40处  -->extract_unverified_text函数中，再想1-2处关键字，一定要通用，可以是三大财务报表的一些必要描述
2、用编辑距离打分判断是否是同一字段可能会有误差  -->在match_strings函数中改进语义匹配方法（不必要）
3、对于field_data（即合并所有字段的json_data2）有多个value值的项，也无法判定用哪个值
4、检测不出单位错误、逆序错误、以及全部数据都错误  -->针对文本中的“万元”和表格上方的”万元“进行识别匹配，找逆序和全部数据错误的例子 分析改进思路
"""
