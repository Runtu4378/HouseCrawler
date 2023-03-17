# 爬取贝壳的租房信息

import json
import time
import xlwt
import os
import re

import config
import utils

from pyquery import PyQuery as pq


def startGetData(url, cityConfig):
    # print("[start] " + url)

    result = []
    doc = pq(url=url)
    i = 0

    dataItems = doc('.content__list--item[data-ad_code="0"]')
    for item in dataItems.items():
        # 房屋编号
        code = item.attr("data-house_code")
        # 详情链接
        href = cityConfig["origin"] + item.find(".content__list--item--aside").attr(
            "href"
        )
        # 标题
        title = item.find(".content__list--item--aside").attr("title")
        # 小区
        neighborhood = item.find(".content__list--item--des a").text().replace(" ", "/")

        itemDesc = item.find(".content__list--item--des").text()
        # 大小
        size = float(re.search("\d{1,}(\.\d{1,}){0,1}(?=㎡)", itemDesc).group())
        # 户型
        try:
            room_type = re.search("\S+\d+卫", itemDesc).group()
        except Exception as e:
            print("[户型字段]: %s" % itemDesc)
            print("[户型字段] 无法匹配: %s" % e)
            raise e
        # 租金
        rant = item.find(".content__list--item-price > em").text()

        result.append(
            {
                "code": code,
                "title": title,
                "neighborhood": neighborhood,
                "size": size,
                "room_type": room_type,
                "rant": int(rant),
                "href": href,
            }
        )
        i += 1

    # print("[finished]\n")
    return result


def write_to_file(content):
    with open("chengjiao.txt", "r", encoding="utf-8") as f:
        f.write(json.dumps(content, ensure_ascii=False) + ",\n")


# 读取缓存
def readTemp():
    result = []
    try:
        f = open(config.TEMP_PATH, "r", encoding="utf-8")
    except FileNotFoundError as e:
        return

    lines = f.readlines()
    if len(lines) == 0:
        f.close()
        os.remove(config.TEMP_PATH)
        return

    result.append(lines[0].strip("\n"))
    result.append(json.loads(lines[1]))

    f.close()
    os.remove(config.TEMP_PATH)
    return result


# 保存缓存
def saveTemp(currentUrl, data):
    with open(config.TEMP_PATH, "a", encoding="utf-8") as f:
        f.write(currentUrl)
        f.write("\n")
        f.write(json.dumps(data, ensure_ascii=False))
        f.close()
    print("end at: " + currentUrl)
    print("already save temp")


# 生成 excel 需要的数据格式
def generate_excel_data(houses):
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
                house["href"],
            ]
        )

    result = list(zip(config.EXCEL_HEADER_CONFIG, *data_array))
    # print(result)
    return result


# 将数据写入excel
def write_to_excel(excel_data):
    # 异常捕获
    try:
        work_book = xlwt.Workbook(encoding="utf-8", style_compression=2)
        sheet = work_book.add_sheet("data")

        x = 0
        y = 0
        for column in excel_data:
            headerText = column[0]
            for cell in column:
                if headerText == "房源链接" and x != 0:
                    sheet.write(
                        x,
                        y,
                        xlwt.Formula('HYPERLINK("' + cell + '";"' + cell + '")'),
                        xlwt.easyxf("font: colour_index 4, underline True"),
                    )
                else:
                    sheet.write(x, y, cell)
                x += 1
            y += 1
            x = 0

        work_book.save(config.EXCEL_PATH)
    except Exception as e:
        print(e)


def calcAreaNumber(list):
    sum = 0

    for city in list:
        for area in city["areas"]:
            sum += 1

    return sum


def filter_list(list_data, exclude_cities):
    """
    根据 exclude_cities 列表中的元素过滤 list_data 中的元素
    :param list_data: 元祖列表
    :param exclude_cities: 排除城市名称列表
    :return: 过滤后的元祖列表
    """
    return [item for item in list_data if item["name"] not in exclude_cities]


if __name__ == "__main__":
    extraConfig = None

    if os.path.exists(config.CONFIG_PATH):
        extraConfig = utils.readLocalConfig(config.CONFIG_PATH)

    print("[config check] start")
    print("  当前版本: %s\n" % config.VERSION)
    print("  当前运行路径                CWD: %s" % config.CWD)
    print("  断点续传文件路径      TEMP_PATH: %s" % config.TEMP_PATH)
    print("  生成的excel文件路径  EXCEL_PATH: %s" % config.EXCEL_PATH)
    if extraConfig:
        print("  要过滤的城市列表               : %s" % extraConfig["excludeCity"] or "无")
    print("[config check] end\n")

    ifLocalTest = False

    if ifLocalTest:
        testArea = config.CITY_AND_AREA[0]
        test = startGetData(
            "https://bj.zu.ke.com/zufang/dongcheng/pg1ab200301001000rt200600000001/",
            testArea,
        )

        for index in range(len(test)):
            test[index]["city"] = testArea["name"]
            test[index]["area"] = "东城"

        print(test)
        excel_data = generate_excel_data(test)
        write_to_excel(excel_data)
        print("complete")
        exit()

    try:
        cityList = config.CITY_AND_AREA
        if extraConfig["excludeCity"]:
            cityList = filter_list(config.CITY_AND_AREA, extraConfig["excludeCity"])

        fullDataSum = calcAreaNumber(cityList)
        processedDataIndex = 0

        timerStart, timerEnd = utils.timer()
        timerStart()

        house_data = []
        realUrlPrev = ""

        tempUrl = ""

        temp = readTemp()
        if temp:
            print("get temp")
            tempUrl = temp[0]
            house_data = temp[1]

        utils.progressBar(0)

        for city in cityList:
            for area in city["areas"]:
                for i in range(config.PAGE_COUNT):
                    # url拼接
                    realUrl = area["href"] + "pg" + str(i + 1)
                    realUrl += "ab200301001000"  # 限制为链家房源
                    realUrl += "rt200600000001"  # 限制为整租
                    realUrl += "/"
                    if i == 0:
                        realUrlPrev = realUrl

                    if tempUrl != "" and realUrl != tempUrl:
                        # print("[skip] " + realUrl + "\n")
                        continue
                    elif realUrl == tempUrl:
                        tempUrl = ""

                    houses = startGetData(realUrl, city)
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
                                "href": house["href"],
                            }
                        )

                    realUrlPrev = realUrl
                    # 增加延时，避免被 block
                    time.sleep(config.SLEEP_TIME)

                processedDataIndex += 1
                utils.progressBar(float(processedDataIndex / fullDataSum))

        # 数组去重
        # TODO

        excel_data = generate_excel_data(house_data)
        write_to_excel(excel_data)
        elapsedTime = timerEnd()
        elapsedTimeText = utils.formatSeconds(elapsedTime, "HH时 mm分 ss秒")

        print("\n")
        print("总耗时：%s" % elapsedTimeText)
        print("执行完成，请手动关闭程序")
        input("Press Enter to exit...")
    except Exception as e:
        print("meet error: %s" % e)

        # 启用断档续传功能
        saveTemp(realUrlPrev, house_data)
