import os

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    total_raw_count = 0

    # 1. 暴力读取，只要有字符就记录
    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    total_raw_count += 1
                    
                    # 统一按 # 分割
                    if '#' in line:
                        parts = line.split('#', 1)
                        addr = parts[0].strip()
                        remark = parts[1].strip()
                    else:
                        addr = line
                        remark = ""

                    if not addr:
                        continue

                    # 同地址去重，备注合并
                    if addr not in merged_data:
                        merged_data[addr] = []
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    # 2. 重新定义分类逻辑 (不靠正则，靠特征)
    groups = {
        'domain_remark': [],   # 域名且有备注
        'telecom': [],         # IP-电信
        'mobile': [],          # IP-移动
        'unicom': [],          # IP-联通
        'ip_other': [],        # IP-其他备注
        'ip_none': [],         # 纯IP-无备注
        'domain_none': []      # 纯域名-无备注
    }

    for addr, remarks in merged_data.items():
        merged_remark = " | ".join(remarks)
        
        # 判断是域名还是IP：只要包含字母，就是域名
        is_domain = any(c.isalpha() for c in addr)
        
        if merged_remark:
            line_str = f"{addr}#{merged_remark}"
        else:
            line_str = addr

        if is_domain:
            if merged_remark:
                groups['domain_remark'].append(line_str)
            else:
                groups['domain_none'].append(line_str)
        else:
            if not merged_remark:
                groups['ip_none'].append(line_str)
            elif '电信' in merged_remark:
                groups['telecom'].append(line_str)
            elif '移动' in merged_remark:
                groups['mobile'].append(line_str)
            elif '联通' in merged_remark:
                groups['unicom'].append(line_str)
            else:
                groups['ip_other'].append(line_str)

    # 3. 组内长短排序
    for key in groups:
        groups[key].sort(key=len)

    # 4. 汇总
    final_output = []
    final_output.extend(groups['domain_remark'])
    final_output.extend(groups['telecom'])
    final_output.extend(groups['mobile'])
    final_output.extend(groups['unicom'])
    final_output.extend(groups['ip_other'])
    final_output.extend(groups['ip_none'])
    final_output.extend(groups['domain_none'])

    final_count = len(final_output)
    
    overview = [
        "========== 采集汇总 ==========",
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
