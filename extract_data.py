import easyocr
import re
import glob
import os

reader = easyocr.Reader(['id', 'en'])

files = (
    glob.glob("struk*.jpg") +
    glob.glob("struk*.jpeg") +
    glob.glob("struk*.png")
)

print("Jumlah struk:", len(files))


def cari_tanggal(teks_list):

    pola = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{2}/\d{2}/\d{4}',
        r'\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}'
    ]

    for teks in teks_list:
        for pola_tanggal in pola:
            cocok = re.search(pola_tanggal, teks)
            if cocok:
                return cocok.group()

    return "Tidak ditemukan"


def ubah_nominal(teks):

    teks = teks.replace("Rp", "")
    teks = teks.replace("rp", "")
    teks = teks.replace(" ", "")
    teks = teks.replace(".", "")

    if "," in teks:
        bagian = teks.split(",")

        if len(bagian[-1]) == 2:
            teks = "".join(bagian[:-1])
        else:
            teks = teks.replace(",", "")

    teks = re.sub(r'[^0-9]', '', teks)

    if teks:
        return int(teks)

    return None


def cari_total(teks_list):

    # ==========================================
    # 1. CARI GRAND TOTAL
    # ==========================================

    for i, teks in enumerate(teks_list):

        teks_bersih = teks.lower().strip()
        teks_bersih = teks_bersih.replace("]", "l")

        if "grand total" in teks_bersih:

            # Cek angka pada baris GRAND TOTAL
            kandidat = teks

            angka = re.findall(
                r'\d[\d.,]*',
                kandidat
            )

            if angka:

                nominal = ubah_nominal(
                    angka[-1]
                )

                if nominal and nominal >= 100:
                    return nominal

            # Cek SATU baris setelahnya
            if i + 1 < len(teks_list):

                kandidat = teks_list[i + 1]

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

                    if nominal and nominal >= 100:
                        return nominal


    # ==========================================
    # 2. CARI TOTAL
    # ==========================================

    for i, teks in enumerate(teks_list):

        teks_bersih = teks.lower().strip()
        teks_bersih = teks_bersih.replace("]", "l")

        # Jangan sampai SUBTOTAL dianggap TOTAL
        if "subtotal" in teks_bersih:
            continue

        if re.search(r'\btotal\b', teks_bersih):

            # ----------------------------------
            # Cek angka pada baris TOTAL
            # ----------------------------------

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

                if nominal and nominal >= 100:
                    return nominal


            # ----------------------------------
            # Cek SATU baris setelah TOTAL
            # ----------------------------------

            if i + 1 < len(teks_list):

                kandidat = teks_list[i + 1]

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

                    if nominal and nominal >= 100:
                        return nominal

    return None


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
        "spbu"
    ]

    kandidat = []

    for posisi, data in enumerate(data_ocr[:10]):

        teks = data[1].strip()
        confidence = data[2]

        teks_lower = teks.lower()

        if len(teks) < 3:
            continue

        if confidence < 0.20:
            continue

        if re.fullmatch(r'[\d\s.,:/-]+', teks):
            continue

        if re.search(
            r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}',
            teks
        ):
            continue

        if any(kata in teks_lower for kata in kata_dihindari):
            continue

        skor = 0

        skor += confidence * 10
        skor += max(0, 5 - posisi)

        if any(kata in teks_lower for kata in kata_toko):
            skor += 8

        jumlah_huruf = len(
            re.findall(r'[A-Za-z]', teks)
        )

        if jumlah_huruf >= 4:
            skor += 2

        if jumlah_huruf >= 7:
            skor += 2

        kandidat.append(
            (skor, teks, confidence)
        )

    if not kandidat:
        return "Tidak ditemukan"

    kandidat.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return kandidat[0][1]


for file in files:

    print("\n")
    print("=" * 50)
    print("FILE:", os.path.basename(file))
    print("=" * 50)

    hasil = reader.readtext(
        file,
        detail=1,
        paragraph=False
    )

    teks_list = []

    for data in hasil:
        teks_list.append(data[1])

    toko = cari_toko(hasil)
    tanggal = cari_tanggal(teks_list)
    total = cari_total(teks_list)

    print("\n--- HASIL EKSTRAKSI ---")

    print("Toko    :", toko)
    print("Tanggal :", tanggal)

    if total:
        print(
            "Total   : Rp" +
            format(total, ",").replace(",", ".")
        )
    else:
        print("Total   : Tidak ditemukan")