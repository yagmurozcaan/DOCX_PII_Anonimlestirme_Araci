import pytest
from anonymizer.anonymizer import Anonymizer

@pytest.fixture
def anonymizer():
    return Anonymizer(config_path="config.json")

def test_full_anonymization(anonymizer):
    text = (
        "Ali VELİ, Hacı Bayram Veli Mah. Şehit Teğmen Kalmaz Cad. No:2 Ulus/ANKARA, "
        "TR36 0006 2000 3470 0006 2982 94, test@example.com"
    )
    result = anonymizer.anonymize_text(text)
    # Her placeholder kontrolü
    assert "[AD_SOYAD_1]" in result
    assert "[ADRES_1]" in result
    assert "[IBAN_1]" in result
    assert "[E_POSTA_1]" in result
