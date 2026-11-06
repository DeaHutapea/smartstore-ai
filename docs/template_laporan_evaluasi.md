# Laporan Evaluasi & Metodologi Benchmark SmartStore AI (T03)

**Proyek:** SmartStore AI Enterprise Copilot (T03 - Benchmark & Evaluasi RAG)  
**Tanggal Pembuatan Template:** 6 November 2026  
**Status Data Eksperimen:** Menunggu eksekusi pipeline RAG (T01/T02) — *Tidak ada angka eksperimen yang dikarang.*

---

## 1. Tujuan & Ruang Lingkup Evaluasi
Dokumen ini mendokumentasikan rancangan dataset pengujian (*benchmark*), pemetaan *ground truth* terhadap *corpus* resmi yang telah diaudit, rumus metrik evaluasi informasi (*Information Retrieval*), serta format pelaporan untuk menguji sistem *Retrieval-Augmented Generation* (RAG) SmartStore AI.

Sesuai aturan proyek:
1. Tidak ada hasil eksperimen fiktif di dalam laporan ini; seluruh sel metrik ditandai `[TBD]` hingga pipeline RAG menghasilkan `predictions.csv`.
2. *Ground truth* hanya mengacu pada dokumen *corpus* yang sudah tersedia dan lolos audit kelayakan.
3. Evaluasi dilakukan secara eksternal melalui `scripts/benchmark.py` tanpa mengubah *source code* T01 maupun T02.

---

## 2. Pemetaan Status Corpus terhadap Ground Truth
Berdasarkan hasil audit dokumen sumber Tokopedia (no. 5–12) dan regulasi Permendag, pemetaan kelayakan dokumen untuk dijadikan rujukan *ground truth* adalah sebagai berikut:

### A. Dokumen Layak (Digunakan Penuh pada Ground Truth)
1. `tokopedia_estimasi_pesanan_tiba.md` — Rujukan utama untuk Grup Query **G1**.
2. `tokopedia_faq_seputar_gratis_ongkir.md` — Rujukan utama untuk Grup Query **G2** dan rujukan pendukung **G5**.
3. `tokopedia_pengembalian_dana_refund.md` — Rujukan utama untuk Grup Query **G3**.
4. `tokopedia_faq_pusat_resolusi_pembeli.md` — Rujukan utama untuk Grup Query **G4**.

### B. Dokumen Layak dengan Perbaikan (Digunakan Terbatas pada Bagian Valid)
5. `tokopedia_opsi_durasi_pengiriman_gratis_ongkir.md` — Rujukan untuk Grup Query **G5**. Pertanyaan dibatasi pada jenis opsi durasi layanan pengiriman dan tidak menanyakan nominal angka subsidi pada tabel yang masih perlu dicocokkan manual.
6. `tokopedia_kurir_rekomendasi.md` — Rujukan untuk Grup Query **G6**. Pertanyaan dibatasi pada definisi layanan dan daftar mitra logistik, menghindari aturan pembulatan berat (masih berupa gambar) serta bagian S&K yang tidak konsisten dengan FAQ.

### C. Dokumen Belum Layak (Dikecualikan dari Ground Truth Aktif)
* `tokopedia_cara_menghitung_ongkos_kirim.md` — Dikecualikan karena syarat dan panduan penggabungan ongkir hanya ada di dalam dua file GIF yang belum diekstrak.
* `tokopedia_batas_waktu_respon_pesanan.md` — Dikecualikan karena tabel SLA terbaru (10 September 2024) dan diagram rumus hanya berupa gambar.
* `permendag_19_2026_pmse.txt` — Dikecualikan karena baru berisi metadata halaman JDIH Kemendag tanpa isi pasal peraturan.

---

## 3. Desain Dataset Benchmark (`benchmark_queries.csv`)
Dataset terdiri dari **6 Grup Bisnis (24 Query)** yang dibagi secara proporsional ke dalam 4 kategori:
* **`business` (6 query):** Pertanyaan spesifik dan formal seputar prosedur/kebijakan layanan pelanggan Tokopedia.
* **`synonym` (6 query):** Pertanyaan dengan maksud semantik yang sama persis dengan kategori `business`, tetapi ditulis menggunakan padanan kata (sinonim) dan struktur kalimat berbeda untuk menguji ketahanan *embedding model*.
* **`ambiguous` (6 query):** Pertanyaan pendek, kolokial, atau multi-tafsir yang sering diajukan pengguna awam untuk menguji kemampuan sistem mengambil dokumen kandidat terdekat atau meminta klarifikasi.
* **`out_of_domain` / OOD (6 query):** Pertanyaan di luar konteks e-commerce Tokopedia yang sengaja memuat kata kunci serupa (*lexical trap*, seperti "estimasi penerbangan", "subsidi pupuk gratis", "restitusi pajak", "gugatan pengadilan", "durasi panggang kue", "rekomendasi sepeda") untuk menguji ketepatan filter penolakan OOD (*OOD rejection*).

---

## 4. Kontrak Antarmuka CSV dengan Pipeline RAG
Agar skrip `scripts/benchmark.py` dapat langsung memproses keluaran sistem tanpa menyentuh kode T01/T02, tim pipeline RAG mengekspor hasil pencarian ke berkas `predictions.csv` dengan kolom berikut:

| Nama Kolom | Tipe Data | Contoh Isi | Keterangan |
| :--- | :--- | :--- | :--- |
| `query_id` | String | `Q01` | ID query sesuai `benchmark_queries.csv` |
| `retrieved_doc_ids` | String (`;` separated) | `tokopedia_estimasi_pesanan_tiba.md;tokopedia_kurir_rekomendasi.md` | Daftar nama dokumen terambil dari peringkat 1 s.d. $K$ (isi `NONE` jika ditolak) |
| `cosine_scores` | String (`;` separated) | `0.8542;0.7120` | Daftar skor *cosine similarity* yang berkorespondensi dengan dokumen terambil |
| `is_rejected` | Boolean | `False` | Bernilai `True` jika query ditolak sebagai Out-of-Domain, `False` jika diterima |

---

## 5. Metodologi Pengukuran & Rumus Evaluasi

### 5.1 Precision@K ($P@K$)
Mengukur proporsi dokumen relevan di antara $K$ dokumen teratas yang diambil untuk setiap query *in-domain* $q$:
$$\text{Precision}@K(q) = \frac{|\text{Ret}_K(q) \cap \text{Rel}(q)|}{K}$$

### 5.2 Recall@K ($R@K$)
Mengukur proporsi dokumen relevan yang berhasil terambil pada $K$ urutan teratas dibandingkan total dokumen relevan di *ground truth* untuk query $q$:
$$\text{Recall}@K(q) = \frac{|\text{Ret}_K(q) \cap \text{Rel}(q)|}{|\text{Rel}(q)|}$$

### 5.3 Mean Reciprocal Rank ($\text{MRR}$)
Mengukur rata-rata kebalikan peringkat (*reciprocal rank*) dari dokumen relevan pertama yang berhasil ditemukan untuk seluruh himpunan query *in-domain* $Q_{\text{in}}$:
$$\text{MRR} = \frac{1}{|Q_{\text{in}}|} \sum_{q \in Q_{\text{in}}} \frac{1}{\text{rank}_q}$$

### 5.4 OOD Rejection Precision
Mengukur tingkat ketepatan sistem ketika memutuskan untuk menolak sebuah query:
$$\text{OOD Rejection Precision} = \frac{\text{TP}_{\text{OOD}}}{\text{TP}_{\text{OOD}} + \text{FP}_{\text{OOD}}}$$
* $\text{TP}_{\text{OOD}}$: Query berlabel Out-of-Domain (`is_ood = True`) yang berhasil ditolak (`is_rejected = True`).
* $\text{FP}_{\text{OOD}}$: Query berlabel In-Domain (`is_ood = False`) yang salah ditolak oleh sistem (`is_rejected = True`).
* Sebagai metrik pendamping, dihitung pula **OOD Rejection Recall** ($\frac{\text{TP}_{\text{OOD}}}{\text{TP}_{\text{OOD}} + \text{FN}_{\text{OOD}}}$) dan **OOD Rejection F1-Score**.

### 5.5 Metode Analisis Cosine Similarity
1. Mengambil skor tertinggi (**Top-1 Cosine Similarity**) dari setiap query terhadap dokumen di dalam *vector database*.
2. Mengelompokkan distribusi skor berdasarkan 4 kategori (`business`, `synonym`, `ambiguous`, `out_of_domain`) dan menghitung nilai statistik: *Count, Mean, Std Dev, Min, Median,* dan *Max*.
3. Memvisualisasikan distribusi menggunakan **Boxplot per Kategori** dan **Histogram Separabilitas In-Domain vs OOD** (`eval_results/cosine_similarity_analysis.png`) guna menentukan ambang batas (*threshold* $\tau$) yang meminimalkan $\text{FP}_{\text{OOD}}$ sekaligus memaksimalkan $\text{TP}_{\text{OOD}}$.

---

## 6. Tabel Hasil Pengujian (Diisi Setelah Eksekusi Pipeline)

### Tabel 6.1 Ringkasan Metrik Retrieval In-Domain
*(Sumber data: `eval_results/retrieval_metrics_summary.csv`)*

| Kategori Query | Jumlah Query | P@1 | P@3 | P@5 | R@1 | R@3 | R@5 | MRR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Business** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **Synonym** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **Ambiguous** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **ALL_IN_DOMAIN** | 18 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

### Tabel 6.2 Hasil Evaluasi Penolakan Out-of-Domain (OOD Rejection)
*(Sumber data: `eval_results/ood_metrics_summary.json`)*

| Metrik Evaluasi OOD | Nilai Hasil Uji | Target Ideal | Keterangan |
| :--- | :---: | :---: | :--- |
| **Similarity Threshold ($\tau$)** | [TBD] | Disesuaikan | Ambang batas skor minimum penerimaan query |
| **True Positive ($\text{TP}_{\text{OOD}}$)** | [TBD] | 6 | Query OOD berhasil ditolak |
| **False Positive ($\text{FP}_{\text{OOD}}$)** | [TBD] | 0 | Query In-Domain salah ditolak (*False Rejection*) |
| **False Negative ($\text{FN}_{\text{OOD}}$)** | [TBD] | 0 | Query OOD gagal ditolak (*kebobolan*) |
| **True Negative ($\text{TN}_{\text{OOD}}$)** | [TBD] | 18 | Query In-Domain berhasil diproses |
| **OOD Rejection Precision** | [TBD] | 1.0000 | $\text{TP}_{\text{OOD}} / (\text{TP}_{\text{OOD}} + \text{FP}_{\text{OOD}})$ |
| **OOD Rejection Recall** | [TBD] | 1.0000 | $\text{TP}_{\text{OOD}} / (\text{TP}_{\text{OOD}} + \text{FN}_{\text{OOD}})$ |
| **OOD Rejection F1-Score** | [TBD] | 1.0000 | Rata-rata harmonik Precision & Recall OOD |

### Tabel 6.3 Statistik Distribusi Top-1 Cosine Similarity
*(Sumber data: `eval_results/cosine_similarity_summary.csv`)*

| Kategori Query | Count | Mean | Std Dev | Min | Median | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **business** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **synonym** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **ambiguous** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **out_of_domain** | 6 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

---

## 7. Visualisasi & Analisis Temuan
*(Lampirkan gambar `eval_results/cosine_similarity_analysis.png` di bagian ini setelah menjalankan `scripts/benchmark.py`)*

* **Analisis Perbandingan Kategori (`business` vs `synonym` vs `ambiguous`):** `[TBD - Jelaskan apakah penurunan skor dari business ke synonym dan ambiguous signifikan]`
* **Analisis Pemisahan Skor In-Domain vs OOD:** `[TBD - Jelaskan apakah terdapat tumpang tindih (overlap) antara skor minimum query ambiguous dengan skor maksimum query out_of_domain]`
* **Rekomendasi Threshold ($\tau$):** `[TBD - Tentukan angka threshold optimal berdasarkan distribusi pada grafik]`
