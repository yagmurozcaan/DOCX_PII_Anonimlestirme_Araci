import pytest
from anonymizer.anonymizer import Anonymizer

def test_handle_names():
    anonymizer = Anonymizer(config_path="config.json")
    text = "Ali VELİ"
    result = anonymizer.handle_names(text)
    assert "[AD_SOYAD_1]" in result
