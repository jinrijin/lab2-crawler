# -*- coding: utf-8 -*-
"""
实验2 案例1：中国大学排名爬取存储（教材 4.2 节，P73）

目标网页：http://www.bspider.top/gaosan/
实现思路：requests 获取网页 HTML 源码 -> BeautifulSoup(lxml) 解析文档
          -> CSS 选择器二层查找（先定位 tr 行，再定位 td 单元格）
          -> 提取“学校名称、总分、全国排名、星级排名、办学层次”并写入 CSV

运行方式：python case1_gaosan.py
输出文件：output/school.csv
"""
import csv
import os
import time

import requests
from bs4 import BeautifulSoup

URL = "http://www.bspider.top/gaosan/"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
}
OUT_PATH = os.path.join("output", "school.csv")
HEADER = ["学校名称", "总分", "全国排名", "星级排名", "办学层次"]


def get_html(url, headers=None, timeout=10, retry=3):
    """GET 请求通用函数：发送请求、设置编码、检查状态码、捕获网络访问异常"""
    for i in range(1, retry + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            # 返回的状态码不等于 200 时抛出 HTTPError 异常
            resp.raise_for_status()
            # 目标网页声明为 utf-8，这里用 apparent_encoding 让 requests 自动识别真实编码，
            # 避免中文学校名称出现乱码
            resp.encoding = resp.apparent_encoding
            return resp.text
        except requests.RequestException as err:
            print(f"[第 {i} 次请求失败] {err}")
            if i < retry:
                time.sleep(2)
    print("[请求失败] 已达到最大重试次数，返回空结果")
    return None


def parser(html):
    """解析函数：从网页 HTML 中提取排名数据，返回二维列表"""
    out_list = []
    if not html:
        return out_list

    soup = BeautifulSoup(html, "lxml")          # HTML 字符串转换为 soup 对象
    rows = soup.select("table > tbody > tr")    # 第一次查找：CSS 选择器定位全部数据行
    print(f"CSS 选择器 table>tbody>tr 共匹配到 {len(rows)} 行")

    for row in rows:
        # 第二次查找：在行 row 内部再查找 td 单元格
        td_html = row.select("td")
        if len(td_html) < 6:                     # 结构不完整的行直接跳过
            continue
        if not td_html[0].get_text(strip=True).isdigit():
            continue                            # 跳过第一行表头（名次、学校名称……）

        row_data = [
            td_html[1].get_text(strip=True),     # 学校名称
            td_html[2].get_text(strip=True),     # 总分
            td_html[3].get_text(strip=True),     # 全国排名
            td_html[4].get_text(strip=True),     # 星级排名
            td_html[5].get_text(strip=True),     # 办学层次
        ]
        out_list.append(row_data)                # 每行数据以列表类型追加到输出列表
    return out_list


def save_csv(item, path, header=None):
    """数据存储函数：把二维列表写入 CSV 文件

    newline="" 用于避免 Windows 平台下每行之间多出一个空行；
    encoding="utf-8-sig" 带 BOM，Excel 双击打开时能正确识别中文。
    """
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv_write = csv.writer(f)
        if header:
            csv_write.writerow(header)
        csv_write.writerows(item)


def main():
    html = get_html(URL, HEADERS)                # 第一步：网页数据获取
    if html is None:
        print("网页获取失败，程序结束")
        return
    print(f"网页源码长度：{len(html)} 个字符")

    out_list = parser(html)                      # 第二步：网页解析
    print(f"共解析出 {len(out_list)} 条高校排名数据")
    print("前 5 条数据：")
    for data in out_list[:5]:
        print(data)

    save_csv(out_list, OUT_PATH, HEADER)         # 第三步：数据存储
    print(f"数据已保存到 {OUT_PATH}")


if __name__ == "__main__":
    main()
