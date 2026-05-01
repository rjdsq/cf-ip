import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    duplicate_details = []
    total_raw_count = 0

    # 修正时区并确保 24 小时制
    # %H 本身就是 24 小时制 (00-23)，%M 补零确保格式整齐
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = bj_time.strftime('%Y/%m/%d/%H:%M')

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
                    else:
                        duplicate_details.append(f"重复项: {addr} (来自 {file_name})")
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    groups = {
        'domain_remark': [], 'telecom': [], 'mobile': [], 
        'unicom': [], 'ip_other': [], 'ip_none': [], 'domain_none': []
    }

    for addr, remarks in merged_data.items():
        if remarks:
            merged_remark = " | ".join(remarks) + f" | {time_str}"
        else:
            merged_remark = time_str

        is_domain = any(c.isalpha() for c in addr)
        line_str = f"{addr}#{merged_remark}"

        if is_domain:
            if remarks: groups['domain_remark'].append(line_str)
            else: groups['domain_none'].append(line_str)
        else:
            raw_remarks_str = " ".join(remarks)
            if not remarks: groups['ip_none'].append(line_str)
            elif '电信' in raw_remarks_str: groups['telecom'].append(line_str)
            elif '移动' in raw_remarks_str: groups['mobile'].append(line_str)
            elif '联通' in raw_remarks_str: groups['unicom'].append(line_str)
            else: groups['ip_other'].append(line_str)

    # 汇总输出
    final_output = []
    order = ['domain_remark', 'telecom', 'mobile', 'unicom', 'ip_other', 'ip_none', 'domain_none']
    
    for key in order:
        groups[key].sort(key=len)
        final_output.extend(groups[key])

    final_count = len(merged_data)
    
    # 构造日志
    log_content = [
        "========== 采集汇总 ==========",
        f"北京时间: {time_str} (24H)",
        f"总读取行数: {total_raw_count}",
        f"去重后总数: {final_count}",
        f"被过滤的重复行数: {len(duplicate_details)}",
        "---------- 详细过滤清单 ----------"
    ]
    if duplicate_details:
        log_content.extend(duplicate_details)
    else:
        log_content.append("无重复数据")
    log_content.append("----------------------------------")

    for l in log_content: print(l)

    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_content) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
