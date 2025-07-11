"""
AARO ERP - PDKS Ana Uygulama
ZKTeco PDKS Cihaz Yönetim Sistemi
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import logging
from datetime import datetime

# Modül importları
from ui.main_window import MainWindow
from core.config_manager import ConfigManager
from core.device_manager import DeviceManager
from utils.logger import setup_logger

class AaroPDKS:
    def __init__(self):
        # Logger'ı önce başlat
        self.logger = setup_logger()
        
        # Ana pencere oluştur
        self.root = tk.Tk()
        self.root.title("AARO ERP - PDKS v2.0")
        self.root.geometry("1200x800")
        
        # Pencere ikonunu ayarla
        try:
            # PyInstaller için resource path'i al
            import sys
            import os
            if getattr(sys, 'frozen', False):
                # EXE içindeyse
                base_path = sys._MEIPASS
            else:
                # Normal Python çalıştırmasında
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = os.path.join(base_path, 'logo.png')
            
            # PNG dosyasını PhotoImage olarak yükle
            icon_image = tk.PhotoImage(file=logo_path)
            self.root.iconphoto(True, icon_image)
        except Exception as e:
            self.logger.warning(f"İkon yüklenemedi: {str(e)}")
        
        # Konfigürasyon yöneticisini başlat
        self.config_manager = ConfigManager()
        
        # Cihaz yöneticisini başlat
        self.device_manager = DeviceManager(self.config_manager)
        
        # Ana pencereyi oluştur
        self.main_window = MainWindow(
            self.root, 
            self.config_manager, 
            self.device_manager,
            self.logger
        )
        
        # Sistem tepsisini başlat
        self.main_window.start_tray()
        
        # Otomatik başlatma
        if self.config_manager.get_setting('auto_connect', True):
            self.auto_start()
    
    def auto_start(self):
        """Otomatik başlatma işlemi"""
        if self.config_manager.get_devices():
            self.main_window.auto_connect_and_refresh()
    
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Uygulama hatası: {str(e)}")
            messagebox.showerror("Kritik Hata", f"Uygulama hatası: {str(e)}")
        finally:
            # Temizlik işlemleri
            self.device_manager.disconnect_all()

if __name__ == "__main__":
    app = AaroPDKS()
    app.run()
