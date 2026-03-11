#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""超级大乐透预测模块 - 增强版"""

import json
import random
from collections import Counter
from datetime import datetime

DATA_DIR = "/workspace/lottery-data"

def load_data():
    with open(f"{DATA_DIR}/data_all.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        data.sort(key=lambda x: x['issue'])
        return data

def load_stats():
    with open(f"{DATA_DIR}/statistics.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def predict_hot(data, stats):
    """热门预测"""
    front_freq = Counter()
    back_freq = Counter()
    for item in data:
        for n in item['f']:
            front_freq[n] += 1
        for n in item['b']:
            back_freq[n] += 1
    
    front_hot = [x[0] for x in front_freq.most_common(5)]
    back_hot = [x[0] for x in back_freq.most_common(2)]
    
    # 生成理由
    reason = f"基于全部{len(data)}期数据，{', '.join(str(x) for x in front_hot[:3])}号出现频率最高"
    
    return {
        "type": "热门推荐",
        "reason": reason,
        "front": sorted(front_hot),
        "back": sorted(back_hot)
    }

def predict_cold(data, stats):
    """冷门预测"""
    front_miss = {i: 0 for i in range(1, 36)}
    back_miss = {i: 0 for i in range(1, 13)}
    
    front_last = {i: -1 for i in range(1, 36)}
    back_last = {i: -1 for i in range(1, 13)}
    
    for idx, item in enumerate(data):
        for n in item['f']:
            if front_last[n] != -1:
                front_miss[n] = idx - front_last[n]
            front_last[n] = idx
        for n in item['b']:
            if back_last[n] != -1:
                back_miss[n] = idx - back_last[n]
            back_last[n] = idx
    
    front_cold = [x[0] for x in sorted(front_miss.items(), key=lambda x: -x[1])[:5]]
    back_cold = [x[0] for x in sorted(back_miss.items(), key=lambda x: -x[1])[:2]]
    
    reason = f"基于历史遗漏数据，{', '.join(str(x) for x in front_cold[:3])}号遗漏值最大"
    
    return {
        "type": "冷门推荐",
        "reason": reason,
        "front": sorted(front_cold),
        "back": sorted(back_cold)
    }

def predict_random(data, stats):
    """随机预测"""
    front = random.sample(range(1, 36), 5)
    back = random.sample(range(1, 13), 2)
    
    return {
        "type": "随机推荐",
        "reason": "完全随机生成，概率与其他方式相等",
        "front": sorted(front),
        "back": sorted(back)
    }

def predict_warm(data, stats):
    """温号预测"""
    front_freq = Counter()
    back_freq = Counter()
    for item in data:
        for n in item['f']:
            front_freq[n] += 1
        for n in item['b']:
            back_freq[n] += 1
    
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1])
    back_sorted = sorted(back_freq.items(), key=lambda x: x[1])
    
    # 取中间部分
    front_mid = [x[0] for x in front_sorted[10:15]]
    back_mid = [x[0] for x in back_sorted[3:5]]
    
    reason = f"选择中等出现频率的号码，避开极热和极冷号码"
    
    return {
        "type": "温号推荐",
        "reason": reason,
        "front": sorted(front_mid),
        "back": sorted(back_mid)
    }

def predict_combine(data, stats):
    """综合预测"""
    front_freq = Counter()
    for item in data:
        for n in item['f']:
            front_freq[n] += 1
    
    front_sorted = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
    
    # 分5区间各选1个
    zones = [[], [], [], [], []]
    for n, c in front_sorted:
        if 1 <= n <= 7:
            zones[0].append((n, c))
        elif 8 <= n <= 14:
            zones[1].append((n, c))
        elif 15 <= n <= 21:
            zones[2].append((n, c))
        elif 22 <= n <= 28:
            zones[3].append((n, c))
        else:
            zones[4].append((n, c))
    
    front_combine = []
    for zone in zones:
        if zone:
            front_combine.append(random.choice(zone[:3])[0])
    
    while len(front_combine) < 5:
        n = random.randint(1, 35)
        if n not in front_combine:
            front_combine.append(n)
    
    back_counter = Counter(n for item in data for n in item['b'])
    back_sorted = sorted(back_counter.items(), key=lambda x: x[1], reverse=True)
    back_combine = [back_sorted[0][0], back_sorted[3][0]] if len(back_sorted) >= 4 else [x[0] for x in back_sorted[:2]]
    
    reason = "综合考虑号码频率和区间分布，每个区间选取1-2个号码"
    
    return {
        "type": "综合推荐",
        "reason": reason,
        "front": sorted(front_combine)[:5],
        "back": sorted(back_combine)
    }

# 六爻预测
HEXAGRAMS = {
    "乾": {"meaning": "刚健有力", "nums": [1, 8, 15, 22, 29]},
    "坤": {"meaning": "柔顺厚重", "nums": [2, 9, 16, 23, 30]},
    "屯": {"meaning": "困难光明", "nums": [3, 10, 17, 24, 31]},
    "蒙": {"meaning": "蒙昧初开", "nums": [4, 11, 18, 25, 32]},
    "需": {"meaning": "等待时机", "nums": [5, 12, 19, 26, 33]},
    "讼": {"meaning": "易有争执", "nums": [6, 13, 20, 27, 34]},
    "师": {"meaning": "领导有方", "nums": [7, 14, 21, 28, 35]},
    "比": {"meaning": "亲比辅佐", "nums": [1, 8, 15, 22, 29]},
    "泰": {"meaning": "天地交泰", "nums": [3, 10, 17, 24, 31]},
    "否": {"meaning": "闭塞不通", "nums": [4, 11, 18, 25, 32]},
    "同人": {"meaning": "志同道合", "nums": [5, 12, 19, 26, 33]},
    "大有": {"meaning": "大获所有", "nums": [6, 13, 20, 27, 34]},
    "谦": {"meaning": "谦虚受益", "nums": [7, 14, 21, 28, 35]},
    "豫": {"meaning": "欢乐祥和", "nums": [1, 9, 16, 23, 30]},
    "随": {"meaning": "随顺时势", "nums": [2, 10, 17, 24, 31]},
    "蛊": {"meaning": "革除旧弊", "nums": [3, 11, 18, 25, 32]},
    "临": {"meaning": "领导驾临", "nums": [4, 12, 19, 26, 33]},
    "观": {"meaning": "仔细观察", "nums": [5, 13, 20, 27, 34]},
    "噬嗑": {"meaning": "刚柔并济", "nums": [6, 14, 21, 28, 35]},
    "贲": {"meaning": "文饰美化", "nums": [1, 8, 15, 23, 32]},
    "剥": {"meaning": "小人当道", "nums": [2, 9, 16, 24, 33]},
    "复": {"meaning": "阳气回复", "nums": [3, 10, 17, 25, 34]},
    "无妄": {"meaning": "不妄为吉", "nums": [4, 11, 18, 26, 35]},
    "大畜": {"meaning": "大有所蓄", "nums": [5, 12, 19, 27, 1]},
    "颐": {"meaning": "颐养之道", "nums": [6, 13, 20, 28, 2]},
    "大过": {"meaning": "过犹不及", "nums": [7, 14, 21, 29, 3]},
    "坎": {"meaning": "险阻重重", "nums": [1, 8, 16, 24, 32]},
    "离": {"meaning": "光明磊落", "nums": [2, 9, 17, 25, 33]},
    "咸": {"meaning": "感应相通", "nums": [3, 10, 18, 26, 34]},
    "恒": {"meaning": "恒久不变", "nums": [4, 11, 19, 27, 35]},
    "遁": {"meaning": "退避隐藏", "nums": [5, 12, 20, 28, 1]},
    "大壮": {"meaning": "声势浩大", "nums": [6, 13, 21, 29, 2]},
    "晋": {"meaning": "晋升发展", "nums": [7, 14, 22, 30, 3]},
    "明夷": {"meaning": "光明受伤", "nums": [1, 9, 17, 25, 34]}
}

def hexagram_predict(count=3):
    """六爻预测"""
    # 使用时间作为随机种子
    random.seed(datetime.now().timestamp())
    selected = random.sample(list(HEXAGRAMS.keys()), min(count, len(HEXAGRAMS)))
    
    # 生成预测
    all_nums = []
    for name in selected:
        all_nums.extend(HEXAGRAMS[name]["nums"])
    
    front = []
    back = []
    for i, n in enumerate(all_nums[:7]):
        if i < 5:
            front.append(((n + i * 7) % 35) + 1)
        else:
            back.append(((n + i * 3) % 12) + 1)
    
    front = list(set(front))[:5]
    while len(front) < 5:
        n = random.randint(1, 35)
        if n not in front:
            front.append(n)
    
    back = list(set(back))[:2]
    while len(back) < 2:
        n = random.randint(1, 12)
        if n not in back:
            back.append(n)
    
    # 生成卦象图形 (6条线)
    hex_lines = []
    for name in selected:
        lines = ""
        for _ in range(6):
            lines += "Y" if random.random() > 0.5 else "N"
        hex_lines.append(lines)
    
    return {
        "hexagrams": selected,
        "hex_lines": hex_lines,
        "meaning": [HEXAGRAMS[s]["meaning"] for s in selected],
        "reason": f"基于《周易》六十四卦，随机选取{count}卦进行预测",
        "front": sorted(front),
        "back": sorted(back)
    }

def generate_predictions():
    """生成预测"""
    data = load_data()
    stats = load_stats()
    
    predictions = {
        "generated_at": datetime.now().isoformat(),
        "latest_issue": data[-1]["issue"] if data else 0,
        "predictions": [
            predict_hot(data, stats),
            predict_warm(data, stats),
            predict_cold(data, stats),
            predict_random(data, stats),
            predict_combine(data, stats)
        ],
        "hexagram": hexagram_predict(3)
    }
    
    return predictions

def main():
    print("=" * 50)
    print("超级大乐透预测")
    print("=" * 50)
    
    predictions = generate_predictions()
    
    # 保存
    with open(f"{DATA_DIR}/predictions.json", 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    
    print("\n预测结果:")
    for p in predictions["predictions"]:
        front_str = " ".join(f"{n:02d}" for n in p["front"])
        back_str = " ".join(f"{n:02d}" for n in p["back"])
        print(f"\n{p['type']}")
        print(f"  理由: {p['reason']}")
        print(f"  号码: {front_str} + {back_str}")
    
    hp = predictions["hexagram"]
    print(f"\n六爻预测: {' '.join(hp['hexagrams'])}")
    print(f"  理由: {hp['reason']}")
    front_str = " ".join(f"{n:02d}" for n in hp["front"])
    back_str = " ".join(f"{n:02d}" for n in hp["back"])
    print(f"  号码: {front_str} + {back_str}")
    
    print("\n预测已保存")

if __name__ == "__main__":
    main()
