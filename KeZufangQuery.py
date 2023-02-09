# 爬取贝壳的租房信息

import json
import time
import xlwt
import os
import re

from pyquery import PyQuery as pq

# 每个地区获取的页数
PAGE_COUNT = 6

# 每次调用接口之后的时间间隔
SLEEP_TIME = 1

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
    i = 0

    dataItems = doc('.content__list--item[data-ad_code="0"]')
    for item in dataItems.items():
        # 标题
        title = item.find(".content__list--item--aside").attr("title")
        # 小区
        neighborhood = item.find(".content__list--item--des a").text().replace(" ", "/")

        itemDesc = item.find(".content__list--item--des").text().split("/")
        # 大小
        size = float(re.search(r"\d+(.)\d+", itemDesc[1]).group())
        # 户型
        room_type = itemDesc[3].strip()
        # 租金
        rant = item.find(".content__list--item-price > em").text()

        yield {
            "title": title,
            "neighborhood": neighborhood,
            "size": size,
            "room_type": room_type,
            "rant": int(rant),
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
    # print(result)
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
    house_data = []

    for city in CITY_AND_AREA:
        for area in city["areas"]:
            for i in range(PAGE_COUNT):
                # url拼接
                realUrl = area["href"] + "pg" + str(i + 1)
                realUrl += "ab200301001000"  # 限制为链家房源
                realUrl += "rt200600000001"  # 限制为整租
                realUrl += "/"

                houses = startGetData(realUrl)
                for house in houses:
                    # print(house)
                    # continue

                    house_data.append(
                        {
                            "city": city["name"],
                            "area": area["text"],
                            "size": house["size"],
                            "neighborhood": house["neighborhood"],
                            "room_type": house["room_type"],
                            "rant": house["rant"],
                        }
                    )
                # 增加延时，避免被 block
                time.sleep(SLEEP_TIME)

    excel_data = generate_excel_data(house_data)
    write_to_excel(excel_data)
    print("complete")
