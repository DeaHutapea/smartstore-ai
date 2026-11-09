# Ringkasan ablation

| Konfigurasi | Chunk | Hit@1 sin. | Hit@3 sin. | MRR sin. | Hit@3 ambigu | Skor top-1 in-domain | Skor top-1 OOD | Ambang OOD | In-domain diterima | OOD ditolak |
|---|---|---|---|---|---|---|---|---|---|---|
| multilingual-e5-small · 180/36 | 302 | 1.00 | 1.00 | 1.00 | 1.00 | 0.876 | 0.792 | 0.850 | 11/11 | 5/5 |
| multilingual-e5-small · 120/24 | 449 | 0.88 | 1.00 | 0.94 | 0.67 | 0.881 | 0.789 | 0.857 | 11/11 | 5/5 |
| paraphrase-multilingual-MiniLM-L12-v2 · 80/16 | 688 | 0.75 | 0.88 | 0.81 | 0.67 | 0.697 | 0.230 | 0.622 | 8/11 | 5/5 |
| paraphrase-multilingual-MiniLM-L12-v2 · 120/24 | 449 | 0.75 | 0.88 | 0.84 | 0.67 | 0.686 | 0.209 | 0.617 | 10/11 | 5/5 |
