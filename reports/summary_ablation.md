# Ringkasan ablation

| Konfigurasi | Chunk | Hit@1 sin. | Hit@3 sin. | MRR sin. | Hit@3 ambigu | Skor top-1 in-domain | Skor top-1 OOD | Ambang OOD | In-domain diterima | OOD ditolak |
|---|---|---|---|---|---|---|---|---|---|---|
| multilingual-e5-small · 180/36 | 302 | 0.88 | 0.88 | 0.90 | 1.00 | 0.873 | 0.792 | 0.835 | 11/11 | 5/5 |
| multilingual-e5-small · 120/24 | 449 | 0.75 | 0.88 | 0.83 | 0.67 | 0.877 | 0.789 | 0.838 | 11/11 | 5/5 |
| paraphrase-multilingual-MiniLM-L12-v2 · 80/16 | 688 | 0.75 | 0.88 | 0.84 | 0.67 | 0.691 | 0.230 | 0.439 | 11/11 | 5/5 |
| paraphrase-multilingual-MiniLM-L12-v2 · 120/24 | 449 | 0.75 | 0.88 | 0.84 | 0.67 | 0.687 | 0.209 | 0.423 | 11/11 | 5/5 |
