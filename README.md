# Cloudflare IP Tester with Xray

Tool untuk mengecek koneksi ke IP Cloudflare dengan range tertentu menggunakan Xray untuk menguji metode inject pada kartu nol kuota.

## Fitur

✨ **Auto-download Xray**: Otomatis download dan setup Xray-core sesuai OS Anda
📱 **Termux/Android Support**: Full support untuk Android devices via Termux
🔍 **Flexible IP Input**: Support CIDR, range notation, single IP, atau baca dari file
🚀 **Concurrent Testing**: Test banyak IP secara bersamaan (default: 10 concurrent)
📊 **Detailed Reports**: JSON, CSV, TXT, dan report lengkap
⚡ **Real-time Progress**: Progress bar dan live updates
🎯 **Top IPs Ranking**: Otomatis ranking IP tercepat berdasarkan latency

## Instalasi

### Android/Termux Users

**Untuk pengguna Android/Termux**, lihat panduan lengkap di **[TERMUX.md](TERMUX.md)**.

**Quick Setup:**
```bash
bash setup-termux.sh
python main.py
```

---

### Desktop/Laptop (Windows/Linux/macOS)

### 1. Clone/Download Project

```bash
cd d:\Absensi\cloudflare-ip-tester
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies yang dibutuhkan:
- `requests` - HTTP requests untuk testing
- `tqdm` - Progress bar
- `colorama` - Colored terminal output
- `ipaddress` - IP parsing

### 3. Xray-core Installation

**Xray akan otomatis didownload** saat pertama kali menjalankan tool. Tidak perlu install manual!

Namun, jika ingin install manual:
- Windows: Download dari [Xray Releases](https://github.com/XTLS/Xray-core/releases)
- Extract ke folder `xray/` di project ini

## Cara Penggunaan

### Basic Usage

```bash
# Test IP range dengan CIDR notation
python main.py --range "104.16.0.0/28"

# Test IP range dengan format range
python main.py --range "104.16.0.1-104.16.0.100"

# Test single IP
python main.py --range "104.16.0.1"

# Test IPs dari file
python main.py --range "@ips.txt"
```

### Zoom-Style Testing (RECOMMENDED for Zero-Quota)

**Zoom-style config** menggunakan DNS hosts mapping untuk routing optimal pada kartu nol kuota.

```bash
# Test dengan zoom-style config (RECOMMENDED)
python main.py \
  --range "170.114.45.0/24" \
  --server-url "vless://UUID@SERVER:443?type=ws&security=tls&sni=SERVER&path=/PATH" \
  --zoom-style

# Custom DNS domain untuk mapping
python main.py \
  --range "@zoom-ips.txt" \
  --server-url "vless://..." \
  --zoom-style \
  --dns-domain "api.ovo.id"

# Test quick dengan script batch
quick-test-zoom.bat
```

**Perbedaan Zoom-Style vs Standard:**
- ✅ **Zoom-style**: Domain di address + DNS hosts mapping → Optimal untuk zero-quota
- ⚙️ **Standard**: IP langsung di address → Testing basic

### Advanced Usage

```bash
# Custom SNI dan protocol
python main.py --range "104.16.0.0/24" --sni "example.com" --protocol vless

# Increase timeout dan concurrent tests
python main.py --range "104.16.0.0/24" --timeout 10 --concurrent 20

# Test semua Cloudflare IP ranges (ribuan IP!)
python main.py --cloudflare-ranges --concurrent 50

# Verbose mode (show each IP result)
python main.py --range "104.16.0.1-50" --verbose
```

### Parameter Lengkap

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `--range` | *required* | IP range (CIDR/range/single/@file) |
| `--cloudflare-ranges` | - | Test semua Cloudflare IP ranges |
| `--server-url` | - | vless/vmess/trojan URL (RECOMMENDED) |
| `--zoom-style` | `false` | Enable zoom-style config (DNS hosts) |
| `--dns-domain` | `api.ovo.id` | Domain untuk DNS mapping |
| `--use-domain-address` | `true` | Gunakan domain di address field |
| `--protocol` | `vmess` | Protocol: vmess/vless/trojan |
| `--sni` | `cloudflare.com` | SNI/Host untuk injection |
| `--port` | `443` | Port tujuan |
| `--timeout` | `5` | Timeout per IP (detik) |
| `--concurrent` | `10` | Jumlah test bersamaan |
| `--output` | `results.json` | Nama output file |
| `--top` | `10` | Jumlah top IP yang ditampilkan |
| `--verbose` | `false` | Show detail setiap IP |
| `--no-csv` | `false` | Jangan save CSV |

## Format Input IP

### 1. CIDR Notation
```bash
python main.py --range "104.16.0.0/24"
# Akan test 254 IPs (104.16.0.1 - 104.16.0.254)
```

### 2. Range Notation
```bash
python main.py --range "104.16.0.1-104.16.0.100"
# Atau short form:
python main.py --range "104.16.0.1-100"
```

### 3. File Input
Buat file `ips.txt`:
```
104.16.0.1
104.16.0.2-104.16.0.50
104.17.0.0/28
```

Jalankan:
```bash
python main.py --range "@ips.txt"
```

### 4. Cloudflare Ranges
```bash
python main.py --cloudflare-ranges
```
Tool sudah include semua official Cloudflare IP ranges.

## Output Files

Setelah testing selesai, akan generate beberapa file di folder `results/`:

1. **`results_TIMESTAMP.json`** - Full results dalam format JSON
2. **`results_TIMESTAMP.csv`** - Results dalam format CSV (Excel-friendly)
3. **`working_ips_TIMESTAMP.txt`** - List IP yang berhasil (sorted by latency)
4. **`report_TIMESTAMP.txt`** - Detailed text report

### Contoh working_ips.txt:
```
104.16.0.15 # 45.23ms
104.16.0.32 # 52.10ms
104.16.0.8 # 68.45ms
```

## Cara Kerja Injection Method

Tool ini menggunakan Xray dengan konfigurasi:
- **Transport**: WebSocket (WS)
- **Security**: TLS
- **SNI**: Custom (default: cloudflare.com)

Ini mensimulasi metode inject yang biasa dipakai untuk:
- ✅ Bug SNI
- ✅ Zero-rated traffic
- ✅ Port forwarding via Cloudflare

## Tips untuk Testing Kartu Nol Kuota

1. **Gunakan SNI yang tepat**: Sesuaikan `--sni` dengan operator Anda
   ```bash
   # Contoh untuk berbagai operator (sesuaikan dengan BUG yang valid):
   python main.py --range "104.16.0.0/24" --sni "zoom.us"
   python main.py --range "104.16.0.0/24" --sni "microsoft.com"
   ```

2. **Test dengan range kecil dulu**:
   ```bash
   python main.py --range "104.16.0.1-20" --verbose
   ```

3. **Increase timeout** jika koneksi lambat:
   ```bash
   python main.py --range "104.16.0.0/24" --timeout 10
   ```

4. **Pakai concurrent tinggi** untuk speed:
   ```bash
   python main.py --range "104.16.0.0/24" --concurrent 50
   ```

5. **Gunakan working IPs untuk config Xray Anda**:
   - Ambil IP dari `working_ips_*.txt`
   - Pakai IP tercepat untuk config Xray pribadi

## Troubleshooting

### Xray download gagal
Jika auto-download gagal, download manual:
1. Download dari https://github.com/XTLS/Xray-core/releases
2. Extract ke folder `xray/`
3. Pastikan file `xray.exe` (Windows) ada di folder tersebut

### Semua IP failed
- Cek koneksi internet Anda
- Coba increase `--timeout`
- Pastikan port 443 tidak diblock firewall
- Ganti `--sni` dengan domain lain

### Permission denied (Linux/Mac)
```bash
chmod +x xray/xray
```

### Module not found
```bash
pip install -r requirements.txt
```

## Advanced: Menggunakan IP Working di Xray Config

Setelah dapat IP working, buat config Xray:

```json
{
  "outbounds": [
    {
      "protocol": "vmess",
      "settings": {
        "vnext": [{
          "address": "104.16.0.15",  // IP tercepat dari hasil test
          "port": 443,
          "users": [{"id": "YOUR-UUID"}]
        }]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "serverName": "cloudflare.com"
        }
      }
    }
  ]
}
```

## Struktur Project

```
cloudflare-ip-tester/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config.example.json     # Config template
├── README.md              # Dokumentasi (file ini)
├── src/
│   ├── __init__.py
│   ├── xray_manager.py    # Auto-download Xray
│   ├── ip_generator.py    # Generate IP lists
│   ├── config_generator.py # Generate Xray configs
│   ├── connection_tester.py # Test connections
│   └── reporter.py        # Generate reports
├── xray/                  # Xray binary (auto-downloaded)
└── results/               # Output files
```

## Known Issues

- Pada Windows, mungkin muncul Windows Defender alert untuk Xray (false positive)
- Testing ribuan IP bisa memakan waktu lama
- Beberapa ISP mungkin rate-limit connection attempts

## Credits

- **Xray-core**: https://github.com/XTLS/Xray-core
- **Cloudflare IP Ranges**: https://www.cloudflare.com/ips/

## License

MIT License - Free to use and modify

---

**Catatan**: Tool ini untuk educational purposes. Pastikan Anda menggunakan sesuai dengan Terms of Service provider Anda.
