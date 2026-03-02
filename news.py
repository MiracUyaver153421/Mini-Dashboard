"""
news.py - GitHub API ile Popüler Python Projeleri
Gereksinim: pip install requests
"""

import requests
from datetime import datetime

# ── Sabitler ────────────────────────────────────────────────────────────────
# GitHub'da en çok yıldız alan Python projelerini getiren resmi API
GITHUB_API_URL = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"

# ── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def github_verisi_cek() -> list | None:
    """GitHub'dan en çok yıldız alan Python projelerini çeker."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-Git-Odevi"
    }
    try:
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        projeler = []
        for repo in data.get("items", [])[:5]: # İlk 5 projeyi al
            projeler.append({
                "isim": repo["name"],
                "yildiz": repo["stargazers_count"],
                "aciklama": repo["description"] or "Açıklama yok."
            })
        return projeler
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None
    except ValueError:
        print("❌ JSON ayrıştırma hatası.")
        return None

# ── Görüntüleme Fonksiyonları ────────────────────────────────────────────────

def projeleri_formatla(projeler: list) -> str:
    """Proje listesini terminalde şık görünecek şekilde formatlar."""
    if not projeler:
        return "❌ Güncel proje bulunamadı."
        
    sonuc = "\n" + "═" * 75 + "\n"
    sonuc += f" 🚀 GitHub'da En Popüler Python Projeleri | 🕐 {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
    sonuc += "═" * 75 + "\n"
    
    for i, proje in enumerate(projeler, 1):
        isim = proje['isim'][:15]
        yildiz = f"⭐ {proje['yildiz']:,}"
        # Açıklama çok uzunsa terminali bozmaması için kırpıyoruz
        aciklama = proje['aciklama'][:40] + "..." if len(proje['aciklama']) > 40 else proje['aciklama']
        
        sonuc += f" {i}. 🔹 {isim:<15} | {yildiz:<11} | {aciklama}\n"
        
    sonuc += "═" * 75 + "\n"
    return sonuc

def get_info() -> str:
    """
    main.py tarafından çağrılacak ana fonksiyon.
    Ödevin beklediği 'news.get_info()' yapısını karşılar.
    """
    projeler = github_verisi_cek()
    if projeler:
        return projeleri_formatla(projeler)
    return "❌ GitHub servisi şu an kullanılamıyor."

# ── Giriş Noktası ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🌍 GitHub verileri getiriliyor...\n")
    print(get_info())