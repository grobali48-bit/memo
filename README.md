# AVAXUSDT EMA13 Telegram Alert Bot — GitHub Actions

Bot, Binance Spot AVAXUSDT 1 saatlik kapanmış mumları kontrol eder.

Sinyal:
- Önceki kapanış <= önceki EMA13
- Son kapanış > son EMA13

Şart oluşursa Telegram'a mesaj gönderir. İşlem açmaz/kapatmaz.

## GitHub kurulumu

1. GitHub'da bir repository oluştur.
2. Bu klasördeki dosyaları repository'ye yükle.
3. Repository → Settings → Secrets and variables → Actions → New repository secret.
4. Şunları ekle:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. Actions sekmesine gir.
6. Workflow'u manuel olarak `Run workflow` ile bir kez test edebilirsin.

## Zamanlama

Workflow her saat UTC'nin 2. dakikasında çalışır.

GitHub Actions zamanlamaları yoğunluk nedeniyle birkaç dakika gecikebilir. Bot sadece kapanmış Binance mumlarını kontrol ettiği için açık mumdan yanlış sinyal üretmez.

## Önemli

GitHub Actions cron çalışmasının tam dakikasında başlaması garanti değildir. Bu nedenle saatlik alarmda birkaç dakikalık gecikme olabilir.

Telegram tokenını kodun içine koyma; GitHub Secrets kullan.
