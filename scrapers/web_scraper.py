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
chrome_options.add_argument("--headless")  # 启用无界面模式
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
        div_main = soup.find("main")
        div_container = div_main.find("div", class_=["lg:ml-64"])
        div_row = div_container.find("div", class_=["flex"])

        # 这层就是包含立绘的最后一层了
        div_col = div_row.find("div", class_=["flex-col"])

        # 立绘图片链接，全部例为：https://paimon.moe/images/characters/full/albedo.png
        div_lihui = div_col.find("img")["src"]

        # 这层是不包含立绘的最后一层
        div_content = div_col.find("div", class_=["mt-4"])

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

        # 提取天赋书链接和周本材料链接，
        # 例子为：https://paimon.moe/images/items/teachings_of_ballad.png
        # https: // paimon.moe / images / items / tusk_of_monoceros_caeli.png
        div_gift = div_content.find("div", class_="space-y-4")
        # 跳了几层，没必要抽丝剥茧
        div_sub_gift = div_gift.find("div", class_="mr-2")
        pic_gift = div_sub_gift.find("img")["src"]

        # 打印提取的内容
        print(f"网页链接: {url}")
        print(f"角色名称: {h1_text}")
        print(f"立绘链接：{div_lihui}")
        print(f"元素力图片链接: {img_src}")
        print(f"武器类型: {p_weapon}")
        print(f"星级：{svg_count}")
        print(f"角色介绍:{p_intro_text}")
        print(f"天赋书图片链接:{pic_gift}")

    except requests.exceptions.RequestException as e:
        print(f"发生请求错误: {e}")
        traceback.print_exc()  # 打印异常信息，包括行数
    except AttributeError as e:
        print(f"发生属性错误: {e}")
        traceback.print_exc()  # 打印异常信息，包括行数
    print("-" * 40)

# 关闭浏览器
driver.quit()



