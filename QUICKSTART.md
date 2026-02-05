# Cloudflare IP Tester with Xray - Quick Start Guide

## 🚀 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the interactive CLI
python main.py
```

Xray akan otomatis didownload saat pertama kali running!

## 📱 Termux/Android Installation

**Untuk pengguna Android**, lihat panduan lengkap di [TERMUX.md](TERMUX.md).

**Quick Setup di Termux:**
```bash
# Install dependencies
bash setup-termux.sh

# Run interactive mode
python main.py
```


## 📖 Interactive Mode

Program sekarang menggunakan **interactive wizard** yang mudah digunakan:

```bash
python main.py
```

Anda akan dipandu step-by-step untuk:

### Step 1: Select Testing Mode
- **Quick Test**: Test 100 IPs (~5 menit)
- **Custom Range**: Specify IP range Anda sendiri  
- **From File**: Load dari file txt
- **All Cloudflare**: Test semua IP Cloudflare

### Step 2: Server Configuration
- Masukkan server URL VLESS/VMESS/Trojan Anda
- Atau skip untuk testing mode saja

### Step 3: Zoom-Style Config
- Enable DNS hosts mapping untuk zero-quota
- Pilih DNS domain (default: api.ovo.id)
- Domain atau IP di address field

### Step 4: Test Parameters
- Timeout per IP (default: 10s)
- Concurrent tests (default: 20)
- Top IPs to display (default: 20)

### Step 5: Confirm & Run
- Review konfigurasi
- Konfirmasi untuk start test

## 📊 Output Files

Results tersimpan di folder `results/`:

- `working_ips_TIMESTAMP.txt` - IP tercepat yang berhasil
- `results_TIMESTAMP.json` - Full results JSON
- `results_TIMESTAMP.csv` - Excel-compatible CSV
- `report_TIMESTAMP.txt` - Detailed report

## 🎯 Quick Examples

### Test dengan Server Real (Zoom-Style)
```bash
python main.py
# Pilih: 1 (Quick Test)
# Server URL: vless://YOUR-UUID@YOUR-SERVER:443?...  
# Zoom-style: y
# DNS domain: api.ovo.id
# Start: y
```

### Run Xray dengan Config yang Sudah Ada

**Zoom-Style (dengan IP Mapping):**
```bash
.\xray\xray.exe run -c xray-zoom-config.json
# atau
run-xray-zoom.bat
```

**Direct (tanpa IP Mapping):**
```bash
.\xray\xray.exe run -c xray-direct-config.json
# atau
run-xray-direct.bat
```

**Proxy tersedia di:**
- SOCKS5: `127.0.0.1:10808`
- HTTP: `127.0.0.1:10809`

## 🔍 Speed Test

Test kecepatan koneksi Xray yang sedang running:

```bash
python xray-speedtest.py
# atau
xray-speedtest.bat
```

Akan test:
- ✓ Konektivitas proxy
- ✓ Latency ke berbagai domain
- ✓ Download speed
- ✓ Real-world website loading

## 📁 Project Structure

```
cloudflare-ip-tester/
├── main.py                    # Interactive CLI (START HERE!)
├── xray-speedtest.py          # Speed test tool
├── src/                       # Core modules
│   ├── config_generator.py    # Zoom-style config generator
│   ├── connection_tester.py   # IP testing engine
│   ├── ip_generator.py        # IP range parser
│   ├── reporter.py            # Report generator
│   ├── url_parser.py          # Server URL parser
│   └── xray_manager.py        # Auto Xray installer
├── xray-zoom-config.json      # Example zoom-style config
├── xray-direct-config.json    # Example direct config
├── run-xray-zoom.bat          # Quick run zoom config
├── run-xray-direct.bat        # Quick run direct config
├── xray-speedtest.bat         # Quick speed test
├── all-cloudflare-ips.txt     # All Cloudflare ranges
├── cloudflare-ips.txt         # Popular ranges
└── results/                   # Output folder
```

## 🎨 Features

✨ **Interactive CLI**: Step-by-step wizard, no command line arguments needed  
🔍 **Flexible IP Input**: CIDR, range, file, or all Cloudflare ranges  
🚀 **Concurrent Testing**: Test banyak IP bersamaan (configurable)  
📊 **Detailed Reports**: JSON, CSV, TXT, dan full report  
⚡ **Real-time Progress**: Progress bar dan live updates  
🎯 **Top IPs Ranking**: Automatic ranking berdasarkan latency  
🔧 **Zoom-Style Config**: DNS hosts mapping untuk zero-quota  
🧪 **Speed Test**: Built-in proxy speed tester  

## 💡 Tips

### 1. Gunakan Server URL Real
Untuk testing zero-quota yang akurat, HARUS pakai server URL real:
```
vless://UUID@SERVER:443?type=ws&security=tls&sni=SERVER&path=/PATH
```

### 2. Start dengan Quick Test
Jangan langsung test ribuan IP. Mulai dengan quick test (100 IPs) untuk validasi.

### 3. Zoom-Style untuk Zero-Quota
Enable zoom-style config jika testing untuk kartu nol kuota dengan SNI bug.

### 4. Pakai IP Working
Setelah test selesai, cek `working_ips_*.txt` dan gunakan IP tercepat di config Xray Anda.

## 🆘 Troubleshooting

### Xray download gagal
Download manual dari https://github.com/XTLS/Xray-core/releases  
Extract ke folder `xray/`

### Semua IP failed
- Cek koneksi internet
- Increase timeout
- Pastikan server credentials benar
- Test direct connection dulu (tanpa Cloudflare IP)

### Permission denied (Linux/Mac)
```bash
chmod +x xray/xray
chmod +x main.py
chmod +x xray-speedtest.py
```

## 📚 Documentation

- [ZOOM-TESTING.md](ZOOM-TESTING.md) - Comprehensive zoom-style guide
- [README.md](README.md) - Full documentation
- [USAGE.md](USAGE.md) - Detailed usage guide

## ⚠️ Disclaimer

Tool ini untuk educational purposes. Gunakan sesuai Terms of Service provider Anda.

---

**Ready to start?**
```bash
python main.py
```
