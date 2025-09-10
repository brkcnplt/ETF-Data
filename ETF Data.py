import yfinance as yf
from datetime import datetime
import pandas as pd
from tabulate import tabulate
import requests
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import List, Dict, Union, Optional

# -------------------- Constants --------------------
LOW_OVERLAP_THRESHOLD = 30
HIGH_OVERLAP_THRESHOLD = 60
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # yfinance retry için bekleme çarpanı

# -------------------- Logging --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------------------- Requests Session with Retry --------------------
session = requests.Session()
retries = Retry(total=MAX_RETRIES, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)


def fetch_yf_history(ticker: yf.Ticker, period: str) -> pd.DataFrame:
    """
    yfinance history fonksiyonu için retry ile güvenli çağrı.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = ticker.history(period=period)
            if not data.empty:
                return data
            logging.warning(f"Boş veri döndü (attempt {attempt})")
        except Exception as e:
            logging.warning(f"yfinance hata (attempt {attempt}): {e}")
        time.sleep(BACKOFF_FACTOR ** attempt)
    return pd.DataFrame()


def calc_cagr_with_dividend(etf_name: str, years: int) -> Optional[List[Union[str, float]]]:
    """
    Belirli bir ETF için CAGR (Compound Annual Growth Rate) ve
    ortalama temettü verimini hesaplar.
    """
    try:
        ticker = yf.Ticker(etf_name)
        data = fetch_yf_history(ticker, f"{years}y")

        if data.empty:
            logging.warning(f"Veri bulunamadı: {etf_name}")
            return None

        price_col = "Adj Close" if "Adj Close" in data.columns else "Close"
        first_date, last_date = data.index[0], data.index[-1]
        first_price, last_price = data[price_col].iloc[0], data[price_col].iloc[-1]

        years_diff = max((last_date - first_date).days / 365.0, 1.0)
        cagr = ((last_price / first_price) ** (1 / years_diff) - 1) * 100

        # Temettü hesaplama
        avg_div_yield = 0
        dividends = ticker.dividends
        if not dividends.empty:
            dividends.index = dividends.index.tz_localize(None)
            start_date = datetime.now() - pd.DateOffset(years=years)
            recent_divs = dividends[dividends.index >= start_date]
            if not recent_divs.empty:
                avg_div_yield = (recent_divs.sum() / years_diff) / ((first_price + last_price) / 2) * 100

        return [etf_name, round(cagr, 2), round(avg_div_yield, 2)]

    except Exception as e:
        logging.error(f"Hata oluştu ({etf_name}): {e}")
        return None


def get_etf_overlap(etf1: str, etf2: str) -> Union[str, Dict]:
    """
    İki ETF arasındaki overlap oranlarını hesaplar.
    """
    try:
        url = f"https://api.wisesheets.io/public/compare-etfs?etf1={etf1}&etf2={etf2}"
        response = session.get(url, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            return f"API hatası: {response.status_code}"

        data = response.json()
        profiles = data.get("profiles", [])

        if not profiles:
            return "ETF verisi bulunamadı."

        total_overlap = sum(item.get("overlapWeight", 0) for item in profiles)
        total_etf1 = sum(item.get("etf1Weight", 0) for item in profiles)
        total_etf2 = sum(item.get("etf2Weight", 0) for item in profiles)

        return {
            "total_overlap": total_overlap,
            "overlap_percent_etf1": (total_overlap / total_etf1) * 100 if total_etf1 else 0,
            "overlap_percent_etf2": (total_overlap / total_etf2) * 100 if total_etf2 else 0,
            "profiles": profiles
        }
    except Exception as e:
        logging.error(f"ETF overlap alınırken hata oluştu: {e}")
        return f"Hata oluştu: {e}"


def print_overlap_with_color(overlap_percent: float) -> None:
    """
    Overlap oranını renklendirerek yazdırır ve loglar.
    """
    RED, YELLOW, GREEN, RESET = '\033[91m', '\033[93m', '\033[92m', '\033[0m'

    try:
        if overlap_percent < LOW_OVERLAP_THRESHOLD:
            color, explanation = GREEN, "Çok düşük overlap → Portföy çeşitlendirmesi yüksek."
        elif LOW_OVERLAP_THRESHOLD <= overlap_percent <= HIGH_OVERLAP_THRESHOLD:
            color, explanation = YELLOW, "Orta seviyede overlap → Dengeli çeşitlendirme ve bazı ortak hisseler."
        else:
            color, explanation = RED, "Yüksek overlap → Çoğunlukla aynı hisseler, risk azaltımı sınırlı."

        message = f"Toplam overlap ağırlığı: {overlap_percent:.2f}% | Açıklama: {explanation}"

        # Hem print hem log
        print(f"\nToplam overlap ağırlığı: {color}{overlap_percent:.2f}%{RESET}")
        print(f"Açıklama: {explanation}\n")
        logging.info(message)

    except Exception as e:
        logging.error(f"Overlap sonucu yazdırılırken hata oluştu: {e}")


if __name__ == "__main__":
    try:
        options = [
            ["1", "ETF Overlap", "İki ETF’nin portföylerinde aynı şirketlere sahip olma ve bu şirketlerin toplam ağırlıklarının kesişim oranını gösterir."],
            ["2", "CAGR Hesaplama", "Yıllık Bileşik Büyüme Oranı (CAGR) ve Ortalama Temettü Verimini hesaplar."]
        ]

        print(tabulate(options, headers=["Seçenek", "İşlem", "Açıklama"], tablefmt="fancy_grid"))
        choice = input("\nLütfen yapmak istediğiniz işlemi seçin (1 veya 2): ").strip()

        if choice == "2":
            etf_input = input("ETF sembollerini virgülle ayırarak giriniz (örn: VOO,SCHD,QQQ): ").strip()
            if not etf_input:
                raise ValueError("Hiç ETF girmediniz!")

            years_input = input("Kaç yıllık veri istersiniz? (örn: 5): ").strip()
            if not years_input.isdigit():
                raise ValueError("Yıl sayısı geçersiz.")
            years = int(years_input)

            etf_list = [e.strip().upper() for e in etf_input.split(",")]
            table_data = [res for etf in etf_list if (res := calc_cagr_with_dividend(etf, years))]

            if table_data:
                headers = ["ETF", f"CAGR {years}Y (%) [Total Return]", f"Avg Dividend {years}Y (%)"]
                print("\nETF Performans Tablosu:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("Hiçbir ETF verisi bulunamadı veya hatalı girdiniz.")

        elif choice == "1":
            etf1 = input("ETF1 kodunu giriniz: ").strip().upper()
            etf2 = input("ETF2 kodunu giriniz: ").strip().upper()

            if not etf1 or not etf2:
                raise ValueError("ETF kodları boş olamaz!")

            result = get_etf_overlap(etf1, etf2)
            if isinstance(result, dict):
                print_overlap_with_color(result['total_overlap'])
            else:
                print(result)
        else:
            print("Geçersiz seçim. Lütfen 1 veya 2 giriniz.")

    except Exception as e:
        logging.critical(f"Beklenmedik bir hata oluştu: {e}")
