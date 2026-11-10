# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011-2012) beserta dashboard interaktif Streamlit.

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv      (data per jam, sudah bersih)
| ├───day_clean.csv      (data harian, sudah bersih)
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment
```
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Menjalankan Notebook
```
jupyter notebook notebook.ipynb
```
Jalankan dari folder `submission` agar path `data/` dan `dashboard/` terbaca.

## Menjalankan Dashboard
```
cd submission
streamlit run dashboard/dashboard.py
```
Dashboard terbuka di `http://localhost:8501`.
