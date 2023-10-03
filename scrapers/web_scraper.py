import traceback

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 写在前面，虽然我最后应该（确信）会做代码混淆加密处理，但是gay_hub的仓库肯定是开源的
# 本程序，不管是app还是python原版，均不收费，仅为个人业余开发，无收益
# 仓库地址：https://github.com/gbc-star/genshin_characters/tree/master
# 数据来源和引用（排名不分先后）：
# https://paimon.moe
# https://sites.google.com/chromium.org/driver/

# 创建Chrome WebDriver实例并启用无界面模式
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 启用无界面模式
driver = webdriver.Chrome(options=chrome_options)

# 定义目标网页链接
base_url = "https://paimon.moe"
url = f"{base_url}/characters"

# 发送 GET 请求获取网页内容
driver.get(url)

# 使用 BeautifulSoup 解析网页内容
soup = BeautifulSoup(driver.page_source, "html.parser")

# 获取所有a标签（角色可点击部分）
character_links = soup.find_all("a")

# 创建一个空列表来存储提取的完整网址
character_urls = []

# 遍历所有链接
for link in character_links:
    # 获取链接的 href 属性
    href = link.get("href")
    # 检查链接是否以 "/characters/" 开头
    if href and href.startswith("/characters/"):
        # 生成完整的网址并将其添加到列表中
        full_url = f"{base_url}{href}"
        character_urls.append(full_url)
        # print(character_urls)

for url in character_urls:
    try:
        # 发送 GET 请求获取网页内容
        response = requests.get(url)
        # 使用 BeautifulSoup 解析网页内容
        soup = BeautifulSoup(response.text, "html.parser")
        # body->div->main可找的最小层
        div_main = soup.find("main")
        # main下嵌套一层div
        # 此div下分为五大div和多个作为空格的div
        div_container = div_main.find("div", class_=["lg:ml-64"])

        # 五大div按顺序分别为：
        #   角色基本信息+突破材料信息div_1
        #   角色推荐出装div_2
        #   战斗天赋相关信息div_3
        #   固有天赋相关信息div_4
        #   命座相关信息div_5

        # 下面五行按顺序执行五大div查找
        div_1 = div_container.find("div", class_=["flex"])
        # div_2 = div_container.find_all("div", class_=["flex"])[14]
        # div_3 = div_container.find_all("div", class_=["flex"])[48]
        # div_4 = div_container.find_all("div", class_=["flex"])[55]
        # div_5 = div_container.find_all("div", class_=["flex"])[64]

        # 寻找第一div相关信息div_1

        # 这层就是包含立绘的最后一层了
        div_1_1 = div_1.find("div", class_=["flex-col"])

        # 立绘图片链接，全部例为：https://paimon.moe/images/characters/full/albedo.png
        div_lihui = div_1_1.find("img")["src"]

        # 这层是不包含立绘的最后一层
        div_content = div_1_1.find("div", class_=["mt-4"])

        # 往下开始逐层提取
        # 角色名称和元素力图片层
        div_chara = div_content.find("div", class_=["items-center"])
        # 提取角色名称
        h1_text = div_chara.find("h1").text.strip()
        # 提取 img 标签的 src 属性,元素力图片链接，全部例为：https://paimon.moe/images/elements/geo.png
        img_src = div_chara.find("img")["src"]

        # 太逆天了，鬼知道什么问题，常规层找不到数据但是可以在上层找到（p_weapon），武器类型和角色星级
        # 承接上个注释，见下面一大段，实际上是我严重错误理解了
        # 提取武器类型
        div_weapon = div_content.find("div", class_=["text-2xl"])
        p_weapon = div_weapon.find("p", class_="text-base").text.strip()
        # 提取角色星级
        star_tags = div_weapon.find_all("svg")
        svg_count = len(star_tags)-1

        # p_weapon = div_content.find("p", class_="text-base").text.strip()
        # 保留着这部分吧，也算是值得纪念的经历了，实际上我错误的理解了一个问题：
        # beautiful soup的这个find方法，class里面可以添加多个属性（["","",""]）
        # 我之前一直以为，比如一个标签有12345属性，那么我find如果写12345就会精准找到这个标签
        # 但实际上这个是找到其中一个，比如我find12345，返回的就是第一个包含这五个之一的标签
        # 这也就导致什么问题呢，已知有两个div，class"1" "2" "3"和class"2" "3" "4"
        # 如果我find234，找到的不会是第二个标签而是第一个，这里我是严重错误理解的

        # 提取角色简介
        p_intro_text = div_content.find("p", class_="text-gray-200").text.strip()

        # 提取天赋书链接和周本材料链接
        # 例子为：https://paimon.moe/images/items/teachings_of_ballad.png
        # https://paimon.moe/images/items/tusk_of_monoceros_caeli.png
        div_gift = div_content.find("div", class_="space-y-4")
        # 上div层包含两个同级div且class完全相同，分别为天赋书＋周本材料（sub1）//突破材料（sub2）
        div_gift_sub1 = div_gift.find("div", class_="text-gray-200")
        div_gift_sub2 = div_gift.find_all("div", class_="text-gray-200")[1]
        # 寻找sub1相关信息
        div_gift_sub1_sub1 = div_gift_sub1.find("div", class_="mr-4")
        div_gift_sub1_sub2 = div_gift_sub1.find_all("div", class_="svelte-ti79zj")[3]
        # 跳层，直接找到天赋书图片链接和名称
        pic_gift = div_gift_sub1_sub1.find("img")["src"]
        text_gift = div_gift_sub1_sub1.find("p", class_="mb-1").text.strip()
        # 跳层，直接找到周本图片链接
        pic_weekly = div_gift_sub1_sub2.find("img")["src"]
        # 寻找sub2相关信息
        tupo_1 = div_gift_sub2.find_all("img")[0]["src"]
        tupo_2 = div_gift_sub2.find_all("img")[1]["src"]
        tupo_3 = div_gift_sub2.find_all("img")[2]["src"]
        tupo_4 = div_gift_sub2.find_all("img")[3]["src"]

        # 提取突破材料详细数据信息
        div_exa_intro = div_content.find("div", class_="md:ml-4")
        div_exa_intro_sub = div_exa_intro.find("div", class_="px-4")
        div_exa_intro_sub_sub = div_exa_intro_sub.find("div", class_="table")
        div_table = div_exa_intro_sub_sub.find("table", class_="text-gray-200")

        div_table_col_1 = div_table.find_all("tr", class_="svelte-ti79zj")[0]
        div_table_col_1_row_1 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_1_row_2 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_1_row_3 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_1_row_4 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_1_row_5 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_1_row_6 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_1_row_7 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_1_row_8 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_1_row_9 = div_table_col_1.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_1_row_9 = div_table_col_1_row_8
            div_table_col_1_row_8 = None

        div_table_col_2 = div_table.find_all("tr", class_="svelte-ti79zj")[1]
        div_table_col_2_row_1 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_2_row_2 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_2_row_3 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_2_row_4 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_2_row_5 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_2_row_6 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_2_row_7 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_2_row_8 = div_table_col_2.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        if div_table_col_2_row_8 is not None:
            div_table_col_2_row_8 = div_table_col_2_row_8
        else:
            div_table_col_2_row_8 = div_table_col_1_row_7
            div_table_col_1_row_7 = None

        div_table_col_3 = div_table.find_all("tr", class_="svelte-ti79zj")[2]
        div_table_col_3_row_1 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_3_row_2 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_3_row_3 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_3_row_4 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_3_row_5 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_3_row_6 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        try:
            div_table_col_3_row_7 = div_table_col_3.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        except IndexError:
            div_table_col_3_row_7 = div_table_col_3_row_6
            div_table_col_3_row_6 = None

        div_table_col_4 = div_table.find_all("tr", class_="svelte-ti79zj")[3]
        div_table_col_4_row_1 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_4_row_2 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_4_row_3 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_4_row_4 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_4_row_5 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_4_row_6 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_4_row_7 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_4_row_8 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_4_row_9 = div_table_col_4.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_4_row_9 = div_table_col_1_row_8
            div_table_col_4_row_8 = None
        div_table_col_4_row_9_sub = div_table_col_4_row_9.find("span", class_="w-max")
        div_table_col_4_row_9_sub_sub_1 = div_table_col_4_row_9_sub.find_all("span", class_="mr-2")[0]
        div_table_col_4_row_9_sub_sub_2 = div_table_col_4_row_9_sub.find_all("span", class_="mr-2")[1]
        div_table_col_4_row_9_sub_sub_3 = div_table_col_4_row_9_sub.find_all("span", class_="mr-2")[2]
        div_table_col_4_row_9_sub_sub_4 = div_table_col_4_row_9_sub.find("span", class_="pt-1")
        pic_tupo_a_1 = div_table_col_4_row_9_sub_sub_1.find("img")["src"]
        num_tupo_a_1 = div_table_col_4_row_9_sub_sub_1.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_a_2 = div_table_col_4_row_9_sub_sub_2.find("img")["src"]
        num_tupo_a_2 = div_table_col_4_row_9_sub_sub_2.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_a_3 = div_table_col_4_row_9_sub_sub_3.find("img")["src"]
        num_tupo_a_3 = div_table_col_4_row_9_sub_sub_3.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_a_4 = div_table_col_4_row_9_sub_sub_4.find("img")["src"]
        num_tupo_a_4 = div_table_col_4_row_9_sub_sub_4.find_all("span", class_="svelte-ti79zj")[0].text.strip()

        div_table_col_5 = div_table.find_all("tr", class_="svelte-ti79zj")[4]
        div_table_col_5_row_1 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_5_row_2 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_5_row_3 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_5_row_4 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_5_row_5 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_5_row_6 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_5_row_7 = div_table_col_5.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        if div_table_col_5_row_7 is not None:
            div_table_col_5_row_7 = div_table_col_5_row_7
        else:
            div_table_col_5_row_7 = div_table_col_5_row_6
            div_table_col_5_row_6 = None

        div_table_col_6 = div_table.find_all("tr", class_="svelte-ti79zj")[5]
        div_table_col_6_row_1 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_6_row_2 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_6_row_3 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_6_row_4 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_6_row_5 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_6_row_6 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_6_row_7 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_6_row_8 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_6_row_9 = div_table_col_6.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_6_row_9 = div_table_col_6_row_8
            div_table_col_6_row_8 = None
        div_table_col_6_row_9_sub = div_table_col_6_row_9.find("span", class_="w-max")
        div_table_col_6_row_9_sub_sub_1 = div_table_col_6_row_9_sub.find_all("span", class_="mr-2")[0]
        div_table_col_6_row_9_sub_sub_2 = div_table_col_6_row_9_sub.find_all("span", class_="mr-2")[1]
        div_table_col_6_row_9_sub_sub_3 = div_table_col_6_row_9_sub.find_all("span", class_="mr-2")[2]
        div_table_col_6_row_9_sub_sub_4 = div_table_col_6_row_9_sub.find_all("span", class_="mr-2")[3]
        div_table_col_6_row_9_sub_sub_5 = div_table_col_6_row_9_sub.find("span", class_="pt-1")
        pic_tupo_b_1 = div_table_col_6_row_9_sub_sub_1.find("img")["src"]
        num_tupo_b_1 = div_table_col_6_row_9_sub_sub_1.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_b_2 = div_table_col_6_row_9_sub_sub_2.find("img")["src"]
        num_tupo_b_2 = div_table_col_6_row_9_sub_sub_2.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_b_3 = div_table_col_6_row_9_sub_sub_3.find("img")["src"]
        num_tupo_b_3 = div_table_col_6_row_9_sub_sub_3.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_b_4 = div_table_col_6_row_9_sub_sub_4.find("img")["src"]
        num_tupo_b_4 = div_table_col_6_row_9_sub_sub_4.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_b_5 = div_table_col_6_row_9_sub_sub_5.find("img")["src"]
        num_tupo_b_5 = div_table_col_6_row_9_sub_sub_5.find_all("span", class_="svelte-ti79zj")[0].text.strip()

        div_table_col_7 = div_table.find_all("tr", class_="svelte-ti79zj")[6]
        div_table_col_7_row_1 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_7_row_2 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_7_row_3 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_7_row_4 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_7_row_5 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_7_row_6 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_7_row_7 = div_table_col_7.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        if div_table_col_7_row_7 is not None:
            div_table_col_7_row_7 = div_table_col_7_row_7
        else:
            div_table_col_7_row_7 = div_table_col_7_row_6
            div_table_col_7_row_6 = None

        div_table_col_8 = div_table.find_all("tr", class_="svelte-ti79zj")[7]
        div_table_col_8_row_1 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_8_row_2 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_8_row_3 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_8_row_4 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_8_row_5 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_8_row_6 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_8_row_7 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_8_row_8 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_8_row_9 = div_table_col_8.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_8_row_9 = div_table_col_8_row_8
            div_table_col_8_row_8 = None
        div_table_col_8_row_9_sub = div_table_col_8_row_9.find("span", class_="w-max")
        div_table_col_8_row_9_sub_sub_1 = div_table_col_8_row_9_sub.find_all("span", class_="mr-2")[0]
        div_table_col_8_row_9_sub_sub_2 = div_table_col_8_row_9_sub.find_all("span", class_="mr-2")[1]
        div_table_col_8_row_9_sub_sub_3 = div_table_col_8_row_9_sub.find_all("span", class_="mr-2")[2]
        div_table_col_8_row_9_sub_sub_4 = div_table_col_8_row_9_sub.find_all("span", class_="mr-2")[3]
        div_table_col_8_row_9_sub_sub_5 = div_table_col_8_row_9_sub.find("span", class_="pt-1")
        pic_tupo_c_1 = div_table_col_8_row_9_sub_sub_1.find("img")["src"]
        num_tupo_c_1 = div_table_col_8_row_9_sub_sub_1.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_c_2 = div_table_col_8_row_9_sub_sub_2.find("img")["src"]
        num_tupo_c_2 = div_table_col_8_row_9_sub_sub_2.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_c_3 = div_table_col_8_row_9_sub_sub_3.find("img")["src"]
        num_tupo_c_3 = div_table_col_8_row_9_sub_sub_3.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_c_4 = div_table_col_8_row_9_sub_sub_4.find("img")["src"]
        num_tupo_c_4 = div_table_col_8_row_9_sub_sub_4.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_c_5 = div_table_col_8_row_9_sub_sub_5.find("img")["src"]
        num_tupo_c_5 = div_table_col_8_row_9_sub_sub_5.find_all("span", class_="svelte-ti79zj")[0].text.strip()

        div_table_col_9 = div_table.find_all("tr", class_="svelte-ti79zj")[8]
        div_table_col_9_row_1 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_9_row_2 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_9_row_3 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_9_row_4 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_9_row_5 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_9_row_6 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_9_row_7 = div_table_col_9.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        if div_table_col_9_row_7 is not None:
            div_table_col_9_row_7 = div_table_col_9_row_7
        else:
            div_table_col_9_row_7 = div_table_col_9_row_6
            div_table_col_9_row_6 = None

        div_table_col_10 = div_table.find_all("tr", class_="svelte-ti79zj")[9]
        div_table_col_10_row_1 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_10_row_2 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_10_row_3 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_10_row_4 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_10_row_5 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_10_row_6 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_10_row_7 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_10_row_8 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_10_row_9 = div_table_col_10.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_10_row_9 = div_table_col_10_row_8
            div_table_col_10_row_8 = None
        div_table_col_10_row_9_sub = div_table_col_10_row_9.find("span", class_="w-max")
        div_table_col_10_row_9_sub_sub_1 = div_table_col_10_row_9_sub.find_all("span", class_="mr-2")[0]
        div_table_col_10_row_9_sub_sub_2 = div_table_col_10_row_9_sub.find_all("span", class_="mr-2")[1]
        div_table_col_10_row_9_sub_sub_3 = div_table_col_10_row_9_sub.find_all("span", class_="mr-2")[2]
        div_table_col_10_row_9_sub_sub_4 = div_table_col_10_row_9_sub.find_all("span", class_="mr-2")[3]
        div_table_col_10_row_9_sub_sub_5 = div_table_col_10_row_9_sub.find("span", class_="pt-1")
        pic_tupo_d_1 = div_table_col_10_row_9_sub_sub_1.find("img")["src"]
        num_tupo_d_1 = div_table_col_10_row_9_sub_sub_1.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_d_2 = div_table_col_10_row_9_sub_sub_2.find("img")["src"]
        num_tupo_d_2 = div_table_col_10_row_9_sub_sub_2.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_d_3 = div_table_col_10_row_9_sub_sub_3.find("img")["src"]
        num_tupo_d_3 = div_table_col_10_row_9_sub_sub_3.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_d_4 = div_table_col_10_row_9_sub_sub_4.find("img")["src"]
        num_tupo_d_4 = div_table_col_10_row_9_sub_sub_4.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_d_5 = div_table_col_10_row_9_sub_sub_5.find("img")["src"]
        num_tupo_d_5 = div_table_col_10_row_9_sub_sub_5.find_all("span", class_="svelte-ti79zj")[0].text.strip()

        div_table_col_11 = div_table.find_all("tr", class_="svelte-ti79zj")[10]
        div_table_col_11_row_1 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_11_row_2 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_11_row_3 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_11_row_4 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_11_row_5 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_11_row_6 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_11_row_7 = div_table_col_11.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        if div_table_col_11_row_7 is not None:
            div_table_col_11_row_7 = div_table_col_11_row_7
        else:
            div_table_col_11_row_7 = div_table_col_11_row_6
            div_table_col_11_row_6 = None

        div_table_col_12 = div_table.find_all("tr", class_="svelte-ti79zj")[11]
        div_table_col_12_row_1 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_12_row_2 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_12_row_3 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_12_row_4 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_12_row_5 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_12_row_6 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_12_row_7 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_12_row_8 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_12_row_9 = div_table_col_12.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_12_row_9 = div_table_col_12_row_8
            div_table_col_12_row_8 = None
        div_table_col_12_row_9_sub = div_table_col_12_row_9.find("span", class_="w-max")
        div_table_col_12_row_9_sub_sub_1 = div_table_col_12_row_9_sub.find_all("span", class_="mr-2")[0]
        div_table_col_12_row_9_sub_sub_2 = div_table_col_12_row_9_sub.find_all("span", class_="mr-2")[1]
        div_table_col_12_row_9_sub_sub_3 = div_table_col_12_row_9_sub.find_all("span", class_="mr-2")[2]
        div_table_col_12_row_9_sub_sub_4 = div_table_col_12_row_9_sub.find_all("span", class_="mr-2")[3]
        div_table_col_12_row_9_sub_sub_5 = div_table_col_12_row_9_sub.find("span", class_="pt-1")
        pic_tupo_e_1 = div_table_col_12_row_9_sub_sub_1.find("img")["src"]
        num_tupo_e_1 = div_table_col_12_row_9_sub_sub_1.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_e_2 = div_table_col_12_row_9_sub_sub_2.find("img")["src"]
        num_tupo_e_2 = div_table_col_12_row_9_sub_sub_2.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_e_3 = div_table_col_12_row_9_sub_sub_3.find("img")["src"]
        num_tupo_e_3 = div_table_col_12_row_9_sub_sub_3.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_e_4 = div_table_col_12_row_9_sub_sub_4.find("img")["src"]
        num_tupo_e_4 = div_table_col_12_row_9_sub_sub_4.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_e_5 = div_table_col_12_row_9_sub_sub_5.find("img")["src"]
        num_tupo_e_5 = div_table_col_12_row_9_sub_sub_5.find_all("span", class_="svelte-ti79zj")[0].text.strip()

        div_table_col_13 = div_table.find_all("tr", class_="svelte-ti79zj")[12]
        div_table_col_13_row_1 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_13_row_2 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_13_row_3 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_13_row_4 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_13_row_5 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_13_row_6 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_13_row_7 = div_table_col_13.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        if div_table_col_13_row_7 is not None:
            div_table_col_13_row_7 = div_table_col_13_row_7
        else:
            div_table_col_13_row_7 = div_table_col_13_row_6
            div_table_col_13_row_6 = None

        div_table_col_14 = div_table.find_all("tr", class_="svelte-ti79zj")[13]
        div_table_col_14_row_1 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_14_row_2 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_14_row_3 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_14_row_4 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_14_row_5 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_14_row_6 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_14_row_7 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        div_table_col_14_row_8 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[7].text.strip()
        try:
            div_table_col_14_row_9 = div_table_col_14.find_all("td", class_="svelte-ti79zj")[8]
        except IndexError:
            div_table_col_14_row_9 = div_table_col_14_row_8
            div_table_col_14_row_8 = None
        div_table_col_14_row_9_sub = div_table_col_14_row_9.find("span", class_="w-max")
        div_table_col_14_row_9_sub_sub_1 = div_table_col_14_row_9_sub.find_all("span", class_="mr-2")[0]
        div_table_col_14_row_9_sub_sub_2 = div_table_col_14_row_9_sub.find_all("span", class_="mr-2")[1]
        div_table_col_14_row_9_sub_sub_3 = div_table_col_14_row_9_sub.find_all("span", class_="mr-2")[2]
        div_table_col_14_row_9_sub_sub_4 = div_table_col_14_row_9_sub.find_all("span", class_="mr-2")[3]
        div_table_col_14_row_9_sub_sub_5 = div_table_col_14_row_9_sub.find("span", class_="pt-1")
        pic_tupo_f_1 = div_table_col_14_row_9_sub_sub_1.find("img")["src"]
        num_tupo_f_1 = div_table_col_14_row_9_sub_sub_1.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_f_2 = div_table_col_14_row_9_sub_sub_2.find("img")["src"]
        num_tupo_f_2 = div_table_col_14_row_9_sub_sub_2.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_f_3 = div_table_col_14_row_9_sub_sub_3.find("img")["src"]
        num_tupo_f_3 = div_table_col_14_row_9_sub_sub_3.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_f_4 = div_table_col_14_row_9_sub_sub_4.find("img")["src"]
        num_tupo_f_4 = div_table_col_14_row_9_sub_sub_4.find_all("span", class_="svelte-ti79zj")[1].text.strip()
        pic_tupo_f_5 = div_table_col_14_row_9_sub_sub_5.find("img")["src"]
        num_tupo_f_5 = div_table_col_14_row_9_sub_sub_5.find_all("span", class_="svelte-ti79zj")[0].text.strip()

        div_table_col_15 = div_table.find_all("tr", class_="svelte-ti79zj")[14]
        div_table_col_15_row_1 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[0].text.strip()
        div_table_col_15_row_2 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[1].text.strip()
        div_table_col_15_row_3 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[2].text.strip()
        div_table_col_15_row_4 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[3].text.strip()
        div_table_col_15_row_5 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[4].text.strip()
        div_table_col_15_row_6 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[5].text.strip()
        div_table_col_15_row_7 = div_table_col_15.find_all("td", class_="svelte-ti79zj")[6].text.strip()
        if div_table_col_15_row_7 is not None:
            div_table_col_15_row_7 = div_table_col_15_row_7
        else:
            div_table_col_15_row_7 = div_table_col_15_row_6
            div_table_col_15_row_6 = None

        # 数据清洗
        data_dict = {
            "网址": url,
            "角色名称": h1_text,
            "立绘链接": "https://paimon.moe" + div_lihui,
            "元素力图片链接": "https://paimon.moe" + img_src,
            "武器类型": p_weapon,
            "角色星级": svg_count,
            "角色简介": p_intro_text,
            "天赋书图片链接": "https://paimon.moe" + pic_gift,
            "天赋书名称": text_gift,
            "周本图片链接": "https://paimon.moe" + pic_weekly,
            "突破材料链接1": "https://paimon.moe" + tupo_1,
            "突破材料链接2": "https://paimon.moe" + tupo_2,
            "突破材料链接3": "https://paimon.moe" + tupo_3,
            "突破材料链接4": "https://paimon.moe" + tupo_4,

            "表格表头：突破次数": div_table_col_1_row_1,
            "表格表头：等级": div_table_col_1_row_2,
            "表格表头：生命值": div_table_col_1_row_3,
            "表格表头：攻击力": div_table_col_1_row_4,
            "表格表头：防御力": div_table_col_1_row_5,
            "表格表头：暴击率": div_table_col_1_row_6,
            "表格表头：暴击伤害": div_table_col_1_row_7,
            "表格表头：元素伤害加成": div_table_col_1_row_8,
            "表格表头：突破所需材料": div_table_col_1_row_9,

            "第一行数据：突破次数": div_table_col_2_row_1,
            "第一行数据：等级": div_table_col_2_row_2,
            "第一行数据：生命值": div_table_col_2_row_3,
            "第一行数据：攻击力": div_table_col_2_row_4,
            "第一行数据：防御力": div_table_col_2_row_5,
            "第一行数据：暴击率": div_table_col_2_row_6,
            "第一行数据：暴击伤害": div_table_col_2_row_7,
            "第一行数据：元素伤害加成": div_table_col_2_row_8,
            "第一行数据：突破所需材料": "null",

            "第二行数据：突破次数": "null",
            "第二行数据：等级": div_table_col_3_row_1,
            "第二行数据：生命值": div_table_col_3_row_2,
            "第二行数据：攻击力": div_table_col_3_row_3,
            "第二行数据：防御力": div_table_col_3_row_4,
            "第二行数据：暴击率": div_table_col_3_row_5,
            "第二行数据：暴击伤害": div_table_col_3_row_6,
            "第二行数据：元素伤害加成": div_table_col_3_row_7,
            "第二行数据：突破所需材料": "null",

            "第三行数据：突破次数": div_table_col_4_row_1,
            "第三行数据：等级": div_table_col_4_row_2,
            "第三行数据：生命值": div_table_col_4_row_3,
            "第三行数据：攻击力": div_table_col_4_row_4,
            "第三行数据：防御力": div_table_col_4_row_5,
            "第三行数据：暴击率": div_table_col_4_row_6,
            "第三行数据：暴击伤害": div_table_col_4_row_7,
            "第三行数据：元素伤害加成": div_table_col_4_row_8,
            "第三行数据：突破所需材料": {
                "晶石": {
                    "图片链接": "https://paimon.moe" + pic_tupo_a_1,
                    "所需数量": num_tupo_a_1
                },
                "小boss": {
                    "图片链接": "null",
                    "所需数量": "null",
                },
                "世界素材": {
                    "图片链接": "https://paimon.moe" + pic_tupo_a_2,
                    "所需数量": num_tupo_a_2
                },
                "小怪掉落": {
                    "图片链接": "https://paimon.moe" + pic_tupo_a_3,
                    "所需数量": num_tupo_a_3
                },
                "摩拉": {
                    "图片链接": "https://paimon.moe" + pic_tupo_a_4,
                    "所需数量": num_tupo_a_4
                }
            },

            "第四行数据：突破次数": "null",
            "第四行数据：等级": div_table_col_5_row_1,
            "第四行数据：生命值": div_table_col_5_row_2,
            "第四行数据：攻击力": div_table_col_5_row_3,
            "第四行数据：防御力": div_table_col_5_row_4,
            "第四行数据：暴击率": div_table_col_5_row_5,
            "第四行数据：暴击伤害": div_table_col_5_row_6,
            "第四行数据：元素伤害加成": div_table_col_5_row_7,
            "第四行数据：突破所需材料": "null",

            "第五行数据：突破次数": div_table_col_6_row_1,
            "第五行数据：等级": div_table_col_6_row_2,
            "第五行数据：生命值": div_table_col_6_row_3,
            "第五行数据：攻击力": div_table_col_6_row_4,
            "第五行数据：防御力": div_table_col_6_row_5,
            "第五行数据：暴击率": div_table_col_6_row_6,
            "第五行数据：暴击伤害": div_table_col_6_row_7,
            "第五行数据：元素伤害加成": div_table_col_6_row_8,
            "第五行数据：突破所需材料": {
                "晶石": {
                    "图片链接": "https://paimon.moe" + pic_tupo_b_1,
                    "所需数量": num_tupo_b_1
                },
                "小boss": {
                    "图片链接": "https://paimon.moe" + pic_tupo_b_2,
                    "所需数量": num_tupo_b_2
                },
                "世界素材": {
                    "图片链接": "https://paimon.moe" + pic_tupo_b_3,
                    "所需数量": num_tupo_b_3
                },
                "小怪掉落": {
                    "图片链接": "https://paimon.moe" + pic_tupo_b_4,
                    "所需数量": num_tupo_b_4
                },
                "摩拉": {
                    "图片链接": "https://paimon.moe" + pic_tupo_b_5,
                    "所需数量": num_tupo_b_5
                }
            },

            "第六行数据：突破次数": "null",
            "第六行数据：等级": div_table_col_7_row_1,
            "第六行数据：生命值": div_table_col_7_row_2,
            "第六行数据：攻击力": div_table_col_7_row_3,
            "第六行数据：防御力": div_table_col_7_row_4,
            "第六行数据：暴击率": div_table_col_7_row_5,
            "第六行数据：暴击伤害": div_table_col_7_row_6,
            "第六行数据：元素伤害加成": div_table_col_7_row_7,
            "第六行数据：突破所需材料": "null",

            "第七行数据：突破次数": div_table_col_8_row_1,
            "第七行数据：等级": div_table_col_8_row_2,
            "第七行数据：生命值": div_table_col_8_row_3,
            "第七行数据：攻击力": div_table_col_8_row_4,
            "第七行数据：防御力": div_table_col_8_row_5,
            "第七行数据：暴击率": div_table_col_8_row_6,
            "第七行数据：暴击伤害": div_table_col_8_row_7,
            "第七行数据：元素伤害加成": div_table_col_8_row_8,
            "第七行数据：突破所需材料": {
                "晶石": {
                    "图片链接": "https://paimon.moe" + pic_tupo_c_1,
                    "所需数量": num_tupo_c_1
                },
                "小boss": {
                    "图片链接": "https://paimon.moe" + pic_tupo_c_2,
                    "所需数量": num_tupo_c_2
                },
                "世界素材": {
                    "图片链接": "https://paimon.moe" + pic_tupo_c_3,
                    "所需数量": num_tupo_c_3
                },
                "小怪掉落": {
                    "图片链接": "https://paimon.moe" + pic_tupo_c_4,
                    "所需数量": num_tupo_c_4
                },
                "摩拉": {
                    "图片链接": "https://paimon.moe" + pic_tupo_c_5,
                    "所需数量": num_tupo_c_5
                }
            },

            "第八行数据：突破次数": "null",
            "第八行数据：等级": div_table_col_9_row_1,
            "第八行数据：生命值": div_table_col_9_row_2,
            "第八行数据：攻击力": div_table_col_9_row_3,
            "第八行数据：防御力": div_table_col_9_row_4,
            "第八行数据：暴击率": div_table_col_9_row_5,
            "第八行数据：暴击伤害": div_table_col_9_row_6,
            "第八行数据：元素伤害加成": div_table_col_9_row_7,
            "第八行数据：突破所需材料": "null",

            "第九行数据：突破次数": div_table_col_10_row_1,
            "第九行数据：等级": div_table_col_10_row_2,
            "第九行数据：生命值": div_table_col_10_row_3,
            "第九行数据：攻击力": div_table_col_10_row_4,
            "第九行数据：防御力": div_table_col_10_row_5,
            "第九行数据：暴击率": div_table_col_10_row_6,
            "第九行数据：暴击伤害": div_table_col_10_row_7,
            "第九行数据：元素伤害加成": div_table_col_10_row_8,
            "第九行数据：突破所需材料": {
                "晶石": {
                    "图片链接": "https://paimon.moe" + pic_tupo_d_1,
                    "所需数量": num_tupo_d_1
                },
                "小boss": {
                    "图片链接": "https://paimon.moe" + pic_tupo_d_2,
                    "所需数量": num_tupo_d_2
                },
                "世界素材": {
                    "图片链接": "https://paimon.moe" + pic_tupo_d_3,
                    "所需数量": num_tupo_d_3
                },
                "小怪掉落": {
                    "图片链接": "https://paimon.moe" + pic_tupo_d_4,
                    "所需数量": num_tupo_d_4
                },
                "摩拉": {
                    "图片链接": "https://paimon.moe" + pic_tupo_d_5,
                    "所需数量": num_tupo_d_5
                }
            },

            "第十行数据：突破次数": "null",
            "第十行数据：等级": div_table_col_11_row_1,
            "第十行数据：生命值": div_table_col_11_row_2,
            "第十行数据：攻击力": div_table_col_11_row_3,
            "第十行数据：防御力": div_table_col_11_row_4,
            "第十行数据：暴击率": div_table_col_11_row_5,
            "第十行数据：暴击伤害": div_table_col_11_row_6,
            "第十行数据：元素伤害加成": div_table_col_11_row_7,
            "第十行数据：突破所需材料": "null",

            "第十一行数据：突破次数": div_table_col_12_row_1,
            "第十一行数据：等级": div_table_col_12_row_2,
            "第十一行数据：生命值": div_table_col_12_row_3,
            "第十一行数据：攻击力": div_table_col_12_row_4,
            "第十一行数据：防御力": div_table_col_12_row_5,
            "第十一行数据：暴击率": div_table_col_12_row_6,
            "第十一行数据：暴击伤害": div_table_col_12_row_7,
            "第十一行数据：元素伤害加成": div_table_col_12_row_8,
            "第十一行数据：突破所需材料": {
                "晶石": {
                    "图片链接": "https://paimon.moe" + pic_tupo_e_1,
                    "所需数量": num_tupo_e_1
                },
                "小boss": {
                    "图片链接": "https://paimon.moe" + pic_tupo_e_2,
                    "所需数量": num_tupo_e_2
                },
                "世界素材": {
                    "图片链接": "https://paimon.moe" + pic_tupo_e_3,
                    "所需数量": num_tupo_e_3
                },
                "小怪掉落": {
                    "图片链接": "https://paimon.moe" + pic_tupo_e_4,
                    "所需数量": num_tupo_e_4
                },
                "摩拉": {
                    "图片链接": "https://paimon.moe" + pic_tupo_e_5,
                    "所需数量": num_tupo_e_5
                }
            },

            "第十二行数据：突破次数": "null",
            "第十二行数据：等级": div_table_col_13_row_1,
            "第十二行数据：生命值": div_table_col_13_row_2,
            "第十二行数据：攻击力": div_table_col_13_row_3,
            "第十二行数据：防御力": div_table_col_13_row_4,
            "第十二行数据：暴击率": div_table_col_13_row_5,
            "第十二行数据：暴击伤害": div_table_col_13_row_6,
            "第十二行数据：元素伤害加成": div_table_col_13_row_7,
            "第十二行数据：突破所需材料": "null",

            "第十三行数据：突破次数": div_table_col_14_row_1,
            "第十三行数据：等级": div_table_col_14_row_2,
            "第十三行数据：生命值": div_table_col_14_row_3,
            "第十三行数据：攻击力": div_table_col_14_row_4,
            "第十三行数据：防御力": div_table_col_14_row_5,
            "第十三行数据：暴击率": div_table_col_14_row_6,
            "第十三行数据：暴击伤害": div_table_col_14_row_7,
            "第十三行数据：元素伤害加成": div_table_col_14_row_8,
            "第十三行数据：突破所需材料": {
                "晶石": {
                    "图片链接": "https://paimon.moe" + pic_tupo_f_1,
                    "所需数量": num_tupo_f_1
                },
                "小boss": {
                    "图片链接": "https://paimon.moe" + pic_tupo_f_2,
                    "所需数量": num_tupo_f_2
                },
                "世界素材": {
                    "图片链接": "https://paimon.moe" + pic_tupo_f_3,
                    "所需数量": num_tupo_f_3
                },
                "小怪掉落": {
                    "图片链接": "https://paimon.moe" + pic_tupo_f_4,
                    "所需数量": num_tupo_f_4
                },
                "摩拉": {
                    "图片链接": "https://paimon.moe" + pic_tupo_f_5,
                    "所需数量": num_tupo_f_5
                }
            },

            "第十四行数据：突破次数": "null",
            "第十四行数据：等级": div_table_col_15_row_1,
            "第十四行数据：生命值": div_table_col_15_row_2,
            "第十四行数据：攻击力": div_table_col_15_row_3,
            "第十四行数据：防御力": div_table_col_15_row_4,
            "第十四行数据：暴击率": div_table_col_15_row_5,
            "第十四行数据：暴击伤害": div_table_col_15_row_6,
            "第十四行数据：元素伤害加成": div_table_col_15_row_7,
            "第十四行数据：突破所需材料": "null",
        }

        print(data_dict)

    except requests.exceptions.RequestException as e:
        print(f"发生请求错误: {e}")
        traceback.print_exc()  # 打印异常信息，包括行数
    except AttributeError as e:
        print(f"发生属性错误: {e}")
        traceback.print_exc()  # 打印异常信息，包括行数
    print("-" * 40)

# 关闭浏览器
driver.quit()



