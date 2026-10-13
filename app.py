import json
import random
import sqlite3
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="SmartStudy AI | Learn Smarter", page_icon="📚", layout="wide")

# Premium, responsive visual system
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --brand:#5145CD; --brand2:#756CF0; --ink:#172033; --muted:#68738A; --line:#E7EAF2; --surface:#FFFFFF; --soft:#F5F6FC; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.brand-eyebrow { display:inline-block; color:#5145CD; background:#ECEBFF; border:1px solid #DFDDFF; border-radius:999px; padding:5px 11px; font-size:.72rem; font-weight:800; letter-spacing:.12em; margin-bottom:8px; }
.stApp { background:linear-gradient(180deg,#F8F9FF 0%,#F5F7FC 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(248,249,255,.92); }
.block-container { max-width:1320px; padding-top:2rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; color:#172033; }
h1 { font-size:2.35rem !important; font-weight:800 !important; }
h2 { font-size:1.55rem !important; font-weight:800 !important; }
h3 { font-size:1.12rem !important; font-weight:700 !important; }
p, label, .stCaption { color:#536078; }
[data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid #E7EAF2; }
[data-testid="stSidebar"] > div { padding-top:1.5rem; }
[data-testid="stMetric"] { background:#FFFFFF; border:1px solid var(--line); border-radius:18px; padding:20px 22px; box-shadow:0 5px 20px rgba(33,42,80,.045); }
[data-testid="stMetricLabel"] { color:#68738A !important; font-weight:600; }
[data-testid="stMetricValue"] { color:#22294A !important; font-family:'Manrope',sans-serif; font-weight:800; }
.stButton > button, [data-testid="stFormSubmitButton"] button { border-radius:12px; min-height:2.8rem; border:1px solid #DADDF0; font-weight:700; transition:all .15s ease; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] { background:linear-gradient(135deg,#5145CD,#756CF0); color:white; border:0; box-shadow:0 6px 15px rgba(81,69,205,.18); }
.stButton > button:hover { border-color:#756CF0; transform:translateY(-1px); }
[data-testid="stTabs"] [role="tablist"] { gap:8px; border-bottom:1px solid #E2E6F0; }
[data-testid="stTabs"] button[role="tab"] { border-radius:11px 11px 0 0; padding:12px 15px; font-weight:700; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#5145CD; border-bottom:3px solid #5145CD; }
/* High-contrast form controls: force dark text on white controls */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  border-radius:11px !important;
  border-color:#DDE2EE !important;
  background:#FFFFFF !important;
  color:#172033 !important;
  -webkit-text-fill-color:#172033 !important;
  caret-color:#5145CD !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stDateInput"] input::placeholder {
  color:#68738A !important;
  -webkit-text-fill-color:#68738A !important;
  opacity:1 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] *,
[role="listbox"] [role="option"],
[role="option"] {
  color:#172033 !important;
}
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] { background:#FFFFFF !important; }
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label { color:#172033 !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border:1px solid #E5E8F0; border-radius:13px; overflow:hidden; }
[data-testid="stAlert"] { border-radius:13px; }
hr { border-color:#E6E9F2; }
@media (max-width: 700px) { .block-container { padding:1rem .8rem 2rem; } h1 {font-size:1.75rem !important;} [data-testid="stMetric"] {padding:14px;} [data-testid="stTabs"] [role="tablist"] {gap:0; overflow-x:auto;} [data-testid="stTabs"] button[role="tab"] {padding:9px 10px; font-size:.85rem;} }
</style>
""", unsafe_allow_html=True)

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
    # Expanded Science question bank: PCM
    {"id":"PHY_028","stream":"Science","subject":"Physics","topic":"Units and Measurements","difficulty":"Easy","q":"The dimensional formula of velocity is:","options":["[LT⁻¹]","[LT⁻²]","[MLT⁻¹]","[ML²T⁻²]"],"answer":"[LT⁻¹]","explanation":"Velocity is displacement divided by time, so its dimension is L T⁻¹."},
    {"id":"PHY_029","stream":"Science","subject":"Physics","topic":"Vectors","difficulty":"Easy","q":"Which quantity is a vector?","options":["Mass","Time","Acceleration","Temperature"],"answer":"Acceleration","explanation":"Acceleration has both magnitude and direction."},
    {"id":"PHY_030","stream":"Science","subject":"Physics","topic":"Kinematics","difficulty":"Medium","q":"A body moving at 10 m/s accelerates at 2 m/s² for 4 s. Its final speed is:","options":["12 m/s","14 m/s","18 m/s","20 m/s"],"answer":"18 m/s","explanation":"v = u + at = 10 + 2×4 = 18 m/s."},
    {"id":"PHY_031","stream":"Science","subject":"Physics","topic":"Work, Energy and Power","difficulty":"Easy","q":"Power is the rate of doing:","options":["Force","Work","Momentum","Displacement"],"answer":"Work","explanation":"Power is work done per unit time."},
    {"id":"PHY_032","stream":"Science","subject":"Physics","topic":"Circular Motion","difficulty":"Medium","q":"Centripetal acceleration is directed:","options":["Tangentially forward","Away from the centre","Towards the centre","Vertically upward always"],"answer":"Towards the centre","explanation":"Centripetal acceleration points radially inward."},
    {"id":"PHY_033","stream":"Science","subject":"Physics","topic":"Laws of Motion","difficulty":"Medium","q":"The SI unit of impulse is:","options":["N s","N/s","J/s","kg/m"],"answer":"N s","explanation":"Impulse equals change in momentum and has unit newton-second."},
    {"id":"PHY_034","stream":"Science","subject":"Physics","topic":"Work, Energy and Power","difficulty":"Hard","q":"A 2 kg body moving at 5 m/s has kinetic energy:","options":["10 J","20 J","25 J","50 J"],"answer":"25 J","explanation":"KE = ½mv² = ½×2×25 = 25 J."},
    {"id":"PHY_035","stream":"Science","subject":"Physics","topic":"Units and Measurements","difficulty":"Medium","q":"How many significant figures are in 0.00450?","options":["2","3","4","5"],"answer":"3","explanation":"Leading zeros are not significant; 4, 5 and the trailing decimal zero count."},
    {"id":"CHE_021","stream":"Science","subject":"Chemistry","topic":"Mole Concept","difficulty":"Easy","q":"Avogadro's constant is approximately:","options":["6.022 × 10²³ mol⁻¹","3.14 × 10⁸ mol⁻¹","9.8 mol⁻¹","1.6 × 10⁻¹⁹ mol⁻¹"],"answer":"6.022 × 10²³ mol⁻¹","explanation":"One mole contains approximately 6.022 × 10²³ specified entities."},
    {"id":"CHE_022","stream":"Science","subject":"Chemistry","topic":"Atomic Structure","difficulty":"Easy","q":"The atomic number of an element equals the number of:","options":["Neutrons only","Protons","Protons plus neutrons","Shells"],"answer":"Protons","explanation":"Atomic number is defined by the number of protons in the nucleus."},
    {"id":"CHE_023","stream":"Science","subject":"Chemistry","topic":"Chemical Bonding","difficulty":"Medium","q":"Which species has a trigonal planar molecular shape?","options":["NH₃","BF₃","H₂O","CH₄"],"answer":"BF₃","explanation":"BF₃ has three bonding regions around boron and no lone pair on the central atom."},
    {"id":"CHE_024","stream":"Science","subject":"Chemistry","topic":"Periodic Table","difficulty":"Medium","q":"Across a period, first ionization enthalpy generally:","options":["Generally increases","Always becomes zero","Always decreases","Never changes"],"answer":"Generally increases","explanation":"Effective nuclear charge generally increases across a period, though exceptions occur."},
    {"id":"CHE_025","stream":"Science","subject":"Chemistry","topic":"Redox Reactions","difficulty":"Easy","q":"Oxidation is commonly defined as:","options":["Gain of electrons","Loss of electrons","Gain of neutrons","Loss of protons from nucleus"],"answer":"Loss of electrons","explanation":"In electron-transfer terms, oxidation is loss of electrons."},
    {"id":"CHE_026","stream":"Science","subject":"Chemistry","topic":"Chemical Bonding","difficulty":"Easy","q":"The bond in sodium chloride is primarily:","options":["Covalent","Ionic","Metallic","Hydrogen"],"answer":"Ionic","explanation":"Sodium transfers an electron to chlorine, producing oppositely charged ions."},
    {"id":"CHE_027","stream":"Science","subject":"Chemistry","topic":"Mole Concept","difficulty":"Medium","q":"The molar mass of CO₂ is approximately:","options":["28 g/mol","32 g/mol","44 g/mol","48 g/mol"],"answer":"44 g/mol","explanation":"12 + 2×16 = 44 g/mol."},
    {"id":"CHE_028","stream":"Science","subject":"Chemistry","topic":"Atomic Structure","difficulty":"Hard","q":"For a p subshell, the azimuthal quantum number l equals:","options":["0","1","2","3"],"answer":"1","explanation":"The s, p, d and f subshells correspond to l = 0, 1, 2 and 3."},
    {"id":"MAT_021","stream":"Science","subject":"Maths","topic":"Sets","difficulty":"Easy","q":"If A = {1,2,3}, how many elements are in A?","options":["2","3","4","6"],"answer":"3","explanation":"The set contains three distinct elements."},
    {"id":"MAT_022","stream":"Science","subject":"Maths","topic":"Sequences and Series","difficulty":"Easy","q":"The common difference of 7, 11, 15, 19, ... is:","options":["2","3","4","5"],"answer":"4","explanation":"Subtract consecutive terms: 11 − 7 = 4."},
    {"id":"MAT_023","stream":"Science","subject":"Maths","topic":"Trigonometry","difficulty":"Easy","q":"The value of cos 0° is:","options":["0","1/2","1","−1"],"answer":"1","explanation":"cos 0° = 1."},
    {"id":"MAT_024","stream":"Science","subject":"Maths","topic":"Permutations","difficulty":"Medium","q":"The number of ways to arrange 4 distinct books in a row is:","options":["16","24","12","8"],"answer":"24","explanation":"There are 4! = 4×3×2×1 = 24 arrangements."},
    {"id":"MAT_025","stream":"Science","subject":"Maths","topic":"Quadratic Equations","difficulty":"Medium","q":"The discriminant of ax² + bx + c = 0 is:","options":["b² − 4ac","a² − 4bc","b − 4ac","b² + 4ac"],"answer":"b² − 4ac","explanation":"The discriminant is D = b² − 4ac."},
    {"id":"MAT_026","stream":"Science","subject":"Maths","topic":"Sets","difficulty":"Medium","q":"If n(A)=5, n(B)=4 and A and B are disjoint, n(A ∪ B) is:","options":["1","5","9","20"],"answer":"9","explanation":"For disjoint sets, n(A ∪ B) = n(A) + n(B) = 9."},
    {"id":"MAT_027","stream":"Science","subject":"Maths","topic":"Sequences and Series","difficulty":"Medium","q":"The sum of the first n natural numbers is:","options":["n²","n(n+1)/2","n(n−1)/2","2n+1"],"answer":"n(n+1)/2","explanation":"The standard sum formula is n(n+1)/2."},
    {"id":"MAT_028","stream":"Science","subject":"Maths","topic":"Trigonometry","difficulty":"Hard","q":"If sin θ = 5/13 and θ is acute, cos θ is:","options":["5/12","12/13","13/12","8/13"],"answer":"12/13","explanation":"Using sin²θ + cos²θ = 1 gives cos θ = √(1 − 25/169) = 12/13."},
    # Expanded Science question bank: PCB
    {"id":"BIO_003","stream":"Science","subject":"Biology","topic":"Cell Biology","difficulty":"Easy","q":"The site of protein synthesis in a cell is the:","options":["Ribosome","Lysosome","Vacuole","Centrosome"],"answer":"Ribosome","explanation":"Ribosomes translate mRNA to assemble proteins."},
    {"id":"BIO_004","stream":"Science","subject":"Biology","topic":"Biomolecules","difficulty":"Easy","q":"Enzymes are mostly:","options":["Carbohydrates","Proteins","Lipids","Mineral salts"],"answer":"Proteins","explanation":"Most enzymes are proteins, although some RNA molecules can catalyse reactions."},
    {"id":"BIO_005","stream":"Science","subject":"Biology","topic":"Plant Physiology","difficulty":"Medium","q":"Photosynthesis mainly occurs in the:","options":["Mitochondrion","Chloroplast","Nucleus","Golgi apparatus"],"answer":"Chloroplast","explanation":"Chloroplasts contain chlorophyll and the machinery for photosynthesis."},
    {"id":"BIO_006","stream":"Science","subject":"Biology","topic":"Human Physiology","difficulty":"Easy","q":"Which blood cells primarily transport oxygen?","options":["Red blood cells","Platelets","White blood cells","Plasma proteins"],"answer":"Red blood cells","explanation":"Haemoglobin in red blood cells binds and transports oxygen."},
    {"id":"BIO_007","stream":"Science","subject":"Biology","topic":"Cell Biology","difficulty":"Medium","q":"The organelle containing most of a eukaryotic cell's DNA is the:","options":["Nucleus","Ribosome","Lysosome","Cell wall"],"answer":"Nucleus","explanation":"The nucleus houses most of the cell's genetic material."},
    {"id":"BIO_008","stream":"Science","subject":"Biology","topic":"Plant Physiology","difficulty":"Medium","q":"Water and minerals are mainly transported in plants by:","options":["Phloem","Xylem","Epidermis","Stomata"],"answer":"Xylem","explanation":"Xylem conducts water and dissolved minerals from roots to other plant parts."},
    {"id":"BIO_009","stream":"Science","subject":"Biology","topic":"Human Physiology","difficulty":"Medium","q":"The functional unit of the kidney is the:","options":["Neuron","Nephron","Alveolus","Villus"],"answer":"Nephron","explanation":"Nephrons filter blood and help form urine."},
    {"id":"BIO_010","stream":"Science","subject":"Biology","topic":"Biomolecules","difficulty":"Easy","q":"DNA stands for:","options":["Deoxyribonucleic acid","Dinitrogen acid","Dynamic nucleic atom","Deoxygenated nitrogen acid"],"answer":"Deoxyribonucleic acid","explanation":"DNA is the molecule that stores hereditary information in organisms."},
    {"id":"BIO_011","stream":"Science","subject":"Biology","topic":"Cell Biology","difficulty":"Hard","q":"During mitosis, sister chromatids separate in:","options":["Prophase","Metaphase","Anaphase","Interphase"],"answer":"Anaphase","explanation":"Sister chromatids are pulled to opposite poles during anaphase."},
    {"id":"BIO_012","stream":"Science","subject":"Biology","topic":"Human Physiology","difficulty":"Hard","q":"Gas exchange in human lungs occurs mainly across the:","options":["Trachea","Alveolar walls","Epiglottis","Bronchi cartilage"],"answer":"Alveolar walls","explanation":"Thin alveolar walls provide a large surface for diffusion of gases."},
    # Expanded Commerce question bank
    {"id":"ACC_004","stream":"Commerce","subject":"Accountancy","topic":"Accounting Equation","difficulty":"Easy","q":"A business owner invests cash as capital. The effect is generally:","options":["Assets and capital increase","Assets decrease and liabilities increase","Only expenses increase","Capital decreases"],"answer":"Assets and capital increase","explanation":"Cash (an asset) and owner's capital both increase by the investment."},
    {"id":"ACC_005","stream":"Commerce","subject":"Accountancy","topic":"Journal Entries","difficulty":"Medium","q":"Rent paid in cash is recorded by:","options":["Debit Rent, Credit Cash","Debit Cash, Credit Rent","Debit Capital, Credit Rent","Debit Sales, Credit Cash"],"answer":"Debit Rent, Credit Cash","explanation":"Rent expense is debited and cash is credited."},
    {"id":"ACC_006","stream":"Commerce","subject":"Accountancy","topic":"Accounting Equation","difficulty":"Medium","q":"If capital is ₹40,000 and liabilities are ₹10,000, assets equal:","options":["₹30,000","₹40,000","₹50,000","₹10,000"],"answer":"₹50,000","explanation":"Assets = Liabilities + Capital = ₹10,000 + ₹40,000."},
    {"id":"ACC_007","stream":"Commerce","subject":"Accountancy","topic":"Journal Entries","difficulty":"Easy","q":"Cash received from a debtor is recorded by debiting:","options":["Cash account","Sales account","Debtor account only","Purchases account"],"answer":"Cash account","explanation":"Cash increases, so the cash account is debited in the basic entry."},
    {"id":"ACC_008","stream":"Commerce","subject":"Accountancy","topic":"Accounting Equation","difficulty":"Hard","q":"A transaction that purchases equipment for cash will usually:","options":["Increase total assets","Decrease total assets","Change the composition of assets but not total assets","Increase liabilities"],"answer":"Change the composition of assets but not total assets","explanation":"Equipment increases while cash decreases by the same amount."},
    {"id":"BST_003","stream":"Commerce","subject":"Business Studies","topic":"Business Objectives","difficulty":"Easy","q":"Which is a non-economic objective of a business?","options":["Customer satisfaction","Maximising only inventory","Ignoring quality","Avoiding all innovation"],"answer":"Customer satisfaction","explanation":"Meeting customer needs is an important non-financial objective that supports business success."},
    {"id":"BST_004","stream":"Commerce","subject":"Business Studies","topic":"Forms of Business","difficulty":"Easy","q":"A major advantage of a partnership is:","options":["Shared capital and responsibility","No agreement between partners ever","Unlimited access to public funds","No need for coordination"],"answer":"Shared capital and responsibility","explanation":"Partners can pool resources, skills and decision-making."},
    {"id":"BST_005","stream":"Commerce","subject":"Business Studies","topic":"Business Objectives","difficulty":"Medium","q":"Entrepreneurship primarily involves:","options":["Identifying opportunities and organising resources","Avoiding all risk and decisions","Only recording transactions","Eliminating customer needs"],"answer":"Identifying opportunities and organising resources","explanation":"Entrepreneurs identify opportunities, organise resources and accept calculated risks."},
    {"id":"ECO_003","stream":"Commerce","subject":"Economics","topic":"Basic Concepts","difficulty":"Easy","q":"Opportunity cost is the:","options":["Value of the next best alternative forgone","Total money in a bank","Price of every good added together","Cost that is always zero"],"answer":"Value of the next best alternative forgone","explanation":"Opportunity cost measures what is given up when a choice is made."},
    {"id":"ECO_004","stream":"Commerce","subject":"Economics","topic":"Demand","difficulty":"Medium","q":"A demand schedule shows the relationship between price and:","options":["Quantity demanded","Production technology only","Tax rates only","Population only"],"answer":"Quantity demanded","explanation":"A demand schedule lists quantities demanded at different prices, other things equal."},
    {"id":"ECO_005","stream":"Commerce","subject":"Economics","topic":"Basic Concepts","difficulty":"Medium","q":"Which is an example of a capital good?","options":["A machine used in a factory","A snack bought for immediate consumption","A bus ticket for a passenger","A household's daily meal"],"answer":"A machine used in a factory","explanation":"Capital goods help produce other goods and services."},
    {"id":"ECO_006","stream":"Commerce","subject":"Economics","topic":"Demand","difficulty":"Hard","q":"If demand increases while supply stays the same, equilibrium price generally:","options":["Rises","Falls to zero","Always remains unchanged","Becomes negative"],"answer":"Rises","explanation":"An increase in demand with supply unchanged generally raises equilibrium price and quantity."},
    # Expanded Humanities question bank
    {"id":"HIS_002","stream":"Humanities","subject":"History","topic":"Historical Sources","difficulty":"Easy","q":"Coins are especially useful to historians for studying:","options":["Rulers, symbols and economic exchanges","Modern internet speed","Today's weather forecast","Future election results"],"answer":"Rulers, symbols and economic exchanges","explanation":"Coins can provide evidence about rulers, inscriptions, symbols and trade."},
    {"id":"HIS_003","stream":"Humanities","subject":"History","topic":"Historical Sources","difficulty":"Medium","q":"Why do historians compare multiple sources about an event?","options":["To cross-check evidence and perspectives","To avoid all evidence","To guarantee every source is identical","To replace research with guesses"],"answer":"To cross-check evidence and perspectives","explanation":"Comparing sources helps evaluate reliability, context and differing perspectives."},
    {"id":"HIS_004","stream":"Humanities","subject":"History","topic":"Historical Sources","difficulty":"Hard","q":"A primary source is generally one that:","options":["Comes from the period or a direct participant","Is always a modern textbook summary","Contains no evidence","Is necessarily fictional"],"answer":"Comes from the period or a direct participant","explanation":"Primary sources originate in or directly relate to the period being studied."},
    {"id":"GEO_002","stream":"Humanities","subject":"Geography","topic":"Maps and Scale","difficulty":"Easy","q":"Lines joining places of equal height above sea level are called:","options":["Contours","Isobars","Isotherms","Meridians"],"answer":"Contours","explanation":"Contour lines connect points of equal elevation."},
    {"id":"GEO_003","stream":"Humanities","subject":"Geography","topic":"Maps and Scale","difficulty":"Medium","q":"The Equator is located at:","options":["0° latitude","0° longitude","90° north latitude","180° longitude"],"answer":"0° latitude","explanation":"The Equator is the reference line at zero degrees latitude."},
    {"id":"GEO_004","stream":"Humanities","subject":"Geography","topic":"Maps and Scale","difficulty":"Medium","q":"The Prime Meridian passes through:","options":["Greenwich","The Equator only","The North Pole only","The International Date Line only"],"answer":"Greenwich","explanation":"The zero-degree longitude reference passes through Greenwich, London."},
    {"id":"GEO_005","stream":"Humanities","subject":"Geography","topic":"Physical Geography","difficulty":"Easy","q":"The continuous movement of water between Earth's surface and atmosphere is the:","options":["Water cycle","Rock cycle only","Carbon dating process","Tide table"],"answer":"Water cycle","explanation":"Evaporation, condensation and precipitation are key parts of the water cycle."},
    {"id":"POL_002","stream":"Humanities","subject":"Political Science","topic":"Constitution","difficulty":"Easy","q":"The principle that everyone is subject to the same law is called:","options":["Rule of law","Rule by wealth","Absolute privilege","Censorship"],"answer":"Rule of law","explanation":"Rule of law means laws apply according to established legal principles rather than arbitrary power."},
    {"id":"POL_003","stream":"Humanities","subject":"Political Science","topic":"Democracy","difficulty":"Medium","q":"In a democracy, citizens commonly choose representatives through:","options":["Elections","Inheritance only","Random weather events","Military rank"],"answer":"Elections","explanation":"Free and fair elections are a central way citizens choose representatives in representative democracies."},
    {"id":"POL_004","stream":"Humanities","subject":"Political Science","topic":"Constitution","difficulty":"Medium","q":"Separation of powers divides government authority among:","options":["Legislature, executive and judiciary","Only private companies","Only schools","Only local shops"],"answer":"Legislature, executive and judiciary","explanation":"The separation of powers distributes legislative, executive and judicial functions."},
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

st.markdown("<div class='brand-eyebrow'>YOUR PERSONAL LEARNING SPACE</div>", unsafe_allow_html=True)
st.title("SmartStudy AI")
st.caption("Learn smarter. Plan better. Make every study session count.")

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
            new_stream = st.selectbox("Stream / track", ["Science • PCM", "Science • PCB", "Commerce", "Humanities"], key="new_stream")
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
            stream_options = ["Science • PCM", "Science • PCB", "Commerce", "Humanities"]
            saved_stream = user[1]
            if saved_stream == "Science": saved_stream = "Science • PCM"
            if saved_stream not in stream_options: saved_stream = "Science • PCM"
            chosen_stream = st.selectbox(
                "Active stream / track",
                stream_options,
                index=stream_options.index(saved_stream),
                key="active_stream_selector",
                help="Choose PCM or PCB for Science, or switch to Commerce/Humanities."
            )
            if chosen_stream != saved_stream or user[1] != chosen_stream:
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
    st.markdown("- Take randomized quizzes with explanations\n- Review progress analytics\n- Generate a topic-based revision plan\n- Save notes for revision\n- Choose PCM, PCB, Commerce, or Humanities")
    st.warning("Prototype note: local SQLite storage is used. Streamlit Cloud's local disk is not guaranteed permanent; for durable online accounts, connect a managed database before using this with real student data.")
    st.stop()

username = st.session_state.signed_in_user
user = get_user(username)
profile_stream = user[1]
class_level = user[2]
science_track = "PCB" if profile_stream == "Science • PCB" else "PCM"
question_stream = "Science" if profile_stream.startswith("Science") else profile_stream
all_attempts = get_attempts(username)
topic_scores = topics_summary(all_attempts)

tab_dashboard, tab_quiz, tab_planner, tab_notes, tab_about = st.tabs(
    ["🏠 Dashboard", "📝 Smart Quiz", "📅 Study Planner", "🗒️ Notes", "ℹ️ About"]
)

with tab_dashboard:
    st.markdown(f"## Welcome back, {username.title()} 👋")
    st.markdown(f"<div style='background:linear-gradient(120deg,#5145CD,#8178F4);padding:18px 22px;border-radius:18px;color:white;margin:10px 0 22px 0;'><div style='font-size:12px;letter-spacing:.1em;font-weight:700;opacity:.85;'>YOUR CURRENT LEARNING TRACK</div><div style='font-family:Manrope,sans-serif;font-size:24px;font-weight:800;margin-top:3px;'>{profile_stream} · Class {class_level}</div><div style='opacity:.9;font-size:13px;margin-top:4px;'>Small consistent sessions build strong results.</div></div>", unsafe_allow_html=True)
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
    subjects = sorted({q["subject"] for q in QUESTIONS if q["stream"] == question_stream and
                       (question_stream != "Science" or (science_track == "PCM" and q["subject"] != "Biology") or (science_track == "PCB" and q["subject"] != "Maths"))})
    subject_choices = ["All subjects"] + subjects
    c1,c2,c3 = st.columns(3)
    with c1: subject_filter = st.selectbox("Subject", subject_choices, key=f"quiz_subject_{profile_stream}")
    with c2: difficulty_filter = st.selectbox("Difficulty", ["All","Easy","Medium","Hard"], key="quiz_difficulty")
    with c3: question_count = st.selectbox("Questions", [5,10], index=1, key="quiz_count")
    if st.button("🎲 Generate quiz", type="primary", use_container_width=True):
        pool = [q for q in QUESTIONS if q["stream"] == question_stream and
                (question_stream != "Science" or (science_track == "PCM" and q["subject"] != "Biology") or (science_track == "PCB" and q["subject"] != "Maths")) and
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
            topics=[f"{s} revision" for s in sorted({q['subject'] for q in QUESTIONS if q['stream']==question_stream and (question_stream != 'Science' or (science_track == 'PCM' and q['subject'] != 'Biology') or (science_track == 'PCB' and q['subject'] != 'Maths'))})[:3]]
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
        n_subject=st.selectbox("Subject", sorted({q["subject"] for q in QUESTIONS if q["stream"]==question_stream and (question_stream != "Science" or (science_track == "PCM" and q["subject"] != "Biology") or (science_track == "PCB" and q["subject"] != "Maths"))}), key=f"note_subject_{profile_stream}")
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
    ## About SmartStudy AI 3.0
    **Problem statement:** Students may struggle to decide what to revise first and how to divide available study time.

    **Prototype workflow**
    1. Student creates a local prototype profile and chooses a stream/class.
    2. The question bank supplies practice questions.
    3. Quiz answers are scored and grouped by topic.
    4. Transparent rules classify topic priority: below 50% High, 50–79% Medium, 80%+ Low.
    5. The planner allocates more time to higher-priority topics.
    6. Quiz attempts and notes are stored in a local SQLite database.

    **Current tracks:** Science • PCM (Physics, Chemistry, Maths), Science • PCB (Physics, Chemistry, Biology), Commerce and Humanities.
    **Current limitations:** This is an educational prototype. Priority rules are not a production-trained AI model. The question bank is expanded but remains a learning prototype and should be reviewed against the current syllabus. Local SQLite storage on free hosted instances may not survive restarts/rebuilds. The profile/PIN is for prototype separation, not high-security authentication. Do not store sensitive personal information.
    """)
    st.metric("Questions in this prototype", len(QUESTIONS))
    counts = [
        {"Track": "Science • PCM", "Subjects": "Physics, Chemistry, Maths", "Questions": sum(q["stream"]=="Science" and q["subject"]!="Biology" for q in QUESTIONS)},
        {"Track": "Science • PCB", "Subjects": "Physics, Chemistry, Biology", "Questions": sum(q["stream"]=="Science" and q["subject"]!="Maths" for q in QUESTIONS)},
        {"Track": "Commerce", "Subjects": "Accountancy, Business Studies, Economics", "Questions": sum(q["stream"]=="Commerce" for q in QUESTIONS)},
        {"Track": "Humanities", "Subjects": "History, Geography, Political Science", "Questions": sum(q["stream"]=="Humanities" for q in QUESTIONS)},
    ]
    st.dataframe(pd.DataFrame(counts), use_container_width=True, hide_index=True)

st.sidebar.caption("SmartStudy AI 3.0 • Student prototype")
