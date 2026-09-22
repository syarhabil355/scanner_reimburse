import easyocr
import glob
import os

# Membuat OCR reader satu kali
reader = easyocr.Reader(['id', 'en'])

# Mencari semua file gambar struk
files = glob.glob("struk*.jpg")

print("Jumlah struk ditemukan:", len(files))

for file in files:

    print("\n================================")
    print("MEMBACA:", os.path.basename(file))
    print("================================")

    hasil = reader.readtext(
        file,
        detail=1,
        paragraph=False
    )

    for data in hasil:
        teks = data[1]
        confidence = data[2]

        print(
            teks,
            "| confidence:",
            round(confidence, 2)
        )