"""
news.py - RSS Feed ile Güncel Teknoloji Haberleri Uygulaması
Gereksinim: pip install requests
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

RSS_URL = "https://www.ntv.com.tr/teknoloji.rss"


def rss_verisi_cek() -> list | None:
    """RSS kaynağından son dakika teknoloji haberlerini çeker."""
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
        
        # XML içeriğini ayrıştır
        root = ET.fromstring(response.content)
        haberler = []
        
        # channel içindeki item'ları bul (En güncel 5 haberi alıyoruz)
        for item in root.findall('./channel/item')[:5]:
            title_element = item.find('title')
            
            if title_element is not None and title_element.text:
                haberler.append({"baslik": title_element.text.strip()})
            
        return haberler
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Haberler alınırken bağlantı hatası: {e}")
        return None
    except ET.ParseError:
        print("❌ XML ayrıştırma hatası.")
        return None


def haberleri_formatla(haberler: list) -> str:
    """Haber listesini terminalde şık görünecek şekilde formatlar."""
    if not haberler:
        return "❌ Güncel haber bulunamadı."
        
    sonuc = "\n" + "═" * 60 + "\n"
    sonuc += f" 📰 Güncel Teknoloji Haberleri | 🕐 {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
    sonuc += "═" * 60 + "\n"
    
    for i, haber in enumerate(haberler, 1):
        # Başlık çok uzunsa terminalde satır kaymasını önlemek için kes
        baslik = haber['baslik'][:52] + "..." if len(haber['baslik']) > 52 else haber['baslik']
        sonuc += f" {i}. 🔹 {baslik}\n"
        
    sonuc += "═" * 60 + "\n"
    return sonuc

def get_info() -> str:
    """
    main.py tarafından çağrılacak ana fonksiyon.
    Ödevin beklediği 'news.get_info()' yapısını karşılar.
    """
    haberler = rss_verisi_cek()
    if haberler:
        return haberleri_formatla(haberler)
    return "❌ Haber servisi şu an kullanılamıyor."


if __name__ == "__main__":
    print("🌍 En güncel teknoloji haberleri getiriliyor...\n")
    print(get_info())