# -*- coding: utf-8 -*-
"""
实验2 案例2：百度新闻爬取（教材 4.3 节，P77）

目标网页：http://www.bspider.top/baidunews/
实现思路：复用案例1 的三步流程（获取 -> 解析 -> 存储）
          网页“热点要闻”由两部分构成：
            1) 热点新闻：div.hotnews 下的 li 列表
            2) 焦点新闻：ul.focuslistnews 下的 li 列表
          逐个 li 提取“新闻标题 + 详情页链接”，保存为 CSV

运行方式：python case2_baidunews.py
输出文件：output/news.csv
"""
import csv
import os
import re
import time

import requests
from bs4 import BeautifulSoup

URL = "http://www.bspider.top/baidunews/"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
}
OUT_PATH = os.path.join("output", "news.csv")
HEADER = ["序号", "新闻栏目", "新闻标题", "详情页链接"]


def get_html(url, headers=None, timeout=10, retry=3):
    """GET 请求通用函数（与案例1 相同，封装成通用函数后可直接复用）"""
    for i in range(1, retry + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding
            return resp.text
        except requests.RequestException as err:
            print(f"[第 {i} 次请求失败] {err}")
            if i < retry:
                time.sleep(2)
    print("[请求失败] 已达到最大重试次数，返回空结果")
    return None


def clean_text(text):
    """清洗文本：把连续空白、换行、不间断空格 \\xa0 合并成一个空格"""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def parse_li_list(li_list, column):
    """解析一个 li 列表：每个 li 内二次查找 a[href]，取标题和详情页链接"""
    items = []
    for li in li_list:
        a_list = li.select("a[href]")
        if not a_list:
            continue

        # 一个 li 内可能有多个 a 标签（如“标题 + 血与心”两个链接），
        # 只取第一个“有效”链接：跳过 href="#" 的占位链接和空链接
        href, title = "", ""
        for a in a_list:
            link = (a.get("href") or "").strip()
            if link and link != "#":
                href = link
                title = clean_text(a.get_text())
                break
        if not href:
            continue
        if not title:
            title = clean_text(li.get_text())

        items.append([column, title, href])
    return items


def parser(html):
    """解析函数：分别解析“热点新闻”和“焦点新闻”两部分"""
    out_list = []
    if not html:
        return out_list

    soup = BeautifulSoup(html, "lxml")

    # 1) 热点新闻：div.hotnews 是唯一的容器
    hot_li = soup.select("div.hotnews li")
    print(f"CSS 选择器 div.hotnews li 匹配到 {len(hot_li)} 条热点新闻")

    # 2) 焦点新闻：ul.focuslistnews 在页面中重复出现了多次（页面按不同频道做了冗余拷贝），
    #    这里只取第一个 ul，避免把同一批新闻重复抓取多遍
    focus_ul = soup.select("ul.focuslistnews")
    print(f"CSS 选择器 ul.focuslistnews 匹配到 {len(focus_ul)} 个列表（页面存在冗余拷贝）")
    focus_li = focus_ul[0].select("li") if focus_ul else []
    print(f"取第一个 ul.focuslistnews 中的 {len(focus_li)} 条焦点新闻")

    out_list.extend(parse_li_list(hot_li, "热点新闻"))
    out_list.extend(parse_li_list(focus_li, "焦点新闻"))

    # 按链接去重，保证每条新闻只出现一次
    seen, result = set(), []
    for row in out_list:
        if row[2] in seen:
            continue
        seen.add(row[2])
        row.insert(0, len(result) + 1)
        result.append(row)
    return result


def save_csv(item, path, header=None):
    """数据存储函数：写入 CSV 文件（与案例1 相同）"""
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv_write = csv.writer(f)
        if header:
            csv_write.writerow(header)
        csv_write.writerows(item)


def main():
    html = get_html(URL, HEADERS)
    if html is None:
        print("网页获取失败，程序结束")
        return
    print(f"网页源码长度：{len(html)} 个字符")

    out_list = parser(html)
    print(f"共解析出 {len(out_list)} 条新闻数据")
    print("抓取结果：")
    for row in out_list:
        print(f"{row[0]:>2}  [{row[1]}] {row[2][:40]}")
        print(f"      {row[3]}")

    save_csv(out_list, OUT_PATH, HEADER)
    print(f"数据已保存到 {OUT_PATH}")


if __name__ == "__main__":
    main()
