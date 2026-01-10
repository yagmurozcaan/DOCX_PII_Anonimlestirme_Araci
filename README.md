# DOCX PII Anonimleştirme Aracı

Bu proje, **DOCX belgelerinde kişisel olarak tanımlanabilir bilgileri (PII) tespit edip anonimleştirmek** için geliştirilmiş bir Python aracıdır.  
Kurum ve unvan isimlerini **dinamik JSON listesi** üzerinden alır ve placeholder’lar ile değiştirir. Ayrıca mapping CSV dosyası oluşturarak hangi verinin hangi placeholder ile değiştirildiğini kaydeder.

---

## Özellikler

- Word belgelerindeki (DOCX) tüm paragraflar ve tablolar anonimleştirilebilir.
- **Ad–Soyad**, **Adres (Mahalle/Cadde/Sokak/No/Kat/İlçe/İl)**, **Telefon**, **E-posta**, **IBAN**, **Vergi Numarası**, **Ticaret Sicil**, **Dernek Kütük Numarası**, **Tutar**, **Tarih** gibi PII’leri tanır ve anonimleştirir.
- Kurum ve unvanlar **JSON konfigürasyonu** ile dinamik olarak yönetilir.
- Mapping CSV dosyası ile orijinal ve placeholder bilgileri kaydedilir.
- CLI desteği ile kolayca çalıştırılabilir.

---


## 📁 Proje Yapısı

```
DOCX_PII_Anonimlestirme_Araci/
│
├─ anonymizer/
│   ├─ __init__.py
│   ├─ anonymizer.py       # Anonymizer sınıfı
│   └─ doc_handler.py      # DocProcessor sınıfı
│
├─ tests/
│   ├─ __init__.py
│   ├─ test_core.py        # Unit testler
│   └─ test_integration.py # Integration testler
│
├─ main.py                 # Programın çalıştırılabilir kısmı
├─ config.json             # Kurum ve unvan listesi
├─ requirements.txt
└─ README.md
```

---

## Gereksinimler

- Python 3.10+
- Paketler:

```bash
pip install python-docx pandas
```

---

## Kurulum

1. Projeyi klonlayın veya indirin.
2. `config.json` dosyasını oluşturun ve kurum/unvan listelerinizi ekleyin.
3. Python paketlerini yükleyin:

```bash
pip install -r requirements.txt
```

`requirements.txt` içeriği:
```
python-docx
pandas
```

---

## JSON Konfigürasyon Örneği (`config.json`)

```json
{
  "KURUM": [
    "TÜRKİYE MİLLİ PARALİMPİK KOMİTESİ DERNEĞİ",
    "POSTA VE TELGRAF TEŞKİLATI ANONİM ŞİRKETİ",
    "ULUSAL POSTA İDARESİ",
    "Türkiye Milli Paralimpik Komitesi Derneği",
    "TÜRKİYE İSTATİSTİK KURUMU",
    "TÜRK TELEKOM A.Ş.",
    "ZİRAAT BANKASI",
    "VAKIFBANK",
    "HALKBANK",
    "AKBANK",
    "YAPI KREDİ BANKASI",
    "TÜRKİYE BÜYÜK MİLLET MECLİSİ",
    "SAĞLIK BAKANLIĞI",
    "MİLLİ EĞİTİM BAKANLIĞI",
    "ULAŞTIRMA VE ALTYAPI BAKANLIĞI"
  ],
  "UNVAN": [
    "Genel Müdür Yardımcısı",
    "Genel Müdür",
    "Genel Koordinatör",
    "Başkan",
    "Müdür",
    "Direktör",
    "Proje Yöneticisi",
    "Yazılım Mühendisi",
    "Sistem Analisti",
    "Veri Bilimci",
    "İK Müdürü",
    "Finans Müdürü",
    "Operasyon Koordinatörü",
    "Satış Müdürü",
    "Pazarlama Müdürü",
    "Bilgi Teknolojileri Direktörü"
  ]
}

```

> Kurum ve unvan listelerini dilediğiniz kadar çoğaltabilir ve güncelleyebilirsiniz. Kod otomatik olarak JSON’dan okur.

---

## Kullanım

### CLI ile çalıştırma

```bash
python main.py --input case_09_01_2026.docx --output results/case_09_01_2026_anonymized.docx --mapping results/case_09_01_2026_mapping.csv --config config.json
```

Parametreler:

| Parametre | Açıklama |
|-----------|----------|
| `--input` | Girdi DOCX dosyası |
| `--output` | Anonimleştirilmiş DOCX dosyası |
| `--mapping` | Placeholder mapping CSV dosyası |
| `--config` | Kurum ve unvan JSON konfigürasyonu |

---

### Örnek Çalışma

**Orijinal metin:**

```
TÜRKİYE MİLLİ PARALİMPİK KOMİTESİ DERNEĞİ Başkanı Ali YILMAZ Ulus Mah. Atatürk Cad. No:5 Kat:2 Altındağ/ANKARA
```

**Anonimleştirilmiş çıktı:**

```
[KURUM_1] [AD_SOYAD_1] ADRES_1
MAHALLE: MAHALLE_1
CADDE: CADDE_1
NO: NO_1
KAT: KAT_1
ILCE: ILCE_1
IL: IL_1
```

**Mapping CSV:**

| TYPE     | ORIGINAL                                 | PLACEHOLDER | ID | OCCURRENCE_COUNT |
|----------|-----------------------------------------|------------|----|----------------|
| KURUM    | TÜRKİYE MİLLİ PARALİMPİK KOMİTESİ DERNEĞİ | [KURUM_1] | 1  | 1              |
| AD_SOYAD | Ali YILMAZ                               | [AD_SOYAD_1] | 2  | 1              |
| ADRES    | Ulus Mah. Atatürk Cad. No:5 Kat:2 Altındağ/ANKARA | [ADRES_1] | 3  | 1              |

---

## Özelleştirme

- **Yeni kurum veya unvan ekleme:** `config.json` içine eklemeniz yeterli.
- **Yeni PII türleri ekleme:** `main.py` içindeki `self.patterns` listesine yeni regex ekleyebilirsiniz.
- **Adres ve ad-soyad ayarları:** Kodda mevcut regex’ler Türkçe karakterleri ve standart adres formatlarını destekler.

---

## İpuçları ve Profesyonel Kullanım

- Çok sayıda belgeyi işlemek için Python script’i bir **batch işlem** ile çalıştırabilirsiniz.
- Mapping CSV dosyası **denetim ve raporlama** için kullanılabilir.
- JSON konfigürasyon ile kurum ve unvan listeleri sürekli güncellenebilir, kod değişmeden kullanılabilir.
- Logging sayesinde hangi adımda hata oluştuğunu kolayca takip edebilirsiniz.

---


**Testleri çalıştır**
```bash
pytest tests/
```

Çıktıda:
- ✅ Başarılı testler yeşil  
- ❌ Başarısız testler kırmızı  

**Testlerin anlamı**
- `tests/test_core.py` → **Unit Test** (tekil metodlar)  
- `tests/test_integration.py` → **Integration Test** (tüm sınıf akışı)  

Örnek çıktı:
```text
======================================================== test session starts =========================================================
platform win32 -- Python 3.10.0, pytest-9.0.2
collected 2 items

tests/test_core.py .                                                                                                            [ 50%] 
tests/test_integration.py .                                                                                                     [100%]

========================================================= 2 passed in 2.22s ==========================================================
```

---