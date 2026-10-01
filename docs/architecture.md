# Arsitektur Sistem 5-Lapis — SmartStore AI

Dokumen desain arsitektur (AI Architect & Model Lead). Mengikuti arsitektur
5-lapis pada panduan proyek akhir. Bagian bertanda **(rencana)** belum
diimplementasikan; status per lapisan ada di tabel bawah.

```mermaid
flowchart TB
    subgraph L1["1. Data & Document Layer"]
        D1["data/cart_catalog.json"]
        D2["Korpus kebijakan/SOP marketplace (rencana M3)"]
    end
    subgraph L2["2. Knowledge & RAG Layer"]
        K1["Chunking + Embeddings + ChromaDB (rencana M3)"]
    end
    subgraph L3["3. Agent & Tool Layer"]
        A1["Solver: UCS/A* (src/search) dan CSP (src/csp)"]
        A2["ReAct agent + Gemini 2.5 Flash (rencana M4)"]
        A3["Tool server FastMCP (rencana M4)"]
    end
    subgraph L4["4. Interface Layer"]
        I1["Dashboard Gradio (rencana M5)"]
    end
    subgraph L5["5. Observability & Guardrails Layer"]
        O1["pytest (tests/)"]
        O2["Tracing, LLM-as-a-Judge, anti prompt-injection (rencana)"]
    end
    L1 --> L2 --> L3 --> L4
    L5 -. mengawasi .-> L3
    L5 -. mengawasi .-> L4
```

## Status per lapisan
| Lapisan | Status saat ini (Milestone 1-2) | Rencana |
|---|---|---|
| 1. Data & Document | Katalog dummy masih tertanam di kode; pemindahan ke JSON dan loader tervalidasi menjadi kontribusi tahap Rospika berikutnya | Korpus dokumen bisnis, OCR bila diperlukan |
| 2. Knowledge & RAG | Belum ada | Word-aware chunking, embeddings, ChromaDB (M3) |
| 3. Agent & Tool | Solver UCS/A* dan CSP (AC-3, MRV, LCV) sebagai fungsi Python | Dibungkus sebagai tool FastMCP; siklus ReAct dengan batas iterasi (M4) |
| 4. Interface | CLI demo | Gradio dengan streaming dan panel sitasi (M5) |
| 5. Observability & Guardrails | Unit test pytest | Log terstruktur, evaluasi LLM-as-a-Judge, delimiter `<<<USER_INPUT>>>` |

## Keputusan desain
- **Solver tetap deterministik dan terpisah dari LLM.** Agen memanggil solver
  sebagai *tool*, sehingga angka biaya selalu berasal dari algoritma yang
  terverifikasi (dibandingkan dengan brute-force di test), bukan dari
  perkiraan model bahasa.
- **Data dipisah dari logika** (`data/` + `knowledge/catalog_loader.py`)
  pada tahap berikutnya, agar pergantian ke data nyata tidak mengubah kode
  solver.
- **Gagal secara eksplisit:** solver mengembalikan `infeasible` beserta alasan,
  bukan solusi yang melanggar batasan.
