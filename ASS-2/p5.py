import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class ContactManagerApp:
    def __init__(self, root, db_config):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("900x600")
        self.db_config = db_config
        
        self.email_regex = re.compile(r'^[a-zA-Z0-9+._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.selected_contact_id = None
        
        self.setup_database()
        self.create_widgets()
        self.load_contacts()

    def setup_database(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Contact (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    category VARCHAR(50),
                    notes TEXT,
                    INDEX idx_search (name, email, phone)
                ) ENGINE=InnoDB;
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            sys.exit(1)

    def create_widgets(self):
        form_frame = ttk.LabelFrame(self.root, text=" Contact Details ", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_name = ttk.Entry(form_frame, width=25)
        self.ent_name.grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ent_email = ttk.Entry(form_frame, width=25)
        self.ent_email.grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ent_phone = ttk.Entry(form_frame, width=25)
        self.ent_phone.grid(row=2, column=1, pady=5)

        ttk.Label(form_frame, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cmb_category = ttk.Combobox(form_frame, values=["Faculty", "Student", "Staff", "Other"], width=23, state="readonly")
        self.cmb_category.grid(row=3, column=1, pady=5)
        self.cmb_category.current(0)

        ttk.Label(form_frame, text="Notes:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.txt_notes = tk.Text(form_frame, width=20, height=5, wrap=tk.WORD)
        self.txt_notes.grid(row=4, column=1, pady=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="Add", command=self.add_contact).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_contact).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_contact).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=2)

        display_frame = ttk.LabelFrame(self.root, text=" Contacts Directory ", padding=10)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = ttk.Frame(display_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.ent_search = ttk.Entry(search_frame, width=30)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        self.ent_search.bind("<KeyRelease>", self.search_contacts)

        columns = ("id", "name", "email", "phone", "category")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("category", text="Category")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=130)
        self.tree.column("email", width=160)
        self.tree.column("phone", width=100)
        self.tree.column("category", width=90)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_contact_select)

    def clear_form(self):
        self.selected_contact_id = None
        self.ent_name.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.cmb_category.current(0)
        self.txt_notes.delete("1.0", tk.END)

    def validate_inputs(self, name, email, phone):
        if not name or not email or not phone:
            messagebox.showwarning("Validation Error", "Name, Email, and Phone fields are required.")
            return False
        if not self.email_regex.match(email):
            messagebox.showwarning("Validation Error", "Invalid email address format.")
            return False
        return True

    def load_contacts(self, query_filter=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            if query_filter:
                sql = """SELECT id, name, email, phone, category FROM Contact 
                         WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s 
                         ORDER BY name ASC"""
                pattern = f"%{query_filter}%"
                cursor.execute(sql, (pattern, pattern, pattern))
            else:
                sql = "SELECT id, name, email, phone, category FROM Contact ORDER BY name ASC"
                cursor.execute(sql)
                
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
                
            cursor.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load records: {e}")

    def search_contacts(self, event):
        self.load_contacts(self.ent_search.get().strip())

    def on_contact_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        values = self.tree.item(selected_item, "values")
        self.selected_contact_id = int(values[0])
        
        self.ent_name.delete(0, tk.END)
        self.ent_name.insert(0, values[1])
        
        self.ent_email.delete(0, tk.END)
        self.ent_email.insert(0, values[2])
        
        self.ent_phone.delete(0, tk.END)
        self.ent_phone.insert(0, values[3])
        
        self.cmb_category.set(values[4])
        
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT notes FROM Contact WHERE id = %s", (self.selected_contact_id,))
            row = cursor.fetchone()
            self.txt_notes.delete("1.0", tk.END)
            if row and row[0]:
                self.txt_notes.insert("1.0", row[0])
            cursor.close()
            conn.close()
        except Error:
            pass

    def add_contact(self):
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        category = self.cmb_category.get()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        if not self.validate_inputs(name, email, phone):
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            sql = "INSERT INTO Contact (name, email, phone, category, notes) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, email, phone, category, notes))
            conn.commit()
            cursor.close()
            conn.close()
            
            self.clear_form()
            self.load_contacts()
            messagebox.showinfo("Success", "Record inserted and visible in contact list.")
        except Error as e:
            if e.errno == 1062:
                messagebox.showerror("Error", "Duplicate email address encountered.")
            else:
                messagebox.showerror("Database Error", f"Operation failed: {e}")

    def update_contact(self):
        if not self.selected_contact_id:
            messagebox.showwarning("Selection Error", "Please select a contact from the list to update.")
            return

        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        category = self.cmb_category.get()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        if not self.validate_inputs(name, email, phone):
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            sql = "UPDATE Contact SET name=%s, email=%s, phone=%s, category=%s, notes=%s WHERE id=%s"
            cursor.execute(sql, (name, email, phone, category, notes, self.selected_contact_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            self.clear_form()
            self.load_contacts()
            messagebox.showinfo("Success", "Record updated successfully.")
        except Error as e:
            if e.errno == 1062:
                messagebox.showerror("Error", "Duplicate email address encountered.")
            else:
                messagebox.showerror("Database Error", f"Operation failed: {e}")

    def delete_contact(self):
        if not self.selected_contact_id:
          messagebox.showwarning("Selection Error", "Please select a contact from the list to delete.")
          return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
          return
          try:
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        sql = "DELETE FROM Contact WHERE id = %s"
        cursor.execute(sql, (self.selected_contact_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.clear_form()
        self.load_contacts()
        messagebox.showinfo("Success", "Record deleted successfully.")
  except Error as e:
    messagebox.showerror("Database Error", f"Operation failed: {e}")
    if name == "main":
    db_configuration = {
    'host': 'localhost',
    'database': 'directory_db',
    'user': 'root',
    'password': 'password'
    }
root_window = tk.Tk()
app = ContactManagerApp(root_window, db_configuration)
root_window.mainloop()
