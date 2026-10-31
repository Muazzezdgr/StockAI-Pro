"""Sözlük tabanlı haber duygu analizi."""
import pytest

from utils.sentiment_utils import analyze_sentiment_lexicon


@pytest.mark.parametrize("metin, beklenen", [
    ("Apple shares rally after record profit", "Pozitif"),
    ("Tesla stock crash as losses deepen and sales decline", "Negatif"),
    ("Company to hold annual meeting on Tuesday", "Nötr"),
    ("", "Nötr"),
])
def test_temel_siniflandirma(metin, beklenen):
    assert analyze_sentiment_lexicon(metin)["label"] == beklenen


@pytest.mark.parametrize("metin", [
    "Regulators move against the enterprise software merger",  # "gain" ⊂ against, "rise" ⊂ enterprise
    "Board will execute the plan on schedule",                 # "cut" ⊂ execute
    "Highlights from the shareholder meeting",                 # "high" ⊂ highlights
])
def test_kelime_parcasi_yanlis_eslesmez(metin):
    """Kelimeler tam eşleşmeli; başka bir kelimenin içinde geçmesi sayılmamalı."""
    sonuc = analyze_sentiment_lexicon(metin)
    assert sonuc["pos"] == 0 and sonuc["neg"] == 0


def test_ayni_kelime_iki_kez_sayilmaz():
    """'risk' hem İngilizce hem Türkçe listede olduğu için çift sayılıyordu."""
    assert analyze_sentiment_lexicon("Analysts see risk ahead")["neg"] == 1


def test_turkce_kelimeler_taninir():
    assert analyze_sentiment_lexicon("Şirketin karında güçlü büyüme ve rekor artış")["label"] == "Pozitif"
