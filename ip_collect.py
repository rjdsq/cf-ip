import re
import subprocess
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

API_LIST = [
    "https://bestcf.pages.dev/vps789/top20.txt",
    "https://bestcf.pages.dev/tiancheng/all.txt",
    "https://bestcf.pages.dev/vvhan/ipv4.txt",
    "https://bestcf.pages.dev/vvhan/ipv6.txt",
    "https://bestcf.pages.dev/xinyitang3/ipv4.txt",
    "https://bestcf.pages.dev/nirevil/ipv4.txt",
    "https://bestcf.pages.dev/mingyu/ipv4.txt",
    "https://bestcf.pages.dev/zhixuanwang/ipv4-onlyip.txt",
    "https://cf.090227.xyz/ip.164746.xyz",
    "https://cf.090227.xyz/CloudFlareYes",
    "https://cf.090227.xyz/cmcc?ips=8",
    "https://cf.090227.xyz/cu",
    "https://cf.090227.xyz/ct?ips=6"
]

IPV4_REG = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

def fetch_content(url):
    try:
        headers = {"User-Agent":"Mozilla/5.0"}
        resp = requests.get(url,timeout=8,headers=headers)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return ""

def parse_ip(line):
    match = IPV4_REG.search(line)
    if match:
        return match.group()
    return None

def ping_check(ip_addr):
    if os.name == "nt":
        args = ["ping","-n","1","-w","500",ip_addr]
    else:
        args = ["ping","-c","1","-W","0.5",ip_addr]
    try:
        ret = subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=2).returncode
        return ret == 0
    except:
        return False

def main():
    line_pool = []
    for api in API_LIST:
        content = fetch_content(api)
        lines = content.splitlines()
        for item in lines:
            trim_line = item.strip()
            if trim_line:
                line_pool.append(trim_line)
    unique_line = list(set(line_pool))
    valid_data = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_line = {executor.submit(ping_check, parse_ip(line)): line for line in unique_line if parse_ip(line)}
        for future in as_completed(future_to_line):
            line = future_to_line[future]
            try:
                if future.result():
                    valid_data.append(line)
            except:
                continue
    with open("max.txt","w",encoding="utf-8") as f:
        for d in valid_data:
            f.write(d + "\n")

if __name__ == "__main__":
    main()
