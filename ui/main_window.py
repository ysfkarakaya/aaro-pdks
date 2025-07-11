"""
AARO ERP - PDKS Ana Pencere
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# PyInstaller uyumluluğu için import yöntemini değiştir
try:
    from ui.dialogs import LoadingDialog, DeviceDialog, SettingsDialog, LogDialog, ScanResultDialog
except ImportError as e:
    print(f"ui.dialogs import hatası: {e}")
    try:
        import ui.dialogs
        LoadingDialog = ui.dialogs.LoadingDialog
        DeviceDialog = ui.dialogs.DeviceDialog
        SettingsDialog = ui.dialogs.SettingsDialog
        LogDialog = ui.dialogs.LogDialog
        ScanResultDialog = ui.dialogs.ScanResultDialog
    except ImportError as e2:
        print(f"ui.dialogs modül import hatası: {e2}")
        LoadingDialog = None
        DeviceDialog = None
        SettingsDialog = None
        LogDialog = None
        ScanResultDialog = None
from ui.users_tab import UsersTab
from ui.attendance_tab import AttendanceTab
from ui.connection_logs_tab import ConnectionLogsTab
from ui.device_panel import DevicePanel
from ui.menu_bar import MenuBar
from utils.export_manager import ExportManager

# Sistem tepsisi için pystray import et
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class MainWindow:
    def __init__(self, root, config_manager, device_manager, logger):
        self.root = root
        self.config_manager = config_manager
        self.device_manager = device_manager
        self.logger = logger
        
        # Export manager
        self.export_manager = ExportManager()
        
        # API manager
        from utils.api_manager import APIManager
        self.api_manager = APIManager(self.config_manager)
        
        # UI bileşenleri
        self.setup_ui()
        
        # Bağlantı logları callback'lerini ayarla
        self.device_manager.set_connection_logs_callback(self.connection_logs_tab.add_log)
        self.api_manager.set_connection_logs_callback(self.connection_logs_tab.add_log)
        
        # API manager'a main window referansını ver
        self.api_manager.set_main_window_ref(self)
        
        # Durum değişkenleri
        self.loading_dialog = None
        
        # Sistem tepsisi değişkenleri
        self.tray_icon = None
        self.is_hidden = False
        
        # Sistem tepsisi kurulumu
        self.setup_system_tray()
        
        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Ana UI'yi oluştur"""
        # Menü çubuğu
        self.menu_bar = MenuBar(self.root, self)
        
        # Ana frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Logo ve başlık frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ekle
        try:
            # PyInstaller için resource path'i al
            import sys
            import os
            if getattr(sys, 'frozen', False):
                # EXE içindeyse
                base_path = sys._MEIPASS
            else:
                # Normal Python çalıştırmasında
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            logo_path = os.path.join(base_path, 'logo.png')
            
            logo_image = tk.PhotoImage(file=logo_path)
            # Logoyu yeniden boyutlandır (64x64)
            logo_resized = logo_image.subsample(logo_image.width() // 64, logo_image.height() // 64)
            logo_label = ttk.Label(header_frame, image=logo_resized)
            logo_label.image = logo_resized  # Referansı koru
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            self.logger.warning(f"Logo yüklenemedi: {str(e)}")
        
        # Başlık ve versiyon
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="AARO ERP - PDKS", font=('Arial', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        version_label = ttk.Label(title_frame, text="PDKS Cihaz Yönetim Sistemi ", font=('Arial', 9), foreground='gray')
        version_label.pack(anchor=tk.W)
        
        # Cihaz paneli
        self.device_panel = DevicePanel(main_frame, self)
        self.device_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Kullanıcılar sekmesi
        self.users_tab = UsersTab(self.notebook, self)
        self.notebook.add(self.users_tab, text="👥 Kullanıcılar")
        
        # Giriş-Çıkış kayıtları sekmesi
        self.attendance_tab = AttendanceTab(self.notebook, self)
        self.notebook.add(self.attendance_tab, text="📋 Giriş-Çıkış Kayıtları")
        
        # AARO Personeller sekmesi
        from ui.aaro_personnel_tab import AAROPersonnelTab
        self.aaro_personnel_tab = AAROPersonnelTab(self.notebook, self)
        self.notebook.add(self.aaro_personnel_tab, text="🏢 AARO Personeller")
        
        # Bağlantı logları sekmesi
        self.connection_logs_tab = ConnectionLogsTab(self.notebook, self)
        self.notebook.add(self.connection_logs_tab, text="🔗 Bağlantı Logları")
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def auto_connect_and_refresh(self):
        """Otomatik bağlantı ve veri yenileme"""
        if not self.config_manager.get_devices():
            self.status_var.set("Hiç cihaz eklenmemiş")
            return
        
        # Loading dialog göster
        if LoadingDialog is not None:
            self.loading_dialog = LoadingDialog(self.root, "Başlatılıyor", "Cihazlara bağlanılıyor ve veriler yükleniyor...")
            threading.Thread(target=self._auto_connect_and_refresh_thread, daemon=True).start()
        else:
            # Dialog yüklenemezse direkt thread'i başlat
            threading.Thread(target=self._auto_connect_and_refresh_thread, daemon=True).start()
    
    def _auto_connect_and_refresh_thread(self):
        """Otomatik bağlantı ve veri yenileme thread'i"""
        try:
            # Cihazlara bağlan
            self.root.after(0, lambda: self.loading_dialog.update_message("Cihazlara bağlanılıyor..."))
            
            def progress_callback(message):
                self.root.after(0, lambda: self.loading_dialog.update_detail(message))
            
            connected_count = self.device_manager.connect_all_devices(progress_callback)
            
            # Cihaz panelini güncelle
            self.root.after(0, self.device_panel.refresh_device_list)
            
            # Eğer bağlı cihaz varsa verileri yenile
            if connected_count > 0:
                self.root.after(0, lambda: self.loading_dialog.update_message("Veriler yükleniyor..."))
                self.root.after(0, lambda: self.loading_dialog.update_detail(f"{connected_count} cihazdan veriler çekiliyor..."))
                
                # Verileri çek ve göster
                self._refresh_all_data(progress_callback)
                
                # Başarı mesajı
                total_users = len(self.users_tab.get_all_users())
                total_attendance = len(self.attendance_tab.get_all_attendance())
                self.root.after(0, lambda: self.status_var.set(f"Başlatıldı - {connected_count} cihaz bağlı, {total_users} kullanıcı, {total_attendance} kayıt"))
            else:
                # Hiç cihaz bağlanamadı
                self.root.after(0, lambda: self.status_var.set("Hiç cihaza bağlanılamadı"))
            
            # Loading dialog kapat
            self.root.after(0, self.loading_dialog.close)
            
        except Exception as e:
            self.logger.error(f"Otomatik başlatma hatası: {str(e)}")
            self.root.after(0, self.loading_dialog.close)
            self.root.after(0, lambda: self.status_var.set("Başlatma hatası"))
    
    def connect_all_devices(self):
        """Tüm cihazlara bağlan"""
        if not self.config_manager.get_devices():
            messagebox.showinfo("Bilgi", "Henüz hiç cihaz eklenmemiş.")
            return
        
        # Loading dialog göster
        self.loading_dialog = LoadingDialog(self.root, "Cihazlara Bağlanılıyor", "Cihazlara bağlantı kuruluyor...")
        threading.Thread(target=self._connect_devices_thread, daemon=True).start()
    
    def _connect_devices_thread(self):
        """Cihazlara bağlanma thread'i"""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.loading_dialog.update_detail(message))
            
            connected_count = self.device_manager.connect_all_devices(progress_callback)
            
            # Loading dialog kapat
            self.root.after(0, self.loading_dialog.close)
            
            # UI güncelleme
            self.root.after(0, self.device_panel.refresh_device_list)
            self.root.after(0, lambda: self.status_var.set(f"{connected_count} cihaz bağlı"))
            
        except Exception as e:
            self.logger.error(f"Cihaz bağlantı hatası: {str(e)}")
            self.root.after(0, self.loading_dialog.close)
            self.root.after(0, lambda: self.status_var.set("Bağlantı hatası"))
    
    def refresh_data(self):
        """Verileri yenile"""
        if not self.device_manager.get_connected_devices():
            messagebox.showinfo("Bilgi", "Hiç bağlı cihaz yok. Önce cihazlara bağlanın.")
            return
        
        # Loading dialog göster
        self.loading_dialog = LoadingDialog(self.root, "Veriler Yenileniyor", "Cihazlardan veriler çekiliyor...")
        threading.Thread(target=self._refresh_data_thread, daemon=True).start()
    
    def _refresh_data_thread(self):
        """Veri yenileme thread'i"""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.loading_dialog.update_detail(message))
            
            # Verileri çek ve göster
            self._refresh_all_data(progress_callback)
            
            # Loading dialog kapat
            self.root.after(0, self.loading_dialog.close)
            
            total_users = len(self.users_tab.get_all_users())
            total_attendance = len(self.attendance_tab.get_all_attendance())
            self.root.after(0, lambda: self.status_var.set(f"Veriler güncellendi - {total_users} kullanıcı, {total_attendance} kayıt"))
            
        except Exception as e:
            self.logger.error(f"Veri yenileme hatası: {str(e)}")
            self.root.after(0, self.loading_dialog.close)
            self.root.after(0, lambda: self.status_var.set("Veri yenileme hatası"))
    
    def _refresh_all_data(self, progress_callback=None):
        """Tüm verileri yenile"""
        # Kullanıcıları yenile
        if progress_callback:
            progress_callback("Kullanıcılar yükleniyor...")
        self.root.after(0, self.users_tab.refresh_users)
        
        # Attendance kayıtlarını yenile
        if progress_callback:
            progress_callback("Giriş-çıkış kayıtları yükleniyor...")
        self.root.after(0, self.attendance_tab.refresh_attendance)
    
    def scan_network(self):
        """Ağ taraması yap"""
        # Loading dialog göster
        self.loading_dialog = LoadingDialog(self.root, "Ağ Taraması", "Yerel ağda ZKTeco cihazları aranıyor...")
        threading.Thread(target=self._scan_network_thread, daemon=True).start()
    
    def _scan_network_thread(self):
        """Ağ taraması thread'i"""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.loading_dialog.update_detail(message))
            
            found_devices = self.device_manager.scan_network_for_devices(progress_callback)
            
            # Loading dialog kapat
            self.root.after(0, self.loading_dialog.close)
            
            # Sonuçları göster
            if found_devices:
                self.root.after(0, lambda: self._show_scan_results(found_devices))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Ağ Taraması", "Hiç ZKTeco cihazı bulunamadı."))
                
        except Exception as e:
            self.logger.error(f"Ağ taraması hatası: {str(e)}")
            self.root.after(0, self.loading_dialog.close)
            self.root.after(0, lambda: messagebox.showerror("Hata", f"Ağ taraması sırasında hata oluştu: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.status_var.set("Hazır"))
    
    def _show_scan_results(self, found_devices):
        """Tarama sonuçlarını göster"""
        if ScanResultDialog is not None:
            try:
                dialog = ScanResultDialog(self.root, found_devices, self)
            except Exception as e:
                messagebox.showerror("Hata", f"Tarama sonuçları gösterilemedi: {str(e)}")
        else:
            messagebox.showerror("Hata", "ScanResultDialog sınıfı yüklenemedi.")
    
    def export_to_excel(self):
        """Verileri Excel'e aktar"""
        users_data = self.users_tab.get_all_users()
        attendance_data = self.attendance_tab.get_all_attendance()
        
        if not users_data and not attendance_data:
            messagebox.showinfo("Bilgi", "Aktarılacak veri yok. Önce verileri yükleyin.")
            return
        
        self.export_manager.export_data(self.root, users_data, attendance_data)
    
    def show_settings(self):
        """Ayarlar penceresini göster"""
        if SettingsDialog is not None:
            try:
                dialog = SettingsDialog(self.root, self.config_manager, self)
            except Exception as e:
                messagebox.showerror("Hata", f"Ayarlar penceresi açılamadı: {str(e)}")
        else:
            messagebox.showerror("Hata", "SettingsDialog sınıfı yüklenemedi.")
    
    def show_logs(self):
        """Log penceresini göster"""
        if LogDialog is not None:
            try:
                dialog = LogDialog(self.root)
            except Exception as e:
                messagebox.showerror("Hata", f"Log penceresi açılamadı: {str(e)}")
        else:
            messagebox.showerror("Hata", "LogDialog sınıfı yüklenemedi.")
    
    def clear_data(self):
        """Verileri temizle"""
        if messagebox.askyesno("Onay", "Tüm kullanıcı ve giriş-çıkış verilerini temizlemek istediğinizden emin misiniz?"):
            self.users_tab.clear_users()
            self.attendance_tab.clear_attendance()
            self.status_var.set("Veriler temizlendi")
    
    def reload_config(self):
        """Konfigürasyonu yeniden yükle"""
        self.config_manager.reload_config()
        self.device_panel.refresh_device_list()
        messagebox.showinfo("Bilgi", "Konfigürasyon yeniden yüklendi.")
    
    def test_all_connections(self):
        """Tüm cihazlara bağlantı testi yap"""
        devices = self.config_manager.get_devices()
        if not devices:
            messagebox.showinfo("Bilgi", "Test edilecek cihaz yok.")
            return
        
        self.loading_dialog = LoadingDialog(self.root, "Bağlantı Testi", "Tüm cihazlara bağlantı test ediliyor...")
        threading.Thread(target=self._test_all_connections_thread, daemon=True).start()
    
    def _test_all_connections_thread(self):
        """Tüm cihazlara bağlantı testi thread'i"""
        devices = self.config_manager.get_devices()
        results = []
        
        for i, device in enumerate(devices, 1):
            self.root.after(0, lambda d=device, i=i, t=len(devices): 
                          self.loading_dialog.update_detail(f"Test ediliyor: {d['name']} ({i}/{t})"))
            
            test_result = self.device_manager.test_device_connection(device)
            
            if test_result["success"]:
                results.append(f"✓ {device['name']}: {test_result['message']}")
            else:
                results.append(f"✗ {device['name']}: {test_result['message']}")
        
        # Sonuçları göster
        self.root.after(0, self.loading_dialog.close)
        self.root.after(0, lambda: self._show_test_results(results))
    
    def _show_test_results(self, results):
        """Test sonuçlarını göster"""
        result_text = "\n".join(results)
        messagebox.showinfo("Bağlantı Test Sonuçları", result_text)
    
    def show_help(self):
        """Yardım penceresini göster"""
        help_text = """
AARO ERP - PDKS v2.0 Kullanım Kılavuzu

🔧 Cihaz Yönetimi:
• Cihaz Ekle: Yeni ZKTeco cihazı ekleyin
• Ağ Taraması: Yerel ağdaki cihazları otomatik bulun
• Bağlantı Testi: Cihazlara erişimi test edin

📊 Veri Yönetimi:
• Verileri Yenile: Cihazlardan güncel verileri çekin
• Excel'e Aktar: Verileri Excel/CSV formatında kaydedin
• Verileri Temizle: Ekrandaki verileri temizleyin

⚙️ Ayarlar:
• Otomatik bağlantı ayarları
• Yenileme aralığı
• Log seviyesi

🔍 Sağ Tık Menüsü:
Cihaz listesinde sağ tıklayarak:
• Cihaz düzenleme
• Cihaz silme
• Bağlantı testi
• Cihaz bilgileri

📋 Kısayollar:
• F5: Verileri yenile
• Ctrl+E: Excel'e aktar
• Ctrl+S: Ayarlar
        """
        messagebox.showinfo("Kullanım Kılavuzu", help_text)
    
    def show_about(self):
        """Hakkında penceresini göster"""
        about_text = """
AARO ERP - PDKS v2.0

ZKTeco PDKS Cihaz Yönetim Sistemi

Özellikler:
✅ Çoklu cihaz desteği
✅ Otomatik ağ taraması
✅ Gerçek zamanlı veri senkronizasyonu
✅ Excel/CSV export
✅ Modern modüler mimari
✅ Detaylı loglama

Geliştirici: AARO ERP
Tarih: 2025
Lisans: MIT

ZKTeco cihazları için geliştirilmiş
profesyonel PDKS yönetim çözümü.
        """
        messagebox.showinfo("Hakkında", about_text)
    
    def setup_system_tray(self):
        """Sistem tepsisi kurulumu"""
        if not TRAY_AVAILABLE:
            self.logger.warning("Sistem tepsisi desteği yok (pystray veya PIL yüklü değil)")
            return
        
        try:
            # Tray ikonu oluştur
            image = self.create_tray_icon()
            
            # Tray menüsü oluştur
            menu = pystray.Menu(
                item('🖥️ Pencereyi Göster', self.show_window, default=True),
                item('🔄 Verileri Yenile', self.refresh_data_from_tray),
                item('📤 Veri Gönder', self.send_data_from_tray),
                pystray.Menu.SEPARATOR,
                item('⚙️ Ayarlar', self.show_settings_from_tray),
                item('📋 Loglar', self.show_logs_from_tray),
                pystray.Menu.SEPARATOR,
                item('🚪 Çıkış', self.quit_application)
            )
            
            # Tray ikonu oluştur
            self.tray_icon = pystray.Icon("AARO_PDKS", image, "AARO ERP - PDKS", menu)
            
            self.logger.info("Sistem tepsisi kuruldu")
            
        except Exception as e:
            self.logger.error(f"Sistem tepsisi kurulum hatası: {str(e)}")
    
    def create_tray_icon(self):
        """Tray ikonu oluştur"""
        try:
            # Logo dosyasını kullanmaya çalış
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            logo_path = os.path.join(base_path, 'logo.png')
            
            if os.path.exists(logo_path):
                # Logo dosyasını yükle ve yeniden boyutlandır
                image = Image.open(logo_path)
                image = image.resize((64, 64), Image.Resampling.LANCZOS)
                return image
            else:
                raise FileNotFoundError("Logo bulunamadı")
                
        except Exception as e:
            self.logger.warning(f"Logo yüklenemedi, varsayılan ikon oluşturuluyor: {str(e)}")
            
            # Varsayılan ikon oluştur
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Basit bir ikon çiz
            draw.rectangle([10, 10, width-10, height-10], fill='blue', outline='darkblue', width=2)
            draw.text((width//2-10, height//2-5), "PDKS", fill='white')
            
            return image
    
    def start_tray(self):
        """Sistem tepsisini başlat"""
        if self.tray_icon and TRAY_AVAILABLE:
            try:
                # Tray'i ayrı thread'de çalıştır
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
                self.logger.info("Sistem tepsisi başlatıldı")
            except Exception as e:
                self.logger.error(f"Sistem tepsisi başlatma hatası: {str(e)}")
    
    def hide_to_tray(self):
        """Pencereyi sistem tepsisine gizle"""
        if self.tray_icon and TRAY_AVAILABLE:
            self.root.withdraw()  # Pencereyi gizle
            self.is_hidden = True
            self.logger.info("Pencere sistem tepsisine gizlendi")
        else:
            # Tray desteği yoksa minimize et
            self.root.iconify()
    
    def show_window(self, icon=None, item=None):
        """Pencereyi göster"""
        self.root.after(0, self._show_window_main_thread)
    
    def _show_window_main_thread(self):
        """Ana thread'de pencereyi göster"""
        self.root.deiconify()  # Pencereyi göster
        self.root.lift()       # Öne getir
        self.root.focus_force() # Odakla
        self.is_hidden = False
        self.logger.info("Pencere gösterildi")
    
    def on_closing(self):
        """Pencere kapatma olayı"""
        if TRAY_AVAILABLE and self.tray_icon:
            # Sistem tepsisi varsa gizle
            self.hide_to_tray()
            
            # İlk kez gizleniyorsa bilgi ver
            if not hasattr(self, '_tray_info_shown'):
                self.root.after(100, lambda: messagebox.showinfo(
                    "Sistem Tepsisi", 
                    "Uygulama sistem tepsisinde çalışmaya devam ediyor.\n\n"
                    "Pencereyi tekrar açmak için sistem tepsisindeki ikona çift tıklayın."
                ))
                self._tray_info_shown = True
        else:
            # Sistem tepsisi yoksa çıkış yap
            self.quit_application()
    
    def refresh_data_from_tray(self, icon=None, item=None):
        """Tray'den veri yenileme"""
        self.root.after(0, self.refresh_data)
    
    def send_data_from_tray(self, icon=None, item=None):
        """Tray'den veri gönderimi"""
        self.root.after(0, self.menu_bar.send_attendance_data)
    
    def show_settings_from_tray(self, icon=None, item=None):
        """Tray'den ayarlar"""
        self.root.after(0, self.show_settings)
    
    def show_logs_from_tray(self, icon=None, item=None):
        """Tray'den loglar"""
        self.root.after(0, self.show_logs)
    
    def quit_application(self, icon=None, item=None):
        """Uygulamayı tamamen kapat"""
        try:
            # API manager'ı durdur
            if hasattr(self, 'api_manager'):
                self.api_manager.stop_auto_send()
                self.api_manager.stop_auto_refresh()
            
            # Cihaz bağlantılarını kes
            if hasattr(self, 'device_manager'):
                self.device_manager.disconnect_all()
            
            # Tray ikonu durdur
            if self.tray_icon and TRAY_AVAILABLE:
                self.tray_icon.stop()
            
            self.logger.info("Uygulama kapatılıyor")
            
            # Tkinter'ı kapat
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Uygulama kapatma hatası: {str(e)}")
        finally:
            # Zorla çık
            sys.exit(0)
