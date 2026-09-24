// Puan Sapma Riski ve Kalibrasyon Motoru
//
// 1) Öz değerlendirme ile yönetici değerlendirmesi arasındaki farka göre
//    risk grubunu belirler.
// 2) İkinci kademe kalibrasyonu temel puandan en fazla +/- 0.5 ile sınırlar.
//
// Derleme:  g++ -std=c++17 -O2 -o score_calibration cpp/score_calibration.cpp

#include <algorithm> // std::min, std::max
#include <iomanip>   // Ondalıklı sayıları düzenli göstermek için
#include <iostream>
#include <string>

using namespace std;

// Kurallar değişirse yalnızca bu sabitler güncellenir
const double ORTA_RISK_ESIGI = -0.30;
const double YUKSEK_RISK_ESIGI = -0.60;
const double KALIBRASYON_LIMITI = 0.5;

// Fark (yönetici - öz) değerine göre risk grubu
string riskGrubuBelirle(double fark) {
    if (fark >= ORTA_RISK_ESIGI) {
        return "Risk Yok";
    } else if (fark >= YUKSEK_RISK_ESIGI) {
        return "Orta Seviye Risk";
    }
    return "Yuksek Seviye Risk";
}

// Kalibrasyon talebini [temel - 0.5, temel + 0.5] aralığına sıkıştırır.
// Önce min ile talep ve üst sınırdan küçük olan seçilir, ardından max ile
// alt sınırla karşılaştırılıp büyük olan alınır.
// (Örnek: talep 6 ise önce üst sınır seçilir; alt sınırdan büyük olduğu için o kalır.)
double kalibrasyonuSinirla(double temelPuan, double talep) {
    double altSinir = temelPuan - KALIBRASYON_LIMITI;
    double ustSinir = temelPuan + KALIBRASYON_LIMITI;
    return max(altSinir, min(talep, ustSinir));
}

// Risk hesaplama ve kalibrasyon işlemlerini yapan çekirdek fonksiyon
void degerlendir(const string& calisan, double yetkinlikOz, double sonDegerlendirme,
                 double kalibreEdilmekIstenen) {
    double fark = sonDegerlendirme - yetkinlikOz;
    string riskGrubu = riskGrubuBelirle(fark);
    double nihaiPuan = kalibrasyonuSinirla(sonDegerlendirme, kalibreEdilmekIstenen);

    cout << "--- Calisan: " << calisan << " ---" << endl;
    cout << fixed << setprecision(2); // virgülden sonra 2 hane
    cout << "Yetkinlik (Oz)               : " << yetkinlikOz << endl;
    cout << "Son Degerlendirme (Yonetici) : " << sonDegerlendirme << endl;
    cout << "Oz / Son Degerlendirme Farki : " << fark << endl;
    cout << "Risk Grubu                   : " << riskGrubu << endl;
    cout << "2. Kademe Kalibrasyon Talebi : " << kalibreEdilmekIstenen << endl;
    cout << "Sistemin Izin Verdigi Nihai  : " << nihaiPuan << endl;
    cout << "---------------------------------" << endl << endl;
}

int main() {
    cout << "=== Puan Sapma ve Kalibrasyon Sistemi ===" << endl << endl;

    // Senaryo 1: Fark -0.20 -> Risk Yok (talep sınır içinde, değişmez)
    degerlendir("Ali Veli", 3.50, 3.30, 3.50);

    // Senaryo 2: Fark -0.40 -> Orta Seviye Risk (talep sınır içinde)
    degerlendir("Zeynep Ece", 3.90, 3.50, 4.00);

    // Senaryo 3: Fark -0.70 -> Yuksek Seviye Risk (talep sınır içinde)
    degerlendir("Fatma Zehra", 4.00, 3.30, 3.00);

    // Senaryo 4: Kalibrasyon talebi üst sınırı aşıyor -> 3.80'e çekilir
    degerlendir("Deniz Kaya", 3.20, 3.30, 4.50);

    return 0; // Programı başarıyla bitir
}
