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
    .uploaded-title {
        font-size: 20px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
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
    st.markdown('<div class="uploaded-title">📝 Files You Have Uploaded</div>', unsafe_allow_html=True)
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

    # ✅ แจ้งผลอัปโหลด และปุ่มไปหน้า Web1
    st.success("🎉 Your CSV files have been uploaded successfully!")
    st.markdown("🟢 You can now move on to the **data analysis** page.")
    st.page_link("pages/Web1.py", label="👉 📊 Go to Analysis Page")
    with st.sidebar:
        st.page_link("pages/Web1.py", label="👉 📊 Proceed to Analysis (Web1)")

    # 🔍 วิเคราะห์ข้อมูลจากไฟล์แรกในรายการ
    first_filename = list(st.session_state["files"].keys())[0]
    df_raw = st.session_state["files"][first_filename]

    # 🔍 หาหัวตาราง (Header Row)
    header_row_idx = None
    for i, row in df_raw.iterrows():
        if row.astype(str).str.contains("Probe ID", case=False, na=False).any():
            header_row_idx = i
            break

    if header_row_idx is not None:
        df_data = df_raw.iloc[header_row_idx + 1:].copy()
        df_data.columns = df_raw.iloc[header_row_idx]
        df_data = df_data.reset_index(drop=True)

        # แปลงคอลัมน์ Diameter (µm) เป็น float
        df_data["Diameter (µm)"] = pd.to_numeric(df_data["Diameter (µm)"], errors='coerce')

        # 🔝 Top 5 Largest Diameters
        top5_max = df_data.sort_values(by='Diameter (µm)', ascending=False).reset_index(drop=True).head(5)
        top5_max = top5_max.rename(columns={'User Defined Label 4': 'Probe name'})
        st.subheader("🔝 Top 5 Largest Diameters")
        st.table(top5_max[['Probe name', 'Diameter (µm)']])

        csv_largest = top5_max[['Probe name', 'Diameter (µm)']].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Largest Diameters CSV",
            data=csv_largest,
            file_name="top_5_largest_diameters.csv",
            mime='text/csv'
        )

        # 🔻 Top 5 Smallest Diameters
        top5_min = df_data.sort_values(by='Diameter (µm)', ascending=True).reset_index(drop=True).head(5)
        top5_min = top5_min.rename(columns={'User Defined Label 4': 'Probe name'})
        st.subheader("🔻 Top 5 Smallest Diameters")
        st.table(top5_min[['Probe name', 'Diameter (µm)']])

        csv_smallest = top5_min[['Probe name', 'Diameter (µm)']].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Smallest Diameters CSV",
            data=csv_smallest,
            file_name="top_5_smallest_diameters.csv",
            mime='text/csv'
        )
    else:
        st.error("❌ ไม่พบ Header Row ที่มีคำว่า 'Probe ID'")

else:
    st.warning("⚠️ No files uploaded yet.")
