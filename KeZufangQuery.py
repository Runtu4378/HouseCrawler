# 爬取贝壳的租房信息

import json
import time
import xlwt
import os

from pyquery import PyQuery as pq

# 每个地区获取的页数
PAGE_COUNT = 1

# 保存的文件名
EXCEL_NAME = "数据表.xls"

# 获取各区域的首页链接
# 上海：https://sh.zu.ke.com/zufang
# 获取区域枚举的js语句
# #filter > ul[data-target="area"] 的第一个元素
# [...document.querySelector('#filter > ul[data-target="area"]').querySelectorAll('li a').values()].map(i => ({ href: i.href, text: i.innerText })).filter(i => i.text !== '不限')

# 城市和地区的映射
CITY_AND_AREA = [
    {
        "key": "SHANGHAI",
        "name": "上海",
        "areas": [
            {"href": "https://sh.zu.ke.com/zufang/jingan/", "text": "静安"},
            {"href": "https://sh.zu.ke.com/zufang/xuhui/", "text": "徐汇"},
            {"href": "https://sh.zu.ke.com/zufang/huangpu/", "text": "黄浦"},
            {"href": "https://sh.zu.ke.com/zufang/changning/", "text": "长宁"},
            {"href": "https://sh.zu.ke.com/zufang/putuo/", "text": "普陀"},
            {"href": "https://sh.zu.ke.com/zufang/pudong/", "text": "浦东"},
            {"href": "https://sh.zu.ke.com/zufang/baoshan/", "text": "宝山"},
            {"href": "https://sh.zu.ke.com/zufang/hongkou/", "text": "虹口"},
            {"href": "https://sh.zu.ke.com/zufang/yangpu/", "text": "杨浦"},
            {"href": "https://sh.zu.ke.com/zufang/minhang/", "text": "闵行"},
            {"href": "https://sh.zu.ke.com/zufang/jinshan/", "text": "金山"},
            {"href": "https://sh.zu.ke.com/zufang/jiading/", "text": "嘉定"},
            {"href": "https://sh.zu.ke.com/zufang/chongming/", "text": "崇明"},
            {"href": "https://sh.zu.ke.com/zufang/fengxian/", "text": "奉贤"},
            {"href": "https://sh.zu.ke.com/zufang/songjiang/", "text": "松江"},
            {"href": "https://sh.zu.ke.com/zufang/qingpu/", "text": "青浦"},
        ],
    }
]


def startGetData(url):
    print(url)
    doc = pq(url=url)

    titles = doc('.content__list--item[data-ad_code="0"] .content__list--item--aside')
    titleList = []
    hrefList = []
    for item in titles.items():
        titleList.append(item.attr("title"))
        hrefList.append("https://sh.zu.ke.com" + item.attr("href"))

    imgs = doc('.content__list--item[data-ad_code="0"] .content__list--item--aside img')
    imgList = []
    for item in imgs.items():
        img = item.attr("data-src")
        imgList.append(img)

    locations = doc(".content__list--item--des")
    locationList = []
    for item in locations.items():
        locationList.append(item.text().strip())

    unitPrices = doc(".content__list--item-price")
    unitPriceList = []
    for item in unitPrices.items():
        unitPriceList.append(item.text().strip())

    timeInfos = doc(".content__list--item--time.oneline")
    timeInfoList = []
    for item in timeInfos.items():
        timeInfoList.append(item.text().strip())

    tags = doc(".content__list--item--bottom.oneline")
    tagList = []
    for item in tags.items():
        tagList.append(item.text().strip())

    i = 0
    for item in imgList:
        yield {
            "title": titleList[i],  # 标题
            "unitPrice": unitPriceList[i],  # 租金
            "location": locationList[i],  # 地址
            "time": timeInfoList[i],  # 发布时间
            "tag": tagList[i],  # 标签
            "href": hrefList[i],  # 跳转链接
            "image": imgList[i],  # 图片
        }
        i += 1


def write_to_file(content):
    with open("chengjiao.txt", "a", encoding="utf-8") as f:
        f.write(json.dumps(content, ensure_ascii=False) + ",\n")


# 生成 excel 需要的数据格式
def generate_excel_data(houses):
    header_array = ["城市", "行政区", "面积", "小区名称", "户型", "租金"]
    data_array = []

    for house in houses:
        data_array.append(
            [
                house["city"],
                house["area"],
                house["size"],
                house["neighborhood"],
                house["room_type"],
                house["rant"],
            ]
        )

    result = list(zip(header_array, *data_array))
    print(result)
    return result


# 将数据写入excel
def write_to_excel(excel_data):
    # 异常捕获
    try:
        work_book = xlwt.Workbook(encoding="utf-8")
        sheet = work_book.add_sheet("data")

        x = 0
        y = 0
        for column in excel_data:
            for cell in column:
                sheet.write(x, y, cell)
                x += 1
            y += 1
            x = 0

        file_path = os.path.dirname(os.path.realpath(__file__))
        work_book.save(file_path + "/" + EXCEL_NAME)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    for city in CITY_AND_AREA:
        for area in city["areas"]:
            for i in range(PAGE_COUNT):
                write_to_file("---" + area["text"] + "---")
                realUrl = area["href"] + "pg" + str(i + 1) + "/"
                houses = startGetData(realUrl)
                for house in houses:
                    write_to_file(house)
                # 增加延时，避免被 block
                time.sleep(1)
    print("complete")
