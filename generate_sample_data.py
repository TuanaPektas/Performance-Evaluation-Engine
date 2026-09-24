"""
Örnek (sentetik) ham veri üretici.

Gerçek çalışan verisi kullanılmaz. Bu betik, performance_report.py'nin
girdi olarak beklediği formatta rastgele ama tutarlı bir Excel dosyası üretir.

Kullanım:
    python python/generate_sample_data.py              # data/sample_raw_data.xlsx
    python python/generate_sample_data.py -n 250 -o data/ornek.xlsx
"""
import argparse
import random

import pandas as pd

AD = ["Ali", "Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Selin",
      "Emre", "Deniz", "Kerem", "Ece", "Mert", "İrem", "Onur", "Buse"]
SOYAD = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Arslan", "Doğan",
         "Kurt", "Aydın", "Özdemir", "Koç", "Aksoy"]
DEPARTMAN = ["Bakım Planlama", "Kalite", "İnsan Kaynakları", "Finans",
             "Bilgi Teknolojileri", "Satın Alma", "Operasyon"]


def uret(n: int, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    satirlar = []
    for i in range(n):
        # Puanlar 1.00 - 5.00 arasında, ortalamaya yakın değerler daha sık
        puan = round(min(5.0, max(1.0, random.gauss(3.2, 0.7))), 2)
        # Geçmiş dönemlerde düşük performans havuzuna giriş sayısı (çoğunlukla 0)
        gecmis = random.choices([0, 1, 2], weights=[80, 15, 5])[0]
        satirlar.append({
            "Sicil_No": 10000 + i,
            "Ad_Soyad": f"{random.choice(AD)} {random.choice(SOYAD)}",
            "Departman": random.choice(DEPARTMAN),
            "Kalibre_Edilmis_Puan": puan,
            "Havuz_Giris_Sayisi": gecmis,
        })
    return pd.DataFrame(satirlar)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Sentetik performans verisi üretir.")
    ap.add_argument("-n", type=int, default=120, help="Çalışan sayısı (varsayılan 120)")
    ap.add_argument("-o", default="data/sample_raw_data.xlsx", help="Çıktı dosyası")
    ap.add_argument("--seed", type=int, default=42, help="Tekrarlanabilirlik için seed")
    a = ap.parse_args()
    df = uret(a.n, a.seed)
    df.to_excel(a.o, index=False)
    print(f"{len(df)} satırlık örnek veri oluşturuldu: {a.o}")
