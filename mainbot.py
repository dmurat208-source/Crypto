import time
import requests

# SİMÜLASYON AYARLARI
SANAL_BAKIYE = 100.0       # Başlangıç sanal bakiyesi (USDT)
ISLEM_BUTCESI = 10.0       # Her sanal işleme ayrılan bütçe (USDT)
KAR_HEDEFI_YUZDE = 2.0     # %2 kâr hedefi
STOP_LOSS_YUZDE = 1.0      # %1 stop-loss
TARAMA_ARALIGI = 15        # Saniye

# AKTİF SİMÜLASYON POZİSYONLARI
acik_pozisyonlar = {}

def piyasa_verisi_al():
    """Binance canlı 24s ticker verilerini çeker."""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        res = requests.get(url, timeout=5)
        return res.json()
    except Exception as e:
        print(f"[AĞ HATASI] Veri çekilemedi: {e}")
        return None

def anlik_fiyat_al(symbol):
    """Belirli bir çiftin anlık fiyatını çeker."""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5).json()
        return float(res['price'])
    except:
        return None

def pozisyonlari_guncelle():
    """Açık sanal pozisyonların kâr/zarar durumunu kontrol eder."""
    global SANAL_BAKIYE
    if not acik_pozisyonlar:
        return

    print("\n--- [SANAL POZİSYON TAKİBİ] ---")
    kapanacaklar = []

    for symbol, pos in acik_pozisyonlar.items():
        guncel_fiyat = anlik_fiyat_al(symbol)
        if not guncel_fiyat:
            continue

        degisim_pct = ((guncel_fiyat - pos['alıs_fiyati']) / pos['alıs_fiyati']) * 100
        print(f"> {symbol} | Giriş: {pos['alıs_fiyati']} | Güncel: {guncel_fiyat} | Anlık Durum: %{degisim_pct:.2f}")

        # Kâr Hedefi Kontrolü
        if degisim_pct >= KAR_HEDEFI_YUZDE:
            kazanc = pos['miktar_usdt'] * (1 + degisim_pct / 100)
            SANAL_BAKIYE += kazanc
            print(f"  [+] [SİMÜLASYON KÂR SATIŞI] {symbol} | Kâr: %{degisim_pct:.2f} | Yeni Bakiye: ${SANAL_BAKIYE:.2f}")
            kapanacaklar.append(symbol)

        # Stop-Loss Kontrolü
        elif degisim_pct <= -STOP_LOSS_YUZDE:
            kalan = pos['miktar_usdt'] * (1 + degisim_pct / 100)
            SANAL_BAKIYE += kalan
            print(f"  [-] [SİMÜLASYON STOP-LOSS] {symbol} | Zarar: %{degisim_pct:.2f} | Yeni Bakiye: ${SANAL_BAKIYE:.2f}")
            kapanacaklar.append(symbol)

    for sym in kapanacaklar:
        del acik_pozisyonlar[sym]

def check_breakout_sim():
    global SANAL_BAKIYE
    print(f"\n[SİMÜLASYON TARAMASI] Kasa: ${SANAL_BAKIYE:.2f} | Açık Pozisyon: {len(acik_pozisyonlar)}")
    
    tickers = piyasa_verisi_al()
    if not tickers:
        return

    for t in tickers:
        symbol = t['symbol']
        if symbol.endswith('USDT') and symbol not in acik_pozisyonlar:
            hacim = float(t['quoteVolume'])
            fiyat_degisim = float(t['priceChangePercent'])

            # Kırılım Kriteri: Hacim > 1M USDT ve Günlük Değişim > %3
            if hacim > 1000000 and fiyat_degisim > 3.0:
                fiyat = float(t['lastPrice'])
                
                if SANAL_BAKIYE >= ISLEM_BUTCESI:
                    SANAL_BAKIYE -= ISLEM_BUTCESI
                    acik_pozisyonlar[symbol] = {
                        'alıs_fiyati': fiyat,
                        'miktar_usdt': ISLEM_BUTCESI
                    }
                    print(f"\n>>> [SANAL ALIM YAPILDI] {symbol}")
                    print(f"    Fiyat: {fiyat} | Bütçe: ${ISLEM_BUTCESI} | Kalan Bakiye: ${SANAL_BAKIYE:.2f}")
                    break

def run_simulation():
    print("=" * 45)
    print("   CANLI PİYASA BREAKOUT SİMÜLATÖRÜ BAŞLATILDI   ")
    print("   (Gerçek API Key/Bakiye Kullanılmamaktadır)   ")
    print("=" * 45)
    
    while True:
        pozisyonlari_guncelle()
        check_breakout_sim()
        time.sleep(TARAMA_ARALIGI)

if __name__ == "__main__":
    run_simulation()
