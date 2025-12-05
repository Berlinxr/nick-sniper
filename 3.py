import time
import requests
import sys

# Discord API'ye erişim için gerekli olan Discord kullanıcı token'ınız.
# !!! Bu token hassas bir bilgidir. Güvenliğinden emin olun.
TOKEN = "BURAYA_KENDİ_DISCORD_TOKENINIZI_YAZIN" # <--- TOKENI BURAYA YAZMALISIN

DISCORD_API = "https://discord.com/api/v9/users/@me/pomelo-attempt"
OUTPUT_FILE = "approved.txt" # Kullanılabilir kullanıcı adlarının kaydedileceği dosya

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

def save_to_file(username):
    """
    Kullanılabilir kullanıcı adını belirtilen dosyaya kaydeder.
    """
    try:
        # Dosyayı "append" (a) modunda açar ve kullanıcı adını yeni bir satıra ekler
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(username + "\n")
        print(f" (Dosyaya kaydedildi: {OUTPUT_FILE})", end="")
    except Exception as e:
        print(f" (❌ KAYIT HATASI: {e})", end="")


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
            return False, "Rate Limit"

        if "taken" in data:
            if not data["taken"]:
                print(f"✅ KULLANILABİLİR!", end="")
                # Kullanılabilirse dosyaya kaydet
                save_to_file(username)
                print() # Yeni satıra geç
                return True, "Kullanılabilir"
            else:
                print(f"❌ ALINMIŞ.")
                return True, "Alınmış"
        else:
            # API'den beklenmedik yanıt veya hata
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
    print("-" * 70)
    print("Discord Kullanıcı Adı Kontrol Aracı (İnteraktif)")
    print(f"Kullanılabilir isimler '{OUTPUT_FILE}' dosyasına kaydedilecektir.")
    print("Çıkış yapmak için boş bırakıp Enter'a basın.")
    print("-" * 70)
    
    while True:
        try:
            raw_username = input("👉 Kontrol edilecek kullanıcı adı: ").strip()
            
            if not raw_username:
                print("\nÇıkış yapılıyor...")
                break

            # Kullanıcı adını kontrol et ve sonucu al
            success, message = check_single_username(raw_username)

            if message != "Rate Limit":
                # Rate Limit durumunda bekleme yapmıyoruz, hemen kullanıcıdan yeni girdi istiyoruz.
                # Diğer durumlarda sunucuyu yormamak için 2 saniye bekleme yap
                time.sleep(2) 

        except KeyboardInterrupt:
            print("\nÇıkış yapılıyor...")
            sys.exit(0)
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            break

if __name__ == "__main__":
    interactive_checker()
