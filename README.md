# 📊 ETF Analiz Aracı

Bu Python aracı, **ETF’ler (Exchange Traded Fund)** üzerinde iki temel analiz yapmanıza olanak tanır:

---

## 🔍 ETF Overlap Analizi
- İki ETF’nin portföylerindeki ortak hisseleri (**overlap**) hesaplar.  
- Overlap oranını renkli olarak görselleştirir:  

✅ **Yeşil (Düşük overlap):** Portföy çeşitlendirmesi yüksek.  
🟡 **Sarı (Orta overlap):** Dengeli çeşitlendirme, bazı ortak hisseler mevcut.  
🔴 **Kırmızı (Yüksek overlap):** ETF’ler büyük oranda aynı hisselere yatırım yapıyor, çeşitlendirme sınırlı.  

---

## 📈 CAGR ve Temettü Analizi
- Bir veya birden fazla ETF için **CAGR (Compound Annual Growth Rate)** ve **ortalama temettü verimini** hesaplar.  
- Sonuçları tablo halinde gösterir.
- **✅ seekingalpha, etfdb, investing gibi sitelerdeki 10 yıllık veri için ücret talep edilirken bununla ücretsiz CAGR hesaplayabilirsiniz**

---

## 🚀 Özellikler
- **Retry mekanizması** ile daha güvenilir veri çekme (yfinance & API çağrıları).  
- **Renkli çıktı** ile overlap oranının kolay yorumlanması.  
- **Tablo formatında raporlama** (`tabulate` kütüphanesi ile).  
- **Hata yönetimi ve loglama** (`logging` ile detaylı kayıt tutulur).  

---

## 📦 Gereksinimler
Python **3.8+** sürümü önerilir.  
Gerekli kütüphaneleri kurmak için:  

```bash```
pip install yfinance tabulate requests 
---

## ⚡ Kullanım
- Program çalıştırıldığında size bir menü sunulur: 
- 1 → **ETF Overlap:** İki ETF’nin portföylerinde aynı şirketlere sahip olma ve bu şirketlerin toplam ağırlıklarının kesişim oranını gösterir.  
- 2 → **CAGR Hesaplama:** Yıllık Bileşik Büyüme Oranı (CAGR) ve Ortalama Temettü Verimini hesaplar.  
- **🔹 Örnek 1 — ETF Overlap**
-  ETF1 kodunu giriniz: VOO
-  ETF2 kodunu giriniz: QQQ

  **Çıktı:**
-  **Toplam overlap ağırlığı:** 🔴 65.78%
-  **Açıklama: Yüksek overlap** → Çoğunlukla aynı hisseler, risk azaltımı sınırlı.


- **🔹 Örnek 2 — CAGR ve Temettü**
-  ETF sembollerini virgülle ayırarak giriniz (örn: VOO,SCHD,QQQ): FDVV,QQQM,VOO
-  Kaç yıllık veri istersiniz? (örn: 5): 5

  **Çıktı:**

<img width="706" height="318" alt="image" src="https://github.com/user-attachments/assets/62034356-8cbc-41bf-959a-153e9e843bfe" />

---

## 📌Notlar
 - **Overlap oranı yalnızca ağırlık bazlı hesaplanır.**
 - **Yüksek overlap portföy çeşitlendirmesini azaltabilir.**
 - **CAGR ve temettü oranları geçmiş veriye dayalıdır, gelecek performansı garanti etmez.**







