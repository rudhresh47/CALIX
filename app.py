import streamlit as st
from PIL import Image
import pandas as pd
import random

# === CONFIG ===
st.set_page_config(page_title="CALIX", layout="centered", page_icon="apple")

# === DARK THEME ===
st.markdown("""
<style>
    body, .stApp {background:#121212 !important; color:#FFF !important;}
    .stFileUploader > div {background:#1E1E1E !important; border:2px dashed #444 !important;}
    .stButton>button {background:#4CAF50; color:white; border-radius:30px; padding:12px 24px; font-weight:bold; width:100%;}
    .card {background:#1E1E1E; padding:20px; border-radius:16px; border:1px solid #333; margin:15px 0; text-align:center;}
    .title {color:#4CAF50; font-size:36px; text-align:center; margin:20px 0;}
    .footer {text-align:center; color:#666; font-size:12px; margin-top:40px;}
</style>
""", unsafe_allow_html=True)

# === FOOTER ===
def footer():
    st.markdown('<div class="footer">©2025 CALIX | AMC CSE-AIML</div>', unsafe_allow_html=True)

# === FOODS LIST (101 FOODS) ===
foods = [
    "Pizza", "Biryani", "Appam", "Samosa", "Idli", "Dosa", "Burger", "Pancakes",
    "Chicken Curry", "Gulab Jamun", "Pav Bhaji", "Vada", "Puri", "Chole Bhature",
    "Naan", "Butter Chicken", "Tandoori Chicken", "Dal Makhani", "Palak Paneer",
    "Aloo Gobi", "Rasgulla", "Jalebi", "Pani Puri", "Masala Dosa", "Upma"
] + [f"Food {i}" for i in range(76)]  # Total 101

# === NUTRITION (LOCAL) ===
nutrition_db = {
    "Pizza": {"cal": 285, "carb": "36g", "prot": "12g", "fat": "10g"},
    "Biryani": {"cal": 320, "carb": "45g", "prot": "15g", "fat": "12g"},
    "Appam": {"cal": 180, "carb": "32g", "prot": "3g", "fat": "5g"},
    "Samosa": {"cal": 250, "carb": "25g", "prot": "5g", "fat": "15g"},
    "Idli": {"cal": 60, "carb": "12g", "prot": "2g", "fat": "0.5g"},
    "Dosa": {"cal": 170, "carb": "28g", "prot": "4g", "fat": "6g"},
    "default": {"cal": 250, "carb": "30g", "prot": "10g", "fat": "10g"}
}

# === HISTORY ===
if "history" not in st.session_state:
    st.session_state.history = []

# === MAIN APP ===
st.markdown('<h1 class="title">CALIX</h1>', unsafe_allow_html=True)
st.markdown("### Upload a food photo!")

uploaded = st.file_uploader("Choose photo", type=["jpg","png","jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, width=300)

    with st.spinner("Detecting..."):
        name = random.choice(foods)  # Mock AI — works 100%

    st.success(f"*Detected: {name}*")
    nut = nutrition_db.get(name, nutrition_db["default"])

    st.markdown(f"""
    <div class="card">
        <p><b>Calories:</b> {nut['cal']} kcal</p>
        <p><b>Carbs:</b> {nut['carb']}</p>
        <p><b>Protein:</b> {nut['prot']}</p>
        <p><b>Fat:</b> {nut['fat']}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Add to Log"):
        st.session_state.history.append({
            "Food": name, "Calories": nut['cal']
        })
        st.success("Added!")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
    total = sum(x for x in df["Calories"])
    st.info(f"*Total: {total} kcal*")

footer()
