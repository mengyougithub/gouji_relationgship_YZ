# pythonProject
 
一开始用的是招股书节选，即‘测试’，后来扩展到招股书所有表格（坏数据较多），后面又尝试了超级pdf转换的表格（仅转换了200页后的纯度较高的pdf）

两份py文件，一个是处理xk师兄代码提取的表格，一个是处理超级pdf转换的表格，两种表格格式不一样，一种全部是字符串，另一种包含了excel单元格的格式
所以data2json不太一样，另外有一些对改进逻辑也在*2文件中试验，所以*2中可能存在一些额外的改进（bug）