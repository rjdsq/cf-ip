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

# --- 核心字典：映射到最终的带国旗标准名称 ---
_BASE_MAP = {
    "US": "🇺🇸 美国", "HK": "🇭🇰 香港", "SG": "🇸🇬 新加坡", "JP": "🇯🇵 日本",
    "KR": "🇰🇷 韩国", "TW": "🇹🇼 台湾", "GB": "🇬🇧 英国", "DE": "🇩🇪 德国",
    "NL": "🇳🇱 荷兰", "FR": "🇫🇷 法国", "AU": "🇦🇺 澳大利亚", "CA": "🇨🇦 加拿大",
    "IN": "🇮🇳 印度", "BR": "🇧🇷 巴西", "ZA": "🇿🇦 南非", "RU": "🇷🇺 俄罗斯",
    "MY": "🇲🇾 马来西亚", "ID": "🇮🇩 印尼", "TH": "🇹🇭 泰国", "VN": "🇻🇳 越南",
    "PH": "🇵🇭 菲律宾", "AE": "🇦🇪 阿联酋", "MO": "🇲🇴 澳门", "CN": "🇨🇳 中国",
    "IT": "🇮🇹 意大利", "ES": "🇪🇸 西班牙", "CH": "🇨🇭 瑞士", "SE": "🇸🇪 瑞典",
    "NO": "🇳🇴 挪威", "DK": "🇩🇰 丹麦", "FI": "🇫🇮 芬兰", "PL": "🇵🇱 波兰",
    "TR": "🇹🇷 土耳其", "AR": "🇦🇷 阿根廷", "MX": "🇲🇽 墨西哥"
}

# --- 扩展别名词典：支持各种机场代码、城市、别称 ---
_ALIASES = {
    # 机场代码 / 缩写
    "USA": "US", "LAX": "US", "SJC": "US", "FRA": "DE", "NRT": "JP", "HND": "JP",
    "HKG": "HK", "SGP": "SG", "JPN": "JP", "KOR": "KR", "GBR": "GB",
    "SIN": "SG", "LHR": "GB", "SYD": "AU", "YVR": "CA", "TPE": "TW", "ICN": "KR",
    "KIX": "JP", "CDG": "FR", "AMS": "NL", "BOM": "IN", "IAD": "US", "EWR": "US",
    "LGA": "US", "JFK": "US", "SFO": "US", "SEA": "US", "ORD": "US", "DFW": "US",
    "MIA": "US", "ATL": "US", "BNE": "AU", "MEL": "AU", "MAD": "ES", "MIL": "IT",
    "KUL": "MY", "BKK": "TH", "DXB": "AE", "GRU": "BR",
    # 常用中文地名/别称
    "美国": "US", "洛杉矶": "US", "圣何塞": "US", "芝加哥": "US", "西雅图": "US", "纽约": "US", "达拉斯": "US",
    "香港": "HK", "港岛": "HK", "深港": "HK", "广港": "HK", "新加坡": "SG", "狮城": "SG",
    "日本": "JP", "东京": "JP", "大阪": "JP", "沪日": "JP",
    "韩国": "KR", "首尔": "KR", "春川": "KR",
    "台湾": "TW", "台北": "TW", "新北": "TW", "彰化": "TW",
    "英国": "GB", "伦敦": "GB",
    "德国": "DE", "法兰克福": "DE", "慕尼黑": "DE",
    "荷兰": "NL", "阿姆斯特丹": "NL",
    "法国": "FR", "巴黎": "FR",
    "澳大利亚": "AU", "澳洲": "AU", "悉尼": "AU", "墨尔本": "AU",
    "加拿大": "CA", "多伦多": "CA", "温哥华": "CA",
    "印度": "IN", "孟买": "IN", "新德里": "IN",
    "巴西": "BR", "圣保罗": "BR",
    "南非": "ZA", "约翰内斯堡": "ZA",
    "俄罗斯": "RU", "莫斯科": "RU", "圣彼得堡": "RU",
    "马来西亚": "MY", "吉隆坡": "MY",
    "印尼": "ID", "印度尼西亚": "ID", "雅加达": "ID",
    "泰国": "TH", "曼谷": "TH",
    "越南": "VN", "胡志明市": "VN", "河内": "VN",
    "菲律宾": "PH", "马尼拉": "PH",
    "阿联酋": "AE", "迪拜": "AE",
    "澳门": "MO", "中国": "CN",
    "意大利": "IT", "米兰": "IT", "罗马": "IT",
    "西班牙": "ES", "马德里": "ES",
    "瑞士": "CH", "苏黎世": "CH"
}

# 构建合并的查询表
COUNTRY_MAP = {k: v for k, v in _BASE_MAP.items()}
for k, v in _ALIASES.items():
    if v in _BASE_MAP:
        COUNTRY_MAP[k.upper()] = _BASE_MAP[v]

# 中文别名按长度降序排序，优先匹配长词（防止“港”等短词误杀）
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
    # 识别类似 cf.877774.xyz / saas.sin.fan 的域名广告
    # 域名一般不含中文
    if re.search(r'[\u4e00-\u9fa5]', text):
        return False
    # 匹配字母数字开头，中间有点，字母结尾的常见域名格式
    return bool(re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\-\.]*\.[a-zA-Z]{2,}$", text.strip()))

def rebuild_line(raw):
    ip = get_only_ip(raw)
    if not ip:
        return raw

    is_ipv6 = ":" in ip
    parts = raw.split("#", 1)
    base = parts[0]
    remark = parts[1] if len(parts) > 1 else ""

    # IPv6 无脑替换
    if is_ipv6:
        return f"{base}#优选IPV6"

    if not remark:
        return f"{base}#{ip}"

    raw_remark_parts = [p.strip() for p in remark.split("|") if p.strip()]
    
    valid_parts = []
    # 【清洗过滤】：删掉尾部跟IP一样的段落、删掉广告域名
    for p in raw_remark_parts:
        # 如果这段文本就是 IP，丢弃
        if p == ip or re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", p):
            continue
        # 如果是域名广告，丢弃
        if is_ad_domain(p):
            continue
        valid_parts.append(p)

    country_info = None
    custom_name = None
    rest_parts = []
    
    # 【智能匹配】：提取地区、分离定制名字
    for p in valid_parts:
        upper_p = p.upper()
        
        # 1. 完全匹配机场代码或中文名 (如 LAX, HKG, 狮城)
        if upper_p in COUNTRY_MAP:
            if not country_info: country_info = COUNTRY_MAP[upper_p]
            continue # 这是纯地理位置，提纯后丢弃原段落
            
        # 2. 已经包含了完整的国旗+名字
        is_flag = False
        for mapped_val in set(COUNTRY_MAP.values()):
            if mapped_val in p:
                if not country_info: country_info = mapped_val
                is_flag = True
                break
        if is_flag:
            continue
            
        # 3. 包含中文别名（如 “港岛古惑” 中包含 “港岛”）
        found_alias = None
        for alias in CHINESE_ALIASES_SORTED:
            if len(alias) >= 2 and alias in p:
                found_alias = alias
                break
        if found_alias and not country_info:
            country_info = COUNTRY_MAP[found_alias.upper()]
                
        # 4. 隐式包含机场英文简写（如 "移动-LAX"）
        if not country_info:
            m = re.search(r'(?i)\b([A-Z]{2,3})\b', p)
            if m and m.group(1).upper() in COUNTRY_MAP:
                country_info = COUNTRY_MAP[m.group(1).upper()]
                
        # 提取完位置信息后，不是纯地点的文字，留作定制名
        if custom_name is None:
            custom_name = p
        else:
            rest_parts.append(p)
            
    # 【重组拼装】：国旗 -> 定制名 -> 其他信息
    new_remark_list = []
    if country_info:
        new_remark_list.append(country_info)
    if custom_name:
        new_remark_list.append(custom_name)
    new_remark_list.extend(rest_parts)
    
    new_remark = " | ".join(new_remark_list)
    
    # 智能兜底：如果广告被删空了，或者根本没文字，就用 IP
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
                # 域名解析出来的IPv4，备注不要用域名，直接用IP
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
            if not s:
                continue
            ip = get_only_ip(s)
            if not ip or ip in ip_seen:
                continue
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
