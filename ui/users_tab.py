"""
AARO ERP - PDKS Kullanıcılar Sekmesi
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.device_manager import DeviceManager
from ui.dialogs import UserDialog, BulkUserDialog
import csv

class UsersTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.device_manager = main_window.device_manager
        self.config_manager = main_window.config_manager
        
        self.setup_ui()
        self.setup_context_menu()
        self.users_data = []
    
    def setup_ui(self):
        """UI'yi oluştur"""
        # Üst panel - Butonlar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sol taraf butonları
        left_btn_frame = ttk.Frame(top_frame)
        left_btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_btn_frame, text="➕ Kullanıcı Ekle", command=self.add_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="📥 Toplu Ekle", command=self.bulk_add_users).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="📤 CSV'den İçe Aktar", command=self.import_from_csv).pack(side=tk.LEFT, padx=(0, 5))
        
        # Sağ taraf butonları
        right_btn_frame = ttk.Frame(top_frame)
        right_btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_btn_frame, text="📊 CSV'ye Aktar", command=self.export_to_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_btn_frame, text="🔄 Yenile", command=self.refresh_users).pack(side=tk.LEFT)
        
        # Ana frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Kullanıcılar tree
        self.users_tree = ttk.Treeview(main_frame, columns=("uid", "name", "privilege", "device"), show="headings")
        self.users_tree.heading("uid", text="Kullanıcı ID")
        self.users_tree.heading("name", text="Ad Soyad")
        self.users_tree.heading("privilege", text="Yetki")
        self.users_tree.heading("device", text="Cihaz")
        
        self.users_tree.column("uid", width=100)
        self.users_tree.column("name", width=200)
        self.users_tree.column("privilege", width=100)
        self.users_tree.column("device", width=200)
        
        # Scrollbar
        users_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        # Pack
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_context_menu(self):
        """Sağ tık menüsünü ayarla"""
        self.context_menu = tk.Menu(self.main_window.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Düzenle", command=self.edit_user)
        self.context_menu.add_command(label="🗑️ Sil", command=self.delete_user)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Kopyala", command=self.copy_user)
        self.context_menu.add_command(label="ℹ️ Detayları Göster", command=self.show_user_details)
        
        # Sağ tık olayını bağla
        self.users_tree.bind("<Button-3>", self.show_context_menu)
        
        # Çift tık için düzenleme
        self.users_tree.bind("<Double-1>", lambda e: self.edit_user())
    
    def show_context_menu(self, event):
        """Sağ tık menüsünü göster"""
        # Tıklanan öğeyi seç
        item = self.users_tree.identify_row(event.y)
        if item:
            self.users_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def refresh_users(self):
        """Kullanıcıları yenile"""
        # Mevcut verileri temizle
        self.clear_users()
        
        # Tüm cihazlardan kullanıcıları al
        all_users = self.device_manager.get_all_users()
        
        # Tree'ye ekle
        for user in all_users:
            privilege_text = DeviceManager.get_privilege_text(user['privilege'])
            user_data = {
                'uid': user['uid'],
                'name': user['name'],
                'privilege_text': privilege_text,
                'device_name': user['device_name']
            }
            self.users_data.append(user_data)
            
            self.users_tree.insert("", tk.END, values=(
                user['uid'], 
                user['name'], 
                privilege_text, 
                user['device_name']
            ))
    
    def clear_users(self):
        """Kullanıcıları temizle"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        self.users_data = []
    
    def get_all_users(self):
        """Tüm kullanıcı verilerini al"""
        return self.users_data
    
    def add_user(self):
        """Yeni kullanıcı ekle"""
        devices = self.config_manager.get_devices()
        if not devices:
            messagebox.showwarning("Uyarı", "Önce en az bir cihaz eklemelisiniz.")
            return
        
        dialog = UserDialog(self.main_window.root, "Kullanıcı Ekle", devices)
        if dialog.result:
            self.create_user_on_device(dialog.result)
    
    def edit_user(self):
        """Seçili kullanıcıyı düzenle"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek istediğiniz kullanıcıyı seçin.")
            return
        
        item = self.users_tree.item(selection[0])
        user_data = {
            'uid': item['values'][0],
            'name': item['values'][1],
            'privilege_text': item['values'][2],
            'device_name': item['values'][3]
        }
        
        devices = self.config_manager.get_devices()
        dialog = UserDialog(self.main_window.root, "Kullanıcı Düzenle", devices, user_data)
        if dialog.result:
            self.update_user_on_device(user_data['uid'], dialog.result)
    
    def delete_user(self):
        """Seçili kullanıcıyı sil"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz kullanıcıyı seçin.")
            return
        
        item = self.users_tree.item(selection[0])
        user_name = item['values'][1]
        user_uid = item['values'][0]
        
        if messagebox.askyesno("Onay", f"'{user_name}' kullanıcısını silmek istediğinizden emin misiniz?"):
            self.delete_user_from_device(user_uid)
    
    def copy_user(self):
        """Seçili kullanıcıyı kopyala"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen kopyalamak istediğiniz kullanıcıyı seçin.")
            return
        
        item = self.users_tree.item(selection[0])
        user_data = {
            'uid': '',  # Yeni UID verilecek
            'name': item['values'][1] + " (Kopya)",
            'privilege_text': item['values'][2],
            'device_name': item['values'][3]
        }
        
        devices = self.config_manager.get_devices()
        dialog = UserDialog(self.main_window.root, "Kullanıcı Kopyala", devices, user_data)
        if dialog.result:
            self.create_user_on_device(dialog.result)
    
    def show_user_details(self):
        """Seçili kullanıcının detaylarını göster"""
        selection = self.users_tree.selection()
        if not selection:
            return
        
        item = self.users_tree.item(selection[0])
        details = f"""Kullanıcı Detayları:

👤 Kullanıcı ID: {item['values'][0]}
📝 Ad Soyad: {item['values'][1]}
🔐 Yetki: {item['values'][2]}
🖥️ Cihaz: {item['values'][3]}"""
        
        messagebox.showinfo("Kullanıcı Detayları", details)
    
    def bulk_add_users(self):
        """Toplu kullanıcı ekleme"""
        devices = self.config_manager.get_devices()
        if not devices:
            messagebox.showwarning("Uyarı", "Önce en az bir cihaz eklemelisiniz.")
            return
        
        dialog = BulkUserDialog(self.main_window.root, devices)
        if dialog.result:
            self.create_bulk_users(dialog.result)
    
    def import_from_csv(self):
        """CSV dosyasından kullanıcı içe aktarma"""
        filename = filedialog.askopenfilename(
            title="CSV Dosyası Seç",
            filetypes=[("CSV dosyaları", "*.csv"), ("Tüm dosyalar", "*.*")]
        )
        
        if filename:
            try:
                users_to_import = []
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if 'uid' in row and 'name' in row:
                            users_to_import.append({
                                'uid': row.get('uid', ''),
                                'name': row.get('name', ''),
                                'privilege': int(row.get('privilege', 0)),
                                'device_id': int(row.get('device_id', 1))
                            })
                
                if users_to_import:
                    self.import_users_from_list(users_to_import)
                else:
                    messagebox.showwarning("Uyarı", "CSV dosyasında geçerli kullanıcı verisi bulunamadı.")
                    
            except Exception as e:
                messagebox.showerror("Hata", f"CSV dosyası okunamadı: {str(e)}")
    
    def export_to_csv(self):
        """Kullanıcıları CSV'ye aktar"""
        if not self.users_data:
            messagebox.showinfo("Bilgi", "Aktarılacak kullanıcı yok.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV dosyaları", "*.csv"), ("Tüm dosyalar", "*.*")],
            title="CSV Dosyası Kaydet"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['uid', 'name', 'privilege', 'device']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for user in self.users_data:
                        writer.writerow({
                            'uid': user['uid'],
                            'name': user['name'],
                            'privilege': user['privilege_text'],
                            'device': user['device_name']
                        })
                
                messagebox.showinfo("Başarılı", f"✅ Kullanıcılar CSV'ye aktarıldı: {filename}")
                
            except Exception as e:
                messagebox.showerror("Hata", f"❌ CSV dosyası kaydedilemedi: {str(e)}")
    
    def create_user_on_device(self, user_data):
        """Cihazda kullanıcı oluştur"""
        try:
            device_id = user_data['device_id']
            if device_id not in self.device_manager.connected_devices:
                messagebox.showerror("Hata", "Seçili cihaz bağlı değil!")
                return
            
            device = self.device_manager.connected_devices[device_id]['device']
            conn = self.device_manager.connected_devices[device_id]['connection']
            
            # Log ekle
            self.device_manager.add_connection_log(device['name'], "Kullanıcı Ekleme", "Deneniyor", 
                                                 f"Kullanıcı: {user_data['name']} (ID: {user_data['uid']})", "Kullanıcı İşlemleri")
            
            # Kullanıcı oluştur
            conn.set_user(
                uid=int(user_data['uid']),
                name=user_data['name'],
                privilege=user_data['privilege'],
                password=user_data.get('password', ''),
                group_id=user_data.get('group_id', ''),
                user_id=user_data.get('user_id', user_data['uid'])
            )
            
            # Başarı logu
            self.device_manager.add_connection_log(device['name'], "Kullanıcı Ekleme", "Başarılı", 
                                                 f"Kullanıcı '{user_data['name']}' başarıyla eklendi", "Kullanıcı İşlemleri")
            
            messagebox.showinfo("Başarılı", f"✅ Kullanıcı '{user_data['name']}' başarıyla eklendi.")
            self.refresh_users()
            
        except Exception as e:
            # Hata logu
            device = self.device_manager.connected_devices.get(device_id, {}).get('device', {})
            device_name = device.get('name', 'Bilinmeyen Cihaz')
            self.device_manager.add_connection_log(device_name, "Kullanıcı Ekleme", "Hata", 
                                                 f"Hata: {str(e)}", "Kullanıcı İşlemleri")
            messagebox.showerror("Hata", f"❌ Kullanıcı eklenemedi: {str(e)}")
    
    def update_user_on_device(self, old_uid, user_data):
        """Cihazda kullanıcıyı güncelle"""
        try:
            device_id = user_data['device_id']
            if device_id not in self.device_manager.connected_devices:
                messagebox.showerror("Hata", "Seçili cihaz bağlı değil!")
                return
            
            conn = self.device_manager.connected_devices[device_id]['connection']
            
            # Eski kullanıcıyı sil
            conn.delete_user(uid=int(old_uid))
            
            # Yeni kullanıcı oluştur
            conn.set_user(
                uid=int(user_data['uid']),
                name=user_data['name'],
                privilege=user_data['privilege'],
                password=user_data.get('password', ''),
                group_id=user_data.get('group_id', ''),
                user_id=user_data.get('user_id', user_data['uid'])
            )
            
            messagebox.showinfo("Başarılı", f"✅ Kullanıcı '{user_data['name']}' başarıyla güncellendi.")
            self.refresh_users()
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Kullanıcı güncellenemedi: {str(e)}")
    
    def delete_user_from_device(self, uid):
        """Cihazdan kullanıcıyı sil"""
        try:
            # Kullanıcının hangi cihazda olduğunu bul
            user_device_id = None
            for user in self.users_data:
                if str(user['uid']) == str(uid):
                    # Device name'den device_id'yi bul
                    for device in self.config_manager.get_devices():
                        if device['name'] == user['device_name']:
                            user_device_id = device['id']
                            break
                    break
            
            if user_device_id and user_device_id in self.device_manager.connected_devices:
                conn = self.device_manager.connected_devices[user_device_id]['connection']
                conn.delete_user(uid=int(uid))
                
                messagebox.showinfo("Başarılı", f"✅ Kullanıcı (ID: {uid}) başarıyla silindi.")
                self.refresh_users()
            else:
                messagebox.showerror("Hata", "Kullanıcının bulunduğu cihaz bağlı değil!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Kullanıcı silinemedi: {str(e)}")
    
    def create_bulk_users(self, users_list):
        """Toplu kullanıcı oluştur"""
        success_count = 0
        error_count = 0
        
        for user_data in users_list:
            try:
                device_id = user_data['device_id']
                if device_id in self.device_manager.connected_devices:
                    conn = self.device_manager.connected_devices[device_id]['connection']
                    
                    conn.set_user(
                        uid=int(user_data['uid']),
                        name=user_data['name'],
                        privilege=user_data['privilege'],
                        password=user_data.get('password', ''),
                        group_id=user_data.get('group_id', ''),
                        user_id=user_data.get('user_id', user_data['uid'])
                    )
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                self.main_window.logger.error(f"Toplu kullanıcı ekleme hatası: {str(e)}")
        
        messagebox.showinfo("Toplu Ekleme Sonucu", 
                           f"✅ Başarılı: {success_count}\n❌ Hatalı: {error_count}")
        self.refresh_users()
    
    def import_users_from_list(self, users_list):
        """Liste halindeki kullanıcıları içe aktar"""
        success_count = 0
        error_count = 0
        
        for user_data in users_list:
            try:
                device_id = user_data.get('device_id', 1)
                if device_id in self.device_manager.connected_devices:
                    conn = self.device_manager.connected_devices[device_id]['connection']
                    
                    conn.set_user(
                        uid=int(user_data['uid']),
                        name=user_data['name'],
                        privilege=user_data.get('privilege', 0),
                        password='',
                        group_id='',
                        user_id=user_data['uid']
                    )
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                self.main_window.logger.error(f"CSV içe aktarma hatası: {str(e)}")
        
        messagebox.showinfo("İçe Aktarma Sonucu", 
                           f"✅ Başarılı: {success_count}\n❌ Hatalı: {error_count}")
        self.refresh_users()
