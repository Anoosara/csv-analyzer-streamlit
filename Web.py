import streamlit as st
import pandas as pd
import chardet

# 🔧 ปรับ CSS ให้กล่อง Upload ดูเล็กลงและเรียบร้อยขึ้น
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

# 🔹 เตรียม session_state สำหรับเก็บไฟล์
if "files" not in st.session_state:
    st.session_state["files"] = {}

# 🔹 โหลดไฟล์เข้า session_state
if uploaded_files:
    for file in uploaded_files:
        raw_bytes = file.read()
        encoding = chardet.detect(raw_bytes)["encoding"]
        file.seek(0)
        df = pd.read_csv(file, header=None, encoding=encoding)
        st.session_state["files"][file.name] = df

# 🔹 แสดงรายการไฟล์ที่อัปโหลดแล้ว พร้อมปุ่มลบ
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

    # 🔁 ลบไฟล์แล้วโหลดหน้าใหม่
    if delete_file:
        del st.session_state["files"][delete_file]
        st.rerun()

    # ✅ แจ้งผลการอัปโหลดและลิงก์ไปหน้า Web1
    st.success("🎉 Your CSV files have been uploaded successfully!")
    st.markdown("🟢 You can now move on to the **data analysis** page.")
    st.page_link("pages/Web1.py", label="📊 Proceed to Analysis (Web1)", icon="➡️")

else:
    st.warning("⚠️ No files uploaded yet.")
