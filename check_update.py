#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并更新最新彩票数据
"""

import urllib.request
import json
import re
import os
import ssl
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

DATA_DIR = "/workspace/lottery-data"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}

def make_request(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8')

def get_latest_from_web():
    """从官网获取最新一期数据"""
    url = "http://datachart.500.com/dlt/history/newinc/history.php?start=26020&end=26030"
    try:
        text = make_request(url)
        tbody_match = re.search(r'<tbody[^>]*id="tdata"[^>]*>(.*?)</tbody>', text, re.DOTALL)
        if not tbody_match:
            return None
        
        tbody = tbody_match.group(1)
        trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody)
        
        latest = None
        for tr in trs:
            if 't_tr' not in tr:
                continue
            tds_all = re.findall(r'<td[^>]*>([^<]*)</td>', tr)
            if len(tds_all) >= 16:
                try:
                    issue_str = tds_all[1].strip()
                    issue = int(issue_str)
                    front = [int(tds_all[i].strip()) for i in range(2, 7)]
                    back = [int(tds_all[i].strip()) for i in range(7, 9)]
                    date = tds_all[15].strip()
                    
                    if latest is None or issue > latest['issue']:
                        latest = {"issue": issue, "date": date, "f": front, "b": back}
                except:
                    continue
        
        return latest
    except Exception as e:
        print(f"获取最新数据失败: {e}")
        return None

def load_existing_data():
    """加载现有数据"""
    try:
        with open(f"{DATA_DIR}/data_all.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    """保存数据"""
    # 按年份分组
    year_data = {}
    for item in data:
        year = item['date'][:4] if item['date'] else "unknown"
        if year not in year_data:
            year_data[year] = []
        year_data[year].append(item)
    
    # 保存每年
    for year in sorted(year_data.keys()):
        with open(f"{DATA_DIR}/data_{year}.json", 'w', encoding='utf-8') as f:
            json.dump(year_data[year], f, ensure_ascii=False, indent=2)
    
    # 保存汇总
    with open(f"{DATA_DIR}/data_all.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_and_update():
    """检查并更新数据"""
    print("=" * 50)
    print("检查最新数据...")
    print("=" * 50)
    
    # 获取现有数据
    existing_data = load_existing_data()
    if existing_data:
        existing_data.sort(key=lambda x: x['issue'])
        local_latest = existing_data[-1]
        print(f"本地最新: 第{local_latest['issue']}期 ({local_latest['date']})")
    else:
        local_latest = None
        print("本地无数据")
    
    # 获取网上最新
    web_latest = get_latest_from_web()
    if not web_latest:
        print("无法获取网上最新数据")
        return False
    
    print(f"网上最新: 第{web_latest['issue']}期 ({web_latest['date']})")
    
    # 检查是否需要更新
    if local_latest and web_latest['issue'] <= local_latest['issue']:
        print("数据已是最新，无需更新")
        return False
    
    # 有新数据
    print(f"\n发现新数据! 第{web_latest['issue']}期")
    
    # 添加新数据
    existing_data.append(web_latest)
    existing_data.sort(key=lambda x: x['issue'])
    
    # 保存
    save_data(existing_data)
    print(f"已更新数据，共 {len(existing_data)} 期")
    
    return True

if __name__ == "__main__":
    updated = check_and_update()
    if updated:
        print("\n数据已更新，需要重新运行统计和预测脚本")
    else:
        print("\n数据已是最新状态")
