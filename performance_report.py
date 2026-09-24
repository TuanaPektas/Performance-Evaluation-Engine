"""
Performans Kategorizasyonu ve Düşük Performans Havuzu Raporlama Motoru

Girdi : Kalibrasyon sonrası nihai puanları içeren ham Excel dosyası
Çıktı : Koşullu biçimlendirmeli ve pasta grafikli Excel raporu

Kullanım:
    python python/performance_report.py data/sample_raw_data.xlsx
    python python/performance_report.py girdi.xlsx -o output/rapor.xlsx
"""
import argparse
import os

import pandas as pd
from xlsxwriter.utility import xl_col_to_name

# =====================================================================
# AYARLAR: Kurallar değişirse yalnızca burası güncellenir
# =====================================================================
PUAN_SUTUNU = "Kalibre_Edilmis_Puan"
HAVUZ_SUTUNU = "Havuz_Giris_Sayisi"
KATEGORI_SUTUNU = "Performans_Kategorisi"
IDARI_ISLEM_SUTUNU = "İdari_İşlem_Gerekli"

ESIK_DUSUK = 2.40          # <= Düşük Performans
ESIK_GELISIME_ACIK = 2.99  # <= Gelişime Açık
ESIK_BEKLENEN = 3.75       # <= Beklenen Seviyede, üstü: Beklenen Seviyenin Üstünde
IDARI_ISLEM_ESIGI = 2      # Havuz giriş sayısı bu değere ulaşırsa idari işlem gerekir

DUSUK = "Düşük Performans"


# =====================================================================
# 1. İŞ KURALI: Performans Kategorizasyonu
# =====================================================================
def classify_performance(score: float) -> str:
    if score <= ESIK_DUSUK:
        return DUSUK
    elif score <= ESIK_GELISIME_ACIK:
        return "Gelişime Açık"
    elif score <= ESIK_BEKLENEN:
        return "Beklenen Seviyede"
    else:
        return "Beklenen Seviyenin Üstünde"


# =====================================================================
# 2. DÜŞÜK PERFORMANS HAVUZU KURAL MOTORU
# =====================================================================
def uygula_kurallar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Yüzlerce çalışanı saniyeler içinde kategorize et
    df[KATEGORI_SUTUNU] = df[PUAN_SUTUNU].apply(classify_performance)

    # Kural 1: Bu dönem Düşük Performans alanların havuz giriş sayısını +1 artır
    df.loc[df[KATEGORI_SUTUNU] == DUSUK, HAVUZ_SUTUNU] += 1

    # Kural 2: Havuz giriş sayısı eşiğe ulaştıysa 'İdari İşlem Gerekli' = True (yüksek risk)
    df[IDARI_ISLEM_SUTUNU] = df[HAVUZ_SUTUNU] >= IDARI_ISLEM_ESIGI
    return df


# =====================================================================
# 3. EXCEL OTOMASYONU VE GÖRSELLEŞTİRME (xlsxwriter)
# =====================================================================
def excel_raporu_yaz(df: pd.DataFrame, cikti: str) -> None:
    with pd.ExcelWriter(cikti, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Performans_Analizi", index=False)

        # Grafik için özet tablo (kategori bazlı çalışan sayısı)
        ozet_df = df[KATEGORI_SUTUNU].value_counts().reset_index()
        ozet_df.columns = ["Kategori", "Kişi_Sayısı"]
        ozet_df.to_excel(writer, sheet_name="Grafik_Verisi", index=False)

        workbook = writer.book
        ws = writer.sheets["Performans_Analizi"]
        son_satir = len(df) + 1  # başlık satırı dahil

        # Sütun harflerini sabit yazmak yerine sütun adından buluyoruz;
        # böylece girdi dosyasına sütun eklense bile biçimlendirme kaymaz.
        kat_harf = xl_col_to_name(df.columns.get_loc(KATEGORI_SUTUNU))
        idari_harf = xl_col_to_name(df.columns.get_loc(IDARI_ISLEM_SUTUNU))

        # KOŞULLU BİÇİMLENDİRME (kırmızı alarm)
        red_format = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
        ws.conditional_format(f"{idari_harf}2:{idari_harf}{son_satir}",
                              {"type": "cell", "criteria": "==", "value": True, "format": red_format})
        ws.conditional_format(f"{kat_harf}2:{kat_harf}{son_satir}",
                              {"type": "text", "criteria": "containing", "value": DUSUK, "format": red_format})

        # Okunabilirlik: başlık satırını sabitle, sütun genişliklerini içeriğe göre ayarla
        ws.freeze_panes(1, 0)
        for i, sutun in enumerate(df.columns):
            genislik = max(len(str(sutun)), int(df[sutun].astype(str).str.len().max())) + 2
            ws.set_column(i, i, min(genislik, 32))

        # PASTA GRAFİĞİ
        chart = workbook.add_chart({"type": "pie"})
        n = len(ozet_df)
        chart.add_series({
            "name": "Performans Dağılımı",
            "categories": ["Grafik_Verisi", 1, 0, n, 0],
            "values": ["Grafik_Verisi", 1, 1, n, 1],
            "data_labels": {"percentage": True, "position": "inside_end"},  # yüzdeler dilimlerin içinde
        })
        chart.set_title({"name": "Performans Skalası"})
        chart.set_size({"width": 480, "height": 320})
        ws.insert_chart(1, len(df.columns) + 1, chart)  # tablonun sağına yerleştir


def main() -> None:
    ap = argparse.ArgumentParser(description="Performans kategorizasyonu ve Excel raporu üretir.")
    ap.add_argument("girdi", help="Ham veri Excel dosyası")
    ap.add_argument("-o", "--cikti", default="output/performans_raporu.xlsx", help="Rapor dosyası")
    a = ap.parse_args()

    df = pd.read_excel(a.girdi)
    eksik = {PUAN_SUTUNU, HAVUZ_SUTUNU} - set(df.columns)
    if eksik:
        raise SystemExit(f"Girdi dosyasında eksik sütun(lar): {', '.join(sorted(eksik))}")

    sonuc = uygula_kurallar(df)
    os.makedirs(os.path.dirname(a.cikti) or ".", exist_ok=True)
    excel_raporu_yaz(sonuc, a.cikti)

    print(sonuc[KATEGORI_SUTUNU].value_counts().to_string())
    print(f"\nİdari işlem gereken çalışan sayısı: {int(sonuc[IDARI_ISLEM_SUTUNU].sum())}")
    print(f"Rapor oluşturuldu: {a.cikti}")


if __name__ == "__main__":
    main()
