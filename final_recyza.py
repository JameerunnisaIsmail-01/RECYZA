
import os, re, html
from pathlib import Path
from urllib.parse import urljoin
import numpy as np
import requests
from bs4 import BeautifulSoup
from PIL import Image
import streamlit as st

st.set_page_config(page_title="RECYZA | Shop • Recycle • Earn", page_icon="♻️", layout="wide")

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 10% 0%,rgba(123,22,49,.25),transparent 28%),radial-gradient(circle at 90% 10%,rgba(91,16,36,.20),transparent 25%),#070707;color:#f5edf0}
[data-testid="stSidebar"]{background:#0b0b0b;border-right:1px solid #2d1b22}
[data-testid="stSidebar"] *{color:#f5edf0!important}
.hero{padding:30px 34px;border:1px solid #4b1b2a;border-radius:24px;background:linear-gradient(135deg,#10090c,#260d16 52%,#090909);box-shadow:0 20px 60px rgba(0,0,0,.45);margin-bottom:24px}
.hero h1{margin:0;font-size:46px;color:#fff}.hero .accent{color:#c92d58}.hero p{color:#c7b7bd;font-size:17px}
.badge{display:inline-block;background:#3a0d1c;color:#f0b7c7;border:1px solid #75203a;padding:6px 11px;border-radius:999px;font-size:12px;margin:3px}
.product-card{background:linear-gradient(180deg,#141414,#0c0c0c);border:1px solid #2d1b22;border-radius:18px;padding:12px;min-height:410px;box-shadow:0 12px 35px rgba(0,0,0,.25)}
.product-name{color:#fff;font-size:17px;font-weight:700;margin-top:12px;min-height:48px}
.ai-tag{color:#f0b7c7;background:#35101e;border:1px solid #6b1b35;border-radius:8px;padding:4px 8px;font-size:11px;display:inline-block;margin-top:5px}
.price{color:#fff;font-size:21px;font-weight:800;margin:8px 0}
.panel,.order-card,.reward-card{background:#101010;border:1px solid #2d1b22;border-radius:18px;padding:20px;margin:12px 0}
.delivered{background:#11231d;border:1px solid #205d48;color:#6ce0ad;padding:9px 12px;border-radius:10px;margin:10px 0}
.verified{background:#10231b;border:1px solid #277253;border-radius:15px;padding:18px;color:#7de6b8}
.rejected{background:#2a0d14;border:1px solid #742039;border-radius:15px;padding:18px;color:#ff9ab4}
.coin{color:#f2c14e;font-size:28px;font-weight:900}.wallet{color:#7de6b8;font-size:28px;font-weight:900}
.small{color:#9e9096;font-size:12px}.footer{text-align:center;color:#76666d;padding:30px 0;border-top:1px solid #25161c;margin-top:40px}

/* Yellow user-input fields requested for the demo. */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stFileUploader section {
    background:#fff7bf!important;
    color:#111!important;
    border:2px solid #d4a900!important;
}
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder {
    color:#6b5a00!important;
    opacity:1!important;
}
.stSelectbox div[data-baseweb="select"] * {
    color:#111!important;
}
.stFileUploader section * {
    color:#111!important;
}

div.stButton>button{background:#6e1530;color:white;border:1px solid #9a2347;border-radius:10px;font-weight:700}
div.stButton>button:hover{background:#8b1b3d;border-color:#c12b57;color:white}
.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"]{background:#111!important;color:white!important;border-color:#3c222b!important}
</style>
""", unsafe_allow_html=True)

PRODUCTS = [{'name': 'white tone face powder', 'url': 'https://dl.flipkart.com/s/O1KcArNNNN', 'ai_class': 'whitetone face powder'}, {'name': 'dove hairfall resue shampoo', 'url': 'https://dl.flipkart.com/s/O14qWGNNNN', 'ai_class': 'Dove HairFall Rescue'}, {'name': 'parachute coconut oil', 'url': 'https://dl.flipkart.com/s/aG_EuHuuuN', 'ai_class': 'parachute hair oil'}, {'name': 'lizol floor cleaner', 'url': 'https://dl.flipkart.com/dl/lizol-disinfectant-surface-cleaner-floor-bathroom-kitchen-tile-not-phenyl-liquid-citrus/p/itm1a57ec8070d55?pid=BCRET7WHDEHBH9PD&lid=LSTBCRET7WHDEHBH9PDQRRDGC&marketplace=FLIPKART&_refId=&_appId=WA', 'ai_class': 'Lizol floor cleaner'}, {'name': 'wottagirl perfume', 'url': 'https://dl.flipkart.com/s/aGEdgwuuuN', 'ai_class': 'wotta girl perfume'}, {'name': 'nivya body lotion', 'url': 'https://dl.flipkart.com/s/O1zk4jNNNN', 'ai_class': 'nivya body mik'}, {'name': 'liveon serum', 'url': 'https://dl.flipkart.com/s/aG71pAuuuN', 'ai_class': 'Livon serum'}, {'name': 'denver perfume', 'url': 'https://dl.flipkart.com/s/O1GjSZNNNN', 'ai_class': 'Denver perfume'}, {'name': 'clinic plus shampoo', 'url': 'https://dl.flipkart.com/dl/clinic-plus-strong-long-healthy-hair-shampoo-milk-protein-multivitamins/p/itm217070c370413?pid=SMPG2ZXWAEHA2GNQ&lid=LSTSMPG2ZXWAEHA2GNQKTDANW&marketplace=FLIPKART&hl_lid=&q=clinic+plus+shampoo&store=g9b/lcf/qqm/t36&ctx=eyJkZWxpdmVyZWRCeSI6IjE3ODY2NzYzNTExNDYiLCJkaXNwbGF5UHJpY2UiOiI1ODEifQ==&fm=eyJ3dHAiOiJwcm9kdWN0Q2FyZExpc3QiLCJwcnB0Ijoic3AiLCJtaWQiOiJQUk9EVUNUIn0&_refId=&_appId=WA', 'ai_class': 'clinic plus shampoo'}, {'name': 'mamaearth rosemary water', 'url': 'https://dl.flipkart.com/s/O1lAryNNNN', 'ai_class': 'Mamaearth Rosemary Water'}, {'name': 'Woven, Solid/Plain Maheshwari Cotton Silk Saree', 'url': 'https://dl.flipkart.com/s/aGZ3xkuuuN', 'ai_class': None}, {'name': 'Printed Daily Wear Cotton Silk Saree', 'url': 'https://dl.flipkart.com/s/O10M2BNNNN', 'ai_class': None}, {'name': 'Women Ethnic Dress Green Midi/Calf Length Dress', 'url': 'https://dl.flipkart.com/s/aGA3kauuuN', 'ai_class': None}, {'name': 'Women Ethnic Dress Green Midi/Calf Length Dress', 'url': 'https://dl.flipkart.com/dl/zwerlon-women-a-line-light-blue-midi-calf-length-dress/p/itm68bef1e01bb4f?pid=DREHC8KYZHAZAC9H&lid=LSTDREHC8KYZHAZAC9HQEBZYQ&hl_lid=&marketplace=FLIPKART&fm=eyJ3dHAiOiJhdGxhc19wcm9kdWN0X3N1bW1hcnlfZ3JpZF9saWZlc3R5bGVfdjIiLCJwcnB0Ijoic3AiLCJtaWQiOiJhZHMifQ==&_refId=&_appId=CL', 'ai_class': None}, {'name': 'Women Straight Fit High Rise Blue Jeans', 'url': 'https://dl.flipkart.com/s/aGgyP1uuuN', 'ai_class': None}, {'name': 'Men Colorblock Zip Neck Polyester Pink T-Shirt', 'url': 'https://dl.flipkart.com/dl/vebnor-colorblock-men-zip-neck-pink-t-shirt/p/itm0eed7ea508fbe?pid=TSHHHUXECJCUNNVD&lid=LSTTSHHHUXECJCUNNVD7NLYCF&hl_lid=&marketplace=FLIPKART&fm=eyJ3dHAiOiJhdGxhc19wcm9kdWN0X3N1bW1hcnlfZ3JpZF9saWZlc3R5bGVfdjIiLCJwcnB0Ijoic3AiLCJtaWQiOiJhZHMifQ==&_refId=&_appId=CL', 'ai_class': None}, {'name': 'Men Colorblock Zip Neck Polyester Pink T-Shirt', 'url': 'https://dl.flipkart.com/dl/tazo-striped-men-polo-neck-multicolor-t-shirt/p/itm16aec7bdec68f?pid=TSHHCQF75ZQEVYN4&lid=LSTTSHHCQF75ZQEVYN48QVEXS&hl_lid=&marketplace=FLIPKART&fm=eyJ3dHAiOiJhdGxhc19wcm9kdWN0X3N1bW1hcnlfZ3JpZF9saWZlc3R5bGVfdjIiLCJwcnB0Ijoic3AiLCJtaWQiOiJhZHMifQ==&_refId=&_appId=CL', 'ai_class': None}, {'name': 'Dry Fruits Combo Pack Of Almond, Cashew, Golden Raisins, Pistachios - 400g Almonds, Cashews, Raisins, Pistachios', 'url': 'https://dl.flipkart.com/dl/pramix-dry-fruits-combo-pack-almond-cashew-golden-raisins-pistachios-400g-almonds-cashews/p/itmb3552abcc22a8?pid=NDFGGGGUJHJGRMZC&lid=LSTNDFGGGGUJHJGRMZCSGR4YD&marketplace=FLIPKART&hl_lid=&q=grocery+all+item&store=eat/ltb&ctx=eyJkZWxpdmVyZWRCeSI6IjE3ODY3NjI3NTQ2NTciLCJkaXNwbGF5UHJpY2UiOiI0NzUifQ==&fm=eyJ3dHAiOiJwcm9kdWN0Q2FyZExpc3QiLCJwcnB0Ijoic3AiLCJtaWQiOiJQUk9EVUNUIn0&_refId=&_appId=WA', 'ai_class': None}, {'name': 'Premium -Mewa- Mix(Almonds,Cashews Raisin,Apricot,Assorted Seeds & Nuts(1x250g) Assorted Nuts', 'url': 'https://dl.flipkart.com/s/aobYykuuuN', 'ai_class': None}, {'name': 'Gradient Rectangular Sunglasses (50)', 'url': 'https://dl.flipkart.com/s/ao_saFuuuN', 'ai_class': None}, {'name': 'UV Protection Retro Square Sunglasses (Free Size)', 'url': 'https://dl.flipkart.com/s/O6JbjjNNNN', 'ai_class': None}, {'name': 'Premium -Mewa- Mix(Almonds,Cashews Raisin,Apricot,Assorted Seeds & Nuts(1x250g) Assorted Nuts', 'url': 'https://dl.flipkart.com/s/O6WOEZNNNN', 'ai_class': None}, {'name': 'Premium -Mewa- Mix(Almonds,Cashews Raisin,Apricot,Assorted Seeds & Nuts(1x250g) Assorted Nuts', 'url': 'https://dl.flipkart.com/s/O6WRHYNNNN', 'ai_class': None}, {'name': 'Premium -Mewa- Mix(Almonds,Cashews Raisin,Apricot,Assorted Seeds & Nuts(1x250g) Assorted Nuts', 'url': 'https://dl.flipkart.com/s/aooD1auuuN', 'ai_class': None}, {'name': 'Premium -Mewa- Mix(Almonds,Cashews Raisin,Apricot,Assorted Seeds & Nuts(1x250g) Assorted Nuts', 'url': 'https://www.flipkart.com/yashika-crepe-printed-salwar-suit-material/p/itmeeb4604919452?pid=FABH3S95QGG4ZJTU&lid=LSTFABH3S95QGG4ZJTUJS32EN&marketplace=FLIPKART&store=clo%2Fqfi%2Fxcx%2Fms4&spotlightTagId=default_BestsellerId_clo%2Fqfi%2Fxcx%2Fms4&srno=b_1_10&otracker=browse&fm=Search&iid=e8ce588b-b103-456b-b695-b4cb53854072.FABH3S95QGG4ZJTU.SEARCH&ppt=browse&ppn=browse&ov_redirect=true', 'ai_class': None}, {'name': 'Premium -Mewa- Mix(Almonds,Cashews Raisin,Apricot,Assorted Seeds & Nuts(1x250g) Assorted Nuts', 'url': 'https://www.flipkart.com/krishna-boutique-pure-cotton-printed-salwar-suit-material/p/itmc5ea47b4451df?pid=FABHNJAZZNVPWAYT&lid=LSTFABHNJAZZNVPWAYTZMDIJT&marketplace=FLIPKART&store=clo%2Fqfi%2Fxcx%2Fms4&srno=b_1_14&otracker=browse&fm=Search&iid=e8ce588b-b103-456b-b695-b4cb53854072.FABHNJAZZNVPWAYT.SEARCH&ppt=browse&ppn=browse&ov_redirect=true', 'ai_class': None}]
MODEL_CLASSES = ["Denver perfume","Dove HairFall Rescue","Livon serum","Lizol floor cleaner","Mamaearth Rosemary Water","clinic plus shampoo","nivya body mik","parachute hair oil","whitetone face powder","wotta girl perfume"]
MODEL_FILES = ["RECYZA_FINAL_MODEL_95_16.keras","RECYZA_FINAL_MODEL_95_16(1).keras","RECYZA_BEST_10_EPOCH_MODEL.keras","recyza_best_model.keras"]

for key, default in {"page":"Home","cart":[],"orders":[],"wallet":0,"coins":0,"selected_order":None,"recycle_result":None}.items():
    if key not in st.session_state: st.session_state[key]=default

def go(page):
    st.session_state.page=page
    st.rerun()

def clean_name(x):
    x=re.sub(r"\s+"," ",str(x)).strip()
    return x[:95]+("…" if len(x)>95 else "")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_meta(url):
    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0 Chrome/131 Safari/537.36","Accept-Language":"en-US,en;q=0.9"},timeout=10,allow_redirects=True)
        if r.status_code>=400: return {"title":None,"image":None}
        soup=BeautifulSoup(r.text,"html.parser")
        title=image=None
        m=soup.find("meta",attrs={"property":"og:title"})
        if m: title=m.get("content")
        m=soup.find("meta",attrs={"property":"og:image"})
        if m: image=urljoin(r.url,m.get("content",""))
        return {"title":title,"image":image}
    except Exception:
        return {"title":None,"image":None}

def add_to_cart(p):
    st.session_state.cart.append(dict(p))
    st.toast(f"Added {p['name']} to cart.")

def price(p):
    return {"Denver perfume":499,"Dove HairFall Rescue":349,"Livon serum":299,"Lizol floor cleaner":239,"Mamaearth Rosemary Water":449,"clinic plus shampoo":299,"nivya body mik":289,"parachute hair oil":199,"whitetone face powder":299,"wotta girl perfume":349}.get(p.get("ai_class"),399)

def find_model():
    here=Path(__file__).resolve().parent
    for f in MODEL_FILES:
        if (here/f).exists(): return str(here/f)
    return None

@st.cache_resource(show_spinner=False)
def load_model(path):
    import tensorflow as tf
    return tf.keras.models.load_model(path,compile=False)

def predict(uploaded):
    path=find_model()
    if not path: raise FileNotFoundError("Put RECYZA_FINAL_MODEL_95_16.keras beside app.py.")
    model=load_model(path)
    im=Image.open(uploaded).convert("RGB").resize((224,224))
    arr=np.expand_dims(np.asarray(im,dtype=np.float32),0)
    probs=model.predict(arr,verbose=0)[0]
    ids=np.argsort(probs)[::-1][:3]
    return [(MODEL_CLASSES[int(i)],float(probs[int(i)])) for i in ids]

st.markdown('<div class="hero"><span class="badge">AI POWERED</span><span class="badge">RECYCLE & EARN</span><span class="badge">SMART SHOPPING</span><h1>♻️ <span class="accent">RECYZA</span></h1><p>Shop real products. Recycle the delivered product. Verify it with AI. Earn money credit or SuperCoins.</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ♻️ RECYZA")
    for label,page in [("🏠 Home","Home"),("🛍️ Shop","Shop"),("🛒 Cart","Cart"),("📦 My Orders","My Orders"),("♻️ Recycle Center","Recycle Center"),("💰 Rewards","Rewards")]:
        suffix=f" ({len(st.session_state.cart)})" if page=="Cart" else ""
        if st.button(label+suffix,use_container_width=True): go(page)
    st.divider()
    st.markdown("### Balance")
    st.markdown(f'<div class="wallet">₹{st.session_state.wallet}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="coin">🪙 {st.session_state.coins} SuperCoins</div>',unsafe_allow_html=True)

# User-supplied local product cover images.
LOCAL_PRODUCT_IMAGES = {
    "clinic plus shampoo": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\clinic plus shampoo\1-strong-and-long-health-hair-shampoo-1-liter-clinic-plus-original-imagyz48yh6eegex.jpg",
    "dove hairfall rescue": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\Dove HairFall Rescue\7143zC6D9vL._AC_UF350,350_QL80_.jpg",
    "denver perfume": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\Denver perfume\slide_1_132ba508-ccbc-47e9-98b9-2ad780ae646f.jpg",
    "livon serum": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\Livon serum\50ml-livon-hair-serum-500x500.jpg",
    "lizol floor cleaner": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\Lizol floor cleaner\ew1zwha9dziukigmwtlm.avif",
    "mamaearth rosemary water": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\Mamaearth Rosemary Water\610PBbsqFkL._AC_UF1000,1000_QL80_.jpg",
    "nivya body milk": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\nivya body mik\400-nourishing-body-milk-for-very-dry-skin-with-almond-oil-enriched-0-original-imagjvg95w5khfwg.jpg",
    "parachute coconut oil": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\parachute hair oil\parachute-100-pure-coconut-oil-300-ml-bottle-3-1654233076.webp",
    "whitetone face powder": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\whitetone face powder\OIP (8).jpeg",
    "wottagirl perfume": r"C:\Users\jamee\OneDrive\Desktop\RECYZA\Dataset\wotta girl perfume\61j9yQJDYXL._SX679_.jpg",
}

def local_image_for_product(p):
    name = p.get("name", "").strip().lower()
    ai_class = (p.get("ai_class") or "").strip().lower()

    aliases = {
        "clinic plus shampoo": "clinic plus shampoo",
        "dove hairfall rescue": "dove hairfall rescue",
        "denver perfume": "denver perfume",
        "livon serum": "livon serum",
        "lizol floor cleaner": "lizol floor cleaner",
        "mamaearth rosemary water": "mamaearth rosemary water",
        "nivya body mik": "nivya body milk",
        "nivya body milk": "nivya body milk",
        "parachute coconut oil": "parachute coconut oil",
        "parachute hair oil": "parachute coconut oil",
        "whitetone face powder": "whitetone face powder",
        "wottagirl perfume": "wottagirl perfume",
        "wotta girl perfume": "wottagirl perfume",
    }

    key = aliases.get(ai_class) or aliases.get(name)
    if key:
        path = Path(LOCAL_PRODUCT_IMAGES[key])
        if path.exists():
            return str(path)
    return None

def product_card(p,key):
    st.markdown('<div class="product-card">',unsafe_allow_html=True)

    local_image = local_image_for_product(p)

    if local_image:
        try:
            st.image(local_image, use_container_width=True)
        except Exception:
            local_image = None

    if not local_image:
        meta=fetch_meta(p["url"])
        if meta["image"]:
            st.image(meta["image"],use_container_width=True)
        else:
            st.info("Product cover image unavailable. Use View original product.")

    st.markdown(
        f'<div class="product-name">{html.escape(clean_name(p["name"]))}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<span class="ai-tag">♻️ AI recyclable</span>'
        if p.get("ai_class")
        else '<span class="ai-tag">Marketplace product</span>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="price">₹{price(p)}</div>',unsafe_allow_html=True)

    if st.button("Add to cart",key=key,use_container_width=True):
        add_to_cart(p)

    st.link_button("View original product",p["url"],use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

if st.session_state.page=="Home":
    st.markdown("## How RECYZA works")
    a,b,c=st.columns(3)
    a.markdown('<div class="panel"><h3>🛍️ Shop</h3><p>Browse the real product links you supplied.</p></div>',unsafe_allow_html=True)
    b.markdown('<div class="panel"><h3>♻️ Recycle</h3><p>Open My Orders and press the visible Recycle Product button after delivery.</p></div>',unsafe_allow_html=True)
    c.markdown('<div class="panel"><h3>🤖 AI Verify</h3><p>Your 10-class trained RECYZA model verifies the uploaded product.</p></div>',unsafe_allow_html=True)
    st.markdown("## Featured AI-recyclable products")
    featured=[p for p in PRODUCTS if p.get("ai_class")][:10]
    for start in range(0,len(featured),5):
        cols=st.columns(5)
        for j,p in enumerate(featured[start:start+5]):
            with cols[j]: product_card(p,f"home_{start}_{j}")

elif st.session_state.page=="Shop":
    st.markdown("## 🛍️ Shop")
    q=st.text_input("Search products",placeholder="Search perfume, shampoo, clothes, grocery...")
    filt=[p for p in PRODUCTS if not q or q.lower() in p["name"].lower()]
    st.caption(f"{len(filt)} products from the supplied catalog.")
    for start in range(0,len(filt),4):
        cols=st.columns(4)
        for j,p in enumerate(filt[start:start+4]):
            with cols[j]: product_card(p,f"shop_{start}_{j}")

elif st.session_state.page=="Cart":
    st.markdown("## 🛒 Cart")
    if not st.session_state.cart: st.info("Cart is empty.")
    else:
        total=0
        for i,p in enumerate(st.session_state.cart):
            total+=price(p)
            with st.container(border=True):
                c1,c2,c3=st.columns([5,2,1])
                c1.markdown(f"### {clean_name(p['name'])}")
                c2.markdown(f"### ₹{price(p)}")
                if c3.button("✕",key=f"remove_{i}"): st.session_state.cart.pop(i); st.rerun()
        st.markdown(f"## Total: ₹{total}")
        st.markdown("### Demo checkout")
        name=st.text_input("Customer name"); phone=st.text_input("Phone"); address=st.text_area("Delivery address")
        pay=st.radio("Payment",["Cash on Delivery","Demo UPI"])
        if st.button("Place order",use_container_width=True):
            if not name or not phone or not address: st.error("Enter name, phone and address.")
            else:
                for p in st.session_state.cart:
                    st.session_state.orders.append({"id":f"RCZ{1001+len(st.session_state.orders)}","product":p,"status":"Delivered","payment":pay,"customer":name,"phone":phone,"address":address})
                st.session_state.cart=[]; st.success("Order placed. Demo orders are marked Delivered so the recycle workflow can be demonstrated."); go("My Orders")

elif st.session_state.page=="My Orders":
    st.markdown("## 📦 My Orders")
    if not st.session_state.orders: st.info("No orders yet.")
    for i,o in enumerate(st.session_state.orders):
        p=o["product"]
        st.markdown('<div class="order-card">',unsafe_allow_html=True)
        st.markdown(f"### 🧾 {o['id']}")
        st.markdown(f'<div class="delivered">Status: <b>{o["status"]}</b> • Payment: {html.escape(o["payment"])}</div>',unsafe_allow_html=True)
        st.markdown(f"**{clean_name(p['name'])}** — ₹{price(p)}")
        if p.get("ai_class"):
            st.success(f"♻️ AI recycling supported: **{p['ai_class']}**")
            if st.button("♻️ Recycle Product",key=f"recycle_{i}",use_container_width=True):
                st.session_state.selected_order=i; st.session_state.recycle_result=None; go("Recycle Center")
        else:
            st.warning("Your current 10-class model does not visually verify this product.")
            st.link_button("View original product",p["url"],use_container_width=True)
        st.markdown("</div>",unsafe_allow_html=True)

elif st.session_state.page=="Recycle Center":
    st.markdown("## ♻️ Recycle Center")
    if st.session_state.selected_order is None: st.info("Open My Orders and click ♻️ Recycle Product.")
    else:
        o=st.session_state.orders[st.session_state.selected_order]; p=o["product"]; expected=p["ai_class"]
        st.markdown(f'<div class="panel"><h2>AI recycling verification</h2><p><b>Order:</b> {o["id"]}</p><p><b>Ordered:</b> {html.escape(p["name"])}</p><p><b>Expected model class:</b> {html.escape(expected)}</p></div>',unsafe_allow_html=True)
        up=st.file_uploader("Upload a clear product image",type=["jpg","jpeg","png","webp"])
        if up: st.image(up,caption="Uploaded product",width=360)
        if up and st.button("🤖 Verify with RECYZA AI",use_container_width=True):
            try:
                preds=predict(up); st.session_state.recycle_result={"expected":expected,"preds":preds}
            except Exception as e: st.error(str(e))
        r=st.session_state.recycle_result
        if r:
            st.markdown("### AI predictions")
            cs=st.columns(3)
            for i,(cls,prob) in enumerate(r["preds"]): cs[i].metric(f"Top {i+1}",cls,f"{prob*100:.2f}%")
            top,conf=r["preds"][0]
            if top==r["expected"]:
                st.markdown(f'<div class="verified"><h2>✅ Product Verified</h2><p>Ordered: <b>{html.escape(r["expected"])}</b></p><p>AI detected: <b>{html.escape(top)}</b></p><p>Confidence: <b>{conf*100:.2f}%</b></p></div>',unsafe_allow_html=True)
                st.markdown("## 🎁 Choose ONE reward")
                c1,c2=st.columns(2)
                with c1:
                    st.markdown('<div class="reward-card"><h3>💰 Money Credit</h3><div class="wallet">₹50</div><p>Project wallet credit</p></div>',unsafe_allow_html=True)
                    if st.button("Claim ₹50 Money Credit",key="claim_money",use_container_width=True): st.session_state.wallet+=50; st.success("₹50 credited to your RECYZA wallet!")
                with c2:
                    st.markdown('<div class="reward-card"><h3>🪙 SuperCoins</h3><div class="coin">500</div><p>Project loyalty coins</p></div>',unsafe_allow_html=True)
                    if st.button("Claim 500 SuperCoins",key="claim_coins",use_container_width=True): st.session_state.coins+=500; st.success("500 SuperCoins added!")
            else:
                st.markdown(f'<div class="rejected"><h2>❌ Product Not Verified</h2><p>Ordered: <b>{html.escape(r["expected"])}</b></p><p>AI detected: <b>{html.escape(top)}</b> ({conf*100:.2f}%)</p><p>Upload a clear photo of the same ordered product. Rewards are available only after a matching AI prediction.</p></div>',unsafe_allow_html=True)

elif st.session_state.page=="Rewards":
    st.markdown("## 💰 Rewards")
    c1,c2=st.columns(2)
    c1.markdown(f'<div class="reward-card"><h3>💰 Money Credit</h3><div class="wallet">₹{st.session_state.wallet}</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="reward-card"><h3>🪙 SuperCoins</h3><div class="coin">{st.session_state.coins}</div></div>',unsafe_allow_html=True)
    st.markdown("### Reward flow")
    st.write("Buy → Delivered → ♻️ Recycle Product → Upload image → AI verification → Choose Money Credit OR SuperCoins.")

st.markdown('<div class="footer">RECYZA • AI-powered product verification for smarter recycling ♻️<br>Retailer links are the original links supplied for this project. Prices shown inside the demo are project checkout values.</div>',unsafe_allow_html=True)
