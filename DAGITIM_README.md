# AARO ERP - PDKS v2.0 Dağıtım Kılavuzu

## 📦 EXE Dosyası Oluşturma

### Gereksinimler:
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Windows işletim sistemi

### Adımlar:

1. **Komut satırını yönetici olarak açın**
2. **Proje klasörüne gidin:**
   ```cmd
   cd c:\laragon-local\www\pdksv4
   ```

3. **EXE oluşturma script'ini çalıştırın:**
   ```cmd
   build_exe.bat
   ```

4. **İşlem tamamlandığında:**
   - `dist\AARO_ERP_PDKS.exe` dosyası oluşacak
   - Bu dosya Python kurulu olmayan bilgisayarlarda çalışır

## 🚀 Dağıtım

### Tek Dosya Dağıtımı:
- `dist\AARO_ERP_PDKS.exe` dosyasını kopyalayın
- Hedef bilgisayara yapıştırın
- Çift tıklayarak çalıştırın

### Tam Kurulum Dağıtımı:
Aşağıdaki dosyaları birlikte dağıtın:
```
AARO_ERP_PDKS.exe    # Ana program
config.json          # Varsayılan ayarlar
logo.png             # Program logosu
README.md            # Kullanım kılavuzu
```

## ⚙️ İlk Kurulum

### 1. Program Çalıştırma:
- `AARO_ERP_PDKS.exe` dosyasını çift tıklayın
- Windows Defender uyarısı çıkarsa "Daha fazla bilgi" > "Yine de çalıştır"

### 2. Cihaz Ekleme:
- Menü: Cihaz > Cihaz Ekle
- IP adresi, port ve cihaz adını girin
- "Kaydet" butonuna tıklayın

### 3. API Ayarları:
- Menü: Araçlar > Ayarlar > API sekmesi
- AARO ERP bilgilerinizi girin
- "Kaydet" butonuna tıklayın

## 🔧 Sorun Giderme

### Program Açılmıyor:
1. **Antivirus kontrolü:** Antivirus yazılımı engelliyor olabilir
2. **Windows Defender:** Dosyayı güvenli listesine ekleyin
3. **Yönetici yetkisi:** Sağ tık > "Yönetici olarak çalıştır"

### Cihaza Bağlanamıyor:
1. **Ağ bağlantısı:** Ping testi yapın
2. **Firewall:** Windows Firewall'da port 4370'i açın
3. **Cihaz ayarları:** Cihazın IP ve port ayarlarını kontrol edin

### API Hatası:
1. **İnternet bağlantısı:** AARO sunucularına erişim var mı?
2. **Kullanıcı bilgileri:** Kullanıcı adı ve şifre doğru mu?
3. **Token süresi:** Token'ın süresi dolmuş olabilir

## 📋 Sistem Gereksinimleri

### Minimum:
- **İşletim Sistemi:** Windows 7 SP1 (64-bit)
- **RAM:** 2 GB
- **Disk Alanı:** 100 MB
- **Ağ:** İnternet bağlantısı (API için)

### Önerilen:
- **İşletim Sistemi:** Windows 10/11 (64-bit)
- **RAM:** 4 GB
- **Disk Alanı:** 500 MB
- **Ağ:** Gigabit Ethernet

## 🏢 Teknik Destek

### AARO ERP Yazılım A.Ş.
- **Web:** https://aaro.com.tr
- **E-posta:** destek@aaro.com.tr
- **Telefon:** +90 XXX XXX XX XX

### Yazılım Bilgileri:
- **Versiyon:** 2.0.0.0
- **Geliştirici:** AARO ERP Yazılım A.Ş.
- **Lisans:** Ticari Yazılım
- **Telif Hakkı:** © 2025 AARO ERP Yazılım A.Ş.

## 📄 Lisans

Bu yazılım AARO ERP Yazılım A.Ş. tarafından geliştirilmiştir.
Tüm hakları saklıdır. İzinsiz kopyalama, dağıtım veya değiştirme yasaktır.

---

**Not:** Bu yazılım ZKTeco PDKS cihazları ile çalışmak üzere tasarlanmıştır.
Diğer marka cihazlarla uyumluluk garanti edilmez.
