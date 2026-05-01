import os
import datetime

def merge_and_sort_files():
    fast_file = '极速.txt'
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    
    final_fast_map = {}
    other_data_map = {}
    dup_records = []
    source_stats = {name: {"total": 0, "valid": 0, "dup": 0} for name in input_files + [fast_file]}
    
    now_utc = datetime.datetime.utcnow()
    bj_time = now_utc + datetime.timedelta(hours=8)
    std_time = bj_time.strftime('%Y-%m-%d %H:%M:%S')
    top_time_str = f"{bj_time.year}/{bj_time.month}/{bj_time.day}/{bj_time.hour}:{bj_time.minute:02d}"

    if os.path.exists(fast_file):
        with open(fast_file, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                raw = line.strip()
                if not raw: continue
                source_stats[fast_file]["total"] += 1
                
                parts = raw.split('#', 1) if '#' in raw else [raw, ""]
                addr = parts[0].strip()
                rem = parts[1].strip()
                
                if addr not in final_fast_map:
                    final_fast_map[addr] = rem
                    source_stats[fast_file]["valid"] += 1
                else:
                    source_stats[fast_file]["dup"] += 1
                    dup_records.append(f"┃ ⚠️ 金标内部重复: [{addr}] 在 {fast_file} 第 {idx} 行被舍弃")

    for file_name in input_files:
        if not os.path.exists(file_name): continue
        with open(file_name, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                raw = line.strip()
                if not raw: continue
                source_stats[file_name]["total"] += 1
                
                parts = raw.split('#', 1) if '#' in raw else [raw, ""]
                addr = parts[0].strip()
                rem = parts[1].strip()

                if addr in final_fast_map:
                    source_stats[file_name]["dup"] += 1
                    dup_records.append(f"┃ 🛡️ 金标保护触发: [{addr}] 来自 {file_name} 第 {idx} 行，因与极速清单冲突已被剔除")
                    continue

                if addr not in other_data_map:
                    other_data_map[addr] = {"remarks": [], "origin": f"{file_name} 第 {idx} 行"}
                    source_stats[file_name]["valid"] += 1
                else:
                    source_stats[file_name]["dup"] += 1
                    dup_records.append(f"┃ ✂️ 普通重复: [{addr}] 在 {file_name} 第 {idx} 行被过滤")
                
                if rem and rem not in other_data_map[addr]["remarks"]:
                    other_data_map[addr]["remarks"].append(rem)

    groups = {'域名备注': [], '电信线路': [], '移动线路': [], '联通线路': [], '其他备注': [], '纯净IP': [], '纯净域名': []}
    top_domain_node = None
    
    for addr, info in other_data_map.items():
        rems = info["remarks"]
        is_dom = any(c.isalpha() for c in addr)
        
        if is_dom and not rems and top_domain_node is None:
            top_domain_node = f"{addr}#节点更新时间：{top_time_str} | 间隔：10分钟"
            continue

        line_str = f"{addr}#{' | '.join(rems)}" if rems else addr
        if is_dom:
            target = '域名备注' if rems else '纯净域名'
        else:
            raw_all_rems = " ".join(rems)
            if not rems: target = '纯净IP'
            elif '电信' in raw_all_rems: target = '电信线路'
            elif '移动' in raw_all_rems: target = '移动线路'
            elif '联通' in raw_all_rems: target = '联通线路'
            else: target = '其他备注'
        groups[target].append(line_str)

    final_output = []
    addr_to_line = {}
    
    if top_domain_node:
        final_output.append(top_domain_node)
        addr_to_line[top_domain_node.split('#')[0]] = 1
    
    curr = len(final_output) + 1
    for addr, rem in final_fast_map.items():
        line = f"{addr}#{rem}" if rem else addr
        final_output.append(line)
        addr_to_line[addr] = curr
        curr += 1
    
    order = ['域名备注', '电信线路', '移动线路', '联通线路', '其他备注', '纯净IP', '纯净域名']
    for key in order:
        groups[key].sort(key=len)
        for item in groups[key]:
            final_output.append(item)
            addr_to_line[item.split('#')[0]] = curr
            curr += 1

    log = [
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓",
        f"┃ 🚀 极速优先-高精度自动化对账  [{std_time}] ┃",
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫",
        f"┃ 📊 汇总: 读取 {sum(s['total'] for s in source_stats.values())} | 保留 {len(final_output)} | 拦截 {sum(s['dup'] for s in source_stats.values())}",
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫",
        "┃ 📂 来源细分 (有效/原始):"
    ]
    for s_name, s_val in source_stats.items():
        log.append(f"┃ ┣ {s_name.ljust(15)}: {str(s_val['valid']).rjust(3)} / {str(s_val['total']).rjust(3)}")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ ⚠️ 深度审计清单:")
    log.extend(dup_records if dup_records else ["┃ ┗ ✅ 无冲突记录"])
    log.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    for l in log: print(l)
    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')
    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
