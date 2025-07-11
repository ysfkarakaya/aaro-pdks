"""
AARO ERP - PDKS API Yöneticisi
"""

import requests
import json
import logging
from datetime import datetime

class APIManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.token = None
        self.token_expires = None
        self.connection_logs_callback = None
        self.refresh_token = None
        self.auto_refresh_timer = None
        
        # Program başlangıcında otomatik token al
        self.initialize_token()
        
        # Otomatik gönderim zamanlayıcısı
        self.auto_send_timer = None
        self.last_sent_timestamps = {}  # Cihaz başına son gönderilen timestamp'ları takip et
        self.start_auto_send()
    
    def set_connection_logs_callback(self, callback):
        """Bağlantı logları callback'ini ayarla"""
        self.connection_logs_callback = callback
    
    def add_connection_log(self, operation, status, details, log_type="API"):
        """Bağlantı logu ekle"""
        if self.connection_logs_callback:
            self.connection_logs_callback("API Server", operation, status, details, log_type)
    
    def get_api_settings(self):
        """API ayarlarını al"""
        return self.config_manager.get_setting('api_settings', {
            "enabled": False,
            "token_url": "https://erp.aaro.com.tr/Token",
            "data_url": "https://erp.aaro.com.tr/api/attendance",
            "username": "",
            "password": "",
            "auto_send": False,
            "send_interval": 300
        })
    
    def get_token(self):
        """API token'ı al"""
        try:
            api_settings = self.get_api_settings()
            
            if not api_settings.get('enabled', False):
                return None
            
            if not api_settings.get('username') or not api_settings.get('password'):
                self.logger.error("API kullanıcı adı veya şifre boş")
                self.add_connection_log("Token Alma", "Hata", "Kullanıcı adı veya şifre boş")
                return None
            
            # Log ekle
            self.add_connection_log("Token Alma", "Deneniyor", 
                                  f"URL: {api_settings['token_url']}\nKullanıcı: {api_settings['username']}")
            
            # Token isteği
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'Oturum=Grup=935&Sirket=0&Sube=0'
            }
            
            data = {
                'grant_type': 'password',
                'username': api_settings['username'],
                'password': api_settings['password']
            }
            
            response = requests.post(
                api_settings['token_url'],
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                
                # Token süresini hesapla (varsayılan 1 saat)
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires = datetime.now().timestamp() + expires_in
                
                # Otomatik yenileme zamanlayıcısını başlat
                self.schedule_token_refresh(expires_in)
                
                self.logger.info("API token başarıyla alındı")
                
                # Başarı logu - ham veri ile
                token_preview = self.token[:20] + "..." if self.token and len(self.token) > 20 else self.token
                
                # Gönderilen veriyi hazırla
                sent_data = {
                    'grant_type': 'password',
                    'username': api_settings['username'],
                    'password': '***' # Şifreyi gizle
                }
                
                log_details = f"""Token başarıyla alındı
Token: {token_preview}
Süre: {expires_in} saniye

GÖNDERİLEN VERİ:
{json.dumps(sent_data, indent=2, ensure_ascii=False)}

SUNUCU YANITI (HAM VERİ):
{response.text}"""
                
                self.add_connection_log("Token Alma", "Başarılı", log_details)
                
                # Token'ı config'e kaydet
                self.save_token_to_config(token_data, expires_in)
                
                return self.token
            else:
                self.logger.error(f"Token alma hatası: {response.status_code} - {response.text}")
                
                # Hata logu - ham veri ile
                sent_data = {
                    'grant_type': 'password',
                    'username': api_settings['username'],
                    'password': '***' # Şifreyi gizle
                }
                
                log_details = f"""HTTP {response.status_code} hatası

GÖNDERİLEN VERİ:
{json.dumps(sent_data, indent=2, ensure_ascii=False)}

HATA YANITI (HAM VERİ):
{response.text}"""
                
                self.add_connection_log("Token Alma", "Hata", log_details)
                return None
                
        except Exception as e:
            self.logger.error(f"Token alma hatası: {str(e)}")
            self.add_connection_log("Token Alma", "Hata", f"İstek hatası: {str(e)}")
            return None
    
    def is_token_valid(self):
        """Token'ın geçerli olup olmadığını kontrol et"""
        if not self.token or not self.token_expires:
            return False
        
        # Token'ın süresi dolmuş mu kontrol et (5 dakika önceden yenile)
        return datetime.now().timestamp() < (self.token_expires - 300)
    
    def send_attendance_data(self, attendance_data):
        """Giriş-çıkış verilerini API'ye gönder"""
        try:
            api_settings = self.get_api_settings()
            
            if not api_settings.get('enabled', False):
                self.logger.info("API gönderimi devre dışı")
                self.add_connection_log("Veri Gönderimi", "Hata", "API gönderimi devre dışı")
                return {"success": False, "message": "API devre dışı"}
            
            # Log ekle
            self.add_connection_log("Veri Gönderimi", "Deneniyor", 
                                  f"URL: {api_settings['data_url']}\nKayıt sayısı: {len(attendance_data)}")
            
            # Token kontrolü
            if not self.is_token_valid():
                self.logger.info("Token geçersiz, yeni token alınıyor...")
                if not self.get_token():
                    self.add_connection_log("Veri Gönderimi", "Hata", "Token alınamadı")
                    return {"success": False, "message": "Token alınamadı"}
            
            # Veri gönderimi
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            # Gönderilecek veriyi JSON olarak hazırla
            payload_json = json.dumps(attendance_data, indent=2, ensure_ascii=False)
            
            response = requests.post(
                api_settings['data_url'],
                headers=headers,
                json=attendance_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                # API yanıtını kontrol et
                try:
                    response_data = response.json() if response.content else {}
                    
                    # Yanıt formatını kontrol et (liste mi sözlük mü?)
                    if isinstance(response_data, list):
                        # Liste formatında yanıt - herhangi birinin Sonuc=true olması yeterli
                        any_success = False
                        failed_items = []
                        
                        for i, item in enumerate(response_data):
                            if isinstance(item, dict):
                                item_success = item.get('Sonuc', False)
                                if item_success:
                                    any_success = True
                                else:
                                    failed_items.append(f"Öğe {i+1}: {item.get('Detay', 'Bilinmeyen hata')}")
                            else:
                                failed_items.append(f"Öğe {i+1}: Geçersiz format")
                        
                        api_success = any_success
                        
                    elif isinstance(response_data, dict):
                        # Sözlük formatında yanıt - tek öğe kontrol et
                        api_success = response_data.get('Sonuc', False)
                        failed_items = []
                        
                    else:
                        # Beklenmeyen format
                        api_success = False
                        failed_items = ["Beklenmeyen yanıt formatı"]
                    
                    if api_success:
                        self.logger.info(f"API'ye {len(attendance_data)} kayıt başarıyla gönderildi ve işlendi")
                        
                        # Başarı logu
                        response_text = response.text if response.content else "Boş yanıt"
                        log_details = f"""{len(attendance_data)} kayıt başarıyla gönderildi ve işlendi

GÖNDERİLEN VERİ:
{payload_json}

SUNUCU YANITI:
{response_text}"""
                        
                        self.add_connection_log("Veri Gönderimi", "Başarılı", log_details)
                        
                        # Başarılı gönderimde cihaz temizleme kontrolü
                        api_settings = self.get_api_settings()
                        if api_settings.get('clear_device_on_success', False):
                            self.clear_device_attendance_records()
                        
                        return {
                            "success": True, 
                            "message": f"{len(attendance_data)} kayıt gönderildi ve işlendi",
                            "response": response_data
                        }
                    else:
                        # API'den false yanıtı geldi veya hata var
                        error_details = " | ".join(failed_items) if failed_items else "Bilinmeyen hata"
                        self.logger.warning(f"API yanıtı: Sonuc=false - Veriler işlenmedi - {error_details}")
                        
                        # Uyarı logu
                        response_text = response.text if response.content else "Boş yanıt"
                        log_details = f"""Veriler gönderildi ancak işlenmedi (Sonuc=false)

HATA DETAYLARI: {error_details}

GÖNDERİLEN VERİ:
{payload_json}

SUNUCU YANITI:
{response_text}"""
                        
                        self.add_connection_log("Veri Gönderimi", "Uyarı", log_details)
                        
                        return {
                            "success": False, 
                            "message": f"Veriler gönderildi ancak API tarafından işlenmedi: {error_details}",
                            "response": response_data
                        }
                        
                except Exception as e:
                    # JSON parse hatası
                    self.logger.error(f"API yanıt parse hatası: {str(e)}")
                    
                    response_text = response.text if response.content else "Boş yanıt"
                    log_details = f"""Yanıt parse edilemedi

GÖNDERİLEN VERİ:
{payload_json}

SUNUCU YANITI:
{response_text}

PARSE HATASI: {str(e)}"""
                    
                    self.add_connection_log("Veri Gönderimi", "Hata", log_details)
                    
                    return {
                        "success": False, 
                        "message": f"API yanıtı parse edilemedi: {str(e)}"
                    }
            else:
                self.logger.error(f"API gönderim hatası: {response.status_code} - {response.text}")
                
                # Hata logu
                log_details = f"""HTTP {response.status_code} hatası

GÖNDERİLEN VERİ:
{payload_json}

HATA YANITI:
{response.text}"""
                
                self.add_connection_log("Veri Gönderimi", "Hata", log_details)
                
                return {
                    "success": False, 
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            self.logger.error(f"API gönderim hatası: {str(e)}")
            self.add_connection_log("Veri Gönderimi", "Hata", f"İstek hatası: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def _send_attendance_data_internal(self, attendance_data):
        """Otomatik gönderim için internal veri gönderimi - detaylı log ile"""
        try:
            api_settings = self.get_api_settings()
            
            if not api_settings.get('enabled', False):
                return {"success": False, "message": "API devre dışı"}
            
            # Token kontrolü
            if not self.is_token_valid():
                if not self.get_token():
                    return {"success": False, "message": "Token alınamadı"}
            
            # Veri gönderimi
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            # Gönderilecek veriyi JSON olarak hazırla
            payload_json = json.dumps(attendance_data, indent=2, ensure_ascii=False)
            
            response = requests.post(
                api_settings['data_url'],
                headers=headers,
                json=attendance_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json() if response.content else {}
                    
                    # Yanıt formatını kontrol et (liste mi sözlük mü?) - otomatik gönderim için
                    if isinstance(response_data, list):
                        # Liste formatında yanıt - herhangi birinin Sonuc=true olması yeterli
                        any_success = False
                        failed_items = []
                        
                        for i, item in enumerate(response_data):
                            if isinstance(item, dict):
                                item_success = item.get('Sonuc', False)
                                if item_success:
                                    any_success = True
                                else:
                                    failed_items.append(f"Öğe {i+1}: {item.get('Detay', 'Bilinmeyen hata')}")
                            else:
                                failed_items.append(f"Öğe {i+1}: Geçersiz format")
                        
                        api_success = any_success
                        
                    elif isinstance(response_data, dict):
                        # Sözlük formatında yanıt - tek öğe kontrol et
                        api_success = response_data.get('Sonuc', False)
                        failed_items = []
                        
                    else:
                        # Beklenmeyen format
                        api_success = False
                        failed_items = ["Beklenmeyen yanıt formatı"]
                    
                    if api_success:
                        # Başarı logu - otomatik gönderim için
                        response_text = response.text if response.content else "Boş yanıt"
                        log_details = f"""{len(attendance_data)} kayıt otomatik gönderildi ve işlendi

GÖNDERİLEN VERİ:
{payload_json}

SUNUCU YANITI:
{response_text}"""
                        
                        self.add_connection_log("Otomatik Veri Gönderimi", "Başarılı", log_details)
                        
                        # Başarılı gönderimde cihaz temizleme kontrolü
                        if api_settings.get('clear_device_on_success', False):
                            self.clear_device_attendance_records()
                        
                        return {
                            "success": True, 
                            "message": f"{len(attendance_data)} kayıt gönderildi ve işlendi",
                            "response": response_data
                        }
                    else:
                        # API'den false yanıtı geldi veya hata var - otomatik gönderim için
                        error_details = " | ".join(failed_items) if failed_items else "Bilinmeyen hata"
                        
                        # Uyarı logu - otomatik gönderim için
                        response_text = response.text if response.content else "Boş yanıt"
                        log_details = f"""Otomatik gönderim: Veriler gönderildi ancak işlenmedi (Sonuc=false)

HATA DETAYLARI: {error_details}

GÖNDERİLEN VERİ:
{payload_json}

SUNUCU YANITI:
{response_text}"""
                        
                        self.add_connection_log("Otomatik Veri Gönderimi", "Uyarı", log_details)
                        
                        return {
                            "success": False, 
                            "message": f"Veriler gönderildi ancak API tarafından işlenmedi: {error_details}",
                            "response": response_data
                        }
                        
                except Exception as e:
                    # Hata logu - otomatik gönderim için
                    response_text = response.text if response.content else "Boş yanıt"
                    log_details = f"""Otomatik gönderim: Yanıt parse edilemedi

GÖNDERİLEN VERİ:
{payload_json}

SUNUCU YANITI:
{response_text}

PARSE HATASI: {str(e)}"""
                    
                    self.add_connection_log("Otomatik Veri Gönderimi", "Hata", log_details)
                    
                    return {
                        "success": False, 
                        "message": f"API yanıtı parse edilemedi: {str(e)}"
                    }
            else:
                # Hata logu - otomatik gönderim için
                log_details = f"""Otomatik gönderim: HTTP {response.status_code} hatası

GÖNDERİLEN VERİ:
{payload_json}

HATA YANITI:
{response.text}"""
                
                self.add_connection_log("Otomatik Veri Gönderimi", "Hata", log_details)
                
                return {
                    "success": False, 
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def start_auto_send(self):
        """Otomatik veri gönderimini başlat"""
        try:
            api_settings = self.get_api_settings()
            
            if api_settings.get('enabled', False) and api_settings.get('auto_send', False):
                send_interval = api_settings.get('send_interval', 300)
                
                self.logger.info(f"Otomatik veri gönderimi başlatıldı - {send_interval} saniye aralıkla")
                self.add_connection_log("Otomatik Gönderim", "Başlatıldı", 
                                      f"Otomatik veri gönderimi {send_interval} saniye aralıkla başlatıldı")
                
                # İlk gönderimi gecikmeli yap (token hazır olana kadar bekle)
                import threading
                threading.Timer(30.0, self.auto_send_data).start()
                
                # Periyodik gönderimi başlat
                self.schedule_auto_send(send_interval)
            
        except Exception as e:
            self.logger.error(f"Otomatik gönderim başlatma hatası: {str(e)}")
    
    def schedule_auto_send(self, interval):
        """Otomatik gönderim zamanlayıcısını ayarla"""
        try:
            import threading
            
            # Mevcut zamanlayıcıyı iptal et
            if self.auto_send_timer:
                self.auto_send_timer.cancel()
            
            # Yeni zamanlayıcıyı başlat
            self.auto_send_timer = threading.Timer(interval, self.auto_send_data)
            self.auto_send_timer.daemon = True
            self.auto_send_timer.start()
            
        except Exception as e:
            self.logger.error(f"Otomatik gönderim zamanlayıcısı hatası: {str(e)}")
    
    def auto_send_data(self):
        """Otomatik veri gönderimi"""
        try:
            api_settings = self.get_api_settings()
            
            # Ayarlar kontrol et
            if not api_settings.get('enabled', False) or not api_settings.get('auto_send', False):
                self.logger.info("Otomatik gönderim devre dışı")
                return
            
            self.logger.info("Otomatik veri gönderimi başlıyor...")
            self.add_connection_log("Otomatik Gönderim", "Deneniyor", 
                                  "Cihazlardan yeni veriler toplanıyor")
            
            # Ana pencereye erişim için callback kullan
            if hasattr(self, 'main_window_ref') and self.main_window_ref:
                main_window = self.main_window_ref()
                if main_window:
                    # Cihazlardan attendance verilerini al
                    attendance_data = self.collect_attendance_data(main_window)
                    
                    if attendance_data:
                        # Veriyi API'ye gönder (otomatik gönderim için özel fonksiyon)
                        result = self._send_attendance_data_internal(attendance_data)
                        
                        if result['success']:
                            self.add_connection_log("Otomatik Gönderim", "Başarılı", 
                                                  f"{len(attendance_data)} kayıt otomatik gönderildi")
                        else:
                            self.add_connection_log("Otomatik Gönderim", "Hata", 
                                                  f"Otomatik gönderim hatası: {result['message']}")
                    else:
                        self.add_connection_log("Otomatik Gönderim", "Bilgi", 
                                              "Gönderilecek yeni veri bulunamadı")
            
            # Bir sonraki gönderim için zamanlayıcıyı ayarla
            send_interval = api_settings.get('send_interval', 300)
            self.schedule_auto_send(send_interval)
            
        except Exception as e:
            self.logger.error(f"Otomatik veri gönderim hatası: {str(e)}")
            self.add_connection_log("Otomatik Gönderim", "Hata", 
                                  f"Otomatik gönderim hatası: {str(e)}")
            
            # Hata durumunda da zamanlayıcıyı devam ettir
            api_settings = self.get_api_settings()
            send_interval = api_settings.get('send_interval', 300)
            self.schedule_auto_send(send_interval)
    
    def collect_attendance_data(self, main_window):
        """Cihazlardan tüm attendance verilerini topla (filtreleme yok)"""
        try:
            # Tüm cihazlardan formatlanmış attendance verilerini al (timestamp bilgisi ile birlikte)
            all_formatted_attendance = main_window.device_manager.get_formatted_attendance()
            
            if not all_formatted_attendance:
                return []
            
            # Tüm verileri gönder (filtreleme yok)
            clean_formatted_data = []
            
            for formatted_att in all_formatted_attendance:
                # Ek bilgileri temizle (API'ye gönderilmemesi için)
                clean_formatted_att = {k: v for k, v in formatted_att.items() if not k.startswith('_')}
                clean_formatted_data.append(clean_formatted_att)
            
            return clean_formatted_data
            
        except Exception as e:
            self.logger.error(f"Veri toplama hatası: {str(e)}")
            return []
    
    def stop_auto_send(self):
        """Otomatik gönderimi durdur"""
        if self.auto_send_timer:
            self.auto_send_timer.cancel()
            self.auto_send_timer = None
            self.logger.info("Otomatik veri gönderimi durduruldu")
            self.add_connection_log("Otomatik Gönderim", "Durduruldu", 
                                  "Otomatik veri gönderimi durduruldu")
    
    def set_main_window_ref(self, main_window_ref):
        """Ana pencere referansını ayarla (weak reference)"""
        import weakref
        self.main_window_ref = weakref.ref(main_window_ref)
    
    def save_token_to_config(self, token_data, expires_in):
        """Token'ı config dosyasına kaydet"""
        try:
            expires_at = datetime.now().timestamp() + expires_in
            expires_at_str = datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d %H:%M:%S")
            
            token_config = {
                "access_token": token_data.get('access_token', ''),
                "refresh_token": token_data.get('refresh_token', ''),
                "expires_at": expires_at_str,
                "token_type": token_data.get('token_type', 'bearer')
            }
            
            # API ayarlarını güncelle
            api_settings = self.get_api_settings()
            api_settings['token_data'] = token_config
            
            self.config_manager.update_settings({'api_settings': api_settings})
            
            self.logger.info("Token config'e kaydedildi")
            
        except Exception as e:
            self.logger.error(f"Token kaydetme hatası: {str(e)}")
    
    def load_saved_token(self):
        """Kaydedilmiş token'ı yükle"""
        try:
            api_settings = self.get_api_settings()
            token_data = api_settings.get('token_data', {})
            
            if not token_data.get('access_token'):
                return False
            
            # Token süresini kontrol et
            expires_at_str = token_data.get('expires_at', '')
            if not expires_at_str:
                return False
            
            expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S").timestamp()
            now = datetime.now().timestamp()
            
            # Token süresi dolmuş mu?
            if now >= expires_at:
                self.logger.info("Kaydedilmiş token süresi dolmuş")
                return False
            
            # Token'ı yükle
            self.token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.token_expires = expires_at
            
            # Kalan süreyi hesapla
            expires_in = expires_at - now
            
            # Otomatik yenileme zamanlayıcısını başlat
            self.schedule_token_refresh(expires_in)
            
            self.logger.info(f"Kaydedilmiş token yüklendi, {expires_in:.0f} saniye geçerli")
            
            # Log ekle
            self.add_connection_log("Token Yükleme", "Başarılı", 
                                  f"Kaydedilmiş token yüklendi\nGeçerlilik: {expires_at_str}\nKalan süre: {expires_in:.0f} saniye")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Token yükleme hatası: {str(e)}")
            return False
    
    def clear_saved_token(self):
        """Kaydedilmiş token'ı temizle"""
        try:
            api_settings = self.get_api_settings()
            api_settings['token_data'] = {
                "access_token": "",
                "refresh_token": "",
                "expires_at": "",
                "token_type": "bearer"
            }
            
            self.config_manager.update_settings({'api_settings': api_settings})
            
            self.token = None
            self.refresh_token = None
            self.token_expires = None
            
            self.logger.info("Kaydedilmiş token temizlendi")
            
        except Exception as e:
            self.logger.error(f"Token temizleme hatası: {str(e)}")
    
    def initialize_token(self):
        """Program başlangıcında token'ı başlat"""
        try:
            api_settings = self.get_api_settings()
            
            if api_settings.get('enabled', False):
                self.logger.info("API etkin, kaydedilmiş token kontrol ediliyor...")
                
                # Önce kaydedilmiş token'ı kontrol et
                if self.load_saved_token():
                    self.logger.info("Kaydedilmiş geçerli token bulundu")
                else:
                    self.logger.info("Geçerli token yok, yeni token alınıyor...")
                    # Callback henüz ayarlanmamış olabilir, bu yüzden gecikmeli çalışma
                    import threading
                    threading.Timer(2.0, self.delayed_token_fetch).start()
            
        except Exception as e:
            self.logger.error(f"Token başlatma hatası: {str(e)}")
    
    def delayed_token_fetch(self):
        """Gecikmeli token alma - SADECE token alır, veri göndermez"""
        try:
            self.get_token()
        except Exception as e:
            self.logger.error(f"Gecikmeli token alma hatası: {str(e)}")
    
    def schedule_token_refresh(self, expires_in):
        """Token yenileme zamanlayıcısını ayarla"""
        try:
            import threading
            
            # Mevcut zamanlayıcıyı iptal et
            if self.auto_refresh_timer:
                self.auto_refresh_timer.cancel()
            
            # Token süresinin %80'i geçtiğinde yenile (örn: 12 saat token için 9.6 saat sonra)
            refresh_delay = expires_in * 0.8
            
            self.logger.info(f"Token otomatik yenileme {refresh_delay:.0f} saniye sonra ayarlandı")
            
            # Zamanlayıcıyı başlat
            self.auto_refresh_timer = threading.Timer(refresh_delay, self.auto_refresh_token)
            self.auto_refresh_timer.daemon = True
            self.auto_refresh_timer.start()
            
        except Exception as e:
            self.logger.error(f"Token yenileme zamanlayıcısı hatası: {str(e)}")
    
    def auto_refresh_token(self):
        """Otomatik token yenileme"""
        try:
            self.logger.info("Token otomatik yenileniyor...")
            self.add_connection_log("Otomatik Token Yenileme", "Deneniyor", 
                                  "Token süresi dolmak üzere, otomatik yenileniyor")
            
            # Yeni token al
            if self.get_token():
                self.add_connection_log("Otomatik Token Yenileme", "Başarılı", 
                                      "Token başarıyla otomatik yenilendi")
            else:
                self.add_connection_log("Otomatik Token Yenileme", "Hata", 
                                      "Token otomatik yenilenemedi")
                
        except Exception as e:
            self.logger.error(f"Otomatik token yenileme hatası: {str(e)}")
            self.add_connection_log("Otomatik Token Yenileme", "Hata", 
                                  f"Otomatik yenileme hatası: {str(e)}")
    
    def stop_auto_refresh(self):
        """Otomatik yenilemeyi durdur"""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.cancel()
            self.auto_refresh_timer = None
            self.logger.info("Token otomatik yenileme durduruldu")
    
    def get_token_status(self):
        """Token durumunu al"""
        if not self.token:
            return {"status": "Yok", "expires_in": 0, "valid": False}
        
        if not self.token_expires:
            return {"status": "Bilinmeyen", "expires_in": 0, "valid": False}
        
        now = datetime.now().timestamp()
        expires_in = self.token_expires - now
        
        if expires_in <= 0:
            return {"status": "Süresi Dolmuş", "expires_in": 0, "valid": False}
        elif expires_in <= 300:  # 5 dakika
            return {"status": "Yakında Dolacak", "expires_in": expires_in, "valid": True}
        else:
            return {"status": "Geçerli", "expires_in": expires_in, "valid": True}
    
    def test_api_connection(self):
        """API bağlantısını test et"""
        try:
            api_settings = self.get_api_settings()
            
            if not api_settings.get('enabled', False):
                return {"success": False, "message": "API devre dışı"}
            
            # Token alma testi
            token = self.get_token()
            if token:
                return {"success": True, "message": "API bağlantısı başarılı, token alındı"}
            else:
                return {"success": False, "message": "Token alınamadı"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def send_test_data(self):
        """Test verisi gönder"""
        try:
            test_data = [{
                "CihazID": "Test Cihazı",
                "CihazLogID": "999999",
                "CihazPersonelID": "TEST001",
                "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            
            result = self.send_attendance_data(test_data)
            return result
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def clear_device_attendance_records(self):
        """Başarılı gönderimden sonra cihazlardan attendance kayıtlarını temizle"""
        try:
            if not hasattr(self, 'main_window_ref') or not self.main_window_ref:
                return
            
            main_window = self.main_window_ref()
            if not main_window:
                return
            
            self.logger.info("Başarılı gönderim sonrası cihaz kayıtları temizleniyor...")
            self.add_connection_log("Cihaz Temizleme", "Deneniyor", 
                                  "Başarılı gönderim sonrası cihazlardan kayıtlar temizleniyor")
            
            cleared_devices = []
            error_devices = []
            
            # Tüm bağlı cihazları temizle
            connected_devices = main_window.device_manager.get_connected_devices()
            
            for device_id, device_info in connected_devices.items():
                device = device_info['device']
                
                try:
                    # Cihaz bağlantısını al
                    device_conn = main_window.device_manager.get_device_connection(device_id)
                    
                    if device_conn:
                        # Attendance kayıtlarını temizle
                        device_conn.clear_attendance()
                        cleared_devices.append(device['name'])
                        
                        # Cihaz logu
                        main_window.device_manager.add_connection_log(
                            device['name'], 
                            "Kayıt Temizleme", 
                            "Başarılı", 
                            "Başarılı API gönderimi sonrası attendance kayıtları temizlendi",
                            "Veri Yönetimi"
                        )
                        
                    else:
                        error_devices.append(f"{device['name']} (bağlantı yok)")
                        
                except Exception as e:
                    error_devices.append(f"{device['name']} ({str(e)})")
                    
                    # Hata logu
                    main_window.device_manager.add_connection_log(
                        device['name'], 
                        "Kayıt Temizleme", 
                        "Hata", 
                        f"Kayıt temizleme hatası: {str(e)}",
                        "Veri Yönetimi"
                    )
            
            # Sonuç logu
            if cleared_devices:
                success_msg = f"Temizlenen cihazlar: {', '.join(cleared_devices)}"
                if error_devices:
                    success_msg += f"\nHata olan cihazlar: {', '.join(error_devices)}"
                
                self.add_connection_log("Cihaz Temizleme", "Başarılı", success_msg)
                self.logger.info(f"Cihaz temizleme tamamlandı - Başarılı: {len(cleared_devices)}, Hata: {len(error_devices)}")
            else:
                self.add_connection_log("Cihaz Temizleme", "Uyarı", 
                                      "Hiç cihaz temizlenemedi" + (f" - Hatalar: {', '.join(error_devices)}" if error_devices else ""))
                
        except Exception as e:
            self.logger.error(f"Cihaz temizleme hatası: {str(e)}")
            self.add_connection_log("Cihaz Temizleme", "Hata", 
                                  f"Cihaz temizleme hatası: {str(e)}")
