# Performance Evaluation Engine

A rule-based engine for a multi-stage employee performance review cycle. It covers the full path from the raw scores to a management-ready report:

- **Score deviation risk:** flags employees whose self-assessment differs significantly from their manager's evaluation.
- **Calibration limits:** keeps second-level calibration within a fixed range of the base score.
- **Performance categorization:** maps final scores to four performance bands.
- **Low-performance pool tracking:** counts repeated low-performance results and flags cases that require administrative action.
- **Automated Excel reporting:** conditional formatting and a distribution chart, generated in one command.

The calibration and risk module is written in **C++17**; the categorization and reporting pipeline is written in **Python (pandas + xlsxwriter)**.

> All data in this repository is synthetic. No real employee data is used.

---

## How the Review Cycle Works

```
 Self-assessment ──► Manager evaluation ──► 2nd-level calibration ──► Final score
   (employee)          (base score)          (limited to ±0.5)             │
        │                    │                                             ▼
        └──── deviation ─────┘                                 Performance category
              risk group                                                   │
                                                                           ▼
                                                        Low-performance pool rules
                                                                           │
                                                                           ▼
                                                                  Excel report
```

1. The employee rates themselves out of 5.
2. The manager gives the base score. The difference between the two scores determines a **deviation risk group**.
3. A second-level reviewer may calibrate the score, but only within **±0.5** of the base score.
4. The final score is placed into a **performance category**.
5. Employees in the lowest category are added to the **low-performance pool**; repeated entries trigger an **administrative action flag**.

---

## Business Rules

### Deviation risk (`cpp/score_calibration.cpp`)

Difference = manager score − self-assessment score

| Difference | Risk group |
|---|---|
| ≥ −0.30 | No risk |
| −0.30 to −0.60 (inclusive) | Medium risk |
| < −0.60 | High risk |

### Calibration limit (`cpp/score_calibration.cpp`)

The calibrated score is clamped to `[base − 0.5, base + 0.5]`:

```cpp
double nihaiPuan = max(altSinir, min(talep, ustSinir));
```

For example, with a base score of 3.30 a calibration request of 4.50 is reduced to 3.80.

### Performance categories (`python/performance_report.py`)

| Final score | Category |
|---|---|
| ≤ 2.40 | Düşük Performans (Low performance) |
| 2.41 – 2.99 | Gelişime Açık (Open to development) |
| 3.00 – 3.75 | Beklenen Seviyede (Meets expectations) |
| > 3.75 | Beklenen Seviyenin Üstünde (Exceeds expectations) |

### Low-performance pool (`python/performance_report.py`)

- Every low-performance result increases the employee's pool entry count by one.
- When the count reaches **2**, `İdari_İşlem_Gerekli` (administrative action required) is set to `True`.

All thresholds are defined as constants at the top of each file, so a policy change only requires editing one place.

---

## Project Structure

```
performance-evaluation-engine/
├── cpp/
│   └── score_calibration.cpp     # Deviation risk + calibration limit (C++17)
├── python/
│   ├── generate_sample_data.py   # Synthetic input data generator
│   └── performance_report.py     # Categorization, pool rules, Excel report
├── data/
│   └── sample_raw_data.xlsx      # Sample input (synthetic)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Getting Started

### Requirements

- Python 3.9+
- A C++17 compiler (g++, clang++ or MSVC)

### Installation

```bash
git clone https://github.com/TuanaPektas/performance-evaluation-engine.git
cd performance-evaluation-engine
pip install -r requirements.txt
```

### Run the Python pipeline

```bash
# 1. (Optional) generate a new synthetic dataset
python python/generate_sample_data.py -n 120

# 2. Categorize scores, apply pool rules and build the Excel report
python python/performance_report.py data/sample_raw_data.xlsx -o output/performans_raporu.xlsx
```

Console output:

```
Performans_Kategorisi
Beklenen Seviyede             46
Beklenen Seviyenin Üstünde    36
Gelişime Açık                 24
Düşük Performans              14

İdari işlem gereken çalışan sayısı: 9
Rapor oluşturuldu: output/performans_raporu.xlsx
```

The generated workbook contains:

- **Performans_Analizi:** all employees with their category and action flag. Low-performance rows and `True` action flags are highlighted in red, and the header row is frozen.
- **Grafik_Verisi:** the category summary used by the chart.
- **A pie chart** showing the percentage distribution of the categories.

### Run the C++ module

```bash
g++ -std=c++17 -O2 -o score_calibration cpp/score_calibration.cpp
./score_calibration
```

Sample output:

```
=== Puan Sapma ve Kalibrasyon Sistemi ===

--- Calisan: Zeynep Ece ---
Yetkinlik (Oz)               : 3.90
Son Degerlendirme (Yonetici) : 3.50
Oz / Son Degerlendirme Farki : -0.40
Risk Grubu                   : Orta Seviye Risk
2. Kademe Kalibrasyon Talebi : 4.00
Sistemin Izin Verdigi Nihai  : 4.00
---------------------------------

--- Calisan: Deniz Kaya ---
Yetkinlik (Oz)               : 3.20
Son Degerlendirme (Yonetici) : 3.30
Oz / Son Degerlendirme Farki : 0.10
Risk Grubu                   : Risk Yok
2. Kademe Kalibrasyon Talebi : 4.50
Sistemin Izin Verdigi Nihai  : 3.80
---------------------------------
```

### Input format

`performance_report.py` expects an Excel file with at least these columns:

| Column | Description |
|---|---|
| `Kalibre_Edilmis_Puan` | Final (calibrated) score, 1.00 – 5.00 |
| `Havuz_Giris_Sayisi` | Number of previous low-performance pool entries |

Any other columns (ID, name, department, …) are carried over to the report unchanged.

---

## Tech Stack

| Area | Tools |
|---|---|
| Rule engine | C++17 (`std::min`, `std::max`, `<iomanip>`) |
| Data processing | Python, pandas |
| Reporting | xlsxwriter (conditional formatting, charts) |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
