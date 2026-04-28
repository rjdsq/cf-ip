import re
import subprocess
import requests
import os

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

DOMAIN_LIST = [
    "cf.tencentapp.cn",
    "cloudflare-dl.byoip.top",
    "cf.877774.xyz",
    "saas.sin.fan",
    "bestcf.030101.xyz"
]

IPV4_REG = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

def fetch_content(url):
    try:
        headers = {"User-Agent":"Mozilla/5.0"}
        resp = requests.get(url,timeout=12,headers=headers)
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
        args = ["ping","-n","2","-w","1000",ip_addr]
    else:
        args = ["ping","-c","2","-W","1",ip_addr]
    ret = subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE).returncode
    return ret == 0

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
    for raw_line in unique_line:
        ip = parse_ip(raw_line)
        if not ip:
            continue
        if ping_check(ip):
            valid_data.append(raw_line)
    with open("max.txt","w",encoding="utf-8") as f:
        for d in valid_data:
            f.write(d + "\n")

if __name__ == "__main__":
    main()
