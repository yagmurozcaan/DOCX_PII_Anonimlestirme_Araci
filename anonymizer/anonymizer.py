import re
import json
import logging
import pandas as pd
from typing import List, Dict, Tuple

class Anonymizer:
    """
    DOCX belgelerinde PII (kişisel veriler) anonimleştirmesi yapan sınıf.
    Dinamik olarak kurum ve unvan listesi JSON dosyasından okunur.
    """
    def __init__(self, config_path: str):
        self.placeholder_counters: Dict[str, int] = {}
        self.placeholder_map: Dict[str, str] = {}
        self.mapping: List[Dict[str, str]] = []

        # JSON config oku
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Dinamik pattern oluştur
        self.patterns: List[Tuple[str, re.Pattern]] = []

        for ptype in ["KURUM", "UNVAN"]:
            if ptype in config and config[ptype]:
                joined = "|".join(re.escape(name) for name in config[ptype])
                self.patterns.append((ptype, re.compile(rf"\b({joined})\b", re.IGNORECASE)))

        # Diğer patternler sabit
        self.patterns.extend([
            ("VERGI_NUMARASI", re.compile(r"\b\d{3}\s?\d{3}\s?\d{2}\s?\d{2}|\d{10}\b")),
            ("TICARET_SICIL", re.compile(r"\b\d{6}\b")),
            ("DERNEK_KUTUK", re.compile(r"\b\d{2}/\d{3}-\d{3}\b")),
            ("IBAN", re.compile(r"\bTR[0-9]{2}(?:\s?[0-9]){22}\b")),
            ("BANKA_ADI", re.compile(r"\b(Garanti Bankası|Ziraat|Vakıfbank|Halkbank|İş Bankası|Akbank|Yapı Kredi)\b", re.IGNORECASE)),
            ("SUBE", re.compile(r"\b[\wÇĞİÖŞÜçğıöşü\s]+Şubesi\b", re.IGNORECASE)),
            ("TUTAR", re.compile(r"\b\d{1,3}(?:\.\d{3})*\s?-?\s?TL\b")),
            ("TELEFON", re.compile(r"(?:(?:\+90|0)\s?)?(?:\(?\d{3}\)?\s?)\d{3}\s?\d{2}\s?\d{2}")),
            ("E_POSTA", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
            ("TARIH", re.compile(r"\.\./\.\./2025|\b\d{2}[./-]\d{2}[./-]\d{4}\b")),
        ])

        # AD-SOYAD regex
        self.adsoyad_regex = re.compile(
            r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)"
            r"\s+([A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*)\b",
            re.UNICODE
        )
        self.adsoyad_after_placeholder = re.compile(
            r"(\[AD_SOYAD_\d+\])\s*([A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*)",
            re.UNICODE
        )

    # =========================
    # PLACEHOLDER YÖNETİMİ
    # =========================
    def get_placeholder(self, ptype: str, value: str) -> str:
        key_value = self.normalize_text(value) if ptype in ["KURUM", "BANKA_ADI"] else value.strip()
        key = f"{ptype}_{key_value}"
        if key in self.placeholder_map:
            return self.placeholder_map[key]

        count = self.placeholder_counters.get(ptype, 0) + 1
        self.placeholder_counters[ptype] = count
        ph = f"[{ptype}_{count}]"
        self.placeholder_map[key] = ph
        self.mapping.append({"TYPE": ptype, "ORIGINAL": value.strip(), "PLACEHOLDER": ph})
        return ph

    @staticmethod 
    def normalize_text(text: str) -> str:
        replacements = {"İ":"I","ı":"I","Ş":"S","ş":"S","Ç":"C","ç":"C",
                        "Ğ":"G","ğ":"G","Ö":"O","ö":"O","Ü":"U","ü":"U"}
        for k, v in replacements.items():
            text = text.replace(k, v)
        text = re.sub(r"[.,\-]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.upper().strip()

    # =========================
    # AD-SOYAD İŞLEME
    # =========================
    def handle_names(self, text: str) -> str:
        for first, last in self.adsoyad_regex.findall(text):
            total_words = len(first.split()) + len(last.split())
            if not last.isupper() or total_words > 4:
                continue
            banned = ["SÖZLEŞME","ULUSAL","POSTA","İDARESİ","DERNEĞİ","TÜRKİYE",
                      "MİLLİ","PARALİMPİK","KOMİTESİ","ANONİM","ŞİRKETİ"]
            if any(w.upper() in banned for w in first.split()):
                continue
            full = f"{first} {last}"
            text = text.replace(full, self.get_placeholder("AD_SOYAD", full))

        for ph, surname in self.adsoyad_after_placeholder.findall(text):
            if surname.isupper():
                ph2 = self.get_placeholder("AD_SOYAD", surname)
                text = text.replace(surname, ph2)
        return text

    # =========================
    # ADRES İŞLEME
    # =========================
    def process_address(self, text: str) -> str:
        addr_text = text.replace("\n", " ").replace("\t", " ").strip()
        pattern = (
            r"(?P<mahalle>[\wÇĞİÖŞÜçğıöşü\d\s]+(?:Mah\.?|Mahallesi))\s+"
            r"(?P<cadde>[\wÇĞİÖŞÜçğıöşü\d\s]+(?:Cad\.|Caddesi|Sok\.|Sk\.|Sokak))"
            r"(?:\s+No[: ]\s?(?P<no>\d+))?\s*"
            r"(?:\s*Kat[: ]\s?(?P<kat>\d+))?\s*"
            r"(?:(?P<ilce>[\wÇĞİÖŞÜçğıöşü\d\s]+)\s*/\s*(?P<il>[\wÇĞİÖŞÜçğıöşü\d\s]+))?"
        )
        match = re.search(pattern, addr_text, flags=re.IGNORECASE)
        if not match:
            return text

        addr = re.sub(r"\s+", " ", match.group(0)).strip()
        address_ph = self.get_placeholder("ADRES", addr)
        text = text.replace(addr, address_ph)

        fields = ["mahalle", "cadde", "sokak", "no", "kat", "ilce", "il"]
        for f in fields:
            if f in match.groupdict() and match.group(f):
                value = match.group(f)
                ph = self.get_placeholder(f.upper(), value.strip())
                text += f"\n{f.upper()}: {ph}"
        return text

    # =========================
    # GENEL PATTERNLERİ ANONİMLEŞTİRME
    # =========================
    def replace_patterns(self, text: str) -> str:
        for ptype, pattern in self.patterns:
            for m in pattern.findall(text):
                value = m if isinstance(m, str) else m[0]
                text = text.replace(value, self.get_placeholder(ptype, value))
        return text

    # =========================
    # TÜM METİN ANONİMLEŞTİRME
    # =========================
    def anonymize_text(self, text: str) -> str:
        text = self.handle_names(text)
        text = self.process_address(text)
        text = self.replace_patterns(text)
        return text

    # =========================
    # MAPPING CSV OLUŞTURMA
    # =========================
    def save_mapping(self, path: str):
        df = pd.DataFrame(self.mapping)
        if not df.empty:
            counts = df["ORIGINAL"].value_counts().to_dict()
            df["ID"] = range(1, len(df)+1)
            df["OCCURRENCE_COUNT"] = df["ORIGINAL"].apply(lambda x: counts[x])
            df = df.sort_values("TYPE")
        else:
            df = pd.DataFrame(columns=["TYPE","ORIGINAL","PLACEHOLDER","ID","OCCURRENCE_COUNT"])
        df.to_csv(path, index=False, encoding="utf-8-sig")
        logging.info(f"Mapping CSV başarıyla kaydedildi: {path}")
