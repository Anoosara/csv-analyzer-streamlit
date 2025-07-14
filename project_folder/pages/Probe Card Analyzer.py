
import streamlit as st
import pandas as pd
import chardet
import io
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(
    page_title="CSV Analyzer",
    page_icon="PC_Analysis.ico",
    layout="centered"
)

st.title("📄 CSV Probe Card Analyzer")

def save_table_as_image(df, title, filename):
    fig, ax = plt.subplots(figsize=(6, 2 + 0.3 * len(df)))
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    plt.title(title, fontsize=12)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    st.download_button(
        label=f"📷 Download {filename}",
        data=buf.getvalue(),
        file_name=f"{filename}.png",
        mime="image/png"
    )
    buf.close()
    plt.close()

if "files" not in st.session_state or not st.session_state["files"]:
    st.warning("⚠️ No files uploaded. Please upload from Main page.")
else:
    file_dict = st.session_state["files"]
    tabs = st.tabs(list(file_dict.keys()))

    for tab, filename in zip(tabs, file_dict):
        with tab:
            st.subheader(f"📂 File: {filename}")

            if st.button(f"🗑️ Remove this file", key=f"remove_{filename}"):
                del st.session_state["files"][filename]
                st.rerun()

            raw_bytes = file_dict[filename].read()
            encoding = chardet.detect(raw_bytes)['encoding']
            file_dict[filename].seek(0)

            lines = raw_bytes.decode(encoding).splitlines()
            header_row_idx = None
            for i, line in enumerate(lines):
                if "Probe ID" in line:
                    header_row_idx = i
                    break

            if header_row_idx is None:
                st.error("❌ 'Probe ID' not found in the CSV file")
                continue

            file_dict[filename].seek(0)
            df_data = pd.read_csv(file_dict[filename], skiprows=header_row_idx, encoding=encoding)

            df_data.columns = df_data.iloc[0]
            df_data = df_data[1:]

            for i, row in df_data.iterrows():
                if row.isnull().all() or (row.astype(str).str.strip() == '').all():
                    df_data = df_data.loc[:i - 1]
                    break

            df_data.reset_index(drop=True, inplace=True)
            df_data.columns = df_data.columns.str.strip()
            df_data.columns = [str(col) if pd.notna(col) else f"Unnamed_{i}" for i, col in enumerate(df_data.columns)]
            df_data = df_data.loc[:, ~df_data.columns.duplicated()]
            df_data = df_data.dropna(axis=1, how='all')

            df_data['Diameter (µm)'] = pd.to_numeric(df_data.get('Diameter (µm)'), errors='coerce')
            df_data['Planarity (µm)'] = pd.to_numeric(df_data.get('Planarity (µm)'), errors='coerce')
            df_data['Probe ID'] = pd.to_numeric(df_data.get('Probe ID'), errors='coerce')
            df_data = df_data.dropna(subset=['Probe ID'])

            st.success("✅ Data loaded and processed successfully")
            st.dataframe(df_data)

            df_sorted = df_data.sort_values(by='Probe ID').reset_index(drop=True)

            fig_dia = px.scatter(
                df_sorted,
                x='Probe ID',
                y='Diameter (µm)',
                title="Diameter vs Probe ID",
                labels={"Diameter (µm)": "Diameter (µm)", "Probe ID": "Probe ID"},
                template='simple_white'
            )
            fig_dia.add_hline(y=24, line_dash="solid", line_color="red", line_width=2,
                              annotation_text="UCL = 24", annotation_position="top left")
            fig_dia.add_hline(y=14, line_dash="solid", line_color="red", line_width=2,
                              annotation_text="LCL = 14", annotation_position="bottom left")
            fig_dia.update_layout(xaxis=dict(showgrid=True), yaxis=dict(showgrid=True), plot_bgcolor='white')
            st.plotly_chart(fig_dia, use_container_width=True)

            fig_plan = px.scatter(
                df_sorted,
                x='Probe ID',
                y='Planarity (µm)',
                title="Planarity vs Probe ID",
                labels={"Planarity (µm)": "Planarity (µm)", "Probe ID": "Probe ID"},
                template='simple_white'
            )
            fig_plan.update_layout(xaxis=dict(showgrid=True), yaxis=dict(showgrid=True), plot_bgcolor='white')
            st.plotly_chart(fig_plan, use_container_width=True)

            top5_max = df_data.sort_values(by='Diameter (µm)', ascending=False).reset_index(drop=True).head(5)
            top5_max = top5_max.rename(columns={'User Defined Label 4': 'Probe name'})
            st.subheader("🔝 Top 5 Largest Diameters")
            st.table(top5_max[['Probe ID', 'Probe name', 'Diameter (µm)']])
            save_table_as_image(top5_max[['Probe ID', 'Probe name', 'Diameter (µm)']], "Top 5 Largest Diameters", "top5_largest_diameters")

            top5_min = df_data.sort_values(by='Diameter (µm)', ascending=True).reset_index(drop=True).head(5)
            top5_min = top5_min.rename(columns={'User Defined Label 4': 'Probe name'})
            st.subheader("🔻 Top 5 Smallest Diameters")
            st.table(top5_min[['Probe ID', 'Probe name', 'Diameter (µm)']])
            save_table_as_image(top5_min[['Probe ID', 'Probe name', 'Diameter (µm)']], "Top 5 Smallest Diameters", "top5_smallest_diameters")

            if st.button("💾 Download Excel File", key=f"download_{filename}"):
                towrite = io.BytesIO()
                df_data.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                st.download_button(
                    label="📥 Download Excel File",
                    data=towrite,
                    file_name=f"analyzed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
