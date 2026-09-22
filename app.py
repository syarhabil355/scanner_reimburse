import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Scanner Reimburse",
    page_icon="🧾",
    layout="centered"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
}

.block-container {
    max-width: 900px;
    padding-top: 95px;
    padding-bottom: 40px;
}


/* Navbar */

.custom-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;

    height: 60px;

    background-color: #161b22;
    border-bottom: 1px solid #30363d;

    display: flex;
    align-items: center;
    justify-content: center;

    z-index: 999999;
}

.navbar-title {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
}


/* Header */

.header {
    text-align: center;
    margin-bottom: 35px;
}

.header-title {
    color: #ffffff;
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 8px;
}

.header-subtitle {
    color: #9ca3af;
    font-size: 15px;
    line-height: 1.6;
}


/* Section */

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 25px;
    margin-bottom: 12px;
}


/* Upload */

[data-testid="stFileUploader"] {
    background-color: #161b22;
    border: 1px dashed #4b5563;
    border-radius: 12px;
    padding: 12px;
}


/* Button */

.stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #374151;

    padding: 10px 18px;

    font-size: 15px;
    font-weight: 700;

    background-color: #ffffff;
    color: #111827;
}

.stButton > button:hover {
    background-color: #d1d5db;
    color: #111827;
}


/* Metric */

[data-testid="stMetric"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
}

[data-testid="stMetricLabel"] {
    color: #9ca3af;
}

[data-testid="stMetricValue"] {
    color: #ffffff;
}


/* Footer */

.footer {
    text-align: center;
    color: #6b7280;
    font-size: 12px;
    margin-top: 45px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVBAR
# =========================================================

st.html("""
<div class="custom-navbar">
    <div class="navbar-title">
        🧾 Scanner Reimburse
    </div>
</div>
""")


# =========================================================
# HEADER
# =========================================================

st.html("""
<div class="header">

    <div class="header-title">
        Scanner Reimburse
    </div>

    <div class="header-subtitle">
        Scan dan kelola data reimbursement dari foto struk
        secara otomatis menggunakan teknologi OCR.
    </div>

</div>
""")


# =========================================================
# EASY OCR
# =========================================================

@st.cache_resource
def load_reader():

    reader = easyocr.Reader(
        ['id', 'en'],
        gpu=False
    )

    return reader


reader = load_reader()


# =========================================================
# CARI TANGGAL
# =========================================================

def cari_tanggal(teks_list):

    pola = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{2}/\d{2}/\d{4}',
        r'\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}'
    ]

    for teks in teks_list:

        for pola_tanggal in pola:

            cocok = re.search(
                pola_tanggal,
                teks
            )

            if cocok:
                return cocok.group()

    return "Tidak ditemukan"


# =========================================================
# UBAH NOMINAL
# =========================================================

def ubah_nominal(teks):

    teks = teks.replace("Rp", "")
    teks = teks.replace("rp", "")
    teks = teks.replace(" ", "")
    teks = teks.replace(".", "")

    if "," in teks:

        bagian = teks.split(",")

        if len(bagian[-1]) == 2:

            teks = "".join(
                bagian[:-1]
            )

        else:

            teks = teks.replace(",", "")

    teks = re.sub(
        r'[^0-9]',
        '',
        teks
    )

    if teks:
        return int(teks)

    return None


# =========================================================
# CARI TOTAL
# =========================================================

def cari_total(teks_list):

    def normalisasi_total(teks):

        teks = teks.lower()

        teks = teks.replace(
            "tolal",
            "total"
        )

        teks = teks.replace(
            "belanje",
            "belanja"
        )

        teks = teks.replace(
            "tota]",
            "total"
        )

        teks = teks.replace(
            "tota1",
            "total"
        )

        return teks


    # Cari berdasarkan kata total

    for i, teks in enumerate(teks_list):

        teks_bersih = normalisasi_total(
            teks.strip()
        )

        if "subtotal" in teks_bersih:
            continue


        if (
            "grand total" in teks_bersih
            or "total belanja" in teks_bersih
            or "total harga" in teks_bersih
            or "total bayar" in teks_bersih
            or re.search(
                r'\btotal\b',
                teks_bersih
            )
        ):

            kandidat = teks

            kandidat = re.sub(
                r'\s+([.,])',
                r'\1',
                kandidat
            )

            angka = re.findall(
                r'\d[\d.,]*',
                kandidat
            )


            if angka:

                nominal = ubah_nominal(
                    angka[-1]
                )

                if (
                    nominal
                    and nominal >= 100
                ):
                    return nominal


            # Cek baris setelah total

            for j in range(
                i + 1,
                min(i + 3, len(teks_list))
            ):

                kandidat = teks_list[j]

                kandidat = re.sub(
                    r'\s+([.,])',
                    r'\1',
                    kandidat
                )

                angka = re.findall(
                    r'\d[\d.,]*',
                    kandidat
                )


                if angka:

                    nominal = ubah_nominal(
                        angka[-1]
                    )

                    if (
                        nominal
                        and nominal >= 100
                    ):
                        return nominal


    # Fallback cari Rp

    for teks in teks_list:

        if "rp" in teks.lower():

            kandidat = teks

            kandidat = re.sub(
                r'\s+([.,])',
                r'\1',
                kandidat
            )

            angka = re.findall(
                r'\d[\d.,]*',
                kandidat
            )


            if angka:

                nominal = ubah_nominal(
                    angka[-1]
                )

                if (
                    nominal
                    and nominal >= 100
                ):
                    return nominal


    return None


# =========================================================
# CARI TOKO
# =========================================================

def cari_toko(data_ocr):

    kata_dihindari = [

        "jl",
        "jalan",
        "alamat",
        "surabaya",
        "bekasi",
        "bogor",
        "jawa",
        "malang",
        "ruko",

        "shift",
        "kasir",
        "operator",

        "telp",
        "phone",
        "hp",

        "www",
        "http",

        "tanggal",
        "waktu",
        "trans",
        "no.",
        "nomor",

        "total",
        "subtotal",

        "cash",
        "tunai",
        "payment",
        "pembayaran"
    ]


    kata_toko = [

        "apotek",
        "cafe",
        "shop",
        "store",
        "mart",
        "minimarket",
        "restaurant",
        "resto",
        "bakery",
        "clinic",
        "klinik",
        "hotel",
        "spbu",
        "pertamina"
    ]


    kandidat = []


    for posisi, data in enumerate(
        data_ocr[:10]
    ):

        teks = data[1].strip()

        confidence = data[2]

        teks_lower = teks.lower()


        if len(teks) < 3:
            continue


        if confidence < 0.20:
            continue


        if re.fullmatch(
            r'[\d\s.,:/-]+',
            teks
        ):
            continue


        if re.search(
            r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}',
            teks
        ):
            continue


        if any(
            kata in teks_lower
            for kata in kata_dihindari
        ):
            continue


        skor = 0

        skor += confidence * 10

        skor += max(
            0,
            5 - posisi
        )


        if any(
            kata in teks_lower
            for kata in kata_toko
        ):

            skor += 8


        jumlah_huruf = len(
            re.findall(
                r'[A-Za-z]',
                teks
            )
        )


        if jumlah_huruf >= 4:
            skor += 2


        if jumlah_huruf >= 7:
            skor += 2


        kandidat.append(
            (
                skor,
                teks,
                confidence
            )
        )


    if not kandidat:
        return "Tidak ditemukan"


    kandidat.sort(
        key=lambda x: x[0],
        reverse=True
    )


    return kandidat[0][1]


# =========================================================
# UPLOAD
# =========================================================

st.markdown(
    '<div class="section-title">📤 Upload Foto Struk</div>',
    unsafe_allow_html=True
)


uploaded_files = st.file_uploader(

    "Pilih satu atau beberapa foto struk",

    type=[
        "jpg",
        "jpeg",
        "png"
    ],

    accept_multiple_files=True
)


# =========================================================
# INFO FILE
# =========================================================

if uploaded_files:

    st.info(
        "📄 "
        + str(len(uploaded_files))
        + " foto struk siap diproses."
    )


# =========================================================
# BUTTON SCAN
# =========================================================

if st.button(
    "🔍 Scan Semua Struk"
):

    if not uploaded_files:

        st.warning(
            "Silakan upload foto struk terlebih dahulu."
        )

    else:

        hasil_tabel = []

        progress_bar = st.progress(0)

        status_text = st.empty()

        total_file = len(
            uploaded_files
        )


        # =============================================
        # PROSES SEMUA FOTO
        # =============================================

        for nomor, uploaded_file in enumerate(
            uploaded_files,
            start=1
        ):

            status_text.text(
                "Sedang memproses "
                + uploaded_file.name
                + "..."
            )


            # Baca gambar

            image = Image.open(
                uploaded_file
            ).convert("RGB")


            image_np = np.array(
                image
            )


            # OCR

            data_ocr = reader.readtext(
                image_np
            )


            # Ambil semua teks

            teks_list = []

            for data in data_ocr:

                teks_list.append(
                    data[1]
                )


            # Ekstraksi

            toko = cari_toko(
                data_ocr
            )

            tanggal = cari_tanggal(
                teks_list
            )

            total = cari_total(
                teks_list
            )


            # Format total

            if total is not None:

                total_format = (
                    "Rp"
                    + f"{total:,}"
                    .replace(",", ".")
                )

            else:

                total_format = (
                    "Tidak ditemukan"
                )


            # Simpan hasil

            hasil_tabel.append({

                "No": nomor,

                "File": uploaded_file.name,

                "Toko": toko,

                "Tanggal": tanggal,

                "Total": total_format

            })


            # Progress

            progress_bar.progress(
                nomor / total_file
            )


        # =============================================
        # SELESAI
        # =============================================

        status_text.success(
            "✅ Semua struk berhasil diproses."
        )


        # =============================================
        # HASIL SCAN
        # =============================================

        st.markdown(
            '<div class="section-title">📋 Hasil Scan</div>',
            unsafe_allow_html=True
        )


        st.dataframe(

            hasil_tabel,

            use_container_width=True,

            hide_index=True

        )


        # =============================================
        # HITUNG TOTAL
        # =============================================

        total_semua = 0

        jumlah_berhasil = 0


        for hasil in hasil_tabel:

            if (
                hasil["Total"]
                != "Tidak ditemukan"
            ):

                angka = re.sub(
                    r'[^0-9]',
                    '',
                    hasil["Total"]
                )


                if angka:

                    total_semua += int(
                        angka
                    )

                    jumlah_berhasil += 1


        # =============================================
        # RINGKASAN
        # =============================================

        st.markdown(
            '<div class="section-title">📊 Ringkasan</div>',
            unsafe_allow_html=True
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Total Struk",
                len(hasil_tabel)
            )


        with col2:

            st.metric(
                "Berhasil Dibaca",
                jumlah_berhasil
            )


        with col3:

            total_format = (
                "Rp"
                + f"{total_semua:,}"
                .replace(",", ".")
            )


            st.metric(
                "Total Reimburse",
                total_format
            )


        # =============================================
        # TOTAL REIMBURSEMENT
        # =============================================

        st.markdown(
            '<div class="section-title">💰 Total Reimbursement</div>',
            unsafe_allow_html=True
        )


        st.success(
            "Total reimbursement: Rp"
            + f"{total_semua:,}"
            .replace(",", ".")
        )


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">
    Scanner Reimburse • OCR berbasis EasyOCR & OpenCV
</div>
""")