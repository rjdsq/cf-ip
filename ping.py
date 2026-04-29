import socket
import concurrent.futures
import sys
from datetime import datetime

def check_tcp_ping(line):
    line = line.strip()
    if not line:
        return None, None
    try:
        left_part = line.split('#')[0].strip()
        if left_part.startswith('['):
            host = left_part.split(']')[0][1:]
            port_str = left_part.split(']')[-1]
            port = int(port_str[1:]) if port_str.startswith(':') else 443
        else:
            if ':' in left_part:
                host, port_str = left_part.split(':', 1)
                port = int(port_str)
            else:
                host = left_part
                port = 443
                
        with socket.create_connection((host, port), timeout=2):
            print(f"[保留] 端口开放: {host}:{port}")
            return True, line
    except:
        # 如果解析失败或者无法连通，统一走这里
        fail_target = left_part if 'left_part' in locals() else line
        print(f"[丢弃] 无法连通或异常: {fail_target}")
        return False, line

if __name__ == '__main__':
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"=== 开始执行 TCP 端口清洗任务 ({start_time}) ===")
    
    try:
        with open('max.txt', 'r', encoding='utf-8') as f:
            lines = [l for l in f.readlines() if l.strip()]
    except FileNotFoundError:
        print("错误: 找不到 max.txt 文件！")
        sys.exit(1)

    total_count = len(lines)
    print(f"-> 成功读取 max.txt，共发现 {total_count} 个待测目标。")
    print("-> 正在启动 50 线程并发检测，请稍候...\n")

    keep_list = []
    fail_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_tcp_ping, lines))
        for is_ok, content in results:
            if is_ok:
                keep_list.append(content)
            else:
                fail_list.append(content)

    kept_count = len(keep_list)
    discarded_count = len(fail_list)
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n=== 检测过程结束 ===")
    print(f"统计信息: 总数 {total_count} | 保留 {kept_count} | 丢弃 {discarded_count}")

    # 写入 ping.log 文件 (只包含统计和丢弃清单)
    log_content = [
        f"任务开始时间：{start_time}",
        f"任务结束时间：{end_time}",
        f"--------------------------",
        f"节点总数：{total_count}",
        f"保留数量：{kept_count}",
        f"丢弃数量：{discarded_count}",
        f"存活率：{round(kept_count/total_count*100, 2) if total_count > 0 else 0}%",
        f"--------------------------",
        f"\n[丢弃清单]",
        *fail_list
    ]

    with open('ping.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_content))

    # 更新 max.txt 文件 (只包含存活节点)
    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(keep_list) + '\n')
    
    print(f"-> 存活节点已重新写入 max.txt，详细丢弃日志已保存至 ping.log")
