# Cloudflare IP Tester - Termux/Android Guide

Panduan lengkap untuk menjalankan Cloudflare IP Tester di Android menggunakan Termux.

## 📱 Persyaratan

- **Termux**: Aplikasi terminal emulator untuk Android
- **Storage**: Minimal 100 MB ruang kosong
- **RAM**: Minimal 2 GB (recommended 4 GB)
- **Android**: Versi 7.0 atau lebih baru

## 🚀 Instalasi

### 1. Install Termux

Download dan install Termux dari:
- [F-Droid](https://f-droid.org/packages/com.termux/) (RECOMMENDED)
- ⚠️ **JANGAN dari Google Play** (versi outdated)

### 2. Setup Storage Permission

Buka Termux dan jalankan:
```bash
termux-setup-storage
```
Izinkan akses storage saat diminta.

### 3. Clone/Download Project

**Metode 1: Menggunakan Git**
```bash
pkg install git -y
cd ~/storage/shared
git clone https://github.com/YOUR_REPO/cloudflare-ip-tester.git
cd cloudflare-ip-tester
```

**Metode 2: Manual Download**
1. Download ZIP project dari GitHub
2. Extract ke folder `/storage/emulated/0/cloudflare-ip-tester/`
3. Di Termux:
```bash
cd ~/storage/shared/cloudflare-ip-tester
```

### 4. Jalankan Setup Otomatis

```bash
bash setup-termux.sh
```

Script ini akan:
- ✅ Install Python
- ✅ Install dependencies (requests, tqdm, colorama, dll)
- ✅ Set executable permissions untuk semua script
- ✅ Verify instalasi

**Setup manual** (jika script gagal):
```bash
# Update packages
pkg update -y

# Install Python
pkg install python -y

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Cara Penggunaan

### Mode Interactive (RECOMMENDED)

```bash
python main.py
```

Anda akan dipandu step-by-step untuk:
1. Pilih mode testing (Quick/Custom/Domain/File)
2. Input server URL (jika ada)
3. Konfigurasi zoom-style (untuk zero-quota)
4. Set timeout dan concurrency
5. Start testing!

### Quick Test Scripts

**Basic Quick Test:**
```bash
# Edit quick-test.sh dulu, ganti VLESS_URL dengan server Anda
nano quick-test.sh  # atau vim quick-test.sh

# Jalankan
bash quick-test.sh
```

**Zoom-Style Test (Zero-Quota):**
```bash
# Edit dulu
nano quick-test-zoom.sh

# Jalankan
bash quick-test-zoom.sh
```

### Test Single IP Range

```bash
python main.py --range "104.16.0.1-50" --timeout 10 --concurrent 20
```

### Test dengan Server Real

```bash
python main.py \
  --range "170.114.45.1-100" \
  --server-url "vless://UUID@SERVER:443?type=ws&security=tls&path=/path" \
  --zoom-style \
  --dns-domain "api.ovo.id"
```

## 🔧 Running Xray di Termux

### Jalankan Xray dengan Config

**Direct Config:**
```bash
bash run-xray-direct.sh
```

**Zoom-Style Config:**
```bash
bash run-xray-zoom.sh
```

Proxy akan tersedia di:
- SOCKS5: `127.0.0.1:10808`
- HTTP: `127.0.0.1:10809`

### Speed Test

Pastikan Xray running, kemudian:
```bash
bash xray-speedtest.sh
```

## 📊 Output Files

Semua hasil di folder `results/`:
```
results/
├── working_ips_TIMESTAMP.txt    # IP yang berhasil
├── results_TIMESTAMP.json       # Full JSON
├── results_TIMESTAMP.csv        # Excel format
└── report_TIMESTAMP.txt         # Full report
```

## 💡 Tips untuk Android/Termux

### 1. Optimasi Concurrency

Android memiliki keterbatasan resource. Gunakan concurrency lebih rendah:
```bash
# Lebih aman untuk Android
python main.py --range "104.16.0.1-100" --concurrent 10

# Jangan terlalu tinggi (bisa crash)
# python main.py --concurrent 100  # ❌
```

### 2. Prevent Sleep/Timeout

**Gunakan Termux Wake Lock:**
```bash
# Install API Termux
pkg install termux-api -y

# Acquire wake lock
termux-wake-lock

# Jalankan test
python main.py

# Release wake lock setelah selesai
termux-wake-unlock
```

**Atau gunakan screen:**
```bash
pkg install screen -y

# Start screen session
screen -S iptest

# Jalankan test
python main.py

# Detach: Ctrl+A lalu D
# Reattach: screen -r iptest
```

### 3. Battery Optimization

- Disable battery optimization untuk Termux di Settings Android
- Gunakan charger saat testing banyak IP
- Monitor suhu device

### 4. Network Considerations

**Test dengan WiFi lebih stabil:**
```bash
# Check connection
ping -c 4 1.1.1.1
```

**Jika menggunakan mobile data:**
- Set timeout lebih tinggi: `--timeout 15`
- Reduce concurrency: `--concurrent 5`

### 5. Storage Management

**Check disk space:**
```bash
df -h ~/storage/shared
```

**Clean old results:**
```bash
rm -rf results/*
```

## 🆘 Troubleshooting

### Xray Download Gagal

**Error**: `Failed to download Xray`

**Solusi**:
```bash
# Download manual
pkg install wget -y
cd xray/
wget https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-arm64-v8a.zip
unzip Xray-linux-arm64-v8a.zip
chmod +x xray
./xray version  # test
```

### Permission Denied

```bash
chmod +x xray/xray
chmod +x *.sh
```

### Module Not Found

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Termux Session Killed

- Android menutup background apps untuk save battery
- Solusi: 
  1. Disable battery optimization untuk Termux
  2. Gunakan `termux-wake-lock`
  3. Gunakan `screen` atau `tmux`

### Out of Memory

Reduce concurrent tests:
```bash
python main.py --range "104.16.0.1-20" --concurrent 5
```

### Slow Performance

ARM processors lebih lambat dari desktop:
- Test dalam batch kecil
- Gunakan `--concurrent 10` max
- Close aplikasi lain

## 📝 File Penting untuk Termux

```
cloudflare-ip-tester/
├── setup-termux.sh          # Setup script
├── main.py                  # Main app (works on Termux!)
├── quick-test.sh            # Quick test (Termux version)
├── quick-test-zoom.sh       # Zoom test (Termux version)
├── run-xray-direct.sh       # Run Xray direct
├── run-xray-zoom.sh         # Run Xray zoom
├── xray-speedtest.sh        # Speed test
└── results/                 # Output folder
```

## 🎨 Architecture Info

Termux menjalankan Linux di Android. Script otomatis mendeteksi:
```bash
OS: linux
Architecture: aarch64 (ARM64)
Xray binary: Xray-linux-arm64-v8a.zip
```

## ⚠️ Known Issues di Termux

1. **Battery drain**: Testing banyak IP menguras baterai
2. **Memory limits**: Android bisa kill app jika RAM habis
3. **Network throttling**: Beberapa ISP limit concurrent connections
4. **Storage**: Results bisa besar untuk testing ribuan IP

## 🔗 Resources

- [Termux Wiki](https://wiki.termux.com/)
- [Termux F-Droid](https://f-droid.org/packages/com.termux/)
- [Xray Core](https://github.com/XTLS/Xray-core)

## 📞 Support

Jika ada masalah khusus Termux, sertakan info:
```bash
# System info
uname -a
python --version
pip list | grep -E "requests|tqdm|colorama"
```

---

**Happy Testing di Android! 🚀📱**
