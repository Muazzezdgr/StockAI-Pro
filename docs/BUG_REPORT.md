# 🐞 Test & Bug Report — StockAI Pro

| | |
|---|---|
| **Tested build** | v2.0 (`fb1ed8c` + local changes) → fixed in v2.1 |
| **Test types** | Unit, boundary value, data-integrity (ML leakage), regression, Streamlit smoke |
| **Tools** | pytest, Streamlit AppTest, synthetic price data (no network) |
| **Before fixes** | 52 unit tests run against the original code → **14 failed** |
| **After fixes** | 52 unit + 10 app smoke tests → **62 / 62 passed** ✅ |

Severity = impact on the user · Priority = how urgently it should be fixed.

## Summary

| ID | Title | Severity | Priority | Status |
|---|---|---|---|---|
| BUG-01 | Scaler fitted on full dataset → test data leaks into training | Medium | High | ✅ Fixed |
| BUG-02 | Backtest pairs each prediction with the **wrong day's** price (off by one) | High | High | ✅ Fixed |
| BUG-03 | Open position at period end not counted in win rate | Medium | Medium | ✅ Fixed |
| BUG-04 | Annualized return / Sharpe assume 252 periods for hourly and crypto data | Medium | Medium | ✅ Fixed |
| BUG-05 | Sentiment: substring matches ("against" → *gain*) and double counting ("risk") | Medium | Medium | ✅ Fixed |
| BUG-06 | Dashboard "model confidence" predicted **yesterday**, not tomorrow | High | High | ✅ Fixed |
| BUG-07 | News feature never called NewsAPI; fabricated headlines shown as Reuters/Bloomberg news | Critical | Highest | ✅ Fixed |
| BUG-08 | LSTM advertised in UI but unavailable in the deployed app (no TensorFlow) | Medium | High | ✅ Fixed |
| BUG-09 | Deprecated `use_container_width` (30 uses) — removal would break the live app | Low | Medium | ✅ Fixed |
| BUG-10 | No `.gitignore`; 21 `__pycache__/*.pyc` files committed | Low | Low | ✅ Fixed |
| OPEN-01 | Sidebar portfolio total labeled "TL" even when holdings are priced in USD | Low | Low | ⏳ Open |

---

## BUG-01 — Data leakage in feature scaling
`prepare_rf_data` / `prepare_lstm_data` called `scaler.fit_transform()` on **all** rows before the train/test split, so the min/max/mean of the test period influenced training.
**Impact:** None for Random Forest/Gradient Boosting (tree splits are scale-invariant), but real for LSTM (MinMax scaling). Fixed for correctness and so the pipeline stays valid if new models are added.
**Fix:** fit on the training slice only, then transform all rows.
**Tests:** `test_rf_scaler_sadece_egitim_verisiyle_fit_edilir`, `test_lstm_scaler_sadece_egitim_verisiyle_fit_edilir`

## BUG-02 — Backtest prices shifted by one day
`prepare_rf_data` drops the last row (its target is unknown) and splits `len(df) - 1` rows, but the backtest page computed its split from `len(df)`. For most data lengths, `int(0.8·N) ≠ int(0.8·(N-1))`, so every prediction was paired with the **next** day's price.
**Reproduce:** `test_tahminler_dogru_gunun_fiyatiyla_eslesir` inverse-transforms the test features and compares the real close price with the price used by the backtest → mismatch for 5 of 6 data lengths.
**Fix:** `fiyatlari_hizala()` uses the same split as the model data. The simulation moved to `utils/backtest_utils.py` so it can be unit-tested.

## BUG-03 — Open position excluded from win rate
If the strategy was still holding at the end, the trade was counted in `trades` but never closed, so it could never count as a win.
**Example:** buy at 100, price ends at 130, no sell signal → *1 trade, 0 wins, win rate 0%*.
**Fix:** close the position at the last price and record it in the trade log.

## BUG-04 — Wrong annualization for hourly and crypto data
Annual return and Sharpe ratio always used 252 periods/year. Hourly bars (~1,764/yr for stocks) and crypto (365 days, 24/7) were annualized incorrectly.
**Fix:** `periods_per_year(interval, crypto)`.

## BUG-05 — Sentiment keyword matching
Plain substring search (`"gain" in text`) produced false matches: *against* → gain, *enterprise* → rise, *execute* → cut, *highlights* → high. `"risk"` appeared in both the English and Turkish lists and was counted twice.
**Fix:** whole-word matching for English and stem matching for Turkish (an agglutinative language: *kazanç* → *kazancı*), plus Turkish-aware lowercasing.

## BUG-06 — "Model confidence" was yesterday's prediction
The dashboard used `X_test[-1]`, which is the **second-to-last** day (the last day has no label and is dropped). The "prediction" was therefore for a move that had already happened.
**Fix:** `yarin_icin_tahmin()` predicts from the latest day's indicators.
**Test:** changing the last day's features must change the prediction.

## BUG-07 — Fabricated news presented as real (critical)
`fetch_news(symbol)` was always called **without an API key**, so the app always showed five hard-coded headlines attributed to *Financial Times, Reuters, Bloomberg, WSJ, CNBC*. Their sentiment scores came from separate keyword strings, not from the headlines. Users had no way to know.
**Fix:** the key is read from `NEWSAPI_KEY` (env or Streamlit secrets). Without it, example headlines are labeled **"Örnek veri (demo)"**, sentiment is computed from the headline itself, and both news views show a clear warning.

## BUG-08 — LSTM advertised but unavailable
TensorFlow was removed from `requirements.txt` for cloud compatibility, but the UI still advertised "LSTM + RF + NLP", and selecting LSTM ended in an error.
**Fix:** the LSTM option and window slider appear only when TensorFlow is installed; UI texts list the models that actually run.

## BUG-09 — Deprecated Streamlit parameter
Streamlit warned that `use_container_width` would be removed. With `streamlit>=` in requirements, Streamlit Cloud installs the newest version, so the live app could break without any code change. Replaced with `width="stretch"`.

## BUG-10 — Build artifacts in the repository
No `.gitignore`; compiled `.pyc` files for two Python versions were committed. Added `.gitignore` (also excluding `.env`, `secrets.toml`, editor settings).

---

### A note on model accuracy
On a synthetic random-walk price series, the Random Forest scores **~51%**, which is what a correct pipeline should produce, since a random walk is unpredictable. A much higher score on such data would indicate leakage. This is a useful sanity check whenever the pipeline changes.
