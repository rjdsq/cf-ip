import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    first_seen_info = {}
    audit_list = []
    source_stats = {name: {"total": 0, "valid": 0, "dup": 0} for name in input_files}
    
    now_utc = datetime.datetime.utcnow()
    bj_time = now_utc + datetime.timedelta(hours=8)
    std_time = bj_time.strftime('%Y-%m-%d %H:%M:%S')
    data_tag = f"{bj_time.month}/{bj_time.day}/{bj_time.hour}:{bj_time.minute}"

    for file_name in input_files:
        if not os.path.exists(file_name):
            continue
        
        with open(file_name, 'r', encoding='utf-8') as f:
            for line_idx, line in enumerate(f, 1):
                raw_line = line.replace('\n', '').replace('\r', '')
                if not raw_line.strip():
                    continue
                
                source_stats[file_name]["total"] += 1
                
                if '#' in raw_line:
                    parts = raw_line.split('#', 1)
                    addr = parts[0]
                    remark = parts[1].strip()
                else:
                    addr = raw_line
                    remark = ""

                if addr not in merged_data:
                    merged_data[addr] = []
                    first_seen_info[addr] = f"{file_name} 第 {line_idx} 行"
                    source_stats[file_name]["valid"] += 1
                else:
                    source_stats[file_name]["dup"] += 1
                    audit_list.append(f"┃ 🔍 地址: {addr.strip()}")
                    audit_list.append(f"┃   ┣ 📥 原始位置: {first_seen_info[addr]}")
                    audit_list.append(f"┃   ┗ ⚠️ 重复位置: {file_name} 第 {line_idx} 行")
                    audit_list.append(f"┃")

                if remark and remark not in merged_data[addr]:
                    merged_data[addr].append(remark)

    groups = {
        '域名备注': [], '电信线路': [], '移动线路': [], 
        '联通线路': [], '其他备注': [], '纯净IP': [], '纯净域名': []
    }

    for addr, remarks in merged_data.items():
        merged_remark = " | ".join(remarks) + f" | {data_tag}" if remarks else data_tag
        is_domain = any(c.isalpha() for c in addr)
        line_str = f"{addr}#{merged_remark}"

        if is_domain:
            target = '域名备注' if remarks else '纯净域名'
        else:
            raw_remarks_str = " ".join(remarks)
            if not remarks: target = '纯净IP'
            elif '电信' in raw_remarks_str: target = '电信线路'
            elif '移动' in raw_remarks_str: target = '移动线路'
            elif '联通' in raw_remarks_str: target = '联通线路'
            else: target = '其他备注'
        groups[target].append(line_str)

    final_output = []
    order = ['域名备注', '电信线路', '移动线路', '联通线路', '其他备注', '纯净IP', '纯净域名']
    for key in order:
        groups[key].sort(key=len)
        final_output.extend(groups[key])

    log = []
    log.append("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    log.append(f"┃ 🚀 优选 IP 自动化对账系统  [{std_time}] ┃")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append(f"┃ 📊 数据统计汇总:")
    log.append(f"┃ ┣ 📥 原始读取总数: {sum(s['total'] for s in source_stats.values())} 行")
    log.append(f"┃ ┣ 🛒 最终保留总数: {len(merged_data)} 行")
    log.append(f"┃ ┗ ✂️ 累计拦截重复: {sum(s['dup'] for s in source_stats.values())} 次")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ 📂 文件来源及过滤详情:")
    for src, stats in source_stats.items():
        log.append(f"┃ ┣ 📄 {src.ljust(18)}")
        log.append(f"┃ ┃ ┣ 读取: {str(stats['total']).rjust(4)} | 有效: {str(stats['valid']).rjust(4)} | 重复: {str(stats['dup']).rjust(4)}")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ 🔍 分类分布明细:")
    for key in order:
        count = len(groups[key])
        perc = (count / len(merged_data)) * 100 if merged_data else 0
        log.append(f"┃ ┣ 🏷️ {key} : {str(count).rjust(4)} 项 ({perc:>5.1f}%)")
    log.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    log.append("┃ ⚠️ 深度审计清单 (精准对账):")
    if audit_list:
        log.extend(audit_list[:-1] if audit_list[-1] == "┃" else audit_list)
    else:
        log.append("┃ ┗ ✅ 此轮采集未发现任何跨文件或同文件重复项")
    log.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    for line in log: print(line)

    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
