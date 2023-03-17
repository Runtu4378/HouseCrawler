# HouseCrawler

租房爬虫

## 环境要求

- Python3
- Window11/mac


## 指令

```python
# 执行脚本
python3 KeZufangQuery.py

# 打包为可执行文件
Pyinstaller -i biao.ico KeZufangQuery.py --onefile --console
```

## 动态配置

在和可执行文件同一文件夹下创建 `KeZufangQuery.config` 可以进行动态配置，比如：

```python
# 不爬取佛山和广州的数据
excludeCity = 佛山,广州
```

支持的动态配置列表：

- **excludeCity**: 字符数组，不进行爬取的城市名称列表，完整的城市列表见：`config.py`

## 参考文档

- [知乎 - 别再问我Python打包成exe了（最适合小白的终极解答）！](https://zhuanlan.zhihu.com/p/370914926)
- [Using PyInstaller — PyInstaller 5.9.0 documentation](https://pyinstaller.org/en/stable/usage.html)
