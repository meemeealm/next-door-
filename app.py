import streamlit as st
import pandas as pd
from datetime import datetime
import os
import random
from database import init_db, add_item, get_all_items, toggle_claim, get_user_items
import pydeck as pdk

# 2. Page Configuration
st.set_page_config(page_title="Neighborhood Food Swap", page_icon="🍎")
st.title("🍎 NextDoor")

init_db()

# Fetch data from DB
data = get_all_items()


# --- CUSTOM CSS ---
st.markdown("""
    
            
<style>
    /* Remove default Streamlit padding from columns */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Force all buttons to same height and remove top margins */
    .stButton, .wa-btn {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        width: 100% !important;
    }

    /* Style for both Streamlit buttons and the Link button */
    /* Ensure both button types have the exact same structural footprint */
    .claim-btn div.stButton > button, 
    .wa-btn {
        height: 42px !important;
        line-height: 42px !important; /* Centers text vertically in the link */
        padding: 0px 15px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        font-size: 14px !important;
        border-radius: 8px !important; /* Matching corners looks cleaner */
    }

    /* Fix for the WhatsApp link specifically */
    .wa-btn {
        display: inline-flex !important; /* Changed from flex to inline-flex */
        width: 100%;
        text-align: center;
    }

    /* Remove Streamlit's default widget margin which pushes buttons down */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        padding-top: 0px !important;
    }

    /* Colors */
    .claim-btn div.stButton > button { background-color: #007bff !important; color: white !important; }
    .undo-btn div.stButton > button { background-color: #6c757d !important; color: white !important; }
    .wa-btn { background-color: #25D366 !important; color: white !important; font-size: 14px; }
    
    /* Hover effects */
    .wa-btn:hover { background-color: #128C7E !important; }
</style>
""", unsafe_allow_html=True)

st.info("💡 Pro-tip: If you claim an item, please message the owner to coordinate pickup!")

# Sidebar for Posting

# --- SIDEBAR START ---
st.sidebar.header("Post an Item")

# 1. THE FORM 
with st.sidebar.form("post_form", clear_on_submit=True):
    user = st.text_input("Your Name")
    phone = st.text_input("WhatsApp Number (e.g., 60123456789)")
    item = st.text_input("What are you sharing?")
    category = st.selectbox("Category", ["Vegetables", "Fruit", "Cooked Meal", "Herbs", "Other"])
    qty = st.text_input("Quantity")
    submit = st.form_submit_button("Post to Board")

    if submit:
        if user and item and phone:
            # 📍 GENERATE COORDINATES
            # Since the user isn't typing GPS, we generate a point near Bacoor
            # 14.4445, 120.9473 is your neighborhood center
            lat = 14.4445 + random.uniform(-0.01, 0.01)
            lon = 120.9473 + random.uniform(-0.01, 0.01)

            # 💾 DATABASE CALL
            # Make sure the order matches your add_item function in database.py
            from database import add_item
            add_item(user, phone, item, category, qty, lat, lon)
            
            st.success(f"✅ {item} added to the map!")
            st.rerun() # Refresh the app to show the new item on the map/list
        else:
            st.error("Please fill in Name, Item, and Phone!")

st.sidebar.divider()

# 2. THE MANAGEMENT SECTION (Uses 'name' from the form above)
st.sidebar.subheader("👤 Manage My Postings")

# If the user typed a name in the form, let's show their posts automatically
# OR they can type a specific name to search
manage_lookup = st.sidebar.text_input("Enter name to manage posts", value=user if user else "")

if manage_lookup:
    my_df = get_user_items(manage_lookup)
    
    if not my_df.empty:
        st.sidebar.caption(f"Postings for '{manage_lookup}'")
        for index, row in my_df.iterrows():
            with st.sidebar.expander(f"📦 {row['item']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    t_label = "Free" if row['status'] == 'Reserved' else "Reserve"
                    if st.button(t_label, key=f"tgl_{row['id']}", use_container_width=True):
                        toggle_claim(row['id'], row['status'])
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{row['id']}", use_container_width=True):
                        from database import delete_item
                        delete_item(row['id'])
                        st.rerun()
    else:
        st.sidebar.info("No postings found.")
# --- SIDEBAR END ---

# 4. Search & Filter Section

# Fetch data from DB
df = get_all_items()

# FORCE the sort right here
if not df.empty:
    # Convert 'posted' to actual datetime objects so Pandas knows how to sort them
    df['posted'] = pd.to_datetime(df['posted'])
    # Sort by newest first
    df = df.sort_values(by='posted', ascending=False)

df = get_all_items() # Pulls from SQLite as a DataFrame
st.divider()
search_col, cat_col = st.columns([2, 1])

with search_col:
    search_term = st.text_input("🔍 Search the board...", placeholder="e.g. Eggs, Basil")

with cat_col:
    categories = ["All", "Vegetables", "Fruit", "Cooked Meal", "Herbs", "Other"]
    selected_cat = st.selectbox("Filter by Category", categories)

# Apply Filters
# Apply Filters
if search_term:
    # Change 'Item' to 'item' and 'User' to 'user'
    df = df[df['item'].str.contains(search_term, case=False) | 
            df['user'].str.contains(search_term, case=False)]

if selected_cat != "All":
    # Change 'Category' to 'category'
    df = df[df['category'] == selected_cat]

# 5. Initialize Temporary Memory (Session State)
# This list resets to empty every time the app server restarts
if 'claimed_indices' not in st.session_state:
    st.session_state.claimed_indices = []

# Create the tabs
tab1, tab2 = st.tabs(["📋 List View", "📍 Interactive Map"])

# 6. The Main Display Loop
with tab1:
    if not df.empty:
        for index, row in df.iterrows():
            # Check status from the DATABASE column, not session_state
            is_claimed = (row['status'] == 'Reserved')
            
            cols = st.columns([3, 1, 1], vertical_alignment="center")
            
            with cols[0]:
                if is_claimed:
                    st.markdown(f"### ~~{row['item']}~~")
                    st.caption(f"🚩 Reserved by a neighbor (Owner: {row['user']})")
                else:
                    st.markdown(f"### {row['item']}")
                    st.write(f"**Owner:** {row['user']} | **Qty:** {row['quantity']}")

            with cols[1]:
                wa_link = f"https://wa.me/{row['phone']}?text=Hi%20{row['user']},%20is%20the%20{row['item']}%20still%20available?"
                st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">💬 WhatsApp</a>', unsafe_allow_html=True)

            with cols[2]:
                # The Button now talks to the DB
                button_label = "Undo ↩️" if is_claimed else "Claim"
                button_key = f"btn_{row['id']}" # Use the SQL ID as the key
                
                if st.button(button_label, key=button_key):
                    from database import toggle_claim
                    toggle_claim(row['id'], row['status'])
                    st.rerun() # Refresh to show the new status to everyone
            st.divider()


with tab2:
    st.subheader("📍 Neighborhood Food Map")
    
    # Filter for Available items
    map_df = df[df['status'] == 'Available'].copy()

    # Define colors (R, G, B, Alpha)
    CATEGORY_COLORS = {
        "Vegetables": [34, 139, 34, 160],   # Forest Green
        "Fruit": [255, 165, 0, 160],        # Orange
        "Cooked Meal": [220, 20, 60, 160],  # Crimson Red
        "Herbs": [124, 252, 0, 160],       # Lawn Green
        "Other": [128, 128, 128, 160]      # Gray
    }

    if not map_df.empty:
        # Create a new column 'color' based on the category
        # If category isn't in our dict, default to Gray
        map_df['color'] = map_df['category'].map(lambda x: CATEGORY_COLORS.get(x, [128, 128, 128, 160]))

        view_state = pdk.ViewState(
            latitude=map_df['lat'].mean(),
            longitude=map_df['lon'].mean(),
            zoom=12,
            pitch=0,
        )

        layer = pdk.Layer(
            'ScatterplotLayer',
            data=map_df,
            get_position='[lon, lat]',
            get_color='color',  # Tell Pydeck to look at our new 'color' column
            get_radius=150,
            pickable=True,
        )

        st.pydeck_chart(pdk.Deck(
        # This uses CartoDB's Positron tiles which are reliable and free
        map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            "html": "<b>{item}</b><br/>Cat: {category}<br/>Owner: {user}",
            "style": {"color": "white", "backgroundColor": "#333"}
        }
))
        
        # Add a small Legend so users know what the colors mean
        st.write("### Legend")
        cols = st.columns(len(CATEGORY_COLORS))
        for i, (cat, color) in enumerate(CATEGORY_COLORS.items()):
            cols[i].markdown(f'<span style="color:rgb({color[0]},{color[1]},{color[2]})">●</span> {cat}', unsafe_allow_html=True)
    else:
        st.info("No active locations to show.")