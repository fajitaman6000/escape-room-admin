import tkinter as tk
from tkinter import ttk
import time

class AdminInterfaceBuilder:
    def __init__(self, app):
        self.app = app
        self.connected_kiosks = {}  # Stores UI elements for each kiosk
        self.selected_kiosk = None
        self.stats_elements = {
            'time_label': None,
            'hints_label': None,
            'msg_entry': None,
            'send_btn': None
        }
        self.setup_ui()
        
    def setup_ui(self):
        self.main_container = tk.Frame(self.app.root)
        self.main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        left_frame = tk.Frame(self.main_container)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.kiosk_frame = tk.LabelFrame(left_frame, text="Online Kiosk Computers", padx=10, pady=5)
        self.kiosk_frame.pack(fill='both', expand=True)
        
        self.stats_frame = tk.LabelFrame(left_frame, text="No Room Selected", padx=10, pady=5)
        self.stats_frame.pack(fill='both', expand=True, pady=10)
        
    def update_stats_timer(self):
        if self.selected_kiosk and self.selected_kiosk in self.app.kiosk_tracker.kiosk_stats:
            self.update_stats_display(self.selected_kiosk)
        self.app.root.after(1000, self.update_stats_timer)
        
    def setup_stats_panel(self, computer_name):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats_container = tk.Frame(self.stats_frame)
        stats_container.pack(fill='x', expand=True, padx=10, pady=5)
        
        self.stats_elements['time_label'] = tk.Label(stats_container, justify='left')
        self.stats_elements['time_label'].pack(anchor='w')
        
        self.stats_elements['hints_label'] = tk.Label(stats_container, justify='left')
        self.stats_elements['hints_label'].pack(anchor='w')
        
        hint_frame = tk.Frame(self.stats_frame)
        hint_frame.pack(fill='x', pady=10, padx=10)
        
        tk.Label(hint_frame, text="Custom text hint:").pack(anchor='w')
        self.stats_elements['msg_entry'] = tk.Entry(hint_frame, width=40)
        self.stats_elements['msg_entry'].pack(fill='x', pady=5)
        
        self.stats_elements['send_btn'] = tk.Button(hint_frame, text="Send",
            command=lambda: self.send_hint(computer_name))
        self.stats_elements['send_btn'].pack(pady=5)
        
    def add_kiosk_to_ui(self, computer_name):
        current_time = time.time()
        
        if computer_name in self.connected_kiosks:
            self.connected_kiosks[computer_name]['last_seen'] = current_time
            return
            
        frame = tk.Frame(self.kiosk_frame)
        frame.pack(fill='x', pady=2)
        
        if computer_name in self.app.kiosk_tracker.kiosk_assignments:
            room_num = self.app.kiosk_tracker.kiosk_assignments[computer_name]
            room_name = self.app.rooms[room_num]
            name_label = tk.Label(frame, 
                text=room_name,
                font=('Arial', 12, 'bold'))
            name_label.pack(side='left', padx=5)
            computer_label = tk.Label(frame,
                text=f"({computer_name})",
                font=('Arial', 12, 'italic'))
            computer_label.pack(side='left')
        else:
            name_label = tk.Label(frame, 
                text="Unassigned",
                font=('Arial', 12, 'bold'))
            name_label.pack(side='left', padx=5)
            computer_label = tk.Label(frame,
                text=f"({computer_name})",
                font=('Arial', 12, 'italic'))
            computer_label.pack(side='left')
        
        def click_handler(cn=computer_name):
            self.select_kiosk(cn)
        
        frame.bind('<Button-1>', lambda e: click_handler())
        name_label.bind('<Button-1>', lambda e: click_handler())
        computer_label.bind('<Button-1>', lambda e: click_handler())
        
        room_var = tk.StringVar()
        dropdown = ttk.Combobox(frame, textvariable=room_var, 
            values=list(self.app.rooms.values()), state='readonly')
        dropdown.pack(side='left', padx=5)
        
        help_label = tk.Label(frame, text="", font=('Arial', 14, 'bold'), fg='red')
        help_label.pack(side='left', padx=5)
        
        def assign_room():
            if not room_var.get():
                return
            selected_room = next(num for num, name in self.app.rooms.items() 
                              if name == room_var.get())
            self.app.kiosk_tracker.assign_kiosk_to_room(computer_name, selected_room)
            dropdown.set('')
            name_label.config(text=self.app.rooms[selected_room])
        
        assign_btn = tk.Button(frame, text="Assign Room", command=assign_room)
        assign_btn.pack(side='left', padx=5)
        
        self.connected_kiosks[computer_name] = {
            'frame': frame,
            'help_label': help_label,
            'dropdown': dropdown,
            'assign_btn': assign_btn,
            'last_seen': current_time,
            'name_label': name_label,
            'computer_label': computer_label
        }
        
        if computer_name == self.selected_kiosk:
            self.select_kiosk(computer_name)
            
    def update_kiosk_display(self, computer_name):
        if computer_name in self.connected_kiosks:
            if computer_name in self.app.kiosk_tracker.kiosk_assignments:
                room_num = self.app.kiosk_tracker.kiosk_assignments[computer_name]
                self.connected_kiosks[computer_name]['name_label'].config(
                    text=self.app.rooms[room_num]
                )
                
                if computer_name == self.selected_kiosk:
                    self.stats_frame.configure(
                        text=f"{self.app.rooms[room_num]} ({computer_name})"
                    )
                    if self.stats_elements['send_btn']:
                        self.stats_elements['send_btn'].config(state='normal')
                    
    def mark_help_requested(self, computer_name):
        if computer_name in self.connected_kiosks:
            self.connected_kiosks[computer_name]['help_label'].config(
                text="HINT REQUESTED",
                fg='red',
                font=('Arial', 14, 'bold')
            )
            
    def remove_kiosk(self, computer_name):
        if computer_name in self.connected_kiosks:
            self.connected_kiosks[computer_name]['frame'].destroy()
            del self.connected_kiosks[computer_name]
            
            if computer_name in self.app.kiosk_tracker.kiosk_assignments:
                del self.app.kiosk_tracker.kiosk_assignments[computer_name]
            if computer_name in self.app.kiosk_tracker.kiosk_stats:
                del self.app.kiosk_tracker.kiosk_stats[computer_name]
            if computer_name in self.app.kiosk_tracker.assigned_rooms:
                del self.app.kiosk_tracker.assigned_rooms[computer_name]
            if computer_name in self.app.kiosk_tracker.help_requested:
                self.app.kiosk_tracker.help_requested.remove(computer_name)
            
            if self.selected_kiosk == computer_name:
                self.selected_kiosk = None
                self.stats_frame.configure(text="No Room Selected")
                for widget in self.stats_frame.winfo_children():
                    widget.destroy()
                self.stats_elements = {key: None for key in self.stats_elements}
                
    def select_kiosk(self, computer_name):
        self.selected_kiosk = computer_name
        
        if computer_name in self.app.kiosk_tracker.kiosk_assignments:
            room_num = self.app.kiosk_tracker.kiosk_assignments[computer_name]
            room_name = self.app.rooms[room_num]
            title = f"{room_name} ({computer_name})"
        else:
            title = f"Unassigned ({computer_name})"
        self.stats_frame.configure(text=title)
        
        # Update highlighting
        for cn, data in self.connected_kiosks.items():
            if cn == computer_name:
                data['frame'].configure(bg='lightblue')
                for widget in data['frame'].winfo_children():
                    if not isinstance(widget, ttk.Combobox):
                        widget.configure(bg='lightblue')
            else:
                data['frame'].configure(bg='SystemButtonFace')
                for widget in data['frame'].winfo_children():
                    if not isinstance(widget, ttk.Combobox):
                        widget.configure(bg='SystemButtonFace')
        
        self.setup_stats_panel(computer_name)
        self.update_stats_display(computer_name)
        
    def update_stats_display(self, computer_name, setup=False):
        if setup or not self.stats_elements['time_label']:
            self.setup_stats_panel(computer_name)
        
        if computer_name in self.app.kiosk_tracker.kiosk_stats:
            stats = self.app.kiosk_tracker.kiosk_stats[computer_name]
            minutes = stats.get('room_time', 0) // 60
            seconds = stats.get('room_time', 0) % 60
            
            self.stats_elements['time_label'].config(
                text=f"Time in room: {minutes}m {seconds}s"
            )
            self.stats_elements['hints_label'].config(
                text=f"Hints requested: {stats.get('total_hints', 0)}"
            )
            
            if computer_name in self.app.kiosk_tracker.kiosk_assignments:
                self.stats_elements['send_btn'].config(state='normal')
            else:
                self.stats_elements['send_btn'].config(state='disabled')
                
    def send_hint(self, computer_name):
        if not self.stats_elements['msg_entry'] or not computer_name in self.app.kiosk_tracker.kiosk_assignments:
            return
            
        message_text = self.stats_elements['msg_entry'].get()
        if not message_text:
            return
            
        room_number = self.app.kiosk_tracker.kiosk_assignments[computer_name]
        self.app.network_handler.send_hint(room_number, message_text)
        
        if computer_name in self.app.kiosk_tracker.help_requested:
            self.app.kiosk_tracker.help_requested.remove(computer_name)
            if computer_name in self.connected_kiosks:
                self.connected_kiosks[computer_name]['help_label'].config(text="")
        
        self.stats_elements['msg_entry'].delete(0, 'end')