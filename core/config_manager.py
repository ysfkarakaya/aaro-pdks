"""
AARO ERP - PDKS Konfigürasyon Yöneticisi
"""

import json
import os
from tkinter import messagebox

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Konfigürasyon dosyasını yükle"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Varsayılan konfigürasyon oluştur
                return self.create_default_config()
        except FileNotFoundError:
            messagebox.showerror("Hata", f"{self.config_file} dosyası bulunamadı!")
            return self.create_default_config()
        except json.JSONDecodeError:
            messagebox.showerror("Hata", f"{self.config_file} dosyası geçersiz!")
            return self.create_default_config()
    
    def create_default_config(self):
        """Varsayılan konfigürasyon oluştur"""
        default_config = {
            "devices": [],
            "settings": {
                "auto_connect": True,
                "refresh_interval": 60,
                "log_level": "INFO",
                "default_timeout": 30,
                "default_port": 4370,
                "scan_threads": 50
            }
        }
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """Konfigürasyonu kaydet"""
        try:
            config_to_save = config if config else self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)
            if config:
                self.config = config
        except Exception as e:
            messagebox.showerror("Hata", f"Konfigürasyon kaydedilemedi: {str(e)}")
    
    def get_devices(self):
        """Cihaz listesini al"""
        return self.config.get('devices', [])
    
    def add_device(self, device_data):
        """Yeni cihaz ekle"""
        device_data['id'] = self.get_next_device_id()
        self.config['devices'].append(device_data)
        self.save_config()
        return device_data['id']
    
    def update_device(self, device_id, device_data):
        """Cihazı güncelle"""
        for i, device in enumerate(self.config['devices']):
            if device.get('id') == device_id:
                device_data['id'] = device_id
                self.config['devices'][i] = device_data
                self.save_config()
                return True
        return False
    
    def delete_device(self, device_id):
        """Cihazı sil"""
        self.config['devices'] = [d for d in self.config['devices'] if d.get('id') != device_id]
        self.save_config()
    
    def get_device_by_id(self, device_id):
        """ID'ye göre cihaz al"""
        for device in self.config['devices']:
            if device.get('id') == device_id:
                return device
        return None
    
    def get_device_by_name(self, device_name):
        """İsme göre cihaz al"""
        # Tip uyumluluğu için string'e çevir
        device_name_str = str(device_name)
        
        for device in self.config['devices']:
            device_name_in_config = device.get('name')
            device_name_in_config_str = str(device_name_in_config)
            
            if device_name_in_config_str == device_name_str:
                return device
        
        return None
    
    def get_next_device_id(self):
        """Sonraki cihaz ID'sini al"""
        if not self.config['devices']:
            return 1
        return max([d.get('id', 0) for d in self.config['devices']]) + 1
    
    def get_settings(self):
        """Ayarları al"""
        return self.config.get('settings', {})
    
    def get_setting(self, key, default=None):
        """Belirli bir ayarı al"""
        return self.config.get('settings', {}).get(key, default)
    
    def update_settings(self, settings):
        """Ayarları güncelle"""
        self.config['settings'].update(settings)
        self.save_config()
    
    def reload_config(self):
        """Konfigürasyonu yeniden yükle"""
        self.config = self.load_config()
        return self.config
