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
SLEEP_TIME = 0.6

CWD = os.getcwd()

# 保存的文件名
EXCEL_NAME = "数据表.xls"

EXCEL_PATH = os.path.join(CWD, EXCEL_NAME)

# 获取各区域的首页链接
# 北京: https://bj.zu.ke.com/zufang
# 东莞: https://dg.zu.ke.com/zufang
# 佛山: https://fs.zu.ke.com/zufang
# 广州: https://gz.zu.ke.com/zufang
# 杭州: https://hz.zu.ke.com/zufang
# 深圳: https://sz.zu.ke.com/zufang
# 武汉: https://wh.zu.ke.com/zufang
# 中山: https://zs.zu.ke.com/zufang
# 珠海: https://zh.zu.ke.com/zufang
# 获取区域枚举的js语句
# #filter > ul[data-target="area"] 的第一个元素
# [...document.querySelector('#filter > ul[data-target="area"]').querySelectorAll('li a').values()].map(i => ({ href: i.href, text: i.innerText })).filter(i => i.text !== '不限')

# 城市和地区的映射
CITY_AND_AREA = [
    {
        "key": "bj",
        "name": "北京",
        "origin": "https://bj.zu.ke.com",
        "areas": [
            {"href": "https://bj.zu.ke.com/zufang/dongcheng/", "text": "东城"},
            {"href": "https://bj.zu.ke.com/zufang/xicheng/", "text": "西城"},
            {"href": "https://bj.zu.ke.com/zufang/chaoyang/", "text": "朝阳"},
            {"href": "https://bj.zu.ke.com/zufang/haidian/", "text": "海淀"},
            {"href": "https://bj.zu.ke.com/zufang/fengtai/", "text": "丰台"},
            {"href": "https://bj.zu.ke.com/zufang/shijingshan/", "text": "石景山"},
            {"href": "https://bj.zu.ke.com/zufang/tongzhou/", "text": "通州"},
            {"href": "https://bj.zu.ke.com/zufang/changping/", "text": "昌平"},
            {"href": "https://bj.zu.ke.com/zufang/daxing/", "text": "大兴"},
            {"href": "https://bj.zu.ke.com/zufang/yizhuangkaifaqu/", "text": "亦庄开发区"},
            {"href": "https://bj.zu.ke.com/zufang/shunyi/", "text": "顺义"},
            {"href": "https://bj.zu.ke.com/zufang/fangshan/", "text": "房山"},
            {"href": "https://bj.zu.ke.com/zufang/mentougou/", "text": "门头沟"},
            {"href": "https://bj.zu.ke.com/zufang/pinggu/", "text": "平谷"},
            {"href": "https://bj.zu.ke.com/zufang/huairou/", "text": "怀柔"},
            {"href": "https://bj.zu.ke.com/zufang/miyun/", "text": "密云"},
            {"href": "https://bj.zu.ke.com/zufang/yanqing/", "text": "延庆"},
        ],
    },
    {
        "key": "dg",
        "name": "东莞",
        "origin": "https://dg.zu.ke.com",
        "areas": [
            {"href": "https://dg.zu.ke.com/zufang/nanchengqu/", "text": "南城区"},
            {"href": "https://dg.zu.ke.com/zufang/dongchengqu/", "text": "东城区"},
            {"href": "https://dg.zu.ke.com/zufang/wanjiangqu/", "text": "万江区"},
            {"href": "https://dg.zu.ke.com/zufang/wanchengqu/", "text": "莞城区"},
            {"href": "https://dg.zu.ke.com/zufang/liaobuzhen1/", "text": "寮步镇"},
            {"href": "https://dg.zu.ke.com/zufang/humenzhen3/", "text": "虎门镇"},
            {"href": "https://dg.zu.ke.com/zufang/changanzhen1/", "text": "长安镇"},
            {
                "href": "https://dg.zu.ke.com/zufang/songshanhugaoxinqu/",
                "text": "松山湖高新区",
            },
            {"href": "https://dg.zu.ke.com/zufang/houjiezhen2/", "text": "厚街镇"},
            {"href": "https://dg.zu.ke.com/zufang/gaobuzhen1/", "text": "高埗镇"},
            {"href": "https://dg.zu.ke.com/zufang/daojiaozhen/", "text": "道滘镇"},
            {"href": "https://dg.zu.ke.com/zufang/hongmeizhen/", "text": "洪梅镇"},
            {"href": "https://dg.zu.ke.com/zufang/shatianzhen/", "text": "沙田镇"},
            {"href": "https://dg.zu.ke.com/zufang/dalingshanzhen1/", "text": "大岭山镇"},
            {"href": "https://dg.zu.ke.com/zufang/changpingzhen/", "text": "常平镇"},
            {"href": "https://dg.zu.ke.com/zufang/dalangzhen/", "text": "大朗镇"},
            {"href": "https://dg.zu.ke.com/zufang/zhangmutouzhen/", "text": "樟木头镇"},
            {"href": "https://dg.zu.ke.com/zufang/tangxiazhen/", "text": "塘厦镇"},
            {"href": "https://dg.zu.ke.com/zufang/qingxizhen/", "text": "清溪镇"},
            {"href": "https://dg.zu.ke.com/zufang/fenggangzhen/", "text": "凤岗镇"},
            {"href": "https://dg.zu.ke.com/zufang/henglizhen/", "text": "横沥镇"},
            {"href": "https://dg.zu.ke.com/zufang/dongkengzhen/", "text": "东坑镇"},
            {"href": "https://dg.zu.ke.com/zufang/qishizhen/", "text": "企石镇"},
            {"href": "https://dg.zu.ke.com/zufang/shipaizhen/", "text": "石排镇"},
            {"href": "https://dg.zu.ke.com/zufang/chashanzhen/", "text": "茶山镇"},
            {"href": "https://dg.zu.ke.com/zufang/machongzhen/", "text": "麻涌镇"},
            {"href": "https://dg.zu.ke.com/zufang/shilongzhen/", "text": "石龙镇"},
            {"href": "https://dg.zu.ke.com/zufang/shijiezhen1/", "text": "石碣镇"},
            {"href": "https://dg.zu.ke.com/zufang/qiaotouzhen/", "text": "桥头镇"},
            {"href": "https://dg.zu.ke.com/zufang/xiegangzhen/", "text": "谢岗镇"},
            {"href": "https://dg.zu.ke.com/zufang/huangjiangzhen/", "text": "黄江镇"},
            {"href": "https://dg.zu.ke.com/zufang/zhongtangzhen/", "text": "中堂镇"},
            {"href": "https://dg.zu.ke.com/zufang/wangniudunzhen/", "text": "望牛墩镇"},
        ],
    },
    {
        "key": "fs",
        "name": "佛山",
        "origin": "https://fs.zu.ke.com",
        "areas": [
            {"href": "https://fs.zu.ke.com/zufang/chancheng/", "text": "禅城"},
            {"href": "https://fs.zu.ke.com/zufang/nanhai/", "text": "南海"},
            {"href": "https://fs.zu.ke.com/zufang/shunde/", "text": "顺德"},
            {"href": "https://fs.zu.ke.com/zufang/sanshui1/", "text": "三水"},
            {"href": "https://fs.zu.ke.com/zufang/gaoming1/", "text": "高明"},
        ],
    },
    {
        "key": "gz",
        "name": "广州",
        "origin": "https://gz.zu.ke.com",
        "areas": [
            {"href": "https://gz.zu.ke.com/zufang/tianhe/", "text": "天河"},
            {"href": "https://gz.zu.ke.com/zufang/yuexiu/", "text": "越秀"},
            {"href": "https://gz.zu.ke.com/zufang/liwan/", "text": "荔湾"},
            {"href": "https://gz.zu.ke.com/zufang/haizhu/", "text": "海珠"},
            {"href": "https://gz.zu.ke.com/zufang/panyu/", "text": "番禺"},
            {"href": "https://gz.zu.ke.com/zufang/baiyun/", "text": "白云"},
            {"href": "https://gz.zu.ke.com/zufang/huangpugz/", "text": "黄埔"},
            {"href": "https://gz.zu.ke.com/zufang/conghua/", "text": "从化"},
            {"href": "https://gz.zu.ke.com/zufang/zengcheng/", "text": "增城"},
            {"href": "https://gz.zu.ke.com/zufang/huadou/", "text": "花都"},
            {"href": "https://gz.zu.ke.com/zufang/nansha/", "text": "南沙"},
        ],
    },
    {
        "key": "hz",
        "name": "杭州",
        "origin": "https://hz.zu.ke.com",
        "areas": [
            {"href": "https://hz.zu.ke.com/zufang/fuyang/", "text": "富阳"},
            {"href": "https://hz.zu.ke.com/zufang/jiande/", "text": "建德"},
            {"href": "https://hz.zu.ke.com/zufang/linan/", "text": "临安"},
            {"href": "https://hz.zu.ke.com/zufang/hainingshi/", "text": "海宁市"},
            {"href": "https://hz.zu.ke.com/zufang/linpingqu/", "text": "临平区"},
            {"href": "https://hz.zu.ke.com/zufang/qiantangqu/", "text": "钱塘区"},
            {"href": "https://hz.zu.ke.com/zufang/chunan1/", "text": "淳安"},
            {"href": "https://hz.zu.ke.com/zufang/tonglu1/", "text": "桐庐"},
            {"href": "https://hz.zu.ke.com/zufang/gongshu/", "text": "拱墅"},
            {"href": "https://hz.zu.ke.com/zufang/xiacheng/", "text": "下城"},
            {"href": "https://hz.zu.ke.com/zufang/xihu/", "text": "西湖"},
            {"href": "https://hz.zu.ke.com/zufang/binjiang/", "text": "滨江"},
            {"href": "https://hz.zu.ke.com/zufang/yuhang/", "text": "余杭"},
            {"href": "https://hz.zu.ke.com/zufang/xiaoshan/", "text": "萧山"},
            {"href": "https://hz.zu.ke.com/zufang/shangcheng/", "text": "上城"},
        ],
    },
    {
        "key": "sz",
        "name": "深圳",
        "origin": "https://sz.zu.ke.com",
        "areas": [
            {"href": "https://sz.zu.ke.com/zufang/luohuqu/", "text": "罗湖区"},
            {"href": "https://sz.zu.ke.com/zufang/futianqu/", "text": "福田区"},
            {"href": "https://sz.zu.ke.com/zufang/nanshanqu/", "text": "南山区"},
            {"href": "https://sz.zu.ke.com/zufang/yantianqu/", "text": "盐田区"},
            {"href": "https://sz.zu.ke.com/zufang/baoanqu/", "text": "宝安区"},
            {"href": "https://sz.zu.ke.com/zufang/longgangqu/", "text": "龙岗区"},
            {"href": "https://sz.zu.ke.com/zufang/longhuaqu/", "text": "龙华区"},
            {"href": "https://sz.zu.ke.com/zufang/guangmingqu/", "text": "光明区"},
            {"href": "https://sz.zu.ke.com/zufang/pingshanqu/", "text": "坪山区"},
            {"href": "https://sz.zu.ke.com/zufang/dapengxinqu/", "text": "大鹏新区"},
        ],
    },
    {
        "key": "wh",
        "name": "武汉",
        "origin": "https://wh.zu.ke.com",
        "areas": [
            {"href": "https://wh.zu.ke.com/zufang/jiangan/", "text": "江岸"},
            {"href": "https://wh.zu.ke.com/zufang/jianghan/", "text": "江汉"},
            {"href": "https://wh.zu.ke.com/zufang/qiaokou/", "text": "硚口"},
            {"href": "https://wh.zu.ke.com/zufang/dongxihu/", "text": "东西湖"},
            {"href": "https://wh.zu.ke.com/zufang/wuchang/", "text": "武昌"},
            {"href": "https://wh.zu.ke.com/zufang/qingshan/", "text": "青山"},
            {"href": "https://wh.zu.ke.com/zufang/hongshan/", "text": "洪山"},
            {"href": "https://wh.zu.ke.com/zufang/hanyang/", "text": "汉阳"},
            {"href": "https://wh.zu.ke.com/zufang/donghugaoxin/", "text": "东湖高新"},
            {"href": "https://wh.zu.ke.com/zufang/jiangxia/", "text": "江夏"},
            {"href": "https://wh.zu.ke.com/zufang/caidian/", "text": "蔡甸"},
            {"href": "https://wh.zu.ke.com/zufang/huangbei/", "text": "黄陂"},
            {"href": "https://wh.zu.ke.com/zufang/xinzhou/", "text": "新洲"},
            {"href": "https://wh.zu.ke.com/zufang/hannan/", "text": "汉南"},
            {"href": "https://wh.zu.ke.com/zufang/zhuankoukaifaqu/", "text": "沌口开发区"},
        ],
    },
    {
        "key": "zs",
        "name": "中山",
        "origin": "https://zs.zu.ke.com",
        "areas": [
            {"href": "https://zs.zu.ke.com/zufang/dongqu/", "text": "东区"},
            {"href": "https://zs.zu.ke.com/zufang/xiqu/", "text": "西区"},
            {"href": "https://zs.zu.ke.com/zufang/nanqu/", "text": "南区"},
            {"href": "https://zs.zu.ke.com/zufang/shiqiqu/", "text": "石岐区"},
            {"href": "https://zs.zu.ke.com/zufang/huoju/", "text": "火炬"},
            {"href": "https://zs.zu.ke.com/zufang/gangkouzhen/", "text": "港口镇"},
            {"href": "https://zs.zu.ke.com/zufang/shaxizhen/", "text": "沙溪镇"},
            {"href": "https://zs.zu.ke.com/zufang/wuguishan/", "text": "五桂山"},
            {"href": "https://zs.zu.ke.com/zufang/sanxiangzhen/", "text": "三乡镇"},
            {"href": "https://zs.zu.ke.com/zufang/henglanzhen/", "text": "横栏镇"},
            {"href": "https://zs.zu.ke.com/zufang/fushazhen/", "text": "阜沙镇"},
            {"href": "https://zs.zu.ke.com/zufang/shenwanzhen/", "text": "神湾镇"},
            {"href": "https://zs.zu.ke.com/zufang/minzhongzhen/", "text": "民众镇"},
            {"href": "https://zs.zu.ke.com/zufang/xiaolanzhen/", "text": "小榄镇"},
            {"href": "https://zs.zu.ke.com/zufang/banfuzhen/", "text": "板芙镇"},
            {"href": "https://zs.zu.ke.com/zufang/sanjiaozhen/", "text": "三角镇"},
            {"href": "https://zs.zu.ke.com/zufang/dayongzhen/", "text": "大涌镇"},
            {"href": "https://zs.zu.ke.com/zufang/tanzhouzhen/", "text": "坦洲镇"},
            {"href": "https://zs.zu.ke.com/zufang/guzhenzhen/", "text": "古镇镇"},
            {"href": "https://zs.zu.ke.com/zufang/nanlangzhen/", "text": "南朗镇"},
            {"href": "https://zs.zu.ke.com/zufang/nantouzhen/", "text": "南头镇"},
            {"href": "https://zs.zu.ke.com/zufang/dongshengzhen1/", "text": "东升镇"},
            {"href": "https://zs.zu.ke.com/zufang/dongfengzhen/", "text": "东凤镇"},
            {"href": "https://zs.zu.ke.com/zufang/huangpuzhen/", "text": "黄圃镇"},
        ],
    },
    {
        "key": "zh",
        "name": "珠海",
        "origin": "https://zh.zu.ke.com",
        "areas": [
            {"href": "https://zh.zu.ke.com/zufang/xiangzhouqu/", "text": "香洲区"},
            {"href": "https://zh.zu.ke.com/zufang/jinwanqu/", "text": "金湾区"},
            {"href": "https://zh.zu.ke.com/zufang/doumenqu/", "text": "斗门区"},
            {"href": "https://zh.zu.ke.com/zufang/gaoxinqu21/", "text": "高新区"},
            {"href": "https://zh.zu.ke.com/zufang/hengqinqu/", "text": "横琴区"},
        ],
    },
]

# 断档续传缓存路径
TEMP_PATH = os.path.join(CWD, ".temp")

EXCEL_HEADER_CONFIG = ["城市", "行政区", "面积", "小区名称", "户型", "租金", "房源链接"]


def startGetData(url, cityConfig):
    print("[start] " + url)

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

    print("[finished]\n")
    return result


def write_to_file(content):
    with open("chengjiao.txt", "r", encoding="utf-8") as f:
        f.write(json.dumps(content, ensure_ascii=False) + ",\n")


# 读取缓存
def readTemp():
    result = []
    try:
        f = open(TEMP_PATH, "r", encoding="utf-8")
    except FileNotFoundError as e:
        return

    lines = f.readlines()
    if len(lines) == 0:
        f.close()
        os.remove(TEMP_PATH)
        return

    result.append(lines[0].strip("\n"))
    result.append(json.loads(lines[1]))

    f.close()
    os.remove(TEMP_PATH)
    return result


# 保存缓存
def saveTemp(currentUrl, data):
    with open(TEMP_PATH, "a", encoding="utf-8") as f:
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

    result = list(zip(EXCEL_HEADER_CONFIG, *data_array))
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

        work_book.save(EXCEL_PATH)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print("[config check] start")
    print("  当前运行路径                CWD: %s" % CWD)
    print("  断点续传文件路径      TEMP_PATH: %s" % TEMP_PATH)
    print("  生成的excel文件路径  EXCEL_PATH: %s" % EXCEL_PATH)
    print("[config check] end\n")

    ifLocalTest = False

    if ifLocalTest:
        testArea = CITY_AND_AREA[0]
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
        house_data = []
        realUrlPrev = ""

        tempUrl = ""

        temp = readTemp()
        if temp:
            print("get temp")
            tempUrl = temp[0]
            house_data = temp[1]

        for city in CITY_AND_AREA:
            for area in city["areas"]:
                for i in range(PAGE_COUNT):
                    # url拼接
                    realUrl = area["href"] + "pg" + str(i + 1)
                    realUrl += "ab200301001000"  # 限制为链家房源
                    realUrl += "rt200600000001"  # 限制为整租
                    realUrl += "/"
                    if i == 0:
                        realUrlPrev = realUrl

                    if tempUrl != "" and realUrl != tempUrl:
                        print("[skip] " + realUrl + "\n")
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
                    time.sleep(SLEEP_TIME)

        # 数组去重
        # TODO

        excel_data = generate_excel_data(house_data)
        write_to_excel(excel_data)
        print("complete")
    except Exception as e:
        print("meet error: %s" % e)

        # 启用断档续传功能
        saveTemp(realUrlPrev, house_data)
