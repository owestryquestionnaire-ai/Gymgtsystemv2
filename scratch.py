import streamlit as st
from datetime import datetime, time, timedelta
import json
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- THE VAULT GUARD ---
if os.path.exists("gym_system.vault"):
    st.set_page_config(page_title="System Portal", layout="centered")
    st.error(
        "🔒 System is currently locked in the Vault. Please run the Vault script in your terminal to unlock the database.")
    st.stop()

# --- ZERO-KNOWLEDGE ENCRYPTION CONFIGURATION ---
DB_FILE = "gym_system.db"


def get_key_and_cipher(password: str):
    salt = b'clinic_gym_static_salt_2026'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, Fernet(key)


def verify_master_password(password):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS auth_lock (verify_text TEXT)")
    row = cursor.execute("SELECT verify_text FROM auth_lock").fetchone()

    key, cipher = get_key_and_cipher(password)

    if not row:
        enc_text = cipher.encrypt(b"SystemSecured").decode('utf-8')
        cursor.execute("INSERT INTO auth_lock (verify_text) VALUES (?)", (enc_text,))
        conn.commit()
        conn.close()
        return True, key
    else:
        try:
            text = cipher.decrypt(row[0].encode('utf-8')).decode('utf-8')
            conn.close()
            if text == "SystemSecured":
                return True, key
            return False, None
        except Exception:
            conn.close()
            return False, None


def encrypt_data(data_str):
    if not data_str or 'aes_key' not in st.session_state: return data_str
    cipher = Fernet(st.session_state.aes_key)
    return cipher.encrypt(data_str.encode('utf-8')).decode('utf-8')


def decrypt_data(data_str):
    if not data_str or 'aes_key' not in st.session_state: return data_str
    try:
        cipher = Fernet(st.session_state.aes_key)
        return cipher.decrypt(data_str.encode('utf-8')).decode('utf-8')
    except:
        return data_str


# --- Page Config (Stealth Browser Tab Name) ---
st.set_page_config(page_title="System Portal", layout="wide")

# --- Custom CSS (Clean Classic Layout with Fixed Spacing) ---
st.markdown(
    """
    <style>
    html, body, .stApp { max-width: 100vw !important; overflow-x: hidden !important; margin: 0 !important; padding: 0 !important; }

    .block-container { 
        padding-top: 3.5rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 2rem !important; 
        padding-right: 2rem !important; 
        max-width: 100vw !important; 
        overflow-x: hidden !important; 
        box-sizing: border-box !important; 
    }

    html, body, [class*="css"]  { font-size: 16px !important; }
    [data-testid="stVerticalBlock"] { gap: 0.8rem !important; }
    .stMarkdown { margin-bottom: -5px !important; }

    .cat-header { 
        font-size: 17px; 
        font-weight: 800; 
        text-decoration: underline; 
        background-color: #e1f5fe; 
        color: #01579b; 
        padding: 8px 10px; 
        border-radius: 4px; 
        margin-bottom: 12px; 
        margin-top: 15px; 
    }

    .queue-card { background-color: white; border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ffa000; }
    .queue-active { border-left: 5px solid #43a047; background-color: #f1f8e9; }
    .wait-time { font-size: 24px; font-weight: bold; color: #d32f2f; }

    div[data-testid="stExpander"] details summary p { font-size: 22px !important; font-weight: 800 !important; color: #1976d2 !important; }
    div[data-testid="stCheckbox"] label p { font-size: 19px !important; font-weight: 400 !important; line-height: 1.4 !important; white-space: normal !important; word-break: break-word !important; }

    div[data-testid="stCheckbox"] { margin-top: -6px !important; margin-bottom: -6px !important; padding-bottom: 0px !important; padding-top: 0px !important; }

    div[data-testid="stForm"] div[data-testid="stCheckbox"] label p { font-size: 15px !important; line-height: 1.2 !important; }
    div[data-testid="stForm"] div[data-testid="stRadio"] label p { font-size: 15px !important; }
    div[data-testid="stForm"] label p { font-size: 15px !important; }
    div[data-testid="stForm"] .stMarkdown p { font-size: 15px !important; }

    @media (max-width: 768px) {
        div[data-testid="stExpanderDetails"] { overflow-x: auto !important; -webkit-overflow-scrolling: touch !important; padding-bottom: 10px !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; min-width: 105% !important; gap: 10px !important; padding-right: 10px !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) { flex: 1 1 auto !important; min-width: 0 !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) { flex: 0 0 60px !important; min-width: 60px !important; max-width: 60px !important; display: flex !important; justify-content: flex-end !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button { width: 60px !important; height: 60px !important; min-height: 60px !important; max-height: 60px !important; padding: 2px !important; border-radius: 8px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button p { font-size: 11px !important; margin: 0 !important; white-space: normal !important; text-align: center !important; line-height: 1.1 !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"]:last-of-type { min-width: 100% !important; width: 100% !important; padding-right: 0px !important; margin-top: 10px !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"]:last-of-type > div[data-testid="column"] { flex: 0 0 50% !important; min-width: 50% !important; max-width: 50% !important; justify-content: center !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"]:last-of-type > div[data-testid="column"] button { width: 100% !important; height: auto !important; min-height: 0 !important; max-height: none !important; font-size: 14px !important; }
        div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"]:last-of-type > div[data-testid="column"] button p { font-size: 14px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_db():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, case_no TEXT, p_name TEXT, timestamp TEXT,
        op_details TEXT, op_date TEXT, p_class TEXT, p_precautions TEXT, 
        prescription_json TEXT, is_checked_in INTEGER DEFAULT 0,
        next_appt_date TEXT, next_appt_time TEXT)''')

    try:
        cursor.execute("ALTER TABLE history ADD COLUMN assessment_text TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE history ADD COLUMN therapist TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE history ADD COLUMN daily_seq_no INTEGER")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS queues (
        id INTEGER PRIMARY KEY AUTOINCREMENT, case_no TEXT, p_name TEXT, 
        item_id TEXT, item_name TEXT, prescribed_mins INTEGER, 
        status TEXT DEFAULT 'waiting', joined_at TEXT)''')

    try:
        cursor.execute("ALTER TABLE queues ADD COLUMN daily_seq_no INTEGER")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS waitroom (
        case_no TEXT PRIMARY KEY, added_at TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_tickets (date TEXT PRIMARY KEY, last_seq INTEGER)''')

    conn.commit()
    conn.close()


def get_and_reserve_ticket():
    today_str = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_FILE, timeout=10)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO daily_tickets (date, last_seq) VALUES (?, 0)", (today_str,))
    cursor.execute("UPDATE daily_tickets SET last_seq = last_seq + 1 WHERE date = ?", (today_str,))
    row = cursor.execute("SELECT last_seq FROM daily_tickets WHERE date = ?", (today_str,)).fetchone()

    conn.commit()
    conn.close()
    return row[0]


def add_to_waitroom(case_no):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute("INSERT OR IGNORE INTO waitroom (case_no, added_at) VALUES (?, ?)",
                 (case_no, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()


def remove_from_waitroom(case_no):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute("DELETE FROM waitroom WHERE case_no = ?", (case_no,))
    conn.commit()
    conn.close()


def add_to_queue(case_no, p_name, item_id, item_name, mins, seq_no):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    cursor = conn.cursor()
    exists = cursor.execute("SELECT id FROM queues WHERE case_no = ? AND item_id = ?", (case_no, item_id)).fetchone()
    if not exists:
        safe_name = encrypt_data(p_name)
        cursor.execute(
            "INSERT INTO queues (case_no, p_name, item_id, item_name, prescribed_mins, joined_at, daily_seq_no) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (case_no, safe_name, item_id, item_name, int(mins if mins else 10), datetime.now().strftime('%H:%M:%S'),
             seq_no))
    conn.commit()
    conn.close()


def update_queue_status(qid, status, case_no=None, item_id=None):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    if status == "finished":
        conn.execute("DELETE FROM queues WHERE id = ?", (qid,))
    else:
        conn.execute("UPDATE queues SET status = ? WHERE id = ?", (status, qid))

        if status == "active" and case_no and item_id:
            row = conn.execute(
                "SELECT id, prescription_json FROM history WHERE case_no = ? AND is_checked_in = 1 ORDER BY id DESC LIMIT 1",
                (case_no,)).fetchone()
            if row:
                hist_id, presc_str = row
                presc = json.loads(decrypt_data(presc_str))
                for ex in presc:
                    if ex['id'] == item_id:
                        ex['done'] = True

                safe_presc = encrypt_data(json.dumps(presc, ensure_ascii=False))
                conn.execute("UPDATE history SET prescription_json = ? WHERE id = ?",
                             (safe_presc, hist_id))
                state_key = f"done_{case_no}_{item_id}"
                st.session_state[state_key] = True

    conn.commit()
    conn.close()


def set_check_status(case_no, status):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute("UPDATE history SET is_checked_in = ? WHERE case_no = ?", (status, case_no))
    if status == 0:
        conn.execute("DELETE FROM queues WHERE case_no = ?", (case_no,))
    conn.commit()
    conn.close()


def save_h(c_no, name, presc, op_text, o_date, p_class, p_pre, is_chk, n_date, n_time, assessment, therapist, seq_no):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    cursor = conn.cursor()

    safe_name = encrypt_data(name)
    safe_op_text = encrypt_data(op_text)
    safe_pre = encrypt_data(p_pre)
    safe_presc = encrypt_data(json.dumps(presc, ensure_ascii=False))
    safe_assess = encrypt_data(assessment)

    cursor.execute('''INSERT INTO history 
        (case_no, p_name, timestamp, op_details, op_date, p_class, p_precautions, prescription_json, is_checked_in, next_appt_date, next_appt_time, assessment_text, therapist, daily_seq_no) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (c_no, safe_name, datetime.now().strftime('%Y-%m-%d %H:%M'), safe_op_text, o_date, p_class, safe_pre,
                    safe_presc, is_chk, n_date, n_time, safe_assess, therapist, seq_no))
    conn.commit()
    conn.close()


def toggle_exercise_db(history_id, case_no, ex_id, sub_id=None):
    state_key = f"done_{case_no}_{ex_id}_{sub_id}" if sub_id else f"done_{case_no}_{ex_id}"
    if state_key in st.session_state:
        is_done = st.session_state[state_key]
        conn = sqlite3.connect(DB_FILE, timeout=10)
        row = conn.execute("SELECT prescription_json FROM history WHERE id = ?", (history_id,)).fetchone()
        if row:
            presc = json.loads(decrypt_data(row[0]))
            for ex in presc:
                if ex['id'] == ex_id:
                    if sub_id:
                        ex[f'done_{sub_id}'] = is_done
                    else:
                        ex['done'] = is_done

            safe_presc = encrypt_data(json.dumps(presc, ensure_ascii=False))
            conn.execute("UPDATE history SET prescription_json = ? WHERE id = ?",
                         (safe_presc, history_id))
            conn.commit()
        conn.close()


def delete_patient(case_no):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute("DELETE FROM history WHERE case_no = ?", (case_no,))
    conn.execute("DELETE FROM waitroom WHERE case_no = ?", (case_no,))
    conn.commit()
    conn.close()


@st.dialog("⚠️ Confirm Deletion")
def confirm_delete_dialog(case_no, p_name):
    st.write(f"Are you sure you want to permanently delete all records for **{p_name}** ({case_no})?")
    st.write("This action cannot be undone.")

    col1, col2 = st.columns(2)
    if col1.button("Cancel", use_container_width=True):
        st.rerun()
    if col2.button("Yes, Delete", type="primary", use_container_width=True):
        delete_patient(case_no)
        st.rerun()


init_db()

# --- Exercise Config ---
EXERCISE_DB = {
    "Electrotherapy": [{"id": "e1", "name": "冰磁"}, {"id": "e2", "name": "Gameready"},
                       {"id": "e3", "name": "EMS"}, {"id": "e4", "name": "Lymphapress"},
                       {"id": "e5", "name": "Hot Pack"}],
    "Mobilization": [{"id": "s3", "name": "拉花生波"}, {"id": "s4", "name": "小單車"},
                     {"id": "s5", "name": "Nustep"}, {"id": "s9", "name": "RT300"}, {"id": "s10", "name": "Cybercycle"},
                     {"id": "s11", "name": "Sling suspension"}, {"id": "s12", "name": "遊乾水"}],
    "Strengthening": [{"id": "st1", "name": "踢沙包"}, {"id": "st2", "name": "企 ＋ 屈腳"},
                      {"id": "st3", "name": "挨花生波"}, {"id": "st4", "name": "企 Hip strengthening"},
                      {"id": "st7", "name": "花生波拱橋"}, {"id": "st8", "name": "Minipress"},
                      {"id": "st9", "name": "坐 Hip Abduction"}],
    "Functional": [{"id": "f4", "name": "踏級"}, {"id": "f6", "name": "跨欄"},
                   {"id": "f13", "name": "海綿踏步"}, {"id": "f8", "name": "PWB踩磅"},
                   {"id": "f10", "name": "Wall bar: 坐>企"}, {"id": "f14", "name": "Arjo"},
                   {"id": "f11", "name": "海綿單腳企"}],
    "Walking Exercise": [{"id": "w1", "name": "學行拐杖"}, {"id": "w2", "name": "學行四爪叉"},
                         {"id": "w3", "name": "學行樓梯"}],
    "Others": [{"id": "o1", "name": "按摩棍"}, {"id": "o4", "name": "網球"}, {"id": "o3", "name": "斜板"}],
    "Assessment": [{"id": "a1", "name": "KOOS"}, {"id": "a2", "name": "考試"}]
}

QUEUEABLE_IDS = {"e1": "冰磁", "e2": "Gameready", "s5": "Nustep"}


def get_ex_info(target_eid):
    for cat, items in EXERCISE_DB.items():
        for ex in items:
            if ex["id"] == target_eid:
                return ex["name"], cat
    return "Unknown", "Unknown"


# --- CLINICAL FORMATTER FOR HISTORY (Dynamic Knee/Hip Support & N/A Pain) ---
def format_assessment_display(raw_str, op_details=""):
    if not raw_str or not raw_str.strip():
        return ""
    try:
        data = json.loads(raw_str)
        if isinstance(data, dict) and "free_text" in data:
            lines = []

            is_hip = "THR" in op_details
            is_knee = any(x in op_details for x in ["TKR", "UKA", "HTO"])
            joint_str = "Hip" if (is_hip and not is_knee) else "Knee" if (is_knee and not is_hip) else "Joint"

            # 1. Pain & Walking (Smart N/A Filter)
            pain_parts = []
            if "pain_l" in data or "pain_r" in data:
                pl = str(data.get('pain_l', 'N/A'))
                pr = str(data.get('pain_r', 'N/A'))
                if pl != 'N/A': pain_parts.append(f"L:{pl}/10")
                if pr != 'N/A': pain_parts.append(f"R:{pr}/10")
            elif "pain" in data:
                p = str(data.get('pain', 'N/A'))
                if p != 'N/A': pain_parts.append(f"{p}/10")

            line1_parts = []
            if pain_parts:
                line1_parts.append(f"{joint_str} pain NPRS {', '.join(pain_parts)} on walking.")
            if data.get('tol'):
                line1_parts.append(f"Walking tolerance: {data.get('tol')} mins.")
            if data.get('aid') and data['aid'] != 'None':
                line1_parts.append(f"Aid: {data.get('aid')}.")

            if line1_parts:
                lines.append(" ".join(line1_parts))

            # 2. Analgesics
            if data.get('med_panadol'): lines.append(
                f"on Panadol ({data.get('med_panadol_dose')}) ({data.get('med_panadol_freq')})")
            if data.get('med_tramadol'): lines.append(f"on Tramadol ({data.get('med_tramadol_freq')})")
            if data.get('med_arcoxia'): lines.append(f"on Arcoxia ({data.get('med_arcoxia_freq')})")
            if data.get('med_celebrex'): lines.append(f"on Celebrex ({data.get('med_celebrex_freq')})")
            if data.get('med_lyrica'): lines.append(f"on Lyrica ({data.get('med_lyrica_freq')})")
            if data.get('med_df118'): lines.append(f"on DF118 ({data.get('med_df118_freq')})")

            # 3. Transportation
            if data.get('trans') and len(data['trans']) > 0:
                lines.append(f"Come by {', '.join(data['trans']).lower()}.")

            # 4. Objective Examination (Dynamic Knee/Hip reading)
            if data.get('rom_l') or data.get('rom_r'):
                lines.append(f"Knee AROM - L: {data.get('rom_l', '-')} | R: {data.get('rom_r', '-')}")
            elif data.get('rom'):
                lines.append(f"Knee AROM: {data.get('rom')}")

            if data.get('quad_l') or data.get('quad_r'):
                lines.append(f"Quadriceps strength - L: {data.get('quad_l', '-')} | R: {data.get('quad_r', '-')}")
            elif data.get('quad'):
                lines.append(f"Quadriceps strength {data['quad']}")

            if data.get('ham_l') or data.get('ham_r'):
                lines.append(f"Hamstring strength - L: {data.get('ham_l', '-')} | R: {data.get('ham_r', '-')}")
            elif data.get('ham'):
                lines.append(f"Hamstring strength {data['ham']}")

            if data.get('hip_rom_flex_l') or data.get('hip_rom_flex_r'):
                lines.append(
                    f"Hip AROM Flexion - L: {data.get('hip_rom_flex_l', '-')} | R: {data.get('hip_rom_flex_r', '-')}")

            if data.get('hip_rom_abd_l') or data.get('hip_rom_abd_r'):
                lines.append(
                    f"Hip AROM Abduction - L: {data.get('hip_rom_abd_l', '-')} | R: {data.get('hip_rom_abd_r', '-')}")

            if data.get('hip_str_flex_l') or data.get('hip_str_flex_r'):
                lines.append(
                    f"Hip Flexor strength - L: {data.get('hip_str_flex_l', '-')} | R: {data.get('hip_str_flex_r', '-')}")

            if data.get('hip_str_abd_l') or data.get('hip_str_abd_r'):
                lines.append(
                    f"Hip Abductor strength - L: {data.get('hip_str_abd_l', '-')} | R: {data.get('hip_str_abd_r', '-')}")

            # 5. Free Text Notes
            free_text = data.get('free_text', '').strip()
            if free_text:
                lines.append(f"<br><b>Notes:</b><br>{free_text}")

            return "<br>".join(lines)
        else:
            return f"<b>Notes:</b><br>{raw_str}"
    except:
        return f"<b>Notes:</b><br>{raw_str}"


def format_ex_details(item):
    name = item.get('name', 'Unknown')
    eid = item.get('id', '')

    if eid == "st1":  # 踢沙包
        weight = str(item.get('weight', '')).strip()
        mins = str(item.get('mins', '')).strip()
        parts = []
        if weight: parts.append(f"{weight}lbs")
        if mins: parts.append(f'{mins}"')
        return f"{name}, {', '.join(parts)}" if parts else name

    if eid == "e5":  # Hot Pack
        side = item.get('side', '').lower()
        region = item.get('region', '').lower()
        mins = str(item.get('mins', '')).strip()
        parts = []
        combo = f"{side} {region}".strip()
        if combo: parts.append(combo)
        if mins: parts.append(f'{mins}"')
        return f"{name}, {', '.join(parts)}" if parts else name

    if eid == "f4":  # 踏級 
        height = str(item.get('box_height', '4"')).replace('"', "''")
        direction = "落" if item.get('downstairs') else "上"
        mins = str(item.get('mins', '10'))
        return f"{direction}{height}級 x {mins}\""

    if eid == "f11":  # 海綿單腳企 
        target = str(item.get('target_sec', '')).strip()
        mins = str(item.get('mins', '10')).strip()
        parts = []
        if target: parts.append(f"{target}秒")
        if mins: parts.append(f'{mins}"')
        return f"{name}, {', '.join(parts)}" if parts else name

    if eid == "f8":  # PWB 踩磅 (隱藏 Target 字眼)
        target_wt = str(item.get('target_wt', '')).strip()
        mins = str(item.get('mins', '10')).strip()
        parts = []
        if target_wt: parts.append(f"{target_wt}lbs")
        if mins: parts.append(f'{mins}"')
        return f"{name}, {', '.join(parts)}" if parts else name

    details = []
    if eid == "st4":
        dirs = [("rf", "右前"), ("ra", "右側"), ("re", "右後"),
                ("lf", "左前"), ("la", "左側"), ("le", "左後")]
        st4_details = []
        for d_id, d_label in dirs:
            if item.get(f"{d_id}_chk"):
                m = item.get(f"{d_id}_mins", "10")
                g = "腳踩地" if item.get(f"{d_id}_gnd") else ""
                band = item.get(f"{d_id}_band_color", "紅橡根") if item.get(f"{d_id}_band_chk") else ""

                parts = []
                if band: parts.append(band)
                if g: parts.append(g)
                parts.append(f'{m}"')
                st4_details.append(f"{d_label}, {', '.join(parts)}")
        if st4_details: details.append("; ".join(st4_details))
    else:
        if 'side' in item: details.append(item['side'])
        if 'pressure' in item: details.append(f"{item['pressure']} pressure")
        if 'degree' in item and str(item['degree']).strip(): details.append(f"{item['degree']}°")
        if 'mode' in item: details.append(item['mode'])
        if 'region' in item: details.append(item['region'])
        if 'weight' in item and str(item['weight']).strip():
            if eid in ["st1", "st2", "e3"]:
                details.append(f"Sandbag: {item['weight']} lbs")
            else:
                details.append(f"{item['weight']} lbs")
        if 'ball' in item and item['ball'] != 'None': details.append(item['ball'])
        if 'circle' in item: details.append(item['circle'])
        if 'res' in item and item['res']: details.append(f"Level {item['res']}")
        if 'seat' in item and item['seat']: details.append(f"Seat {item['seat']}")
        if item.get('hands'): details.append("用手")
        if item.get('lseat'): details.append("Long seat")
        if 'rt_res' in item and item['rt_res']: details.append(f"{item['rt_res']} Nm")

        if item.get('band') and item.get('band') != 'None': details.append(item['band'])

        if item.get('sling_abd'):
            tb = f", {item.get('sabd_color', '紅橡根')}" if item.get('sabd_tb') else ""
            details.append(f"平訓＋左右{tb}")
        if item.get('sling_flex'):
            tb = f", {item.get('sflx_color', '紅橡根')}" if item.get('sflx_tb') else ""
            details.append(f"側訓+前後{tb}")

        if item.get('towel'): details.append("毛巾於膝下")
        if eid == "st8":
            cords = []
            b = item.get('black_cord', '')
            r = item.get('red_cord', '')
            if b: cords.append(f"{b} black")
            if r: cords.append(f"{r} red")
            if cords: details.append(f"{' + '.join(cords)} cord")
        if 'hurdle_height' in item: details.append(item['hurdle_height'])
        if item.get('pbar'): details.append("平衡架內")
        if item.get('family'): details.append("家人陪")
        if 'target_wt' in item and item['target_wt'] and eid != 'f8': details.append(f"Target: {item['target_wt']}")
        if 'target_sec' in item and item['target_sec'] and eid != 'f11': details.append(
            f"Target: {item['target_sec']} secs")
        if 'roller_region' in item: details.append(item['roller_region'])
        if 'slant_level' in item: details.append(item['slant_level'])

        if 'mins' in item and not eid.startswith('w'):
            details.append(f'{item["mins"]}"')

    if details:
        return f"{name}, {', '.join(filter(None, details))}"
    return name


def get_therapist_color(name):
    if not name or name == "Unassigned": return "#757575"
    if name.upper() == "MC": return "#1976D2"
    if name.upper() == "TY": return "#388E3C"
    colors = ["#D32F2F", "#7B1FA2", "#C2185B", "#0097A7", "#F57C00", "#E64A19"]
    return colors[sum(ord(c) for c in name) % len(colors)]


if "logged_in" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #424242;'>Secure Portal</h4>", unsafe_allow_html=True)
            st.info("Authentication required to decrypt local database.")

            sys_password = st.text_input("Master Password", type="password")
            therapist_input = st.text_input("User Initials")

            if st.button("Authenticate", type="primary", use_container_width=True):
                if sys_password.strip() == "":
                    st.error("❌ Password cannot be empty.")
                elif therapist_input.strip() == "":
                    st.error("❌ Initials cannot be empty.")
                else:
                    is_valid, derived_key = verify_master_password(sys_password)
                    if not is_valid:
                        st.error("❌ Incorrect Master Password. Database remains locked.")
                    else:
                        st.session_state.aes_key = derived_key
                        user = therapist_input.strip().upper()
                        st.session_state.current_therapist = user
                        st.session_state.logged_in = True
                        st.query_params["user"] = user

                        if st.session_state.current_therapist == "PCA":
                            st.session_state.nav_radio_key = "🗒️ Active Cases"
                        else:
                            st.session_state.nav_radio_key = "👥 Database"

                        st.rerun()
    st.stop()

if "active_patient" not in st.session_state:
    st.session_state.active_patient = {
        "case_no": "", "p_name": "", "p_class": "None",
        "p_att": False, "p_fing": False, "exercises": {},

        "assessment": "", "a_pain_l": "N/A", "a_pain_r": "N/A", "a_tol": "", "a_aid": "None", "a_trans": [],
        "a_med_panadol": False, "a_med_panadol_dose": "500 mg", "a_med_panadol_freq": "QD",
        "a_med_tramadol": False, "a_med_tramadol_freq": "QD",
        "a_med_arcoxia": False, "a_med_arcoxia_freq": "QD",
        "a_med_celebrex": False, "a_med_celebrex_freq": "QD",
        "a_med_lyrica": False, "a_med_lyrica_freq": "QD",
        "a_med_df118": False, "a_med_df118_freq": "QD",
        "a_rom_l": "", "a_rom_r": "", "a_quad_l": "", "a_quad_r": "", "a_ham_l": "", "a_ham_r": "",
        "a_hip_rom_flex_l": "", "a_hip_rom_flex_r": "", "a_hip_rom_abd_l": "", "a_hip_rom_abd_r": "",
        "a_hip_str_flex_l": "", "a_hip_str_flex_r": "", "a_hip_str_abd_l": "", "a_hip_str_abd_r": "",

        "current_chk": 1, "current_nd": "None", "current_nt": "None", "is_loaded": False,
        "op_left_chk": False, "op_left_val": "TKR",
        "op_right_chk": False, "op_right_val": "TKR",
        "op_bi_chk": False, "op_bi_val": "TKR",
        "op_notes": "", "op_date": datetime.now().date(), "daily_seq_no": None
    }

if "nav_radio_key" not in st.session_state:
    st.session_state.nav_radio_key = "👥 Database"

ap = st.session_state.active_patient

if st.session_state.current_therapist == "PCA":
    pages = ["🗒️ Active Cases", "📊 Dashboard", "🚦 Queue Status"]
else:
    pages = ["👥 Database", "📝 Assessment", "📋 Prescription", "🗒️ Active Cases", "🚦 Queue Status", "📊 Dashboard",
             "🗂️ Patient History"]


def nav_to(page_name):
    st.session_state.nav_radio_key = page_name


page = st.sidebar.radio("Navigation Panel", pages, key="nav_radio_key")

st.sidebar.divider()
st.sidebar.markdown(f"**🩺 Logged in as:** {st.session_state.current_therapist}")

if page in ["🗒️ Active Cases", "📊 Dashboard", "🚦 Queue Status"]:
    st_autorefresh(interval=5000, limit=None, key="live_dashboard_refresh")


def perform_logout():
    st.session_state.clear()
    st.query_params.clear()


st.sidebar.button("Log Out", use_container_width=True, on_click=perform_logout)


def load_and_assess(r):
    ex_dict = {}
    try:
        data = json.loads(r[7])
        if isinstance(data, str): data = json.loads(data)
        for item in data:
            eid = item.get("id")
            if eid:
                parsed_data = {k: v for k, v in item.items() if k not in ["id", "name", "done"]}
                if f"{eid}_weight" in parsed_data: parsed_data["weight"] = parsed_data.pop(f"{eid}_weight")
                ex_dict[eid] = parsed_data
    except Exception:
        pass

    op_details = r[8] if r[8] and r[8] != "None recorded" else ""
    op_notes = ""
    if " | Notes: " in op_details:
        parts = op_details.split(" | Notes: ")
        op_details = parts[0]
        op_notes = parts[1]
    elif op_details.startswith("Notes: "):
        op_notes = op_details.replace("Notes: ", "")
        op_details = ""

    op_left_chk, op_left_val = False, "TKR"
    op_right_chk, op_right_val = False, "TKR"
    op_bi_chk, op_bi_val = False, "TKR"

    for val in ["TKR", "UKA", "HTO", "THR"]:
        if f"Left {val}" in op_details: op_left_chk, op_left_val = True, val
        if f"Right {val}" in op_details: op_right_chk, op_right_val = True, val
        if f"Bilateral {val}" in op_details: op_bi_chk, op_bi_val = True, val

    try:
        parsed_op_date = datetime.strptime(r[11], '%Y-%m-%d').date() if r[11] else datetime.now().date()
    except Exception:
        parsed_op_date = datetime.now().date()

    raw_assess = r[10] if r[10] else ""
    try:
        parsed_a = json.loads(raw_assess)
        if isinstance(parsed_a, dict) and "free_text" in parsed_a:
            ap_assessment = parsed_a["free_text"]
            ap_a_pain_l = str(parsed_a.get("pain_l", parsed_a.get("pain", "N/A")))
            ap_a_pain_r = str(parsed_a.get("pain_r", parsed_a.get("pain", "N/A")))
            ap_a_tol = parsed_a.get("tol", "")
            ap_a_aid = parsed_a.get("aid", "None")
            ap_a_trans = parsed_a.get("trans", [])
            ap_a_med_panadol = parsed_a.get("med_panadol", False)
            ap_a_med_panadol_dose = parsed_a.get("med_panadol_dose", "500 mg")
            ap_a_med_panadol_freq = parsed_a.get("med_panadol_freq", "QD")
            ap_a_med_tramadol = parsed_a.get("med_tramadol", False)
            ap_a_med_tramadol_freq = parsed_a.get("med_tramadol_freq", "QD")
            ap_a_med_arcoxia = parsed_a.get("med_arcoxia", False)
            ap_a_med_arcoxia_freq = parsed_a.get("med_arcoxia_freq", "QD")
            ap_a_med_celebrex = parsed_a.get("med_celebrex", False)
            ap_a_med_celebrex_freq = parsed_a.get("med_celebrex_freq", "QD")
            ap_a_med_lyrica = parsed_a.get("med_lyrica", False)
            ap_a_med_lyrica_freq = parsed_a.get("med_lyrica_freq", "QD")
            ap_a_med_df118 = parsed_a.get("med_df118", False)
            ap_a_med_df118_freq = parsed_a.get("med_df118_freq", "QD")

            ap_a_rom_l = parsed_a.get("rom_l", parsed_a.get("rom", ""))
            ap_a_rom_r = parsed_a.get("rom_r", parsed_a.get("rom", ""))
            ap_a_quad_l = parsed_a.get("quad_l", parsed_a.get("quad", ""))
            ap_a_quad_r = parsed_a.get("quad_r", parsed_a.get("quad", ""))
            ap_a_ham_l = parsed_a.get("ham_l", parsed_a.get("ham", ""))
            ap_a_ham_r = parsed_a.get("ham_r", parsed_a.get("ham", ""))

            ap_a_hip_rom_flex_l = parsed_a.get("hip_rom_flex_l", "")
            ap_a_hip_rom_flex_r = parsed_a.get("hip_rom_flex_r", "")
            ap_a_hip_rom_abd_l = parsed_a.get("hip_rom_abd_l", "")
            ap_a_hip_rom_abd_r = parsed_a.get("hip_rom_abd_r", "")
            ap_a_hip_str_flex_l = parsed_a.get("hip_str_flex_l", "")
            ap_a_hip_str_flex_r = parsed_a.get("hip_str_flex_r", "")
            ap_a_hip_str_abd_l = parsed_a.get("hip_str_abd_l", "")
            ap_a_hip_str_abd_r = parsed_a.get("hip_str_abd_r", "")
        else:
            ap_assessment, ap_a_pain_l, ap_a_pain_r, ap_a_tol, ap_a_aid, ap_a_trans = raw_assess, "N/A", "N/A", "", "None", []
            ap_a_med_panadol, ap_a_med_panadol_dose, ap_a_med_panadol_freq = False, "500 mg", "QD"
            ap_a_med_tramadol, ap_a_med_tramadol_freq = False, "QD"
            ap_a_med_arcoxia, ap_a_med_arcoxia_freq = False, "QD"
            ap_a_med_celebrex, ap_a_med_celebrex_freq = False, "QD"
            ap_a_med_lyrica, ap_a_med_lyrica_freq = False, "QD"
            ap_a_med_df118, ap_a_med_df118_freq = False, "QD"
            ap_a_rom_l, ap_a_rom_r, ap_a_quad_l, ap_a_quad_r, ap_a_ham_l, ap_a_ham_r = "", "", "", "", "", ""
            ap_a_hip_rom_flex_l, ap_a_hip_rom_flex_r, ap_a_hip_rom_abd_l, ap_a_hip_rom_abd_r = "", "", "", ""
            ap_a_hip_str_flex_l, ap_a_hip_str_flex_r, ap_a_hip_str_abd_l, ap_a_hip_str_abd_r = "", "", "", ""
    except:
        ap_assessment, ap_a_pain_l, ap_a_pain_r, ap_a_tol, ap_a_aid, ap_a_trans = raw_assess, "N/A", "N/A", "", "None", []
        ap_a_med_panadol, ap_a_med_panadol_dose, ap_a_med_panadol_freq = False, "500 mg", "QD"
        ap_a_med_tramadol, ap_a_med_tramadol_freq = False, "QD"
        ap_a_med_arcoxia, ap_a_med_arcoxia_freq = False, "QD"
        ap_a_med_celebrex, ap_a_med_celebrex_freq = False, "QD"
        ap_a_med_lyrica, ap_a_med_lyrica_freq = False, "QD"
        ap_a_med_df118, ap_a_med_df118_freq = False, "QD"
        ap_a_rom_l, ap_a_rom_r, ap_a_quad_l, ap_a_quad_r, ap_a_ham_l, ap_a_ham_r = "", "", "", "", "", ""
        ap_a_hip_rom_flex_l, ap_a_hip_rom_flex_r, ap_a_hip_rom_abd_l, ap_a_hip_rom_abd_r = "", "", "", ""
        ap_a_hip_str_flex_l, ap_a_hip_str_flex_r, ap_a_hip_str_abd_l, ap_a_hip_str_abd_r = "", "", "", ""

    st.session_state.active_patient = {
        "case_no": r[1], "p_name": r[2],
        "p_class": r[5] if r[5] and r[5] != "None" else "None",
        "p_att": "多注目" in (r[6] or ""), "p_fing": "夾手指做運動" in (r[6] or ""),
        "exercises": ex_dict,

        "assessment": ap_assessment,
        "a_pain_l": ap_a_pain_l, "a_pain_r": ap_a_pain_r, "a_tol": ap_a_tol, "a_aid": ap_a_aid, "a_trans": ap_a_trans,
        "a_med_panadol": ap_a_med_panadol, "a_med_panadol_dose": ap_a_med_panadol_dose,
        "a_med_panadol_freq": ap_a_med_panadol_freq,
        "a_med_tramadol": ap_a_med_tramadol, "a_med_tramadol_freq": ap_a_med_tramadol_freq,
        "a_med_arcoxia": ap_a_med_arcoxia, "a_med_arcoxia_freq": ap_a_med_arcoxia_freq,
        "a_med_celebrex": ap_a_med_celebrex, "a_med_celebrex_freq": ap_a_med_celebrex_freq,
        "a_med_lyrica": ap_a_med_lyrica, "a_med_lyrica_freq": ap_a_med_lyrica_freq,
        "a_med_df118": ap_a_med_df118, "a_med_df118_freq": ap_a_med_df118_freq,

        "a_rom_l": ap_a_rom_l, "a_rom_r": ap_a_rom_r,
        "a_quad_l": ap_a_quad_l, "a_quad_r": ap_a_quad_r,
        "a_ham_l": ap_a_ham_l, "a_ham_r": ap_a_ham_r,
        "a_hip_rom_flex_l": ap_a_hip_rom_flex_l, "a_hip_rom_flex_r": ap_a_hip_rom_flex_r,
        "a_hip_rom_abd_l": ap_a_hip_rom_abd_l, "a_hip_rom_abd_r": ap_a_hip_rom_abd_r,
        "a_hip_str_flex_l": ap_a_hip_str_flex_l, "a_hip_str_flex_r": ap_a_hip_str_flex_r,
        "a_hip_str_abd_l": ap_a_hip_str_abd_l, "a_hip_str_abd_r": ap_a_hip_str_abd_r,

        "current_chk": r[4], "current_nd": r[3], "current_nt": r[9], "is_loaded": True,
        "op_left_chk": op_left_chk, "op_left_val": op_left_val,
        "op_right_chk": op_right_chk, "op_right_val": op_right_val,
        "op_bi_chk": op_bi_chk, "op_bi_val": op_bi_val,
        "op_notes": op_notes, "op_date": parsed_op_date,
        "daily_seq_no": r[12] if len(r) > 12 else None
    }
    nav_to("📝 Assessment")


def quick_history(c_no):
    st.session_state.active_patient["case_no"] = c_no
    nav_to("🗂️ Patient History")


def render_patient_list(patient_rows, key_prefix, wr_cases):
    if not patient_rows:
        st.info("No records found in this view.")
        return

    h = st.columns([1.2, 1.5, 0.9, 0.9, 0.6, 0.5, 0.8])
    h[0].markdown("**Case No.**")
    h[1].markdown("**Name**")

    for row in patient_rows:
        c = st.columns([1.2, 1.5, 0.9, 0.9, 0.6, 0.5, 0.8])
        c[0].write(row[1])
        c[1].write(row[2])

        is_active = (row[4] == 1)

        c[2].button("Assess", key=f"{key_prefix}_ld_{row[0]}", type="primary", use_container_width=True,
                    disabled=is_active, help="Disabled while active on Gym Floor" if is_active else None,
                    on_click=load_and_assess, args=(row,))

        c[3].button("History", key=f"{key_prefix}_hist_{row[0]}", use_container_width=True, on_click=quick_history,
                    args=(row[1],))

        if c[4].button("View", key=f"{key_prefix}_sh_{row[0]}", use_container_width=True):
            with st.expander("Latest Prescription Details"):
                try:
                    for ex in json.loads(row[7]): st.write(f"• {format_ex_details(ex)}")
                except:
                    st.write("Could not decode exercises.")

        if c[5].button("❌", key=f"{key_prefix}_del_{row[0]}", help="Delete Patient Record"):
            confirm_delete_dialog(row[1], row[2])

        in_wr = row[1] in wr_cases
        if in_wr:
            c[6].button("➖ Wait", key=f"{key_prefix}_wrrm_{row[0]}", help="Remove from Waitroom",
                        use_container_width=True, on_click=remove_from_waitroom, args=(row[1],))
        else:
            c[6].button("➕ Wait", key=f"{key_prefix}_wradd_{row[0]}", help="Add to tomorrow's Waitroom",
                        use_container_width=True, on_click=add_to_waitroom, args=(row[1],))


# --- PAGE 1: DATABASE ---
if page == "👥 Database":
    st.subheader("Step 1: Patient Database & Waitroom")

    with st.expander("➕ Add new patients", expanded=False):
        with st.form("new_patient_form", clear_on_submit=True):
            p_c1, p_c2, p_c3 = st.columns([1.2, 1, 1.8])

            with p_c1:
                new_case = st.text_input("Case Number*")
                new_name = st.text_input("Name*")
                new_class = st.radio("Mobility Class", ["Class I", "Class II", "Class III"], index=None,
                                     horizontal=True)

            with p_c2:
                st.markdown("**Precautions:**")
                new_att = st.checkbox("多注目")
                new_fing = st.checkbox("夾手指做運動")
                new_op_date = st.date_input("Date of Operation")

            with p_c3:
                st.markdown("**Operation Details:**")
                op_choices = ["TKR", "UKA", "HTO", "THR"]
                c_op1, c_op2, c_op3 = st.columns(3)
                with c_op1:
                    chk_l = st.checkbox("Left")
                    val_l = st.selectbox("Op L", op_choices, key="nl", label_visibility="collapsed")
                with c_op2:
                    chk_r = st.checkbox("Right")
                    val_r = st.selectbox("Op R", op_choices, key="nr", label_visibility="collapsed")
                with c_op3:
                    chk_b = st.checkbox("Bilateral")
                    val_b = st.selectbox("Op B", op_choices, key="nb", label_visibility="collapsed")

                new_notes = st.text_area("Other Details / Complications", placeholder="e.g., bleeding...", height=68)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("💾 Save to Database", type="primary", use_container_width=True)

            if submitted:
                if not new_case.strip() or not new_name.strip():
                    st.error("Case Number and Name are required to register a patient!")
                else:
                    pre_list = []
                    if new_att: pre_list.append("多注目")
                    if new_fing: pre_list.append("夾手指做運動")
                    final_pre = ", ".join(pre_list) if pre_list else "None"

                    op_list = []
                    if chk_l: op_list.append(f"Left {val_l}")
                    if chk_r: op_list.append(f"Right {val_r}")
                    if chk_b: op_list.append(f"Bilateral {val_b}")

                    op_string = ", ".join(op_list)
                    if new_notes.strip():
                        if op_string:
                            op_string += f" | Notes: {new_notes}"
                        else:
                            op_string = f"Notes: {new_notes}"
                    if not op_string.strip(): op_string = "None recorded"

                    final_class = new_class if new_class else "None"

                    save_h(new_case.strip(), new_name.strip(), [], op_string, new_op_date.strftime("%Y-%m-%d"),
                           final_class, final_pre, 0, "None", "None", "", st.session_state.current_therapist, None)
                    st.success(f"Successfully registered {new_name} to the database!")
                    st.rerun()

    conn = sqlite3.connect(DB_FILE, timeout=10)
    query = "SELECT id, case_no, p_name, next_appt_date, is_checked_in, p_class, p_precautions, prescription_json, op_details, next_appt_time, assessment_text, op_date FROM history WHERE id IN (SELECT MAX(id) FROM history GROUP BY case_no) ORDER BY id DESC"
    raw_db_all = conn.execute(query).fetchall()
    wr_cases = [r[0] for r in conn.execute("SELECT case_no FROM waitroom").fetchall()]
    conn.close()

    db_all = []
    for r in raw_db_all:
        db_all.append((
            r[0], r[1], decrypt_data(r[2]), r[3], r[4], r[5],
            decrypt_data(r[6]), decrypt_data(r[7]), decrypt_data(r[8]),
            r[9], decrypt_data(r[10]), r[11]
        ))

    db_all = sorted(db_all, key=lambda x: x[2])

    db_waitroom = [r for r in db_all if r[1] in wr_cases]

    tab_wait, tab_all = st.tabs(["🛋️ Waitroom (Next Day)", "🗃️ All Patients Database"])

    with tab_wait:
        st.markdown("##### 🛋️ Patients pre-sorted for next session")
        render_patient_list(db_waitroom, "wr", wr_cases)

    with tab_all:
        col_search, _ = st.columns([1, 1])
        search_term = col_search.text_input("🔍 Quick Search by Name or Case No.", key="db_search")
        st.divider()

        if search_term:
            filtered_db = [r for r in db_all if
                           search_term.lower() in r[1].lower() or search_term.lower() in r[2].lower()]
        else:
            filtered_db = db_all

        render_patient_list(filtered_db, "all", wr_cases)

# --- PAGE 2: ASSESSMENT ---
elif page == "📝 Assessment":
    st.subheader("Step 2: Clinical Assessment")

    if not ap["case_no"]:
        st.warning("⚠️ No patient selected. Please select a patient from the Database first.")
    else:
        seq_display = ap.get('daily_seq_no', 'Unassigned')
        st.markdown(f"### No. {seq_display} | Assessing: {ap['p_name']} ({ap['case_no']})")

        # --- DYNAMIC SMART DETECTION (KNEE VS HIP) ---
        current_ops = []
        if ap.get("op_left_chk"): current_ops.append(ap.get("op_left_val", ""))
        if ap.get("op_right_chk"): current_ops.append(ap.get("op_right_val", ""))
        if ap.get("op_bi_chk"): current_ops.append(ap.get("op_bi_val", ""))
        op_string_check = " ".join(current_ops)

        is_knee = any(x in op_string_check for x in ["TKR", "UKA", "HTO"])
        is_hip = "THR" in op_string_check
        if not is_knee and not is_hip:
            is_knee = True  # Default fallback if nothing matches

        # --- GUIDED ASSESSMENT QUESTIONS ---
        st.markdown("<h4 style='color: #01579b; margin-top: 10px; margin-bottom: 20px;'>Guided Assessment</h4>",
                    unsafe_allow_html=True)

        pain_opts = ["N/A"] + [str(i) for i in range(11)]

        st.markdown(
            "<div style='font-size: 18px; font-weight: 600; margin-bottom: 5px; margin-top: 15px;'>1. Pain score on walking (0-10)</div>",
            unsafe_allow_html=True)
        p_c1, p_c2 = st.columns(2)
        with p_c1:
            st.caption("Left Leg")
            curr_pl = str(ap.get("a_pain_l", "N/A"))
            if curr_pl not in pain_opts: curr_pl = "N/A"
            ap["a_pain_l"] = st.select_slider("Left Pain", options=pain_opts, value=curr_pl,
                                              label_visibility="collapsed")
        with p_c2:
            st.caption("Right Leg")
            curr_pr = str(ap.get("a_pain_r", "N/A"))
            if curr_pr not in pain_opts: curr_pr = "N/A"
            ap["a_pain_r"] = st.select_slider("Right Pain", options=pain_opts, value=curr_pr,
                                              label_visibility="collapsed")

        st.markdown(
            "<div style='font-size: 18px; font-weight: 600; margin-bottom: 5px; margin-top: 15px;'>2. Walking tolerance (minutes)</div>",
            unsafe_allow_html=True)
        ap["a_tol"] = st.text_input("Tolerance", ap.get("a_tol", ""), label_visibility="collapsed")

        st.markdown(
            "<div style='font-size: 18px; font-weight: 600; margin-bottom: 5px; margin-top: 15px;'>3. Walking aids used</div>",
            unsafe_allow_html=True)
        aid_opts = ["None", "拐杖", "Frame", "四爪叉", "Rollator"]
        ap["a_aid"] = st.selectbox("Aid", aid_opts, index=aid_opts.index(ap.get("a_aid", "None")),
                                   label_visibility="collapsed")

        st.markdown(
            "<div style='font-size: 18px; font-weight: 600; margin-bottom: 5px; margin-top: 15px;'>4. Transportation</div>",
            unsafe_allow_html=True)
        trans_opts = ["Taxi", "ETS", "Train", "Bus", "Minibus", "Private car"]
        ap["a_trans"] = st.multiselect("Transport", trans_opts, default=ap.get("a_trans", []),
                                       label_visibility="collapsed")

        st.markdown(
            "<div style='font-size: 18px; font-weight: 600; margin-bottom: 10px; margin-top: 15px;'>5. Analgesics</div>",
            unsafe_allow_html=True)
        with st.container(border=True):
            # Panadol
            c1, c2, c3 = st.columns([1.5, 1, 1.5])
            with c1:
                ap["a_med_panadol"] = st.checkbox("Panadol", value=ap.get("a_med_panadol", False))
            if ap["a_med_panadol"]:
                with c2: ap["a_med_panadol_dose"] = st.selectbox("Dose", ["500 mg", "1000 mg"],
                                                                 index=0 if ap.get("a_med_panadol_dose",
                                                                                   "500 mg") == "500 mg" else 1,
                                                                 label_visibility="collapsed", key="pan_dose")
                with c3: ap["a_med_panadol_freq"] = st.selectbox("Freq", ["QD", "BD", "TDS", "QID"],
                                                                 index=["QD", "BD", "TDS", "QID"].index(
                                                                     ap.get("a_med_panadol_freq", "QD")),
                                                                 label_visibility="collapsed", key="pan_freq")

            st.markdown("<hr style='margin: 0px;'>", unsafe_allow_html=True)

            # Tramadol
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                ap["a_med_tramadol"] = st.checkbox("Tramadol", value=ap.get("a_med_tramadol", False))
            if ap["a_med_tramadol"]:
                with c2: ap["a_med_tramadol_freq"] = st.radio("Freq", ["QD", "BD", "TDS", "QID"],
                                                              index=["QD", "BD", "TDS", "QID"].index(
                                                                  ap.get("a_med_tramadol_freq", "QD")), horizontal=True,
                                                              label_visibility="collapsed", key="tram_freq")

            st.markdown("<hr style='margin: 0px;'>", unsafe_allow_html=True)

            # Arcoxia
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                ap["a_med_arcoxia"] = st.checkbox("Arcoxia", value=ap.get("a_med_arcoxia", False))
            if ap["a_med_arcoxia"]:
                with c2: ap["a_med_arcoxia_freq"] = st.radio("Freq", ["QD", "BD", "TDS", "QID"],
                                                             index=["QD", "BD", "TDS", "QID"].index(
                                                                 ap.get("a_med_arcoxia_freq", "QD")), horizontal=True,
                                                             label_visibility="collapsed", key="arc_freq")

            st.markdown("<hr style='margin: 0px;'>", unsafe_allow_html=True)

            # Celebrex
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                ap["a_med_celebrex"] = st.checkbox("Celebrex", value=ap.get("a_med_celebrex", False))
            if ap["a_med_celebrex"]:
                with c2: ap["a_med_celebrex_freq"] = st.radio("Freq", ["QD", "BD", "TDS", "QID"],
                                                              index=["QD", "BD", "TDS", "QID"].index(
                                                                  ap.get("a_med_celebrex_freq", "QD")), horizontal=True,
                                                              label_visibility="collapsed", key="cel_freq")

            st.markdown("<hr style='margin: 0px;'>", unsafe_allow_html=True)

            # Lyrica
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                ap["a_med_lyrica"] = st.checkbox("Lyrica", value=ap.get("a_med_lyrica", False))
            if ap["a_med_lyrica"]:
                with c2: ap["a_med_lyrica_freq"] = st.radio("Freq", ["QD", "BD", "TDS", "QID"],
                                                            index=["QD", "BD", "TDS", "QID"].index(
                                                                ap.get("a_med_lyrica_freq", "QD")), horizontal=True,
                                                            label_visibility="collapsed", key="lyr_freq")

            st.markdown("<hr style='margin: 0px;'>", unsafe_allow_html=True)

            # DF118
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                ap["a_med_df118"] = st.checkbox("DF118", value=ap.get("a_med_df118", False))
            if ap["a_med_df118"]:
                with c2: ap["a_med_df118_freq"] = st.radio("Freq", ["QD", "BD", "TDS", "QID"],
                                                           index=["QD", "BD", "TDS", "QID"].index(
                                                               ap.get("a_med_df118_freq", "QD")), horizontal=True,
                                                           label_visibility="collapsed", key="df118_freq")

        # --- DYNAMIC OBJECTIVE EXAMINATION ---
        st.markdown("<h4 style='color: #01579b; margin-top: 30px; margin-bottom: 20px;'>Objective Examination</h4>",
                    unsafe_allow_html=True)

        c_obj_l, c_obj_r = st.columns(2)

        with c_obj_l:
            st.markdown("##### 🦵 Left Leg")

            if is_knee:
                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Knee ROM</div>",
                    unsafe_allow_html=True)
                ap["a_rom_l"] = st.text_input("L Knee ROM", ap.get("a_rom_l", ""), placeholder="e.g., 0-90",
                                              label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Quadriceps Strength</div>",
                    unsafe_allow_html=True)
                ap["a_quad_l"] = st.text_input("L Quad Strength", ap.get("a_quad_l", ""), placeholder="e.g., Grade 4",
                                               label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hamstring Strength</div>",
                    unsafe_allow_html=True)
                ap["a_ham_l"] = st.text_input("L Ham Strength", ap.get("a_ham_l", ""), placeholder="e.g., Grade 4",
                                              label_visibility="collapsed")

            if is_hip:
                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip AROM Flexion</div>",
                    unsafe_allow_html=True)
                ap["a_hip_rom_flex_l"] = st.text_input("L Hip Flexion", ap.get("a_hip_rom_flex_l", ""),
                                                       placeholder="e.g., 0-90", label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip AROM Abduction</div>",
                    unsafe_allow_html=True)
                ap["a_hip_rom_abd_l"] = st.text_input("L Hip Abduction", ap.get("a_hip_rom_abd_l", ""),
                                                      placeholder="e.g., 0-30", label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip Flexor Strength</div>",
                    unsafe_allow_html=True)
                ap["a_hip_str_flex_l"] = st.text_input("L Hip Flexor Str", ap.get("a_hip_str_flex_l", ""),
                                                       placeholder="e.g., Grade 4", label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip Abductor Strength</div>",
                    unsafe_allow_html=True)
                ap["a_hip_str_abd_l"] = st.text_input("L Hip Abd Str", ap.get("a_hip_str_abd_l", ""),
                                                      placeholder="e.g., Grade 4", label_visibility="collapsed")

        with c_obj_r:
            st.markdown("##### 🦵 Right Leg")

            if is_knee:
                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Knee ROM</div>",
                    unsafe_allow_html=True)
                ap["a_rom_r"] = st.text_input("R Knee ROM", ap.get("a_rom_r", ""), placeholder="e.g., 0-90",
                                              label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Quadriceps Strength</div>",
                    unsafe_allow_html=True)
                ap["a_quad_r"] = st.text_input("R Quad Strength", ap.get("a_quad_r", ""), placeholder="e.g., Grade 4",
                                               label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hamstring Strength</div>",
                    unsafe_allow_html=True)
                ap["a_ham_r"] = st.text_input("R Ham Strength", ap.get("a_ham_r", ""), placeholder="e.g., Grade 4",
                                              label_visibility="collapsed")

            if is_hip:
                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip AROM Flexion</div>",
                    unsafe_allow_html=True)
                ap["a_hip_rom_flex_r"] = st.text_input("R Hip Flexion", ap.get("a_hip_rom_flex_r", ""),
                                                       placeholder="e.g., 0-90", label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip AROM Abduction</div>",
                    unsafe_allow_html=True)
                ap["a_hip_rom_abd_r"] = st.text_input("R Hip Abduction", ap.get("a_hip_rom_abd_r", ""),
                                                      placeholder="e.g., 0-30", label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip Flexor Strength</div>",
                    unsafe_allow_html=True)
                ap["a_hip_str_flex_r"] = st.text_input("R Hip Flexor Str", ap.get("a_hip_str_flex_r", ""),
                                                       placeholder="e.g., Grade 4", label_visibility="collapsed")

                st.markdown(
                    "<div style='font-size: 16px; font-weight: 600; margin-bottom: 5px; margin-top: 10px;'>Hip Abductor Strength</div>",
                    unsafe_allow_html=True)
                ap["a_hip_str_abd_r"] = st.text_input("R Hip Abd Str", ap.get("a_hip_str_abd_r", ""),
                                                      placeholder="e.g., Grade 4", label_visibility="collapsed")

        # --- FREE TEXT NOTES ---
        st.markdown(
            "<h4 style='color: #01579b; margin-top: 30px; margin-bottom: 15px;'>Additional Free Text Notes</h4>",
            unsafe_allow_html=True)


        def sync_assess():
            ap["assessment"] = st.session_state.assess_input


        def save_notes_and_proceed():
            ap["assessment"] = st.session_state.assess_input
            nav_to("📋 Prescription")


        st.text_area(
            "Notes",
            value=ap["assessment"],
            key="assess_input",
            height=150,
            on_change=sync_assess,
            placeholder="Type any other subjective/objective findings or progression notes here...",
            label_visibility="collapsed"
        )

        st.button("Save Assessment & Proceed to Prescription ➡️", type="primary", on_click=save_notes_and_proceed)

# --- PAGE 3: PRESCRIPTION ---
elif page == "📋 Prescription":

    c1, c2 = st.columns([4, 1])
    c1.subheader("Step 3: Update Exercise Prescription")


    def blank_patient():
        st.session_state.active_patient = {
            "case_no": "", "p_name": "", "p_class": "None",
            "p_att": False, "p_fing": False, "exercises": {},

            "assessment": "", "a_pain_l": "N/A", "a_pain_r": "N/A", "a_tol": "", "a_aid": "None", "a_trans": [],
            "a_med_panadol": False, "a_med_panadol_dose": "500 mg", "a_med_panadol_freq": "QD",
            "a_med_tramadol": False, "a_med_tramadol_freq": "QD",
            "a_med_arcoxia": False, "a_med_arcoxia_freq": "QD",
            "a_med_celebrex": False, "a_med_celebrex_freq": "QD",
            "a_med_lyrica": False, "a_med_lyrica_freq": "QD",
            "a_med_df118": False, "a_med_df118_freq": "QD",
            "a_rom_l": "", "a_rom_r": "", "a_quad_l": "", "a_quad_r": "", "a_ham_l": "", "a_ham_r": "",
            "a_hip_rom_flex_l": "", "a_hip_rom_flex_r": "", "a_hip_rom_abd_l": "", "a_hip_rom_abd_r": "",
            "a_hip_str_flex_l": "", "a_hip_str_flex_r": "", "a_hip_str_abd_l": "", "a_hip_str_abd_r": "",

            "current_chk": 1, "current_nd": "None", "current_nt": "None", "is_loaded": False,
            "op_left_chk": False, "op_left_val": "TKR",
            "op_right_chk": False, "op_right_val": "TKR",
            "op_bi_chk": False, "op_bi_val": "TKR",
            "op_notes": "", "op_date": datetime.now().date(),
            "daily_seq_no": None
        }


    c2.button("✨ Blank New Patient", type="primary", use_container_width=True, on_click=blank_patient)
    if ap["is_loaded"]: st.info(f"✏️ **Updating Prescription for {ap['p_name']}.**")


    def sync_form():
        ap["case_no"] = st.session_state.rx_case
        ap["p_name"] = st.session_state.rx_name
        ap["p_class"] = st.session_state.rx_class if st.session_state.rx_class else "None"
        ap["p_att"] = st.session_state.rx_att
        ap["p_fing"] = st.session_state.rx_fing
        ap["op_left_chk"] = st.session_state.rx_op_l_chk
        if "rx_op_l_val" in st.session_state: ap["op_left_val"] = st.session_state.rx_op_l_val
        ap["op_right_chk"] = st.session_state.rx_op_r_chk
        if "rx_op_r_val" in st.session_state: ap["op_right_val"] = st.session_state.rx_op_r_val
        ap["op_bi_chk"] = st.session_state.rx_op_b_chk
        if "rx_op_b_val" in st.session_state: ap["op_bi_val"] = st.session_state.rx_op_b_val
        ap["op_notes"] = st.session_state.rx_op_notes
        ap["op_date"] = st.session_state.rx_op_d


    def toggle_ex(eid):
        if st.session_state[f"ui_{eid}"]:
            if eid not in ap["exercises"]:
                _, cat = get_ex_info(eid)
                defaults = {}
                if cat == "Electrotherapy":
                    defaults["mins"] = "15"
                    if eid == "e1":
                        defaults["side"] = "Right knee"
                    elif eid == "e2":
                        defaults.update({"side": "Right", "pressure": "Low"})
                    elif eid == "e3":
                        defaults.update({"side": "Right Quad", "mode": "Static Quad"})
                    elif eid == "e4":
                        defaults.update({"side": "Right", "pressure": "40"})
                    elif eid == "e5":
                        defaults.update({"side": "左", "region": "大髀前"})
                elif cat in ["Walking Exercise", "Assessment"]:
                    pass
                else:
                    defaults["mins"] = "10"
                    if eid in ["s3", "st3", "st7"]:
                        defaults["ball"] = "None"
                    elif eid == "s4":
                        defaults["circle"] = "半圈"
                    elif eid == "s10":
                        defaults["mode"] = "easy"
                    elif eid == "st8":
                        defaults["side"] = "Right"
                    elif eid == "st9":
                        defaults["band"] = "None"
                    elif eid == "f4":
                        defaults["box_height"] = "4\""
                    elif eid == "f6":
                        defaults["hurdle_height"] = "4\""
                    elif eid in ["o1", "o4"]:
                        defaults["roller_region"] = "大脾前" if eid == "o1" else "大脾後"
                    elif eid == "o3":
                        defaults["slant_level"] = "1格"
                ap["exercises"][eid] = defaults
        else:
            if eid in ap["exercises"]: del ap["exercises"][eid]


    def update_dict(eid, key, val_key):
        if eid not in ap["exercises"]: ap["exercises"][eid] = {}
        ap["exercises"][eid][key] = st.session_state[val_key]


    def remove_cart_item(item_eid):
        if item_eid in ap["exercises"]:
            del ap["exercises"][item_eid]
        if f"ui_{item_eid}" in st.session_state:
            st.session_state[f"ui_{item_eid}"] = False


    def check_in_patient():
        if ap["case_no"]:
            remove_from_waitroom(ap["case_no"])

        pre_list = []
        if ap["p_att"]: pre_list.append("多注目")
        if ap["p_fing"]: pre_list.append("夾手指做運動")
        final_pre = ", ".join(pre_list) if pre_list else "None"

        op_list = []
        if ap.get("op_left_chk"): op_list.append(f"Left {ap.get('op_left_val', 'TKR')}")
        if ap.get("op_right_chk"): op_list.append(f"Right {ap.get('op_right_val', 'TKR')}")
        if ap.get("op_bi_chk"): op_list.append(f"Bilateral {ap.get('op_bi_val', 'TKR')}")

        op_string = ", ".join(op_list)
        if ap.get("op_notes", "").strip():
            if op_string:
                op_string += f" | Notes: {ap['op_notes']}"
            else:
                op_string = f"Notes: {ap['op_notes']}"
        if not op_string.strip(): op_string = "None recorded"

        sel = []
        for eid, data in ap["exercises"].items():
            ex_name = next((x["name"] for cat in EXERCISE_DB.values() for x in cat if x["id"] == eid), "Unknown")
            ex_data = {"id": eid, "name": ex_name}

            if isinstance(data, dict):
                ex_data.update(data)
                if ex_data.get('region') == 'Other (Type below)' and 'other_region' in ex_data:
                    ex_data['region'] = ex_data['other_region']
                if ex_data.get('roller_region') == '其他' and 'custom_roller_region' in ex_data:
                    ex_data['roller_region'] = ex_data['custom_roller_region']
            sel.append(ex_data)

        final_ticket = ap.get("daily_seq_no")
        if not final_ticket:
            final_ticket = get_and_reserve_ticket()

        # Compile the new structured assessment payload
        assess_payload = {
            "pain_l": ap.get("a_pain_l", "N/A"),
            "pain_r": ap.get("a_pain_r", "N/A"),
            "tol": ap.get("a_tol", ""),
            "aid": ap.get("a_aid", "None"),
            "trans": ap.get("a_trans", []),
            "med_panadol": ap.get("a_med_panadol", False),
            "med_panadol_dose": ap.get("a_med_panadol_dose", "500 mg"),
            "med_panadol_freq": ap.get("a_med_panadol_freq", "QD"),
            "med_tramadol": ap.get("a_med_tramadol", False),
            "med_tramadol_freq": ap.get("a_med_tramadol_freq", "QD"),
            "med_arcoxia": ap.get("a_med_arcoxia", False),
            "med_arcoxia_freq": ap.get("a_med_arcoxia_freq", "QD"),
            "med_celebrex": ap.get("a_med_celebrex", False),
            "med_celebrex_freq": ap.get("a_med_celebrex_freq", "QD"),
            "med_lyrica": ap.get("a_med_lyrica", False),
            "med_lyrica_freq": ap.get("a_med_lyrica_freq", "QD"),
            "med_df118": ap.get("a_med_df118", False),
            "med_df118_freq": ap.get("a_med_df118_freq", "QD"),

            "rom_l": ap.get("a_rom_l", ""),
            "rom_r": ap.get("a_rom_r", ""),
            "quad_l": ap.get("a_quad_l", ""),
            "quad_r": ap.get("a_quad_r", ""),
            "ham_l": ap.get("a_ham_l", ""),
            "ham_r": ap.get("a_ham_r", ""),

            "hip_rom_flex_l": ap.get("a_hip_rom_flex_l", ""),
            "hip_rom_flex_r": ap.get("a_hip_rom_flex_r", ""),
            "hip_rom_abd_l": ap.get("a_hip_rom_abd_l", ""),
            "hip_rom_abd_r": ap.get("a_hip_rom_abd_r", ""),
            "hip_str_flex_l": ap.get("a_hip_str_flex_l", ""),
            "hip_str_flex_r": ap.get("a_hip_str_flex_r", ""),
            "hip_str_abd_l": ap.get("a_hip_str_abd_l", ""),
            "hip_str_abd_r": ap.get("a_hip_str_abd_r", ""),

            "free_text": ap.get("assessment", "")
        }
        final_assessment_str = json.dumps(assess_payload, ensure_ascii=False)

        save_h(ap["case_no"], ap["p_name"], sel, op_string,
               ap.get("op_date", datetime.now().date()).strftime("%Y-%m-%d"), ap["p_class"], final_pre, 1,
               ap["current_nd"], ap["current_nt"], final_assessment_str, st.session_state.current_therapist,
               final_ticket)

        ap.clear()
        ap.update({
            "case_no": "", "p_name": "", "p_class": "None",
            "p_att": False, "p_fing": False, "exercises": {},
            "assessment": "", "a_pain_l": "N/A", "a_pain_r": "N/A", "a_tol": "", "a_aid": "None", "a_trans": [],
            "a_med_panadol": False, "a_med_panadol_dose": "500 mg", "a_med_panadol_freq": "QD",
            "a_med_tramadol": False, "a_med_tramadol_freq": "QD",
            "a_med_arcoxia": False, "a_med_arcoxia_freq": "QD",
            "a_med_celebrex": False, "a_med_celebrex_freq": "QD",
            "a_med_lyrica": False, "a_med_lyrica_freq": "QD",
            "a_med_df118": False, "a_med_df118_freq": "QD",
            "a_rom_l": "", "a_rom_r": "", "a_quad_l": "", "a_quad_r": "", "a_ham_l": "", "a_ham_r": "",
            "a_hip_rom_flex_l": "", "a_hip_rom_flex_r": "", "a_hip_rom_abd_l": "", "a_hip_rom_abd_r": "",
            "a_hip_str_flex_l": "", "a_hip_str_flex_r": "", "a_hip_str_abd_l": "", "a_hip_str_abd_r": "",
            "current_chk": 1, "current_nd": "None", "current_nt": "None", "is_loaded": False,
            "op_left_chk": False, "op_left_val": "TKR",
            "op_right_chk": False, "op_right_val": "TKR",
            "op_bi_chk": False, "op_bi_val": "TKR",
            "op_notes": "", "op_date": datetime.now().date(),
            "daily_seq_no": None
        })
        nav_to("🗒️ Active Cases")


    # --- TOP SECTION: Patient Data Container ---
    with st.container(border=True):
        st.markdown(
            "<h4 style='color: #01579b; margin-top: -10px; margin-bottom: 15px;'>👤 Patient Data & Operation Details</h4>",
            unsafe_allow_html=True)
        p_c1, p_c2, p_c3 = st.columns([1.2, 1, 1.8])

        with p_c1:
            st.text_input("Case Number", value=ap["case_no"], key="rx_case", on_change=sync_form)
            st.text_input("Name", value=ap["p_name"], key="rx_name", on_change=sync_form)

            opts = ["Class I", "Class II", "Class III"]
            current_cls = ap.get("p_class", "None")
            idx = opts.index(current_cls) if current_cls in opts else None
            st.radio("Mobility Class", opts, index=idx, horizontal=True, key="rx_class", on_change=sync_form)

        with p_c2:
            st.markdown("**Precautions:**")
            st.checkbox("多注目", value=ap["p_att"], key="rx_att", on_change=sync_form)
            st.checkbox("夾手指做運動", value=ap["p_fing"], key="rx_fing", on_change=sync_form)
            st.date_input("Date of Operation", value=ap.get("op_date", datetime.now().date()), key="rx_op_d",
                          on_change=sync_form)

        with p_c3:
            st.markdown("**Operation Details:**")
            op_choices = ["TKR", "UKA", "HTO", "THR"]

            c_op1, c_op2, c_op3 = st.columns(3)
            with c_op1:
                if st.checkbox("Left", value=ap.get("op_left_chk", False), key="rx_op_l_chk", on_change=sync_form):
                    st.selectbox("Op", op_choices, index=op_choices.index(ap.get("op_left_val", "TKR")),
                                 key="rx_op_l_val", on_change=sync_form, label_visibility="collapsed")
            with c_op2:
                if st.checkbox("Right", value=ap.get("op_right_chk", False), key="rx_op_r_chk", on_change=sync_form):
                    st.selectbox("Op", op_choices, index=op_choices.index(ap.get("op_right_val", "TKR")),
                                 key="rx_op_r_val", on_change=sync_form, label_visibility="collapsed")
            with c_op3:
                if st.checkbox("Bilateral", value=ap.get("op_bi_chk", False), key="rx_op_b_chk", on_change=sync_form):
                    st.selectbox("Op", op_choices, index=op_choices.index(ap.get("op_bi_val", "TKR")),
                                 key="rx_op_b_val", on_change=sync_form, label_visibility="collapsed")

            st.text_area("Other Details / Complications", value=ap.get("op_notes", ""), placeholder="e.g., bleeding...",
                         key="rx_op_notes", on_change=sync_form, height=68)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BOTTOM SECTION: Cart (Left) and Select (Right) ---
    col_cart, col_select = st.columns([1.2, 1.2], gap="large")

    with col_cart:
        with st.container(border=True):
            st.markdown("<h4 style='color: #01579b; margin-top: -10px; margin-bottom: 10px;'>🛒 Exercise Cart</h4>",
                        unsafe_allow_html=True)
            if not ap["exercises"]:
                st.info("👈 Select exercises from the right panel to add them to your cart.")
            else:
                for eid, data in list(ap["exercises"].items()):
                    ex_name, ex_cat = get_ex_info(eid)

                    with st.container(border=True):
                        c_title, c_del = st.columns([0.8, 0.2])
                        with c_title:
                            st.markdown(f"**{ex_name}**")
                        with c_del:
                            st.button("🗑️", key=f"del_cart_{eid}", help="Remove from Cart", on_click=remove_cart_item,
                                      args=(eid,))

                        if ex_cat == "Electrotherapy":
                            if eid == "e1":  # 冰磁
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "15"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["Right knee", "Left knee", "Bilateral knee"]
                                    current = data.get("side", "Right knee")
                                    st.selectbox("Side", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_side_{eid}", on_change=update_dict,
                                                 args=(eid, "side", f"ui_side_{eid}"))

                            elif eid == "e2":  # Gameready
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "15"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts_s = ["Right", "Left"]
                                    current_s = data.get("side", "Right")
                                    st.selectbox("Side", opts_s,
                                                 index=opts_s.index(current_s) if current_s in opts_s else 0,
                                                 key=f"ui_side_{eid}", on_change=update_dict,
                                                 args=(eid, "side", f"ui_side_{eid}"))
                                c3, c4 = st.columns(2)
                                with c3:
                                    opts_p = ["Low", "Medium"]
                                    current_p = data.get("pressure", "Low")
                                    st.selectbox("Pressure", opts_p,
                                                 index=opts_p.index(current_p) if current_p in opts_p else 0,
                                                 key=f"ui_pres_{eid}", on_change=update_dict,
                                                 args=(eid, "pressure", f"ui_pres_{eid}"))
                                with c4:
                                    st.text_input("Degree", value=data.get("degree", ""), placeholder="e.g. 10",
                                                  key=f"ui_deg_{eid}", on_change=update_dict,
                                                  args=(eid, "degree", f"ui_deg_{eid}"))

                            elif eid == "e3":  # EMS
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "15"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts_s = ["Right Quad", "Left Quad", "Bilateral Quad"]
                                    current_s = data.get("side", "Right Quad")
                                    st.selectbox("Side", opts_s,
                                                 index=opts_s.index(current_s) if current_s in opts_s else 0,
                                                 key=f"ui_side_{eid}", on_change=update_dict,
                                                 args=(eid, "side", f"ui_side_{eid}"))
                                c3, c4 = st.columns(2)
                                with c3:
                                    opts_m = ["Static Quad", "Quad board 踢腳", "沙包壓腳"]
                                    current_m = data.get("mode", "Static Quad")
                                    st.selectbox("Mode", opts_m,
                                                 index=opts_m.index(current_m) if current_m in opts_m else 0,
                                                 key=f"ui_mode_{eid}", on_change=update_dict,
                                                 args=(eid, "mode", f"ui_mode_{eid}"))
                                if data.get("mode", "Static Quad") == "沙包壓腳":
                                    with c4:
                                        st.text_input("Weight (lbs)", value=data.get("weight", ""), key=f"ui_w_{eid}",
                                                      on_change=update_dict, args=(eid, "weight", f"ui_w_{eid}"))

                            elif eid == "e4":  # Lymphapress
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "15"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts_s = ["Right", "Left", "Alternate bilateral"]
                                    current_s = data.get("side", "Right")
                                    st.selectbox("Side", opts_s,
                                                 index=opts_s.index(current_s) if current_s in opts_s else 0,
                                                 key=f"ui_side_{eid}", on_change=update_dict,
                                                 args=(eid, "side", f"ui_side_{eid}"))
                                c3, _ = st.columns(2)
                                with c3:
                                    opts_p = ["40", "50", "60"]
                                    current_p = data.get("pressure", "40")
                                    st.selectbox("Pressure", opts_p,
                                                 index=opts_p.index(current_p) if current_p in opts_p else 0,
                                                 key=f"ui_pres_{eid}", on_change=update_dict,
                                                 args=(eid, "pressure", f"ui_pres_{eid}"))

                            elif eid == "e5":  # Hot pack
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "15"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts_s = ["左", "右", "雙側"]
                                    current_s = data.get("side", "左")
                                    st.selectbox("Side", opts_s,
                                                 index=opts_s.index(current_s) if current_s in opts_s else 0,
                                                 key=f"ui_side_{eid}", on_change=update_dict,
                                                 args=(eid, "side", f"ui_side_{eid}"))
                                c3, c4 = st.columns(2)
                                with c3:
                                    opts_r = ["大髀前", "大髀後", "小腿前", "小腿後", "內側", "外側",
                                              "Other (Type below)"]
                                    current_r = data.get("region", "大髀前")
                                    st.selectbox("Region", opts_r,
                                                 index=opts_r.index(current_r) if current_r in opts_r else 0,
                                                 key=f"ui_reg_{eid}", on_change=update_dict,
                                                 args=(eid, "region", f"ui_reg_{eid}"))
                                with c4:
                                    st.text_input("Custom Region", value=data.get("custom_region", ""),
                                                  placeholder="Type here...", key=f"ui_creg_{eid}",
                                                  on_change=update_dict,
                                                  args=(eid, "custom_region", f"ui_creg_{eid}"))

                        elif ex_cat == "Mobilization":
                            if eid == "s3":  # Knee to chest
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["None", "紅波", "藍波"]
                                    current = data.get("ball", "None")
                                    st.selectbox("Option", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_ball_{eid}", on_change=update_dict,
                                                 args=(eid, "ball", f"ui_ball_{eid}"))

                            elif eid == "s4":  # Static bike
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["半圈", "全圈"]
                                    current = data.get("circle", "半圈")
                                    st.selectbox("Option", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_circ_{eid}", on_change=update_dict,
                                                 args=(eid, "circle", f"ui_circ_{eid}"))

                            elif eid == "s5":  # Nustep
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.text_input("Resistance", value=data.get("res", ""), key=f"ui_res_{eid}",
                                                  on_change=update_dict, args=(eid, "res", f"ui_res_{eid}"))
                                with c3:
                                    st.text_input("Seat", value=data.get("seat", ""), key=f"ui_seat_{eid}",
                                                  on_change=update_dict, args=(eid, "seat", f"ui_seat_{eid}"))
                                c4, c5 = st.columns(2)
                                with c4:
                                    st.checkbox("用手", value=data.get("hands", False), key=f"ui_hnds_{eid}",
                                                on_change=update_dict, args=(eid, "hands", f"ui_hnds_{eid}"))
                                with c5:
                                    st.checkbox("Long Seat", value=data.get("lseat", False), key=f"ui_lseat_{eid}",
                                                on_change=update_dict, args=(eid, "lseat", f"ui_lseat_{eid}"))

                            elif eid == "s9":  # RT300
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.text_input("Resistance (Nm)", value=data.get("rt_res", ""),
                                                  key=f"ui_rtres_{eid}",
                                                  on_change=update_dict, args=(eid, "rt_res", f"ui_rtres_{eid}"))

                            elif eid == "s10":  # Cybercycle
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["easy", "medium"]
                                    current = data.get("mode", "easy")
                                    st.selectbox("Mode", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_mode_{eid}", on_change=update_dict,
                                                 args=(eid, "mode", f"ui_mode_{eid}"))

                            elif eid == "s11":  # Sling suspension
                                c1, _ = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))

                                st.checkbox("平訓 ＋左右 (Abduction)", value=data.get("sling_abd", False),
                                            key=f"ui_sabd_{eid}", on_change=update_dict,
                                            args=(eid, "sling_abd", f"ui_sabd_{eid}"))
                                if data.get("sling_abd", False):
                                    cb1, cb2 = st.columns(2)
                                    with cb1:
                                        st.checkbox("加橡根", value=data.get("sabd_tb", False), key=f"ui_sabdtb_{eid}",
                                                    on_change=update_dict, args=(eid, "sabd_tb", f"ui_sabdtb_{eid}"))
                                    if data.get("sabd_tb", False):
                                        with cb2:
                                            opts = ["紅橡根", "綠橡根"]
                                            curr = data.get("sabd_color", "紅橡根")
                                            st.selectbox("Color", opts, index=opts.index(curr) if curr in opts else 0,
                                                         key=f"ui_sabdcol_{eid}", on_change=update_dict,
                                                         args=(eid, "sabd_color", f"ui_sabdcol_{eid}"),
                                                         label_visibility="collapsed")

                                st.checkbox("側訓 + 前後 (Flexion/ Extension)", value=data.get("sling_flex", False),
                                            key=f"ui_sflx_{eid}", on_change=update_dict,
                                            args=(eid, "sling_flex", f"ui_sflx_{eid}"))
                                if data.get("sling_flex", False):
                                    cf1, cf2 = st.columns(2)
                                    with cf1:
                                        st.checkbox("加橡根", value=data.get("sflx_tb", False), key=f"ui_sflxtb_{eid}",
                                                    on_change=update_dict, args=(eid, "sflx_tb", f"ui_sflxtb_{eid}"))
                                    if data.get("sflx_tb", False):
                                        with cf2:
                                            opts = ["紅橡根", "綠橡根"]
                                            curr = data.get("sflx_color", "紅橡根")
                                            st.selectbox("Color", opts, index=opts.index(curr) if curr in opts else 0,
                                                         key=f"ui_sflxcol_{eid}", on_change=update_dict,
                                                         args=(eid, "sflx_color", f"ui_sflxcol_{eid}"),
                                                         label_visibility="collapsed")

                            elif eid == "s12":  # 遊乾水
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                                    st.checkbox("毛巾於膝下", value=data.get("towel", False), key=f"ui_twl_{eid}",
                                                on_change=update_dict, args=(eid, "towel", f"ui_twl_{eid}"))

                        elif ex_cat == "Strengthening":
                            if eid in ["st1", "st2"]:  # 踢沙包 / 企 ＋ 屈腳
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.text_input("Sandbag (lbs)", value=data.get("weight", ""), key=f"ui_w_{eid}",
                                                  on_change=update_dict, args=(eid, "weight", f"ui_w_{eid}"))

                            elif eid in ["st3", "st7"]:  # 挨花生波 / 花生波拱橋
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["None", "紅波", "藍波"]
                                    current = data.get("ball", "None")
                                    st.selectbox("Option", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_ball_{eid}", on_change=update_dict,
                                                 args=(eid, "ball", f"ui_ball_{eid}"))

                            elif eid == "st8":  # Minipress
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts_s = ["Right", "Left", "Bilateral"]
                                    current_s = data.get("side", "Right")
                                    st.selectbox("Side", opts_s,
                                                 index=opts_s.index(current_s) if current_s in opts_s else 0,
                                                 key=f"ui_side_{eid}", on_change=update_dict,
                                                 args=(eid, "side", f"ui_side_{eid}"))
                                c3, c4 = st.columns(2)
                                with c3:
                                    st.text_input("Black cord", value=data.get("black_cord", ""), placeholder="e.g. 2",
                                                  key=f"ui_blk_{eid}", on_change=update_dict,
                                                  args=(eid, "black_cord", f"ui_blk_{eid}"))
                                with c4:
                                    st.text_input("Red cord", value=data.get("red_cord", ""), placeholder="e.g. 1",
                                                  key=f"ui_red_{eid}", on_change=update_dict,
                                                  args=(eid, "red_cord", f"ui_red_{eid}"))

                            elif eid == "st9":  # 坐 Hip Abduction
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["None", "紅橡根", "綠橡根"]
                                    current = data.get("band", "None")
                                    st.selectbox("Band Option", opts,
                                                 index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_band_{eid}", on_change=update_dict,
                                                 args=(eid, "band", f"ui_band_{eid}"))

                            elif eid == "st4":  # 企 Hip strengthening (Multi-direction)
                                st.caption("Select Leg:")
                                st.checkbox("Right Leg", value=data.get("right_leg", False), key=f"ui_{eid}_rleg",
                                            on_change=update_dict, args=(eid, "right_leg", f"ui_{eid}_rleg"))
                                if data.get("right_leg", False):
                                    with st.container(border=True):
                                        r_dirs = [("rf", "右前"), ("ra", "右側"), ("re", "右後")]
                                        for d_id, d_label in r_dirs:
                                            chk_key = f"{d_id}_chk"
                                            st.checkbox(f"{d_label}", value=data.get(chk_key, False),
                                                        key=f"ui_{eid}_{chk_key}", on_change=update_dict,
                                                        args=(eid, chk_key, f"ui_{eid}_{chk_key}"))
                                            if data.get(chk_key, False):
                                                c1, c2, c3 = st.columns(3)
                                                with c1:
                                                    st.text_input("Mins", value=data.get(f"{d_id}_mins", "10"),
                                                                  key=f"ui_min_{eid}_{d_id}", on_change=update_dict,
                                                                  args=(eid, f"{d_id}_mins", f"ui_min_{eid}_{d_id}"))
                                                with c2:
                                                    st.markdown("<div style='margin-top: 35px;'></div>",
                                                                unsafe_allow_html=True)
                                                    st.checkbox("腳踩地", value=data.get(f"{d_id}_gnd", False),
                                                                key=f"ui_gnd_{eid}_{d_id}", on_change=update_dict,
                                                                args=(eid, f"{d_id}_gnd", f"ui_gnd_{eid}_{d_id}"))
                                                with c3:
                                                    st.checkbox("加橡根", value=data.get(f"{d_id}_band_chk", False),
                                                                key=f"ui_bnd_{eid}_{d_id}", on_change=update_dict,
                                                                args=(eid, f"{d_id}_band_chk", f"ui_bnd_{eid}_{d_id}"))
                                                    if data.get(f"{d_id}_band_chk", False):
                                                        opts = ["紅橡根", "綠橡根"]
                                                        curr = data.get(f"{d_id}_band_color", "紅橡根")
                                                        st.selectbox("Color", opts,
                                                                     index=opts.index(curr) if curr in opts else 0,
                                                                     key=f"ui_bcol_{eid}_{d_id}", on_change=update_dict,
                                                                     args=(eid, f"{d_id}_band_color",
                                                                           f"ui_bcol_{eid}_{d_id}"),
                                                                     label_visibility="collapsed")

                                st.checkbox("Left Leg", value=data.get("left_leg", False), key=f"ui_{eid}_lleg",
                                            on_change=update_dict, args=(eid, "left_leg", f"ui_{eid}_lleg"))
                                if data.get("left_leg", False):
                                    with st.container(border=True):
                                        l_dirs = [("lf", "左前"), ("la", "左側"), ("le", "左後")]
                                        for d_id, d_label in l_dirs:
                                            chk_key = f"{d_id}_chk"
                                            st.checkbox(f"{d_label}", value=data.get(chk_key, False),
                                                        key=f"ui_{eid}_{chk_key}", on_change=update_dict,
                                                        args=(eid, chk_key, f"ui_{eid}_{chk_key}"))
                                            if data.get(chk_key, False):
                                                c1, c2, c3 = st.columns(3)
                                                with c1:
                                                    st.text_input("Mins", value=data.get(f"{d_id}_mins", "10"),
                                                                  key=f"ui_min_{eid}_{d_id}", on_change=update_dict,
                                                                  args=(eid, f"{d_id}_mins", f"ui_min_{eid}_{d_id}"))
                                                with c2:
                                                    st.markdown("<div style='margin-top: 35px;'></div>",
                                                                unsafe_allow_html=True)
                                                    st.checkbox("腳踩地", value=data.get(f"{d_id}_gnd", False),
                                                                key=f"ui_gnd_{eid}_{d_id}", on_change=update_dict,
                                                                args=(eid, f"{d_id}_gnd", f"ui_gnd_{eid}_{d_id}"))
                                                with c3:
                                                    st.checkbox("加橡根", value=data.get(f"{d_id}_band_chk", False),
                                                                key=f"ui_bnd_{eid}_{d_id}", on_change=update_dict,
                                                                args=(eid, f"{d_id}_band_chk", f"ui_bnd_{eid}_{d_id}"))
                                                    if data.get(f"{d_id}_band_chk", False):
                                                        opts = ["紅橡根", "綠橡根"]
                                                        curr = data.get(f"{d_id}_band_color", "紅橡根")
                                                        st.selectbox("Color", opts,
                                                                     index=opts.index(curr) if curr in opts else 0,
                                                                     key=f"ui_bcol_{eid}_{d_id}", on_change=update_dict,
                                                                     args=(eid, f"{d_id}_band_color",
                                                                           f"ui_bcol_{eid}_{d_id}"),
                                                                     label_visibility="collapsed")

                        elif ex_cat == "Functional":
                            if eid == "f4":  # 踏級
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["4\"", "6\"", "8\""]
                                    current = data.get("box_height", "4\"")
                                    st.selectbox("Height", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_hgt_{eid}", on_change=update_dict,
                                                 args=(eid, "box_height", f"ui_hgt_{eid}"))
                                with c3:
                                    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                                    st.checkbox("落級", value=data.get("downstairs", False),
                                                key=f"ui_dwst_{eid}", on_change=update_dict,
                                                args=(eid, "downstairs", f"ui_dwst_{eid}"))

                            elif eid == "f6":  # 跨欄
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["4\"", "6\""]
                                    current = data.get("hurdle_height", "4\"")
                                    st.selectbox("Height", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_hgt_{eid}", on_change=update_dict,
                                                 args=(eid, "hurdle_height", f"ui_hgt_{eid}"))

                            elif eid == "f13":  # 海綿踏步
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                                    st.checkbox("平衡架內", value=data.get("pbar", False), key=f"ui_pbar_{eid}",
                                                on_change=update_dict, args=(eid, "pbar", f"ui_pbar_{eid}"))
                                with c3:
                                    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                                    st.checkbox("家人陪", value=data.get("family", False), key=f"ui_fam_{eid}",
                                                on_change=update_dict, args=(eid, "family", f"ui_fam_{eid}"))

                            elif eid == "f8":  # PWB踩磅
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.text_input("Target weight", value=data.get("target_wt", ""), key=f"ui_twt_{eid}",
                                                  on_change=update_dict, args=(eid, "target_wt", f"ui_twt_{eid}"))

                            elif eid == "f11":  # 海綿單腳企
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    st.text_input("Target (seconds)", value=data.get("target_sec", ""),
                                                  key=f"ui_tsec_{eid}", on_change=update_dict,
                                                  args=(eid, "target_sec", f"ui_tsec_{eid}"))

                            else:
                                c1, _ = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))

                        elif ex_cat == "Others":
                            if eid in ["o1", "o4"]:  # 按摩棍 / 網球
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    if eid == "o1":
                                        opts = ["大脾前", "大脾外側", "大脾內側", "大脾後", "小腿後", "其他"]
                                        default_val = "大脾前"
                                    else:
                                        opts = ["大脾後", "小腿後", "其他"]
                                        default_val = "大脾後"

                                    current = data.get("roller_region", default_val)
                                    if current not in opts: current = default_val

                                    st.selectbox("Region", opts, index=opts.index(current),
                                                 key=f"ui_rreg_{eid}", on_change=update_dict,
                                                 args=(eid, "roller_region", f"ui_rreg_{eid}"))
                                with c3:
                                    if data.get("roller_region", default_val) == "其他":
                                        st.text_input("Custom Region", value=data.get("custom_roller_region", ""),
                                                      placeholder="Type here...", key=f"ui_crreg_{eid}",
                                                      on_change=update_dict,
                                                      args=(eid, "custom_roller_region", f"ui_crreg_{eid}"))
                            elif eid == "o3":  # 斜板
                                c1, c2 = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))
                                with c2:
                                    opts = ["1格", "2格", "3格", "4格"]
                                    current = data.get("slant_level", "1格")
                                    st.selectbox("Level", opts, index=opts.index(current) if current in opts else 0,
                                                 key=f"ui_slant_{eid}", on_change=update_dict,
                                                 args=(eid, "slant_level", f"ui_slant_{eid}"))
                            else:
                                c1, _ = st.columns(2)
                                with c1:
                                    st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                                  on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))

                        elif ex_cat in ["Walking Exercise", "Assessment"]:
                            st.caption("Standard item. No additional parameters required.")

                        else:
                            c1, _ = st.columns(2)
                            with c1:
                                st.text_input("Mins", value=data.get("mins", "10"), key=f"ui_min_{eid}",
                                              on_change=update_dict, args=(eid, "mins", f"ui_min_{eid}"))

                st.markdown("<br>", unsafe_allow_html=True)
                btn_label = "💾 Finalize & Check In to Gym" if ap["is_loaded"] else "🚀 Generate & Check In"
                st.button(btn_label, type="primary", use_container_width=True, on_click=check_in_patient)

    with col_select:
        with st.container(border=True):
            st.markdown("<h4 style='color: #01579b; margin-top: -10px; margin-bottom: 10px;'>✔️ Select Exercises</h4>",
                        unsafe_allow_html=True)
            s_c1, s_c2 = st.columns(2)

            for cat, items in EXERCISE_DB.items():
                if cat in ["Electrotherapy", "Mobilization", "Strengthening"]:
                    col_to_use = s_c1
                else:
                    col_to_use = s_c2

                with col_to_use:
                    st.markdown(f'<div class="cat-header">{cat}</div>', unsafe_allow_html=True)
                    for ex in items:
                        eid = ex["id"]
                        is_selected = eid in ap["exercises"]
                        st.checkbox(ex["name"], value=is_selected, key=f"ui_{eid}", on_change=toggle_ex, args=(eid,))

# --- PAGE 4: ACTIVE CASES ---
elif page == "🗒️ Active Cases":
    st.subheader("Active Cases in Room")
    conn = sqlite3.connect(DB_FILE, timeout=10)
    raw_rows = conn.execute(
        "SELECT id, case_no, p_name, prescription_json, next_appt_date, next_appt_time, assessment_text, p_precautions, therapist, op_details, op_date, p_class, daily_seq_no FROM history WHERE is_checked_in = 1 AND id IN (SELECT MAX(id) FROM history GROUP BY case_no) ORDER BY id DESC").fetchall()
    queued_cases = [r[0] for r in conn.execute("SELECT case_no FROM queues").fetchall()]
    conn.close()

    # DECRYPT FOR DISPLAY
    rows = []
    for r in raw_rows:
        rows.append((
            r[0], r[1], decrypt_data(r[2]), decrypt_data(r[3]), r[4], r[5],
            decrypt_data(r[6]), decrypt_data(r[7]), r[8], decrypt_data(r[9]), r[10], r[11], r[12]
        ))
    rows = sorted(rows, key=lambda x: x[12] if x[12] is not None else 9999)


    def edit_active_prescription(r):
        ex_dict = {}
        try:
            data = json.loads(r[3])
            if isinstance(data, str): data = json.loads(data)
            for item in data:
                eid = item.get("id")
                if eid:
                    parsed_data = {k: v for k, v in item.items() if k not in ["id", "name"]}
                    if f"{eid}_weight" in parsed_data: parsed_data["weight"] = parsed_data.pop(f"{eid}_weight")
                    ex_dict[eid] = parsed_data
        except Exception:
            pass

        op_details = r[9] if r[9] and r[9] != "None recorded" else ""
        op_notes = ""
        if " | Notes: " in op_details:
            parts = op_details.split(" | Notes: ")
            op_details = parts[0]
            op_notes = parts[1]
        elif op_details.startswith("Notes: "):
            op_notes = op_details.replace("Notes: ", "")
            op_details = ""

        op_left_chk, op_left_val = False, "TKR"
        op_right_chk, op_right_val = False, "TKR"
        op_bi_chk, op_bi_val = False, "TKR"

        for val in ["TKR", "UKA", "HTO", "THR"]:
            if f"Left {val}" in op_details:
                op_left_chk, op_left_val = True, val
            if f"Right {val}" in op_details:
                op_right_chk, op_right_val = True, val
            if f"Bilateral {val}" in op_details:
                op_bi_chk, op_bi_val = True, val

        try:
            parsed_op_date = datetime.strptime(r[10], '%Y-%m-%d').date() if r[10] else datetime.now().date()
        except Exception:
            parsed_op_date = datetime.now().date()

        raw_assess = r[6] if r[6] else ""
        try:
            parsed_a = json.loads(raw_assess)
            if isinstance(parsed_a, dict) and "free_text" in parsed_a:
                ap_assessment = parsed_a["free_text"]
                ap_a_pain_l = str(parsed_a.get("pain_l", parsed_a.get("pain", "N/A")))
                ap_a_pain_r = str(parsed_a.get("pain_r", parsed_a.get("pain", "N/A")))
                ap_a_tol = parsed_a.get("tol", "")
                ap_a_aid = parsed_a.get("aid", "None")
                ap_a_trans = parsed_a.get("trans", [])
                ap_a_med_panadol = parsed_a.get("med_panadol", False)
                ap_a_med_panadol_dose = parsed_a.get("med_panadol_dose", "500 mg")
                ap_a_med_panadol_freq = parsed_a.get("med_panadol_freq", "QD")
                ap_a_med_tramadol = parsed_a.get("med_tramadol", False)
                ap_a_med_tramadol_freq = parsed_a.get("med_tramadol_freq", "QD")
                ap_a_med_arcoxia = parsed_a.get("med_arcoxia", False)
                ap_a_med_arcoxia_freq = parsed_a.get("med_arcoxia_freq", "QD")
                ap_a_med_celebrex = parsed_a.get("med_celebrex", False)
                ap_a_med_celebrex_freq = parsed_a.get("med_celebrex_freq", "QD")
                ap_a_med_lyrica = parsed_a.get("med_lyrica", False)
                ap_a_med_lyrica_freq = parsed_a.get("med_lyrica_freq", "QD")
                ap_a_med_df118 = parsed_a.get("med_df118", False)
                ap_a_med_df118_freq = parsed_a.get("med_df118_freq", "QD")

                ap_a_rom_l = parsed_a.get("rom_l", parsed_a.get("rom", ""))
                ap_a_rom_r = parsed_a.get("rom_r", parsed_a.get("rom", ""))
                ap_a_quad_l = parsed_a.get("quad_l", parsed_a.get("quad", ""))
                ap_a_quad_r = parsed_a.get("quad_r", parsed_a.get("quad", ""))
                ap_a_ham_l = parsed_a.get("ham_l", parsed_a.get("ham", ""))
                ap_a_ham_r = parsed_a.get("ham_r", parsed_a.get("ham", ""))

                ap_a_hip_rom_flex_l = parsed_a.get("hip_rom_flex_l", "")
                ap_a_hip_rom_flex_r = parsed_a.get("hip_rom_flex_r", "")
                ap_a_hip_rom_abd_l = parsed_a.get("hip_rom_abd_l", "")
                ap_a_hip_rom_abd_r = parsed_a.get("hip_rom_abd_r", "")
                ap_a_hip_str_flex_l = parsed_a.get("hip_str_flex_l", "")
                ap_a_hip_str_flex_r = parsed_a.get("hip_str_flex_r", "")
                ap_a_hip_str_abd_l = parsed_a.get("hip_str_abd_l", "")
                ap_a_hip_str_abd_r = parsed_a.get("hip_str_abd_r", "")
            else:
                ap_assessment, ap_a_pain_l, ap_a_pain_r, ap_a_tol, ap_a_aid, ap_a_trans = raw_assess, "N/A", "N/A", "", "None", []
                ap_a_med_panadol, ap_a_med_panadol_dose, ap_a_med_panadol_freq = False, "500 mg", "QD"
                ap_a_med_tramadol, ap_a_med_tramadol_freq = False, "QD"
                ap_a_med_arcoxia, ap_a_med_arcoxia_freq = False, "QD"
                ap_a_med_celebrex, ap_a_med_celebrex_freq = False, "QD"
                ap_a_med_lyrica, ap_a_med_lyrica_freq = False, "QD"
                ap_a_med_df118, ap_a_med_df118_freq = False, "QD"
                ap_a_rom_l, ap_a_rom_r, ap_a_quad_l, ap_a_quad_r, ap_a_ham_l, ap_a_ham_r = "", "", "", "", "", ""
                ap_a_hip_rom_flex_l, ap_a_hip_rom_flex_r, ap_a_hip_rom_abd_l, ap_a_hip_rom_abd_r = "", "", "", ""
                ap_a_hip_str_flex_l, ap_a_hip_str_flex_r, ap_a_hip_str_abd_l, ap_a_hip_str_abd_r = "", "", "", ""
        except:
            ap_assessment, ap_a_pain_l, ap_a_pain_r, ap_a_tol, ap_a_aid, ap_a_trans = raw_assess, "N/A", "N/A", "", "None", []
            ap_a_med_panadol, ap_a_med_panadol_dose, ap_a_med_panadol_freq = False, "500 mg", "QD"
            ap_a_med_tramadol, ap_a_med_tramadol_freq = False, "QD"
            ap_a_med_arcoxia, ap_a_med_arcoxia_freq = False, "QD"
            ap_a_med_celebrex, ap_a_med_celebrex_freq = False, "QD"
            ap_a_med_lyrica, ap_a_med_lyrica_freq = False, "QD"
            ap_a_med_df118, ap_a_med_df118_freq = False, "QD"
            ap_a_rom_l, ap_a_rom_r, ap_a_quad_l, ap_a_quad_r, ap_a_ham_l, ap_a_ham_r = "", "", "", "", "", ""
            ap_a_hip_rom_flex_l, ap_a_hip_rom_flex_r, ap_a_hip_rom_abd_l, ap_a_hip_rom_abd_r = "", "", "", ""
            ap_a_hip_str_flex_l, ap_a_hip_str_flex_r, ap_a_hip_str_abd_l, ap_a_hip_str_abd_r = "", "", "", ""

        st.session_state.active_patient = {
            "case_no": r[1], "p_name": r[2],
            "p_class": r[11] if r[11] and r[11] != "None" else "None",
            "p_att": "多注目" in (r[7] or ""), "p_fing": "夾手指做運動" in (r[7] or ""),
            "exercises": ex_dict,

            "assessment": ap_assessment,
            "a_pain_l": ap_a_pain_l, "a_pain_r": ap_a_pain_r, "a_tol": ap_a_tol, "a_aid": ap_a_aid,
            "a_trans": ap_a_trans,
            "a_med_panadol": ap_a_med_panadol, "a_med_panadol_dose": ap_a_med_panadol_dose,
            "a_med_panadol_freq": ap_a_med_panadol_freq,
            "a_med_tramadol": ap_a_med_tramadol, "a_med_tramadol_freq": ap_a_med_tramadol_freq,
            "a_med_arcoxia": ap_a_med_arcoxia, "a_med_arcoxia_freq": ap_a_med_arcoxia_freq,
            "a_med_celebrex": ap_a_med_celebrex, "a_med_celebrex_freq": ap_a_med_celebrex_freq,
            "a_med_lyrica": ap_a_med_lyrica, "a_med_lyrica_freq": ap_a_med_lyrica_freq,
            "a_med_df118": ap_a_med_df118, "a_med_df118_freq": ap_a_med_df118_freq,
            "a_rom_l": ap_a_rom_l, "a_rom_r": ap_a_rom_r,
            "a_quad_l": ap_a_quad_l, "a_quad_r": ap_a_quad_r,
            "a_ham_l": ap_a_ham_l, "a_ham_r": ap_a_ham_r,
            "a_hip_rom_flex_l": ap_a_hip_rom_flex_l, "a_hip_rom_flex_r": ap_a_hip_rom_flex_r,
            "a_hip_rom_abd_l": ap_a_hip_rom_abd_l, "a_hip_rom_abd_r": ap_a_hip_rom_abd_r,
            "a_hip_str_flex_l": ap_a_hip_str_flex_l, "a_hip_str_flex_r": ap_a_hip_str_flex_r,
            "a_hip_str_abd_l": ap_a_hip_str_abd_l, "a_hip_str_abd_r": ap_a_hip_str_abd_r,

            "current_chk": 1, "current_nd": r[4], "current_nt": r[5], "is_loaded": True,
            "op_left_chk": op_left_chk, "op_left_val": op_left_val,
            "op_right_chk": op_right_chk, "op_right_val": op_right_val,
            "op_bi_chk": op_bi_chk, "op_bi_val": op_bi_val,
            "op_notes": op_notes, "op_date": parsed_op_date,
            "daily_seq_no": r[12]
        }
        nav_to("📋 Prescription")


    if rows:
        cols = st.columns(3)
        for i, r in enumerate(rows):
            therapist_name = r[8] if r[8] else "Unassigned"
            seq_display = f"No. {r[12]}" if r[12] else "Unassigned"

            with cols[i % 3]:
                with st.expander(f"👤 {r[2]} ({r[1]})"):

                    info_blocks = ""
                    if r[9] and r[9] != "None recorded":
                        info_blocks += f"<div style='background-color: #e1f5fe; color: #01579b; padding: 6px 10px; border-radius: 4px; margin-bottom: 4px; margin-top: -5px; font-size: 15px;'><b>🔪 Op:</b> {r[9]} | <b>📅 Date:</b> {r[10]}</div>"

                    if r[11] and r[11].strip() and r[11] != "None":
                        if r[11] == "Class III":
                            info_blocks += f"<div style='background-color: #ffebee; color: #c62828; padding: 6px 10px; border-radius: 4px; margin-bottom: 4px; font-size: 15px;'><b>❤️ {r[11]}</b></div>"
                        else:
                            info_blocks += f"<div style='background-color: #e8f5e9; color: #2e7d32; padding: 6px 10px; border-radius: 4px; margin-bottom: 4px; font-size: 15px;'><b>❤️ {r[11]}</b></div>"

                    precautions = r[7]
                    if precautions and precautions != "None":
                        info_blocks += f"<div style='background-color: #fff3e0; color: #e65100; padding: 6px 10px; border-radius: 4px; margin-bottom: 8px; font-size: 15px;'><b>⚠️ Precautions:</b> {precautions}</div>"

                    if info_blocks:
                        st.markdown(info_blocks, unsafe_allow_html=True)

                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

                    try:
                        presc_list = json.loads(r[3])
                        for ex in presc_list:

                            if ex['id'] == 'st4':
                                dirs = [("rf", "右前"), ("ra", "右側"), ("re", "右後"),
                                        ("lf", "左前"), ("la", "左側"), ("le", "左後")]
                                has_dir = False

                                for d_id, d_label in dirs:
                                    if ex.get(f"{d_id}_chk"):
                                        has_dir = True
                                        is_done = ex.get(f'done_{d_id}', False)
                                        checkbox_key = f"done_{r[1]}_{ex['id']}_{d_id}"

                                        if st.session_state.get(checkbox_key) != is_done:
                                            st.session_state[checkbox_key] = is_done

                                        m = ex.get(f"{d_id}_mins", "10")
                                        g = "腳踩地" if ex.get(f"{d_id}_gnd") else ""

                                        band = ex.get(f"{d_id}_band_color", "紅橡根") if ex.get(
                                            f"{d_id}_band_chk") else ""

                                        parts = []
                                        if band: parts.append(band)
                                        if g: parts.append(g)
                                        parts.append(f'{m}"')

                                        label = f"企Hip: {d_label}, {', '.join(parts)}"

                                        st.checkbox(
                                            label,
                                            key=checkbox_key,
                                            on_change=toggle_exercise_db,
                                            args=(r[0], r[1], ex['id'], d_id)
                                        )
                                        st.markdown("<hr style='margin: 5px 0px; border: 0.5px solid #eee;'>",
                                                    unsafe_allow_html=True)

                                if not has_dir:
                                    is_done = ex.get('done', False)
                                    checkbox_key = f"done_{r[1]}_{ex['id']}"
                                    if st.session_state.get(checkbox_key) != is_done:
                                        st.session_state[checkbox_key] = is_done
                                    st.checkbox(
                                        format_ex_details(ex),
                                        key=checkbox_key,
                                        on_change=toggle_exercise_db,
                                        args=(r[0], r[1], ex['id'])
                                    )
                                    st.markdown("<hr style='margin: 5px 0px; border: 0.5px solid #eee;'>",
                                                unsafe_allow_html=True)

                            elif ex['id'] == 's11':
                                sling_parts = [
                                    ("sling_abd", "平訓＋左右", "sabd_tb", "sabd_color"),
                                    ("sling_flex", "側訓＋前後", "sflx_tb", "sflx_color")
                                ]
                                has_sling = False

                                for s_id, s_label, tb_key, color_key in sling_parts:
                                    if ex.get(s_id):
                                        has_sling = True
                                        is_done = ex.get(f'done_{s_id}', False)
                                        checkbox_key = f"done_{r[1]}_{ex['id']}_{s_id}"

                                        if st.session_state.get(checkbox_key) != is_done:
                                            st.session_state[checkbox_key] = is_done

                                        m = ex.get("mins", "10")
                                        tb = f" ({ex.get(color_key, '紅橡根')})" if ex.get(tb_key) else ""
                                        label = f"Sling: {s_label}{tb}, {m}\""

                                        st.checkbox(
                                            label,
                                            key=checkbox_key,
                                            on_change=toggle_exercise_db,
                                            args=(r[0], r[1], ex['id'], s_id)
                                        )
                                        st.markdown("<hr style='margin: 5px 0px; border: 0.5px solid #eee;'>",
                                                    unsafe_allow_html=True)

                                if not has_sling:
                                    is_done = ex.get('done', False)
                                    checkbox_key = f"done_{r[1]}_{ex['id']}"
                                    if st.session_state.get(checkbox_key) != is_done:
                                        st.session_state[checkbox_key] = is_done
                                    st.checkbox(
                                        format_ex_details(ex),
                                        key=checkbox_key,
                                        on_change=toggle_exercise_db,
                                        args=(r[0], r[1], ex['id'])
                                    )
                                    st.markdown("<hr style='margin: 5px 0px; border: 0.5px solid #eee;'>",
                                                unsafe_allow_html=True)

                            else:
                                is_done = ex.get('done', False)
                                checkbox_key = f"done_{r[1]}_{ex['id']}"

                                if st.session_state.get(checkbox_key) != is_done:
                                    st.session_state[checkbox_key] = is_done

                                st.checkbox(
                                    format_ex_details(ex),
                                    key=checkbox_key,
                                    on_change=toggle_exercise_db,
                                    args=(r[0], r[1], ex['id'])
                                )

                                if ex['id'] in QUEUEABLE_IDS:
                                    q_label = "✅ Already in Queue" if r[1] in queued_cases else "🚦 Join Queue"
                                    st.button(
                                        q_label,
                                        key=f"q_{r[1]}_{ex['id']}",
                                        disabled=(r[1] in queued_cases),
                                        use_container_width=True,
                                        on_click=add_to_queue,
                                        args=(r[1], r[2], ex['id'], QUEUEABLE_IDS[ex['id']], ex.get('mins', 15), r[12])
                                    )

                                st.markdown("<hr style='margin: 5px 0px; border: 0.5px solid #eee;'>",
                                            unsafe_allow_html=True)
                    except:
                        st.write("Could not decode exercises.")

                    st.markdown(
                        f"<div style='text-align: right; font-size: 15px; color: #555; margin-bottom: 10px;'>🩺 <b>Case Therapist:</b> {therapist_name}</div>",
                        unsafe_allow_html=True)

                    if st.session_state.current_therapist != "PCA":
                        b1, b2 = st.columns(2)
                        b1.button("✏️ Edit", key=f"edit_rx_{r[0]}", use_container_width=True,
                                  on_click=edit_active_prescription, args=(r,))
                        b2.button("🚪 Check Out", key=f"co_{r[0]}", use_container_width=True, type="primary",
                                  on_click=set_check_status, args=(r[1], 0))
                    else:
                        st.button("🚪 Check Out Patient", key=f"co_{r[0]}", use_container_width=True, type="primary",
                                  on_click=set_check_status, args=(r[1], 0))
    else:
        st.info("Gym is empty.")


# --- PAGE: QUEUE STATUS ---
elif page == "🚦 Queue Status":
    st.subheader("🚦 Equipment Real-time Queue List")

    conn = sqlite3.connect(DB_FILE, timeout=10)
    q_data = pd.read_sql_query("SELECT * FROM queues ORDER BY id ASC", conn)
    conn.close()

    cols = st.columns(3)
    for i, (item_id, item_label) in enumerate(QUEUEABLE_IDS.items()):
        with cols[i]:
            st.markdown(f"### ⚙️ {item_label}")
            item_q = q_data[q_data['item_id'] == item_id]

            active_and_waiting = item_q[item_q['status'].isin(['waiting', 'active'])]
            total_wait = active_and_waiting['prescribed_mins'].sum()
            st.markdown(f"Estimated Wait: <span class='wait-time'>{total_wait} mins</span>", unsafe_allow_html=True)
            st.divider()

            if item_q.empty:
                st.caption("No one in queue.")
            else:
                for _, p in item_q.iterrows():
                    is_active = p['status'] == 'active'
                    status_cls = "queue-active" if is_active else ""

                    decrypted_name = decrypt_data(p['p_name'])

                    st.markdown(f"""
                    <div class='queue-card {status_cls}'>
                        <b>{decrypted_name}</b> (Case: {p['case_no']})<br>
                        Time: {p['prescribed_mins']} mins | Joined: {p['joined_at']}<br>
                        Status: <b>{p['status'].upper()}</b>
                    </div>
                    """, unsafe_allow_html=True)

                    b1, b2 = st.columns(2)
                    if not is_active:
                        b1.button("▶️ Start", key=f"start_{p['id']}", on_click=update_queue_status,
                                  args=(p['id'], "active", p['case_no'], p['item_id']))

                    b2.button("✅ Finish", key=f"fin_{p['id']}", on_click=update_queue_status,
                              args=(p['id'], "finished"))


# --- PAGE 5: DASHBOARD ---
elif page == "📊 Dashboard":
    st.subheader("Gym Real-time Monitoring")
    conn = sqlite3.connect(DB_FILE, timeout=10)
    raw_active = conn.execute(
        "SELECT case_no, p_name, prescription_json, therapist FROM history WHERE is_checked_in = 1 AND id IN (SELECT MAX(id) FROM history GROUP BY case_no)").fetchall()
    conn.close()

    active = []
    for p in raw_active:
        active.append((p[0], decrypt_data(p[1]), decrypt_data(p[2]), p[3]))

    if active:
        h1, h2, h3, h4 = st.columns([1.5, 2.2, 2.2, 1.1])
        h1.markdown('<div class="dash-header">Patient Details</div>', unsafe_allow_html=True)
        h2.markdown('<div class="dash-header">✅ Completed</div>', unsafe_allow_html=True)
        h3.markdown('<div class="dash-header">⏳ Remaining</div>', unsafe_allow_html=True)
        h4.markdown('<div class="dash-header">Progress</div>', unsafe_allow_html=True)

        for p in active:
            c_no, name, presc_str, th_name = p[0], p[1], p[2], p[3]
            th_name = th_name if th_name else "Unassigned"
            t_color = get_therapist_color(th_name)

            try:
                presc = json.loads(presc_str)
                done = []
                todo = []

                for ex in presc:
                    if ex['id'] == 'st4':
                        dirs = [("rf", "右前"), ("ra", "右側"), ("re", "右後"),
                                ("lf", "左前"), ("la", "左側"), ("le", "左後")]
                        has_dir = False
                        for d_id, d_label in dirs:
                            if ex.get(f"{d_id}_chk"):
                                has_dir = True

                                m = ex.get(f"{d_id}_mins", "10")
                                g = "腳踩地" if ex.get(f"{d_id}_gnd") else ""

                                band = ex.get(f"{d_id}_band_color", "紅橡根") if ex.get(f"{d_id}_band_chk") else ""

                                parts = []
                                if band: parts.append(band)
                                if g: parts.append(g)
                                parts.append(f'{m}"')

                                ex_name = f"企Hip: {d_label}, {', '.join(parts)}"

                                if ex.get(f'done_{d_id}', False):
                                    done.append(ex_name)
                                else:
                                    todo.append(ex_name)
                        if not has_dir:
                            if ex.get('done', False):
                                done.append(ex['name'])
                            else:
                                todo.append(ex['name'])

                    elif ex['id'] == 's11':
                        sling_parts = [
                            ("sling_abd", "平訓＋左右", "sabd_tb", "sabd_color"),
                            ("sling_flex", "側訓＋前後", "sflx_tb", "sflx_color")
                        ]
                        has_sling = False
                        for s_id, s_label, tb_key, color_key in sling_parts:
                            if ex.get(s_id):
                                has_sling = True
                                m = ex.get("mins", "10")
                                tb = f" ({ex.get(color_key, '紅橡根')})" if ex.get(tb_key) else ""
                                ex_name = f"Sling: {s_label}{tb}, {m}\""

                                if ex.get(f'done_{s_id}', False):
                                    done.append(ex_name)
                                else:
                                    todo.append(ex_name)
                        if not has_sling:
                            if ex.get('done', False):
                                done.append(ex['name'])
                            else:
                                todo.append(ex['name'])

                    elif ex['id'] == 'f4':
                        height = str(ex.get('box_height', '4"')).replace('"', "''")
                        direction = "落" if ex.get('downstairs') else "上"
                        mins = str(ex.get('mins', '10'))
                        ex_name = f"{direction}{height}級 x {mins}\""
                        if ex.get('done', False):
                            done.append(ex_name)
                        else:
                            todo.append(ex_name)

                    elif ex['id'] == 'f11':
                        target = str(ex.get('target_sec', '')).strip()
                        mins = str(ex.get('mins', '10')).strip()
                        parts = []
                        if target: parts.append(f"{target}秒")
                        if mins: parts.append(f'{mins}"')
                        ex_name = f"{ex['name']}, {', '.join(parts)}" if parts else ex['name']
                        if ex.get('done', False):
                            done.append(ex_name)
                        else:
                            todo.append(ex_name)

                    elif ex['id'] == 'f8':
                        target_wt = str(ex.get('target_wt', '')).strip()
                        mins = str(ex.get('mins', '10')).strip()
                        parts = []
                        if target_wt: parts.append(f"{target_wt}lbs")
                        if mins: parts.append(f'{mins}"')
                        ex_name = f"{ex['name']}, {', '.join(parts)}" if parts else ex['name']
                        if ex.get('done', False):
                            done.append(ex_name)
                        else:
                            todo.append(ex_name)

                    else:
                        if ex.get('done', False):
                            done.append(format_ex_details(ex))
                        else:
                            todo.append(format_ex_details(ex))

                total_ex = len(done) + len(todo)
                pct = len(done) / total_ex if total_ex > 0 else 0
            except:
                done, todo, pct, presc = [], [], 0, []

            r1, r2, r3, r4 = st.columns([1.5, 2.2, 2.2, 1.1])
            with r1:
                st.markdown(
                    f"<div style='line-height: 1.6; padding-top: 10px;'>"
                    f"<span style='font-size: 20px; font-weight: 800; color: #1976d2;'>{name}</span><br>"
                    f"<span style='background-color: {t_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; vertical-align: middle;'>🩺 {th_name}</span><br>"
                    f"<span style='font-size: 12px; font-weight: 600; color: #757575;'>Case: {c_no}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with r2:
                html_done = "<br>".join([f"✔️ {x}" for x in done]) if done else "---"
                st.markdown(f'<div class="ex-list-condensed">{html_done}</div>', unsafe_allow_html=True)

            with r3:
                html_todo = "<br>".join([f"🔹 {x}" for x in todo]) if todo else "<b>Clear</b>"
                st.markdown(f'<div class="ex-list-condensed">{html_todo}</div>', unsafe_allow_html=True)

            with r4:
                st.progress(pct)
                st.markdown(
                    f"<div style='font-size:14px; font-weight: bold; color:#666; margin-top:-5px; text-align: right;'>{int(pct * 100)}%</div>",
                    unsafe_allow_html=True)

            st.markdown("<hr style='margin: 25px 0px; border: 1px solid #ddd;'>", unsafe_allow_html=True)
    else:
        st.info("No active cases currently being monitored on the gym floor.")

# --- PAGE 7: Patient History ---
elif page == "🗂️ Patient History":
    st.subheader("🗂️ Patient Historical Records")

    search_query = st.text_input("🔍 Search Database by Case Number",
                                 placeholder="Enter Patient Case No. (e.g., C12345)", value=ap["case_no"])
    st.divider()

    if not search_query:
        st.info("👆 Enter a Case Number above to pull up a patient's history.")
    else:
        conn = sqlite3.connect(DB_FILE, timeout=10)
        patient_info = conn.execute("SELECT p_name FROM history WHERE case_no = ? LIMIT 1", (search_query,)).fetchone()

        if patient_info:
            p_name = decrypt_data(patient_info[0])
            st.markdown(f"### History for: **{p_name}** ({search_query})")

            hist_records = conn.execute(
                "SELECT timestamp, assessment_text, prescription_json, therapist, op_details, op_date FROM history WHERE case_no = ? ORDER BY timestamp DESC",
                (search_query,)).fetchall()
            conn.close()

            if hist_records:
                filter_date = st.date_input("Filter by Specific Date (Optional)", value=None)
                count = 0
                for record in hist_records:
                    rec_date = record[0].split(" ")[0]
                    if filter_date and rec_date != filter_date.strftime('%Y-%m-%d'): continue

                    count += 1
                    th_name = record[3] if record[3] else "Unassigned"

                    safe_assess = decrypt_data(record[1])
                    safe_presc = decrypt_data(record[2])
                    safe_op_details = decrypt_data(record[4])

                    with st.expander(f"📅 Record Date: {record[0]} (🩺 Assessed by: {th_name})"):

                        if safe_op_details and safe_op_details != "None recorded":
                            st.info(f"**🔪 Operation:** {safe_op_details} *(Date: {record[5]})*")

                        st.markdown(
                            f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 4px; margin-bottom: 8px; font-size: 15px; line-height: 1.6;'>{format_assessment_display(safe_assess, safe_op_details)}</div>",
                            unsafe_allow_html=True)

                        st.markdown("**🏋️ Exercises:**")
                        try:
                            ex_list = json.loads(safe_presc)
                            if isinstance(ex_list, str): ex_list = json.loads(ex_list)
                            if ex_list:
                                for ex in ex_list: st.write(f"- {format_ex_details(ex)}")
                            else:
                                st.caption("No exercises recorded.")
                        except:
                            st.caption("No exercises recorded.")
                if count == 0: st.info("No records found for the selected date.")
            else:
                st.info("No historical records found for this patient.")
        else:
            conn.close()
            st.error("❌ Patient not found. Please check the Case Number and try again.")