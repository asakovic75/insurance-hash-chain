import hashlib
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class InsuranceContract:
    def __init__(self, fio, policy_number, phone, object_insured, risk, 
                 start_date, end_date, premium, coverage, agent, previous_hash='0', timestamp=None):
        self.fio = fio
        self.policy_number = policy_number
        self.phone = phone
        self.object_insured = object_insured
        self.risk = risk
        self.start_date = start_date
        self.end_date = end_date
        self.premium = float(premium)
        self.coverage = float(coverage)
        self.agent = agent
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.previous_hash = previous_hash
        self.current_hash = self.calculate_hash()

    def calculate_hash(self):
        premium_str = f"{self.premium:.2f}"
        coverage_str = f"{self.coverage:.2f}"
        block_string = (f"{self.fio}{self.policy_number}{self.phone}"
                        f"{self.object_insured}{self.risk}{self.start_date}{self.end_date}"
                        f"{premium_str}{coverage_str}{self.agent}{self.timestamp}"
                        f"{self.previous_hash}")
        return hashlib.sha256(block_string.encode()).hexdigest()

class HashChainDB:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return InsuranceContract("Genesis", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", 0, 0, "N/A", "0", timestamp="2025-01-01 00:00:00")

    def get_last_contract(self):
        return self.chain[-1]
    
    def is_policy_number_unique(self, policy_number):
        return not any(contract.policy_number == policy_number for contract in self.chain[1:])

    def add_contract(self, *args, **kwargs):
        previous_hash = self.get_last_contract().current_hash
        new_contract = InsuranceContract(*args, **kwargs, previous_hash=previous_hash)
        self.chain.append(new_contract)
        return new_contract

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_contract = self.chain[i]
            previous_contract = self.chain[i - 1]
            if current_contract.current_hash != current_contract.calculate_hash():
                return False, i
            if current_contract.previous_hash != previous_contract.current_hash:
                return False, i
        return True, -1

class App:
    def __init__(self, root):
        self.db = HashChainDB()
        self.filename = "insurance_ledger.json"
        self.is_dirty = False
        self.root = root
        self.root.title("Система страхования")
        self.root.geometry("1920x1080")
        self.root.minsize(1500, 800)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        self.SIDEBAR_BG = "#F0F4F8"
        self.MAIN_BG = "#FFFFFF"
        self.TEXT_COLOR = "#333333"
        self.HEADER_COLOR = "#00796B"
        self.ACCENT_COLOR = "#00897B"
        self.BUTTON_TEXT_COLOR = "#FFFFFF"
        
        self.root.configure(bg=self.MAIN_BG)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        sidebar_frame = tk.Frame(root, bg=self.SIDEBAR_BG, width=400, padx=25, pady=25)
        sidebar_frame.grid(row=0, column=0, sticky="nsw")
        sidebar_frame.grid_propagate(False)
        sidebar_frame.grid_rowconfigure(0, weight=1)

        input_fields_frame = tk.Frame(sidebar_frame, bg=self.SIDEBAR_BG)
        input_fields_frame.grid(row=0, column=0, sticky="nsew")

        header_label = tk.Label(input_fields_frame, text="Новый договор", font=("Arial", 24, "bold"), bg=self.SIDEBAR_BG, fg=self.HEADER_COLOR)
        header_label.pack(pady=(10, 20), anchor="w")

        self.entries = {}
        fields = {
            "fio": "ФИО Клиента:", "policy_number": "Номер полиса:", "phone": "Телефон клиента:",
            "object_insured": "Объект страхования:", "risk": "Страховой риск:", "start_date": "Дата начала (ДД.ММ.ГГГГ):",
            "end_date": "Дата окончания (ДД.ММ.ГГГГ):", "premium": "Стоимость, руб.:",
            "coverage": "Сумма покрытия, руб.:", "agent": "Агент:"
        }
        
        object_values = [
            'Квартира', 'Дом', 'Дача', 'Коммерческая недвижимость', 'Земельный участок',
            'Автомобиль легковой', 'Автомобиль грузовой', 'Мотоцикл', 'Спецтехника',
            'Смартфон', 'Ноутбук', 'Телевизор', 'Фотоаппарат', 'Бытовая техника',
            'Туристическая поездка', 'Авиабилеты', 'Круиз', 'Багаж',
            'Жизнь и здоровье', 'От несчастных случаев', 'ДМС',
            'Гражданская ответственность', 'Профессиональная ответственность',
            'Драгоценности', 'Произведение искусства', 'Антиквариат'
        ]
        risk_values = [
            'Затопление', 'Пожар', 'Кража со взломом', 'Противоправные действия третьих лиц', 'Стихийное бедствие',
            'ДТП по своей вине', 'ДТП не по своей вине', 'Угон', 'Хищение',
            'Механическое повреждение', 'Поломка', 'Производственный брак', 'Гарантийный случай',
            'Утеря багажа', 'Задержка рейса', 'Отмена поездки', 'Медицинские расходы за рубежом', 'Невыезд',
            'Травма', 'Инвалидность', 'Временная нетрудоспособность',
            'Причинение вреда соседям', 'Врачебная ошибка', 'Ошибка юриста'
        ]
        agent_values = ['Иванов И.И.', 'Петров П.П.', 'Сидорова А.А.', 'Кузнецов М.В.']
        
        for key, text in fields.items():
            label = tk.Label(input_fields_frame, text=text, font=("Arial", 11), bg=self.SIDEBAR_BG, fg=self.TEXT_COLOR)
            label.pack(fill='x', pady=(8, 2), anchor="w")
            
            if key == "object_insured": entry = ttk.Combobox(input_fields_frame, font=("Arial", 10), values=object_values)
            elif key == "risk": entry = ttk.Combobox(input_fields_frame, font=("Arial", 10), values=risk_values)
            elif key == "agent": entry = ttk.Combobox(input_fields_frame, font=("Arial", 10), values=agent_values)
            else: entry = ttk.Entry(input_fields_frame, font=("Arial", 10))
            
            entry.pack(fill='x')
            self.entries[key] = entry
        
        button_container = tk.Frame(sidebar_frame, bg=self.SIDEBAR_BG)
        button_container.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        button_container.columnconfigure((0,1), weight=1)

        self.style.configure("Accent.TButton", font=("Arial", 12, "bold"), padding=12, borderwidth=0, background=self.ACCENT_COLOR, foreground=self.BUTTON_TEXT_COLOR)
        self.style.map("Accent.TButton", background=[("active", self.HEADER_COLOR)])
        
        ttk.Button(button_container, text="Добавить договор", command=self.add_contract_gui, style="Accent.TButton").grid(row=0, column=0, columnspan=2, sticky='ew', ipady=5, pady=(0, 10))
        ttk.Button(button_container, text="Сохранить", command=self.save_file, style="Accent.TButton").grid(row=1, column=0, sticky='ew', padx=(0,5), ipady=5)
        ttk.Button(button_container, text="Проверить целостность", command=self.validate_chain_gui, style="Accent.TButton").grid(row=1, column=1, sticky='ew', padx=(5,0), ipady=5)
        
        content_frame = tk.Frame(root, bg=self.MAIN_BG)
        content_frame.grid(row=0, column=1, sticky="nsew")
        self.tree = self.create_treeview(content_frame)
        self.tree.bind("<Double-1>", self.open_tamper_window)

        self.status_bar = tk.Label(root, text="Загрузка...", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#263238", fg="#ECEFF1", font=("Arial", 9))
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='we')
        
        self.load_from_filepath(self.filename, is_initial_load=True)

    def create_treeview(self, parent):
        tree_frame = tk.Frame(parent, bg=self.MAIN_BG)
        tree_frame.pack(padx=20, pady=20, fill="both", expand=True)
        self.style.configure("Treeview.Heading", font=("Arial", 11, "bold"), padding=10)
        self.style.configure("Treeview", rowheight=30, font=("Arial", 10), fieldbackground=self.MAIN_BG)
        self.style.map("Treeview", background=[('selected', self.ACCENT_COLOR)])
        
        columns = ('id', 'fio', 'policy', 'phone', 'object', 'risk', 'period', 'premium', 'coverage', 'agent', 'curr_hash')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        headings = {
            'id':'ID', 'fio':'ФИО Клиента', 'policy':'Номер полиса', 'phone':'Телефон', 'object':'Объект страхования', 'risk':'Страховой риск', 
            'period':'Время действия', 'premium':'Стоимость', 'coverage':'Сумма покрытия', 'agent': 'Агент', 'curr_hash':'Текущий хэш'
        }
        widths = {
            'id':50, 'fio':250, 'policy':150, 'phone': 120, 'object':200, 'risk':200, 
            'period':180, 'premium':150, 'coverage':150, 'agent': 150, 'curr_hash':250
        }
        
        for col, text in headings.items():
            tree.heading(col, text=text)
            tree.column(col, width=widths[col], anchor="w")
        
        tree.tag_configure('oddrow', background='#F0F4F8')
        tree.tag_configure('evenrow', background='#FFFFFF')
        tree.tag_configure('tampered', background='#FFCDD2', foreground='#B71C1C', font=("Arial", 10, "bold"))

        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)

        return tree
    
    def open_tamper_window(self, event=None):
        selected_item_id = self.tree.focus()
        if not selected_item_id: return
        item_values = self.tree.item(selected_item_id, "values")
        contract_id = int(item_values[0])
        contract = self.db.chain[contract_id]
        
        tamper_window = tk.Toplevel(self.root)
        tamper_window.title("Режим взлома (демонстрация)")
        tamper_window.geometry("600x550")
        tamper_window.transient(self.root)
        tamper_window.grab_set()
        
        frame = tk.Frame(tamper_window, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Измените любые данные, чтобы нарушить целостность", font=("Arial", 11)).pack(pady=(0,15))

        tamper_entries = {}
        contract_data = vars(contract)
        label_map = {
            "fio": "ФИО Клиента:", "policy_number": "Номер полиса:", "phone": "Телефон:", "object_insured": "Объект страхования:", 
            "risk": "Страховой риск:", "start_date": "Дата начала:", "end_date": "Дата окончания:", 
            "premium": "Стоимость полиса:", "coverage": "Сумма покрытия:", "agent": "Агент:"
        }
        
        for key, text in label_map.items():
            row = tk.Frame(frame)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=text, font=("Arial", 10, "bold"), width=22, anchor="w").pack(side="left")
            entry = ttk.Entry(row, font=("Arial", 10))
            entry.insert(0, contract_data.get(key, ""))
            entry.pack(side="left", fill="x", expand=True)
            tamper_entries[key] = entry
            
        def save_tampered_data():
            for key, entry in tamper_entries.items():
                new_value = entry.get()
                try:
                    if key in ["premium", "coverage"]: 
                        new_value = float(new_value) if new_value else 0.0
                except ValueError: 
                    new_value = getattr(contract, key)
                setattr(contract, key, new_value)
            
            self.is_dirty = True
            self.update_table()
            tamper_window.destroy()
            messagebox.showwarning("Внимание", "Данные были изменены!")
            
        ttk.Button(frame, text="Сохранить изменения (взлом)", command=save_tampered_data, style="Accent.TButton").pack(pady=20, ipady=4)

    def add_contract_gui(self):
        try:
            data = {key: entry.get() for key, entry in self.entries.items()}
            if not data["fio"] or not data["policy_number"] or not data["agent"]:
                messagebox.showerror("Ошибка ввода", "ФИО, Номер полиса и Агент являются обязательными полями!")
                return
            if not self.db.is_policy_number_unique(data["policy_number"]):
                messagebox.showerror("Ошибка ввода", f"Номер полиса '{data['policy_number']}' уже существует!")
                return
                
            premium = float(data.get("premium") or 0)
            coverage = float(data.get("coverage") or 0)
            
            self.db.add_contract(
                data["fio"], data["policy_number"], data["phone"], data["object_insured"], 
                data["risk"], data["start_date"], data["end_date"], premium, coverage, data["agent"]
            )
            
            self.is_dirty = True
            self.update_table()
            for entry in self.entries.values():
                if isinstance(entry, ttk.Entry): entry.delete(0, 'end')
                else: entry.set('')
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Стоимость и Сумма покрытия должны быть числами!")

    def validate_chain_gui(self):
        is_valid, error_index = self.db.is_chain_valid()
        if is_valid:
            messagebox.showinfo("Проверка успешна", "ЦЕЛОСТНОСТЬ ПОДТВЕРЖДЕНА! Все записи в базе данных верны.", icon='info')
        else:
            self.show_tamper_analysis(error_index)
            self.update_table()
            
    def show_tamper_analysis(self, error_index):
        tampered_contract = self.db.chain[error_index]
        recalculated_hash = tampered_contract.calculate_hash()
        stored_hash = tampered_contract.current_hash
        
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Анализ нарушения целостности")
        analysis_window.geometry("1000x300")
        analysis_window.transient(self.root)
        analysis_window.grab_set()
        
        frame = tk.Frame(analysis_window, padx=25, pady=25)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text=f"НАРУШЕНИЕ ЦЕЛОСТНОСТИ в записи с ID {error_index}!", font=("Arial", 16, "bold"), fg="#B71C1C").pack(pady=(0, 20), anchor="w")
        
        tk.Label(frame, text="Сравнение хэшей:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        
        hash_frame = tk.Frame(frame)
        hash_frame.pack(fill='x', pady=5)
        
        tk.Label(hash_frame, text="Сохраненный хэш:", font=("Arial", 11)).grid(row=0, column=0, sticky='w')
        tk.Label(hash_frame, text=stored_hash, font=("Courier", 11), fg="green").grid(row=0, column=1, sticky='w', padx=10)
        
        tk.Label(hash_frame, text="Рассчитанный хэш:", font=("Arial", 11, "bold"), fg="red").grid(row=1, column=0, sticky='w', pady=(5,0))
        tk.Label(hash_frame, text=recalculated_hash, font=("Courier", 11, "bold"), fg="red").grid(row=1, column=1, sticky='w', padx=10, pady=(5,0))

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        is_chain_valid, invalid_index = self.db.is_chain_valid()
        for i, contract in enumerate(self.db.chain[1:]):
            current_id = i + 1
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            if not is_chain_valid and current_id >= invalid_index:
                tag = 'tampered'
            
            period = f"{contract.start_date} - {contract.end_date}"
            
            self.tree.insert('', 'end', values=(
                current_id, contract.fio, contract.policy_number, contract.phone, contract.object_insured, 
                contract.risk, period, f"{contract.premium:.2f}", f"{contract.coverage:.2f}",
                contract.agent, contract.current_hash
            ), tags=(tag,))
        
        count = len(self.db.chain) - 1
        filename_text = os.path.basename(self.filename) if self.filename else "Новый файл"
        status_text = f"Всего договоров: {count} | Файл: {filename_text}"
        if self.is_dirty: status_text += " (есть несохраненные изменения)"
        self.status_bar.config(text=status_text)

    def save_to_filepath(self, filepath):
        data_to_save = [vars(contract) for contract in self.db.chain[1:]]
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            self.filename = filepath
            self.is_dirty = False
            self.update_table()
            messagebox.showinfo("Сохранение", f"Данные успешно сохранены в файл:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def save_file(self):
        if self.filename:
            self.save_to_filepath(self.filename)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Сохранить файл как..."
        )
        if filepath:
            self.save_to_filepath(filepath)
    
    def load_from_filepath(self, filepath, is_initial_load=False):
        if not os.path.exists(filepath):
            if not is_initial_load:
                messagebox.showerror("Ошибка", f"Файл не найден: {filepath}")
            self.update_table()
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self.db.chain = [self.db.create_genesis_block()]
            
            for item in loaded_data:
                recreated_contract = InsuranceContract(
                    item.get('fio', ''), item.get('policy_number', ''), item.get('phone', ''), 
                    item.get('object_insured', ''), item.get('risk', ''), item.get('start_date', ''), 
                    item.get('end_date', ''), item.get('premium', 0.0), item.get('coverage', 0.0), item.get('agent', 'N/A'),
                    previous_hash=item.get('previous_hash'), timestamp=item.get('timestamp')
                )
                recreated_contract.current_hash = item.get('current_hash') 
                self.db.chain.append(recreated_contract)
            
            self.filename = filepath
            self.is_dirty = False
            self.update_table()
        except Exception as e:
            if not is_initial_load:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные из файла: {e}")
            else:
                self.update_table()

    def on_closing(self):
        if self.is_dirty:
            response = messagebox.askyesnocancel("Выход", "У вас есть несохраненные изменения. Сохранить их перед выходом?")
            if response is True: 
                self.save_file()
                if not self.is_dirty: self.root.destroy()
            elif response is False: self.root.destroy()
        else:
            self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()