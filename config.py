"""
配置管理，从文件加载配置
"""
import json5

with open("config.json", "r") as fp:
    config = json5.load(fp)
