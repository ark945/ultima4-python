import json
import re
from pathlib import Path
from .constants import VIRTUES

U4PY_DIR = Path(__file__).resolve().parent.parent
U4_CHT_DUMPS = Path("d:/MyLab/u4-cht/dumps")

# In-memory translation caches
_exact_cache = {}
_regex_rules = []

VIRTUE_ZH = {
    "Honesty": "誠實",
    "Compassion": "慈悲",
    "Valor": "勇敢",
    "Justice": "正義",
    "Sacrifice": "犧牲",
    "Honor": "榮譽",
    "Spirituality": "靈性",
    "Humility": "謙卑"
}

CLASS_ZH = {
    "Mage": "法師",
    "Bard": "吟遊詩人",
    "Fighter": "鬥士",
    "Druid": "德魯伊",
    "Tinker": "工匠",
    "Paladin": "聖騎士",
    "Ranger": "遊俠",
    "Shepherd": "牧羊人"
}

ITEM_ZH = {
    "Sulfur Ash": "硫磺灰",
    "Ginseng": "人蔘",
    "Garlic": "大蒜",
    "Spider Silk": "蜘蛛絲",
    "Blood Moss": "血苔",
    "Black Pearl": "黑珍珠",
    "Nightshade": "龍葵",
    "Mandrake": "曼陀羅",
    "Rations": "糧食",
    "Gems": "寶石",
    "Torches": "火把",
    "Keys": "鑰匙",
    "Sextant": "六分儀",
    "Skull": "骷髏",
    "Candle": "蠟燭",
    "Book": "典籍",
    "Bell": "法鐘",
    "Horn": "號角",
    "Wheel": "船舵"
}

def clean_key(s):
    if not s:
        return ""
    return "".join(s.split()).lower().replace("\n", "").replace("\r", "")

def init_translation():
    global _exact_cache, _regex_rules
    _exact_cache = {}
    
    # 1. Load virtue translations
    for en, zh in VIRTUE_ZH.items():
        _exact_cache[clean_key(en)] = zh
        _exact_cache[clean_key(f"the rune of {en}")] = f"{zh}之符記"
        _exact_cache[clean_key(f"The rune of {en}!")] = f"{zh}之符記！"
        _exact_cache[clean_key(f"Rune of {en}")] = f"{zh}之符記"
        
    # 2. Load classes & items
    for en, zh in CLASS_ZH.items():
        _exact_cache[clean_key(en)] = zh
    for en, zh in ITEM_ZH.items():
        _exact_cache[clean_key(en)] = zh

    # 3. Load u4-cht dumps
    for filename in ["hardcoded_strings.json", "vendor_bilingual.json", "ui_bilingual.json", "names_bilingual.json"]:
        filepath = U4_CHT_DUMPS / filename
        if not filepath.exists():
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Identify where the strings are stored (strings or sections)
            entries = data.get("strings", [])
            if not entries and "sections" in data:
                # Flat map sections
                for sec_name, sec_data in data["sections"].items():
                    entries.extend(sec_data.get("entries", []))
                    
            for entry in entries:
                en = entry.get("en", "")
                zh = entry.get("zh", "")
                if en and zh:
                    # Strip formatting symbols like %s, %d for matching or keep them for regex
                    _exact_cache[clean_key(en)] = zh
        except Exception as e:
            print(f"Error loading {filename}: {e}")


    # 3b. Load talk_bilingual.json for NPC names
    talk_filepath = U4_CHT_DUMPS / "talk_bilingual.json"
    if talk_filepath.exists():
        try:
            with open(talk_filepath, "r", encoding="utf-8") as f:
                talk_data = json.load(f)
            for entry in talk_data.get("npcs", []):
                fields = entry.get("fields", {})
                name_field = fields.get("name", {})
                en = name_field.get("en", "")
                zh = name_field.get("zh", "")
                if en and zh:
                    _exact_cache[clean_key(en)] = zh
        except Exception as e:
            print(f"Error loading talk_bilingual.json: {e}")

    # 4. Custom regex/pattern rules for dynamic python strings
    # (Many python format strings in shops.py/game.py do not exactly match C templates)
    
    # Readying weapons/armor
    _regex_rules.append((r"^(.+?) readies the (.+?)\.$", lambda m: f"{m.group(1)}已裝備{translate_term(m.group(2))}。"))
    _regex_rules.append((r"^(.+?) wears the (.+?)\.$", lambda m: f"{m.group(1)}已穿上{translate_term(m.group(2))}。"))
    
    # Finding chests/gold
    _regex_rules.append((r"^You open the chest and find (\d+) gold!$", lambda m: f"汝打開寶箱，發現了 {m.group(1)} 金幣！"))
    
    # Attacks
    _regex_rules.append((r"^(.+?) attacks!$", lambda m: f"{m.group(1)}發動攻擊！"))
    
    # Avatarhood and Shrines
    _regex_rules.append((r"^You enter the ancient Shrine of (.+?) and sit before the altar\.$", 
                         lambda m: f"汝進入古老的{translate_term(m.group(1))}聖壇，並在祭壇前坐下。"))
    _regex_rules.append((r"^Thou hast achieved partial Avatarhood in the Virtue of (.+?)!$", 
                         lambda m: f"汝已在{translate_term(m.group(1))}之美德中取得部分聖者資格！"))
    _regex_rules.append((r"^Thou hast already achieved Avatarhood in (.+?)!$", 
                         lambda m: f"汝已在{translate_term(m.group(1))}中取得聖者資格！"))
    _regex_rules.append((r"^Thou dost not bear the rune of entry!  A strange force keeps thee out!$", 
                         lambda m: "汝未帶有入場之符記！一股奇特的力量阻擋了汝！"))
    
    # Ships and boarding
    _regex_rules.append((r"^Board (.+?)!$", lambda m: f"登上{translate_term(m.group(1))}！"))
    
    # Coordinates / Sextant
    _regex_rules.append((r"^Locate position:\s*(\d+)([A-P])'(\d+)([A-P])'$", 
                         lambda m: f"定位位置：緯度 {m.group(1)}{m.group(2)}，經度 {m.group(3)}{m.group(4)}"))

    # Shops & Vendors
    _regex_rules.append((r"^Welcome to (.+?)!$", lambda m: f"歡迎光臨{m.group(1)}！"))
    _regex_rules.append((r"^(.+?) says:\s*May I interest you in some (.+?)\?$", 
                         lambda m: f"{m.group(1)}說道：汝有興趣買些{translate_term(m.group(2))}嗎？"))
    _regex_rules.append((r"^How many (.+?) wouldst thou sell\?\s*\(own (\d+)\)$", 
                         lambda m: f"汝欲售出幾件{translate_term(m.group(1))}？(擁有 {m.group(2)})"))
    _regex_rules.append((r"^I will give you (\d+)gp for (them|it)\.\s*Deal\?$", 
                         lambda m: f"這物/這些我願出 {m.group(1)} gp 收購。成交否？"))
    _regex_rules.append((r"^(.+?) says:\s*A fine choice!$", lambda m: f"{m.group(1)}說道：精明之選！"))
    _regex_rules.append((r"^(.+?) says:\s*Fare thee well!$", lambda m: f"{m.group(1)}說道：願汝安好！"))
    
    # Generic stubs/not implemented
    _regex_rules.append((r"^\((.+?): coming in v1\)$", lambda m: f"({m.group(1)}：將於v1版本推出)"))
    _regex_rules.append((r"^\((.+?): not yet implemented\)$", lambda m: f"({m.group(1)}：尚未實作)"))
    
    # Status line: [MODE] (x,y) on tile moves=N gold=G
    _regex_rules.append((r"^\[(.+?)\]\s*\((\d+),(\d+)\)\s*on\s*(.+?)\s+moves=(\d+)\s+gold=(\d+)$",
                         lambda m: f"[{translate_mode(m.group(1))}] ({m.group(2)},{m.group(3)}) 位於 {translate_tile(m.group(4))}  步數={m.group(5)}  金幣={m.group(6)}"))

def translate_mode(mode):
    mapping = {"OUTDOORS": "戶外", "BUILDING": "城鎮", "DUNGEON": "地城", "COMBAT": "戰鬥"}
    return mapping.get(mode.upper(), mode)

def translate_tile(tile):
    mapping = {
        "grass": "草地", "deep_water": "深水", "water": "淺水", "forest": "森林",
        "hills": "丘陵", "mountains": "山脈", "swamp": "沼澤", "shrubbery": "灌木",
        "brick_floor": "磚地", "wood_floor": "木地板", "bridge": "橋樑", "stone_wall": "石牆",
        "dungeon_wall": "地城牆", "door": "門扉", "ladder_up": "向上梯", "ladder_down": "向下梯",
        "chest": "寶箱", "altar": "祭壇"
    }
    clean_t = tile.lower().replace(" ", "_")
    return mapping.get(clean_t, tile)

def translate_term(term):
    """Helper to translate single terms inside format strings."""
    t_clean = clean_key(term)
    # Check virtues
    for en, zh in VIRTUE_ZH.items():
        if t_clean == clean_key(en):
            return zh
    # Check classes
    for en, zh in CLASS_ZH.items():
        if t_clean == clean_key(en):
            return zh
    # Check items
    for en, zh in ITEM_ZH.items():
        if t_clean == clean_key(en):
            return zh
    return term

def translate(text: str) -> str:
    if not text:
        return text
    
    # Clean text to lookup in the exact match cache
    key = clean_key(text)
    if key in _exact_cache:
        return _exact_cache[key]
        
    # Check regex rules
    for pattern, handler in _regex_rules:
        # We match case-insensitively or strictly depending on need
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            return handler(match)
            
    # Fallback to checking word-by-word or returning as-is
    return text

# Initialize cache automatically on import
init_translation()
