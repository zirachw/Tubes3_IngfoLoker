<h1 align="center"> Tugas Besar 3 IF2211 Strategi Algoritma </h1>
<h1 align="center">Pemanfaatan Pattern Matching untuk Membangun Sistem ATS (Applicant Tracking System) Berbasis CV Digital</h1>

## Deskripsi Algoritma KMP dan Boyer-Moore pada Program
### Langkah KMP
Secara algoritmik, tahapan KMP dapat diuraikan sebagai berikut:
1. Pra-proses Pola (Konstruksi Border Function):
Inisialisasi border[0] = 0. Lakukan iterasi terhadap pola untuk menghitung
nilai Border Function pada setiap indeks dengan membandingkan karakter
pola terkini dengan karakter pada posisi len. Jika karakter sama, tingkatkan
len dan simpan ke border[i]; jika berbeda dan len 6 = 0, mundurkan len ke
border[len-1]; jika len = 0, simpan border[i] = 0 dan lanjutkan iterasi.
2 IF2211 - Strategi Algoritma
2. Pencarian di Teks:
Selama indeks teks i < n:
j 0 1 2 3 4 5
P[j] a b a c a b
k 0 0 2 3 4
border[k] 0 0 1 0 1
• Jika P[j] = T[i], majukan kedua indeks i++ dan j++.
• Jika j = m, pola ditemukan pada posisi i  j; simpan posisi tersebut dan
set j = border[j-1] untuk mencari kecocokan berikutnya.
• Jika terjadi mismatch dan j 6 = 0, geser pola dengan j = border[j-1].
• Jika terjadi mismatch dan j = 0, majukan indeks teks i++.
3. Basis:
Proses berakhir ketika indeks teks mencapai n, sehingga seluruh teks telah
diperiksa.

### Langkah Boyer-Moore
Secara algoritmik, tahapan Boyer–Moore dapat diurai menjadi:
1. Pra-proses Pola
Bangun Last Occurrence Table L(x) untuk setiap karakter alfabet dan
tabel Good Suffix guna menentukan pergeseran minimal saat sufiks cocok
sebelumnya.
Karakter (x) a b c d
L(x) 4 5 3 -1
2. Pencarian di Teks
Bandingkan karakter pola dan teks dari kanan ke kiri. Jika semua karakter
cocok, laporkan posisi kecocokan lalu geser pola menggunakan Good Suffix.
Jika mismatch pada posisi j, hitung
shift
BC
= j  L(T[i]); shift
kemudian geser pola sebesar max(shift
BC
GS
; shift
= goodSuffix[j];
; 1) dan ulangi proses.
3. Basis
GS
Pencarian selesai ketika indeks awal pola melampaui n  m.
Gambar 3: Ilustrasi pergerakan pola selama proses pencarian Boyer-Moore
Algoritma Boyer–Moore banyak dipakai pada utilitas pencarian teks (grep,
diff ), editor kode, kompresi data, dan analisis bioinformatika berkat kemampuannya
melompati bagian teks yang panjang tanpa pemeriksaan karakter per karakter


## Requirement
- uv package


## Command Run Program
1. Clone repository ini 
2. Jalankan uv sync
```bash
uv sync
```
3. Buat env
```bash
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=

# PHPMyAdmin Configuration
PHP_HOST=localhost
PHP_PORT=8080

# FF3 Cipher Parameters
ENABLE_FF3=true
FF3_KEY=EF4359D8D580AA4F7F036D6F04FC6A94
FF3_TWEAK=D8E7920AFA330A73

# Data Management
ENABLE_SAVE=false
APPLICANT_COUNT = 30
DATA_FOLDER = data

ENABLE_DEMO=true
```

2. Buka docker desktop dan lakukan Docker Compose Up
    ```
    docker-compose up -d
    ```
3. Jalankan di localhost:
    ```bash
    uv run -m src.main
    ```
4. Aplikasi dapat digunakan


## Authors
### **Kelompok "APA AJA UDAH"**
|   NIM    |                  Nama                  |
| :------: | :-------------------------------------:|
| 13523004 |              Razi Rachman              |
| 13523114 |             Guntara Hambali            |
| 13523119 |           Reza Ahmad         |
