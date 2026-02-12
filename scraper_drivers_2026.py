import json
import os

def generate_drivers_2026():
    # 2026 赛季车手与车队 Slug 映射表 (基于官方 2026 CDN 规则)
    # 规则: https://media.formula1.com/image/upload/c_lfill,w_440/q_auto/d_common:f1:2026:fallback:driver:2026fallbackdriverright.webp/v1740000000/common/f1/2026/[TEAM_SLUG]/[DRIVER_ID]/2026[TEAM_SLUG][DRIVER_ID]right.webp
    
    TEAM_SLUGS = {
        "Ferrari": "ferrari",
        "Red Bull": "redbullracing",
        "Mercedes": "mercedes",
        "McLaren": "mclaren",
        "Aston Martin": "astonmartin",
        "Williams": "williams",
        "Alpine": "alpine",
        "Haas": "haas",
        "Audi": "audi",
        "Racing Bulls": "racingbulls",
        "Cadillac": "cadillac"
    }

    # 车手 ID 生成器 (Heuristic: First 3 + Last 3 + 01)
    def get_driver_id(first, last):
        # 特例处理
        overrides = {
            "Lewis Hamilton": "lewham01",
            "Max Verstappen": "maxver01",
            "Charles Leclerc": "chalec01",
            "Lando Norris": "lannor01",
            "Oscar Piastri": "oscpia01",
            "George Russell": "georus01",
            "Andrea Kimi Antonelli": "andant01",
            "Kimi Antonelli": "andant01",
            "Fernando Alonso": "feralo01",
            "Lance Stroll": "lanstr01",
            "Carlos Sainz": "carsai01",
            "Alexander Albon": "alealb01",
            "Pierre Gasly": "piegas01",
            "Franco Colapinto": "fracol01",
            "Esteban Ocon": "estoco01",
            "Oliver Bearman": "olibea01",
            "Nico Hulkenberg": "nichul01",
            "Gabriel Bortoleto": "gabbor01",
            "Liam Lawson": "lialaw01",
            "Arvid Lindblad": "arvlin01",
            "Sergio Perez": "serper01",
            "Valtteri Bottas": "valbot01",
            "Isack Hadjar": "isahad01"
        }
        full_name = f"{first} {last}"
        if full_name in overrides:
            return overrides[full_name]
        
        # 默认算法
        f = first.lower()[:3]
        l = last.lower()[:3]
        return f"{f}{l}01"

    # 基础数据
    drivers_raw = [
        {"firstName": "Lewis", "lastName": "Hamilton", "firstNameCn": "刘易斯", "lastNameCn": "汉密尔顿", "code": "HAM", "number": 44, "team": "Ferrari", "teamCn": "法拉利", "country": "United Kingdom"},
        {"firstName": "Max", "lastName": "Verstappen", "firstNameCn": "马克斯", "lastNameCn": "维斯塔潘", "code": "VER", "number": 1, "team": "Red Bull", "teamCn": "红牛", "country": "Netherlands"},
        {"firstName": "Charles", "lastName": "Leclerc", "firstNameCn": "夏尔", "lastNameCn": "勒克莱尔", "code": "LEC", "number": 16, "team": "Ferrari", "teamCn": "法拉利", "country": "Monaco"},
        {"firstName": "Lando", "lastName": "Norris", "firstNameCn": "兰多", "lastNameCn": "诺里斯", "code": "NOR", "number": 4, "team": "McLaren", "teamCn": "迈凯伦", "country": "United Kingdom"},
        {"firstName": "Oscar", "lastName": "Piastri", "firstNameCn": "奥斯卡", "lastNameCn": "皮亚斯特里", "code": "PIA", "number": 81, "team": "McLaren", "teamCn": "迈凯伦", "country": "Australia"},
        {"firstName": "George", "lastName": "Russell", "lastName": "Russell", "firstNameCn": "乔治", "lastNameCn": "拉塞尔", "code": "RUS", "number": 63, "team": "Mercedes", "teamCn": "梅赛德斯", "country": "United Kingdom"},
        {"firstName": "Kimi", "lastName": "Antonelli", "firstNameCn": "安德里亚", "lastNameCn": "安东内利", "code": "ANT", "number": 12, "team": "Mercedes", "teamCn": "梅赛德斯", "country": "Italy"},
        {"firstName": "Fernando", "lastName": "Alonso", "firstNameCn": "费尔南多", "lastNameCn": "阿隆索", "code": "ALO", "number": 14, "team": "Aston Martin", "teamCn": "阿斯顿·马丁", "country": "Spain", "bioCn": "迈克尔·舒马赫是 2000 年代初期一级方程式赛车当之无愧的王者，他获胜和夺冠的速度在当时简直闻所未闻。只有非常特别的人才能将这位法拉利传奇从王座上拉下来——而正是费尔南多·阿隆索做到了这一点，这足以说明这位西班牙车手的一切。\n\n阿隆索极具竞争力，他对自己的才华直言不讳，评价自己在“每一项”上都是 9/10，业内很少有人会对此表示异议。他在 F1 中的表现以惊人的速度、出色的战术思维、示范性的驾驶技术、对细节的敏锐洞察以及对胜利的不懈决心为特征。\n\n早年间，他是一名连破纪录的车手，曾一度是 F1 最年轻的杆位获得者、分站冠军、世界冠军和两届世界冠军，当时他在雷诺车队取得了巨大的成功。然而，即使是阿隆索也无法在职业生涯后期延续这种惊人的势头，尽管效力过迈凯伦和法拉利，但他没能为自己的收藏增添另一个冠军头衔。\n\n在离开 F1 两年后（期间他在勒芒获得了两场胜利），阿隆索于 2021 年随阿尔卑车队回归。他的速度和决心丝毫未减，在那一年重返领奖台，但由于可靠性不佳以及缺乏长期合同，他在随后的赛季感到沮丧，并选择再次跳槽。\n\n在加入阿斯顿·马丁的首个赛季获得 8 次领奖台之后，他已成为首位达成 400 场大奖赛首发的车手。随着技术传奇安德里安·纽维的加入，阿隆索希望这支绿色车队最终能让他重回胜利之路，因为他在 F1 还有未竟的事业……"},
        {"firstName": "Lance", "lastName": "Stroll", "firstNameCn": "兰斯", "lastNameCn": "斯特罗尔", "code": "STR", "number": 18, "team": "Aston Martin", "teamCn": "阿斯顿·马丁", "country": "Canada"},
        {"firstName": "Carlos", "lastName": "Sainz", "firstNameCn": "卡洛斯", "lastNameCn": "赛恩斯", "code": "SAI", "number": 55, "team": "Williams", "teamCn": "威廉姆斯", "country": "Spain"},
        {"firstName": "Alexander", "lastName": "Albon", "firstNameCn": "亚历山大", "lastNameCn": "阿尔本", "code": "ALB", "number": 23, "team": "Williams", "teamCn": "威廉姆斯", "country": "Thailand"},
        {"firstName": "Pierre", "lastName": "Gasly", "firstNameCn": "皮埃尔", "lastNameCn": "加斯利", "code": "GAS", "number": 10, "team": "Alpine", "teamCn": "阿尔派", "country": "France"},
        {"firstName": "Franco", "lastName": "Colapinto", "firstNameCn": "弗朗哥", "lastNameCn": "科拉平托", "code": "COL", "number": 43, "team": "Alpine", "teamCn": "阿尔派", "country": "Argentina"},
        {"firstName": "Esteban", "lastName": "Ocon", "firstNameCn": "埃斯特班", "lastNameCn": "奥康", "code": "OCO", "number": 31, "team": "Haas", "teamCn": "哈斯", "country": "France"},
        {"firstName": "Oliver", "lastName": "Bearman", "firstNameCn": "奥利弗", "lastNameCn": "比尔曼", "code": "BEA", "number": 87, "team": "Haas", "teamCn": "哈斯", "country": "United Kingdom"},
        {"firstName": "Nico", "lastName": "Hulkenberg", "firstNameCn": "尼科", "lastNameCn": "霍肯伯格", "code": "HUL", "number": 27, "team": "Audi", "teamCn": "奥迪 (Sauber)", "country": "Germany"},
        {"firstName": "Gabriel", "lastName": "Bortoleto", "firstNameCn": "加布里埃尔", "lastNameCn": "博托莱托", "code": "BOR", "number": 5, "team": "Audi", "teamCn": "奥迪 (Sauber)", "country": "Brazil"},
        {"firstName": "Liam", "lastName": "Lawson", "firstNameCn": "利亚姆", "lastNameCn": "劳森", "code": "LAW", "number": 30, "team": "Racing Bulls", "teamCn": "RB", "country": "New Zealand"},
        {"firstName": "Arvid", "lastName": "Lindblad", "firstNameCn": "阿尔维德", "lastNameCn": "林德布拉德", "code": "LIN", "number": 17, "team": "Racing Bulls", "teamCn": "RB", "country": "United Kingdom"},
        {"firstName": "Sergio", "lastName": "Perez", "firstNameCn": "塞尔吉奥", "lastNameCn": "佩雷兹", "code": "PER", "number": 11, "team": "Cadillac", "teamCn": "凯迪拉克", "country": "Mexico"},
        {"firstName": "Valtteri", "lastName": "Bottas", "firstNameCn": "瓦尔特利", "lastNameCn": "博塔斯", "code": "BOT", "number": 77, "team": "Cadillac", "teamCn": "凯迪拉克", "country": "Finland"},
        {"firstName": "Isack", "lastName": "Hadjar", "firstNameCn": "艾萨克", "lastNameCn": "哈贾尔", "code": "HAD", "number": 20, "team": "Red Bull", "teamCn": "红牛", "country": "France"}
    ]

    processed = []
    for d in drivers_raw:
        driver_id = get_driver_id(d['firstName'], d['lastName'])
        team_slug = TEAM_SLUGS.get(d['team'], d['team'].lower().replace(" ", ""))
        
        # 构建 2026 官方 URL
        image_url = f"https://media.formula1.com/image/upload/c_lfill,w_440/q_auto/d_common:f1:2026:fallback:driver:2026fallbackdriverright.webp/v1740000000/common/f1/2026/{team_slug}/{driver_id}/2026{team_slug}{driver_id}right.webp"
        
        d['id'] = driver_id.replace("01", "") # 前端习惯 ID
        d['image'] = image_url
        processed.append(d)

    os.makedirs("data", exist_ok=True)
    with open("data/drivers_2026.json", 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully generated {len(processed)} drivers with official 2026 image URLs.")

if __name__ == "__main__":
    generate_drivers_2026()
