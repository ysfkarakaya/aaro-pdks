"""
AARO ERP - PDKS AARO Personeller Sekmesi
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

class AAROPersonnelTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        
        self.setup_ui()
        self.personnel_data = []
        self.selected_personnel = []
    
    def setup_ui(self):
        """UI'yi oluştur"""
        # Üst panel - Butonlar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sol taraf butonları
        left_btn_frame = ttk.Frame(top_frame)
        left_btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_btn_frame, text="🔄 AARO'dan Çek", command=self.fetch_personnel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="➕ Seçilileri Cihaza Ekle", command=self.add_selected_to_device).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="🧹 Listeyi Temizle", command=self.clear_list).pack(side=tk.LEFT, padx=(0, 5))
        
        # Sağ taraf - Bilgi
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT)
        
        self.info_label = ttk.Label(right_frame, text="AARO'dan personel listesi çekmek için 'AARO'dan Çek' butonuna tıklayın")
        self.info_label.pack(side=tk.RIGHT)
        
        # Ana frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Personel listesi frame
        list_frame = ttk.LabelFrame(main_frame, text="📋 AARO Personel Listesi")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Personel tree
        self.personnel_tree = ttk.Treeview(list_frame, columns=("personnel_id", "name", "status"), show="headings", selectmode="extended")
        self.personnel_tree.heading("#0", text="")
        self.personnel_tree.heading("personnel_id", text="Personel ID")
        self.personnel_tree.heading("name", text="Ad Soyad")
        self.personnel_tree.heading("status", text="Durum")
        
        self.personnel_tree.column("personnel_id", width=100)
        self.personnel_tree.column("name", width=250)
        self.personnel_tree.column("status", width=150)
        
        # Scrollbar
        personnel_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.personnel_tree.yview)
        self.personnel_tree.configure(yscrollcommand=personnel_scrollbar.set)
        
        # Pack
        self.personnel_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        personnel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Cihaz seçimi frame
        device_frame = ttk.LabelFrame(main_frame, text="🖥️ Hedef Cihaz Seçimi")
        device_frame.pack(fill=tk.X)
        
        device_inner = ttk.Frame(device_frame)
        device_inner.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(device_inner, text="Cihaz:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_inner, textvariable=self.device_var, width=30)
        self.device_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cihaz listesini güncelle
        self.refresh_device_list()
        
        # Seçim bilgisi
        self.selection_label = ttk.Label(device_inner, text="Seçili personel: 0")
        self.selection_label.pack(side=tk.RIGHT)
        
        # Seçim değişikliği için event
        self.personnel_tree.bind("<<TreeviewSelect>>", self.on_selection_change)
    
    def refresh_device_list(self):
        """Cihaz listesini yenile"""
        devices = self.main_window.config_manager.get_devices()
        device_names = [device['name'] for device in devices]
        self.device_combo['values'] = device_names
        
        if device_names:
            self.device_combo.set(device_names[0])
    
    def fetch_personnel(self):
        """AARO'dan personel listesini çek"""
        # API etkin mi kontrol et
        api_settings = self.main_window.api_manager.get_api_settings()
        if not api_settings.get('enabled', False):
            messagebox.showwarning("Uyarı", "⚠️ API entegrasyonu devre dışı. Önce Ayarlar > API'den etkinleştirin.")
            return
        
        # Loading göster
        self.info_label.config(text="Token kontrol ediliyor...")
        
        # Thread'de çalıştır
        threading.Thread(target=self._fetch_personnel_thread, daemon=True).start()
    
    def _fetch_personnel_thread(self):
        """Personel çekme thread'i"""
        try:
            import requests
            
            # API ayarlarını al
            api_settings = self.main_window.api_manager.get_api_settings()
            personnel_url = api_settings.get('personnel_url', 'https://erp.aaro.com.tr/api/Personel')
            page_size = api_settings.get('personnel_page_size', 100)
            
            # Token kontrolü ve gerekirse yeni token alma
            self.root.after(0, lambda: self.info_label.config(text="Token kontrol ediliyor..."))
            
            if not self.main_window.api_manager.is_token_valid():
                self.root.after(0, lambda: self.info_label.config(text="Yeni token alınıyor..."))
                
                if not self.main_window.api_manager.get_token():
                    error_msg = "API token alınamadı. Kullanıcı adı ve şifre kontrol edin."
                    self.root.after(0, lambda: self._show_error(error_msg))
                    return
            
            # Token var, personel listesi çekiliyor
            self.root.after(0, lambda: self.info_label.config(text="AARO'dan personel listesi çekiliyor..."))
            
            # API isteği
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.main_window.api_manager.token}',
                'Cookie': 'Oturum=Grup=935&Sirket=0&Sube=0'
            }
            
            # Parametreler
            params = {
                'SayfaSatirSayisi': page_size
            }
            
            # Gönderilecek veriyi hazırla
            import json
            headers_json = json.dumps(headers, indent=2, ensure_ascii=False)
            params_json = json.dumps(params, indent=2, ensure_ascii=False)
            
            # Log ekle
            log_details = f"""AARO'dan personel listesi çekiliyor
URL: {personnel_url}
Sayfa boyutu: {page_size}

GÖNDERİLEN HEADERS:
{headers_json}

GÖNDERİLEN PARAMETRELER:
{params_json}"""
            
            self.main_window.api_manager.add_connection_log("Personel Listesi", "Deneniyor", log_details)
            
            response = requests.get(
                personnel_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                personnel_list = data.get('Model', [])
                
                # UI'yi güncelle
                self.root.after(0, lambda: self._update_personnel_list(personnel_list))
                
                # Log ekle
                log_details = f"""Personel listesi başarıyla çekildi
Toplam personel: {len(personnel_list)}

SUNUCU YANITI:
{response.text[:500]}..."""
                
                self.main_window.api_manager.add_connection_log("Personel Listesi", "Başarılı", log_details)
                
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.root.after(0, lambda: self._show_error(error_msg))
                
                # Hata logu
                self.main_window.api_manager.add_connection_log("Personel Listesi", "Hata", 
                                                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            error_msg = f"İstek hatası: {str(e)}"
            self.root.after(0, lambda: self._show_error(error_msg))
            
            # Hata logu
            self.main_window.api_manager.add_connection_log("Personel Listesi", "Hata", 
                                                          f"İstek hatası: {str(e)}")
    
    def _update_personnel_list(self, personnel_list):
        """Personel listesini güncelle"""
        # Mevcut listeyi temizle
        for item in self.personnel_tree.get_children():
            self.personnel_tree.delete(item)
        
        self.personnel_data = []
        
        # Yeni verileri ekle
        for person in personnel_list:
            personnel_id = person.get('PersonelID')
            name = person.get('PersonelAdiSoyadi', '')
            status = "Aktif" if person.get('Durum', False) else "Pasif"
            
            if personnel_id and name:
                self.personnel_tree.insert("", tk.END, values=(personnel_id, name, status))
                self.personnel_data.append({
                    'PersonelID': personnel_id,
                    'PersonelAdiSoyadi': name,
                    'Durum': person.get('Durum', False)
                })
        
        # Bilgi güncelle
        self.info_label.config(text=f"✅ {len(self.personnel_data)} personel listelendi")
    
    def _show_error(self, error_msg):
        """Hata göster"""
        self.info_label.config(text="❌ Personel listesi çekilemedi")
        messagebox.showerror("Hata", f"Personel listesi çekilemedi:\n{error_msg}")
    
    def on_selection_change(self, event):
        """Seçim değişikliği"""
        selected_items = self.personnel_tree.selection()
        self.selection_label.config(text=f"Seçili personel: {len(selected_items)}")
    
    def add_selected_to_device(self):
        """Seçili personelleri cihaza ekle"""
        selected_items = self.personnel_tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Uyarı", "⚠️ Lütfen eklemek istediğiniz personelleri seçin.")
            return
        
        device_name = self.device_var.get()
        if not device_name:
            messagebox.showwarning("Uyarı", "⚠️ Lütfen hedef cihazı seçin.")
            return
        
        # Cihazı bul
        devices = self.main_window.config_manager.get_devices()
        target_device = None
        for device in devices:
            if device['name'] == device_name:
                target_device = device
                break
        
        if not target_device:
            messagebox.showerror("Hata", "❌ Seçili cihaz bulunamadı.")
            return
        
        # Seçili personelleri al
        selected_personnel = []
        for item in selected_items:
            values = self.personnel_tree.item(item)['values']
            personnel_id = values[0]
            name = values[1]
            
            selected_personnel.append({
                'personnel_id': personnel_id,
                'name': name
            })
        
        # Onay iste
        if not messagebox.askyesno("Onay", 
                                  f"🤔 {len(selected_personnel)} personeli '{device_name}' cihazına eklemek istediğinizden emin misiniz?\n\n"
                                  f"Personeller cihazda Kullanıcı ID olarak PersonelID ile kaydedilecek."):
            return
        
        # Thread'de ekle
        threading.Thread(target=self._add_personnel_to_device_thread, 
                        args=(selected_personnel, target_device), daemon=True).start()
    
    def _add_personnel_to_device_thread(self, personnel_list, device):
        """Personelleri cihaza ekleme thread'i"""
        try:
            # Cihaza bağlan
            device_conn = self.main_window.device_manager.get_device_connection(device['id'])
            if not device_conn:
                self.root.after(0, lambda: messagebox.showerror("Hata", "❌ Cihaza bağlanılamadı."))
                return
            
            success_count = 0
            error_count = 0
            
            for person in personnel_list:
                try:
                    # Kullanıcıyı cihaza ekle
                    device_conn.set_user(
                        uid=int(person['personnel_id']),
                        name=person['name'],
                        privilege=0,  # Normal kullanıcı
                        password='',
                        group_id='',
                        user_id=str(person['personnel_id'])
                    )
                    
                    success_count += 1
                    
                    # Log ekle
                    self.main_window.device_manager.add_connection_log(
                        device['name'], 
                        "Kullanıcı Ekleme", 
                        "Başarılı", 
                        f"AARO Personel eklendi: {person['name']} (ID: {person['personnel_id']})",
                        "Kullanıcı İşlemleri"
                    )
                    
                except Exception as e:
                    error_count += 1
                    
                    # Hata logu
                    self.main_window.device_manager.add_connection_log(
                        device['name'], 
                        "Kullanıcı Ekleme", 
                        "Hata", 
                        f"AARO Personel eklenemedi: {person['name']} (ID: {person['personnel_id']}) - {str(e)}",
                        "Kullanıcı İşlemleri"
                    )
            
            # Sonuç mesajı
            result_msg = f"✅ {success_count} personel başarıyla eklendi"
            if error_count > 0:
                result_msg += f"\n❌ {error_count} personel eklenemedi"
            
            self.root.after(0, lambda: messagebox.showinfo("Sonuç", result_msg))
            
            # Kullanıcılar sekmesini yenile
            self.root.after(0, self.main_window.users_tab.refresh_users)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Hata", f"❌ İşlem hatası: {str(e)}"))
    
    def clear_list(self):
        """Listeyi temizle"""
        if messagebox.askyesno("Onay", "🧹 Personel listesini temizlemek istediğinizden emin misiniz?"):
            for item in self.personnel_tree.get_children():
                self.personnel_tree.delete(item)
            
            self.personnel_data = []
            self.info_label.config(text="Liste temizlendi")
            self.selection_label.config(text="Seçili personel: 0")
    
    @property
    def root(self):
        """Root window'a erişim"""
        return self.main_window.root
