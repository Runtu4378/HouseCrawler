import time


# 定义进度条函数
def progressBar(done):
    # 设定进度条总宽度为50个字符
    barWidth = 50
    # 计算当前进度条已填充的宽度
    fillWidth = int(barWidth * done)
    # 计算未填充部分的宽度
    emptyWidth = barWidth - fillWidth
    # 使用“#”符号作为已完成部分的填充字符，使用“-”符号作为未完成部分的填充字符
    bar = "#" * fillWidth + "-" * emptyWidth
    # 输出进度条和当前完成百分比
    print("\r[{}] {:.0%}".format(bar, done), end="")


def timer():
    startTime = None

    def start():
        nonlocal startTime
        startTime = time.time()

    def stop():
        nonlocal startTime
        if startTime is None:
            raise Exception("计时器未启动")
        elapsedTime = time.time() - startTime
        startTime = None
        return elapsedTime

    return start, stop


def formatSeconds(seconds, timeFormat="HH:mm:ss"):
    """将秒数转换为指定格式的时间文本"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    if "HH" in timeFormat:
        timeFormat = timeFormat.replace("HH", f"{hours:02d}")
    elif "H" in timeFormat:
        timeFormat = timeFormat.replace("H", str(hours))

    if "mm" in timeFormat:
        timeFormat = timeFormat.replace("mm", f"{minutes:02d}")
    elif "m" in timeFormat:
        timeFormat = timeFormat.replace("m", str(minutes))

    if "ss" in timeFormat:
        timeFormat = timeFormat.replace("ss", f"{seconds:02d}")
    elif "s" in timeFormat:
        timeFormat = timeFormat.replace("s", str(seconds))

    return timeFormat


def readLocalConfig(filePath):
    """
    读取本地配置文件

    Args:
        filePath (str): 配置文件路径

    Returns:
        dict: 配置项字典，键为变量名，值为变量值
    """
    config = {}
    with open(filePath, "r") as f:
        for line in f:
            if not line.strip():
                continue
            key_value = line.strip().split("=")
            key = key_value[0].strip()
            value = key_value[1].strip()

            if "," in value:
                value = [i.strip() for i in value.split(",")]

            config[key] = value
    return config


def generateString(length, str1, str2):
    """
    :param length: int类型，生成字符串长度
    :param str1: string类型，第一个字符串
    :param str2: string类型，第二个字符串
    :return: 返回一个由str1和str2按照空格拼接后重复直到该字符串长度为len得到的新字符串
    """
    concatStr = str1 + " " * (length - len(str1) - len(str2)) + str2

    return concatStr
