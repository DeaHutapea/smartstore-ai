# Laporan Evaluasi Teknis SmartStore AI — Tugas 3

**Mata kuliah:** 10S3001 Kecerdasan Buatan (+P)

**Tugas:** Tugas 3 — Milestone 3, Basis Pengetahuan Korpus & Vector Semantic Search

**Kelompok:** Grup 14

**Tanggal acuan sumber:** 6 November 2026

**Status:** Implementasi dan evaluasi teknis

## 1. Tujuan dan kesesuaian dengan luaran T03

Milestone ini membangun korpus bisnis 12 dokumen, pipeline ekstraksi dan
pembersihan teks, word-aware chunking dengan overlap, Sentence-Transformers,
indeks ChromaDB persisten, dan evaluasi pencarian terhadap kueri relevan,
ambigu, dan out-of-domain. Keempat luaran tersebut sesuai dengan rincian
tugas pada PDF T03.

| Luaran tugas | Artefak |
|---|---|
| Korpus 10–15 dokumen | 4 regulasi + 8 dokumen kebijakan pada `data/corpus/corpus_manifest.csv`; sumber marketplace disediakan lokal dan tidak didistribusikan di Git |
| Ingestion dan chunking | `src/knowledge/corpus_loader.py`, `src/knowledge/chunker.py`, `scripts/build_index.py` |
| Embedding dan indeks persisten | `src/knowledge/embedder.py`, `src/knowledge/vector_store.py`, direktori runtime `chroma_db/` |
| Benchmark relevansi, ambiguitas, dan OOD | `data/benchmark_queries.json`, `scripts/run_benchmark.py`, `scripts/benchmark.py`, hasil pada `reports/` |

## 2. Korpus dan prapemrosesan

Korpus terdiri dari 12 dokumen terdaftar: regulasi konsumen, PMSE, PDP, dan
layanan pos komersial; serta dokumen kebijakan marketplace. Loader hanya
memasukkan keputusan `KEEP`, `KEEP_PROVISIONAL`, dan `REVISE`. Ekstraksi PDF
menggunakan PyMuPDF, Markdown/TXT dibaca langsung, dan pembersihan menghapus
noise web, nomor halaman, pemenggalan kata, serta whitespace berlebih.
Dokumen pendek dan sumber yang hilang dilaporkan, bukan diam-diam dianggap
berhasil.

URL dan tanggal akses seluruh dokumen terdaftar dicatat di manifest. URL
regulasi diverifikasi di portal resmi; empat snapshot Markdown Tokopedia
memuat URL dan tanggal pada front matter. Metadata PDF MKT005–MKT008
menyediakan tanggal snapshot; tautan internal memberi URL kategori untuk
MKT005–MKT007 dan URL artikel untuk MKT008. URL artikel utama Shopee
MKT005–MKT007 belum dapat diidentifikasi dari snapshot, sehingga statusnya
tetap dinamis/tidak diverifikasi dan tidak boleh dipakai untuk menyatakan
kebijakan masih berlaku. Detail provenance ada di `docs/corpus_sources.md`.

PDF/teks marketplace dan hasil ekstraksinya dikecualikan dari Git karena izin
redistribusi belum dipastikan. Sumber lokal yang telah tersedia dipertahankan
untuk evaluasi; clone baru perlu menyiapkan sumber yang berhak digunakan
sebelum indeks lengkap dapat dibangun. Lihat `docs/corpus_sources.md`.

## 3. Chunking, embedding, dan penyimpanan

Chunker memprioritaskan batas kalimat, menggabungkan kalimat sampai target
ukuran, mempertahankan overlap dalam kata antar-chunk, serta memecah kalimat
panjang berdasarkan batas kata. Ablation memakai E5-small pada ukuran
180/36 dan 120/24, serta multilingual MiniLM pada 80/16 dan 120/24
(ukuran/overlap dalam kata). Jumlah chunk pada snapshot korpus masing-masing
302, 449, 688, dan 449; angka ini dapat direproduksi dengan `scripts/run_all.py`.

Pemilihan 180/36 sebagai konfigurasi acuan memberi unit konteks lebih panjang
dengan overlap 20% untuk menjaga konteks lintas batas. Ia bukan klaim optimum
universal: hasil benchmark serta perbedaan model dan ukuran chunk harus
dibaca bersama pada `reports/summary_ablation.md`. Pada benchmark holdout final,
semua 8 kueri synonym berhasil pada Hit@1 untuk E5 180/36; konfigurasi ini
dipakai sebagai acuan pelaporan, bukan karena angka tersebut membuktikan
keunggulan universal. Tokenizer E5-small lokal
diukur pada seluruh konfigurasi; batas 512 token tidak terlampaui (konfigurasi
180/36 maksimum 379 token). Tokenizer MiniLM tidak tersedia lokal ketika diuji,
jadi risiko pemotongan pada batas model 128 token belum terukur.

Embedding dinormalisasi L2; E5 memakai prefix `query:` dan `passage:`.
ChromaDB menggunakan `PersistentClient`, cosine distance, koleksi terpisah
per model/konfigurasi, `upsert` idempoten, dan metadata sumber/dokumen/chunk
untuk filter atau hybrid search.

## 4. Benchmark dan ground truth

`data/benchmark_queries.json` adalah satu-satunya sumber resmi: 16 kueri,
terdiri dari 8 kueri synonym, 3 ambiguous, dan 5 OOD. Label dokumen
menggunakan `document_id` manifest dan diperiksa terhadap korpus yang
diindeks. Benchmark CSV 24 kueri lama tidak lagi digunakan agar tidak ada
dua sumber kebenaran. OOD tidak memiliki dokumen relevan dan dievaluasi
terutama melalui keputusan tolak/terima.

Threshold tidak dicari pada kueri holdout. `scripts/calibrate_threshold.py`
memilih threshold dari dataset development terpisah di
`data/ood_calibration_queries.json` dengan balanced accuracy. Nilai untuk
E5-small 180/36 adalah 0.850363. Dataset dev hanya 7 kueri per kelas; hasil
dev bukan estimasi performa produksi. Untuk konfigurasi lain, kalibrasikan
ambang tersendiri.

Metrik retrieval menghitung Precision@K, Recall@K, dan MRR untuk kueri
in-domain. Untuk OOD, positif berarti kueri OOD yang ditolak; laporan
menghitung precision, recall, F1, dan jumlah false rejection/missed rejection.
Analisis cosine menghasilkan statistik per kategori serta boxplot dan
histogram in-domain vs OOD.

## 5. Hasil dan analisis

Hasil terbaru disimpan sebagai:

- `reports/summary_ablation.md` — perbandingan empat konfigurasi.
- `reports/benchmark_kb_multilingual_e5_small_c180_o36.md` — per-query dan
  ringkasan konfigurasi acuan.
- `reports/evaluation_kb_multilingual_e5_small_c180_o36/` — metrik formal,
  statistik cosine, dan visualisasi dari `scripts/benchmark.py`.
- `reports/calibration_kb_multilingual_e5_small_c180_o36.json` — skor dev dan
  threshold yang dipilih.

Pada E5-small 180/36, korpus menghasilkan 302 chunk dan threshold dev 0.850363.
Holdout terdiri dari 11 kueri in-domain dan 5 OOD: 11/11 diterima dan 5/5
ditolak (precision/recall/F1 penolakan OOD masing-masing 1.00; TP=5, FP=0,
FN=0, TN=11). Rata-rata cosine top-1 adalah 0.877 untuk synonym, 0.874 untuk
ambiguous, dan 0.792 untuk OOD. Skor in-domain minimum adalah 0.8545 dan skor
OOD maksimum 0.8163; jarak pemisahannya 0.0382. Margin skor in-domain minimum
terhadap threshold hanya sekitar 0.0041, sehingga threshold perlu diuji pada
set yang lebih besar.

Metrik retrieval gabungan in-domain: P@1=0.909, P@3=0.424, P@5=0.273,
R@1=0.712, R@3=0.864, R@5=0.894, MRR=0.939. Kategori ambiguous lebih lemah
(Hit@1=0.667, MRR=0.778) daripada synonym (Hit@1=1.00, MRR=1.00). Kueri Q01
sebelumnya tidak menyebut marketplace dan hasil teratasnya berasal dari
Shopee; setelah kueri diperjelas dengan "Di Tokopedia", MKT004 berada pada
peringkat pertama. Ini menunjukkan pentingnya konteks platform pada kueri
yang membandingkan kebijakan.

Angka holdout tersebut berdasarkan sampel kecil dan tidak membuktikan
generalisasi ke trafik produksi. `reports/summary_ablation.md` harus
diperbarui lewat `scripts/run_all.py` setelah seluruh konfigurasi selesai;
jangan menyalin angka dari run lama.

## 6. Reproduksi

Pada working tree yang memiliki semua sumber korpus yang sah:

```powershell
uv sync
uv run python scripts/build_index.py --reset
uv run python scripts/run_all.py
uv run python scripts/benchmark.py --preds reports/predictions_kb_multilingual_e5_small_c180_o36.csv --out reports/evaluation_kb_multilingual_e5_small_c180_o36
uv run pytest -q
```

Jika sumber marketplace belum disediakan, `build_index.py` berhenti dengan
daftar dokumen yang hilang. `--allow-partial-corpus` hanya untuk eksperimen
parsial dan tidak memenuhi korpus 10–15 dokumen.

Laporan PDF yang dibuat dari dokumen ini disimpan sebagai
`Grup14-Tugas03.pdf`. Tim tetap perlu meninjau isi akhir dan memeriksa izin
penggunaan setiap sumber sebelum menyerahkan laporan.
