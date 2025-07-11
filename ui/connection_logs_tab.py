"""
AARO ERP - PDKS Bağlantı Logları Sekmesi
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

class ConnectionLogsTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        
        self.setup_ui()
        self.logs_data = []
    
    def setup_ui(self):
        """UI'yi oluştur"""
        # Üst panel - Butonlar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sol taraf butonları
        left_btn_frame = ttk.Frame(top_frame)
        left_btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_btn_frame, text="🧹 Temizle", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_btn_frame, text="📊 CSV'ye Aktar", command=self.export_to_csv).pack(side=tk.LEFT, padx=(0, 5))
        
        # Sağ taraf - Filtreler
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text="🔍 Filtre:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(right_frame, textvariable=self.filter_var, 
                                   values=['Tümü', 'Bağlantı', 'Kullanıcı İşlemleri', 'Veri Çekme', 'Hata'], 
                                   width=15)
        filter_combo.pack(side=tk.LEFT, padx=(0, 5))
        filter_combo.set('Tümü')
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
        # Ana frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Bağlantı logları tree
        self.logs_tree = ttk.Treeview(main_frame, columns=("timestamp", "device", "operation", "status", "details"), show="headings")
        self.logs_tree.heading("timestamp", text="Zaman")
        self.logs_tree.heading("device", text="Cihaz")
        self.logs_tree.heading("operation", text="İşlem")
        self.logs_tree.heading("status", text="Durum")
        self.logs_tree.heading("details", text="Detaylar")
        
        self.logs_tree.column("timestamp", width=150)
        self.logs_tree.column("device", width=150)
        self.logs_tree.column("operation", width=120)
        self.logs_tree.column("status", width=80)
        self.logs_tree.column("details", width=300)
        
        # Scrollbar
        logs_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)
        
        # Pack
        self.logs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Çift tık için detay gösterme
        self.logs_tree.bind("<Double-1>", self.show_log_details)
    
    def add_log(self, device_name, operation, status, details, log_type="Genel"):
        """Yeni log ekle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Durum ikonları
        status_icon = "✅" if status == "Başarılı" else "❌" if status == "Hata" else "⚠️"
        status_text = f"{status_icon} {status}"
        
        log_entry = {
            'timestamp': timestamp,
            'device': device_name,
            'operation': operation,
            'status': status,
            'details': details,
            'type': log_type
        }
        
        self.logs_data.append(log_entry)
        
        # Tree'ye ekle (en üste)
        self.logs_tree.insert("", 0, values=(
            timestamp,
            device_name,
            operation,
            status_text,
            details
        ))
        
        # Maksimum 1000 log tut
        if len(self.logs_data) > 1000:
            self.logs_data = self.logs_data[-1000:]
            # Tree'den de eski kayıtları sil
            children = self.logs_tree.get_children()
            if len(children) > 1000:
                for item in children[1000:]:
                    self.logs_tree.delete(item)
        
        # En üste scroll
        if self.logs_tree.get_children():
            self.logs_tree.see(self.logs_tree.get_children()[0])
    
    def clear_logs(self):
        """Logları temizle"""
        if messagebox.askyesno("Onay", "Tüm bağlantı loglarını temizlemek istediğinizden emin misiniz?"):
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)
            self.logs_data = []
    
    def export_to_csv(self):
        """Logları CSV'ye aktar"""
        if not self.logs_data:
            messagebox.showinfo("Bilgi", "Aktarılacak log yok.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV dosyaları", "*.csv"), ("Tüm dosyalar", "*.*")],
            title="Bağlantı Logları CSV Kaydet"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'device', 'operation', 'status', 'details', 'type']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for log in reversed(self.logs_data):  # En yeniden en eskiye
                        writer.writerow(log)
                
                messagebox.showinfo("Başarılı", f"✅ Bağlantı logları CSV'ye aktarıldı: {filename}")
                
            except Exception as e:
                messagebox.showerror("Hata", f"❌ CSV dosyası kaydedilemedi: {str(e)}")
    
    def apply_filter(self, event=None):
        """Filtre uygula"""
        filter_value = self.filter_var.get()
        
        # Tüm öğeleri temizle
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Filtrelenmiş verileri göster
        for log in reversed(self.logs_data):  # En yeniden en eskiye
            show_log = False
            
            if filter_value == "Tümü":
                show_log = True
            elif filter_value == "Bağlantı" and log['type'] in ['Bağlantı', 'Genel']:
                show_log = True
            elif filter_value == "Kullanıcı İşlemleri" and log['type'] == 'Kullanıcı İşlemleri':
                show_log = True
            elif filter_value == "Veri Çekme" and log['type'] == 'Veri Çekme':
                show_log = True
            elif filter_value == "Hata" and log['status'] == 'Hata':
                show_log = True
            
            if show_log:
                status_icon = "✅" if log['status'] == "Başarılı" else "❌" if log['status'] == "Hata" else "⚠️"
                status_text = f"{status_icon} {log['status']}"
                
                self.logs_tree.insert("", tk.END, values=(
                    log['timestamp'],
                    log['device'],
                    log['operation'],
                    status_text,
                    log['details']
                ))
    
    def show_log_details(self, event):
        """Log detaylarını göster"""
        selection = self.logs_tree.selection()
        if not selection:
            return
        
        item = self.logs_tree.item(selection[0])
        values = item['values']
        
        # Detaylı log dialog'u oluştur
        self.create_log_detail_dialog(values)
    
    def create_log_detail_dialog(self, values):
        """Log detay dialog'u oluştur"""
        dialog = tk.Toplevel(self)
        dialog.title("📋 Log Detayları")
        dialog.geometry("600x400")
        dialog.transient(self.main_window.root)
        # Modal olmayacak
        
        # Merkeze yerleştir
        x = self.main_window.root.winfo_rootx() + 100
        y = self.main_window.root.winfo_rooty() + 100
        dialog.geometry(f"600x400+{x}+{y}")
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="📋 Bağlantı Log Detayları", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Detay metni
        detail_frame = ttk.Frame(main_frame)
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        detail_text = tk.Text(detail_frame, wrap=tk.WORD, font=('Consolas', 9))
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=detail_text.yview)
        detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Detay içeriği
        details_content = f"""🕐 Zaman: {values[0]}
🖥️ Cihaz: {values[1]}
⚙️ İşlem: {values[2]}
📊 Durum: {values[3]}

📝 Detaylar:
{values[4]}"""
        
        detail_text.insert(tk.END, details_content)
        detail_text.config(state=tk.DISABLED)  # Sadece okunabilir
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        def copy_details():
            dialog.clipboard_clear()
            dialog.clipboard_append(details_content)
            messagebox.showinfo("Kopyalandı", "✅ Log detayları panoya kopyalandı.")
        
        ttk.Button(btn_frame, text="📋 Kopyala", command=copy_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="❌ Kapat", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def get_logs_count(self):
        """Log sayısını al"""
        return len(self.logs_data)
