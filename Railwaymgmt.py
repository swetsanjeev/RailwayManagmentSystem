import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import pandas as pd
import customtkinter

# ------------------ CONFIG ------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "password"  # ← Replace with your MySQL password
DB_NAME = "railway_mgmt"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# ------------------ DB CONNECT ------------------
def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# ------------------ MAIN GUI APP ------------------
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")

class RailwayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Railway Management System")
        self.root.geometry("1000x500")

        self.table_name = tk.StringVar()
        self.search_col = tk.StringVar()
        self.search_val = tk.StringVar()

        self.root.config(bg="#D6EAF8")

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root, bg="#D6EAF8")
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Table:", bg="#D6EAF8").grid(row=1, column=0, padx=5)
        self.tables = ["Station", "Train", "Route", "Passenger", "Ticket", "Payment"]
        self.table_dropdown = ttk.Combobox(top_frame, textvariable=self.table_name, values=self.tables, state="readonly")
        self.table_dropdown.grid(row=1, column=1, padx=5)
        self.table_dropdown.current(0)

        tk.Label(top_frame, text="🚆 Railway Management System",
                 font=("Georgia", 16, "bold"),
                 fg="#154360", bg="#D6EAF8").grid(row=0, column=0, columnspan=8, pady=(10, 15))

        self.create_ctk_button(top_frame, "📄 Show", self.show_table).grid(row=1, column=2, padx=5)
        self.create_ctk_button(top_frame, "➕ Insert", lambda: self.data_form("insert")).grid(row=1, column=3, padx=5)
        self.create_ctk_button(top_frame, "✏️ Update", lambda: self.data_form("update")).grid(row=1, column=4, padx=5)
        self.create_ctk_button(top_frame, "➖ Delete", self.delete_data).grid(row=1, column=5, padx=5)
        self.create_ctk_button(top_frame, "📤 CSV", lambda: self.export_data("csv")).grid(row=1, column=6, padx=5)
        self.create_ctk_button(top_frame, "📊 Excel", lambda: self.export_data("excel")).grid(row=1, column=7, padx=5)

        # Search
        search_frame = tk.Frame(self.root, bg="#D6EAF8")
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search Column:", bg="#D6EAF8").grid(row=0, column=0)
        tk.Entry(search_frame, textvariable=self.search_col).grid(row=0, column=1)
        tk.Label(search_frame, text="Value:", bg="#D6EAF8").grid(row=0, column=2)
        tk.Entry(search_frame, textvariable=self.search_val).grid(row=0, column=3)
        self.create_ctk_button(search_frame, "🔎 Search", self.search_data).grid(row=0, column=4, padx=10)

        # Custom SQL
        sql_frame = tk.Frame(self.root, bg="#D6EAF8")
        sql_frame.pack(pady=5)

        tk.Label(sql_frame, text="Custom SQL:", bg="#D6EAF8").grid(row=0, column=0)
        self.sql_entry = tk.Entry(sql_frame, width=80)
        self.sql_entry.grid(row=0, column=1)
        self.create_ctk_button(sql_frame, "▶️ Run", self.run_custom_sql).grid(row=0, column=2)

        # Treeview
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill="both", expand=True)

    def create_ctk_button(self, parent, text, command):
        return customtkinter.CTkButton(master=parent,
                                       text=text,
                                       command=command,
                                       fg_color="#154360",
                                       text_color="white",
                                       font=("Arial", 10, "bold"),
                                       corner_radius=10,
                                       width=80,
                                       height=28)




    def show_table(self):
        table = self.table_name.get()
        db = connect_db()
        cursor = db.cursor()

        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = columns
            self.tree["show"] = "headings"

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)

            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    def data_form(self, action):
        table = self.table_name.get()
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        db.close()

        form = tk.Toplevel(self.root)
        form.title(f"{action.capitalize()} - {table}")

        entries = {}
        for i, col in enumerate(columns):
            tk.Label(form, text=col).grid(row=i, column=0, padx=5, pady=5)
            entries[col] = tk.Entry(form, width=30)
            entries[col].grid(row=i, column=1, padx=5, pady=5)

        def save():
            data = [entries[col].get() for col in columns]
            db = connect_db()
            cursor = db.cursor()
            try:
                if action == "insert":
                    cursor.execute(f"INSERT INTO {table} VALUES ({','.join(['%s']*len(columns))})", data)
                else:
                    pk = columns[0]
                    cursor.execute(f"UPDATE {table} SET {', '.join([f'{col}=%s' for col in columns[1:]])} WHERE {pk} = %s",
                                   data[1:] + [data[0]])
                db.commit()
                messagebox.showinfo("Success", f"{action.capitalize()} successful")
                form.destroy()
                self.show_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()

        tk.Button(form, text="Save", command=save).grid(row=len(columns), columnspan=2, pady=10)

    def delete_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a row", "No row selected.")
            return

        row = self.tree.item(selected[0], "values")
        table = self.table_name.get()
        pk = self.tree["columns"][0]
        pk_val = row[0]

        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute(f"DELETE FROM {table} WHERE {pk} = %s", (pk_val,))
            db.commit()
            messagebox.showinfo("Deleted", f"Record deleted from {table}")
            self.show_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

    def export_data(self, mode):
        table = self.table_name.get()
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        # Set file extension and file types based on the mode
        if mode == "csv":
            file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        elif mode == "excel":
            file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if not file:
            return

        try:
            # Export to selected file type
            if mode == "csv":
                df.to_csv(file, index=False)
            elif mode == "excel":
                df.to_excel(file, index=False, engine='openpyxl')
            messagebox.showinfo("Exported", f"Data exported to {file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def run_custom_sql(self):
        query = self.sql_entry.get().strip()
        if not query.lower().startswith("select"):
            messagebox.showwarning("Only SELECT", "Only SELECT queries are allowed.")
            return

        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = columns
            self.tree["show"] = "headings"

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)

            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
        finally:
            db.close()

    def search_data(self):
        col = self.search_col.get().strip()
        val = self.search_val.get().strip()
        table = self.table_name.get()

        if not col or not val:
            messagebox.showwarning("Input needed", "Please enter both column and value.")
            return

        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE {col} LIKE %s", (f"%{val}%",))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = columns
            self.tree["show"] = "headings"

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)

            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Search error", str(e))
        finally:
            db.close()

# ------------------ LOGIN SCREEN ------------------
def show_login():
    login = tk.Tk()
    login.title("Admin Login")
    login.geometry("300x180")

    tk.Label(login, text="Username").pack(pady=5)
    username_entry = tk.Entry(login)
    username_entry.pack()

    tk.Label(login, text="Password").pack(pady=5)
    password_entry = tk.Entry(login, show="*")
    password_entry.pack()

    def attempt_login():
        user = username_entry.get()
        pwd = password_entry.get()
        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            login.destroy()
            main = tk.Tk()
            app = RailwayApp(main)
            main.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    tk.Button(login, text="Login", command=attempt_login).pack(pady=10)
    login.mainloop()

# ------------------ MAIN ------------------
if __name__ == "__main__":
    show_login()
