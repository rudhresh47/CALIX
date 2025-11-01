import streamlit as st
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import pandas as pd

st.set_page_config(
    page_title="CALIX",
    page_icon="apple",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === MAKE IT A PHONE APP ===
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="CALIX">
<link rel="manifest" href="/manifest.json">
""", unsafe_allow_html=True)

# === DARK THEME ===
st.markdown("""
<style>
    body, .stApp {background:#121212 !important; color:#FFF !important;}
    .stTextInput input {background:#1E1E1E !important; color:#FFF !important; border:1px solid #444 !important;}
    .stFileUploader > div {background:#1E1E1E !important; border:2px dashed #444 !important;}
    .stButton>button {background:#FF9800; color:white; border-radius:20px; padding:10px 24px; font-weight:bold;}
    .stButton>button:hover {background:#F57C00;}
    .nav {background:#1E1E1E; padding:15px; box-shadow:0 2px 10px rgba(0,0,0,0.3); display:flex; justify-content:center; flex-wrap:wrap; margin-bottom:20px;}
    .logo {font-size:32px; color:#4CAF50; font-weight:bold; margin-right:30px;}
    .link {margin:0 15px; color:#BBB; text-decoration:none; padding:8px 16px; border-radius:8px;}
    .link:hover {background:#333; color:#4CAF50;}
    .card {background:#1E1E1E; padding:25px; border-radius:12px; border:1px solid #333; margin:15px 0;}
    .title {color:#4CAF50; font-size:42px; text-align:center; margin:30px 0;}
    .footer {text-align:center; color:#666; font-size:14px; margin-top:60px; padding:15px; border-top:1px solid #333;}
    .nav-btn {background:#333; color:#FFF; padding:8px 16px; border-radius:8px; border:none; margin:0 5px;}
    .nav-btn:hover {background:#555;}
    .stDataFrame td, .stDataFrame th {color:#FFF !important; background:#1E1E1E !important;}
</style>
""", unsafe_allow_html=True)

# === FOOTER ===
def footer():
    st.markdown('<div class="footer">©2025 CALIX|AMC CSE-AIML|Open Source Powered</div>', unsafe_allow_html=True)

# === NAV BAR ===
def nav_bar():
    st.markdown("""
    <div class="nav">
        <div class="logo">CALIX</div>
        <a href="/?page=home" class="link">Home</a>
        <a href="/?page=estimate" class="link">Estimate</a>
        <a href="/?page=food_library" class="link">Food Library</a>
        <a href="/?page=health_tips" class="link">Health Tips</a>
        <a href="/?page=about" class="link">About</a>
    </div>
    """, unsafe_allow_html=True)

page = st.query_params.get("page", "home")

# === BETTER MODEL: eslamxm/vit-base-food101 (Fine-tuned Food-101 + 88% Accuracy) ===
@st.cache_resource(show_spinner="Loading AI...")
def load_model():
    processor = AutoImageProcessor.from_pretrained("eslamxm/vit-base-food101")
    model = AutoModelForImageClassification.from_pretrained("eslamxm/vit-base-food101")
    return processor, model

processor, model = load_model()
food_names = [model.config.id2label[i].replace("_", " ").title() for i in range(len(model.config.id2label))]

# === LOCAL NUTRITION ===
nutrition_db = {
    "Pizza": {"cal": 285, "carb": "36g", "prot": "12g", "fat": "10g"},
    "Biryani": {"cal": 320, "carb": "45g", "prot": "15g", "fat": "12g"},
    "Appam": {"cal": 180, "carb": "32g", "prot": "3g", "fat": "5g"},
    "Samosa": {"cal": 250, "carb": "25g", "prot": "5g", "fat": "15g"},
    "Idli": {"cal": 60, "carb": "12g", "prot": "2g", "fat": "0.5g"},
    "Dosa": {"cal": 170, "carb": "28g", "prot": "4g", "fat": "6g"},
    "Burger": {"cal": 500, "carb": "45g", "prot": "25g", "fat": "28g"},
    "Pancakes": {"cal": 220, "carb": "32g", "prot": "6g", "fat": "8g"},
    "Chicken Curry": {"cal": 320, "carb": "15g", "prot": "25g", "fat": "18g"},
    "default": {"cal": 250, "carb": "30g", "prot": "10g", "fat": "10g"}
}

# === HISTORY ===
if "history" not in st.session_state:
    st.session_state.history = []

# === 50 TIPS ===
health_tips = [
    "Drink 8 glasses of water daily.", "Eat 5 servings of fruits and vegetables.", "Walk 30 minutes every day.",
    "Avoid sugary drinks.", "Sleep 7-8 hours per night.", "Choose whole grains over refined.",
    "Limit processed foods.", "Eat protein with every meal.", "Reduce salt intake.",
    "Cook at home more often.", "Read food labels.", "Eat slowly and mindfully.",
    "Include healthy fats like avocado.", "Limit alcohol consumption.", "Practice portion control.",
    "Add spices instead of salt.", "Eat breakfast daily.", "Stay hydrated during exercise.",
    "Choose lean proteins.", "Include fiber-rich foods.", "Limit fried foods.",
    "Eat more plant-based meals.", "Avoid late-night snacking.", "Chew food thoroughly.",
    "Include omega-3 rich foods.", "Reduce caffeine after noon.", "Eat colorful foods.",
    "Plan meals ahead.", "Keep healthy snacks handy.", "Avoid emotional eating.",
    "Exercise in the morning.", "Stand more, sit less.", "Take stairs instead of elevator.",
    "Practice yoga or meditation.", "Get sunlight daily.", "Limit screen time before bed.",
    "Eat fermented foods for gut health.", "Include nuts and seeds.", "Drink green tea.",
    "Avoid trans fats.", "Eat fish twice a week.", "Include legumes in diet.",
    "Reduce red meat intake.", "Eat seasonal foods.", "Grow your own herbs.",
    "Share meals with family.", "Practice gratitude before eating.", "Try new healthy recipes.",
    "Keep a food journal.", "Celebrate small wins.", "Stay consistent, not perfect."
]

# === NAV BUTTONS ===
def nav_buttons(prev=None, next=None):
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if prev and st.button("Back", key=f"back_{page}"):
            st.query_params["page"] = prev
            st.rerun()
    with col3:
        if next and st.button("Next", key=f"next_{page}"):
            st.query_params["page"] = next
            st.rerun()

# === PAGES ===
nav_bar()

# === HOME ===
if page == "home":
    st.markdown('<h1 class="title">Know What You Eat - Instantly.</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload food photo", type=["jpg","png","jpeg"])
        if uploaded:
            st.session_state.uploaded_image = uploaded
            st.image(uploaded, width=250)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><p><b>Detects 101 Foods:</b><br>Pizza, Biryani, Appam, Samosa, Idli, Dosa, Burger, etc.</p></div>', unsafe_allow_html=True)
    nav_buttons(next="estimate")
    footer()

# === ESTIMATE ===
elif page == "estimate":
    st.markdown('<h1 class="title">Estimate Calories</h1>', unsafe_allow_html=True)
    uploaded = st.session_state.get("uploaded_image") or st.file_uploader("Upload photo", type=["jpg","png","jpeg"])
    
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, width=300)
        
        with st.spinner("Detecting food..."):
            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            idx = outputs.logits.argmax(-1).item()
            name = food_names[idx]

        st.success(f"*Detected:* {name}")

        nut = nutrition_db.get(name, nutrition_db["default"])

        st.markdown(f"""
        <div class="card">
            <p><b>Calories:</b> {nut['cal']} kcal/100g</p>
            <p><b>Carbs:</b> {nut['carb']}</p>
            <p><b>Protein:</b> {nut['prot']}</p>
            <p><b>Fat:</b> {nut['fat']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Add to Daily Log"):
            st.session_state.history.append({
                "Food": name,
                "Calories": nut['cal'],
                "Carbs": nut['carb'],
                "Protein": nut['prot'],
                "Fat": nut['fat']
            })
            st.success("Added!")

        nav_buttons(prev="home", next="food_library")
    else:
        nav_buttons(prev="home")
    footer()

# === FOOD LIBRARY ===
elif page == "food_library":
    st.markdown('<h1 class="title">Food Library (History)</h1>', unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        total_cal = sum([x for x in df["Calories"] if isinstance(x, (int, float))])
        st.info(f"*Total Calories Logged:* {total_cal} kcal")
    else:
        st.info("No food logged yet.")
    nav_buttons(prev="estimate", next="health_tips")
    footer()

# === HEALTH TIPS ===
elif page == "health_tips":
    st.markdown('<h1 class="title">Health Tips</h1>', unsafe_allow_html=True)
    tip_idx = st.session_state.get("tip_idx", 0)
    st.markdown(f'<div class="card"><p>{health_tips[tip_idx]}</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Previous"):
            st.session_state.tip_idx = (tip_idx - 1) % len(health_tips)
            st.rerun()
    with col3:
        if st.button("Next"):
            st.session_state.tip_idx = (tip_idx + 1) % len(health_tips)
            st.rerun()
    nav_buttons(prev="food_library", next="about")
    footer()

# === ABOUT ===
elif page == "about":
    st.markdown('<h1 class="title">About CALIX</h1>', unsafe_allow_html=True)
    st.markdown("""
    *CALIX* is an AI food detector that identifies *101 foods* from photos.

    ### Features
    - *Detects exact names*: Pizza, Biryani, Appam, Samosa, Idli, Dosa, etc.
    - *Local nutrition*: Calories, Carbs, Protein, Fat (no internet needed)
    - *History log*: Saves all scans with full details
    - *50 Health Tips*
    - *Dark theme + navigation*

    ### AI Model
    - eslamxm/vit-base-food101 (Public, 101 classes from Food-101 dataset)
    - Dataset: 101,000 images, 101 classes

    *Built by:*  
    Rudhreshwaran, Shreyas, Tiya Singh, Shubham Prasad, Shubham Raj  
    *AMC CSE-AIML | 2025*
    """)
    nav_buttons(prev="health_tips")
    footer()