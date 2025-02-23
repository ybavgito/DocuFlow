import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"  # Ensure FastAPI is running on this URL

# Initialize session state
if "token" not in st.session_state:
    st.session_state["token"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "login"

# Sidebar Navigation
st.sidebar.title("Navigation")
if st.session_state["token"]:
    if st.sidebar.button("Logout"):
        st.session_state["token"] = None
        st.session_state["role"] = None
        st.session_state["page"] = "login"
        st.rerun()

# Login Page
if st.session_state["page"] == "login":
    st.title("🔐 Login to System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["role"] = data["role"]
            st.session_state["page"] = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Go to Sign-up"):
        st.session_state["page"] = "signup"
        st.rerun()

# Signup Page
if st.session_state["page"] == "signup":
    st.title("📝 Register New Account")

    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    new_role = st.selectbox("Select Role", ["admin", "manager", "viewer"])

    if st.button("Register"):
        response = requests.post(f"{API_URL}/register/", json={"username": new_username, "password": new_password, "role": new_role})
        if response.status_code == 200:
            st.success("User registered successfully! Please login.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error(response.json()["detail"])

    if st.button("Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()

# Dashboard
if st.session_state["page"] == "dashboard":
    st.title("📊 Dashboard")
    st.subheader(f"Welcome, {st.session_state['role'].capitalize()}")

    menu = ["Upload Document", "View Documents", "Manage Inventory"]
    choice = st.sidebar.radio("Go to", menu)

    # Upload Document Section
    if choice == "Upload Document":
        st.header("📤 Upload a Document")

        uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_URL}/upload/", files=files)

            if response.status_code == 200:
                doc_data = response.json()
                if "file_id" in doc_data:
                    file_id = doc_data["file_id"]
                elif "id" in doc_data:
                    file_id = doc_data["id"]
                else:
                    file_id = "Unknown"

                st.success(f"✅ File '{file_id}' uploaded successfully!")

                st.subheader("Extracted Content")
                st.text_area("Text Extracted", doc_data["content"], height=200)
                st.subheader("AI-Generated Tags")
                st.write(doc_data["tags"])
            else:
                st.error("❌ File upload failed.")

    # View Documents Section
    elif choice == "View Documents":
        st.header("📂 View Uploaded Documents")

        response = requests.get(f"{API_URL}/documents/")
        if response.status_code == 200:
            documents = response.json()
            if documents:
                for doc in documents:
                    with st.expander(doc["title"]):
                        st.write("**Extracted Content:**")
                        st.text_area("Content", doc["content"], height=200, disabled=True)
                        st.write("**Tags:**", doc["tags"])
            else:
                st.info("No documents found.")
        else:
            st.error("❌ Unable to fetch documents.")

    # Inventory Management Section
    elif choice == "Manage Inventory":
        st.header("📦 Manage Inventory")

        tab1, tab2 = st.tabs(["Add Inventory", "View Inventory"])

        with tab1:
            st.subheader("➕ Add Inventory Item")
            item_name = st.text_input("Item Name")
            item_quantity = st.number_input("Quantity", min_value=0)
            item_reorder_level = st.number_input("Reorder Level", min_value=0)

            if st.button("Add Item"):
                response = requests.post(f"{API_URL}/inventory/", json={"name": item_name, "quantity": item_quantity, "reorder_level": item_reorder_level})
                if response.status_code == 200:
                    st.success("Inventory Item Added Successfully")
                else:
                    st.error("Error adding item.")

        with tab2:
            st.subheader("📋 Inventory List")

            response = requests.get(f"{API_URL}/inventory/")
            if response.status_code == 200:
                inventory_data = response.json()
                if inventory_data:
                    st.table(inventory_data)
                else:
                    st.info("No inventory items found.")
            else:
                st.error("❌ Unable to fetch inventory data.")
