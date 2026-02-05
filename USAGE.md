# Example Usage - Cloudflare IP Tester with Real vless Server

## Using Your vless Server URL

```bash
python main.py \
  --server-url "vless://4b70b98a-1b39-4d76-880a-243ba5c5e03b@point.natss.store:443?path=/vless&security=tls&encryption=none&host=point.natss.store&type=ws&sni=point.natss.store#yamete09" \
  --range "104.16.0.1-100" \
  --timeout 8 \
  --concurrent 20
```

## What This Does

Tool akan:
1. Parse vless URL Anda (UUID, server, SNI, path, dll)
2. Generate config Xray untuk setiap IP Cloudflare 
3. Test koneksi ke server vless Anda **melalui** IP Cloudflare yang berbeda
4. Report IP Cloudflare mana yang BERHASIL connect ke server


## Step by Step

### 1. Test Range Kecil Dulu
```bash
python main.py \
  --server-url "vless://YOUR-VLESS-URL" \
  --range "104.16.0.1-20" \
  --timeout 8 \
  --verbose
```

### 2. Jika Ada yang Berhasil, Test Range Lebih Besar
```bash
python main.py \
  --server-url "vless://YOUR-VLESS-URL" \
  --range "104.16.0.0/24" \
  --concurrent 30 \
  --timeout 10
```

### 3. Gunakan Working IPs
Setelah selesai, check file `results/working_ips_TIMESTAMP.txt`:
```
104.16.0.15 # 45.23ms
104.16.0.32 # 52.10ms
```

Pakai IP ini untuk config Xray Anda!

## Tips

### Increase Timeout
Jika koneksi lambat, increase timeout:
```bash
--timeout 10
```

### More Concurrent Tests
Untuk lebih cepat:
```bash
--concurrent 50
```

### Test Specific Range
Jika sudah tau range yang sering work:
```bash
--range "104.16.0.0/16"  # Lebih dari 65k IPs!
```

### Save Results with Custom Name
```bash
--output my-test-results.json
```

## Understanding Results

### Success
```
✓ 104.16.0.15 - 45ms
```
IP ini BISA connect ke server vless Anda!

### Failed
```
✗ 104.16.0.20 - Timeout
✗ 104.16.0.21 - Connection failed
```
IP ini tidak bisa connect.

## After Testing

1. Open `results/working_ips_TIMESTAMP.txt`
2. Copy IP tercepat
3. Update Xray config Anda dengan IP tersebut

Example config update:
```json
{
  "outbounds": [{
    "protocol": "vless",
    "settings": {
      "vnext": [{
        "address": "104.16.0.15",  // <-- GANTI dengan working IP
        "port": 443,
        "users": [{"id": "YOUR-UUID"}]
      }]
    }
  }]
}
```

## Important Notes

- Tool akan test REAL connection ke server Anda
- Perlu internet connection yang bekerja
- IP yang berhasil bisa berubah tergantung operator/waktu
- Test berkala untuk find IP terbaru yang work
