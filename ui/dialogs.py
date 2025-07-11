"""
AARO ERP - PDKS Dialog'ları
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os

class LoadingDialog:
    def __init__(self, parent, title="İşlem Yapılıyor", message="Lütfen bekleyin..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 200, parent.winfo_rooty() + 200))
        
        # Dialog kapatma butonunu devre dışı bırak
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.create_widgets(message)
        
        # Progress bar animasyonu için değişkenler
        self.animation_running = True
        
        # Animasyonu başlat
        self.animate_progress()
    
    def create_widgets(self, message):
        """Loading dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Mesaj
        self.message_label = ttk.Label(main_frame, text=message, font=('Arial', 11))
        self.message_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 10))
        self.progress.start(10)  # 10ms aralıklarla animasyon
        
        # Detay mesajı (opsiyonel)
        self.detail_label = ttk.Label(main_frame, text="", font=('Arial', 9), foreground='gray')
        self.detail_label.pack()
    
    def update_message(self, message):
        """Ana mesajı güncelle"""
        if hasattr(self, 'message_label'):
            self.message_label.config(text=message)
            self.dialog.update()
    
    def update_detail(self, detail):
        """Detay mesajını güncelle"""
        if hasattr(self, 'detail_label'):
            self.detail_label.config(text=detail)
            self.dialog.update()
    
    def animate_progress(self):
        """Progress bar animasyonu"""
        if self.animation_running:
            self.dialog.after(50, self.animate_progress)
    
    def close(self):
        """Loading dialog'u kapat"""
        self.animation_running = False
        if hasattr(self, 'progress'):
            self.progress.stop()
        self.dialog.destroy()


class DeviceDialog:
    def __init__(self, parent, title, device_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(device_data)
        
        self.dialog.wait_window()
    
    def create_widgets(self, device_data):
        """Dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cihaz adı
        ttk.Label(main_frame, text="🏷️ Cihaz Adı:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=device_data.get('name', '') if device_data else '')
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # IP adresi
        ttk.Label(main_frame, text="🌐 IP Adresi:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ip_var = tk.StringVar(value=device_data.get('ip', '') if device_data else '')
        ttk.Entry(main_frame, textvariable=self.ip_var, width=30).grid(row=1, column=1, pady=5)
        
        # Port
        ttk.Label(main_frame, text="🔌 Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value=str(device_data.get('port', 4370)) if device_data else '4370')
        ttk.Entry(main_frame, textvariable=self.port_var, width=30).grid(row=2, column=1, pady=5)
        
        # Protokol
        ttk.Label(main_frame, text="📡 Protokol:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.protocol_var = tk.StringVar(value=device_data.get('protocol', 'TCP') if device_data else 'TCP')
        protocol_combo = ttk.Combobox(main_frame, textvariable=self.protocol_var, values=['TCP', 'UDP'], width=27)
        protocol_combo.grid(row=3, column=1, pady=5)
        
        # Timeout
        ttk.Label(main_frame, text="⏱️ Timeout (saniye):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.StringVar(value=str(device_data.get('timeout', 30)) if device_data else '30')
        ttk.Entry(main_frame, textvariable=self.timeout_var, width=30).grid(row=4, column=1, pady=5)
        
        # Şifre
        ttk.Label(main_frame, text="🔐 Şifre:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=str(device_data.get('password', 0)) if device_data else '0')
        ttk.Entry(main_frame, textvariable=self.password_var, width=30).grid(row=5, column=1, pady=5)
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Kaydet", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ İptal", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """Verileri kaydet"""
        try:
            self.result = {
                'name': self.name_var.get().strip(),
                'ip': self.ip_var.get().strip(),
                'port': int(self.port_var.get()),
                'protocol': self.protocol_var.get(),
                'timeout': int(self.timeout_var.get()),
                'password': int(self.password_var.get()),
                'force_udp': self.protocol_var.get() == 'UDP'
            }
            
            if not self.result['name'] or not self.result['ip']:
                messagebox.showerror("Hata", "Cihaz adı ve IP adresi boş olamaz!")
                return
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Hata", "Port, timeout ve şifre sayısal değer olmalıdır!")
    
    def cancel(self):
        """İptal et"""
        self.dialog.destroy()


class ScanResultDialog:
    def __init__(self, parent, found_devices, main_window):
        self.main_window = main_window
        self.found_devices = found_devices
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔍 Ağ Taraması Sonuçları")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self.create_widgets()
        
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ttk.Label(main_frame, text=f"🎉 {len(self.found_devices)} ZKTeco cihazı bulundu!", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Cihaz listesi
        columns = ("name", "ip", "port")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("name", text="Cihaz Adı")
        self.tree.heading("ip", text="IP Adresi")
        self.tree.heading("port", text="Port")
        
        self.tree.column("name", width=250)
        self.tree.column("ip", width=150)
        self.tree.column("port", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree ve scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cihazları listele
        for device in self.found_devices:
            self.tree.insert("", tk.END, values=(device['name'], device['ip'], device['port']))
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="➕ Seçili Cihazı Ekle", command=self.add_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="➕➕ Tümünü Ekle", command=self.add_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="❌ İptal", command=self.cancel).pack(side=tk.RIGHT)
    
    def add_selected(self):
        """Seçili cihazı ekle"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen eklemek istediğiniz cihazı seçin.")
            return
        
        item = self.tree.item(selection[0])
        device_ip = item['values'][1]
        
        # Cihazı bul
        device = None
        for d in self.found_devices:
            if d['ip'] == device_ip:
                device = d
                break
        
        if device:
            self.add_device_to_config(device)
    
    def add_all(self):
        """Tüm cihazları ekle"""
        added_count = 0
        for device in self.found_devices:
            if self.add_device_to_config(device, show_message=False):
                added_count += 1
        
        messagebox.showinfo("Başarılı", f"🎉 {added_count} cihaz başarıyla eklendi.")
        self.dialog.destroy()
    
    def add_device_to_config(self, device, show_message=True):
        """Cihazı konfigürasyona ekle"""
        # Aynı IP'li cihaz var mı kontrol et
        existing_device = self.main_window.config_manager.get_device_by_name(device['name'])
        if not existing_device:
            for d in self.main_window.config_manager.get_devices():
                if d['ip'] == device['ip']:
                    existing_device = d
                    break
        
        if existing_device:
            if show_message:
                messagebox.showwarning("Uyarı", f"Bu IP adresine ({device['ip']}) sahip bir cihaz zaten mevcut.")
            return False
        
        # Cihazı ekle
        device_id = self.main_window.config_manager.add_device(device)
        self.main_window.device_panel.refresh_device_list()
        
        if show_message:
            messagebox.showinfo("Başarılı", f"✅ '{device['name']}' cihazı başarıyla eklendi (ID: {device_id}).")
            self.dialog.destroy()
        
        return True
    
    def cancel(self):
        """İptal et"""
        self.dialog.destroy()


class SettingsDialog:
    def __init__(self, parent, config_manager, main_window):
        self.config_manager = config_manager
        self.main_window = main_window
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Ayarlar")
        self.dialog.transient(parent)
        # grab_set() kaldırıldı - modal olmayacak
        
        self.create_widgets()
        
        # Otomatik boyutlandırma
        self.dialog.update_idletasks()
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()
        
        # Minimum boyutlar
        min_width = max(600, width)
        min_height = max(500, height)
        
        # Merkeze yerleştir
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (min_width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (min_height // 2)
        
        self.dialog.geometry(f"{min_width}x{min_height}+{x}+{y}")
        self.dialog.minsize(min_width, min_height)
        
        # wait_window() kaldırıldı - non-modal
    
    def create_widgets(self):
        """Ayarlar dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook (sekmeler)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Genel ayarlar sekmesi
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="🔧 Genel")
        
        # Otomatik bağlantı
        self.auto_connect_var = tk.BooleanVar(value=self.config_manager.get_setting('auto_connect', True))
        ttk.Checkbutton(general_frame, text="🚀 Program açılışında otomatik bağlan", 
                       variable=self.auto_connect_var).pack(anchor=tk.W, pady=5)
        
        # Yenileme aralığı
        ttk.Label(general_frame, text="🔄 Otomatik yenileme aralığı (saniye):").pack(anchor=tk.W, pady=(10, 0))
        self.refresh_interval_var = tk.StringVar(value=str(self.config_manager.get_setting('refresh_interval', 60)))
        ttk.Entry(general_frame, textvariable=self.refresh_interval_var, width=10).pack(anchor=tk.W, pady=5)
        
        # Log seviyesi
        ttk.Label(general_frame, text="📋 Log seviyesi:").pack(anchor=tk.W, pady=(10, 0))
        self.log_level_var = tk.StringVar(value=self.config_manager.get_setting('log_level', 'INFO'))
        log_combo = ttk.Combobox(general_frame, textvariable=self.log_level_var, 
                                values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], width=15)
        log_combo.pack(anchor=tk.W, pady=5)
        
        # Ağ ayarları sekmesi
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="🌐 Ağ")
        
        # Veri şablonu sekmesi
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="📋 Veri Şablonu")
        
        # API sekmesi
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="🌐 API")
        
        # API ayarları
        api_settings = self.config_manager.get_setting('api_settings', {
            "enabled": False,
            "token_url": "https://erp.aaro.com.tr/Token",
            "data_url": "https://erp.aaro.com.tr/api/attendance",
            "username": "",
            "password": "",
            "auto_send": False,
            "send_interval": 300
        })
        
        # API etkinleştir
        self.api_enabled_var = tk.BooleanVar(value=api_settings.get('enabled', False))
        ttk.Checkbutton(api_frame, text="🚀 API entegrasyonunu etkinleştir", 
                       variable=self.api_enabled_var).pack(anchor=tk.W, pady=5)
        
        # Token URL
        ttk.Label(api_frame, text="🔑 Token URL:").pack(anchor=tk.W, pady=(10, 0))
        self.token_url_var = tk.StringVar(value=api_settings.get('token_url', ''))
        ttk.Entry(api_frame, textvariable=self.token_url_var, width=50).pack(anchor=tk.W, pady=5)
        
        # Veri URL
        ttk.Label(api_frame, text="📤 Veri Gönderim URL:").pack(anchor=tk.W, pady=(10, 0))
        self.data_url_var = tk.StringVar(value=api_settings.get('data_url', ''))
        ttk.Entry(api_frame, textvariable=self.data_url_var, width=50).pack(anchor=tk.W, pady=5)
        
        # Kullanıcı adı
        ttk.Label(api_frame, text="👤 Kullanıcı Adı:").pack(anchor=tk.W, pady=(10, 0))
        self.api_username_var = tk.StringVar(value=api_settings.get('username', ''))
        ttk.Entry(api_frame, textvariable=self.api_username_var, width=30).pack(anchor=tk.W, pady=5)
        
        # Şifre
        ttk.Label(api_frame, text="🔐 Şifre:").pack(anchor=tk.W, pady=(10, 0))
        self.api_password_var = tk.StringVar(value=api_settings.get('password', ''))
        ttk.Entry(api_frame, textvariable=self.api_password_var, width=30, show="*").pack(anchor=tk.W, pady=5)
        
        # Otomatik gönderim
        self.auto_send_var = tk.BooleanVar(value=api_settings.get('auto_send', False))
        ttk.Checkbutton(api_frame, text="🔄 Otomatik veri gönderimi", 
                       variable=self.auto_send_var).pack(anchor=tk.W, pady=(10, 0))
        
        # Gönderim aralığı
        ttk.Label(api_frame, text="⏱️ Gönderim aralığı (saniye):").pack(anchor=tk.W, pady=(10, 0))
        self.send_interval_var = tk.StringVar(value=str(api_settings.get('send_interval', 300)))
        ttk.Entry(api_frame, textvariable=self.send_interval_var, width=10).pack(anchor=tk.W, pady=5)
        
        # Personel API ayarları
        ttk.Label(api_frame, text="👥 Personel API URL:").pack(anchor=tk.W, pady=(15, 0))
        self.personnel_url_var = tk.StringVar(value=api_settings.get('personnel_url', 'https://erp.aaro.com.tr/api/Personel'))
        ttk.Entry(api_frame, textvariable=self.personnel_url_var, width=50).pack(anchor=tk.W, pady=5)
        
        # Personel sayfa boyutu
        ttk.Label(api_frame, text="📄 Personel sayfa boyutu:").pack(anchor=tk.W, pady=(10, 0))
        self.personnel_page_size_var = tk.StringVar(value=str(api_settings.get('personnel_page_size', 100)))
        ttk.Entry(api_frame, textvariable=self.personnel_page_size_var, width=10).pack(anchor=tk.W, pady=5)
        
        # Başarılı gönderimde cihaz temizleme
        self.clear_device_var = tk.BooleanVar(value=api_settings.get('clear_device_on_success', False))
        ttk.Checkbutton(api_frame, text="🧹 Başarılı gönderimde cihazdan kayıtları sil", 
                       variable=self.clear_device_var).pack(anchor=tk.W, pady=(15, 0))
        
        # Test butonları
        api_test_frame = ttk.Frame(api_frame)
        api_test_frame.pack(anchor=tk.W, pady=(20, 0))
        
        ttk.Button(api_test_frame, text="🔍 Bağlantı Testi", command=self.test_api_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(api_test_frame, text="📤 Test Verisi Gönder", command=self.send_test_data).pack(side=tk.LEFT)
        
        # Veri şablonu açıklaması
        ttk.Label(template_frame, text="📋 Giriş-Çıkış Veri Şablonu:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(template_frame, text="Cihazdan gelen ham verilerin nasıl formatlanacağını belirler.", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        # Sabit şablon (artık config'den çekilmiyor)
        current_template = {
            "CihazID": "{device_name}",
            "CihazLogID": "{uid}",
            "CihazPersonelID": "{user_id}",
            "Tarih": "{timestamp}"
        }
        
        # Şablon metin alanı
        template_text_frame = ttk.Frame(template_frame)
        template_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.template_text = tk.Text(template_text_frame, height=8, font=('Consolas', 9))
        template_scrollbar = ttk.Scrollbar(template_text_frame, orient=tk.VERTICAL, command=self.template_text.yview)
        self.template_text.configure(yscrollcommand=template_scrollbar.set)
        
        self.template_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        template_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mevcut şablonu göster
        import json
        template_json = json.dumps(current_template, indent=2, ensure_ascii=False)
        self.template_text.insert(tk.END, template_json)
        
        # Kullanılabilir değişkenler
        ttk.Label(template_frame, text="🔧 Kullanılabilir Değişkenler:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        variables_text = "{device_name}, {uid}, {user_id}, {timestamp}, {punch}, {status}"
        ttk.Label(template_frame, text=variables_text, font=('Arial', 8), foreground='blue').pack(anchor=tk.W)
        
        # Varsayılan timeout
        ttk.Label(network_frame, text="⏱️ Varsayılan timeout (saniye):").pack(anchor=tk.W, pady=5)
        self.default_timeout_var = tk.StringVar(value=str(self.config_manager.get_setting('default_timeout', 30)))
        ttk.Entry(network_frame, textvariable=self.default_timeout_var, width=10).pack(anchor=tk.W, pady=5)
        
        # Varsayılan port
        ttk.Label(network_frame, text="🔌 Varsayılan port:").pack(anchor=tk.W, pady=(10, 0))
        self.default_port_var = tk.StringVar(value=str(self.config_manager.get_setting('default_port', 4370)))
        ttk.Entry(network_frame, textvariable=self.default_port_var, width=10).pack(anchor=tk.W, pady=5)
        
        # Ağ tarama thread sayısı
        ttk.Label(network_frame, text="🔍 Ağ tarama thread sayısı:").pack(anchor=tk.W, pady=(10, 0))
        self.scan_threads_var = tk.StringVar(value=str(self.config_manager.get_setting('scan_threads', 50)))
        ttk.Entry(network_frame, textvariable=self.scan_threads_var, width=10).pack(anchor=tk.W, pady=5)
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="💾 Kaydet", command=self.save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔄 Varsayılana Sıfırla", command=self.reset_defaults).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="❌ İptal", command=self.cancel).pack(side=tk.RIGHT)
    
    def save(self):
        """Ayarları kaydet"""
        try:
            settings = {
                'auto_connect': self.auto_connect_var.get(),
                'refresh_interval': int(self.refresh_interval_var.get()),
                'log_level': self.log_level_var.get(),
                'default_timeout': int(self.default_timeout_var.get()),
                'default_port': int(self.default_port_var.get()),
                'scan_threads': int(self.scan_threads_var.get())
            }
            
            # Veri şablonunu kaydet
            try:
                import json
                template_text = self.template_text.get(1.0, tk.END).strip()
                template_data = json.loads(template_text)
                settings['attendance_template'] = template_data
            except json.JSONDecodeError:
                messagebox.showerror("Hata", "❌ Veri şablonu geçersiz JSON formatında!")
                return
            except Exception as e:
                messagebox.showerror("Hata", f"❌ Veri şablonu hatası: {str(e)}")
                return
            
            # API ayarlarını kaydet
            api_settings = {
                'enabled': self.api_enabled_var.get(),
                'token_url': self.token_url_var.get().strip(),
                'data_url': self.data_url_var.get().strip(),
                'personnel_url': self.personnel_url_var.get().strip(),
                'username': self.api_username_var.get().strip(),
                'password': self.api_password_var.get(),
                'auto_send': self.auto_send_var.get(),
                'send_interval': int(self.send_interval_var.get()) if self.send_interval_var.get().isdigit() else 300,
                'personnel_page_size': int(self.personnel_page_size_var.get()) if self.personnel_page_size_var.get().isdigit() else 100,
                'clear_device_on_success': self.clear_device_var.get()
            }
            settings['api_settings'] = api_settings
            
            self.config_manager.update_settings(settings)
            
            messagebox.showinfo("Başarılı", "✅ Tüm ayarlar kaydedildi.")
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Hata", "❌ Sayısal değerler geçersiz!")
    
    def test_api_connection(self):
        """API bağlantısını test et"""
        try:
            from utils.api_manager import APIManager
            
            # Geçici API manager oluştur
            temp_api_manager = APIManager(self.config_manager)
            
            # Ana penceredeki callback'i kullan
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'connection_logs_tab'):
                temp_api_manager.set_connection_logs_callback(self.main_window.connection_logs_tab.add_log)
            
            # Geçici ayarları uygula
            temp_settings = {
                'enabled': self.api_enabled_var.get(),
                'token_url': self.token_url_var.get().strip(),
                'data_url': self.data_url_var.get().strip(),
                'username': self.api_username_var.get().strip(),
                'password': self.api_password_var.get(),
                'auto_send': self.auto_send_var.get(),
                'send_interval': int(self.send_interval_var.get()) if self.send_interval_var.get().isdigit() else 300
            }
            
            # Geçici olarak ayarları güncelle
            original_settings = self.config_manager.get_setting('api_settings', {})
            self.config_manager.update_settings({'api_settings': temp_settings})
            
            # Test et
            result = temp_api_manager.test_api_connection()
            
            # Orijinal ayarları geri yükle
            self.config_manager.update_settings({'api_settings': original_settings})
            
            if result['success']:
                messagebox.showinfo("API Test", f"✅ {result['message']}")
            else:
                messagebox.showerror("API Test", f"❌ {result['message']}")
                
        except Exception as e:
            messagebox.showerror("API Test", f"❌ Test hatası: {str(e)}")
    
    def send_test_data(self):
        """Test verisi gönder"""
        try:
            from utils.api_manager import APIManager
            
            # Geçici API manager oluştur
            temp_api_manager = APIManager(self.config_manager)
            
            # Ana penceredeki callback'i kullan
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'connection_logs_tab'):
                temp_api_manager.set_connection_logs_callback(self.main_window.connection_logs_tab.add_log)
            
            # Geçici ayarları uygula
            temp_settings = {
                'enabled': self.api_enabled_var.get(),
                'token_url': self.token_url_var.get().strip(),
                'data_url': self.data_url_var.get().strip(),
                'username': self.api_username_var.get().strip(),
                'password': self.api_password_var.get(),
                'auto_send': self.auto_send_var.get(),
                'send_interval': int(self.send_interval_var.get()) if self.send_interval_var.get().isdigit() else 300
            }
            
            # Geçici olarak ayarları güncelle
            original_settings = self.config_manager.get_setting('api_settings', {})
            self.config_manager.update_settings({'api_settings': temp_settings})
            
            # Test verisi gönder
            result = temp_api_manager.send_test_data()
            
            # Orijinal ayarları geri yükle
            self.config_manager.update_settings({'api_settings': original_settings})
            
            if result['success']:
                messagebox.showinfo("Test Verisi", f"✅ {result['message']}")
            else:
                messagebox.showerror("Test Verisi", f"❌ {result['message']}")
                
        except Exception as e:
            messagebox.showerror("Test Verisi", f"❌ Gönderim hatası: {str(e)}")
    
    def reset_defaults(self):
        """Varsayılan ayarlara sıfırla"""
        if messagebox.askyesno("Onay", "🔄 Tüm ayarları varsayılan değerlere sıfırlamak istediğinizden emin misiniz?"):
            self.auto_connect_var.set(True)
            self.refresh_interval_var.set("60")
            self.log_level_var.set("INFO")
            self.default_timeout_var.set("30")
            self.default_port_var.set("4370")
            self.scan_threads_var.set("50")
    
    def cancel(self):
        """İptal et"""
        self.dialog.destroy()


class LogDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📋 Log Görüntüleyici")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        # grab_set() kaldırıldı - modal olmayacak
        
        # Merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        self.load_logs()
        
        # wait_window() kaldırıldı - non-modal
    
    def create_widgets(self):
        """Log dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Üst panel - Filtreler
        filter_frame = ttk.LabelFrame(main_frame, text="🔍 Filtreler")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        filter_inner = ttk.Frame(filter_frame)
        filter_inner.pack(fill=tk.X, padx=5, pady=5)
        
        # Log seviyesi filtresi
        ttk.Label(filter_inner, text="📊 Seviye:").pack(side=tk.LEFT, padx=(0, 5))
        self.level_filter_var = tk.StringVar(value="Tümü")
        level_combo = ttk.Combobox(filter_inner, textvariable=self.level_filter_var, 
                                  values=['Tümü', 'DEBUG', 'INFO', 'WARNING', 'ERROR'], width=10)
        level_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Arama
        ttk.Label(filter_inner, text="🔍 Arama:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_inner, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Filtre uygula butonu
        ttk.Button(filter_inner, text="🔍 Filtrele", command=self.apply_filter).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_inner, text="🔄 Yenile", command=self.load_logs).pack(side=tk.LEFT)
        
        # Log metni
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=('Consolas', 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Alt panel - Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📋 Seçili Metni Kopyala", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📄 Tümünü Kopyala", command=self.copy_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="💾 Log'u Kaydet", command=self.save_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🧹 Log'u Temizle", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="❌ Kapat", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def load_logs(self):
        """Log dosyasını yükle"""
        self.log_text.delete(1.0, tk.END)
        
        try:
            # Log dosyasını bul
            log_path = os.path.join('logs', 'aaro_pdks.log')
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.log_text.insert(tk.END, content)
            else:
                self.log_text.insert(tk.END, "📝 Log dosyası bulunamadı.\n\n")
                self.log_text.insert(tk.END, "Program çalışma zamanında oluşturulan log'lar burada görünecek.\n")
                
        except Exception as e:
            self.log_text.insert(tk.END, f"❌ Log dosyası okunamadı: {str(e)}\n\n")
        
        # En alta scroll
        self.log_text.see(tk.END)
    
    def apply_filter(self):
        """Filtreleri uygula"""
        level_filter = self.level_filter_var.get()
        search_term = self.search_var.get().lower()
        
        # Tüm metni al
        all_content = self.log_text.get(1.0, tk.END)
        lines = all_content.split('\n')
        
        # Filtreleme
        filtered_lines = []
        for line in lines:
            # Seviye filtresi
            if level_filter != "Tümü":
                if level_filter not in line:
                    continue
            
            # Arama filtresi
            if search_term and search_term not in line.lower():
                continue
            
            filtered_lines.append(line)
        
        # Filtrelenmiş içeriği göster
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, '\n'.join(filtered_lines))
    
    def save_log(self):
        """Log'u dosyaya kaydet"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Metin dosyaları", "*.txt"), ("Tüm dosyalar", "*.*")],
            title="Log Dosyası Kaydet"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    content = self.log_text.get(1.0, tk.END)
                    f.write(content)
                messagebox.showinfo("Başarılı", f"✅ Log dosyası kaydedildi: {filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"❌ Log dosyası kaydedilemedi: {str(e)}")
    
    def copy_selected(self):
        """Seçili metni panoya kopyala"""
        try:
            selected_text = self.log_text.selection_get()
            if selected_text:
                self.dialog.clipboard_clear()
                self.dialog.clipboard_append(selected_text)
                messagebox.showinfo("Kopyalandı", "✅ Seçili metin panoya kopyalandı.")
            else:
                messagebox.showwarning("Uyarı", "⚠️ Kopyalanacak metin seçilmedi.")
        except tk.TclError:
            messagebox.showwarning("Uyarı", "⚠️ Kopyalanacak metin seçilmedi.")
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Kopyalama hatası: {str(e)}")
    
    def copy_all(self):
        """Tüm metni panoya kopyala"""
        try:
            all_text = self.log_text.get(1.0, tk.END)
            if all_text.strip():
                self.dialog.clipboard_clear()
                self.dialog.clipboard_append(all_text)
                messagebox.showinfo("Kopyalandı", "✅ Tüm log metni panoya kopyalandı.")
            else:
                messagebox.showwarning("Uyarı", "⚠️ Kopyalanacak metin yok.")
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Kopyalama hatası: {str(e)}")
    
    def clear_log(self):
        """Log'u temizle"""
        if messagebox.askyesno("Onay", "🧹 Log'u temizlemek istediğinizden emin misiniz?"):
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "✅ Log temizlendi.\n")


class UserDialog:
    def __init__(self, parent, title, devices, user_data=None):
        self.result = None
        self.devices = devices
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(user_data)
        
        self.dialog.wait_window()
    
    def create_widgets(self, user_data):
        """Dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Kullanıcı ID
        ttk.Label(main_frame, text="🆔 Kullanıcı ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.uid_var = tk.StringVar(value=user_data.get('uid', '') if user_data else '')
        ttk.Entry(main_frame, textvariable=self.uid_var, width=30).grid(row=0, column=1, pady=5)
        
        # Ad Soyad
        ttk.Label(main_frame, text="👤 Ad Soyad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=user_data.get('name', '') if user_data else '')
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=1, column=1, pady=5)
        
        # Yetki
        ttk.Label(main_frame, text="🔐 Yetki:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.privilege_var = tk.StringVar(value=user_data.get('privilege_text', 'Kullanıcı') if user_data else 'Kullanıcı')
        privilege_combo = ttk.Combobox(main_frame, textvariable=self.privilege_var, 
                                      values=['Kullanıcı', 'Yönetici'], width=27)
        privilege_combo.grid(row=2, column=1, pady=5)
        
        # Cihaz seçimi
        ttk.Label(main_frame, text="🖥️ Cihaz:").grid(row=3, column=0, sticky=tk.W, pady=5)
        device_names = [device['name'] for device in self.devices]
        self.device_var = tk.StringVar(value=user_data.get('device_name', device_names[0] if device_names else '') if user_data else (device_names[0] if device_names else ''))
        device_combo = ttk.Combobox(main_frame, textvariable=self.device_var, 
                                   values=device_names, width=27)
        device_combo.grid(row=3, column=1, pady=5)
        
        # Şifre (opsiyonel)
        ttk.Label(main_frame, text="🔑 Şifre (opsiyonel):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, width=30, show="*").grid(row=4, column=1, pady=5)
        
        # Grup ID (opsiyonel)
        ttk.Label(main_frame, text="👥 Grup ID (opsiyonel):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.group_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.group_id_var, width=30).grid(row=5, column=1, pady=5)
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Kaydet", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ İptal", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """Verileri kaydet"""
        try:
            if not self.uid_var.get().strip() or not self.name_var.get().strip():
                messagebox.showerror("Hata", "Kullanıcı ID ve Ad Soyad boş olamaz!")
                return
            
            # Cihaz ID'sini bul
            device_id = None
            for device in self.devices:
                if device['name'] == self.device_var.get():
                    device_id = device['id']
                    break
            
            if device_id is None:
                messagebox.showerror("Hata", "Geçerli bir cihaz seçin!")
                return
            
            # Yetki değerini çevir
            privilege_value = 14 if self.privilege_var.get() == 'Yönetici' else 0
            
            self.result = {
                'uid': self.uid_var.get().strip(),
                'name': self.name_var.get().strip(),
                'privilege': privilege_value,
                'device_id': device_id,
                'password': self.password_var.get(),
                'group_id': self.group_id_var.get(),
                'user_id': self.uid_var.get().strip()
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Veri hatası: {str(e)}")
    
    def cancel(self):
        """İptal et"""
        self.dialog.destroy()


class BulkUserDialog:
    def __init__(self, parent, devices):
        self.result = None
        self.devices = devices
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📥 Toplu Kullanıcı Ekleme")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="📥 Toplu Kullanıcı Ekleme", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Açıklama
        info_label = ttk.Label(main_frame, text="Her satıra bir kullanıcı bilgisi girin. Format: ID,Ad Soyad,Yetki(0/14),Cihaz ID")
        info_label.pack(pady=(0, 10))
        
        # Örnek
        example_label = ttk.Label(main_frame, text="Örnek: 1001,Ahmet Yılmaz,0,1", font=('Arial', 9), foreground='gray')
        example_label.pack(pady=(0, 10))
        
        # Metin alanı
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_area = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Varsayılan ayarlar
        settings_frame = ttk.LabelFrame(main_frame, text="Varsayılan Ayarlar")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        settings_inner = ttk.Frame(settings_frame)
        settings_inner.pack(fill=tk.X, padx=5, pady=5)
        
        # Varsayılan cihaz
        ttk.Label(settings_inner, text="🖥️ Varsayılan Cihaz:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        device_names = [device['name'] for device in self.devices]
        self.default_device_var = tk.StringVar(value=device_names[0] if device_names else '')
        device_combo = ttk.Combobox(settings_inner, textvariable=self.default_device_var, 
                                   values=device_names, width=20)
        device_combo.grid(row=0, column=1, padx=(0, 10))
        
        # Varsayılan yetki
        ttk.Label(settings_inner, text="🔐 Varsayılan Yetki:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.default_privilege_var = tk.StringVar(value='Kullanıcı')
        privilege_combo = ttk.Combobox(settings_inner, textvariable=self.default_privilege_var, 
                                      values=['Kullanıcı', 'Yönetici'], width=15)
        privilege_combo.grid(row=0, column=3)
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📝 Şablon Oluştur", command=self.create_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="💾 Kaydet", command=self.save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="❌ İptal", command=self.cancel).pack(side=tk.RIGHT)
    
    def create_template(self):
        """Şablon oluştur"""
        template = """# Toplu Kullanıcı Ekleme Şablonu
# Format: Kullanıcı ID, Ad Soyad, Yetki (0=Kullanıcı, 14=Yönetici), Cihaz ID
# Örnek:
1001,Ahmet Yılmaz,0,1
1002,Mehmet Demir,0,1
1003,Ayşe Kaya,14,1
1004,Fatma Öz,0,2"""
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, template)
    
    def save(self):
        """Verileri kaydet"""
        try:
            content = self.text_area.get(1.0, tk.END).strip()
            if not content:
                messagebox.showwarning("Uyarı", "Lütfen kullanıcı bilgilerini girin.")
                return
            
            users_list = []
            lines = content.split('\n')
            
            # Varsayılan cihaz ID'sini bul
            default_device_id = None
            for device in self.devices:
                if device['name'] == self.default_device_var.get():
                    default_device_id = device['id']
                    break
            
            default_privilege = 14 if self.default_privilege_var.get() == 'Yönetici' else 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = [part.strip() for part in line.split(',')]
                    
                    if len(parts) >= 2:
                        uid = parts[0]
                        name = parts[1]
                        privilege = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else default_privilege
                        device_id = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else default_device_id
                        
                        if uid and name:
                            users_list.append({
                                'uid': uid,
                                'name': name,
                                'privilege': privilege,
                                'device_id': device_id,
                                'password': '',
                                'group_id': '',
                                'user_id': uid
                            })
                    
                except Exception as e:
                    messagebox.showerror("Hata", f"Satır {line_num} hatası: {str(e)}")
                    return
            
            if not users_list:
                messagebox.showwarning("Uyarı", "Geçerli kullanıcı verisi bulunamadı.")
                return
            
            self.result = users_list
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Veri işleme hatası: {str(e)}")
    
    def cancel(self):
        """İptal et"""
        self.dialog.destroy()
