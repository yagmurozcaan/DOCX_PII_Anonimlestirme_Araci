import pytest
from anonymizer.anonymizer import Anonymizer

@pytest.fixture
def anonymizer():
    return Anonymizer(config_path="config.json")

def test_handle_names_basic(anonymizer):
    text = "Ali VELİ"
    result = anonymizer.handle_names(text)
    assert "[AD_SOYAD_1]" in result

def test_handle_names_ignore_banned(anonymizer):
    text = "TÜRKİYE MİLLİ PARALİMPİK KOMİTESİ"
    result = anonymizer.handle_names(text)
    # Banned kelimeler placeholder olmaz
    assert "[AD_SOYAD" not in result

def test_process_address_basic(anonymizer):
    text = "Hacı Bayram Veli Mah. Şehit Teğmen Kalmaz Cad. No:2 Kat:2 Ulus/ANKARA"
    result = anonymizer.process_address(text)
    assert "[ADRES_1]" in result
    assert "MAHALLE" in result
    assert "CADDE" in result

def test_replace_patterns_iban(anonymizer):
    text = "TR36 0006 2000 3470 0006 2982 94"
    result = anonymizer.replace_patterns(text)
    assert "[IBAN_1]" in result

def test_replace_patterns_email(anonymizer):
    text = "test@example.com"
    result = anonymizer.replace_patterns(text)
    assert "[E_POSTA_1]" in result
