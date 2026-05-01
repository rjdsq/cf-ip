import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    raw_data_map = {}
    dup_records = []
    source_stats = {name: {"total": 0, "valid": 0, "dup": 0} for name in input_files}
    
    now_utc = datetime.datetime.utcnow()
    bj_time = now_utc + datetime.timedelta(hours=8)
    std_time = bj_time.strftime('%Y-%m-%d %H:%M:%S')
    data_tag = f"{bj_time.month}/{bj_time.day}/{bj_time.hour}:{bj_time.minute}"

    for file_name in input_files:
        if not os.path.exists(file_name):
            continue
        with open(file_name, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                raw = line.replace('\n', '').replace('\r', '')
                if not raw.strip(): continue
                
                source_stats[file_name]["total"] += 1
                parts = raw.split('#', 1) if '#' in raw else [raw, ""]
                addr = parts[0]
                remark = parts[1].strip()

                if addr not in raw_data_map:
                    raw_data_map[addr] = {"remarks": [], "origin": f"{file_name} 第 {idx} 行"}
                    source_stats[file_name]["valid"] += 1
                else:
                    source_stats[file_name]["dup"] += 1
                    dup_records.append({
                        "addr": addr,
                        "from_file": file_name,
                        "from_line": idx,
                        "target_origin": raw_data_map[addr]["origin"]
                    })
                
                if remark and remark not in raw_data_map[addr]["remarks"]:
                    raw_data_map[addr]["remarks"].append(remark)

    groups = {'域名备注': [], '电信线路': [], '移动线路': [], '联通线路': [], '其他备注': [], '纯净IP': [], '纯净域名': []}
    for addr, info in raw_data_map.items():
        remarks = info["remarks"]
        merged_remark = " | ".join(remarks) + f" | {data_tag}" if remarks else data_tag
        line_str = f"{addr}#{merged_remark}"
        is_domain = any(c.isalpha() for c in addr)
        if is_domain:
            target = '域名备注' if remarks else '纯净域名'
        else:
            raw_rem = " ".join(remarks)
            if not remarks: target = '纯净IP'
            elif '电信' in raw_rem: target = '电信线路'
            elif '移动' in raw_rem: target = '移动线路'
            elif '联通' in raw_rem: target = '联通线路'
            else: target = '其他备注'
        groups[target].append(line_str)

    final_output = []
    order = ['域名备注', '电信线路', '移动线路', '联通线路', '其他备注', '纯净IP', '纯净域名']
    addr_to_max_line = {}
    current_line = 1
    for key in order:
        groups[key].sort(key=len)
        for item in groups[key]:
            final_output.append(item)
            addr_to_max_line[item.split('#')[0]] = current_line
            current_line += 1

    log = []
    log.append("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    log.append(f"┃ 🚀 自动化高精度对账系统  [{std_time}] ┃")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append(f"┃ 📊 全局统计: 读取 {sum(s['total'] for s in source_stats.values())} | 保留 {len(raw_data_map)} | 拦截 {len(dup_records)}")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ ⚠️ 深度重复审计清单 (精确位置追踪):")
    
    if dup_records:
        for r in dup_records:
            max_line = addr_to_max_line.get(r["addr"], "N/A")
            log.append(f"┃ 📍 重复地址: [{r['addr'].strip()}]")
            log.append(f"┃   ┣ 💎 最终保留于: max.txt 第 {max_line} 行")
            log.append(f"┃   ┣ 📥 原始出处: {r['target_origin']}")
            log.append(f"┃   ┗ ❌ 冲突位置: {r['from_file']} 第 {r['from_line']} 行")
            log.append("┃")
    else:
        log.append("┃ ✅ 此轮采集未发现任何重复项")

    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ 📂 来源分布详情:")
    for src, s in source_stats.items():
        log.append(f"┃ ┣ {src.ljust(15)}: 读取 {str(s['total']).rjust(3)} | 有效 {str(s['valid']).rjust(3)} | 重复 {str(s['dup']).rjust(3)}")
    log.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    for line in log: print(line)
    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')
    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
