# Zoom-Style Config Testing Guide

## Apa itu Zoom-Style Config?

Zoom-style config adalah metode konfigurasi Xray yang menggunakan **DNS hosts mapping** untuk meroute traffic melalui IP Cloudflare sambil tetap mempertahankan SNI/Host headers yang benar.

### Konsep Utama

```
┌─────────────┐    DNS Mapping     ┌──────────────┐
│ Your Device │ ──────────────────▶│ Cloudflare IP│
└─────────────┘   api.ovo.id       └──────────────┘
                   ↓                       ↓
                 Domain              Real Server
                in Address         (via SNI header)
```

**Cara Kerja:**
1. DNS hosts map `api.ovo.id` → `170.114.45.6` (Cloudflare IP)
2. Outbound address menggunakan `api.ovo.id` (domain)
3. `domainStrategy: "UseIP"` memaksa Xray resolve ke mapped IP
4. SNI tetap ke server asli: `point.natss.store`

## Kenapa Pakai Zoom-Style?

✅ **Bypass zero-quota**: Operator melihat traffic ke domain gratis (api.ovo.id)  
✅ **Fleksibel**: Bisa ganti IP Cloudflare tanpa ubah address  
✅ **Testing optimal**: Test banyak IP dengan satu server config  

## Cara Penggunaan

### Basic Usage

```bash
# Test dengan zoom-style config
python main.py \
  --range "170.114.45.0/24" \
  --server-url "vless://UUID@SERVER:443?type=ws&security=tls&sni=SERVER&path=/PATH" \
  --zoom-style
```

### Advanced Options

```bash
# Custom DNS domain
python main.py \
  --range "@cloudflare-ips.txt" \
  --server-url "vless://..." \
  --zoom-style \
  --dns-domain "custom.domain.id"

# Use direct IP in address (hybrid mode)
python main.py \
  --range "104.16.0.0/28" \
  --server-url "vless://..." \
  --zoom-style \
  --no-use-domain-address
```

### Quick Test Script

```bash
# Generate dan lihat sample zoom config
python test-zoom-config.py
```

## Parameter Reference

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `--zoom-style` | `false` | Enable zoom-style config |
| `--dns-domain` | `api.ovo.id` | Domain untuk DNS mapping |
| `--use-domain-address` | `true` | Gunakan domain di address field |
| `--no-use-domain-address` | - | Gunakan IP direktCdi address |

## Contoh Config yang Dihasilkan

### Zoom-Style (Domain in Address)
```json
{
  "dns": {
    "hosts": {
      "api.ovo.id": ["170.114.45.6"]
    }
  },
  "outbounds": [{
    "settings": {
      "vnext": [{
        "address": "api.ovo.id",  // ← Domain
        "port": 443
      }]
    },
    "streamSettings": {
      "sockopt": {
        "domainStrategy": "UseIP"  // ← Force mapped IP
      },
      "tlsSettings": {
        "serverName": "point.natss.store"  // ← Real SNI
      }
    }
  }]
}
```

### Direct IP Method
```json
{
  "dns": {
    "hosts": {
      "api.ovo.id": ["170.114.45.6"]
    }
  },
  "outbounds": [{
    "settings": {
      "vnext": [{
        "address": "170.114.45.6",  // ← Direct IP
        "port": 443
      }]
    }
  }]
}
```

## Use Cases

### 1. Zero-Quota Testing
```bash
# Test IP Cloudflare untuk kartu nol kuota
python main.py \
  --range "@zoom-ips.txt" \
  --server-url "vless://YOUR-UUID@your-server.com:443?..." \
  --zoom-style \
  --dns-domain "api.ovo.id" \
  --timeout 10 \
  --concurrent 20
```

### 2. Batch Testing Multiple Domains
```bash
# Test beberapa domain mapping
for domain in api.ovo.id support.zoom.us teams.microsoft.com; do
  python main.py \
    --range "104.16.0.1-100" \
    --server-url "vless://..." \
    --zoom-style \
    --dns-domain "$domain"
done
```

### 3. Find Best IP for Specific Domain
```bash
# Cari IP tercepat untuk domain tertentu
python main.py \
  --cloudflare-ranges \
  --server-url "vless://..." \
  --zoom-style \
  --dns-domain "api.ovo.id" \
  --concurrent 50 \
  --top 20
```

## Tips & Tricks

### 1. Gunakan Server URL Real
⚠️ Untuk testing zero-quota yang akurat, **HARUS pakai `--server-url`** dengan credentials server asli Anda.

```bash
# ✓ BENAR - pakai server real
python main.py --range "..." --server-url "vless://real-uuid@real-server:443?..." --zoom-style

# ✗ SALAH - tanpa server URL (hanya test tool)
python main.py --range "..." --zoom-style
```

### 2. Pilih DNS Domain yang Tepat
Domain yang biasa dipakai untuk zero-quota:
- `api.ovo.id` - OVO Indonesia
- `support.zoom.us` - Zoom
- `teams.microsoft.com` - Microsoft Teams
- `meet.google.com` - Google Meet

### 3. Test Range Kecil Dulu
```bash
# Test 20 IP dulu untuk validasi
python main.py --range "170.114.45.1-20" --server-url "vless://..." --zoom-style --verbose

# Kalau berhasil, baru test range besar
python main.py --range "170.114.45.0/24" --server-url "vless://..." --zoom-style
```

### 4. Save Working IPs
Setelah testing selesai, lihat file `working_ips_*.txt`:
```
170.114.45.6 # 45.23ms
170.114.46.6 # 52.10ms
```

Pakai IP ini di config Xray personal Anda dengan format zoom-style.

## Troubleshooting

### Semua IP Failed
1. Cek koneksi internet
2. Pastikan server URL valid
3. Coba increase `--timeout 15`
4. Ganti `--dns-domain` dengan domain lain

### Config Error
1. Jalankan test script: `python test-zoom-config.py`
2. Compare dengan `xray-zoom-config.json`
3. Validasi server URL parsing

### Permission Denied
```bash
# Linux/Mac
chmod +x test-zoom-config.py
chmod +x xray/xray
```

## Referensi

- [Xray Documentation](https://xtls.github.io/)
- [DNS Hosts Mapping](https://xtls.github.io/config/dns.html)
- [Domain Strategy](https://xtls.github.io/config/routing.html#routingobject)

---

**Note:** Tool ini untuk educational purposes. Pastikan Anda menggunakan sesuai dengan Terms of Service provider Anda.
