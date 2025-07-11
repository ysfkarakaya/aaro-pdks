"""
AARO ERP - PDKS Menü Çubuğu
"""

import tkinter as tk

class MenuBar:
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self.create_menu()
    
    def create_menu(self):
        """Menü çubuğunu oluştur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Dosya", menu=file_menu)
        file_menu.add_command(label="📊 Excel'e Aktar", command=self.main_window.export_to_excel)
        file_menu.add_separator()
        file_menu.add_command(label="🔄 Konfigürasyonu Yenile", command=self.main_window.reload_config)
        file_menu.add_command(label="💾 Konfigürasyonu Kaydet", command=self.main_window.config_manager.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Çıkış", command=self.root.quit)
        
        # Cihaz menüsü
        device_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Cihaz", menu=device_menu)
        device_menu.add_command(label="➕ Cihaz Ekle", command=lambda: self.main_window.device_panel.add_device())
        device_menu.add_command(label="🔍 Ağ Taraması", command=self.main_window.scan_network)
        device_menu.add_separator()
        device_menu.add_command(label="🔗 Tüm Cihazlara Bağlan", command=self.main_window.connect_all_devices)
        device_menu.add_command(label="🔄 Verileri Yenile", command=self.main_window.refresh_data)
        device_menu.add_separator()
        device_menu.add_command(label="🧪 Bağlantı Testi", command=self.main_window.test_all_connections)
        
        # AARO API menüsü
        api_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🌐 AARO API", menu=api_menu)
        api_menu.add_command(label="🔑 Token Al", command=self.get_api_token)
        api_menu.add_command(label="📤 Giriş-Çıkış Verilerini Gönder", command=self.send_attendance_data)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🛠️ Araçlar", menu=tools_menu)
        tools_menu.add_command(label="⚙️ Ayarlar", command=self.main_window.show_settings)
        tools_menu.add_command(label="📋 Log Görüntüle", command=self.main_window.show_logs)
        tools_menu.add_separator()
        tools_menu.add_command(label="🧹 Verileri Temizle", command=self.main_window.clear_data)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Yardım", menu=help_menu)
        help_menu.add_command(label="📖 Kullanım Kılavuzu", command=self.main_window.show_help)
        help_menu.add_command(label="ℹ️ Hakkında", command=self.main_window.show_about)
    
    def get_api_token(self):
        """API token al"""
        from tkinter import messagebox
        import threading
        
        def token_thread():
            try:
                token = self.main_window.api_manager.get_token()
                if token:
                    self.main_window.root.after(0, lambda: messagebox.showinfo("Token Alma", "✅ API token başarıyla alındı!"))
                else:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Token Alma", "❌ API token alınamadı. Ayarları kontrol edin."))
            except Exception as e:
                self.main_window.root.after(0, lambda: messagebox.showerror("Token Alma", f"❌ Hata: {str(e)}"))
        
        threading.Thread(target=token_thread, daemon=True).start()
    
    def send_attendance_data(self):
        """Giriş-çıkış verilerini gönder"""
        from tkinter import messagebox
        import threading
        
        def send_thread():
            try:
                # Formatlanmış verileri direk al (device_manager'dan)
                formatted_data = self.main_window.device_manager.get_formatted_attendance()
                
                if not formatted_data:
                    self.main_window.root.after(0, lambda: messagebox.showwarning("Veri Gönderimi", "⚠️ Gönderilecek veri bulunamadı."))
                    return
                
                # Ek bilgileri temizle (API'ye gönderilmemesi için)
                clean_formatted_data = []
                for att in formatted_data:
                    clean_att = {k: v for k, v in att.items() if not k.startswith('_')}
                    clean_formatted_data.append(clean_att)
                
                # API'ye gönder
                result = self.main_window.api_manager.send_attendance_data(clean_formatted_data)
                
                if result['success']:
                    self.main_window.root.after(0, lambda: messagebox.showinfo("Veri Gönderimi", f"✅ {len(clean_formatted_data)} kayıt başarıyla gönderildi!"))
                else:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Veri Gönderimi", f"❌ Gönderim hatası: {result['message']}"))
                    
            except Exception as e:
                self.main_window.root.after(0, lambda: messagebox.showerror("Veri Gönderimi", f"❌ Hata: {str(e)}"))
        
        threading.Thread(target=send_thread, daemon=True).start()
