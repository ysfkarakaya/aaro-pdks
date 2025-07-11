"""
AARO ERP - PDKS Cihaz Paneli
"""

import tkinter as tk
from tkinter import ttk, messagebox

# PyInstaller uyumluluğu için çoklu import stratejisi
DeviceDialog = None

# Strateji 1: Direct import
try:
    from ui.dialogs import DeviceDialog
    print("DeviceDialog: Direct import başarılı")
except ImportError as e:
    print(f"DeviceDialog direct import hatası: {e}")
    
    # Strateji 2: Module import
    try:
        import ui.dialogs
        DeviceDialog = ui.dialogs.DeviceDialog
        print("DeviceDialog: Module import başarılı")
    except ImportError as e2:
        print(f"DeviceDialog module import hatası: {e2}")
        
        # Strateji 3: Absolute import
        try:
            import sys
            import os
            
            # EXE içindeyse _MEIPASS kullan
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            ui_path = os.path.join(base_path, 'ui')
            if ui_path not in sys.path:
                sys.path.insert(0, ui_path)
            
            from dialogs import DeviceDialog
            print("DeviceDialog: Absolute import başarılı")
        except ImportError as e3:
            print(f"DeviceDialog absolute import hatası: {e3}")
            
            # Strateji 4: Runtime import
            try:
                import importlib.util
                dialogs_path = os.path.join(base_path, 'ui', 'dialogs.py')
                if os.path.exists(dialogs_path):
                    spec = importlib.util.spec_from_file_location("dialogs", dialogs_path)
                    dialogs_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(dialogs_module)
                    DeviceDialog = dialogs_module.DeviceDialog
                    print("DeviceDialog: Runtime import başarılı")
                else:
                    print(f"DeviceDialog: dialogs.py bulunamadı: {dialogs_path}")
            except Exception as e4:
                print(f"DeviceDialog runtime import hatası: {e4}")
                DeviceDialog = None

print(f"DeviceDialog final durumu: {DeviceDialog}")

# Eğer hiçbir import stratejisi çalışmazsa basit bir DeviceDialog oluştur
if DeviceDialog is None:
    print("DeviceDialog bulunamadı, basit dialog oluşturuluyor...")
    
    class SimpleDeviceDialog:
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
    
    DeviceDialog = SimpleDeviceDialog
    print("DeviceDialog: Basit dialog oluşturuldu")

class DevicePanel(ttk.LabelFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent, text="🔧 Cihaz Yönetimi")
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.device_manager = main_window.device_manager
        
        self.setup_ui()
        self.setup_context_menu()
    
    def setup_ui(self):
        """UI'yi oluştur"""
        # Buton çerçevesi
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sol taraf butonları
        left_btn_frame = ttk.Frame(btn_frame)
        left_btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_btn_frame, text="➕ Cihaz Ekle", command=self.add_device).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="🔍 Ağ Taraması", command=self.main_window.scan_network).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="🔗 Tüm Cihazlara Bağlan", command=self.main_window.connect_all_devices).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="🔄 Verileri Yenile", command=self.main_window.refresh_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # Sağ taraf butonları
        right_btn_frame = ttk.Frame(btn_frame)
        right_btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_btn_frame, text="📊 Excel'e Aktar", command=self.main_window.export_to_excel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_btn_frame, text="⚙️ Ayarlar", command=self.main_window.show_settings).pack(side=tk.LEFT)
        
        # Cihaz listesi
        self.device_tree = ttk.Treeview(self, columns=("name", "ip", "port", "status"), show="headings", height=6)
        self.device_tree.heading("name", text="Cihaz Adı")
        self.device_tree.heading("ip", text="IP Adresi")
        self.device_tree.heading("port", text="Port")
        self.device_tree.heading("status", text="Durum")
        
        self.device_tree.column("name", width=200)
        self.device_tree.column("ip", width=150)
        self.device_tree.column("port", width=100)
        self.device_tree.column("status", width=150)
        
        self.device_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # İlk yükleme
        self.refresh_device_list()
    
    def setup_context_menu(self):
        """Sağ tık menüsünü ayarla"""
        self.context_menu = tk.Menu(self.main_window.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Düzenle", command=self.edit_device)
        self.context_menu.add_command(label="🗑️ Sil", command=self.delete_device)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🧪 Bağlantıyı Test Et", command=self.test_connection)
        self.context_menu.add_command(label="🧹 Giriş-Çıkış Kayıtlarını Temizle", command=self.clear_attendance_records)
        self.context_menu.add_command(label="ℹ️ Cihaz Bilgilerini Göster", command=self.show_device_info)
        
        # Sağ tık olayını bağla
        self.device_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Sağ tık menüsünü göster"""
        # Tıklanan öğeyi seç
        item = self.device_tree.identify_row(event.y)
        if item:
            self.device_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def refresh_device_list(self):
        """Cihaz listesini yenile"""
        # Mevcut öğeleri temizle
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        # Cihazları ekle
        for device in self.config_manager.get_devices():
            status = "🟢 Bağlı" if self.device_manager.is_device_connected(device['id']) else "🔴 Bağlı Değil"
            self.device_tree.insert("", tk.END, values=(device['name'], device['ip'], device['port'], status))
    
    def add_device(self):
        """Yeni cihaz ekle"""
        print(f"add_device çağrıldı, DeviceDialog durumu: {DeviceDialog}")
        print(f"DeviceDialog tipi: {type(DeviceDialog)}")
        
        if DeviceDialog is None:
            print("DeviceDialog None, hata mesajı gösteriliyor")
            messagebox.showerror("Hata", "DeviceDialog sınıfı yüklenemedi. Lütfen uygulamayı yeniden başlatın.")
            return
        
        try:
            print("DeviceDialog oluşturuluyor (yeni cihaz)...")
            print(f"Parent: {self.main_window.root}")
            print(f"Title: Cihaz Ekle")
            
            dialog = DeviceDialog(self.main_window.root, "Cihaz Ekle")
            print(f"Dialog oluşturuldu: {dialog}")
            print(f"Dialog result: {dialog.result}")
            
            if dialog.result:
                print("Dialog result var, ekleniyor...")
                device_id = self.config_manager.add_device(dialog.result)
                self.refresh_device_list()
                messagebox.showinfo("Başarılı", f"Cihaz başarıyla eklendi (ID: {device_id})")
            else:
                print("Dialog result yok (iptal edildi)")
                
        except Exception as e:
            print(f"DeviceDialog oluşturma hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Hata", f"Cihaz ekleme hatası: {str(e)}")
    
    def edit_device(self):
        """Seçili cihazı düzenle"""
        print(f"edit_device çağrıldı, DeviceDialog durumu: {DeviceDialog}")
        print(f"DeviceDialog tipi: {type(DeviceDialog)}")
        
        if DeviceDialog is None:
            print("DeviceDialog None, hata mesajı gösteriliyor")
            messagebox.showerror("Hata", "DeviceDialog sınıfı yüklenemedi. Lütfen uygulamayı yeniden başlatın.")
            return
        
        selection = self.device_tree.selection()
        if not selection:
            print("Hiç cihaz seçilmemiş")
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek istediğiniz cihazı seçin.")
            return
        
        item = self.device_tree.item(selection[0])
        device_name = item['values'][0]
        print(f"Düzenlenecek cihaz: {device_name}")
        
        # Cihazı bul
        print(f"get_device_by_name çağrılıyor: '{device_name}'")
        
        # Tüm cihazları listele
        all_devices = self.config_manager.get_devices()
        print(f"Config'deki tüm cihazlar:")
        for i, dev in enumerate(all_devices):
            print(f"  {i}: ID={dev.get('id')}, Name='{dev.get('name')}', IP={dev.get('ip')}")
        
        device = self.config_manager.get_device_by_name(device_name)
        if device:
            print(f"Cihaz bulundu: {device}")
            try:
                print("DeviceDialog oluşturuluyor...")
                print(f"Parent: {self.main_window.root}")
                print(f"Title: Cihaz Düzenle")
                print(f"Device data: {device}")
                
                dialog = DeviceDialog(self.main_window.root, "Cihaz Düzenle", device)
                print(f"Dialog oluşturuldu: {dialog}")
                print(f"Dialog result: {dialog.result}")
                
                if dialog.result:
                    print("Dialog result var, güncelleniyor...")
                    self.config_manager.update_device(device['id'], dialog.result)
                    self.refresh_device_list()
                    messagebox.showinfo("Başarılı", "Cihaz başarıyla güncellendi.")
                else:
                    print("Dialog result yok (iptal edildi)")
                    
            except Exception as e:
                print(f"DeviceDialog oluşturma hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Hata", f"Cihaz düzenleme hatası: {str(e)}")
        else:
            print(f"Cihaz bulunamadı: {device_name}")
    
    def delete_device(self):
        """Seçili cihazı sil"""
        print("delete_device çağrıldı")
        
        selection = self.device_tree.selection()
        if not selection:
            print("Hiç cihaz seçilmemiş")
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz cihazı seçin.")
            return
        
        item = self.device_tree.item(selection[0])
        device_name = item['values'][0]
        print(f"Silinecek cihaz: {device_name}")
        
        if messagebox.askyesno("Onay", f"'{device_name}' cihazını silmek istediğinizden emin misiniz?"):
            print(f"Silme onaylandı, cihaz aranıyor: '{device_name}'")
            
            # Tüm cihazları listele
            all_devices = self.config_manager.get_devices()
            print(f"Config'deki tüm cihazlar:")
            for i, dev in enumerate(all_devices):
                print(f"  {i}: ID={dev.get('id')}, Name='{dev.get('name')}', IP={dev.get('ip')}")
            
            device = self.config_manager.get_device_by_name(device_name)
            if device:
                print(f"Cihaz bulundu, siliniyor: {device}")
                # Bağlantıyı kes
                self.device_manager.disconnect_device(device['id'])
                # Konfigürasyondan sil
                self.config_manager.delete_device(device['id'])
                self.refresh_device_list()
                messagebox.showinfo("Başarılı", "Cihaz başarıyla silindi.")
            else:
                print(f"Cihaz bulunamadı: {device_name}")
                messagebox.showerror("Hata", f"Cihaz bulunamadı: {device_name}")
    
    def test_connection(self):
        """Seçili cihaza bağlantıyı test et"""
        selection = self.device_tree.selection()
        if not selection:
            return
        
        item = self.device_tree.item(selection[0])
        device_name = item['values'][0]
        
        device = self.config_manager.get_device_by_name(device_name)
        if device:
            self.main_window.status_var.set(f"{device_name} bağlantısı test ediliyor...")
            
            # Test et
            result = self.device_manager.test_device_connection(device)
            
            if result["success"]:
                messagebox.showinfo("Bağlantı Testi", f"{device_name}: {result['message']}")
            else:
                messagebox.showerror("Bağlantı Testi", f"{device_name}: {result['message']}")
            
            self.main_window.status_var.set("Hazır")
    
    def show_device_info(self):
        """Seçili cihazın bilgilerini göster"""
        selection = self.device_tree.selection()
        if not selection:
            return
        
        item = self.device_tree.item(selection[0])
        device_name = item['values'][0]
        
        device = self.config_manager.get_device_by_name(device_name)
        if device:
            info = f"""Cihaz Bilgileri:

🏷️ Cihaz Adı: {device['name']}
🌐 IP Adresi: {device['ip']}
🔌 Port: {device['port']}
📡 Protokol: {device['protocol']}
⏱️ Timeout: {device['timeout']} saniye
🔐 Şifre: {device['password']}
🔗 Durum: {'🟢 Bağlı' if self.device_manager.is_device_connected(device['id']) else '🔴 Bağlı Değil'}
🆔 ID: {device['id']}"""
            
            messagebox.showinfo("Cihaz Bilgileri", info)
    
    def clear_attendance_records(self):
        """Seçili cihazın giriş-çıkış kayıtlarını temizle"""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen kayıtlarını temizlemek istediğiniz cihazı seçin.")
            return
        
        item = self.device_tree.item(selection[0])
        device_name = item['values'][0]
        
        device = self.config_manager.get_device_by_name(device_name)
        if not device:
            messagebox.showerror("Hata", "Cihaz bulunamadı.")
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", 
                                  f"🧹 '{device_name}' cihazındaki tüm giriş-çıkış kayıtlarını temizlemek istediğinizden emin misiniz?\n\n"
                                  f"⚠️ Bu işlem geri alınamaz!"):
            return
        
        # Cihazın bağlı olup olmadığını kontrol et
        if not self.device_manager.is_device_connected(device['id']):
            messagebox.showerror("Hata", f"'{device_name}' cihazı bağlı değil. Önce cihaza bağlanın.")
            return
        
        try:
            # Cihaz bağlantısını al
            device_conn = self.device_manager.get_device_connection(device['id'])
            
            if device_conn:
                # Attendance kayıtlarını temizle
                device_conn.clear_attendance()
                
                # Log ekle
                self.device_manager.add_connection_log(
                    device['name'], 
                    "Kayıt Temizleme", 
                    "Başarılı", 
                    "Manuel olarak giriş-çıkış kayıtları temizlendi",
                    "Veri Yönetimi"
                )
                
                messagebox.showinfo("Başarılı", f"✅ '{device_name}' cihazındaki giriş-çıkış kayıtları başarıyla temizlendi.")
                
                # Giriş-çıkış sekmesini yenile
                self.main_window.attendance_tab.refresh_attendance()
                
            else:
                messagebox.showerror("Hata", f"'{device_name}' cihazına bağlantı kurulamadı.")
                
        except Exception as e:
            # Hata logu
            self.device_manager.add_connection_log(
                device['name'], 
                "Kayıt Temizleme", 
                "Hata", 
                f"Manuel kayıt temizleme hatası: {str(e)}",
                "Veri Yönetimi"
            )
            
            messagebox.showerror("Hata", f"❌ Kayıt temizleme hatası: {str(e)}")
