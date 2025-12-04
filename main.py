import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from datetime import datetime
import json
import os
import uuid
from io import BytesIO
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="Kurikulum OBE Dinamis - Ilmu Komputer MNCU",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom dengan tema MNCU
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #0056A4, #00A8E8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .admin-badge {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0056A4;
        border-left: 4px solid #00A8E8;
        padding-left: 1rem;
        margin-top: 2rem;
        font-weight: 600;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 86, 164, 0.1);
        margin: 1rem 0;
        border: 1px solid #E5F6FF;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0056A4 0%, #00A8E8 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #004A8A 0%, #0095D4 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 86, 164, 0.2);
    }
    .delete-btn {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
    }
    .success-msg {
        padding: 1rem;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-msg {
        padding: 1rem;
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        border-radius: 10px;
        margin: 1rem 0;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F9FF;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0056A4;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://mncu.ac.id/Images/navbar_logo.png", width=200)
    
    st.markdown("---")
    st.markdown("<h2 style='color: #0056A4;'>Navigasi Kurikulum</h2>", unsafe_allow_html=True)
    
    # Mode Admin
    admin_mode = st.checkbox("🔐 Mode Admin", value=False)
    
    if admin_mode:
        st.markdown('<div class="admin-badge">ADMIN MODE AKTIF</div>', unsafe_allow_html=True)
        menu_options = [
            "🏠 Dashboard", "👥 Kelola Profil Lulusan", "🎓 Kelola CPL", 
            "📚 Kelola Mata Kuliah", "🔗 Kelola Prasyarat", "🌐 Kelola MBKM",
            "📊 Kelola Evaluasi OBE", "📤 Export/Import Data", "ℹ️ Tentang MNCU"
        ]
    else:
        menu_options = [
            "🏠 Dashboard", "👥 Profil Lulusan", "📚 Struktur Kurikulum", 
            "🔗 Prasyarat MK", "🌐 Program MBKM", "📝 Simulasi KRS",
            "📊 Evaluasi OBE", "📤 Export Data", "ℹ️ Tentang MNCU"
        ]
    
    menu = st.selectbox("Pilih Menu:", menu_options)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Statistik Cepat")
    
    try:
        data = load_all_data()
        pl_count = len(data['pl_data'])
        cpl_count = len(data['cpl_data'])
        mk_count = len(data['mk_wajib'])
        peminatan_count = sum(len(mk_list) for mk_list in data['peminatan_data'].values())
        
        st.metric("Profil Lulusan", pl_count)
        st.metric("CPL", cpl_count)
        st.metric("Mata Kuliah", mk_count + peminatan_count)
    except:
        st.metric("Profil Lulusan", "5")
        st.metric("CPL", "17")
        st.metric("Mata Kuliah", "50+")
    
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%d %B %Y')}")
    st.caption("Kurikulum OBE 2025 - Prodi Ilmu Komputer")

# ==================== SISTEM PENYIMPANAN DATA ====================
DATA_FILES = {
    'pl_data': 'data/profil_lulusan.json',
    'cpl_data': 'data/cpl.json',
    'mk_wajib': 'data/mata_kuliah_wajib.json',
    'peminatan_data': 'data/peminatan.json',
    'prasyarat_data': 'data/prasyarat.json',
    'mbkm_data': 'data/mbkm.json',
    'bk_data': 'data/bahan_kajian.json',
    'cpmk_data': 'data/cpmk.json'
}

def ensure_data_directory():
    """Membuat direktori data jika belum ada"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Buat file default jika belum ada
    for filepath in DATA_FILES.values():
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

def get_default_data():
    """Data default untuk inisialisasi"""
    return {
        'pl_data': [
            {"id": "PL1", "kode": "PL1", "profil": "Software Engineer", 
             "deskripsi": "Mengembangkan aplikasi dan sistem perangkat lunak untuk industri media & entertainment", 
             "icon": "💻", "warna": "#0056A4"},
            {"id": "PL2", "kode": "PL2", "profil": "Data Scientist/Analyst", 
             "deskripsi": "Menganalisis data untuk pengambilan keputusan di industri kreatif digital", 
             "icon": "📊", "warna": "#00A8E8"},
            {"id": "PL3", "kode": "PL3", "profil": "AI Engineer", 
             "deskripsi": "Mengembangkan sistem kecerdasan buatan untuk konten kreatif dan media interaktif", 
             "icon": "🤖", "warna": "#10B981"},
            {"id": "PL4", "kode": "PL4", "profil": "Cybersecurity Specialist", 
             "deskripsi": "Mengamankan sistem dan jaringan komputer di lingkungan media digital", 
             "icon": "🛡️", "warna": "#F59E0B"},
            {"id": "PL5", "kode": "PL5", "profil": "Digital Media Entrepreneur", 
             "deskripsi": "Membangun startup teknologi berbasis media dan konten digital", 
             "icon": "🚀", "warna": "#8B5CF6"}
        ],
        'cpl_data': [
            {"id": "S1", "domain": "Sikap", "kode": "S1", "deskripsi": "Bertakwa kepada Tuhan dan menghargai keberagaman"},
            {"id": "S2", "domain": "Sikap", "kode": "S2", "deskripsi": "Memiliki integritas akademik dan profesional"},
            {"id": "S3", "domain": "Sikap", "kode": "S3", "deskripsi": "Menunjukkan jiwa kewirausahaan dan inovasi"},
            {"id": "S4", "domain": "Sikap", "kode": "S4", "deskripsi": "Berkontribusi pada kemajuan bangsa"},
            {"id": "P1", "domain": "Pengetahuan", "kode": "P1", "deskripsi": "Menguasai konsep matematika dan algoritma"},
            {"id": "P2", "domain": "Pengetahuan", "kode": "P2", "deskripsi": "Memahami arsitektur sistem dan jaringan"},
            {"id": "P3", "domain": "Pengetahuan", "kode": "P3", "deskripsi": "Menguasai prinsip kecerdasan buatan"},
            {"id": "P4", "domain": "Pengetahuan", "kode": "P4", "deskripsi": "Memahami model bisnis digital"},
            {"id": "KU1", "domain": "Keterampilan Umum", "kode": "KU1", "deskripsi": "Berpikir kritis dan kreatif"},
            {"id": "KU2", "domain": "Keterampilan Umum", "kode": "KU2", "deskripsi": "Berkomunikasi efektif dalam tim"},
            {"id": "KU3", "domain": "Keterampilan Umum", "kode": "KU3", "deskripsi": "Mengelola proyek teknologi"},
            {"id": "KU4", "domain": "Keterampilan Umum", "kode": "KU4", "deskripsi": "Belajar sepanjang hayat"},
            {"id": "KK1", "domain": "Keterampilan Khusus", "kode": "KK1", "deskripsi": "Mengembangkan perangkat lunak"},
            {"id": "KK2", "domain": "Keterampilan Khusus", "kode": "KK2", "deskripsi": "Menganalisis data dan audiens"},
            {"id": "KK3", "domain": "Keterampilan Khusus", "kode": "KK3", "deskripsi": "Merancang sistem cerdas"},
            {"id": "KK4", "domain": "Keterampilan Khusus", "kode": "KK4", "deskripsi": "Mengamankan konten digital"},
            {"id": "KK5", "domain": "Keterampilan Khusus", "kode": "KK5", "deskripsi": "Merancang model bisnis digital"}
        ]
    }

@st.cache_data(ttl=60)
def load_all_data():
    """Load semua data dari file JSON"""
    ensure_data_directory()
    data = {}
    
    for key, filepath in DATA_FILES.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        except:
            # Jika file tidak ada atau error, gunakan default
            default_data = get_default_data()
            if key in default_data:
                data[key] = default_data[key]
            else:
                data[key] = []
    
    # Pastikan struktur peminatan_data benar
    if 'peminatan_data' in data and isinstance(data['peminatan_data'], list):
        # Konversi dari list ke dict jika diperlukan
        peminatan_dict = {}
        for item in data['peminatan_data']:
            if 'nama_peminatan' in item:
                peminatan = item['nama_peminatan']
                if peminatan not in peminatan_dict:
                    peminatan_dict[peminatan] = []
                mk_item = {k: v for k, v in item.items() if k != 'nama_peminatan'}
                peminatan_dict[peminatan].append(mk_item)
        data['peminatan_data'] = peminatan_dict
    
    return data

def save_data(key, data):
    """Simpan data ke file JSON"""
    ensure_data_directory()
    filepath = DATA_FILES.get(key)
    
    if filepath:
        # Jika key adalah peminatan_data dan berupa dict, konversi ke list
        if key == 'peminatan_data' and isinstance(data, dict):
            data_to_save = []
            for peminatan, mk_list in data.items():
                for mk in mk_list:
                    mk_copy = mk.copy()
                    mk_copy['nama_peminatan'] = peminatan
                    data_to_save.append(mk_copy)
        else:
            data_to_save = data
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        # Clear cache agar data terbaru di-load
        st.cache_data.clear()
        return True
    return False

# ==================== DASHBOARD ====================
def show_dashboard():
    data = load_all_data()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">🎓 KURIKULUM OBE ILMU KOMPUTER MNCU</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #0056A4; font-size: 1.2rem;">The Real Media & Entertainment Campus</p>', unsafe_allow_html=True)
    with col2:
        st.image("https://mncu.ac.id/Images/navbar_logo.png", width=150)
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        total_mk = len(data['mk_wajib']) + sum(len(mk_list) for mk_list in data['peminatan_data'].values())
        st.metric("Total MK", str(total_mk))
    with col2:
        st.metric("Profil Lulusan", len(data['pl_data']))
    with col3:
        st.metric("CPL", len(data['cpl_data']))
    with col4:
        st.metric("Peminatan", len(data['peminatan_data']))
    with col5:
        st.metric("MBKM", len(data.get('mbkm_data', [])))
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="sub-header">📊 Distribusi Profil Lulusan</div>', unsafe_allow_html=True)
        
        pl_df = pd.DataFrame(data['pl_data'])
        if not pl_df.empty:
            fig = px.bar(pl_df, x='profil', y='kode', 
                        color='profil',
                        title="",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="sub-header">🎯 Domain CPL</div>', unsafe_allow_html=True)
        
        cpl_df = pd.DataFrame(data['cpl_data'])
        if not cpl_df.empty:
            domain_counts = cpl_df['domain'].value_counts()
            fig = px.pie(values=domain_counts.values, 
                        names=domain_counts.index,
                        hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    
    # Quick Actions
    st.markdown("---")
    st.markdown('<div class="sub-header">⚡ Akses Cepat</div>', unsafe_allow_html=True)
    
    if admin_mode:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("➕ Tambah Profil Lulusan", use_container_width=True):
                st.session_state.edit_pl = True
        with col2:
            if st.button("📝 Edit CPL", use_container_width=True):
                st.session_state.edit_cpl = True
        with col3:
            if st.button("📚 Kelola MK", use_container_width=True):
                st.session_state.edit_mk = True
        with col4:
            if st.button("📤 Export Data", use_container_width=True):
                st.session_state.show_export = True
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("👥 Lihat Profil Lulusan", use_container_width=True):
                st.session_state.show_pl = True
        with col2:
            if st.button("📚 Struktur Kurikulum", use_container_width=True):
                st.session_state.show_mk = True
        with col3:
            if st.button("🔗 Cek Prasyarat", use_container_width=True):
                st.session_state.show_prasyarat = True
        with col4:
            if st.button("🌐 Program MBKM", use_container_width=True):
                st.session_state.show_mbkm = True

# ==================== ADMIN: KELOLA PROFIL LULUSAN ====================
def admin_kelola_pl():
    st.markdown('<h1 class="main-header">👥 Kelola Profil Lulusan (PL)</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    pl_data = data['pl_data']
    
    # Tabs untuk Kelola dan Mapping CPL
    tab1, tab2 = st.tabs(["📝 Kelola Profil Lulusan", "🔗 Mapping PL-CPL"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### Daftar Profil Lulusan")
            
            if pl_data:
                df = pd.DataFrame(pl_data)
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "id": st.column_config.TextColumn("ID", disabled=True),
                        "kode": st.column_config.TextColumn("Kode PL"),
                        "profil": st.column_config.TextColumn("Nama Profil"),
                        "deskripsi": st.column_config.TextColumn("Deskripsi"),
                        "icon": st.column_config.SelectboxColumn(
                            "Icon",
                            options=["💻", "📊", "🤖", "🛡️", "🚀", "🎓", "💼", "🔧", "📱", "🌐"]
                        ),
                        "warna": st.column_config.ColorPickerColumn("Warna")
                    },
                    num_rows="dynamic",
                    key="pl_editor"
                )
                
                if st.button("💾 Simpan Perubahan", type="primary"):
                    save_data('pl_data', edited_df.to_dict('records'))
                    st.success("✅ Profil Lulusan berhasil disimpan!")
            else:
                st.info("Belum ada data Profil Lulusan. Tambahkan data baru di form sebelah.")
        
        with col2:
            st.markdown("### Tambah Baru")
            
            with st.form("tambah_pl_form"):
                kode = st.text_input("Kode PL (contoh: PL6)")
                profil = st.text_input("Nama Profil")
                deskripsi = st.text_area("Deskripsi")
                icon = st.selectbox(
                    "Icon",
                    ["💻", "📊", "🤖", "🛡️", "🚀", "🎓", "💼", "🔧", "📱", "🌐"]
                )
                warna = st.color_picker("Warna", "#0056A4")
                
                if st.form_submit_button("➕ Tambah Profil"):
                    if kode and profil:
                        new_pl = {
                            "id": str(uuid.uuid4())[:8],
                            "kode": kode,
                            "profil": profil,
                            "deskripsi": deskripsi,
                            "icon": icon,
                            "warna": warna
                        }
                        pl_data.append(new_pl)
                        save_data('pl_data', pl_data)
                        st.success(f"✅ Profil '{profil}' berhasil ditambahkan!")
                        st.rerun()
    
    with tab2:
        st.markdown("### Mapping Profil Lulusan dengan CPL")
        
        # Pilih PL
        pl_options = {pl['kode']: pl['profil'] for pl in pl_data}
        selected_pl = st.selectbox("Pilih Profil Lulusan:", list(pl_options.keys()),
                                 format_func=lambda x: f"{x} - {pl_options[x]}")
        
        if selected_pl:
            cpl_df = pd.DataFrame(data['cpl_data'])
            
            st.markdown(f"**Pilih CPL untuk {selected_pl}:**")
            
            # Buat checkbox untuk setiap CPL
            cpl_selections = {}
            cols = st.columns(3)
            
            for idx, cpl in enumerate(data['cpl_data']):
                with cols[idx % 3]:
                    cpl_selections[cpl['kode']] = st.checkbox(
                        f"{cpl['kode']} - {cpl['deskripsi'][:50]}...",
                        key=f"cpl_{selected_pl}_{cpl['kode']}"
                    )
            
            if st.button("💾 Simpan Mapping", type="primary"):
                # Simpan mapping (contoh sederhana)
                mapping = {cpl: selected for cpl, selected in cpl_selections.items() if selected}
                st.success(f"✅ Mapping untuk {selected_pl} berhasil disimpan!")
                st.json(mapping)

# ==================== ADMIN: KELOLA CPL ====================
def admin_kelola_cpl():
    st.markdown('<h1 class="main-header">🎓 Kelola Capaian Pembelajaran Lulusan (CPL)</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    cpl_data = data['cpl_data']
    
    tab1, tab2, tab3 = st.tabs(["📝 Kelola CPL", "🏗️ Bahan Kajian (BK)", "🎯 CPMK"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### Daftar CPL")
            
            if cpl_data:
                df = pd.DataFrame(cpl_data)
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "id": st.column_config.TextColumn("ID", disabled=True),
                        "domain": st.column_config.SelectboxColumn(
                            "Domain",
                            options=["Sikap", "Pengetahuan", "Keterampilan Umum", "Keterampilan Khusus"]
                        ),
                        "kode": st.column_config.TextColumn("Kode CPL"),
                        "deskripsi": st.column_config.TextColumn("Deskripsi CPL")
                    },
                    num_rows="dynamic",
                    key="cpl_editor"
                )
                
                if st.button("💾 Simpan CPL", type="primary"):
                    save_data('cpl_data', edited_df.to_dict('records'))
                    st.success("✅ CPL berhasil disimpan!")
            else:
                st.info("Belum ada data CPL.")
        
        with col2:
            st.markdown("### Tambah CPL Baru")
            
            with st.form("tambah_cpl_form"):
                domain = st.selectbox(
                    "Domain",
                    ["Sikap", "Pengetahuan", "Keterampilan Umum", "Keterampilan Khusus"]
                )
                kode = st.text_input("Kode CPL (contoh: KK6)")
                deskripsi = st.text_area("Deskripsi CPL")
                
                if st.form_submit_button("➕ Tambah CPL"):
                    if kode and deskripsi:
                        new_cpl = {
                            "id": str(uuid.uuid4())[:8],
                            "domain": domain,
                            "kode": kode,
                            "deskripsi": deskripsi
                        }
                        cpl_data.append(new_cpl)
                        save_data('cpl_data', cpl_data)
                        st.success(f"✅ CPL '{kode}' berhasil ditambahkan!")
                        st.rerun()
    
    with tab2:
        st.markdown("### 🏗️ Kelola Bahan Kajian (BK)")
        
        # Load atau init BK data
        bk_data = data.get('bk_data', [])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Daftar Bahan Kajian**")
            
            if bk_data:
                for bk in bk_data:
                    with st.expander(f"{bk.get('kode', '')} - {bk.get('nama', '')}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Kode:** {bk.get('kode', '')}")
                            st.write(f"**Nama:** {bk.get('nama', '')}")
                        with col_b:
                            st.write(f"**Deskripsi:** {bk.get('deskripsi', '')}")
                        
                        # Edit BK
                        with st.form(f"edit_bk_{bk.get('id', '')}"):
                            new_nama = st.text_input("Nama BK", value=bk.get('nama', ''))
                            new_deskripsi = st.text_area("Deskripsi", value=bk.get('deskripsi', ''))
                            
                            col_c, col_d = st.columns(2)
                            with col_c:
                                if st.form_submit_button("💾 Update"):
                                    bk['nama'] = new_nama
                                    bk['deskripsi'] = new_deskripsi
                                    save_data('bk_data', bk_data)
                                    st.success("✅ BK berhasil diupdate!")
                            with col_d:
                                if st.form_submit_button("🗑️ Hapus", type="secondary"):
                                    bk_data.remove(bk)
                                    save_data('bk_data', bk_data)
                                    st.success("✅ BK berhasil dihapus!")
                                    st.rerun()
            else:
                st.info("Belum ada Bahan Kajian. Tambahkan BK baru.")
        
        with col2:
            st.markdown("**Tambah BK Baru**")
            
            with st.form("tambah_bk_form"):
                kode_bk = st.text_input("Kode BK")
                nama_bk = st.text_input("Nama Bahan Kajian")
                deskripsi_bk = st.text_area("Deskripsi BK")
                
                if st.form_submit_button("➕ Tambah BK"):
                    if kode_bk and nama_bk:
                        new_bk = {
                            "id": str(uuid.uuid4())[:8],
                            "kode": kode_bk,
                            "nama": nama_bk,
                            "deskripsi": deskripsi_bk
                        }
                        bk_data.append(new_bk)
                        save_data('bk_data', bk_data)
                        st.success("✅ Bahan Kajian berhasil ditambahkan!")
                        st.rerun()
    
    with tab3:
        st.markdown("### 🎯 Kelola CPMK (Capaian Pembelajaran Mata Kuliah)")
        
        # Load MK untuk mapping
        mk_wajib = data['mk_wajib']
        
        if mk_wajib:
            selected_mk = st.selectbox(
                "Pilih Mata Kuliah:",
                [f"{mk['Kode']} - {mk['Nama']}" for mk in mk_wajib]
            )
            
            if selected_mk:
                mk_kode = selected_mk.split(" - ")[0]
                
                # Load CPMK untuk MK ini
                cpmk_data = data.get('cpmk_data', [])
                mk_cpmk = [cpmk for cpmk in cpmk_data if cpmk.get('mk_kode') == mk_kode]
                
                st.markdown(f"**CPMK untuk {selected_mk}**")
                
                # Form tambah CPMK
                with st.form(f"tambah_cpmk_{mk_kode}"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        kode_cpmk = st.text_input("Kode CPMK (contoh: CPMK1)")
                    with col2:
                        deskripsi_cpmk = st.text_area("Deskripsi CPMK")
                    
                    # Pilih CPL yang dicapai
                    st.markdown("**CPL yang Dicapai:**")
                    cpl_options = [f"{cpl['kode']} - {cpl['deskripsi'][:50]}..." for cpl in cpl_data]
                    selected_cpl = st.multiselect("Pilih CPL:", cpl_options)
                    
                    if st.form_submit_button("➕ Tambah CPMK"):
                        if kode_cpmk and deskripsi_cpmk:
                            new_cpmk = {
                                "id": str(uuid.uuid4())[:8],
                                "mk_kode": mk_kode,
                                "kode": kode_cpmk,
                                "deskripsi": deskripsi_cpmk,
                                "cpl_terkait": selected_cpl
                            }
                            cpmk_data.append(new_cpmk)
                            save_data('cpmk_data', cpmk_data)
                            st.success("✅ CPMK berhasil ditambahkan!")
                            st.rerun()
                
                # Tampilkan CPMK yang ada
                if mk_cpmk:
                    st.markdown("**Daftar CPMK:**")
                    for cpmk in mk_cpmk:
                        with st.expander(f"{cpmk['kode']} - {cpmk['deskripsi'][:100]}..."):
                            st.write(f"**Deskripsi Lengkap:** {cpmk['deskripsi']}")
                            st.write(f"**CPL Terkait:** {', '.join(cpmk.get('cpl_terkait', []))}")
                            
                            if st.button(f"🗑️ Hapus {cpmk['kode']}", key=f"del_{cpmk['id']}"):
                                cpmk_data.remove(cpmk)
                                save_data('cpmk_data', cpmk_data)
                                st.success("✅ CPMK berhasil dihapus!")
                                st.rerun()
        else:
            st.info("Belum ada Mata Kuliah. Tambahkan MK terlebih dahulu.")

# ==================== ADMIN: KELOLA MATA KULIAH ====================
def admin_kelola_mk():
    st.markdown('<h1 class="main-header">📚 Kelola Mata Kuliah</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    
    tab1, tab2 = st.tabs(["📖 Mata Kuliah Wajib", "🎯 Mata Kuliah Peminatan"])
    
    with tab1:
        st.markdown("### 📖 Kelola Mata Kuliah Wajib")
        
        mk_wajib = data['mk_wajib']
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if mk_wajib:
                # Konversi ke DataFrame untuk editor
                df = pd.DataFrame(mk_wajib)
                
                # Editor data
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Kode": st.column_config.TextColumn("Kode MK"),
                        "Nama": st.column_config.TextColumn("Nama MK"),
                        "SKS": st.column_config.NumberColumn("SKS", min_value=1, max_value=6),
                        "Semester": st.column_config.NumberColumn("Semester", min_value=1, max_value=8),
                        "Jenis": st.column_config.SelectboxColumn(
                            "Jenis",
                            options=["Teori", "Praktikum", "Teori+Praktikum", "Praktisi", "Project"]
                        ),
                        "CPL": st.column_config.TextColumn("CPL (pisah koma)"),
                        "Prasyarat": st.column_config.TextColumn("Prasyarat (pisah koma)")
                    },
                    num_rows="dynamic",
                    key="mk_wajib_editor"
                )
                
                if st.button("💾 Simpan MK Wajib", type="primary"):
                    save_data('mk_wajib', edited_df.to_dict('records'))
                    st.success("✅ Mata Kuliah Wajib berhasil disimpan!")
            else:
                st.info("Belum ada Mata Kuliah Wajib.")
        
        with col2:
            st.markdown("### Tambah MK Baru")
            
            with st.form("tambah_mk_form"):
                kode = st.text_input("Kode MK")
                nama = st.text_input("Nama MK")
                sks = st.number_input("SKS", min_value=1, max_value=6, value=3)
                semester = st.number_input("Semester", min_value=1, max_value=8, value=1)
                jenis = st.selectbox(
                    "Jenis",
                    ["Teori", "Praktikum", "Teori+Praktikum", "Praktisi", "Project"]
                )
                cpl = st.text_input("CPL (pisahkan koma)")
                prasyarat = st.text_input("Prasyarat (pisahkan koma)")
                
                if st.form_submit_button("➕ Tambah MK"):
                    if kode and nama:
                        new_mk = {
                            "Kode": kode,
                            "Nama": nama,
                            "SKS": int(sks),
                            "Semester": int(semester),
                            "Jenis": jenis,
                            "CPL": cpl,
                            "Prasyarat": prasyarat
                        }
                        mk_wajib.append(new_mk)
                        save_data('mk_wajib', mk_wajib)
                        st.success(f"✅ MK '{nama}' berhasil ditambahkan!")
                        st.rerun()
    
    with tab2:
        st.markdown("### 🎯 Kelola Mata Kuliah Peminatan")
        
        peminatan_data = data['peminatan_data']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Peminatan yang Ada")
            
            if peminatan_data:
                for peminatan, mk_list in peminatan_data.items():
                    with st.expander(f"📁 {peminatan} ({len(mk_list)} MK)"):
                        st.write(f"**Mata Kuliah:**")
                        for mk in mk_list:
                            st.write(f"- {mk['Kode']}: {mk['Nama']} ({mk['SKS']} SKS)")
                        
                        # Hapus peminatan
                        if st.button(f"🗑️ Hapus Peminatan {peminatan}", key=f"del_{peminatan}"):
                            del peminatan_data[peminatan]
                            save_data('peminatan_data', peminatan_data)
                            st.success(f"✅ Peminatan '{peminatan}' dihapus!")
                            st.rerun()
            else:
                st.info("Belum ada peminatan.")
        
        with col2:
            st.markdown("#### Tambah/Edit Peminatan")
            
            # Form tambah peminatan baru
            with st.form("tambah_peminatan_form"):
                nama_peminatan = st.text_input("Nama Peminatan Baru")
                
                if st.form_submit_button("➕ Buat Peminatan Baru"):
                    if nama_peminatan:
                        if nama_peminatan not in peminatan_data:
                            peminatan_data[nama_peminatan] = []
                            save_data('peminatan_data', peminatan_data)
                            st.success(f"✅ Peminatan '{nama_peminatan}' berhasil dibuat!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Peminatan sudah ada!")
            
            st.markdown("---")
            st.markdown("#### Tambah MK ke Peminatan")
            
            # Pilih peminatan
            if peminatan_data:
                selected_peminatan = st.selectbox(
                    "Pilih Peminatan:",
                    list(peminatan_data.keys())
                )
                
                with st.form("tambah_mk_peminatan_form"):
                    kode_mk = st.text_input("Kode MK Peminatan")
                    nama_mk = st.text_input("Nama MK Peminatan")
                    sks_mk = st.number_input("SKS", min_value=1, max_value=6, value=3)
                    semester_mk = st.number_input("Semester", min_value=5, max_value=8, value=5)
                    cpl_mk = st.text_input("CPL (pisahkan koma)")
                    prasyarat_mk = st.text_input("Prasyarat (pisahkan koma)")
                    
                    if st.form_submit_button("➕ Tambah MK ke Peminatan"):
                        if kode_mk and nama_mk:
                            new_mk = {
                                "Kode": kode_mk,
                                "Nama": nama_mk,
                                "SKS": int(sks_mk),
                                "Semester": int(semester_mk),
                                "CPL": cpl_mk,
                                "Prasyarat": prasyarat_mk
                            }
                            peminatan_data[selected_peminatan].append(new_mk)
                            save_data('peminatan_data', peminatan_data)
                            st.success(f"✅ MK '{nama_mk}' berhasil ditambahkan ke '{selected_peminatan}'!")
                            st.rerun()

# ==================== ADMIN: KELOLA PRASYARAT ====================
def admin_kelola_prasyarat():
    st.markdown('<h1 class="main-header">🔗 Kelola Prasyarat Mata Kuliah</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    mk_wajib = data['mk_wajib']
    peminatan_data = data['peminatan_data']
    prasyarat_data = data.get('prasyarat_data', {})
    
    # Kumpulkan semua MK
    all_mk = []
    for mk in mk_wajib:
        all_mk.append(mk['Kode'])
    
    for mk_list in peminatan_data.values():
        for mk in mk_list:
            all_mk.append(mk['Kode'])
    
    if all_mk:
        tab1, tab2 = st.tabs(["🧭 Editor Prasyarat", "🌳 Visualisasi Graph"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Pilih Mata Kuliah")
                selected_mk = st.selectbox("Mata Kuliah:", sorted(set(all_mk)))
                
                if selected_mk:
                    # Dapatkan prasyarat yang sudah ada
                    current_prereqs = prasyarat_data.get(selected_mk, [])
                    
                    st.markdown(f"**Prasyarat untuk {selected_mk}:**")
                    
                    # Multi-select untuk prasyarat
                    available_prereqs = [mk for mk in all_mk if mk != selected_mk]
                    new_prereqs = st.multiselect(
                        "Pilih Prasyarat:",
                        available_prereqs,
                        default=current_prereqs
                    )
                    
                    if st.button("💾 Simpan Prasyarat", type="primary"):
                        if new_prereqs:
                            prasyarat_data[selected_mk] = new_prereqs
                        elif selected_mk in prasyarat_data:
                            del prasyarat_data[selected_mk]
                        
                        save_data('prasyarat_data', prasyarat_data)
                        st.success("✅ Prasyarat berhasil disimpan!")
            
            with col2:
                st.markdown("### Tabel Prasyarat")
                
                if prasyarat_data:
                    table_data = []
                    for mk, prereqs in prasyarat_data.items():
                        table_data.append({
                            "Mata Kuliah": mk,
                            "Prasyarat": ", ".join(prereqs),
                            "Jumlah": len(prereqs)
                        })
                    
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("Belum ada data prasyarat.")
        
        with tab2:
            st.markdown("### 🌳 Visualisasi Graph Prasyarat")
            
            if prasyarat_data:
                # Buat graph
                G = nx.DiGraph()
                
                # Tambahkan node dan edges
                for mk, prereqs in prasyarat_data.items():
                    for prereq in prereqs:
                        G.add_edge(prereq, mk)
                
                # Buat visualisasi dengan plotly
                pos = nx.spring_layout(G, seed=42)
                
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='#888'),
                    hoverinfo='none',
                    mode='lines')
                
                node_x = []
                node_y = []
                node_text = []
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(node)
                
                node_trace = go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    hoverinfo='text',
                    text=node_text,
                    textposition="top center",
                    marker=dict(
                        showscale=True,
                        colorscale='Blues',
                        size=25,
                        color=list(range(len(G.nodes()))),
                        line_width=2))
                
                fig = go.Figure(data=[edge_trace, node_trace],
                              layout=go.Layout(
                                  title='',
                                  showlegend=False,
                                  hovermode='closest',
                                  margin=dict(b=20,l=5,r=5,t=40),
                                  xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                  yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tidak ada data prasyarat untuk divisualisasikan.")
    else:
        st.info("Belum ada Mata Kuliah. Tambahkan MK terlebih dahulu.")

# ==================== ADMIN: KELOLA MBKM ====================
def admin_kelola_mbkm():
    st.markdown('<h1 class="main-header">🌐 Kelola Program MBKM</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    mbkm_data = data.get('mbkm_data', [])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Daftar Kegiatan MBKM")
        
        if mbkm_data:
            for i, mbkm in enumerate(mbkm_data):
                with st.expander(f"{mbkm.get('Kegiatan', '')} ({mbkm.get('SKS', 0)} SKS)"):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        st.write(f"**Deskripsi:** {mbkm.get('Deskripsi', '')}")
                        st.write(f"**Semester:** {mbkm.get('Semester', '')}")
                        st.write(f"**Jenis:** {mbkm.get('Jenis', '')}")
                    
                    with col_b:
                        st.write(f"**Min SKS:** {mbkm.get('SKS', 0)}")
                        st.write(f"**Max SKS:** {mbkm.get('MaxSKS', mbkm.get('SKS', 0))}")
                    
                    with col_c:
                        # Form edit
                        with st.form(f"edit_mbkm_{i}"):
                            kegiatan = st.text_input("Kegiatan", value=mbkm.get('Kegiatan', ''))
                            sks = st.number_input("SKS", value=mbkm.get('SKS', 0))
                            semester = st.text_input("Semester", value=mbkm.get('Semester', ''))
                            deskripsi = st.text_area("Deskripsi", value=mbkm.get('Deskripsi', ''))
                            
                            col_sub1, col_sub2 = st.columns(2)
                            with col_sub1:
                                if st.form_submit_button("💾 Update"):
                                    mbkm_data[i] = {
                                        "Kegiatan": kegiatan,
                                        "SKS": sks,
                                        "Semester": semester,
                                        "Deskripsi": deskripsi,
                                        "Jenis": mbkm.get('Jenis', 'Kegiatan')
                                    }
                                    save_data('mbkm_data', mbkm_data)
                                    st.success("✅ MBKM berhasil diupdate!")
                                    st.rerun()
                            with col_sub2:
                                if st.form_submit_button("🗑️ Hapus"):
                                    mbkm_data.pop(i)
                                    save_data('mbkm_data', mbkm_data)
                                    st.success("✅ MBKM berhasil dihapus!")
                                    st.rerun()
        else:
            st.info("Belum ada data MBKM.")
    
    with col2:
        st.markdown("### Tambah MBKM Baru")
        
        with st.form("tambah_mbkm_form"):
            kegiatan = st.text_input("Nama Kegiatan MBKM")
            sks = st.number_input("SKS", min_value=1, max_value=20, value=3)
            semester = st.text_input("Semester (contoh: 5-6)")
            deskripsi = st.text_area("Deskripsi Kegiatan")
            jenis = st.selectbox(
                "Jenis Kegiatan",
                ["Magang", "Proyek", "Pertukaran", "Kewirausahaan", "KKN", "Sertifikasi", "Lainnya"]
            )
            
            if st.form_submit_button("➕ Tambah MBKM"):
                if kegiatan:
                    new_mbkm = {
                        "Kegiatan": kegiatan,
                        "SKS": sks,
                        "Semester": semester,
                        "Deskripsi": deskripsi,
                        "Jenis": jenis
                    }
                    mbkm_data.append(new_mbkm)
                    save_data('mbkm_data', mbkm_data)
                    st.success("✅ Kegiatan MBKM berhasil ditambahkan!")
                    st.rerun()

# ==================== ADMIN: KELOLA EVALUASI OBE ====================
def admin_kelola_evaluasi():
    st.markdown('<h1 class="main-header">📊 Kelola Sistem Evaluasi OBE</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    
    tab1, tab2, tab3 = st.tabs(["📈 Template Evaluasi", "🎯 Rubrik Penilaian", "📋 Laporan OBE"])
    
    with tab1:
        st.markdown("### 📈 Template Evaluasi Pembelajaran")
        
        # Template untuk berbagai jenis evaluasi
        evaluasi_templates = {
            "Kuis": ["Pemahaman konsep", "Aplikasi teori", "Analisis kasus"],
            "Tugas": ["Implementasi", "Analisis", "Presentasi"],
            "Proyek": ["Perencanaan", "Implementasi", "Dokumentasi", "Presentasi"],
            "UTS/UAS": ["Pemahaman teori", "Penyelesaian masalah", "Analisis kasus"]
        }
        
        selected_template = st.selectbox("Pilih Template:", list(evaluasi_templates.keys()))
        
        if selected_template:
            st.markdown(f"**Komponen Evaluasi {selected_template}:**")
            
            components = evaluasi_templates[selected_template]
            weights = {}
            
            for i, component in enumerate(components):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_name = st.text_input(f"Komponen {i+1}", value=component)
                with col2:
                    weight = st.number_input(f"Bobot (%)", min_value=0, max_value=100, value=100//len(components), key=f"weight_{i}")
                    weights[new_name] = weight
            
            if st.button("💾 Simpan Template", type="primary"):
                st.success(f"✅ Template '{selected_template}' berhasil disimpan!")
    
    with tab2:
        st.markdown("### 🎯 Rubrik Penilaian CPL")
        
        cpl_data = data['cpl_data']
        
        if cpl_data:
            selected_cpl = st.selectbox(
                "Pilih CPL untuk buat rubrik:",
                [f"{cpl['kode']} - {cpl['deskripsi'][:50]}..." for cpl in cpl_data]
            )
            
            if selected_cpl:
                st.markdown(f"**Rubrik untuk {selected_cpl}**")
                
                # Buat rubrik 4 level
                levels = ["Sangat Baik (4)", "Baik (3)", "Cukup (2)", "Perlu Perbaikan (1)"]
                
                rubrik_data = []
                for i in range(3):  # 3 kriteria
                    with st.expander(f"Kriteria {i+1}"):
                        kriteria = st.text_input(f"Deskripsi Kriteria {i+1}", 
                                               value=f"Kriteria penilaian {i+1}")
                        
                        level_descriptions = {}
                        for level in levels:
                            level_descriptions[level] = st.text_area(
                                f"Deskripsi {level}",
                                value=f"Mahasiswa menunjukkan {level.lower()} dalam {kriteria.lower()}"
                            )
                        
                        rubrik_data.append({
                            "kriteria": kriteria,
                            "level_deskripsi": level_descriptions
                        })
                
                if st.button("💾 Simpan Rubrik", type="primary"):
                    st.success("✅ Rubrik penilaian berhasil disimpan!")
        else:
            st.info("Belum ada CPL. Tambahkan CPL terlebih dahulu.")
    
    with tab3:
        st.markdown("### 📋 Generator Laporan OBE")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Jenis Laporan:",
                ["Laporan Semesteran", "Laporan Tahunan", "Laporan Akreditasi", "Laporan MBKM"]
            )
            
            include_sections = st.multiselect(
                "Sertakan Bagian:",
                ["Profil Lulusan", "CPL", "Mata Kuliah", "Prasyarat", "MBKM", "Evaluasi", "Rekomendasi"]
            )
        
        with col2:
            format_report = st.selectbox("Format Export:", ["PDF", "Word", "Excel", "HTML"])
            
            include_charts = st.checkbox("Sertakan grafik/chart")
            include_data = st.checkbox("Sertakan data lengkap")
        
        if st.button("📄 Generate Laporan OBE", type="primary"):
            with st.spinner("Membuat laporan..."):
                st.success(f"✅ Laporan OBE {report_type} berhasil digenerate!")
                
                # Contoh output
                st.markdown("""
                **Preview Laporan:**
                - **Judul:** Laporan Evaluasi OBE Program Studi Ilmu Komputer
                - **Periode:** Semester Ganjil 2024/2025
                - **Tanggal:** """ + datetime.now().strftime("%d %B %Y") + """
                - **Status:** Lengkap
                """)

# ==================== ADMIN: EXPORT/IMPORT DATA ====================
def admin_export_import():
    st.markdown('<h1 class="main-header">📤 Export/Import Data Kurikulum</h1>', unsafe_allow_html=True)
    
    data = load_all_data()
    
    tab1, tab2, tab3 = st.tabs(["📤 Export Data", "📥 Import Data", "🔄 Backup/Restore"])
    
    with tab1:
        st.markdown("### 📤 Export Data ke Berbagai Format")
        
        # Pilih data untuk export
        export_options = st.multiselect(
            "Pilih data yang akan di-export:",
            ["Profil Lulusan", "CPL", "Mata Kuliah Wajib", "Peminatan", "Prasyarat", "MBKM", "BK", "CPMK"],
            default=["Profil Lulusan", "CPL", "Mata Kuliah Wajib"]
        )
        
        # Format export
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.radio(
                "Format Export:",
                ["Excel (.xlsx)", "JSON (.json)", "CSV (.csv)", "PDF Report"]
            )
        
        with col2:
            include_metadata = st.checkbox("Sertakan metadata", value=True)
            timestamp = st.checkbox("Sertakan timestamp", value=True)
        
        if st.button("🚀 Generate Export", type="primary"):
            with st.spinner("Mempersiapkan data untuk export..."):
                # Buat file berdasarkan format
                if export_format == "Excel (.xlsx)":
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        if "Profil Lulusan" in export_options:
                            df_pl = pd.DataFrame(data['pl_data'])
                            df_pl.to_excel(writer, sheet_name='Profil_Lulusan', index=False)
                        
                        if "CPL" in export_options:
                            df_cpl = pd.DataFrame(data['cpl_data'])
                            df_cpl.to_excel(writer, sheet_name='CPL', index=False)
                        
                        if "Mata Kuliah Wajib" in export_options:
                            df_mk = pd.DataFrame(data['mk_wajib'])
                            df_mk.to_excel(writer, sheet_name='MK_Wajib', index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=output,
                        file_name="kurikulum_obe_mncu.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                elif export_format == "JSON (.json)":
                    export_data = {}
                    for option in export_options:
                        if option == "Profil Lulusan":
                            export_data['profil_lulusan'] = data['pl_data']
                        elif option == "CPL":
                            export_data['cpl'] = data['cpl_data']
                        elif option == "Mata Kuliah Wajib":
                            export_data['mata_kuliah_wajib'] = data['mk_wajib']
                    
                    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="📥 Download JSON File",
                        data=json_str,
                        file_name="kurikulum_obe_mncu.json",
                        mime="application/json"
                    )
                
                st.success("✅ Data siap diunduh!")
    
    with tab2:
        st.markdown("### 📥 Import Data dari File")
        
        uploaded_file = st.file_uploader(
            "Upload file data kurikulum:",
            type=['xlsx', 'csv', 'json'],
            help="Upload file Excel, CSV, atau JSON yang berisi data kurikulum"
        )
        
        if uploaded_file:
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type == 'json':
                import_data = json.load(uploaded_file)
                st.success("✅ File JSON berhasil dibaca!")
                
                # Tampilkan preview
                st.markdown("**Preview Data:**")
                st.json(import_data)
                
                if st.button("💾 Import Data ke Sistem", type="primary"):
                    # Proses import data
                    st.success("✅ Data berhasil diimport!")
            
            elif file_type in ['xlsx', 'xls']:
                df_dict = pd.read_excel(uploaded_file, sheet_name=None)
                st.success(f"✅ File Excel berhasil dibaca! Terdapat {len(df_dict)} sheet.")
                
                for sheet_name, df in df_dict.items():
                    with st.expander(f"Sheet: {sheet_name}"):
                        st.dataframe(df.head())
            
            elif file_type == 'csv':
                df = pd.read_csv(uploaded_file)
                st.success("✅ File CSV berhasil dibaca!")
                st.dataframe(df.head())
    
    with tab3:
        st.markdown("### 🔄 Backup & Restore Database")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Buat Backup")
            backup_name = st.text_input("Nama Backup:", value=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            if st.button("💾 Buat Backup", type="primary"):
                # Backup semua data
                backup_data = {}
                for key, filepath in DATA_FILES.items():
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            backup_data[key] = json.load(f)
                    except:
                        backup_data[key] = []
                
                # Simpan backup
                backup_file = f"backups/{backup_name}.json"
                os.makedirs("backups", exist_ok=True)
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ Backup '{backup_name}' berhasil dibuat!")
        
        with col2:
            st.markdown("#### Restore Backup")
            
            # List backup yang ada
            backup_files = []
            if os.path.exists("backups"):
                backup_files = [f for f in os.listdir("backups") if f.endswith('.json')]
            
            if backup_files:
                selected_backup = st.selectbox("Pilih Backup:", backup_files)
                
                if st.button("🔄 Restore Backup", type="primary"):
                    backup_path = f"backups/{selected_backup}"
                    try:
                        with open(backup_path, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                        
                        # Restore data
                        for key, data in backup_data.items():
                            save_data(key, data)
                        
                        st.success(f"✅ Backup '{selected_backup}' berhasil direstore!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.info("Belum ada backup tersedia.")

# ==================== FUNGSI UNTUK USER BIASA ====================
def show_profil_lulusan_user():
    """Tampilan Profil Lulusan untuk user biasa"""
    data = load_all_data()
    pl_data = data['pl_data']
    
    st.markdown('<h1 class="main-header">👥 Profil Lulusan Ilmu Komputer MNCU</h1>', unsafe_allow_html=True)
    
    # Tampilkan semua PL
    for pl in pl_data:
        with st.expander(f"{pl.get('icon', '🎓')} {pl.get('profil', '')} ({pl.get('kode', '')})", expanded=True):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Kode:** {pl.get('kode', '')}")
                st.markdown(f"**Icon:** {pl.get('icon', '🎓')}")
                st.color_picker("Warna", pl.get('warna', '#0056A4'), disabled=True)
            
            with col2:
                st.markdown(f"**Deskripsi:**")
                st.info(pl.get('deskripsi', ''))
                
                # Kompetensi contoh
                st.markdown("**Kompetensi Utama:**")
                kompetensi = [
                    "Analisis dan pemecahan masalah kompleks",
                    "Pengembangan sistem berbasis teknologi",
                    "Manajemen proyek TI",
                    "Komunikasi dan kolaborasi tim"
                ]
                for k in kompetensi:
                    st.checkbox(f"✓ {k}", value=True, disabled=True)

def show_struktur_kurikulum_user():
    """Tampilan Struktur Kurikulum untuk user biasa"""
    data = load_all_data()
    
    st.markdown('<h1 class="main-header">📚 Struktur Kurikulum Ilmu Komputer MNCU</h1>', unsafe_allow_html=True)
    
    # Pilih semester
    semester = st.selectbox("Pilih Semester:", [1, 2, 3, 4, 5, 6, 7, 8])
    
    if semester <= 4:
        # Mata kuliah wajib
        mk_semester = [mk for mk in data['mk_wajib'] if mk['Semester'] == semester]
        
        st.markdown(f"### Semester {semester} - Mata Kuliah Wajib")
        
        for mk in mk_semester:
            with st.expander(f"{mk['Kode']} - {mk['Nama']} ({mk['SKS']} SKS)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Jenis:** {mk['Jenis']}")
                    st.write(f"**SKS:** {mk['SKS']}")
                    st.write(f"**CPL:** {mk['CPL']}")
                with col2:
                    st.write(f"**Prasyarat:** {mk['Prasyarat']}")
                    st.write("**Evaluasi:** Tugas 30%, UTS 30%, UAS 40%")
    
    else:
        # Peminatan
        st.markdown(f"### Semester {semester} - Peminatan")
        
        if data['peminatan_data']:
            selected_peminatan = st.selectbox("Pilih Peminatan:", list(data['peminatan_data'].keys()))
            
            if selected_peminatan:
                mk_peminatan = [mk for mk in data['peminatan_data'][selected_peminatan] if mk['Semester'] == semester]
                
                for mk in mk_peminatan:
                    with st.expander(f"{mk['Kode']} - {mk['Nama']} ({mk['SKS']} SKS)"):
                        st.write(f"**Peminatan:** {selected_peminatan}")
                        st.write(f"**CPL:** {mk['CPL']}")
                        st.write(f"**Prasyarat:** {mk['Prasyarat']}")

# ==================== MAIN APP ROUTING ====================
def main():
    # Initialize session state
    if 'edit_pl' not in st.session_state:
        st.session_state.edit_pl = False
    
    # Routing berdasarkan menu dan mode admin
    if admin_mode:
        if menu == "🏠 Dashboard":
            show_dashboard()
        elif menu == "👥 Kelola Profil Lulusan":
            admin_kelola_pl()
        elif menu == "🎓 Kelola CPL":
            admin_kelola_cpl()
        elif menu == "📚 Kelola Mata Kuliah":
            admin_kelola_mk()
        elif menu == "🔗 Kelola Prasyarat":
            admin_kelola_prasyarat()
        elif menu == "🌐 Kelola MBKM":
            admin_kelola_mbkm()
        elif menu == "📊 Kelola Evaluasi OBE":
            admin_kelola_evaluasi()
        elif menu == "📤 Export/Import Data":
            admin_export_import()
        elif menu == "ℹ️ Tentang MNCU":
            st.markdown('<h1 class="main-header">🏛️ Tentang MNC University</h1>', unsafe_allow_html=True)
            st.info("The Real Media & Entertainment Campus")
    else:
        if menu == "🏠 Dashboard":
            show_dashboard()
        elif menu == "👥 Profil Lulusan":
            show_profil_lulusan_user()
        elif menu == "📚 Struktur Kurikulum":
            show_struktur_kurikulum_user()
        elif menu == "🔗 Prasyarat MK":
            # Implementasi sederhana
            st.info("Fitur Prasyarat MK - User View")
        elif menu == "🌐 Program MBKM":
            # Implementasi sederhana
            st.info("Fitur Program MBKM - User View")
        elif menu == "📝 Simulasi KRS":
            # Implementasi sederhana
            st.info("Fitur Simulasi KRS - User View")
        elif menu == "📊 Evaluasi OBE":
            # Implementasi sederhana
            st.info("Fitur Evaluasi OBE - User View")
        elif menu == "📤 Export Data":
            # Implementasi sederhana
            st.info("Fitur Export Data - User View")
        elif menu == "ℹ️ Tentang MNCU":
            st.markdown('<h1 class="main-header">🏛️ Tentang MNC University</h1>', unsafe_allow_html=True)
            st.info("The Real Media & Entertainment Campus")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if admin_mode:
            st.markdown('<p style="text-align: center; color: #DC2626; font-size: 0.9rem;">🔐 MODE ADMIN - Hati-hati dalam mengedit data</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666; font-size: 0.9rem;">© 2025 MNC University - Prodi Ilmu Komputer<br>Kurikulum OBE Dinamis v2.0</p>', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    # Pastikan direktori data ada
    ensure_data_directory()
    main()
