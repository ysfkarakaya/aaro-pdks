# AARO ERP - PDKS

ZKTeco firmasının PDKS (Personel Devam Kontrol Sistemi) cihazları için geliştirilmiş Python tabanlı yönetim programı.

## Özellikler

### 🔧 Cihaz Yönetimi
- ✅ Birden fazla ZKTeco PDKS cihazı yönetimi
- ✅ Cihaz ekleme, düzenleme ve silme
- ✅ **Otomatik ağ taraması ile ZKTeco cihazlarını tespit etme**
- ✅ **Sağ tık menüsü ile gelişmiş cihaz yönetimi**
- ✅ Otomatik cihaz bağlantısı ve veri yükleme
- ✅ **Bağlantı testi ve cihaz bilgilerini görüntüleme**

### 📊 Veri Yönetimi
- ✅ Kullanıcı listesi görüntüleme
- ✅ Giriş-çıkış kayıtlarını görüntüleme
- ✅ Hangi kullanıcının hangi cihazdan çekildiğini gösterme
- ✅ **Excel/CSV formatında veri export**
- ✅ **Gelişmiş veri filtreleme ve arama**

### 🎨 Kullanıcı Arayüzü
- ✅ **Modern emoji destekli GUI arayüzü**
- ✅ **Kapsamlı menü çubuğu sistemi**
- ✅ **Animasyonlu loading dialog'ları**
- ✅ **Detaylı progress göstergeleri**
- ✅ **Sağ tık context menüleri**

### ⚙️ Sistem Özellikleri
- ✅ JSON tabanlı konfigürasyon sistemi
- ✅ **Gelişmiş ayarlar paneli**
- ✅ Multi-threading desteği
- ✅ **Detaylı loglama ve log görüntüleyici**
- ✅ **Otomatik hata yönetimi**
- ✅ **Kısayol tuşları desteği**

## Kurulum

### 1. Gereksinimler

- Python 3.7 veya üzeri
- Windows/Linux/macOS

### 2. Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

### 3. Programı Çalıştırma

```bash
python main.py
```

## Kullanım

### Cihaz Ekleme

1. "Cihaz Ekle" butonuna tıklayın
2. Cihaz bilgilerini girin:
   - **Cihaz Adı**: Cihazınıza vermek istediğiniz isim
   - **IP Adresi**: Cihazın ağ IP adresi
   - **Port**: Genellikle 4370 (varsayılan)
   - **Protokol**: TCP veya UDP
   - **Timeout**: Bağlantı zaman aşımı (saniye)
   - **Şifre**: Cihaz şifresi (genellikle 0)
3. "Kaydet" butonuna tıklayın

### Cihazlara Bağlanma

- Program açıldığında otomatik olarak tüm kayıtlı cihazlara bağlanır
- Manuel bağlantı için "Tüm Cihazlara Bağlan" butonunu kullanın

### Verileri Görüntüleme

1. **Kullanıcılar Sekmesi**: Tüm cihazlardan çekilen kullanıcı listesi
2. **Giriş-Çıkış Kayıtları Sekmesi**: Attendance kayıtları

### Ağ Taraması ile Otomatik Cihaz Tespiti

1. "Ağ Taraması" butonuna tıklayın
2. Program yerel ağınızı tarayarak ZKTeco cihazlarını otomatik olarak bulur
3. Bulunan cihazlar listesinde:
   - **Seçili Cihazı Ekle**: Listeden seçtiğiniz cihazı ekler
   - **Tümünü Ekle**: Bulunan tüm cihazları otomatik olarak ekler
4. Cihazlar otomatik olarak konfigürasyona eklenir

### Sağ Tık Menüsü ile Cihaz Yönetimi

Cihaz listesinde herhangi bir cihaza sağ tıklayarak:
- **Düzenle**: Cihaz bilgilerini düzenleyin
- **Sil**: Cihazı listeden kaldırın
- **Bağlantıyı Test Et**: Cihaza ping ve ZKTeco bağlantısı test edin
- **Cihaz Bilgilerini Göster**: Detaylı cihaz bilgilerini görüntüleyin

### Verileri Yenileme

"Verileri Yenile" butonuna tıklayarak tüm bağlı cihazlardan güncel verileri çekin.

## Konfigürasyon

Program `config.json` dosyasını kullanarak cihaz bilgilerini saklar:

```json
{
    "devices": [
        {
            "id": 1,
            "name": "Ana Giriş PDKS",
            "ip": "192.168.1.100",
            "port": 4370,
            "protocol": "TCP",
            "timeout": 30,
            "password": 0,
            "force_udp": false
        }
    ],
    "settings": {
        "auto_connect": true,
        "refresh_interval": 60,
        "log_level": "INFO"
    }
}
```

## Desteklenen Cihazlar

Bu program ZKTeco firmasının TCP/IP protokolünü destekleyen tüm PDKS cihazlarıyla uyumludur:

- ZKTeco K40
- ZKTeco K50
- ZKTeco F18
- ZKTeco F19
- ZKTeco MA300
- ZKTeco MA500
- Ve diğer TCP/IP destekli modeller

## Durum Kodları

### Kullanıcı Yetkileri
- **0**: Kullanıcı
- **14**: Yönetici

### Giriş-Çıkış Durumları
- **0**: Giriş
- **1**: Çıkış
- **2**: Mola Başı
- **3**: Mola Sonu
- **4**: Mesai Başı
- **5**: Mesai Sonu

## Sorun Giderme

### Cihaza Bağlanamıyorum
1. IP adresinin doğru olduğundan emin olun
2. Cihazın ağda erişilebilir olduğunu kontrol edin
3. Port numarasının doğru olduğunu kontrol edin (genellikle 4370)
4. Firewall ayarlarını kontrol edin

### Veriler Gelmiyor
1. Cihazın bağlı olduğundan emin olun (yeşil durum)
2. "Verileri Yenile" butonuna tıklayın
3. Cihaz şifresinin doğru olduğunu kontrol edin

### Program Donuyor
- Program multi-threading kullanır, ağ işlemleri arka planda çalışır
- Bağlantı sorunları durumunda timeout süresi kadar bekleyin

## Teknik Detaylar

- **GUI Framework**: Tkinter
- **ZKTeco Kütüphanesi**: pyzk
- **Konfigürasyon**: JSON
- **Loglama**: Python logging modülü
- **Threading**: Ağ işlemleri için ayrı thread'ler

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Destek

Herhangi bir sorun yaşarsanız veya öneriniz varsa lütfen iletişime geçin.

---

**AARO ERP - PDKS v1.0**  
ZKTeco PDKS Cihaz Yönetim Sistemi
