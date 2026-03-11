#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""超级大乐透历史数据获取"""

import urllib.request
import json
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DATA_DIR = "/workspace/lottery-data"
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}

def make_request(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8')

def get_lottery_data():
    url = "http://datachart.500.com/dlt/history/newinc/history.php?start=07011&end=26024"
    print("正在获取数据...")
    
    try:
        text = make_request(url)
        tbody_match = re.search(r'<tbody[^>]*id="tdata"[^>]*>(.*?)</tbody>', text, re.DOTALL)
        if not tbody_match:
            print("未找到数据表格")
            return []
        
        tbody = tbody_match.group(1)
        trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody)
        print(f"找到 {len(trs)} 行")
        
        data = []
        for tr in trs:
            if 't_tr' not in tr:
                continue
            
            tds_all = re.findall(r'<td[^>]*>([^<]*)</td>', tr)
            
            if len(tds_all) >= 16:
                try:
                    # tds_all[1] = 期号 (如 07015)
                    issue_str = tds_all[1].strip()
                    issue = int(issue_str)
                    
                    # tds_all[2:7] = 前区
                    front = [int(tds_all[i].strip()) for i in range(2, 7)]
                    
                    # tds_all[7:9] = 后区
                    back = [int(tds_all[i].strip()) for i in range(7, 9)]
                    
                    # tds_all[15] = 日期
                    date = tds_all[15].strip()
                    
                    data.append({"issue": issue, "date": date, "f": front, "b": back})
                except (ValueError, IndexError):
                    continue
        
        return data
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_data_by_year(data):
    print("\n按年份保存数据...")
    
    year_data = {}
    for item in data:
        year = item['date'][:4] if item['date'] else "unknown"
        if year not in year_data:
            year_data[year] = []
        year_data[year].append(item)
    
    for year in sorted(year_data.keys()):
        filename = f"{DATA_DIR}/data_{year}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(year_data[year], f, ensure_ascii=False, indent=2)
        print(f"  {year}: {len(year_data[year])}期")
    
    with open(f"{DATA_DIR}/data_all.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  汇总: {len(data)}期")

def main():
    print("=" * 50)
    print("超级大乐透历史数据获取")
    print("=" * 50)
    
    data = get_lottery_data()
    
    if data:
        data.sort(key=lambda x: x['issue'])
        print(f"\n成功获取 {len(data)} 期数据")
        print(f"最早期号: {data[0]['issue']} ({data[0]['date']})")
        print(f"最新期号: {data[-1]['issue']} ({data[-1]['date']})")
        save_data_by_year(data)
        print("\n" + "=" * 50)
        print("数据获取完成!")
        print("=" * 50)
    else:
        print("未能获取数据")

if __name__ == "__main__":
    main()
