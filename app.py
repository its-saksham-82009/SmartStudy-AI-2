import json
import random
import sqlite3
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="SmartStudy AI 2.0", page_icon="📚", layout="wide")

# Prototype database. On Streamlit Community Cloud, local files may reset after a rebuild/restart.
DB_PATH = Path("smartstudy_data.db")

QUESTIONS = [
    # SCIENCE: Physics
    {"id":"PHY_013","stream":"Science","subject":"Physics","topic":"Work, Energy and Power","difficulty":"Easy","q":"What is the SI unit of work?","options":["Newton","Joule","Watt","Pascal"],"answer":"Joule","explanation":"Work is measured in joules (J)."},
    {"id":"PHY_014","stream":"Science","subject":"Physics","topic":"Laws of Motion","difficulty":"Easy","q":"A body starts from rest and accelerates at 2 m/s² for 3 s. What is its final speed?","options":["3 m/s","5 m/s","6 m/s","9 m/s"],"answer":"6 m/s","explanation":"v = u + at = 0 + 2×3 = 6 m/s."},
    {"id":"PHY_015","stream":"Science","subject":"Physics","topic":"Units and Measurements","difficulty":"Easy","q":"Which of these is a scalar quantity?","options":["Displacement","Velocity","Speed","Force"],"answer":"Speed","explanation":"Speed has magnitude only, so it is scalar."},
    {"id":"PHY_016","stream":"Science","subject":"Physics","topic":"Kinematics","difficulty":"Easy","q":"The slope of a position-time graph represents:","options":["Acceleration","Velocity","Force","Momentum"],"answer":"Velocity","explanation":"The slope gives change in position per unit time."},
    {"id":"PHY_017","stream":"Science","subject":"Physics","topic":"Laws of Motion","difficulty":"Easy","q":"Which law explains why passengers jerk forward when a moving bus stops suddenly?","options":["Newton's first law","Newton's second law","Newton's third law","Law of gravitation"],"answer":"Newton's first law","explanation":"Inertia tends to keep the passenger moving forward."},
    {"id":"PHY_018","stream":"Science","subject":"Physics","topic":"Work, Energy and Power","difficulty":"Medium","q":"A 2 kg object moves at 3 m/s. Its kinetic energy is:","options":["3 J","6 J","9 J","18 J"],"answer":"9 J","explanation":"KE = ½mv² = ½×2×9 = 9 J."},
    {"id":"PHY_019","stream":"Science","subject":"Physics","topic":"Laws of Motion","difficulty":"Medium","q":"A net force of 12 N acts on a 3 kg body. Find its acceleration.","options":["2 m/s²","3 m/s²","4 m/s²","6 m/s²"],"answer":"4 m/s²","explanation":"a = F/m = 12/3 = 4 m/s²."},
    {"id":"PHY_020","stream":"Science","subject":"Physics","topic":"Circular Motion","difficulty":"Medium","q":"For a car moving on a level circular road, the centripetal force is usually provided by:","options":["Weight","Normal reaction","Friction","Air pressure"],"answer":"Friction","explanation":"Static friction acts towards the centre of the circular path."},
    {"id":"PHY_021","stream":"Science","subject":"Physics","topic":"Vectors","difficulty":"Medium","q":"Two perpendicular vectors have magnitudes 3 and 4. The magnitude of their resultant is:","options":["1","5","7","12"],"answer":"5","explanation":"R = √(3² + 4²) = 5."},
    {"id":"PHY_022","stream":"Science","subject":"Physics","topic":"Kinematics","difficulty":"Medium","q":"A car's velocity changes from 10 m/s to 20 m/s in 5 s. Its average acceleration is:","options":["2 m/s²","5 m/s²","6 m/s²","10 m/s²"],"answer":"2 m/s²","explanation":"a = (20 − 10)/5 = 2 m/s²."},
    {"id":"PHY_023","stream":"Science","subject":"Physics","topic":"Laws of Motion","difficulty":"Hard","q":"A 5 kg block on a frictionless surface is pulled by a 20 N horizontal force. Its acceleration is:","options":["2 m/s²","4 m/s²","5 m/s²","100 m/s²"],"answer":"4 m/s²","explanation":"Newton's second law: a = F/m = 20/5 = 4 m/s²."},
    {"id":"PHY_024","stream":"Science","subject":"Physics","topic":"Work, Energy and Power","difficulty":"Hard","q":"A 2 kg body falls from rest through 5 m. Taking g = 10 m/s² and neglecting air resistance, its speed just before impact is:","options":["5 m/s","10 m/s","15 m/s","20 m/s"],"answer":"10 m/s","explanation":"v² = 2gh = 2×10×5 = 100, so v = 10 m/s."},
    {"id":"PHY_025","stream":"Science","subject":"Physics","topic":"Circular Motion","difficulty":"Hard","q":"A body moves in a circle of radius 2 m at 4 m/s. Its centripetal acceleration is:","options":["2 m/s²","4 m/s²","8 m/s²","16 m/s²"],"answer":"8 m/s²","explanation":"a = v²/r = 16/2 = 8 m/s²."},
    {"id":"PHY_026","stream":"Science","subject":"Physics","topic":"Kinematics","difficulty":"Hard","q":"A ball is thrown vertically upward at 20 m/s. Take g = 10 m/s². Time to reach its highest point is:","options":["1 s","2 s","3 s","4 s"],"answer":"2 s","explanation":"At the highest point v = 0; t = u/g = 20/10 = 2 s."},
    {"id":"PHY_027","stream":"Science","subject":"Physics","topic":"Laws of Motion","difficulty":"Hard","q":"A 2 kg object experiences a net force of 10 N for 3 s. Its change in momentum is:","options":["10 kg m/s","15 kg m/s","30 kg m/s","60 kg m/s"],"answer":"30 kg m/s","explanation":"Change in momentum = impulse = FΔt = 10×3 = 30 kg m/s."},
    # SCIENCE: Chemistry
    {"id":"CHE_011","stream":"Science","subject":"Chemistry","topic":"Atomic Structure","difficulty":"Easy","q":"The maximum number of electrons in the first shell is:","options":["2","8","18","32"],"answer":"2","explanation":"The first shell has n = 1, so maximum electrons = 2n² = 2."},
    {"id":"CHE_012","stream":"Science","subject":"Chemistry","topic":"Chemical Bonding","difficulty":"Easy","q":"Which bond is formed by sharing electron pairs?","options":["Ionic","Covalent","Metallic","Hydrogen"],"answer":"Covalent","explanation":"Covalent bonds form when atoms share electron pairs."},
    {"id":"CHE_013","stream":"Science","subject":"Chemistry","topic":"Periodic Table","difficulty":"Easy","q":"Elements in the same group generally have the same number of:","options":["Neutrons","Electron shells","Valence electrons","Isotopes"],"answer":"Valence electrons","explanation":"For main-group elements, group number relates to valence-electron count."},
    {"id":"CHE_014","stream":"Science","subject":"Chemistry","topic":"Mole Concept","difficulty":"Easy","q":"The SI unit for amount of substance is:","options":["Gram","Mole","Litre","Kilogram"],"answer":"Mole","explanation":"The mole is the SI unit for amount of substance."},
    {"id":"CHE_015","stream":"Science","subject":"Chemistry","topic":"Atomic Structure","difficulty":"Easy","q":"Which subatomic particle has a negative charge?","options":["Proton","Neutron","Electron","Nucleus"],"answer":"Electron","explanation":"An electron carries a negative elementary charge."},
    {"id":"CHE_016","stream":"Science","subject":"Chemistry","topic":"Mole Concept","difficulty":"Medium","q":"How many moles are present in 18 g of water? (Molar mass = 18 g/mol)","options":["0.5 mol","1 mol","2 mol","18 mol"],"answer":"1 mol","explanation":"n = mass/molar mass = 18/18 = 1 mol."},
    {"id":"CHE_017","stream":"Science","subject":"Chemistry","topic":"Chemical Bonding","difficulty":"Medium","q":"The shape of a methane (CH₄) molecule is:","options":["Linear","Trigonal planar","Tetrahedral","Bent"],"answer":"Tetrahedral","explanation":"Four bonding pairs around carbon arrange tetrahedrally."},
    {"id":"CHE_018","stream":"Science","subject":"Chemistry","topic":"Atomic Structure","difficulty":"Medium","q":"The number of orbitals in a p subshell is:","options":["1","2","3","5"],"answer":"3","explanation":"A p subshell has three orbitals: px, py and pz."},
    {"id":"CHE_019","stream":"Science","subject":"Chemistry","topic":"Periodic Table","difficulty":"Medium","q":"Across a period from left to right, atomic radius generally:","options":["Increases","Decreases","Stays exactly constant","First doubles"],"answer":"Decreases","explanation":"Effective nuclear charge generally increases across a period."},
    {"id":"CHE_020","stream":"Science","subject":"Chemistry","topic":"Chemical Bonding","difficulty":"Medium","q":"Which molecule has a linear shape?","options":["H₂O","NH₃","CO₂","CH₄"],"answer":"CO₂","explanation":"CO₂ has two electron domains around carbon and is linear."},
    # SCIENCE: Maths
    {"id":"MAT_011","stream":"Science","subject":"Maths","topic":"Trigonometry","difficulty":"Easy","q":"What is sin 30°?","options":["0","1/2","√3/2","1"],"answer":"1/2","explanation":"sin 30° = 1/2."},
    {"id":"MAT_012","stream":"Science","subject":"Maths","topic":"Permutations","difficulty":"Easy","q":"What is 3!?","options":["3","6","9","12"],"answer":"6","explanation":"3! = 3×2×1 = 6."},
    {"id":"MAT_013","stream":"Science","subject":"Maths","topic":"Quadratic Equations","difficulty":"Medium","q":"The roots of x² − 5x + 6 = 0 are:","options":["1 and 6","2 and 3","−2 and −3","0 and 5"],"answer":"2 and 3","explanation":"x² − 5x + 6 = (x − 2)(x − 3)."},
    {"id":"MAT_014","stream":"Science","subject":"Maths","topic":"Permutations","difficulty":"Medium","q":"How many ways can 3 different books be arranged in a row?","options":["3","6","9","27"],"answer":"6","explanation":"The number of arrangements is 3! = 6."},
    {"id":"MAT_015","stream":"Science","subject":"Maths","topic":"Trigonometry","difficulty":"Hard","q":"If sin θ = 3/5 and θ is acute, then cos θ equals:","options":["2/5","3/4","4/5","5/4"],"answer":"4/5","explanation":"cos θ = √(1 − sin²θ) = √(16/25) = 4/5."},
    {"id":"MAT_016","stream":"Science","subject":"Maths","topic":"Trigonometry","difficulty":"Easy","q":"What is cos 60°?","options":["0","1/2","√3/2","1"],"answer":"1/2","explanation":"cos 60° = 1/2."},
    {"id":"MAT_017","stream":"Science","subject":"Maths","topic":"Quadratic Equations","difficulty":"Easy","q":"Which of these is a root of x² − 9 = 0?","options":["1","2","3","4"],"answer":"3","explanation":"x² = 9, so x = 3 or x = −3; 3 is one root."},
    {"id":"MAT_018","stream":"Science","subject":"Maths","topic":"Permutations","difficulty":"Medium","q":"How many distinct arrangements can be made using all letters of the word CAT?","options":["3","6","9","12"],"answer":"6","explanation":"All three letters are different, so the number of arrangements is 3! = 6."},
    {"id":"MAT_019","stream":"Science","subject":"Maths","topic":"Sequences and Series","difficulty":"Medium","q":"What is the 5th term of the arithmetic sequence 2, 5, 8, 11, ...?","options":["12","13","14","15"],"answer":"14","explanation":"The common difference is 3, so the 5th term is 2 + 4×3 = 14."},
    {"id":"MAT_020","stream":"Science","subject":"Maths","topic":"Trigonometry","difficulty":"Hard","q":"If tan θ = 3/4 and θ is acute, what is sec θ?","options":["4/5","5/4","3/5","5/3"],"answer":"5/4","explanation":"Using a 3–4–5 triangle, sec θ = hypotenuse/adjacent = 5/4."},
    # BIOLOGY
    {"id":"BIO_001","stream":"Science","subject":"Biology","topic":"Cell Biology","difficulty":"Easy","q":"Which cell organelle is known as the powerhouse of the cell?","options":["Ribosome","Mitochondrion","Golgi apparatus","Lysosome"],"answer":"Mitochondrion","explanation":"Mitochondria produce much of the cell's ATP through cellular respiration."},
    {"id":"BIO_002","stream":"Science","subject":"Biology","topic":"Cell Biology","difficulty":"Medium","q":"Which structure controls the movement of substances into and out of a cell?","options":["Cell membrane","Nucleolus","Chromosome","Vacuole only"],"answer":"Cell membrane","explanation":"The plasma membrane regulates movement between the cell and its surroundings."},
    # COMMERCE: Accountancy
    {"id":"ACC_001","stream":"Commerce","subject":"Accountancy","topic":"Accounting Equation","difficulty":"Easy","q":"The basic accounting equation is:","options":["Assets = Liabilities + Capital","Assets = Income − Expenses","Capital = Assets + Liabilities","Liabilities = Assets + Capital"],"answer":"Assets = Liabilities + Capital","explanation":"The accounting equation expresses assets as claims by liabilities and owner's equity/capital."},
    {"id":"ACC_002","stream":"Commerce","subject":"Accountancy","topic":"Journal Entries","difficulty":"Easy","q":"Goods purchased for cash are generally recorded as:","options":["Debit Purchases, Credit Cash","Debit Cash, Credit Purchases","Debit Sales, Credit Cash","Debit Capital, Credit Purchases"],"answer":"Debit Purchases, Credit Cash","explanation":"Purchases are debited and cash is credited in a basic cash purchase entry."},
    {"id":"ACC_003","stream":"Commerce","subject":"Accountancy","topic":"Accounting Equation","difficulty":"Medium","q":"If assets are ₹80,000 and liabilities are ₹30,000, capital is:","options":["₹30,000","₹50,000","₹80,000","₹1,10,000"],"answer":"₹50,000","explanation":"Capital = Assets − Liabilities = ₹80,000 − ₹30,000 = ₹50,000."},
    # COMMERCE: Business Studies
    {"id":"BST_001","stream":"Commerce","subject":"Business Studies","topic":"Business Objectives","difficulty":"Easy","q":"Which is a common economic objective of business?","options":["Earning profit","Avoiding all customers","Eliminating production","Ignoring costs"],"answer":"Earning profit","explanation":"Profit supports continuity, growth and reward for business risk."},
    {"id":"BST_002","stream":"Commerce","subject":"Business Studies","topic":"Forms of Business","difficulty":"Medium","q":"Which form of business is owned and controlled by one person?","options":["Sole proprietorship","Partnership","Company","Co-operative society"],"answer":"Sole proprietorship","explanation":"A sole proprietorship is owned and managed by one proprietor."},
    # COMMERCE: Economics
    {"id":"ECO_001","stream":"Commerce","subject":"Economics","topic":"Basic Concepts","difficulty":"Easy","q":"Economics mainly studies how people allocate:","options":["Unlimited resources to unlimited wants","Scarce resources among competing wants","Only money among banks","Only goods among shops"],"answer":"Scarce resources among competing wants","explanation":"Economics studies choices under scarcity."},
    {"id":"ECO_002","stream":"Commerce","subject":"Economics","topic":"Demand","difficulty":"Medium","q":"Other things remaining equal, when the price of a normal good falls, quantity demanded generally:","options":["Rises","Falls","Becomes zero","Never changes"],"answer":"Rises","explanation":"The law of demand states an inverse relationship between price and quantity demanded, other things equal."},
    # HUMANITIES
    {"id":"HIS_001","stream":"Humanities","subject":"History","topic":"Historical Sources","difficulty":"Easy","q":"Which source is most directly useful for studying an ancient ruler's official orders?","options":["Royal inscription","Modern advertisement","Weather forecast","Sports report"],"answer":"Royal inscription","explanation":"Inscriptions can preserve official orders and public records from the period."},
    {"id":"GEO_001","stream":"Humanities","subject":"Geography","topic":"Maps and Scale","difficulty":"Easy","q":"A map scale of 1:100,000 means 1 cm on the map represents:","options":["100 m on the ground","1 km on the ground","10 km on the ground","100 km on the ground"],"answer":"1 km on the ground","explanation":"100,000 cm = 1 km."},
    {"id":"POL_001","stream":"Humanities","subject":"Political Science","topic":"Constitution","difficulty":"Easy","q":"A constitution primarily sets out a country's:","options":["Basic rules and institutions of government","Daily weather","Private shopping lists","Sports results"],"answer":"Basic rules and institutions of government","explanation":"A constitution defines core principles, powers and institutions of the state."},
]

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, pin_hash TEXT NOT NULL, stream TEXT NOT NULL,
        class_level TEXT NOT NULL, created_at TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, taken_at TEXT NOT NULL,
        stream TEXT NOT NULL, subject TEXT NOT NULL, score INTEGER NOT NULL,
        correct INTEGER NOT NULL, total INTEGER NOT NULL, topics_json TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, created_at TEXT NOT NULL,
        subject TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL)""")
    conn.commit()
    return conn

def init_db():
    conn = connect()
    conn.close()

def get_user(username):
    conn = connect()
    row = conn.execute("SELECT username, stream, class_level FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row

def update_user_stream(username, stream):
    conn = connect()
    conn.execute("UPDATE users SET stream=? WHERE username=?", (stream, username))
    conn.commit()
    conn.close()

def create_user(username, pin, stream, class_level):
    import hashlib
    pin_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
    conn = connect()
    try:
        conn.execute("INSERT INTO users(username,pin_hash,stream,class_level,created_at) VALUES(?,?,?,?,?)",
                     (username, pin_hash, stream, class_level, datetime.now().isoformat(timespec="minutes")))
        conn.commit()
        return True, "Profile created."
    except sqlite3.IntegrityError:
        return False, "That username already exists. Sign in instead."
    finally:
        conn.close()

def verify_user(username, pin):
    import hashlib
    pin_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
    conn = connect()
    row = conn.execute("SELECT username, stream, class_level FROM users WHERE username=? AND pin_hash=?",
                       (username, pin_hash)).fetchone()
    conn.close()
    return row

def save_attempt(username, stream, subject, score, correct, total, topics):
    conn = connect()
    conn.execute("INSERT INTO attempts(username,taken_at,stream,subject,score,correct,total,topics_json) VALUES(?,?,?,?,?,?,?,?)",
                 (username, datetime.now().isoformat(timespec="minutes"), stream, subject, score, correct, total, json.dumps(topics)))
    conn.commit()
    conn.close()

def get_attempts(username):
    conn = connect()
    rows = conn.execute("SELECT taken_at,stream,subject,score,correct,total,topics_json FROM attempts WHERE username=? ORDER BY id DESC",
                        (username,)).fetchall()
    conn.close()
    return [{"Date":r[0], "Stream":r[1], "Subject":r[2], "Score (%)":r[3], "Correct":f"{r[4]}/{r[5]}", "topics":json.loads(r[6])} for r in rows]

def save_note(username, subject, title, content):
    conn = connect()
    conn.execute("INSERT INTO notes(username,created_at,subject,title,content) VALUES(?,?,?,?,?)",
                 (username, datetime.now().isoformat(timespec="minutes"), subject, title, content))
    conn.commit()
    conn.close()

def get_notes(username):
    conn = connect()
    rows = conn.execute("SELECT id,created_at,subject,title,content FROM notes WHERE username=? ORDER BY id DESC", (username,)).fetchall()
    conn.close()
    return rows

def delete_note(note_id, username):
    conn = connect()
    conn.execute("DELETE FROM notes WHERE id=? AND username=?", (note_id, username))
    conn.commit()
    conn.close()

def topics_summary(attempts):
    totals = {}
    for a in attempts:
        for topic, stats in a["topics"].items():
            t = totals.setdefault(topic, {"correct":0,"total":0})
            t["correct"] += stats["correct"]
            t["total"] += stats["total"]
    return {topic: round(100*v["correct"]/v["total"]) for topic,v in totals.items() if v["total"]}

def make_plan(topic_scores, minutes):
    if not topic_scores:
        return pd.DataFrame([{"Topic":"Start with a quiz","Latest status":"No quiz data yet","Priority":"Medium","Minutes":minutes}])
    rows=[]
    for topic,pct in topic_scores.items():
        priority = "High" if pct < 50 else ("Medium" if pct < 80 else "Low")
        weight = {"High":3,"Medium":2,"Low":1}[priority]
        rows.append({"Topic":topic,"Latest status":f"{pct}% accuracy","Priority":priority,"_weight":weight})
    total=sum(r["_weight"] for r in rows)
    for r in rows: r["Minutes"] = minutes*r["_weight"]//total
    for i in range(minutes-sum(r["Minutes"] for r in rows)): rows[i%len(rows)]["Minutes"] += 1
    rows.sort(key=lambda r: ({"High":0,"Medium":1,"Low":2}[r["Priority"]], int(r["Latest status"].split("%")[0])))
    return pd.DataFrame([{k:v for k,v in r.items() if k!="_weight"} for r in rows])

init_db()

if "signed_in_user" not in st.session_state:
    st.session_state.signed_in_user = None
if "active_quiz" not in st.session_state:
    st.session_state.active_quiz = []
if "submitted_result" not in st.session_state:
    st.session_state.submitted_result = None

st.title("📚 SmartStudy AI 2.0")
st.caption("Personalized study support • Quiz • Analytics • Notes • Planner")

with st.sidebar:
    st.markdown("### 👤 Student profile")
    if st.session_state.signed_in_user is None:
        login_tab, signup_tab = st.tabs(["Sign in", "Create profile"])
        with login_tab:
            login_name = st.text_input("Username", key="login_name").strip().lower()
            login_pin = st.text_input("PIN (4+ digits)", type="password", key="login_pin")
            if st.button("Sign in", use_container_width=True):
                user = verify_user(login_name, login_pin)
                if user:
                    st.session_state.signed_in_user = user[0]
                    st.session_state.active_quiz = []
                    st.rerun()
                else:
                    st.error("Username/PIN not found. Create a profile first.")
        with signup_tab:
            new_name = st.text_input("Choose username", key="new_name").strip().lower()
            new_pin = st.text_input("Choose PIN (4+ digits)", type="password", key="new_pin")
            new_stream = st.selectbox("Stream", ["Science", "Commerce", "Humanities"], key="new_stream")
            new_class = st.selectbox("Class", ["9", "10", "11", "12"], index=2, key="new_class")
            if st.button("Create profile", use_container_width=True):
                if len(new_name) < 3 or not new_name.replace("_","").isalnum():
                    st.error("Use at least 3 letters/numbers/underscores for username.")
                elif len(new_pin) < 4:
                    st.error("PIN must be at least 4 characters.")
                else:
                    ok, msg = create_user(new_name, new_pin, new_stream, new_class)
                    if ok:
                        st.success(msg + " Now sign in.")
                    else:
                        st.error(msg)
    else:
        user = get_user(st.session_state.signed_in_user)
        if user:
            st.success(f"Signed in as **{user[0]}**")
            st.caption(f"Class {user[2]} • {user[1]}")
            chosen_stream = st.selectbox(
                "Active stream",
                ["Science", "Commerce", "Humanities"],
                index=["Science", "Commerce", "Humanities"].index(user[1]),
                key="active_stream_selector",
                help="Change this to explore the question bank for another stream."
            )
            if chosen_stream != user[1]:
                update_user_stream(user[0], chosen_stream)
                st.session_state.active_quiz = []
                st.session_state.submitted_result = None
                st.session_state.pop("last_plan", None)
                st.rerun()
        if st.button("Sign out", use_container_width=True):
            st.session_state.signed_in_user = None
            st.session_state.active_quiz = []
            st.session_state.submitted_result = None
            st.rerun()

if not st.session_state.signed_in_user:
    st.info("Create a student profile or sign in from the sidebar to use your personal quiz history, planner, and notes.")
    st.markdown("### What you can do")
    st.markdown("- Take randomized quizzes with explanations\n- Review progress analytics\n- Generate a topic-based revision plan\n- Save notes for revision\n- Choose Science, Commerce, or Humanities")
    st.warning("Prototype note: local SQLite storage is used. Streamlit Cloud's local disk is not guaranteed permanent; for durable online accounts, connect a managed database before using this with real student data.")
    st.stop()

username = st.session_state.signed_in_user
user = get_user(username)
profile_stream = user[1]
class_level = user[2]
all_attempts = get_attempts(username)
topic_scores = topics_summary(all_attempts)

tab_dashboard, tab_quiz, tab_planner, tab_notes, tab_about = st.tabs(
    ["🏠 Dashboard", "📝 Smart Quiz", "📅 Study Planner", "🗒️ Notes", "ℹ️ About"]
)

with tab_dashboard:
    st.markdown(f"## Welcome back, {username.title()} 👋")
    c1,c2,c3 = st.columns(3)
    c1.metric("Quizzes completed", len(all_attempts))
    avg = round(sum(a["Score (%)"] for a in all_attempts)/len(all_attempts)) if all_attempts else 0
    c2.metric("Average score", f"{avg}%")
    c3.metric("Topics tracked", len(topic_scores))
    if all_attempts:
        hist_df = pd.DataFrame([{k:a[k] for k in ["Date","Stream","Subject","Score (%)","Correct"]} for a in all_attempts])
        st.markdown("### Recent quiz history")
        st.dataframe(hist_df.head(10), use_container_width=True, hide_index=True)
        chart_df = hist_df.iloc[::-1].reset_index(drop=True)
        st.markdown("### Score trend")
        st.line_chart(chart_df["Score (%)"])
        if topic_scores:
            topic_df = pd.DataFrame([{"Topic":t,"Accuracy (%)":v} for t,v in sorted(topic_scores.items(), key=lambda x:x[1])])
            st.markdown("### Topics to revise first")
            st.dataframe(topic_df, use_container_width=True, hide_index=True)
            st.bar_chart(topic_df.set_index("Topic"))
    else:
        st.info("Your dashboard will show scores and weak topics after your first quiz.")

with tab_quiz:
    st.markdown("## Practice quiz")
    subjects = sorted({q["subject"] for q in QUESTIONS if q["stream"] == profile_stream})
    subject_choices = ["All subjects"] + subjects
    c1,c2,c3 = st.columns(3)
    with c1: subject_filter = st.selectbox("Subject", subject_choices, key=f"quiz_subject_{profile_stream}")
    with c2: difficulty_filter = st.selectbox("Difficulty", ["All","Easy","Medium","Hard"], key="quiz_difficulty")
    with c3: question_count = st.selectbox("Questions", [5,10], index=1, key="quiz_count")
    if st.button("🎲 Generate quiz", type="primary", use_container_width=True):
        pool = [q for q in QUESTIONS if q["stream"] == profile_stream and
                (subject_filter == "All subjects" or q["subject"] == subject_filter) and
                (difficulty_filter == "All" or q["difficulty"] == difficulty_filter)]
        if not pool:
            st.warning("No questions match these filters yet. Try All subjects or another difficulty.")
            st.session_state.active_quiz = []
        else:
            count = min(question_count, len(pool))
            st.session_state.active_quiz = random.sample(pool, count)
            st.session_state.submitted_result = None
            st.rerun()
    if st.session_state.active_quiz:
        quiz = st.session_state.active_quiz
        with st.form("active_quiz_form"):
            answers={}
            for i,q in enumerate(quiz,1):
                st.markdown(f"**Q{i}. {q['subject']} • {q['difficulty']}**")
                st.write(q["q"])
                answers[q["id"]] = st.radio(f"Answer {i}", q["options"], index=None, key=f"ans_{q['id']}", label_visibility="collapsed")
                st.caption(f"Topic: {q['topic']}")
                st.divider()
            submitted = st.form_submit_button("Submit quiz", use_container_width=True)
        if submitted:
            correct_count=0
            topic_stats={}
            answer_rows=[]
            for q in quiz:
                selected=answers[q["id"]]
                is_correct=selected==q["answer"]
                correct_count += int(is_correct)
                t=topic_stats.setdefault(q["topic"], {"correct":0,"total":0})
                t["correct"] += int(is_correct); t["total"] += 1
                answer_rows.append({"Question":q["q"],"Your answer":selected or "Not answered",
                                    "Correct answer":q["answer"],"Result":"Correct" if is_correct else "Review",
                                    "Explanation":q["explanation"],"Topic":q["topic"]})
            score=round(100*correct_count/len(quiz))
            save_attempt(username, profile_stream, subject_filter, score, correct_count, len(quiz), topic_stats)
            st.session_state.submitted_result={"score":score,"correct":correct_count,"total":len(quiz),"rows":answer_rows}
            st.success(f"Score: {correct_count}/{len(quiz)} ({score}%)")
            st.dataframe(pd.DataFrame(answer_rows), use_container_width=True, hide_index=True)
            st.markdown("### Revision priorities from this attempt")
            st.dataframe(make_plan({t:round(100*s['correct']/s['total']) for t,s in topic_stats.items()}, 90),
                         use_container_width=True, hide_index=True)
            st.caption("Priority uses transparent rules: below 50% = High, 50–79% = Medium, 80%+ = Low.")
    else:
        st.caption("Choose filters and generate a quiz. The quiz length adapts to the number of available questions.")

with tab_planner:
    st.markdown("## Personalized revision planner")
    c1,c2=st.columns(2)
    with c1: minutes=st.slider("Available study time (minutes)",30,360,120,step=15)
    with c2: day=st.date_input("Plan date", value=date.today())
    default_topics = [t for t,v in sorted(topic_scores.items(), key=lambda x:x[1]) if v < 80]
    default_text = "\n".join(default_topics[:8])
    weak_text=st.text_area("Weak topics (one per line)", value=default_text, placeholder="Laws of Motion\nChemical Bonding\nDemand")
    if st.button("Build my revision plan", type="primary", use_container_width=True):
        topics=[x.strip() for x in weak_text.splitlines() if x.strip()]
        if not topics:
            topics=[f"{s} revision" for s in sorted({q['subject'] for q in QUESTIONS if q['stream']==profile_stream})[:3]]
        scores={t:topic_scores.get(t,45) for t in topics}
        plan=make_plan(scores,minutes)
        st.session_state["last_plan"] = {"date":str(day),"minutes":minutes,"rows":plan.to_dict(orient="records")}
        st.success(f"Plan created for {day.strftime('%d %b %Y')}.")
        st.dataframe(plan, use_container_width=True, hide_index=True)
        st.markdown("### Suggested routine")
        st.write("Start with the highest-priority topic, take a short break between blocks, and finish by recalling key points without looking at notes.")
    elif st.session_state.get("last_plan"):
        saved=st.session_state["last_plan"]
        st.caption(f"Last plan in this session: {saved['date']} • {saved['minutes']} minutes")

with tab_notes:
    st.markdown("## Notes & revision cards")
    with st.form("note_form", clear_on_submit=True):
        n_subject=st.selectbox("Subject", sorted({q["subject"] for q in QUESTIONS if q["stream"]==profile_stream}), key=f"note_subject_{profile_stream}")
        n_title=st.text_input("Note title", placeholder="e.g. Newton's laws — key points")
        n_content=st.text_area("Your notes", placeholder="Write definitions, formulas, examples or quick reminders...")
        note_submit=st.form_submit_button("Save note", use_container_width=True)
    if note_submit:
        if n_title.strip() and n_content.strip():
            save_note(username,n_subject,n_title.strip(),n_content.strip())
            st.success("Note saved to this prototype's database.")
            st.rerun()
        else:
            st.warning("Add both a title and note content.")
    saved_notes=get_notes(username)
    st.markdown(f"### Saved notes ({len(saved_notes)})")
    if saved_notes:
        for note_id, created, subj, title, content in saved_notes:
            with st.expander(f"{subj} • {title} • {created[:10]}"):
                st.write(content)
                if st.button("Delete note", key=f"delete_note_{note_id}"):
                    delete_note(note_id,username)
                    st.rerun()
    else:
        st.info("Your saved notes will appear here.")

with tab_about:
    st.markdown("""
    ## About SmartStudy AI 2.0
    **Problem statement:** Students may struggle to decide what to revise first and how to divide available study time.

    **Prototype workflow**
    1. Student creates a local prototype profile and chooses a stream/class.
    2. The question bank supplies practice questions.
    3. Quiz answers are scored and grouped by topic.
    4. Transparent rules classify topic priority: below 50% High, 50–79% Medium, 80%+ Low.
    5. The planner allocates more time to higher-priority topics.
    6. Quiz attempts and notes are stored in a local SQLite database.

    **Current streams:** Science (PCM-style Physics/Chemistry/Maths plus introductory Biology items), Commerce, Humanities.
    **Current limitations:** This is an educational prototype. Priority rules are not a production-trained AI model. The sample question bank is small. Local SQLite storage on free hosted instances may not survive restarts/rebuilds. The profile/PIN is for prototype separation, not high-security authentication. Do not store sensitive personal information.
    """)
    st.metric("Questions in this prototype", len(QUESTIONS))
    st.write(pd.DataFrame([{"Stream":s,"Questions":sum(q["stream"]==s for q in QUESTIONS)} for s in ["Science","Commerce","Humanities"]]))

st.sidebar.caption("SmartStudy AI 2.0 • Student prototype")
