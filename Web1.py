import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import chardet
import os
import io
import plotly.express as px

from datetime import datetime

st.set_page_config(
    page_title="CSV Analyzer",
    page_icon="PC_Analysis.ico",   # ✅ ชื่อนี้ตรงกับไฟล์ที่อยู่ในโฟลเดอร์
    layout="centered"
)
st.title("📄 CSV Probe Card Analyzer")

uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file:
    # ตรวจสอบ encoding ก่อนอ่านไฟล์
    raw_bytes = uploaded_file.read()
    result = chardet.detect(raw_bytes)
    encoding = result['encoding']
    uploaded_file.seek(0)
    
    df_raw = pd.read_csv(uploaded_file, header=None, encoding=encoding)

    # หา header row
    header_row_idx = None
    for i, row in df_raw.iterrows():
        if row.astype(str).str.contains("Probe ID", case=False, na=False).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        st.error("❌ 'Probe ID' not found in the CSV file")
    else:
        df_data = df_raw.iloc[header_row_idx:].copy()
        df_data.columns = df_data.iloc[0]
        df_data = df_data[1:]
        for i, row in df_data.iterrows():
            if row.isnull().all() or (row.astype(str).str.strip() == '').all():
                df_data = df_data.loc[:i - 1]
                break
        df_data.reset_index(drop=True, inplace=True)

        # ลบช่องว่างชื่อคอลัมน์ และตั้งชื่อคอลัมน์ที่เป็น NaN หรือซ้ำซ้อน
        df_data.columns = df_data.columns.str.strip()
        df_data.columns = [str(col) if pd.notna(col) else f"Unnamed_{i}" for i, col in enumerate(df_data.columns)]
        df_data = df_data.loc[:, ~df_data.columns.duplicated()]
        df_data = df_data.dropna(axis=1, how='all')

# แปลงคอลัมน์เป้าหมายเป็นตัวเลข
        df_data['Diameter (µm)'] = pd.to_numeric(df_data.get('Diameter (µm)'), errors='coerce')
        df_data['Planarity (µm)'] = pd.to_numeric(df_data.get('Planarity (µm)'), errors='coerce')


        st.success("✅ Data loaded and processed successfully")
        st.dataframe(df_data)
        # Sort ตาม Probe ID ก่อน
        # ✅ แปลง Probe ID เป็นตัวเลข แล้วจัดการค่า NaN ถ้ามี
        df_data['Probe ID'] = pd.to_numeric(df_data['Probe ID'], errors='coerce')
        df_data = df_data.dropna(subset=['Probe ID'])
        df_sorted = df_data.sort_values(by='Probe ID').reset_index(drop=True)

        x_index = df_sorted.index
        x_labels = df_sorted['Probe ID']
        y_diameter = df_sorted['Diameter (µm)']

        # ----------- Plotly Interactive Diameter Plot -----------
        fig_dia = px.scatter(
        df_sorted,
        x='Probe ID',
        y='Diameter (µm)',
        title="Diameter vs Probe ID",
        labels={"Diameter (µm)": "Diameter (µm)", "Probe ID": "Probe ID"},
        template='simple_white'
         )
        # ✅ เพิ่มเส้นแนวนอน UCL / LCL แบบชัดเจน
        fig_dia.add_hline(
        y=24,
        line_dash="solid",
        line_color="red",
        line_width=2,
        annotation_text="UCL = 24",
        annotation_position="top left",
        layer="above"
        )
        fig_dia.add_hline(
        y=14,
        line_dash="solid",
        line_color="red",
        line_width=2,
        annotation_text="LCL = 14",
        annotation_position="bottom left",
        layer="above"
)


        # ✅ เปิดเส้น Grid
        fig_dia.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
)

        st.plotly_chart(fig_dia, use_container_width=True)

    

       
        
        plt.close()

        y_planarity = df_sorted['Planarity (µm)']  # ✅ เพิ่มบรรทัดนี้


        # Planarity Plot
        # ----------- Plotly Interactive Planarity Plot -----------
        fig_plan = px.scatter(
        df_sorted,
        x='Probe ID',
        y='Planarity (µm)',
        title="Planarity vs Probe ID",
        labels={"Planarity (µm)": "Planarity (µm)", "Probe ID": "Probe ID"},
        template='simple_white'
        
)
        st.plotly_chart(fig_plan, use_container_width=True)
         # ✅ เพิ่ม Grid
        fig_plan.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
       )
        plt.close()
        # Top 5 Max Diameter
        top5_max = df_data.sort_values(by='Diameter (µm)', ascending=False).reset_index(drop=True).head(5)[['User Defined Label 4', 'Diameter (µm)']]

        top5_max = top5_max.rename(columns={'User Defined Label 4': 'Probe name'})
        st.subheader("🔝 Top 5 Largest Diameters")
        st.table(top5_max)

        # Top 5 Min Diameter
        top5_min = df_data.sort_values(by='Diameter (µm)', ascending=True).reset_index(drop=True).head(5)[['User Defined Label 4', 'Diameter (µm)']]

        top5_min = top5_min.rename(columns={'User Defined Label 4': 'Probe name'})
        st.subheader("🔻 Top 5 Smallest Diameters")
        st.table(top5_min)

        # บันทึกเป็น Excel
        if st.button("💾 Download Excel File"):
            towrite = io.BytesIO()
            df_data.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            st.download_button(
                label="📥 Download Excel File",
                data=towrite,
                file_name=f"analyzed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
