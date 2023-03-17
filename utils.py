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
