"""
AARO ERP - PDKS Cihaz Yöneticisi
"""

import socket
import ipaddress
import subprocess
import platform
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from zk import ZK, const
import logging

class DeviceManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.connected_devices = {}
        self.logger = logging.getLogger(__name__)
        self.connection_logs_callback = None
    
    def set_connection_logs_callback(self, callback):
        """Bağlantı logları callback'ini ayarla"""
        self.connection_logs_callback = callback
    
    def add_connection_log(self, device_name, operation, status, details, log_type="Genel"):
        """Bağlantı logu ekle"""
        if self.connection_logs_callback:
            self.connection_logs_callback(device_name, operation, status, details, log_type)
    
    def connect_to_device(self, device):
        """Tek bir cihaza bağlan"""
        try:
            self.add_connection_log(device['name'], "Bağlantı Kurma", "Deneniyor", 
                                  f"IP: {device['ip']}, Port: {device.get('port', 4370)}", "Bağlantı")
            
            zk = ZK(
                device['ip'], 
                port=device.get('port', 4370), 
                timeout=device.get('timeout', 30),
                password=device.get('password', 0), 
                force_udp=device.get('force_udp', False)
            )
            conn = zk.connect()
            
            if conn:
                self.connected_devices[device['id']] = {
                    'device': device,
                    'connection': conn,
                    'zk': zk
                }
                self.logger.info(f"Cihaza bağlandı: {device['name']} ({device['ip']})")
                self.add_connection_log(device['name'], "Bağlantı Kurma", "Başarılı", 
                                      f"Cihaza başarıyla bağlanıldı", "Bağlantı")
                return True
            else:
                self.logger.error(f"Cihaza bağlanılamadı: {device['name']} ({device['ip']})")
                self.add_connection_log(device['name'], "Bağlantı Kurma", "Hata", 
                                      f"Bağlantı kurulamadı", "Bağlantı")
                return False
                
        except Exception as e:
            self.logger.error(f"Bağlantı hatası {device['name']}: {str(e)}")
            self.add_connection_log(device['name'], "Bağlantı Kurma", "Hata", 
                                  f"Bağlantı hatası: {str(e)}", "Bağlantı")
            return False
    
    def disconnect_device(self, device_id):
        """Cihaz bağlantısını kes"""
        if device_id in self.connected_devices:
            try:
                self.connected_devices[device_id]['connection'].disconnect()
                del self.connected_devices[device_id]
                self.logger.info(f"Cihaz bağlantısı kesildi: {device_id}")
                return True
            except Exception as e:
                self.logger.error(f"Bağlantı kesme hatası {device_id}: {str(e)}")
                return False
        return False
    
    def disconnect_all(self):
        """Tüm cihaz bağlantılarını kes"""
        for device_id in list(self.connected_devices.keys()):
            self.disconnect_device(device_id)
    
    def connect_all_devices(self, progress_callback=None):
        """Tüm cihazlara bağlan"""
        devices = self.config_manager.get_devices()
        connected_count = 0
        
        for i, device in enumerate(devices, 1):
            if progress_callback:
                progress_callback(f"Bağlanılıyor: {device['name']} ({i}/{len(devices)})")
            
            if self.connect_to_device(device):
                connected_count += 1
                if progress_callback:
                    progress_callback(f"✓ Bağlandı: {device['name']}")
            else:
                if progress_callback:
                    progress_callback(f"✗ Bağlanamadı: {device['name']}")
            
            time.sleep(0.3)  # Kısa bekleme
        
        return connected_count
    
    def get_connected_devices(self):
        """Bağlı cihazları al"""
        return self.connected_devices
    
    def get_device_connection(self, device_id):
        """Cihaz bağlantısını al"""
        if device_id in self.connected_devices:
            return self.connected_devices[device_id]['connection']
        return None
    
    def is_device_connected(self, device_id):
        """Cihazın bağlı olup olmadığını kontrol et"""
        return device_id in self.connected_devices
    
    def test_device_connection(self, device):
        """Cihaz bağlantısını test et"""
        try:
            # Ping testi
            param = "-n" if platform.system().lower() == "windows" else "-c"
            result = subprocess.run(
                ["ping", param, "1", device['ip']], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # ZKTeco bağlantı testi
                try:
                    zk = ZK(device['ip'], port=device.get('port', 4370), timeout=5)
                    conn = zk.connect()
                    if conn:
                        conn.disconnect()
                        return {"success": True, "message": "Bağlantı başarılı"}
                    else:
                        return {"success": False, "message": "Ping OK, ZKTeco bağlantısı başarısız"}
                except Exception as e:
                    return {"success": False, "message": f"ZKTeco hatası: {str(e)}"}
            else:
                return {"success": False, "message": "Ping başarısız"}
                
        except Exception as e:
            return {"success": False, "message": f"Test hatası: {str(e)}"}
    
    def scan_network_for_devices(self, progress_callback=None):
        """Ağda ZKTeco cihazlarını tara"""
        try:
            # Yerel IP adresini al
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Ağ aralığını belirle
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            total_ips = len(list(network.hosts()))
            
            if progress_callback:
                progress_callback(f"Ağ aralığı: {network} ({total_ips} IP)")
            
            found_devices = []
            scanned_count = 0
            
            # Paralel tarama
            max_workers = self.config_manager.get_setting('scan_threads', 50)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self._scan_ip, str(ip)): str(ip) for ip in network.hosts()}
                
                for future in as_completed(futures):
                    ip = futures[future]
                    scanned_count += 1
                    
                    # Progress güncelle
                    progress_percent = int((scanned_count / total_ips) * 100)
                    if progress_callback:
                        progress_callback(f"Taranıyor... {scanned_count}/{total_ips} (%{progress_percent})")
                    
                    try:
                        result = future.result()
                        if result:
                            found_devices.append(result)
                            self.logger.info(f"ZKTeco cihazı bulundu: {ip}")
                    except Exception as e:
                        pass
            
            return found_devices
            
        except Exception as e:
            self.logger.error(f"Ağ taraması hatası: {str(e)}")
            return []
    
    def _scan_ip(self, ip):
        """Tek IP adresini tara"""
        try:
            # Ping yerine socket ile hızlı port kontrolü
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 4370))
            sock.close()
            
            if result == 0:
                # ZKTeco bağlantı testi
                try:
                    zk = ZK(ip, port=4370, timeout=3)
                    conn = zk.connect()
                    if conn:
                        # Cihaz bilgilerini al
                        device_info = {
                            'ip': ip,
                            'port': 4370,
                            'name': f"ZKTeco Cihazı ({ip})",
                            'protocol': 'TCP',
                            'timeout': 30,
                            'password': 0,
                            'force_udp': False
                        }
                        
                        try:
                            # Cihaz adını almaya çalış
                            device_name = conn.get_device_name()
                            if device_name:
                                device_info['name'] = f"{device_name} ({ip})"
                        except:
                            pass
                        
                        conn.disconnect()
                        return device_info
                except:
                    pass
            return None
        except:
            return None
    
    def get_device_users(self, device_id):
        """Cihazdan kullanıcıları al"""
        if device_id not in self.connected_devices:
            return []
        
        try:
            conn = self.connected_devices[device_id]['connection']
            users = conn.get_users()
            return users
        except Exception as e:
            self.logger.error(f"Kullanıcı alma hatası {device_id}: {str(e)}")
            return []
    
    def get_device_attendance(self, device_id):
        """Cihazdan giriş-çıkış kayıtlarını al"""
        if device_id not in self.connected_devices:
            return []
        
        try:
            conn = self.connected_devices[device_id]['connection']
            attendances = conn.get_attendance()
            return attendances
        except Exception as e:
            self.logger.error(f"Attendance alma hatası {device_id}: {str(e)}")
            return []
    
    def get_all_users(self):
        """Tüm cihazlardan kullanıcıları al"""
        all_users = []
        for device_id, device_info in self.connected_devices.items():
            device = device_info['device']
            
            # Log ekle
            self.add_connection_log(device['name'], "Kullanıcı Listesi Çekme", "Deneniyor", 
                                  f"Cihazdan kullanıcı listesi çekiliyor", "Veri Çekme")
            
            try:
                users = self.get_device_users(device_id)
                
                # Ham veri için JSON formatında detay oluştur
                raw_users_data = []
                for user in users:
                    user_data = {
                        'uid': user.uid,
                        'name': user.name,
                        'privilege': user.privilege,
                        'device_id': device_id,
                        'device_name': device['name']
                    }
                    all_users.append(user_data)
                    
                    # Ham veri için
                    raw_users_data.append({
                        'uid': user.uid,
                        'name': user.name,
                        'privilege': user.privilege,
                        'password': getattr(user, 'password', ''),
                        'group_id': getattr(user, 'group_id', ''),
                        'user_id': getattr(user, 'user_id', ''),
                        'card': getattr(user, 'card', ''),
                    })
                
                # Ham veriyi JSON string olarak hazırla
                import json
                raw_data_json = json.dumps(raw_users_data, indent=2, ensure_ascii=False)
                
                # Başarı logu - ham veri ile
                self.add_connection_log(device['name'], "Kullanıcı Listesi Çekme", "Başarılı", 
                                      f"{len(users)} kullanıcı çekildi\n\nHAM VERİ:\n{raw_data_json}", "Veri Çekme")
                
            except Exception as e:
                # Hata logu
                self.add_connection_log(device['name'], "Kullanıcı Listesi Çekme", "Hata", 
                                      f"Hata: {str(e)}", "Veri Çekme")
        
        return all_users
    
    def get_all_attendance(self):
        """Tüm cihazlardan giriş-çıkış kayıtlarını al"""
        all_attendance = []
        all_formatted_attendance = []
        
        for device_id, device_info in self.connected_devices.items():
            device = device_info['device']
            
            # Log ekle
            self.add_connection_log(device['name'], "Giriş-Çıkış Kayıtları Çekme", "Deneniyor", 
                                  f"Cihazdan giriş-çıkış kayıtları çekiliyor", "Veri Çekme")
            
            try:
                users = self.get_device_users(device_id)
                attendances = self.get_device_attendance(device_id)
                
                # Ham veriyi hiç işlemeden direkt göster
                raw_attendance_data = []
                formatted_attendance_data = []
                
                # Sabit veri şablonu
                template = {
                    "CihazID": "{device_name}",
                    "CihazLogID": "{uid}",
                    "CihazPersonelID": "{user_id}",
                    "Tarih": "{timestamp}"
                }
                
                for att in attendances:
                    # Ham veriden user_id'yi al (gerçek kullanıcı ID'si)
                    actual_user_id = getattr(att, 'user_id', att.uid)
                    
                    # Kullanıcı adını bul - hem uid hem user_id ile kontrol et
                    user_name = None
                    
                    # Önce user_id ile ara
                    for u in users:
                        if str(u.uid) == str(actual_user_id):
                            user_name = u.name
                            break
                    
                    # Bulamazsa uid ile ara
                    if not user_name:
                        for u in users:
                            if str(u.uid) == str(att.uid):
                                user_name = u.name
                                actual_user_id = u.uid
                                break
                    
                    # Hala bulamazsa varsayılan
                    if not user_name:
                        user_name = f"Bilinmeyen Kullanıcı (ID: {actual_user_id})"
                    
                    attendance_data = {
                        'log_id': att.uid,  # Bu log ID'si
                        'uid': actual_user_id,  # Bu gerçek kullanıcı ID'si
                        'user_name': user_name,
                        'timestamp': att.timestamp,
                        'status': att.status,
                        'device_id': device_id,
                        'device_name': device['name']
                    }
                    all_attendance.append(attendance_data)
                    
                    # Ham veri - hiç işlemeden direkt obje özelliklerini göster
                    raw_obj = {}
                    for attr in dir(att):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(att, attr)
                                if not callable(value):
                                    raw_obj[attr] = str(value)
                            except:
                                pass
                    raw_attendance_data.append(raw_obj)
                    
                    # Şablona göre formatlanmış veri
                    formatted_obj = {}
                    for key, value_template in template.items():
                        try:
                            # Template değişkenlerini değiştir
                            formatted_value = value_template.format(
                                device_name=device['name'],
                                uid=getattr(att, 'uid', ''),
                                user_id=getattr(att, 'user_id', getattr(att, 'uid', '')),
                                timestamp=str(getattr(att, 'timestamp', '')),
                                punch=getattr(att, 'punch', ''),
                                status=getattr(att, 'status', '')
                            )
                            formatted_obj[key] = formatted_value
                        except:
                            formatted_obj[key] = value_template
                    formatted_attendance_data.append(formatted_obj)
                    all_formatted_attendance.append(formatted_obj)
                
                # Ham veriyi JSON string olarak hazırla
                import json
                raw_data_json = json.dumps(raw_attendance_data, indent=2, ensure_ascii=False)
                formatted_data_json = json.dumps(formatted_attendance_data, indent=2, ensure_ascii=False)
                
                # Başarı logu - ham veri ve formatlanmış veri ile
                log_details = f"""{len(attendances)} kayıt çekildi

HAM VERİ (Hiç İşlenmemiş):
{raw_data_json}

ŞABLONA GÖRE FORMATLANMIŞ VERİ:
{formatted_data_json}"""
                
                self.add_connection_log(device['name'], "Giriş-Çıkış Kayıtları Çekme", "Başarılı", log_details, "Veri Çekme")
                
            except Exception as e:
                # Hata logu
                self.add_connection_log(device['name'], "Giriş-Çıkış Kayıtları Çekme", "Hata", 
                                      f"Hata: {str(e)}", "Veri Çekme")
        
        return all_attendance
    
    def get_formatted_attendance(self):
        """Tüm cihazlardan formatlanmış giriş-çıkış kayıtlarını al - timestamp bilgisi ile birlikte"""
        all_formatted_attendance = []
        
        for device_id, device_info in self.connected_devices.items():
            device = device_info['device']
            
            try:
                users = self.get_device_users(device_id)
                attendances = self.get_device_attendance(device_id)
                
                # Sabit veri şablonu
                template = {
                    "CihazID": "{device_name}",
                    "CihazLogID": "{uid}",
                    "CihazPersonelID": "{user_id}",
                    "Tarih": "{timestamp}"
                }
                
                for att in attendances:
                    # Şablona göre formatlanmış veri - get_all_attendance() ile aynı mantık
                    formatted_obj = {}
                    for key, value_template in template.items():
                        try:
                            # Template değişkenlerini değiştir
                            formatted_value = value_template.format(
                                device_name=device['name'],
                                uid=getattr(att, 'uid', ''),
                                user_id=getattr(att, 'user_id', getattr(att, 'uid', '')),
                                timestamp=str(getattr(att, 'timestamp', '')),
                                punch=getattr(att, 'punch', ''),
                                status=getattr(att, 'status', '')
                            )
                            formatted_obj[key] = formatted_value
                        except Exception as e:
                            # Hata durumunda template'i olduğu gibi bırak
                            formatted_obj[key] = value_template
                            self.logger.error(f"Template işleme hatası {key}: {str(e)}")
                    
                    # Timestamp kontrolü için ek bilgiler ekle (API manager için)
                    formatted_obj['_device_id'] = device_id
                    formatted_obj['_timestamp'] = getattr(att, 'timestamp', None)
                    
                    all_formatted_attendance.append(formatted_obj)
                
            except Exception as e:
                self.logger.error(f"Formatlanmış veri alma hatası {device['name']}: {str(e)}")
        
        return all_formatted_attendance
    
    @staticmethod
    def get_privilege_text(privilege):
        """Yetki kodunu metne çevir"""
        privilege_map = {
            0: "Kullanıcı",
            14: "Yönetici"
        }
        return privilege_map.get(privilege, f"Bilinmeyen ({privilege})")
    
    @staticmethod
    def get_status_text(status):
        """Durum kodunu metne çevir"""
        status_map = {
            0: "Giriş",
            1: "Çıkış",
            2: "Mola Başı",
            3: "Mola Sonu",
            4: "Mesai Başı",
            5: "Mesai Sonu"
        }
        return status_map.get(status, f"Bilinmeyen ({status})")
