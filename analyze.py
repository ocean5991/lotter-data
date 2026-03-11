#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""超级大乐透统计分析 - 增强版"""

import json
import os
from collections import Counter
from datetime import datetime

DATA_DIR = "/workspace/lottery-data"

def load_all_data():
    with open(f"{DATA_DIR}/data_all.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def calc_frequency(data):
    """计算频率"""
    front_counter = Counter()
    back_counter = Counter()
    
    for item in data:
        for n in item['f']:
            front_counter[n] += 1
        for n in item['b']:
            back_counter[n] += 1
    
    return front_counter, back_counter

def calc_probability(counter, total_draws, numbers_count):
    """计算概率"""
    prob = {}
    for num in range(1, numbers_count + 1):
        count = counter.get(num, 0)
        prob[str(num)] = {
            "count": count,
            "probability": round(count / total_draws * 100, 2) if total_draws > 0 else 0
        }
    return prob

def calc_miss(data, front_range=35, back_range=12):
    """计算遗漏值"""
    front_miss = {i: 0 for i in range(1, front_range + 1)}
    back_miss = {i: 0 for i in range(1, back_range + 1)}
    
    front_last = {i: -1 for i in range(1, front_range + 1)}
    back_last = {i: -1 for i in range(1, back_range + 1)}
    
    for idx, item in enumerate(data):
        for n in item['f']:
            if front_last[n] != -1:
                front_miss[n] = idx - front_last[n]
            front_last[n] = idx
        
        for n in item['b']:
            if back_last[n] != -1:
                back_miss[n] = idx - back_last[n]
            back_last[n] = idx
    
    return front_miss, back_miss

def analyze_odd_even(data):
    """分析奇偶比"""
    results = []
    for item in data:
        odd_front = sum(1 for n in item['f'] if n % 2 == 1)
        even_front = 5 - odd_front
        odd_back = sum(1 for n in item['b'] if n % 2 == 1)
        even_back = 2 - odd_back
        results.append({
            "issue": item["issue"],
            "front": f"{odd_front}:{even_front}",
            "back": f"{odd_back}:{even_back}"
        })
    return results

def analyze_sum_range(data):
    """分析分区"""
    results = []
    for item in data:
        zones = [0, 0, 0, 0, 0]
        for n in item['f']:
            if n <= 7: zones[0] += 1
            elif n <= 14: zones[1] += 1
            elif n <= 21: zones[2] += 1
            elif n <= 28: zones[3] += 1
            else: zones[4] += 1
        
        back_zone = 0 if item['b'][0] <= 6 else 1
        back_zone2 = 0 if item['b'][1] <= 6 else 1
        
        results.append({
            "issue": item["issue"],
            "zones": "/".join(map(str, zones)),
            "back_zones": f"{back_zone},{back_zone2}"
        })
    return results

def calc_statistics(data):
    """计算完整统计"""
    print("计算频率...")
    front_freq, back_freq = calc_frequency(data)
    
    print("计算概率...")
    front_prob = calc_probability(front_freq, len(data), 35)
    back_prob = calc_probability(back_freq, len(data), 12)
    
    print("计算遗漏...")
    front_miss, back_miss = calc_miss(data)
    
    print("计算奇偶比...")
    odd_even = analyze_odd_even(data)
    
    print("计算分区...")
    zone_analysis = analyze_sum_range(data)
    
    # 排序频率
    front_freq_sorted = sorted(front_freq.items(), key=lambda x: -x[1])
    back_freq_sorted = sorted(back_freq.items(), key=lambda x: -x[1])
    
    # 排序遗漏
    front_miss_sorted = sorted(front_miss.items(), key=lambda x: -x[1])
    back_miss_sorted = sorted(back_miss.items(), key=lambda x: -x[1])
    
    # 统计
    stats = {
        "generated_at": datetime.now().isoformat(),
        "total_periods": len(data),
        "date_range": {
            "start": data[0]["date"],
            "end": data[-1]["date"]
        },
        
        # 频率统计
        "front_frequency": {
            "top_10": [{"number": n, "count": c} for n, c in front_freq_sorted[:10]],
            "bottom_10": [{"number": n, "count": c} for n, c in front_freq_sorted[-10:]]
        },
        "back_frequency": {
            "top_6": [{"number": n, "count": c} for n, c in back_freq_sorted[:6]],
            "bottom_6": [{"number": n, "count": c} for n, c in back_freq_sorted[-6:]]
        },
        
        # 概率统计 - 新增
        "front_probability": front_prob,
        "back_probability": back_prob,
        
        # 遗漏统计
        "front_miss": {
            "max_miss": [{"number": n, "miss": m} for n, m in front_miss_sorted[:5]],
            "current_miss": {str(n): m for n, m in front_miss.items()}
        },
        "back_miss": {
            "max_miss": [{"number": n, "miss": m} for n, m in back_miss_sorted[:3]],
            "current_miss": {str(n): m for n, m in back_miss.items()}
        },
        
        # 奇偶统计
        "odd_even_stats": {
            "most_common_front": Counter([x["front"] for x in odd_even]).most_common(5),
            "most_common_back": Counter([x["back"] for x in odd_even]).most_common(3)
        },
        
        # 和值统计
        "sum_stats": {
            "front_sum_avg": sum(sum(item['f']) for item in data) / len(data),
            "front_sum_min": min(sum(item['f']) for item in data),
            "front_sum_max": max(sum(item['f']) for item in data)
        },
        
        # 分区统计
        "zone_stats": Counter([x["zones"] for x in zone_analysis]).most_common(10)
    }
    
    return stats

def main():
    print("=" * 50)
    print("超级大乐透统计分析")
    print("=" * 50)
    
    # 加载数据
    data = load_all_data()
    data.sort(key=lambda x: x['issue'])
    print(f"加载 {len(data)} 期数据")
    
    # 计算统计
    stats = calc_statistics(data)
    
    # 保存
    with open(f"{DATA_DIR}/statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("统计分析完成!")
    print("=" * 50)
    print(f"总期数: {stats['total_periods']}")
    print(f"日期范围: {stats['date_range']['start']} - {stats['date_range']['end']}")
    print(f"前区最热: {[str(x['number']) for x in stats['front_frequency']['top_10'][:5]]}")
    print(f"后区最热: {[str(x['number']) for x in stats['back_frequency']['top_6'][:3]]}")

if __name__ == "__main__":
    main()
