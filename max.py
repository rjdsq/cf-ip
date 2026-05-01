import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    total_raw_count = 0

    # 获取当前采集时间，格式为：2026/4/30/8:16
    # 按照你的示例，去掉秒，使用斜杠分割
    now = datetime.datetime.now()
    time_str = f"{now.year}/{now.month}/{now.day}/{now.hour}:{now.minute:02d}"
    time_remark = f"采集时间{time_str}"

    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    total_raw_count += 1
                    
                    if '#' in line:
                        parts = line.split('#', 1)
                        addr = parts[0].strip()
                        remark = parts[1].strip()
                    else:
                        addr = line
                        remark = ""

                    if not addr:
                        continue

                    if addr not in merged_data:
                        merged_data[addr] = []
                    
                    # 只有当备注不为空且不在列表中时才添加
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    groups = {
        'domain_remark': [],
        'telecom': [],
        'mobile': [],
        'unicom': [],
        'ip_other': [],
        'ip_none': [],
        'domain_none': []
    }

    for addr, remarks in merged_data.items():
        # 核心逻辑修改：在原有备注后拼接时间
        if remarks:
            # 示例：ip # 备注 | 采集时间2026/4/30/8:16
            merged_remark = " | ".join(remarks) + f" | {time_remark}"
        else:
            # 示例：ip # 采集时间2026/4/30/8:16
            merged_remark = time_remark

        is_domain = any(c.isalpha() for c in addr)
        line_str = f"{addr}#{merged_remark}"

        if is_domain:
            # 判定原始是否有备注（不含我们刚加的时间）
            if remarks:
                groups['domain_remark'].append(line_str)
            else:
                groups['domain_none'].append(line_str)
        else:
            # 纯 IP 类归类
            raw_remarks_str = " ".join(remarks)
            if not remarks:
                groups['ip_none'].append(line_str)
            elif '电信' in raw_remarks_str:
                groups['telecom'].append(line_str)
            elif '移动' in raw_remarks_str:
                groups['mobile'].append(line_str)
            elif '联通' in raw_remarks_str:
                groups['unicom'].append(line_str)
            else:
                groups['ip_other'].append(line_str)

    for key in groups:
        groups[key].sort(key=len)

    final_output = []
    final_output.extend(groups['domain_remark'])
    final_output.extend(groups['telecom'])
    final_output.extend(groups['mobile'])
    final_output.extend(groups['unicom'])
    final_output.extend(groups['ip_other'])
    final_output.extend(groups['ip_none'])
    final_output.extend(groups['domain_none'])

    final_count = len(final_output)
    current_log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    overview = [
        "========== 采集汇总 ==========",
        f"执行时间: {current_log_time}",
        f"初始总行数: {total_raw_count}",
        f"重复被过滤: {total_raw_count - final_count}",
        f"最终保留数: {final_count}",
        "---------- 分类详情 ----------",
        f"1. 域名备注: {len(groups['domain_remark'])}",
        f"2. IP 电信 : {len(groups['telecom'])}",
        f"3. IP 移动 : {len(groups['mobile'])}",
        f"4. IP 联通 : {len(groups['unicom'])}",
        f"5. IP 其他 : {len(groups['ip_other'])}",
        f"6. IP 无注 : {len(groups['ip_none'])}",
        f"7. 域名无注: {len(groups['domain_none'])}",
        "=============================="
    ]

    for l in overview: print(l)

    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(overview) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
