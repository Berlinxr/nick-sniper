import time
import requests
import sys

# Discord API'ye erişim için gerekli olan Discord kullanıcı token'ınız.
# !!! Bu token hassas bir bilgidir. Güvenliğinden emin olun.
TOKEN = "BURAYA_KENDİ_DISCORD_TOKENINIZI_YAZIN" # <--- TOKENI YİNE BURAYA YAZMALISIN

DISCORD_API = "https://discord.com/api/v9/users/@me/pomelo-attempt"

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

def check_single_username(username):
    """
    Verilen tek bir kullanıcı adını Discord API üzerinden kontrol eder.
    """
    print(f"🔎 Kontrol ediliyor: {username}...", end=" ")
    
    try:
        res = requests.post(DISCORD_API, headers=HEADERS, json={"username": username})
        data = res.json()

        if res.status_code == 429:
            # Rate limit yedik
            retry = data.get("retry_after", 5)
            print(f"🚨 RATE LIMIT! {retry} saniye bekliyoruz.")
            time.sleep(retry + 1)
            # Rate limit sonrası tekrar deneme şansı vermek için False dönüyoruz
            return False, "Rate Limit"

        if "taken" in data:
            if not data["taken"]:
                print(f"✅ KULLANILABİLİR!")
                return True, "Kullanılabilir"
            else:
                print(f"❌ ALINMIŞ.")
                return True, "Alınmış"
        else:
            # API'den beklenmedik yanıt veya hata (örn: geçersiz format)
            print(f"⚠️ HATA! Mesaj: {data.get('message', 'Bilinmeyen hata')}")
            return True, data.get('message', 'Bilinmeyen hata')

    except requests.exceptions.RequestException as e:
        print(f"❌ BAĞLANTI HATASI: {e}")
        return True, "Bağlantı Hatası"
    except Exception as e:
        print(f"❌ BEKLENMEDİK HATA: {e}")
        return True, "Beklenmedik Hata"


def interactive_checker():
    """
    Kullanıcıdan sürekli girdi alarak kullanıcı adlarını kontrol eden ana döngü.
    """
    print("-" * 50)
    print("Discord Kullanıcı Adı Kontrol Aracı (İnteraktif)")
    print("Çıkış yapmak için boş bırakıp Enter'a basın.")
    print("-" * 50)
    
    while True:
        try:
            # Kullanıcıdan girdi alıyoruz
            raw_username = input("👉 Kontrol edilecek kullanıcı adı: ").strip()
            
            if not raw_username:
                # Boş girdi ile çıkış yapıyoruz
                print("\nÇıkış yapılıyor...")
                break

            # Kullanıcı adını kontrol et ve sonucu al
            success, message = check_single_username(raw_username)

            # Rate Limit yendiyse, tekrar döngü başına dönmeden bekleme yapma
            if message != "Rate Limit":
                # API'yi yormamak için her kontrol arasında bekleme
                time.sleep(2) 

        except KeyboardInterrupt:
            # Ctrl+C ile çıkış
            print("\nÇıkış yapılıyor...")
            sys.exit(0)
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            break

if __name__ == "__main__":
    interactive_checker()
