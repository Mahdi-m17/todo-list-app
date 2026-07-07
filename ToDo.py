import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📋 To-Do List Manager")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        
        # Data file
        self.data_file = "todo_data.json"
        self.tasks = []
        
        # Load existing tasks
        self.load_tasks()
        
        # Setup UI
        self.setup_ui()
        
        # Refresh task list
        self.refresh_task_list()
    
    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with icon
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        header_label = tk.Label(
            header_frame, 
            text="📋 My To-Do List", 
            font=('Segoe UI', 22, 'bold'),
            fg='#2c3e50'
        )
        header_label.pack(side=tk.LEFT)
        
        # Stats label
        self.stats_label = tk.Label(
            main_frame,
            text="",
            font=('Segoe UI', 10),
            fg='#7f8c8d'
        )
        self.stats_label.pack(pady=(0, 10))
        
        # Input frame (Add task)
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.task_entry = tk.Entry(
            input_frame,
            font=('Segoe UI', 11),
            relief=tk.GROOVE,
            bd=2
        )
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        add_btn = tk.Button(
            input_frame,
            text="➕ Add Task",
            font=('Segoe UI', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2',
            command=self.add_task
        )
        add_btn.pack(side=tk.RIGHT)
        
        # Priority selection frame
        priority_frame = tk.Frame(main_frame)
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            priority_frame,
            text="Priority:",
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.priority_var = tk.StringVar(value="High")
        priorities = ["High", "Medium", "Low"]
        self.priority_dropdown = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=priorities,
            state='readonly',
            width=15
        )
        self.priority_dropdown.pack(side=tk.LEFT)
        
        # Spacer
        tk.Label(priority_frame, text="   Filter:").pack(side=tk.LEFT, padx=(20, 10))
        
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All", "High", "Medium", "Low", "Completed", "Pending"]
        filter_dropdown = ttk.Combobox(
            priority_frame,
            textvariable=self.filter_var,
            values=filter_options,
            state='readonly',
            width=15
        )
        filter_dropdown.pack(side=tk.LEFT)
        filter_dropdown.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Task list frame with scrollbar
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview for tasks
        columns = ('Status', 'Task', 'Date', 'Priority')
        self.task_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Define headings with proper column configuration
        self.task_tree.heading('Status', text='Status')
        self.task_tree.heading('Task', text='Task')
        self.task_tree.heading('Date', text='Date Added')
        self.task_tree.heading('Priority', text='Priority')
        
        # Define column widths using the column method
        self.task_tree.column('Status', width=80, anchor='center')
        self.task_tree.column('Task', width=300, anchor='w')
        self.task_tree.column('Date', width=130, anchor='center')
        self.task_tree.column('Priority', width=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        btn_config = {
            'font': ('Segoe UI', 10, 'bold'),
            'padx': 15,
            'pady': 8,
            'relief': tk.RAISED,
            'bd': 2,
            'cursor': 'hand2'
        }
        
        complete_btn = tk.Button(
            button_frame,
            text="✅ Mark Complete",
            bg='#2ecc71',
            fg='white',
            command=self.complete_task,
            **btn_config
        )
        complete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = tk.Button(
            button_frame,
            text="🗑️ Delete Task",
            bg='#e74c3c',
            fg='white',
            command=self.delete_task,
            **btn_config
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🧹 Clear All",
            bg='#95a5a6',
            fg='white',
            command=self.clear_all,
            **btn_config
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind double-click to toggle status
        self.task_tree.bind('<Double-Button-1>', lambda e: self.toggle_task_status())
        self.task_tree.bind('<Delete>', lambda e: self.delete_task())
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return
        
        # Get selected priority
        priority = self.priority_var.get()
        
        task = {
            'id': len(self.tasks) + 1,
            'text': task_text,
            'completed': False,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'priority': priority
        }
        
        self.tasks.append(task)
        self.save_tasks()
        self.task_entry.delete(0, tk.END)
        self.refresh_task_list()
        messagebox.showinfo("Success", f"Task added: {task_text}")
    
    def toggle_task_status(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task!")
            return
        
        item = selected[0]
        values = self.task_tree.item(item, 'values')
        
        # Find and toggle the task
        for task in self.tasks:
            if task['text'] == values[1] and task['date'] == values[2]:
                task['completed'] = not task['completed']
                break
        
        self.save_tasks()
        self.refresh_task_list()
    
    def complete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task!")
            return
        
        for item in selected:
            values = self.task_tree.item(item, 'values')
            for task in self.tasks:
                if task['text'] == values[1] and task['date'] == values[2]:
                    if not task['completed']:
                        task['completed'] = True
                        break
        
        self.save_tasks()
        self.refresh_task_list()
        messagebox.showinfo("Success", "Task(s) marked as complete!")
    
    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task!")
            return
        
        if messagebox.askyesno("Confirm Delete", "Delete selected task(s)?"):
            tasks_to_delete = []
            for item in selected:
                values = self.task_tree.item(item, 'values')
                for task in self.tasks:
                    if task['text'] == values[1] and task['date'] == values[2]:
                        tasks_to_delete.append(task)
                        break
            
            for task in tasks_to_delete:
                self.tasks.remove(task)
            
            self.save_tasks()
            self.refresh_task_list()
            messagebox.showinfo("Success", "Task(s) deleted!")
    
    def clear_all(self):
        if not self.tasks:
            messagebox.showinfo("Info", "No tasks to clear!")
            return
        
        if messagebox.askyesno("Confirm Clear All", "Delete ALL tasks?"):
            self.tasks = []
            self.save_tasks()
            self.refresh_task_list()
            messagebox.showinfo("Success", "All tasks cleared!")
    
    def refresh_task_list(self):
        # Clear current treeview
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Get filter
        filter_option = self.filter_var.get()
        
        # Sort tasks: incomplete first, then by date
        sorted_tasks = sorted(
            self.tasks,
            key=lambda x: (x['completed'], x['date'])
        )
        
        # Display tasks
        completed_count = 0
        for task in sorted_tasks:
            # Apply filters
            if filter_option == "Completed" and not task['completed']:
                continue
            if filter_option == "Pending" and task['completed']:
                continue
            if filter_option not in ["All", "Completed", "Pending"] and task['priority'] != filter_option:
                continue
            
            # Status emoji
            status = "✅" if task['completed'] else "⬜"
            if task['completed']:
                completed_count += 1
            
            # Insert into treeview
            item = self.task_tree.insert(
                '',
                tk.END,
                values=(status, task['text'], task['date'], task['priority'])
            )
            
            # Color code based on priority and status
            if task['completed']:
                self.task_tree.tag_configure('completed', foreground='gray')
                self.task_tree.item(item, tags=('completed',))
            elif task['priority'] == 'High':
                self.task_tree.tag_configure('high', foreground='#c0392b')
                self.task_tree.item(item, tags=('high',))
            elif task['priority'] == 'Medium':
                self.task_tree.tag_configure('medium', foreground='#f39c12')
                self.task_tree.item(item, tags=('medium',))
            elif task['priority'] == 'Low':
                self.task_tree.tag_configure('low', foreground='#27ae60')
                self.task_tree.item(item, tags=('low',))
        
        # Update stats
        total = len(self.tasks)
        pending = total - completed_count
        self.stats_label.config(
            text=f"📊 Total: {total}  |  ✅ Completed: {completed_count}  |  ⬜ Pending: {pending}"
        )
    
    def save_tasks(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {e}")
    
    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.tasks = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load tasks: {e}")
                self.tasks = []

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()