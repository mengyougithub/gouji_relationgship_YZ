# -*- coding: utf-8 -*-
# Date       ：2023/2/17
# Author     ：Chen Xuekai
# Description：
# -*- coding: utf-8 -*-
# Date       ：2023/2/9
# Author     ：Chen Xuekai
# Description：

import pdfplumber
import difflib
import re
import json
import fitz
import time
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
            return "正确"
        # 若序列或逆序有一个能部分匹配，则为勾稽错误，TODO：可能存在两列表不相关，但序列/逆序有重合的情况
        elif unequal_num(list1, list2) != len(list1) or unequal_num(list1, list2[::-1]) != len(list1):
            return "错误"
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
        field_key = re.split(punctuation, all_text[:target.start()])[-1].replace("\n", "")
        # 提取“分别为”后面数字列表作为值  TODO：解决带万元问题
        field_value = re.split(punctuation, all_text[target.end():])[0].replace("\n", "")
        # 提取整句话，便于定位
        sentence = field_key + "分别为" + field_value
        # 格式规范化，数字化为列表形式
        field_key, field_value = field_key.strip(), field_value.strip()
        field_value = to_float_list(re.findall(float_pattern, field_value.replace(",", "")))
        # 去除脏数据，加入字典
        if not (field_key == "" or field_value == []):
            word_articulation_dict[field_key] = {"数字列表": field_value, "整句话": sentence}
    # print(list(word_articulation_dict.items())[:10])
    print("提取文本校验内容完毕...")
    return word_articulation_dict


def check_word_chart(path, output_pdf, output_json_path, word_dict, chart_dict, match_list, inverted_list):
    doc = fitz.open(path)
    pdf = pdfplumber.open(path)
    output_list = []
    error_dict = {"正确": [], "错误": [], "未找到合适匹配项": [], "字段匹配错误": []}
    for matches in match_list:
        txt_num_list = word_dict[matches[0]]["数字列表"]
        chart_num_list = chart_dict[matches[1]]
        if matches[2] >= 80:
            # 勾稽校验
            check_result = equal_check(txt_num_list, chart_num_list)
            # 存储，样例：('报告期内公司的研发费用', [1230.59, 2223.38], '研发费用',[1230.59, 2223.38], 90)
            error_dict[check_result].append((matches[0], txt_num_list, matches[1], chart_num_list, matches[2]))
            if check_result != "字段匹配错误":  # 只对正确匹配到内容的字段进行定位
                output_item = {
                    "规则": matches[0] + " = " + matches[1],
                    "名称": check_result
                }
                # 在文本中定位内容
                sentence = word_dict[matches[0]]["整句话"]
                text_location = locate_txt_info(pdf, doc, sentence)  # 元素为json的列表
                output_item["关联文本"] = {
                    "内容值": sentence,
                    "位置": text_location
                }
                # 在表格中定位内容
                chart_json_list = locate_chart_info(pdf, doc, inverted_list, matches[1], len(chart_num_list)+1)
                output_item["勾稽表"] = chart_json_list
                output_list.append(output_item)
        else:
            error_dict["未找到合适匹配项"].append((matches[0], txt_num_list, matches[1], chart_num_list, matches[2]))

    # 保存高亮后的pdf和输出的json结果
    doc.save(output_pdf)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, ensure_ascii=False)
    # 输出勾稽校验结果及案例
    print("汇总：")
    for error_type, error_ele in error_dict.items():
        print(error_type, "数目：{}".format(len(error_ele)))
        print(*error_ele[:10], sep="\n")
        print()
    return error_dict


# 给出文本，返回其在文档中的位置
def locate_txt_info(pdf, doc, sentence):
    result = []
    # 因为考虑到跨页问题，在抽取时合并了跨页内容，但定位时不能合并，只能从全部pdf页找整句话内容，此处可能可以优化
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = pdf.pages[page_num].extract_text().replace("\n", "")
        if re.findall(sentence, text):  # 首先确定字符肯定在当前页面中  TODO：如果文字段跨页就又不行了
            # 由于直接search会因为各种格式不一致问题而匹配不上，只能不断按最大长度切分匹配  TODO：出现短句转行问题（如公司\n税收优惠金额）
            head = 0
            tail = len(sentence)
            while head != tail:
                search_part = pdf.pages[page_num].search(sentence[head:tail])
                if search_part:  # 搜寻到部分字符串，将四元组加入位置列表
                    for out in search_part:
                        bbox = fitz.Rect(out['x0'], out['top'], out['x1'], out['bottom'])
                        page.add_highlight_annot(bbox)
                        location_tetrad = {
                            "x0": out['x0'],
                            "top": out['top'],
                            "x1": out['x1'],
                            "bottom": out['bottom']
                        }
                        result.append(location_tetrad)
                    head = tail
                    tail = len(sentence)
                    continue
                tail -= 1
    return result


# 给出字段信息，返回其在文档中的位置
def locate_chart_info(pdf, doc, inverted_list, field, col_num):
    # 行号列号？
    result_list = []
    table_names = inverted_list[field]  # 获得表名，可能有多个，因此返回列表形式
    for table_name in table_names:
        # 从表名中提取页码
        chart_start = int(table_name[:-5].split("_")[0].split("-")[0])
        chart_end = int(table_name[:-5].split("_")[-1].split("-")[0])
        # 在表格出现过的页码搜寻字段
        for page_num in range(chart_start, chart_end+1):
            # 遍历表格第一列所有行，若发现与目标field相同字段，则获取其行属性
            for table, table_attr in zip(pdf.pages[page_num].extract_tables(), pdf.pages[page_num].find_tables()):
                for row_num in range(len(table)):
                    # 锁定与校验表格列数相同的表，匹配字段时去除\n
                    if (table[row_num][0] is not None) and \
                            (col_num == len(table[row_num])) and (table[row_num][0].replace("\n", "") == field):
                        # 获取位置信息
                        row_loc = table_attr.rows[row_num].bbox
                        bbox = fitz.Rect(row_loc[0], row_loc[1], row_loc[2], row_loc[3])
                        doc[page_num].add_highlight_annot(bbox)  # highlight
                        location_tetrad = {
                            "x0": row_loc[0],
                            "top": row_loc[1],
                            "x1": row_loc[2],
                            "bottom": row_loc[3]
                        }
                        # 整合勾稽表输出
                        json_result = {
                            "表格编号": table_name[:-5],
                            "表格内容": table,
                            "字段位置": location_tetrad
                        }
                        result_list.append(json_result)
    return result_list


if __name__ == "__main__":
    start = time.time()
    path = "预披露 景杰生物 2022-12-02  1-1 招股说明书_景杰生物.pdf"
    highlight_pdf = "Articulation_out/text_highlight.pdf"
    output_file = "Articulation_out/output_text_articulation.json"
    chart_data, inverted_list = get_all_field()
    text_data = extract_unverified_text(path)
    best_matches = match_strings(list(text_data.keys()), list(chart_data.keys()))
    print("挖掘到总文表勾稽{}处".format(len(best_matches)))
    print(best_matches[:15])
    report = check_word_chart(path, highlight_pdf, output_file, text_data, chart_data, best_matches, inverted_list)
    print("文表勾稽关系校验完毕，用时：{:.2f}秒".format(time.time() - start))

"""
1、仅判断了以“分别为”作为关键字的文表勾稽，内容能对应上的很少，大概30-40处  -->extract_unverified_text函数中，再想1-2处关键字，一定要通用，可以是三大财务报表的一些必要描述
2、用编辑距离打分判断是否是同一字段可能会有误差  -->在match_strings函数中改进语义匹配方法（不必要）
3、对于field_data（即合并所有字段的json_data2）有多个value值的项，也无法判定用哪个值
4、检测不出单位错误、逆序错误、以及全部数据都错误  -->针对文本中的“万元”和表格上方的”万元“进行识别匹配，找逆序和全部数据错误的例子 分析改进思路
"""
