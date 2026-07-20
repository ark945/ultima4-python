import json
import sys
from pathlib import Path

# Paths relative to the script location
U4PY_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = U4PY_DIR / "data"
U4_CHT_DUMPS = Path("d:/MyLab/u4-cht/dumps")

VIRTUE_MAP = {
    "Honesty": "誠實",
    "Compassion": "慈悲",
    "Valor": "勇敢",
    "Justice": "正義",
    "Sacrifice": "犧牲",
    "Honor": "榮譽",
    "Spirituality": "靈性",
    "Humility": "謙卑"
}

def clean(s):
    if not isinstance(s, str):
        return ""
    # Strip spaces, newlines, and convert to lowercase for robust string matching
    return "".join(s.split()).lower().replace("\n", "").replace("\r", "")

def import_dialogues():
    print("Importing NPC dialogues...")
    talk_path = U4_CHT_DUMPS / "talk_bilingual.json"
    if not talk_path.exists():
        print(f"Error: {talk_path} not found!")
        return

    with open(talk_path, "r", encoding="utf-8") as f:
        talk = json.load(f)

    # Group NPCs by tlk_file
    npcs_by_file = {}
    for npc in talk["npcs"]:
        tf = npc["tlk_file"].title()
        if tf not in npcs_by_file:
            npcs_by_file[tf] = {}
        npcs_by_file[tf][npc["conv_index"]] = npc

    # Map Python dialogue fields to u4-cht fields
    field_mapping = {
        "name": "name",
        "pronoun": "pronoun",
        "look": "description",
        "job": "job",
        "health": "health",
        "answer1": "keyword_response_1",
        "answer2": "keyword_response_2",
        "question": "question",
        "yes": "question_yes_answer",
        "no": "question_no_answer"
    }

    dialogue_dir = DATA_DIR / "dialogue"
    for tf, npcs_map in npcs_by_file.items():
        json_path = dialogue_dir / f"{tf}.json"
        if not json_path.exists():
            # Try lowercase stem mapping (e.g. Lcb.json vs Lcb.json)
            json_path = dialogue_dir / f"{tf.title()}.json"
            if not json_path.exists():
                print(f"  Dialogue file {tf}.json not found, skipping.")
                continue

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        translated_count = 0
        for i, item in enumerate(data):
            if i in npcs_map:
                npc_trans = npcs_map[i]
                fields = npc_trans.get("fields", {})
                for py_key, cht_key in field_mapping.items():
                    if cht_key in fields:
                        val = fields[cht_key]
                        zh_val = val.get("zh", "").strip()
                        if zh_val:
                            item[py_key] = zh_val
                            translated_count += 1

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Translated {tf}.json ({translated_count} fields)")

def import_intro():
    print("Importing introduction texts...")
    st_path = U4_CHT_DUMPS / "stringtable_bilingual.json"
    ui_path = U4_CHT_DUMPS / "ui_bilingual.json"
    
    if not st_path.exists():
        print(f"Error: {st_path} not found!")
        return

    with open(st_path, "r", encoding="utf-8") as f:
        st = json.load(f)

    # 1. Questions translation
    questions_path = DATA_DIR / "intro" / "questions.json"
    if questions_path.exists():
        with open(questions_path, "r", encoding="utf-8") as f:
            q_data = json.load(f)

        intro_q_trans = st["sections"]["intro_questions"]["entries"]
        q_trans_by_idx = {entry["idx"]: entry for entry in intro_q_trans}

        translated_q = 0
        for i, q in enumerate(q_data):
            if i in q_trans_by_idx:
                zh_text = q_trans_by_idx[i].get("zh", "").strip()
                if zh_text:
                    q["text"] = zh_text
                    translated_q += 1

        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump(q_data, f, ensure_ascii=False, indent=2)
        print(f"  Translated questions.json ({translated_q} questions)")

    # 2. Narrative translation
    narrative_path = DATA_DIR / "intro" / "narrative.json"
    if narrative_path.exists():
        with open(narrative_path, "r", encoding="utf-8") as f:
            n_data = json.load(f)

        intro_text_trans = st["sections"]["intro_text"]["entries"]
        # Match by normalized English text for robustness
        trans_by_clean_en = {clean(entry["en"]): entry["zh"] for entry in intro_text_trans if entry.get("en")}

        translated_n = 0
        for item in n_data.get("intro_sequence", []):
            if "text" in item:
                clean_en = clean(item["text"])
                if clean_en in trans_by_clean_en:
                    item["text"] = trans_by_clean_en[clean_en]
                    translated_n += 1

        # Also translate bracket casting texts
        casting = n_data.get("casting", {})
        casting_mapping = {
            "place_first_two": "The gypsy places the first two cards\\n",
            "place_two_more": "She places two more cards\\n",
            "place_last_two": "She places the last two cards\\n",
            "are_the_cards_of": "upon the table.  They are the cards of\\n",
            "and": " and\\n",
            "consider": "\\n\\nConsider this:\\n"
        }
        # In u4-cht, these might be defined in hardcoded strings or system strings
        # We can hardcode standard Traditional Chinese values for these casting fragments:
        casting_zh = {
            "place_first_two": "吉普賽人放下前兩張牌\\n",
            "place_two_more": "她又放下兩張牌\\n",
            "place_last_two": "她放下最後兩張牌\\n",
            "are_the_cards_of": "於案几上。此乃\\n",
            "and": " 與\\n",
            "consider": "\\n\\n且思量此事：\\n"
        }
        for k, v in casting_zh.items():
            if k in casting:
                casting[k] = v

        with open(narrative_path, "w", encoding="utf-8") as f:
            json.dump(n_data, f, ensure_ascii=False, indent=2)
        print(f"  Translated narrative.json ({translated_n} sequences)")

    # 3. Menus translation
    menus_path = DATA_DIR / "intro" / "menus.json"
    if menus_path.exists() and ui_path.exists():
        with open(menus_path, "r", encoding="utf-8") as f:
            m_data = json.load(f)

        with open(ui_path, "r", encoding="utf-8") as f:
            ui = json.load(f)

        ui_trans = {clean(entry["en"]): entry["zh"] for entry in ui["strings"]}

        translated_m_lines = 0
        translated_m_opts = 0
        title_screen = m_data.get("title_screen", {})
        
        for line in title_screen.get("lines", []):
            clean_en = clean(line["text"])
            if clean_en in ui_trans:
                line["text"] = ui_trans[clean_en]
                translated_m_lines += 1

        for opt in title_screen.get("options", []):
            clean_en = clean(opt["label"])
            if clean_en in ui_trans:
                opt["label"] = ui_trans[clean_en]
                translated_m_opts += 1

        with open(menus_path, "w", encoding="utf-8") as f:
            json.dump(m_data, f, ensure_ascii=False, indent=2)
        print(f"  Translated menus.json ({translated_m_lines} lines, {translated_m_opts} options)")

    # 4. Cards translation
    cards_path = DATA_DIR / "intro" / "cards.json"
    if cards_path.exists():
        with open(cards_path, "r", encoding="utf-8") as f:
            c_data = json.load(f)

        translated_cards = 0
        for card in c_data:
            eng_v = card.get("virtue")
            if eng_v in VIRTUE_MAP:
                card["virtue"] = VIRTUE_MAP[eng_v]
                translated_cards += 1

        with open(cards_path, "w", encoding="utf-8") as f:
            json.dump(c_data, f, ensure_ascii=False, indent=2)
        print(f"  Translated cards.json ({translated_cards} virtue cards)")

if __name__ == "__main__":
    import_dialogues()
    import_intro()
    print("Done importing Traditional Chinese assets.")
