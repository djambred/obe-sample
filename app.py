import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Kurikulum OBE Ilmu Komputer MNCU",
    page_icon="🎓",
    layout="wide"
)

# CSS Custom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #3B82F6, #1E40AF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E40AF;
        border-left: 4px solid #3B82F6;
        padding-left: 1rem;
        margin-top: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .semester-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .mbkm-badge {
        background: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/800px-Google_Colaboratory_SVG_Logo.svg.png", width=100)
    st.title("Navigasi Kurikulum")
    
    menu = st.selectbox(
        "Pilih Menu:",
        ["Dashboard", "Profil Lulusan", "Struktur Kurikulum", "Prasyarat MK", 
         "MBKM", "Evaluasi OBE", "Simulasi KRS", "Export Data"]
    )
    
    st.divider()
    st.info(f"Last Updated: {datetime.now().strftime('%d %B %Y')}")
    st.caption("Kurikulum OBE 2025 - Prodi Ilmu Komputer MNCU")

# Data Kurikulum
def load_data():
    # Data Profil Lulusan
    pl_data = [
        {"Kode": "PL1", "Profil": "Software Engineer", "Deskripsi": "Mengembangkan aplikasi dan sistem perangkat lunak"},
        {"Kode": "PL2", "Profil": "Data Scientist/Analyst", "Deskripsi": "Menganalisis data untuk pengambilan keputusan"},
        {"Kode": "PL3", "Profil": "AI Engineer", "Deskripsi": "Mengembangkan sistem kecerdasan buatan"},
        {"Kode": "PL4", "Profil": "Cybersecurity Specialist", "Deskripsi": "Mengamankan sistem dan jaringan komputer"},
        {"Kode": "PL5", "Profil": "IT Consultant/Entrepreneur", "Deskripsi": "Konsultan teknologi dan wirausaha digital"}
    ]
    
    # Data CPL
    cpl_data = {
        "Sikap": ["S1", "S2", "S3", "S4"],
        "Pengetahuan": ["P1", "P2", "P3", "P4"],
        "Keterampilan Umum": ["KU1", "KU2", "KU3", "KU4"],
        "Keterampilan Khusus": ["KK1", "KK2", "KK3", "KK4", "KK5"]
    }
    
    # Data Mata Kuliah Wajib
    mk_wajib = [
        # Semester 1
        {"Kode": "MKDU001", "Nama": "Bahasa Indonesia", "SKS": 2, "Semester": 1, "Jenis": "Teori", "CPL": "S1,KU2"},
        {"Kode": "MKU001", "Nama": "Public Speaking", "SKS": 2, "Semester": 1, "Jenis": "Praktikum", "CPL": "KU2,KU4"},
        {"Kode": "ILK101", "Nama": "Matematika Diskrit", "SKS": 3, "Semester": 1, "Jenis": "Teori", "CPL": "P1"},
        {"Kode": "ILK102", "Nama": "Pemrograman Dasar", "SKS": 3, "Semester": 1, "Jenis": "Praktikum", "CPL": "KK1"},
        {"Kode": "ILK103", "Nama": "Pengantar TI", "SKS": 3, "Semester": 1, "Jenis": "Teori+Praktikum", "CPL": "P2,KU1"},
        
        # Semester 2
        {"Kode": "MKDU002", "Nama": "Pancasila", "SKS": 2, "Semester": 2, "Jenis": "Teori", "CPL": "S2"},
        {"Kode": "ILK201", "Nama": "Algoritma & Struktur Data", "SKS": 3, "Semester": 2, "Jenis": "Teori+Praktikum", "CPL": "P1,KK1"},
        {"Kode": "ILK202", "Nama": "Matematika Komputasi", "SKS": 3, "Semester": 2, "Jenis": "Teori", "CPL": "P1"},
        {"Kode": "ILK203", "Nama": "Basis Data", "SKS": 3, "Semester": 2, "Jenis": "Teori+Praktikum", "CPL": "P3,KK2"},
        
        # Semester 3
        {"Kode": "MKDU003", "Nama": "Kewarganegaraan", "SKS": 2, "Semester": 3, "Jenis": "Teori", "CPL": "S4"},
        {"Kode": "ILK301", "Nama": "Machine Learning", "SKS": 3, "Semester": 3, "Jenis": "Teori+Praktikum", "CPL": "P3,KK3"},
        {"Kode": "ILK302", "Nama": "Jaringan Komputer", "SKS": 3, "Semester": 3, "Jenis": "Teori+Praktikum", "CPL": "P2,KK4"},
        {"Kode": "ILK303", "Nama": "Pemrograman Web", "SKS": 3, "Semester": 3, "Jenis": "Praktikum", "CPL": "KK1,KU3"},
        
        # Semester 4
        {"Kode": "MKDU004", "Nama": "Agama & Etika", "SKS": 2, "Semester": 4, "Jenis": "Teori", "CPL": "S3"},
        {"Kode": "ILK401", "Nama": "Rekayasa Perangkat Lunak", "SKS": 3, "Semester": 4, "Jenis": "Teori+Praktikum", "CPL": "KU3,KK1"},
        {"Kode": "ILK402", "Nama": "Sistem Operasi", "SKS": 3, "Semester": 4, "Jenis": "Teori", "CPL": "P2"},
        {"Kode": "ILK403", "Nama": "Keamanan Data", "SKS": 3, "Semester": 4, "Jenis": "Teori+Praktikum", "CPL": "KK4"},
    ]
    
    # Data Peminatan
    peminatan_data = {
        "Software Engineering": [
            {"Kode": "SE501", "Nama": "Pengembangan Game", "SKS": 3, "Semester": 5},
            {"Kode": "SE502", "Nama": "DevOps", "SKS": 3, "Semester": 5},
            {"Kode": "SE601", "Nama": "AR/VR Development", "SKS": 3, "Semester": 6},
        ],
        "Data Science": [
            {"Kode": "DS501", "Nama": "Big Data Analytics", "SKS": 3, "Semester": 5},
            {"Kode": "DS502", "Nama": "Data Visualization", "SKS": 3, "Semester": 5},
            {"Kode": "DS601", "Nama": "Machine Learning Lanjut", "SKS": 3, "Semester": 6},
        ],
        "Artificial Intelligence": [
            {"Kode": "AI501", "Nama": "Computer Vision", "SKS": 4, "Semester": 5},
            {"Kode": "AI502", "Nama": "Natural Language Processing", "SKS": 3, "Semester": 5},
            {"Kode": "AI601", "Nama": "Deep Learning", "SKS": 3, "Semester": 6},
        ],
        "Cybersecurity": [
            {"Kode": "CS501", "Nama": "Digital Forensics", "SKS": 4, "Semester": 5},
            {"Kode": "CS502", "Nama": "Ethical Hacking", "SKS": 3, "Semester": 5},
            {"Kode": "CS601", "Nama": "Cloud Security", "SKS": 3, "Semester": 6},
        ]
    }
    
    # Data Prasyarat
    prasyarat_data = {
        "ILK301": ["ILK102", "ILK202"],  # Machine Learning butuh Pemrograman Dasar dan Matematika Komputasi
        "ILK302": ["ILK402"],  # Jaringan Komputer butuh Sistem Operasi
        "ILK303": ["ILK102"],  # Pemrograman Web butuh Pemrograman Dasar
        "ILK401": ["ILK201"],  # RPL butuh Algoritma
        "SE501": ["ILK303"],   # Game Dev butuh Pemrograman Web
        "DS501": ["ILK203"],   # Big Data butuh Basis Data
        "AI501": ["ILK301"],   # Computer Vision butuh Machine Learning
    }
    
    return pl_data, cpl_data, mk_wajib, peminatan_data, prasyarat_data

# Fungsi untuk dashboard
def show_dashboard(pl_data, cpl_data, mk_wajib):
    st.markdown('<h1 class="main-header">🎓 Dashboard Kurikulum OBE Ilmu Komputer MNCU</h1>', unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total SKS", "145", "8 Semester")
    with col2:
        total_mk = len(mk_wajib) + sum(len(v) for v in cpl_data.values())
        st.metric("Total CPL", str(total_mk), "4 Domain")
    with col3:
        st.metric("Profil Lulusan", "5", "Spesialisasi")
    with col4:
        st.metric("MBKM SKS", "20-40", "Fleksibel")
    
    # Visualisasi 1: Distribusi SKS per Semester
    st.markdown('<div class="sub-header">📊 Distribusi SKS per Semester</div>', unsafe_allow_html=True)
    
    # Hitung SKS per semester
    semester_sks = {}
    for mk in mk_wajib:
        sem = mk["Semester"]
        semester_sks[sem] = semester_sks.get(sem, 0) + mk["SKS"]
    
    # Tambahkan SKS peminatan (rata-rata)
    for sem in range(5, 9):
        semester_sks[sem] = semester_sks.get(sem, 0) + 9  # Rata-rata SKS peminatan
    
    # Buat chart
    df_semester = pd.DataFrame({
        "Semester": list(semester_sks.keys()),
        "SKS": list(semester_sks.values())
    }).sort_values("Semester")
    
    fig1 = px.bar(df_semester, x="Semester", y="SKS", 
                  title="Distribusi SKS per Semester",
                  color="SKS",
                  color_continuous_scale="Viridis")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Visualisasi 2: Jenis Pembelajaran
    st.markdown('<div class="sub-header">🎯 Jenis Pembelajaran</div>', unsafe_allow_html=True)
    
    jenis_data = {"Teori": 0, "Praktikum": 0, "Teori+Praktikum": 0, "Praktisi": 0}
    for mk in mk_wajib:
        jenis_data[mk["Jenis"]] = jenis_data.get(mk["Jenis"], 0) + mk["SKS"]
    
    fig2 = go.Figure(data=[go.Pie(
        labels=list(jenis_data.keys()),
        values=list(jenis_data.values()),
        hole=.3
    )])
    fig2.update_layout(title="Distribusi Jenis Pembelajaran (SKS)")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Quick Stats
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("📋 Ringkasan Kurikulum"):
            st.write(f"**Total Mata Kuliah Wajib:** {len(mk_wajib)}")
            st.write(f"**Total Peminatan:** 4 bidang")
            st.write(f"**MBKM Minimum:** 20 SKS")
            st.write(f"**Masa Studi:** 8 Semester (4 Tahun)")
    
    with col2:
        with st.expander("🎓 Profil Lulusan"):
            for pl in pl_data:
                st.write(f"**{pl['Kode']}**: {pl['Profil']}")

# Fungsi untuk menampilkan Profil Lulusan
def show_profil_lulusan(pl_data):
    st.markdown('<h1 class="main-header">👥 Profil Lulusan Ilmu Komputer MNCU</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs([pl["Profil"] for pl in pl_data])
    
    for i, (tab, pl) in enumerate(zip(tabs, pl_data)):
        with tab:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Kode", pl["Kode"])
                st.metric("Bidang", pl["Profil"])
            
            with col2:
                st.write(f"**Deskripsi:** {pl['Deskripsi']}")
                
                # Contoh posisi karir
                karir = {
                    "PL1": ["Software Developer", "Web Developer", "Mobile App Developer", "Game Developer"],
                    "PL2": ["Data Analyst", "Business Intelligence", "Data Engineer", "Data Scientist"],
                    "PL3": ["AI Engineer", "Machine Learning Engineer", "NLP Specialist", "Computer Vision Engineer"],
                    "PL4": ["Cybersecurity Analyst", "Network Security Engineer", "Ethical Hacker", "Security Consultant"],
                    "PL5": ["IT Consultant", "Tech Entrepreneur", "Product Manager", "Project Manager IT"]
                }
                
                st.write("**Posisi Karir:**")
                for k in karir[pl["Kode"]]:
                    st.write(f"- {k}")
                
                # Skills required
                skills = {
                    "PL1": ["Programming", "Software Design", "Debugging", "Version Control"],
                    "PL2": ["Data Analysis", "Statistics", "SQL", "Data Visualization"],
                    "PL3": ["Machine Learning", "Python", "TensorFlow/PyTorch", "Mathematics"],
                    "PL4": ["Network Security", "Cryptography", "Penetration Testing", "Security Protocols"],
                    "PL5": ["Communication", "Business Analysis", "Project Management", "Entrepreneurship"]
                }
                
                st.write("**Kompetensi Kunci:**")
                cols = st.columns(2)
                for j, skill in enumerate(skills[pl["Kode"]]):
                    with cols[j % 2]:
                        st.success(f"✓ {skill}")

# Fungsi untuk menampilkan Struktur Kurikulum
def show_struktur_kurikulum(mk_wajib, peminatan_data):
    st.markdown('<h1 class="main-header">📚 Struktur Kurikulum 145 SKS</h1>', unsafe_allow_html=True)
    
    # Pilih semester
    semester = st.selectbox("Pilih Semester:", [1, 2, 3, 4, 5, 6, 7, 8])
    
    if semester <= 4:
        # Mata kuliah wajib
        mk_semester = [mk for mk in mk_wajib if mk["Semester"] == semester]
        
        st.markdown(f'<div class="semester-box">Semester {semester} - Mata Kuliah Wajib</div>', unsafe_allow_html=True)
        
        for mk in mk_semester:
            with st.expander(f"{mk['Kode']} - {mk['Nama']} ({mk['SKS']} SKS)"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Jenis:** {mk['Jenis']}")
                with col2:
                    st.write(f"**SKS:** {mk['SKS']}")
                with col3:
                    st.write(f"**CPL:** {mk['CPL']}")
                
                # Detail tambahan
                st.write("**Deskripsi:** Mata kuliah ini memberikan pemahaman tentang...")
                st.write("**Metode Pembelajaran:** Kuliah, Praktikum, Tugas, Project")
                st.write("**Evaluasi:** Tugas 30%, UTS 30%, UAS 40%")
    
    else:
        # Mata kuliah peminatan
        st.markdown(f'<div class="semester-box">Semester {semester} - Peminatan</div>', unsafe_allow_html=True)
        
        # Pilih peminatan
        peminatan = st.radio("Pilih Peminatan:", list(peminatan_data.keys()), horizontal=True)
        
        if peminatan:
            mk_peminatan = [mk for mk in peminatan_data[peminatan] if mk["Semester"] == semester]
            
            for mk in mk_peminatan:
                with st.expander(f"{mk['Kode']} - {mk['Nama']} ({mk['SKS']} SKS)"):
                    st.write(f"**Peminatan:** {peminatan}")
                    st.write(f"**Semester:** {mk['Semester']}")
                    st.write(f"**SKS:** {mk['SKS']}")
                    st.write("**CPL:** KK3, KU2, P3")
                    st.write("**Deskripsi:** Mata kuliah spesialisasi untuk mendukung profil lulusan...")
    
    # Total SKS
    total_sks = 0
    if semester <= 4:
        total_sks = sum(mk["SKS"] for mk in mk_wajib if mk["Semester"] == semester)
    else:
        total_sks = 9  # Rata-rata SKS peminatan + MBKM
    
    st.info(f"**Total SKS Semester {semester}: {total_sks} SKS**")

# Fungsi untuk menampilkan Prasyarat
def show_prasyarat(prasyarat_data, mk_wajib):
    st.markdown('<h1 class="main-header">🔗 Prasyarat Mata Kuliah</h1>', unsafe_allow_html=True)
    
    # Visualisasi graph prasyarat
    st.markdown("### Diagram Prasyarat Mata Kuliah")
    
    # Buat graph
    G = nx.DiGraph()
    
    # Tambahkan node dan edges
    for mk, prasyarat in prasyarat_data.items():
        for p in prasyarat:
            G.add_edge(p, mk)
    
    # Tambahkan node lain yang tidak memiliki prasyarat
    all_mk = set()
    for mk in mk_wajib:
        all_mk.add(mk["Kode"])
    
    for mk in all_mk:
        if mk not in G:
            G.add_node(mk)
    
    # Buat posisi layout
    pos = nx.spring_layout(G, seed=42)
    
    # Buat plotly figure
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
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
            colorscale='Viridis',
            size=20,
            color=list(range(len(G.nodes()))),
            line_width=2))
    
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Diagram Prasyarat Mata Kuliah',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabel prasyarat
    st.markdown("### Tabel Prasyarat")
    
    prasyarat_table = []
    for mk, prasyarat in prasyarat_data.items():
        prasyarat_table.append({
            "Mata Kuliah": mk,
            "Prasyarat": ", ".join(prasyarat),
            "Jumlah Prasyarat": len(prasyarat)
        })
    
    df_prasyarat = pd.DataFrame(prasyarat_table)
    st.dataframe(df_prasyarat, use_container_width=True)
    
    # Cek prasyarat untuk MK tertentu
    st.markdown("### Cek Prasyarat")
    
    selected_mk = st.selectbox("Pilih Mata Kuliah:", list(prasyarat_data.keys()))
    
    if selected_mk:
        st.write(f"**Mata Kuliah:** {selected_mk}")
        st.write(f"**Prasyarat:** {', '.join(prasyarat_data[selected_mk])}")
        
        # Contoh: apakah mahasiswa bisa ambil MK ini?
        col1, col2 = st.columns(2)
        with col1:
            mk_lulus = st.multiselect("Mata Kuliah yang sudah lulus:", 
                                     list(set([item for sublist in prasyarat_data.values() for item in sublist])))
        
        with col2:
            if set(prasyarat_data[selected_mk]).issubset(set(mk_lulus)):
                st.success("✅ Boleh mengambil mata kuliah ini!")
            elif mk_lulus:
                st.error("❌ Belum memenuhi semua prasyarat")
                missing = set(prasyarat_data[selected_mk]) - set(mk_lulus)
                st.write(f"Masih perlu: {', '.join(missing)}")

# Fungsi untuk menampilkan MBKM
def show_mbkm():
    st.markdown('<h1 class="main-header">🌐 Program MBKM (Merdeka Belajar)</h1>', unsafe_allow_html=True)
    
    # Informasi MBKM
    st.markdown("""
    ### 🎯 Skema Konversi SKS MBKM
    
    | Kegiatan MBKM | SKS | Konversi dari MK |
    |--------------|-----|------------------|
    | Magang Industri | 6-12 SKS | 2-4 MK Teori |
    | Proyek Independen | 3-6 SKS | 1-2 MK Pilihan |
    | Pertukaran Pelajar | 6-12 SKS | 2-4 MK Setara |
    | Kewirausahaan | 3-6 SKS | 1-2 MK Pilihan |
    | KKN Tematik | 3 SKS | 1 MK Wajib |
    | Sertifikasi | 3 SKS | 1 MK Pilihan |
    """)
    
    # Simulator MBKM
    st.markdown("### 📊 Simulator Konversi MBKM")
    
    col1, col2 = st.columns(2)
    
    with col1:
        kegiatan = st.selectbox(
            "Pilih Kegiatan MBKM:",
            ["Magang Industri", "Proyek Independen", "Pertukaran Pelajar", 
             "Kewirausahaan", "KKN Tematik", "Sertifikasi Profesional"]
        )
        
        durasi = st.slider("Durasi (jam):", 120, 480, 240, step=40)
        
    with col2:
        sks_dikonversi = min(12, durasi // 40)  # 40 jam = 1 SKS
        st.metric("SKS yang didapat", sks_dikonversi)
        
        mk_diganti = sks_dikonversi // 3
        st.metric("MK yang bisa dikonversi", mk_diganti)
    
    # Contoh konversi
    st.markdown("### 📝 Contoh Dokumen yang Diperlukan")
    
    docs_needed = {
        "Magang Industri": ["Surat Penerimaan Magang", "Logbook Kegiatan", 
                           "Laporan Magang", "Sertifikat", "Evaluasi Pembimbing"],
        "Proyek Independen": ["Proposal Proyek", "Progress Report", 
                             "Final Report", "Demo/Produk", "Presentasi"],
        "Sertifikasi": ["Sertifikat Resmi", "Syllabus Sertifikasi", 
                       "Nilai/Ujian", "Konversi Materi"]
    }
    
    if kegiatan in docs_needed:
        st.write("**Dokumen yang harus diserahkan:**")
        for doc in docs_needed[kegiatan]:
            st.write(f"✓ {doc}")
    
    # Timeline MBKM
    st.markdown("### 📅 Timeline MBKM yang Direkomendasikan")
    
    timeline_data = {
        "Semester 5": "Magang Industri (6 SKS)",
        "Semester 6": "Proyek Independen (6 SKS)",
        "Semester 7": "KKN Tematik (3 SKS)",
        "Semester 8": "Sertifikasi Profesional (3 SKS)"
    }
    
    for sem, kegiatan in timeline_data.items():
        st.write(f"**{sem}**: {kegiatan}")

# Fungsi untuk Simulasi KRS
def show_simulasi_krs(mk_wajib, peminatan_data, prasyarat_data):
    st.markdown('<h1 class="main-header">📝 Simulator KRS Online</h1>', unsafe_allow_html=True)
    
    # Input mahasiswa
    col1, col2 = st.columns(2)
    with col1:
        semester = st.number_input("Semester Saat Ini:", 1, 8, 3)
        ipk = st.slider("IPK:", 0.0, 4.0, 3.2)
    
    with col2:
        peminatan = st.selectbox("Peminatan:", list(peminatan_data.keys()))
        mbkm_plan = st.checkbox("Rencana Ambil MBKM Semester Ini")
    
    # Tampilkan MK yang tersedia
    st.markdown(f"### ✅ Mata Kuliah yang Tersedia Semester {semester}")
    
    available_mk = []
    
    # MK wajib untuk semester ini
    mk_semester = [mk for mk in mk_wajib if mk["Semester"] == semester]
    available_mk.extend(mk_semester)
    
    # MK peminatan untuk semester ini
    if semester >= 5:
        mk_peminatan = [mk for mk in peminatan_data[peminatan] if mk["Semester"] == semester]
        available_mk.extend(mk_peminatan)
    
    # Cek prasyarat untuk setiap MK
    mk_valid = []
    mk_invalid = []
    
    for mk in available_mk:
        mk_code = mk["Kode"]
        if mk_code in prasyarat_data:
            # Asumsikan semua prasyarat sudah dipenuhi (dalam simulasi sederhana)
            mk_valid.append(mk)
        else:
            mk_valid.append(mk)
    
    # Tampilkan MK yang bisa diambil
    selected_mk = []
    total_sks = 0
    
    st.write("**Pilih mata kuliah yang ingin diambil:**")
    
    for mk in mk_valid:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"{mk['Kode']} - {mk['Nama']}")
        with col2:
            st.write(f"{mk['SKS']} SKS")
        with col3:
            if st.checkbox("Ambil", key=mk['Kode']):
                selected_mk.append(mk)
                total_sks += mk["SKS"]
    
    # Validasi KRS
    st.markdown("### 📋 Validasi KRS")
    
    if selected_mk:
        st.write(f"**Total SKS yang diambil:** {total_sks} SKS")
        
        if total_sks < 18:
            st.warning("⚠️ Total SKS kurang dari 18 (minimum rekomendasi)")
        elif total_sks > 24:
            st.error("❌ Total SKS melebihi 24 (maksimum yang diizinkan)")
        else:
            st.success("✅ KRS valid!")
        
        # Tampilkan jadwal contoh
        st.markdown("### 🗓️ Contoh Jadwal Perkuliahan")
        
        jadwal_data = {
            "Hari": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"],
            "Pukul 08:00-10:00": [mk[0]["Nama"] if len(mk) > 0 else "-" for mk in [selected_mk[:1], selected_mk[1:2], selected_mk[2:3], selected_mk[3:4], selected_mk[4:5]]],
            "Pukul 10:00-12:00": [mk[0]["Nama"] if len(mk) > 0 else "-" for mk in [selected_mk[5:6], selected_mk[6:7], selected_mk[7:8], selected_mk[8:9], selected_mk[9:10]]],
            "Pukul 13:00-15:00": ["Praktikum" if i < len(selected_mk) else "-" for i in range(5)]
        }
        
        df_jadwal = pd.DataFrame(jadwal_data)
        st.dataframe(df_jadwal, use_container_width=True, hide_index=True)
    
    # Opsi MBKM
    if mbkm_plan and semester >= 5:
        st.markdown('<div class="mbkm-badge">OPTION MBKM</div>', unsafe_allow_html=True)
        st.info("Anda berencana mengambil MBKM. Konsultasikan dengan Dosen Pembimbing Akademik untuk konversi SKS.")

# Main App
def main():
    # Load data
    pl_data, cpl_data, mk_wajib, peminatan_data, prasyarat_data = load_data()
    
    # Routing berdasarkan menu
    if menu == "Dashboard":
        show_dashboard(pl_data, cpl_data, mk_wajib)
    
    elif menu == "Profil Lulusan":
        show_profil_lulusan(pl_data)
    
    elif menu == "Struktur Kurikulum":
        show_struktur_kurikulum(mk_wajib, peminatan_data)
    
    elif menu == "Prasyarat MK":
        show_prasyarat(prasyarat_data, mk_wajib)
    
    elif menu == "MBKM":
        show_mbkm()
    
    elif menu == "Simulasi KRS":
        show_simulasi_krs(mk_wajib, peminatan_data, prasyarat_data)
    
    elif menu == "Evaluasi OBE":
        st.markdown('<h1 class="main-header">📈 Evaluasi Pencapaian OBE</h1>', unsafe_allow_html=True)
        
        # Upload data mahasiswa (contoh)
        uploaded_file = st.file_uploader("Upload Data Nilai Mahasiswa (CSV)", type="csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("### Data Nilai Mahasiswa")
            st.dataframe(df.head())
            
            # Analisis pencapaian CPL
            st.write("### 📊 Analisis Pencapaian CPL")
            
            # Contoh visualisasi
            cpl_labels = ["S1", "S2", "S3", "S4", "P1", "P2", "P3", "P4", 
                         "KU1", "KU2", "KU3", "KU4", "KK1", "KK2", "KK3", "KK4", "KK5"]
            cpl_values = [85, 90, 88, 82, 78, 85, 80, 75, 88, 90, 85, 82, 80, 78, 85, 82, 80]
            
            fig = go.Figure(data=[go.Bar(
                x=cpl_labels,
                y=cpl_values,
                marker_color=cpl_values,
                text=cpl_values,
                textposition='auto',
            )])
            
            fig.update_layout(
                title="Persentase Pencapaian CPL",
                xaxis_title="Capaian Pembelajaran Lulusan",
                yaxis_title="Persentase Pencapaian (%)",
                yaxis_range=[0, 100]
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    elif menu == "Export Data":
        st.markdown('<h1 class="main-header">📤 Export Data Kurikulum</h1>', unsafe_allow_html=True)
        
        # Pilihan format export
        export_format = st.radio("Pilih Format Export:", ["Excel", "JSON", "PDF Report"])
        
        # Data yang bisa di-export
        data_options = st.multiselect(
            "Pilih data yang akan di-export:",
            ["Profil Lulusan", "CPL", "Mata Kuliah Wajib", "Peminatan", "Prasyarat", "MBKM"]
        )
        
        if st.button("Generate Export"):
            with st.spinner("Mempersiapkan data..."):
                # Buat DataFrame untuk Excel
                if "Mata Kuliah Wajib" in data_options:
                    df_mk = pd.DataFrame(mk_wajib)
                
                if "Peminatan" in data_options:
                    # Flatten data peminatan
                    peminatan_list = []
                    for p, mk_list in peminatan_data.items():
                        for mk in mk_list:
                            mk["Peminatan"] = p
                            peminatan_list.append(mk)
                    df_peminatan = pd.DataFrame(peminatan_list)
                
                if export_format == "Excel":
                    # Create Excel writer
                    import io
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        if "Mata Kuliah Wajib" in data_options:
                            df_mk.to_excel(writer, sheet_name='MK_Wajib', index=False)
                        if "Peminatan" in data_options:
                            df_peminatan.to_excel(writer, sheet_name='Peminatan', index=False)
                    
                    buffer.seek(0)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Excel File",
                        data=buffer,
                        file_name="kurikulum_ilkom_mncu.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                elif export_format == "JSON":
                    import json
                    
                    export_data = {}
                    if "Profil Lulusan" in data_options:
                        export_data["profil_lulusan"] = pl_data
                    if "Mata Kuliah Wajib" in data_options:
                        export_data["mata_kuliah_wajib"] = mk_wajib
                    
                    json_str = json.dumps(export_data, indent=2)
                    
                    st.download_button(
                        label="📥 Download JSON File",
                        data=json_str,
                        file_name="kurikulum_ilkom_mncu.json",
                        mime="application/json"
                    )
                
                st.success("✅ Data siap diunduh!")

# Run the app
if __name__ == "__main__":
    main()
