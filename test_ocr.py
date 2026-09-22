import easyocr

# Membuat OCR reader
reader = easyocr.Reader(['id', 'en'])

# Baca gambar hasil preprocessing
hasil = reader.readtext(
    'struk2.jpg',
    detail=1,
    paragraph=False
)

print("\n=== HASIL OCR ===\n")

for data in hasil:
    teks = data[1]
    confidence = data[2]

    print("Teks       :", teks)
    print("Confidence :", round(confidence, 2))
    print("-" * 40)