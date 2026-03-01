### 🍎 NextDoor: Neighborhood Food Swapping App  

A localized, community-driven web application designed to reduce food waste and strengthen neighborhood ties. This app allows residents to post extra garden harvests, pantry items, or home-cooked meals for their neighbors to claim.
--- 

### ✨ Features
Real-time Postings: Users can easily list items with categories (Vegetables, Fruit, Meals, etc.) via a sidebar form.

Smart Search & Filtering: Find exactly what you need by keyword or category.

WhatsApp Integration: A custom-styled green button that opens a pre-filled chat with the item owner for instant coordination.

Temporary Claiming: Uses Streamlit Session State to allow users to "reserve" items during their browsing session without permanently deleting data.

Persistent Storage: All community data is backed up in a lightweight CSV "database" for easy management.

Modern UI: Custom CSS-styled buttons (Blue for actions, Green for WhatsApp, Grey for Undo) for a professional user experience.

---

### 🛠️ Tech Stack
Python 3.x

Streamlit (Frontend & State Management)

Pandas (Data Handling)

HTML/CSS (Custom UI Injection)
---

### 🚀 How to Run
Clone this repository.

Install requirements: ``pip install streamlit pandas``.

Run the app: ``streamlit run app.py``.
