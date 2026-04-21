import streamlit as st
import sqlite3

# ---------------------------
# 1. DATABASE SETUP
# ---------------------------
# Using :memory: for a fresh start each run; use a filename like 'sop.db' for persistence
conn = sqlite3.connect(":memory:", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")

knowledge_data = [
    ("What is STN Generation?", "STN Generation: IPC creates stock transfer requests."),
    ("What is picklist assignment?", "Picklist Assignment: Tasks assigned to picker."),
    ("What is the picking process?", "Picking Process: Items picked from bins."),
    ("What is packing in Reverse?", "Packing: Items packed into boxes with Box ID."),
    ("What is invoice generation?", "Invoice Generation: Invoice created for shipment."),
    ("What is Flow WMS dispatch?", "Flow WMS dispatch: Stock deducted from system."),
    ("What is TMS dispatch?", "TMS Dispatch: Assigned to vehicle."),
    ("What is In Transit status?", "In Transit: Moving to hub."),
    ("What is Gate Entry?", "Gate Entry: Received at hub."),
    ("What is Putaway?", "Putaway: Stored in bins."),
    ("What is Box Closure?", "Box Closure: Inventory finalized.")
]

cursor.executemany("INSERT INTO knowledge (question, answer) VALUES (?, ?)", knowledge_data)
conn.commit()

# ---------------------------
# 2. APP STATE & LOGIC
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your SOP Assistant. How can I help you with the Reverse process today?"}]

if "step" not in st.session_state:
    st.session_state.step = 0

sop_flow = [q[0] for q in knowledge_data[:5]]

def process_query(q):
    # Query database
    cursor.execute("SELECT answer FROM knowledge WHERE question LIKE ?", (f"%{q}%",))
    res = cursor.fetchone()
    ans = res[0] if res else "I'm sorry, I don't have information on that. Try one of the suggested steps below."
    
    # Append to chat history
    st.session_state.messages.append({"role": "user", "content": q})
    st.session_state.messages.append({"role": "assistant", "content": ans})
    
    # Progression logic: Advance the suggestion flow if the user clicks the current step
    if st.session_state.step < len(sop_flow) and q == sop_flow[st.session_state.step]:
        st.session_state.step += 1

# ---------------------------
# 3. UI LAYOUT
# ---------------------------
st.set_page_config(page_title="Reverse SOP Bot", layout="centered")

st.markdown("""
    <style>
    /* 1. App Background */
    .stApp {
        background-color: #0f172a;
    }
    
    /* 2. Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #1e293b; 
        border: 1px solid #334155; 
        border-radius: 10px;
    }

    /* 3. Force Chat Text to be White */
    [data-testid="stChatMessage"] p {
        color: #ffffff !important;
    }

    /* 4. Fix Buttons: Dark background, white text */
    .stButton>button {
        background-color: #2563eb !important; /* Professional Blue */
        color: #ffffff !important;           /* White Text */
        border: none !important;
        border-radius: 5px !important;
        transition: background-color 0.3s ease;
    }

    /* 5. Button Hover Effect: Lighter blue when mouse is over */
    .stButton>button:hover {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }

    /* 6. Titles and Input Labels */
    h1, h2, h3, .stCaption, label {
        color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# st.title("Reverse SOP Knowledge Bot")

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Render Suggestion Buttons
if st.session_state.step < len(sop_flow):
    st.write("---")
    st.caption("Suggested next steps:")
    cols = st.columns(min(3, len(sop_flow) - st.session_state.step))
    
    # Show the current step and the next 2 steps
    current_suggestions = sop_flow[st.session_state.step : st.session_state.step + 3]
    
    for i, s in enumerate(current_suggestions):
        if i < len(cols):
            if cols[i].button(s, use_container_width=True):
                process_query(s)
                st.rerun()

# User Input Box
if prompt := st.chat_input("Ask about the Reverse SOP process..."):
    process_query(prompt)
    st.rerun()
