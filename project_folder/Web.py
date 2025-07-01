import streamlit as st
import pandas as pd
import chardet

# 🔧 CSS ปรับสไตล์ให้ดูเรียบร้อย
st.markdown("""
    <style>
    .uploadedFileName {
        font-size: 13px !important;
    }
    .stFileUploader > label {
        font-size: 15px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# 🔹 ตั้งค่าหน้าหลัก
st.set_page_config(page_title="Main Page", layout="centered")
st.title("📁 Upload Multiple CSV Files")

# 🔹 กล่องอัปโหลดหลายไฟล์
uploaded_files = st.file_uploader(
    "📂 Upload CSV files", type=["csv"], accept_multiple_files=True
)

# 🔹 เตรียมพื้นที่เก็บใน session_state
if "files" not in st.session_state:
    st.session_state["files"] = {}

# 🔹 โหลดข้อมูลจากแต่ละไฟล์เข้า session_state
if uploaded_files:
    for file in uploaded_files:
        raw_bytes = file.read()
        encoding = chardet.detect(raw_bytes)["encoding"]
        file.seek(0)
        df = pd.read_csv(file, header=None, encoding=encoding)
        st.session_state["files"][file.name] = df

# 🔹 แสดงรายชื่อไฟล์ และลบได้
if st.session_state["files"]:
    st.subheader("📝 Files You Have Uploaded")
    delete_file = None

    for filename in list(st.session_state["files"].keys()):
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.write(f"📄 {filename}")
        with col2:
            if st.button("🗑️ Remove", key=f"remove_{filename}"):
                delete_file = filename

    # 🔁 ลบแล้วรีโหลด
    if delete_file:
        del st.session_state["files"][delete_file]
        st.rerun()

    # ✅ แจ้งผลอัปโหลด และลิงก์ไปหน้า Web1
    st.success("🎉 Your CSV files have been uploaded successfully!")
    st.markdown("🟢 You can now move on to the **data analysis** page.")

    # 🔘 ปุ่มเปิด Web1 ในแท็บใหม่
    st.markdown("""
        <a href="/Web1" target="_blank">
            <button style='padding: 10px 20px; font-size: 16px; border-radius: 6px; background-color: #4CAF50; color: white; border: none; cursor: pointer;'>
                👉 📊 Open Analysis Page (New Tab)
            </button>
        </a>
    """, unsafe_allow_html=True)

    # 🔸 ลิงก์ใน Sidebar ด้วย
    with st.sidebar:
        st.page_link("pages/Web1.py", label="👉 📊 Proceed to Analysis (Web1)")
        st.markdown("""
            <a href="/Web1" target="_blank">
                <button style='padding: 8px 16px; font-size: 14px; border-radius: 5px; background-color: #2196F3; color: white; border: none; cursor: pointer; width: 100%;'>
                    🧭 Open Web1 in New Tab
                </button>
            </a>
        """, unsafe_allow_html=True)

else:
    st.warning("⚠️ No files uploaded yet.")
