# lab2-crawler

大数据采集与处理 · 实验2「网页解析」实验代码。

使用 **requests** 获取网页 HTML 源码，用 **BeautifulSoup（lxml 解析器）** 结合 **CSS 选择器**
提取结构化数据，最后用 **csv** 模块保存为 CSV 文件。

## 目录结构

```
lab2-crawler/
├── README.md              项目说明与运行方法
├── requirements.txt       第三方库清单
├── case1_gaosan.py        案例1：中国大学排名爬取存储（教材 4.2 节 P73）
├── case2_baidunews.py     案例2：百度新闻爬取（教材 4.3 节 P77）
├── .gitignore
└── output/
    ├── school.csv         案例1 抓取结果（820 条高校数据）
    └── news.csv           案例2 抓取结果（10 条新闻）
```

## 环境要求

- Python 3.8 及以上（开发环境 Python 3.13.9）
- requests 2.32.5
- beautifulsoup4 4.13.5
- lxml 5.3.0

安装依赖：

```bash
pip install -r requirements.txt
```

## 案例1：中国大学排名爬取存储

- 目标网页：<http://www.bspider.top/gaosan/>
- 抓取字段：学校名称、总分、全国排名、星级排名、办学层次
- 输出文件：`output/school.csv`

```bash
python case1_gaosan.py
```

实现要点：

1. `get_html()`：`requests.get()` 发送 GET 请求，`raise_for_status()` 检查状态码，
   `resp.encoding = resp.apparent_encoding` 修正编码，`try…except` 捕获网络异常并重试；
2. `parser()`：先用 CSS 选择器 `table > tbody > tr` 取到全部 821 行，
   再在每行内 `row.select("td")` 二次查找单元格，跳过第一行表头；
3. `save_csv()`：`csv.writer()` 写入，`open(newline="")` 防止空行，
   `encoding="utf-8-sig"` 保证 Excel 打开中文不乱码。

运行结果：共解析出 820 条高校排名数据（1 行表头 + 820 行数据）。

## 案例2：百度新闻爬取

- 目标网页：<http://www.bspider.top/baidunews/>
- 抓取字段：序号、新闻栏目、新闻标题、详情页链接
- 输出文件：`output/news.csv`

```bash
python case2_baidunews.py
```

实现要点：

1. 热点新闻：CSS 选择器 `div.hotnews li`；
2. 焦点新闻：`ul.focuslistnews` 在页面中重复出现 20 次，只取第一个 ul，避免重复抓取；
3. 每个 li 内二次查找 `a[href]`，跳过 `href="#"` 的占位链接，只取第一个有效链接；
4. `clean_text()` 用正则把换行、连续空格和 `\xa0` 合并成一个空格；
5. 按链接去重后保存为 CSV。

运行结果：共解析出 10 条新闻数据（4 条热点新闻 + 6 条焦点新闻）。

## 说明

- 目标网页为教学用静态页面，数据仅用于课程实验。
- 部分新闻 li 的链接为 `#`（真实地址由前端 JavaScript 动态生成），静态解析无法获取，
  程序已自动跳过，说明见实验报告「五、未解决的问题」。
