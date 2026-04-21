import streamlit as st
import pandas as pd
import plotly.express as px
import pytz

# Konfigurasi Halaman
st.set_page_config(page_title="SSS App Report", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQi_eM3FiQmBIFHkGLmvI6IZIAec4I3cqdWoF73oW9SA_tJJYjduWKSwdG4xsX5sG3Edr_99cAt76jp/pub?output=csv"

def load_data():
    # Load data dari link CSV
    data = pd.read_csv(SHEET_URL)
    
    # Bersihkan spasi di nama kolom jika ada
    data.columns = data.columns.str.strip()
    
    # Pre-processing data: Ubah '-' jadi 0 dan pastikan tipe data numeric
    cols_to_fix = ['Install', 'Conversion_Rate', 'DAU']
    for col in cols_to_fix:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col].astype(str).replace('-', '0'), errors='coerce').fillna(0)
    
    # LOGIKA AUTO-RANK: Urutkan berdasarkan Install terbanyak (descending)
    data = data.sort_values(by='Install', ascending=False).reset_index(drop=True)
    
    # Isi kolom Rank berdasarkan urutan install (1, 2, 3...)
    data['Rank'] = data.index + 1
    
    return data

try:
    df = load_data()

    # --- HEADER ---
    st.title("Dashboard Performa Aplikasi")
    st.subheader("Suwondo Sigit Solution")
    timezone = pytz.timezone("Asia/Jakarta")
    now_jakarta = pd.Timestamp.now(tz=timezone)
    st.markdown(f"**Update terakhir:** {now_jakarta.strftime('%Y-%m-%d %H:%M')} WIB")

    # --- SIDEBAR ---
    st.sidebar.header("Filter Laporan")
    selected_apps = st.sidebar.multiselect(
        "Pilih Aplikasi:",
        options=df['Application'].unique(),
        default=df['Application'].unique()
    )

    # Filter DataFrame berdasarkan pilihan user
    df_filtered = df[df['Application'].isin(selected_apps)]

    if not df_filtered.empty:
        # --- KPI METRICS ---
        col1, col2, col3 = st.columns(3)
        
        avg_conv = df_filtered['Conversion_Rate'].mean()
        avg_dau = df_filtered['DAU'].mean()
        top_app = df_filtered.loc[df_filtered['Install'].idxmax(), 'Application']

        col1.metric("Avg Conversion Rate", f"{avg_conv:.2f}%")
        col2.metric("Avg Daily Active (DAU)", f"{avg_dau:,.1f}")
        col3.metric("Top App (By Install)", top_app)
        
        st.markdown("---")

        # --- VISUALISASI ---
        left_col, right_col = st.columns(2)

        with left_col:
            # Chart Install (Horizontal Bar)
            # Diurutkan berdasarkan Install agar visualnya rapi
            fig_install = px.bar(
                df_filtered, 
                x='Install', 
                y='Application', 
                orientation='h',
                title="Peringkat Installasi Aplikasi",
                color='Install',
                color_continuous_scale='Blues',
                text_auto='.2s'
            )
            fig_install.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_install, use_container_width=True)

        with right_col:
            # Chart Conversion Rate (Line/Trend)
            fig_conv = px.line(
                df_filtered.sort_values('Rank'), 
                x='Application', 
                y='Conversion_Rate', 
                markers=True,
                title="Perbandingan Conversion Rate",
                line_shape="spline"
            )
            st.plotly_chart(fig_conv, use_container_width=True)

        # --- TABEL DETAIL ---
        st.write("### Detail Laporan (Rank 1 = Install Terbanyak)")
        # Menampilkan kolom sesuai urutan yang kamu mau
        display_cols = ['Rank', 'Application', 'Install', 'Conversion_Rate', 'DAU']
        st.dataframe(
            df_filtered[display_cols].sort_values('Rank'), 
            use_container_width=True, 
            hide_index=True
        )
    
    else:
        st.warning("Pilih minimal satu aplikasi di sidebar untuk melihat data.")

except Exception as e:
    st.error(f"Terjadi kesalahan teknis: {e}")
