import requests
from bs4 import BeautifulSoup

# 定义目标网页链接
base_url = "https://paimon.moe"
url = f"{base_url}/characters"

# 发送 GET 请求获取网页内容
response = requests.get(url)

# 使用 BeautifulSoup 解析网页内容
soup = BeautifulSoup(response.text, "html.parser")

# 找到所有可点击项的链接
# 这些链接通常包含在 <a> 标签中
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

# # 打印提取的完整网址列表
# for url in character_urls:
#     print(url)

# 遍历角色页面的URL列表
for url in character_urls:
    # 发送 GET 请求获取网页内容
    response = requests.get(url)
    # 使用 BeautifulSoup 解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 查找指定结构的标签
    div_main = soup.find("main")
    div_container = div_main.find("div", class_=["lg:ml-64", "pt-20", "lg:pt-8", "svelte-ti79zj"])
    div_row = div_container.find("div", class_=["flex", "svelte-ti79zj"])
    div_col = div_row.find("div", class_=["flex", "flex-col", "xl:flex-row", "items-start", "max-w-screen-2xl", "w-full", "md:w-[calc(100%-1rem)]", "svelte-ti79zj"])
    div_content = div_col.find("div", class_=["flex", "flex-col", "items-start", "mt-4", "xl:mt-0", "flex-1", "side-detail", "pt-4", "xl:pt-0", "min-w-0", "max-w-full", "svelte-ti79zj"])
    div_chara = div_content.find("div", class_=["flex", "items-center", "px-4", "md:px-8", "svelte-ti79zj"])

    # # 提取文字内容
    h1_text = div_chara.find("h1").text.strip()

    # 提取 img 标签的 src 属性
    img_src = div_chara.find("img")["src"]

    # div_wea = div_content.find("div", class_=["text-legendary-from", "px-4", "md:px-8", "text-2xl", "flex", "items-center", "z-0", "-mt-2", "md:-mt-4", "svelte-ti79zj"])
    # # 提取 svg 标签的数量
    # 可恶，竟然使用js，不过反正也不是重要信息，以后需要的话再重构就好了
    # svg_count = len(div_wea.find("svg"))

    # 有些逆天，按理说我这里寻找的是角色简介，但是找到的却是武器类型
    text_intro = div_content.find("p", class_="text-base").text.strip()

    # 打印提取的内容
    print(f"网页链接: {url}")
    print(f"角色名称: {h1_text}")
    print(f"元素力图片链接: {img_src}")
    print(f"武器类型: {text_intro}")
    print("-" * 40)
