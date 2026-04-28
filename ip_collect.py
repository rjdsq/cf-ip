import re
import requests

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

ALLOWED_DOMAINS = set()
for d in DOMAIN_LIST:
    base = d.split("#", 1)[0].strip()
    if "]:" in base:
        host = base.rsplit("]:", 1)[0].lstrip("[")
    elif base.count(":") == 1:
        host = base.split(":", 1)[0]
    else:
        host = base
    ALLOWED_DOMAINS.add(host)

IPV4_REG = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
IPV6_REG = re.compile(r"([0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F]{0,4}")

_BASE_MAP = {
    "US": "🇺🇸 美国", "HK": "🇭🇰 香港", "SG": "🇸🇬 新加坡", "JP": "🇯🇵 日本",
    "KR": "🇰🇷 韩国", "TW": "🇹🇼 台湾", "GB": "🇬🇧 英国", "DE": "🇩🇪 德国",
    "NL": "🇳🇱 荷兰", "FR": "🇫🇷 法国", "AU": "🇦🇺 澳大利亚", "CA": "🇨🇦 加拿大",
    "IN": "🇮🇳 印度", "BR": "🇧🇷 巴西", "ZA": "🇿🇦 南非", "RU": "🇷🇺 俄罗斯",
    "MY": "🇲🇾 马来西亚", "ID": "🇮🇩 印尼", "TH": "🇹🇭 泰国", "VN": "🇻🇳 越南",
    "PH": "🇵🇭 菲律宾", "AE": "🇦🇪 阿联酋", "MO": "🇲🇴 澳门", "CN": "🇨🇳 中国"
}

_ALIASES = {
    "USA": "US", "LAX": "US", "SJC": "US", "SFO": "US", "SEA": "US", "NYC": "US", "JFK": "US", "EWR": "US", "DFW": "US", "ORD": "US", "MIA": "US", "ATL": "US", "IAD": "US", "PDX": "US", "PHX": "US", "LAS": "US", "HNL": "US",
    "美国": "US", "洛杉矶": "US", "圣何塞": "US", "圣塔克拉拉": "US", "芝加哥": "US", "西雅图": "US", "纽约": "US", "达拉斯": "US", "迈阿密": "US", "亚特兰大": "US", "华盛顿": "US", "波特兰": "US", "旧金山": "US", "拉斯维加斯": "US", "凤凰城": "US", "休斯顿": "US", "硅谷": "US", "俄勒冈": "US", "弗吉尼亚": "US",
    "TWN": "TW", "TPE": "TW", "KHH": "TW", "HINET": "TW", "APTG": "TW", "TSTAR": "TW", "CHTTL": "TW", "CHIEF": "TW",
    "台湾": "TW", "台北": "TW", "新北": "TW", "彰化": "TW", "台中": "TW", "高雄": "TW", "桃园": "TW", "中涌": "TW", "中华电信": "TW", "亚太电信": "TW",
    "JPN": "JP", "TYO": "JP", "OSA": "JP", "NRT": "JP", "HND": "JP", "KIX": "JP", "ITM": "JP", "KDDI": "JP", "IIJ": "JP", "NTT": "JP", "SOFTBANK": "JP", "LINODE": "JP", "GCP": "JP", "VULTR": "JP",
    "日本": "JP", "东京": "JP", "大阪": "JP", "埼玉": "JP", "琦玉": "JP", "川崎": "JP", "千叶": "JP", "冲绳": "JP", "北海道": "JP", "横滨": "JP", "名古屋": "JP", "福冈": "JP",
    "SGP": "SG", "SIN": "SG", "AWS": "SG", "DO": "SG", "DIGITALOCEAN": "SG", "OVH": "SG",
    "新加坡": "SG", "狮城": "SG", "坡县": "SG", "星国": "SG",
    "HKG": "HK", "HKT": "HK", "HKBN": "HK", "PCCW": "HK", "WTT": "HK", "HGC": "HK", "香港": "HK", "港岛": "HK"
}

COUNTRY_MAP = {k: v for k, v in _BASE_MAP.items()}
for k, v in _ALIASES.items():
    if v in _BASE_MAP: COUNTRY_MAP[k.upper()] = _BASE_MAP[v]

CHINESE_ALIASES_SORTED = sorted([k for k in _ALIASES.keys() if re.search(r'[\u4e00-\u9fa5]', k)], key=len, reverse=True)

def get(url):
    try:
        hd = {"User-Agent": "Mozilla/5.0"}
        return requests.get(url, timeout=12, headers=hd).text
    except: return ""

def get_only_ip(raw):
    ip4 = IPV4_REG.search(raw)
    ip6 = IPV6_REG.search(raw)
    if ip4: return ip4.group()
    if ip6: return ip6.group()
    return None

def is_ad_domain(text):
    if re.search(r'[\u4e00-\u9fa5]', text): return False
    return bool(re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\-\.]*\.[a-zA-Z]{2,}$", text.strip()))

def rebuild_line(raw):
    parts = raw.split("#", 1)
    base = parts[0].strip()
    remark = parts[1].strip() if len(parts) > 1 else ""

    ip = get_only_ip(base)
    is_ipv6 = bool(IPV6_REG.search(base))
    
    if not remark:
        if is_ipv6: remark = "IPV6"
        elif ip: remark = ip
        else: remark = base.split(":")[0]

    raw_remark_parts = [p.strip() for p in remark.split("|") if p.strip()]
    valid_parts = []
    for p in raw_remark_parts:
        clean_p = re.sub(r'[\[\]]', '', p)
        if re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?", p): continue
        if IPV6_REG.search(clean_p) and len(clean_p) >= 11: continue
        if is_ad_domain(p) and p not in ALLOWED_DOMAINS: continue
        if re.search(r'(?i)\d+(\.\d+)?\s*(ms|mbps|gbps|kb/s|mb/s|m|g)', p): continue
        if re.search(r'\d{2}-\d{2}\s\d{2}:\d{2}', p): continue
        p = re.sub(r'[▼▲]', '', p).strip()
        p = re.sub(r'^(CF优选-|优选-|CF-)', '', p)
        if not p or p.upper() in ["CF", "4", "CF-4", "优选", "DEFAULT", "ANYCAST", "NONE", "IPV6", "优选IPV6"]: continue
        valid_parts.append(p)

    country_info = None; custom_name = None; rest_parts = []
    for p in valid_parts:
        upper_p = p.upper()
        if upper_p in COUNTRY_MAP:
            if not country_info: country_info = COUNTRY_MAP[upper_p]
            continue
        is_flag = False
        for mapped_val in set(COUNTRY_MAP.values()):
            if mapped_val in p:
                if not country_info: country_info = mapped_val
                is_flag = True; break
        if is_flag: continue
        found_alias = None
        for alias in CHINESE_ALIASES_SORTED:
            if (len(alias) >= 2 and alias in p) or alias == p:
                found_alias = alias; break
        if found_alias and not country_info:
            country_info = COUNTRY_MAP[found_alias.upper()]
        if not country_info:
            m = re.search(r'(?i)\b([A-Z]{2,4})\b', p)
            if m and m.group(1).upper() in COUNTRY_MAP: country_info = COUNTRY_MAP[m.group(1).upper()]
        if custom_name is None: custom_name = p
        else: rest_parts.append(p)
            
    new_remark_list = []
    if country_info: new_remark_list.append(country_info)
    if is_ipv6 and ip: new_remark_list.append("IPV6")
    if custom_name: new_remark_list.append(custom_name)
    new_remark_list.extend(rest_parts)
    
    new_remark = " | ".join(new_remark_list)
    if not new_remark:
        if is_ipv6: new_remark = "IPV6"
        elif ip: new_remark = ip
        else: new_remark = base.split(":")[0]
        
    return f"{base}#{new_remark}"

def process_domain_item(raw_item):
    parts = raw_item.split("#", 1)
    base = parts[0].strip()
    original_remark = parts[1].strip() if len(parts) > 1 else ""

    port = "443"
    host = base
    if "]:" in base:
        host, port = base.rsplit("]:", 1)
        host = host.lstrip("[")
    elif base.count(":") == 1:
        host, port = base.split(":", 1)

    remark = original_remark if original_remark else host
    base_addr = f"[{host}]:{port}" if ":" in host else f"{host}:{port}"
    return host, rebuild_line(f"{base_addr}#{remark}")

def main():
    seen_addresses = set(); final_lines = []
    
    for api in API_LIST:
        txt = get(api)
        for line in txt.splitlines():
            s = line.strip()
            if not s: continue
            base = s.split("#", 1)[0].strip()
            addr = get_only_ip(base)
            if not addr or addr in seen_addresses: continue
            seen_addresses.add(addr)
            final_lines.append(rebuild_line(s))
            
    for raw_item in DOMAIN_LIST:
        host, rebuilt_line = process_domain_item(raw_item)
        if host not in seen_addresses:
            seen_addresses.add(host)
            final_lines.append(rebuilt_line)
            
    with open("max.txt", "w", encoding="utf-8") as f:
        for item in final_lines: f.write(item + "\n")

if __name__ == "__main__": main()
