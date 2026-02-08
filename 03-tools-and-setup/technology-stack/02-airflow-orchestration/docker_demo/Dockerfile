# 1️⃣ Gunakan base image resmi Python
FROM python:3.12-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy file proyek
COPY . .

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Jalankan script
CMD ["python", "main.py"]