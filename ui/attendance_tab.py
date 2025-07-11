"""
AARO ERP - PDKS Giriş-Çıkış Kayıtları Sekmesi
"""

import tkinter as tk
from tkinter import ttk
from core.device_manager import DeviceManager

class AttendanceTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.device_manager = main_window.device_manager
        
        self.setup_ui()
        self.attendance_data = []
    
    def setup_ui(self):
        """UI'yi oluştur"""
        # Attendance tree
        self.attendance_tree = ttk.Treeview(self, columns=("uid", "name", "timestamp", "status", "device"), show="headings")
        self.attendance_tree.heading("uid", text="Kullanıcı ID")
        self.attendance_tree.heading("name", text="Ad Soyad")
        self.attendance_tree.heading("timestamp", text="Tarih/Saat")
        self.attendance_tree.heading("status", text="Durum")
        self.attendance_tree.heading("device", text="Cihaz")
        
        self.attendance_tree.column("uid", width=100)
        self.attendance_tree.column("name", width=150)
        self.attendance_tree.column("timestamp", width=150)
        self.attendance_tree.column("status", width=100)
        self.attendance_tree.column("device", width=200)
        
        # Scrollbar
        attendance_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=attendance_scrollbar.set)
        
        # Pack
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attendance_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_attendance(self):
        """Giriş-çıkış kayıtlarını yenile"""
        # Mevcut verileri temizle
        self.clear_attendance()
        
        # Tüm cihazlardan giriş-çıkış kayıtlarını al
        all_attendance = self.device_manager.get_all_attendance()
        
        # Sabit veri şablonu (sadece loglama için - UI'da kullanılmıyor)
        template = {
            "CihazID": "{device_name}",
            "CihazLogID": "{uid}",
            "CihazPersonelID": "{user_id}",
            "Tarih": "{timestamp}"
        }
        
        # Tree'ye ekle
        for att in all_attendance:
            status_text = DeviceManager.get_status_text(att['status'])
            timestamp_str = att['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Ham verileri kullan - şablon sadece loglarda formatlanmış veri için
            # Burada kullanıcı dostu görüntüleme yapalım
            attendance_data = {
                'uid': att['uid'],
                'user_name': att['user_name'],
                'timestamp': timestamp_str,
                'status': status_text,
                'device_name': att['device_name']
            }
            self.attendance_data.append(attendance_data)
            
            # Tree'de gösterilecek veriler - ham veriler
            self.attendance_tree.insert("", tk.END, values=(
                att['uid'],           # Kullanıcı ID (ham veri)
                att['user_name'],     # Ad Soyad (ham veri)
                timestamp_str,        # Tarih/Saat
                status_text,          # Durum
                att['device_name']    # Cihaz adı
            ))
    
    def clear_attendance(self):
        """Giriş-çıkış kayıtlarını temizle"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        self.attendance_data = []
    
    def get_all_attendance(self):
        """Tüm attendance verilerini al"""
        return self.attendance_data
