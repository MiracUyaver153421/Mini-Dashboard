"""
weather.py - Open-Meteo API ile Hava Durumu Uygulaması
Gereksinim: pip install requests
"""

import requests
from datetime import datetime, timedelta

# ── Sabitler ────────────────────────────────────────────────────────────────
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL   = "https://api.open-meteo.com/v1/forecast"

WMO_KODLARI = {
    0: "Açık ☀️",
    1: "Çoğunlukla Açık 🌤️",  2: "Parçalı Bulutlu ⛅",  3: "Kapalı ☁️",
    45: "Sisli 🌫️",           48: "Kırağılı Sis 🌫️",
    51: "Hafif Çisenti 🌦️",   53: "Orta Çisenti 🌦️",   55: "Yoğun Çisenti 🌧️",
    61: "Hafif Yağmur 🌧️",    63: "Orta Yağmur 🌧️",    65: "Şiddetli Yağmur 🌧️",
    71: "Hafif Kar ❄️",        73: "Orta Kar ❄️",         75: "Yoğun Kar ❄️",
    77: "Kar Taneleri 🌨️",
    80: "Hafif Sağanak 🌦️",   81: "Orta Sağanak 🌧️",   82: "Şiddetli Sağanak ⛈️",
    85: "Kar Sağanağı 🌨️",    86: "Yoğun Kar Sağanağı 🌨️",
    95: "Gök Gürültülü Fırtına ⛈️",
    96: "Dolu ile Fırtına ⛈️", 99: "Şiddetli Dolu ile Fırtına ⛈️",
}

RUZGAR_YONLERI = [
    "Kuzey ↑", "KKD ↗", "Kuzeydoğu ↗", "DKD ↗",
    "Doğu →",  "DGD ↘", "Güneydoğu ↘", "GGD ↘",
    "Güney ↓", "GGB ↙", "Güneybatı ↙", "BBG ↙",
    "Batı ←",  "KKB ↖", "Kuzeybatı ↖", "KKB ↖",
]

# ── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def derece_to_yon(derece: float) -> str:
    """Rüzgar derecesini yön adına çevirir."""
    index = round(derece / 22.5) % 16
    return RUZGAR_YONLERI[index]

def wmo_to_aciklama(kod: int) -> str:
    """WMO hava kodu açıklaması döndürür."""
    return WMO_KODLARI.get(kod, f"Bilinmeyen ({kod})")

def basinc_durumu(hpa: float) -> str:
    if hpa < 1000: return "Düşük (Yağmur olasılığı)"
    if hpa < 1013: return "Normal Altı"
    if hpa < 1020: return "Normal"
    return "Yüksek (Açık hava)"

# ── API Fonksiyonları ────────────────────────────────────────────────────────

def sehir_koordinatlari_getir(sehir: str) -> dict | None:
    """
    Şehir adından enlem/boylam bilgisi getirir.
    Başarısız olursa None döner.
    """
    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": sehir, "count": 1, "language": "tr", "format": "json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            print(f"❌ '{sehir}' şehri bulunamadı.")
            return None

        sonuc = data["results"][0]
        return {
            "isim":    sonuc.get("name", sehir),
            "ulke":    sonuc.get("country", ""),
            "enlem":   sonuc["latitude"],
            "boylam":  sonuc["longitude"],
        }

    except requests.exceptions.ConnectionError:
        print("❌ İnternet bağlantısı yok.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Sunucu zaman aşımına uğradı.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP hatası: {e}")
        return None

def hava_verisi_getir(enlem: float, boylam: float) -> dict | None:
    """
    Open-Meteo API'den anlık + 5 günlük tahmin verisi getirir.
    """
    params = {
        "latitude":  enlem,
        "longitude": boylam,
        "timezone":  "auto",
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "surface_pressure",
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
        ],
        "forecast_days": 5,
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        print("❌ İnternet bağlantısı yok.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Hava verisi alınamadı: Zaman aşımı.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP hatası: {e}")
        return None

# ── Görüntüleme Fonksiyonları ────────────────────────────────────────────────

def anlik_hava_goster(konum: dict, veri: dict) -> None:
    """Anlık hava durumu bilgisini terminale yazdırır."""
    c = veri["current"]

    sicaklik     = c["temperature_2m"]
    hissedilen   = c["apparent_temperature"]
    nem          = c["relative_humidity_2m"]
    ruzgar_hiz   = c["wind_speed_10m"]
    ruzgar_yon   = derece_to_yon(c["wind_direction_10m"])
    basinc       = c["surface_pressure"]
    durum_kodu   = c["weather_code"]
    durum        = wmo_to_aciklama(durum_kodu)

    print("\n" + "═" * 50)
    print(f"  📍 {konum['isim']}, {konum['ulke']}")
    print(f"  🕐 {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("═" * 50)
    print(f"  Durum       : {durum}")
    print(f"  Sıcaklık    : {sicaklik}°C  (Hissedilen: {hissedilen}°C)")
    print(f"  Nem         : %{nem}")
    print(f"  Rüzgar      : {ruzgar_hiz} km/s  {ruzgar_yon}")
    print(f"  Basınç      : {basinc:.1f} hPa  → {basinc_durumu(basinc)}")
    print("═" * 50)

def tahmin_goster(veri: dict) -> None:
    """5 günlük tahmin tablosunu terminale yazdırır."""
    daily = veri["daily"]

    print("\n  📅 5 Günlük Tahmin")
    print("─" * 62)
    print(f"  {'Tarih':<14} {'Durum':<28} {'Min':>5} {'Maks':>5} {'Yağış':>7}")
    print("─" * 62)

    for i in range(len(daily["time"])):
        tarih_str = daily["time"][i]
        tarih     = datetime.strptime(tarih_str, "%Y-%m-%d")
        gun_adi   = tarih.strftime("%a, %d %b")

        durum     = wmo_to_aciklama(daily["weather_code"][i])
        # Emoji + metin birlikte max 28 karakter
        durum_kisa = durum[:27].ljust(27)

        t_min  = daily["temperature_2m_min"][i]
        t_max  = daily["temperature_2m_max"][i]
        yagis  = daily["precipitation_sum"][i]

        yagis_str = f"{yagis:.1f}mm" if yagis > 0 else "  -"
        print(f"  {gun_adi:<14} {durum_kisa} {t_min:>4.0f}° {t_max:>4.0f}° {yagis_str:>7}")

    print("─" * 62)

# ── Ana Fonksiyon ────────────────────────────────────────────────────────────

def hava_durumu_goster(sehir: str) -> None:
    """
    Verilen şehir için anlık hava + 5 günlük tahmini gösterir.

    Kullanım:
        hava_durumu_goster("Istanbul")
        hava_durumu_goster("Ankara")
        hava_durumu_goster("New York")
    """
 

    konum = sehir_koordinatlari_getir(sehir)
    if konum is None:
        return

    veri = hava_verisi_getir(konum["enlem"], konum["boylam"])
    if veri is None:
        return

    anlik_hava_goster(konum, veri)
    tahmin_goster(veri)
    print()

# ── Giriş Noktası ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sehir = input("🌍 Şehir adı girin: ").strip()
    if sehir:
        hava_durumu_goster(sehir)
    else:
        print("❌ Şehir adı boş olamaz.")

