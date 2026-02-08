from google.cloud import bigquery

client = bigquery.Client()

table = "weather-cloud-lab.weather_raw.sample_insert"

# row = [
#     {'name':"Sanju Tipes","score":90},
#     {'name':"Doni Montero","score":99}
# ]

row = [
    {'name': "Aura Kasih", "score": 85},
    {'name': "Bima Sakti", "score": 78},
    {'name': "Citra Dewi", "score": 92},
    {'name': "Dian Kusuma", "score": 65},
    {'name': "Eko Prasetyo", "score": 88},
    {'name': "Fajar Nugraha", "score": 95},
    {'name': "Gita Paramita", "score": 71},
    {'name': "Hari Sudarsono", "score": 83},
    {'name': "Indah Permata", "score": 98},
    {'name': "Joko Susilo", "score": 75},
    {'name': "Kiki Amalia", "score": 80},
    {'name': "Lina Agustin", "score": 89},
    {'name': "Maya Sari", "score": 93},
    {'name': "Nanda Pratama", "score": 77},
    {'name': "Oscar Wijaya", "score": 91},
    {'name': "Putri Amelia", "score": 68},
    {'name': "Rendra Hadi", "score": 86},
    {'name': "Santi Monica", "score": 97},
    {'name': "Taufik Hidayat", "score": 70},
    {'name': "Umar Bakri", "score": 84},
    {'name': "Vina Oktavia", "score": 96},
    {'name': "Wawan Setiawan", "score": 73},
    {'name': "Yuni Kartika", "score": 82},
    {'name': "Zaky Siregar", "score": 94},
    {'name': "Agus Salim", "score": 76},
    {'name': "Bambang Pamungkas", "score": 87},
    {'name': "Cinta Laura", "score": 69},
    {'name': "Dimas Aditya", "score": 90},
    {'name': "Elsa Melati", "score": 74},
    {'name': "Farid Hasan", "score": 81},
    {'name': "Gatot Subroto", "score": 99},
    {'name': "Hesti Purwadinata", "score": 66},
    {'name': "Irfan Hakim", "score": 95},
    {'name': "Jenny Rahman", "score": 79},
    {'name': "Kevin Sanjaya", "score": 88},
    {'name': "Luthfi Aulia", "score": 92},
    {'name': "Maudy Ayunda", "score": 72},
    {'name': "Nino Kuya", "score": 85},
    {'name': "Olla Ramlan", "score": 98},
    {'name': "Pasha Ungu", "score": 67},
    {'name': "Raffi Ahmad", "score": 91},
    {'name': "Sherina Munaf", "score": 70},
    {'name': "Teuku Wisnu", "score": 83},
    {'name': "Uut Permatasari", "score": 94},
    {'name': "Vicky Prasetyo", "score": 75},
    {'name': "Wulan Guritno", "score": 80},
    {'name': "Yayan Ruhian", "score": 93},
    {'name': "Zianida Putri", "score": 78},
    {'name': "Andi Lau", "score": 89},
    {'name': "Budi Doremi", "score": 97}
]

job = client.insert_rows_json(table,row)

if job == []:
    print(f"✅ Insert success for {len(row)} rows")
else:
    print("❌ Error:", job)