import re
import requests
import socket

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
IPV6_REG = re.compile(r"([0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F]{0,4}")

_BASE_MAP = {
    "US": "🇺🇸 美国", "HK": "🇭🇰 香港", "SG": "🇸🇬 新加坡", "JP": "🇯🇵 日本",
    "KR": "🇰🇷 韩国", "TW": "🇹🇼 台湾", "GB": "🇬🇧 英国", "DE": "🇩🇪 德国",
    "NL": "🇳🇱 荷兰", "FR": "🇫🇷 法国", "AU": "🇦🇺 澳大利亚", "CA": "🇨🇦 加拿大",
    "IN": "🇮🇳 印度", "BR": "🇧🇷 巴西", "ZA": "🇿🇦 南非", "RU": "🇷🇺 俄罗斯",
    "MY": "🇲🇾 马来西亚", "ID": "🇮🇩 印尼", "TH": "🇹🇭 泰国", "VN": "🇻🇳 越南",
    "PH": "🇵🇭 菲律宾", "AE": "🇦🇪 阿联酋", "MO": "🇲🇴 澳门", "CN": "🇨🇳 中国",
    "IT": "🇮🇹 意大利", "ES": "🇪🇸 西班牙", "CH": "🇨🇭 瑞士", "SE": "🇸🇪 瑞典",
    "NO": "🇳🇴 挪威", "DK": "🇩🇰 丹麦", "FI": "🇫🇮 芬兰", "PL": "🇵🇱 波兰",
    "TR": "🇹🇷 土耳其", "AR": "🇦🇷 阿根廷", "MX": "🇲🇽 墨西哥", "IE": "🇮🇪 爱尔兰",
    "IL": "🇮🇱 以色列", "NZ": "🇳🇿 新西兰", "AT": "🇦🇹 奥地利", "CL": "🇨🇱 智利",
    "PE": "🇵🇪 秘鲁", "RO": "🇷🇴 罗马尼亚", "BG": "🇧🇬 保加利亚", "HU": "🇭🇺 匈牙利",
    "CZ": "🇨🇿 捷克", "GR": "🇬🇷 希腊", "PT": "🇵🇹 葡萄牙", "IS": "🇮🇸 冰岛",
    "KZ": "🇰🇿 哈萨克斯坦", "UZ": "🇺🇿 乌兹别克斯坦", "PK": "🇵🇰 巴基斯坦",
    "NG": "🇳🇬 尼日利亚", "EG": "🇪🇬 埃及"
}

_ALIASES = {
    "HKG": "HK", "HKT": "HK", "HKBN": "HK", "PCCW": "HK", "WTT": "HK", "HGC": "HK", 
    "香港": "HK", "港岛": "HK", "深港": "HK", "广港": "HK", "沪港": "HK", "京港": "HK", "港": "HK",
    "TWN": "TW", "TPE": "TW", "KHH": "TW", "HINET": "TW", "APTG": "TW", "TSTAR": "TW",
    "台湾": "TW", "台北": "TW", "新北": "TW", "彰化": "TW", "台中": "TW", "高雄": "TW", "台": "TW",
    "JPN": "JP", "TYO": "JP", "OSA": "JP", "NRT": "JP", "HND": "JP", "KIX": "JP", "ITM": "JP", "KDDI": "JP", "IIJ": "JP",
    "日本": "JP", "东京": "JP", "大阪": "JP", "埼玉": "JP", "琦玉": "JP", "川崎": "JP", "千叶": "JP", "冲绳": "JP", "北海道": "JP", "沪日": "JP", "日": "JP",
    "KOR": "KR", "SEL": "KR", "ICN": "KR", "GMP": "KR",
    "韩国": "KR", "首尔": "KR", "春川": "KR", "仁川": "KR", "韩": "KR",
    "SGP": "SG", "SIN": "SG",
    "新加坡": "SG", "狮城": "SG", "坡县": "SG", "星国": "SG", "新": "SG",
    "USA": "US", "LAX": "US", "SJC": "US", "SFO": "US", "SEA": "US", "NYC": "US", "JFK": "US", "EWR": "US", "DFW": "US", "ORD": "US", "MIA": "US", "ATL": "US", "IAD": "US", "PDX": "US", "PHX": "US",
    "美国": "US", "洛杉矶": "US", "圣何塞": "US", "圣塔克拉拉": "US", "芝加哥": "US", "西雅图": "US", "纽约": "US", "达拉斯": "US", "迈阿密": "US", "亚特兰大": "US", "华盛顿": "US", "波特兰": "US", "硅谷": "US", "旧金山": "US", "美": "US",
    "GBR": "GB", "LHR": "GB", "LON": "GB", "英国": "GB", "伦敦": "GB",
    "DEU": "DE", "FRA": "DE", "MUC": "DE", "BER": "DE", "德国": "DE", "法兰克福": "DE", "慕尼黑": "DE", "柏林": "DE",
    "NLD": "NL", "AMS": "NL", "荷兰": "NL", "阿姆斯特丹": "NL",
    "FRA": "FR", "CDG": "FR", "PAR": "FR", "法国": "FR", "巴黎": "FR",
    "AUS": "AU", "SYD": "AU", "MEL": "AU", "BNE": "AU", "澳大利亚": "AU", "澳洲": "AU", "悉尼": "AU", "墨尔本": "AU", "布里斯班": "AU",
    "CAN": "CA", "YVR": "CA", "YYZ": "CA", "YUL": "CA", "加拿大": "CA", "多伦多": "CA", "温哥华": "CA", "蒙特利尔": "CA",
    "IND": "IN", "BOM": "IN", "DEL": "IN", "印度": "IN", "孟买": "IN", "新德里": "IN",
    "RUS": "RU", "SVO": "RU", "VVO": "RU", "KHV": "RU", "俄罗斯": "RU", "莫斯科": "RU", "圣彼得堡": "RU", "伯力": "RU", "海参崴": "RU", "新西伯利亚": "RU",
    "ZAF": "ZA", "JNB": "ZA", "南非": "ZA", "约翰内斯堡": "ZA",
    "BRA": "BR", "GRU": "BR", "SAO": "BR", "巴西": "BR", "圣保罗": "BR",
    "MYS": "MY", "KUL": "MY", "马来西亚": "MY", "吉隆坡": "MY",
    "IDN": "ID", "CGK": "ID", "印尼": "ID", "印度尼西亚": "ID", "雅加达": "ID",
    "THA": "TH", "BKK": "TH", "泰国": "TH", "曼谷": "TH",
    "VNM": "VN", "SGN": "VN", "HAN": "VN", "越南": "VN", "胡志明市": "VN", "河内": "VN",
    "PHL": "PH", "MNL": "PH", "菲律宾": "PH", "马尼拉": "PH",
    "ARE": "AE", "DXB": "AE", "阿联酋": "AE", "迪拜": "AE",
    "MAC": "MO", "MFM": "MO", "澳门": "MO", "澳": "MO", "中国": "CN",
    "ITA": "IT", "MIL": "IT", "ROM": "IT", "意大利": "IT", "米兰": "IT", "罗马": "IT",
    "ESP": "ES", "MAD": "ES", "西班牙": "ES", "马德里": "ES",
    "CHE": "CH", "ZRH": "CH", "GVA": "CH", "瑞士": "CH", "苏黎世": "CH", "日内瓦": "CH",
    "SWE": "SE", "STO": "SE", "瑞典": "SE", "斯德哥尔摩": "SE"
}

COUNTRY_MAP = {k: v for k, v in _BASE_MAP.items()}
for k, v in _ALIASES.items():
    if v in _BASE_MAP:
        COUNTRY_MAP[k.upper()] = _BASE_MAP[v]

CHINESE_ALIASES_SORTED = sorted([k for k in _ALIASES.keys() if re.search(r'[\u4e00-\u9fa5]', k)], key=len, reverse=True)

def get(url):
    try:
        hd = {"User-Agent": "Mozilla/5.0"}
        return requests.get(url, timeout=12, headers=hd).text
    except:
        return ""

def get_only_ip(raw):
    ip4 = IPV4_REG.search(raw)
    ip6 = IPV6_REG.search(raw)
    if ip4:
        return ip4.group()
    if ip6:
        return ip6.group()
    return None

def is_ad_domain(text):
    if re.search(r'[\u4e00-\u9fa5]', text):
        return False
    return bool(re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\-\.]*\.[a-zA-Z]{2,}$", text.strip()))

def rebuild_line(raw):
    ip = get_only_ip(raw)
    if not ip: return raw
    is_ipv6 = ":" in ip
    parts = raw.split("#", 1)
    base = parts[0]
    remark = parts[1] if len(parts) > 1 else ""
    if is_ipv6: return f"{base}#优选IPV6"
    if not remark: return f"{base}#{ip}"

    raw_remark_parts = [p.strip() for p in remark.split("|") if p.strip()]
    valid_parts = []
    
    for p in raw_remark_parts:
        if re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{1,5})?", p):
            continue
        if is_ad_domain(p):
            continue
        if re.search(r'(?i)\d+(\.\d+)?\s*(ms|mbps|gbps|kb/s|mb/s|m|g)', p):
            continue
        p = re.sub(r'^(CF优选-|优选-|CF-)', '', p)
        if not p or p.upper() in ["CF", "4", "CF-4", "优选"]:
            continue
        valid_parts.append(p)

    country_info = None
    custom_name = None
    rest_parts = []
    
    for p in valid_parts:
        upper_p = p.upper()
        if upper_p in COUNTRY_MAP:
            if not country_info: country_info = COUNTRY_MAP[upper_p]
            continue
        is_flag = False
        for mapped_val in set(COUNTRY_MAP.values()):
            if mapped_val in p:
                if not country_info: country_info = mapped_val
                is_flag = True
                break
        if is_flag:
            continue
        found_alias = None
        for alias in CHINESE_ALIASES_SORTED:
            if (len(alias) >= 2 and alias in p) or alias == p:
                found_alias = alias
                break
        if found_alias and not country_info:
            country_info = COUNTRY_MAP[found_alias.upper()]
        if not country_info:
            m = re.search(r'(?i)\b([A-Z]{2,4})\b', p)
            if m and m.group(1).upper() in COUNTRY_MAP:
                country_info = COUNTRY_MAP[m.group(1).upper()]
        if custom_name is None:
            custom_name = p
        else:
            rest_parts.append(p)
            
    new_remark_list = []
    if country_info:
        new_remark_list.append(country_info)
    if custom_name:
        new_remark_list.append(custom_name)
    new_remark_list.extend(rest_parts)
    
    new_remark = " | ".join(new_remark_list)
    if not new_remark:
        new_remark = ip
        
    return f"{base}#{new_remark}"

def domain_to_lines(domain):
    out = []
    try:
        addr = socket.getaddrinfo(domain, 443)
        for item in addr:
            ip = item[4][0]
            is_ipv6 = ":" in ip
            if is_ipv6:
                base = f"[{ip}]:443" if not ip.startswith("[") else f"{ip}:443"
                remark = "优选IPV6"
            else:
                base = f"{ip}:443"
                remark = ip
            out.append([ip, f"{base}#{remark}"])
    except:
        pass
    return out

def main():
    ip_seen = set()
    final_lines = []
    for api in API_LIST:
        txt = get(api)
        lines = txt.splitlines()
        for line in lines:
            s = line.strip()
            if not s: continue
            ip = get_only_ip(s)
            if not ip or ip in ip_seen: continue
            ip_seen.add(ip)
            new_line = rebuild_line(s)
            final_lines.append(new_line)
    for d in DOMAIN_LIST:
        d_list = domain_to_lines(d)
        for real_ip, line in d_list:
            if real_ip not in ip_seen:
                ip_seen.add(real_ip)
                final_lines.append(line)
    with open("max.txt", "w", encoding="utf-8") as f:
        for item in final_lines:
            f.write(item + "\n")

if __name__ == "__main__":
    main()
