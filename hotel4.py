import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt
import requests

API_KEY = "da575ceee90ba971c7efb46ce0ce95a4"


class HotelApp:
    def __init__(self):
        self.conn = sqlite3.connect("hotel_final.db")
        self.cursor = self.conn.cursor()

    # =========================
    def create_database(self):
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY,
            room_number INTEGER,
            price REAL
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY,
            client_id INTEGER,
            room_id INTEGER,
            check_in TEXT,
            check_out TEXT
        )""")

        self.conn.commit()

    # =========================
    def login_gui(self):
        root = tk.Tk()
        root.title("Login")
        root.geometry("300x200")
        root.configure(bg="#ffc0cb")

        tk.Label(root, text="Lietotājs", bg="#ffc0cb").pack()
        username = tk.Entry(root)
        username.pack()

        tk.Label(root, text="Parole", bg="#ffc0cb").pack()
        password = tk.Entry(root, show="*")
        password.pack()

        def register():
            pw_hash = bcrypt.hashpw(password.get().encode(), bcrypt.gensalt()).decode()
            try:
                self.cursor.execute("INSERT INTO users VALUES(NULL,?,?)",
                                    (username.get(), pw_hash))
                self.conn.commit()
                messagebox.showinfo("OK", "Reģistrēts!")
            except:
                messagebox.showerror("Kļūda", "Lietotājs eksistē!")

        def login():
            self.cursor.execute("SELECT password FROM users WHERE username=?",
                                (username.get(),))
            res = self.cursor.fetchone()

            if res and bcrypt.checkpw(password.get().encode(), res[0].encode()):
                root.destroy()
                self.main_menu()
            else:
                messagebox.showerror("Kļūda", "Nepareizi dati!")

        tk.Button(root, text="Login", bg="#ff69b4", command=login).pack(pady=5)
        tk.Button(root, text="Reģistrēties", bg="#ff69b4", command=register).pack()

        root.mainloop()

    # =========================
    def main_menu(self):
        menu = tk.Tk()
        menu.title("Viesnīca")
        menu.geometry("350x500")
        menu.configure(bg="#ffc0cb")

        def btn(text, cmd):
            tk.Button(menu, text=text, bg="#ff69b4", fg="white",
                      width=25, command=cmd).pack(pady=5)

        btn("Pievienot klientu", self.add_client)
        btn("Pievienot numuru", self.add_room)
        btn("Veikt rezervāciju", self.make_reservation)
        btn("Parādīt klientus", self.show_clients)
        btn("Parādīt numurus", self.show_rooms)
        btn("Parādīt rezervācijas", self.show_reservations)
        btn("Dzēst klientu", self.delete_client)
        btn("Dzēst numuru", self.delete_room)
        btn("Dzēst rezervāciju", self.delete_reservation)
        btn("Laika prognoze", self.weather)
        btn("Iziet", menu.destroy)

        menu.mainloop()

    # =========================
    # CLIENTS
    # =========================
    def add_client(self):
        win = tk.Toplevel()
        win.configure(bg="#ffc0cb")

        tk.Label(win, text="Vārds", bg="#ffc0cb").pack()
        name = tk.Entry(win)
        name.pack()

        tk.Label(win, text="Telefons", bg="#ffc0cb").pack()
        phone = tk.Entry(win)
        phone.pack()

        def save():
            self.cursor.execute("INSERT INTO clients VALUES(NULL,?,?)",
                                (name.get(), phone.get()))
            self.conn.commit()
            messagebox.showinfo("OK", "Pievienots!")
            win.destroy()

        tk.Button(win, text="Saglabāt", bg="#ff69b4", command=save).pack()

    def show_clients(self):
        win = tk.Toplevel()
        tree = ttk.Treeview(win, columns=("ID", "Vārds", "Telefons"), show="headings")

        for col in ("ID", "Vārds", "Telefons"):
            tree.heading(col, text=col)

        self.cursor.execute("SELECT * FROM clients")
        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True)

    def delete_client(self):
        win = tk.Toplevel()

        tree = ttk.Treeview(win, columns=("ID", "Vārds"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Vārds", text="Vārds")

        self.cursor.execute("SELECT id, name FROM clients")
        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

        tree.pack()

        tk.Label(win, text="Ievadi ID").pack()
        entry = tk.Entry(win)
        entry.pack()

        def delete():
            self.cursor.execute("DELETE FROM clients WHERE id=?", (entry.get(),))
            self.conn.commit()
            messagebox.showinfo("OK", "Dzēsts!")
            win.destroy()

        tk.Button(win, text="Dzēst", bg="#ff69b4", command=delete).pack()

    # =========================
    # ROOMS
    # =========================
    def add_room(self):
        win = tk.Toplevel()
        win.configure(bg="#ffc0cb")

        tk.Label(win, text="Numurs", bg="#ffc0cb").pack()
        num = tk.Entry(win)
        num.pack()

        tk.Label(win, text="Cena", bg="#ffc0cb").pack()
        price = tk.Entry(win)
        price.pack()

        def save():
            self.cursor.execute("INSERT INTO rooms VALUES(NULL,?,?)",
                                (num.get(), price.get()))
            self.conn.commit()
            messagebox.showinfo("OK", "Pievienots!")
            win.destroy()

        tk.Button(win, text="Saglabāt", bg="#ff69b4", command=save).pack()

    def show_rooms(self):
        win = tk.Toplevel()
        tree = ttk.Treeview(win, columns=("ID", "Numurs", "Cena"), show="headings")

        for col in ("ID", "Numurs", "Cena"):
            tree.heading(col, text=col)

        self.cursor.execute("SELECT * FROM rooms")
        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True)

    def delete_room(self):
        win = tk.Toplevel()

        tree = ttk.Treeview(win, columns=("ID", "Numurs"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Numurs", text="Numurs")

        self.cursor.execute("SELECT id, room_number FROM rooms")
        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

        tree.pack()

        tk.Label(win, text="Ievadi ID").pack()
        entry = tk.Entry(win)
        entry.pack()

        def delete():
            self.cursor.execute("DELETE FROM rooms WHERE id=?", (entry.get(),))
            self.conn.commit()
            messagebox.showinfo("OK", "Dzēsts!")
            win.destroy()

        tk.Button(win, text="Dzēst", bg="#ff69b4", command=delete).pack()

    # =========================
    # RESERVATIONS
    # =========================
    def make_reservation(self):
        win = tk.Toplevel()
        win.geometry("600x400")

        tk.Label(win, text="Klienti").pack()
        client_tree = ttk.Treeview(win, columns=("ID", "Vārds"), show="headings")
        client_tree.heading("ID", text="ID")
        client_tree.heading("Vārds", text="Vārds")
        client_tree.pack()

        self.cursor.execute("SELECT id, name FROM clients")
        for row in self.cursor.fetchall():
            client_tree.insert("", "end", values=row)

        tk.Label(win, text="Numuri").pack()
        room_tree = ttk.Treeview(win, columns=("ID", "Numurs"), show="headings")
        room_tree.heading("ID", text="ID")
        room_tree.heading("Numurs", text="Numurs")
        room_tree.pack()

        self.cursor.execute("SELECT id, room_number FROM rooms")
        for row in self.cursor.fetchall():
            room_tree.insert("", "end", values=row)

        tk.Label(win, text="Klienta ID").pack()
        c = tk.Entry(win)
        c.pack()

        tk.Label(win, text="Numura ID").pack()
        r = tk.Entry(win)
        r.pack()

        tk.Label(win, text="Check-in YYYY-MM-DD").pack()
        i = tk.Entry(win)
        i.pack()

        tk.Label(win, text="Check-out YYYY-MM-DD").pack()
        o = tk.Entry(win)
        o.pack()

        def save():
            self.cursor.execute("""
            INSERT INTO reservations VALUES(NULL,?,?,?,?)
            """, (c.get(), r.get(), i.get(), o.get()))
            self.conn.commit()
            messagebox.showinfo("OK", "Rezervācija veikta!")
            win.destroy()

        tk.Button(win, text="Saglabāt", bg="#ff69b4", command=save).pack(pady=10)

    def show_reservations(self):
        win = tk.Toplevel()
        tree = ttk.Treeview(win,
                            columns=("ID", "Klients", "Numurs", "Check-in", "Check-out"),
                            show="headings")

        for col in tree["columns"]:
            tree.heading(col, text=col)

        self.cursor.execute("""
        SELECT reservations.id, clients.name, rooms.room_number, check_in, check_out
        FROM reservations
        JOIN clients ON clients.id = reservations.client_id
        JOIN rooms ON rooms.id = reservations.room_id
        """)

        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True)

    def delete_reservation(self):
        win = tk.Toplevel()

        tree = ttk.Treeview(win,
                            columns=("ID", "Klients", "Numurs"),
                            show="headings")

        tree.heading("ID", text="ID")
        tree.heading("Klients", text="Klients")
        tree.heading("Numurs", text="Numurs")

        self.cursor.execute("""
        SELECT reservations.id, clients.name, rooms.room_number
        FROM reservations
        JOIN clients ON clients.id = reservations.client_id
        JOIN rooms ON rooms.id = reservations.room_id
        """)

        for row in self.cursor.fetchall():
            tree.insert("", "end", values=row)

        tree.pack()

        tk.Label(win, text="Ievadi ID").pack()
        entry = tk.Entry(win)
        entry.pack()

        def delete():
            self.cursor.execute("DELETE FROM reservations WHERE id=?", (entry.get(),))
            self.conn.commit()
            messagebox.showinfo("OK", "Dzēsts!")
            win.destroy()

        tk.Button(win, text="Dzēst", bg="#ff69b4", command=delete).pack()

    # =========================
    # WEATHER (7 DIENAS)
    # =========================
    def weather(self):
        win = tk.Toplevel()
        win.title("Laika prognoze")
        win.geometry("300x400")
        win.configure(bg="#ffc0cb")

        tk.Label(win, text="Ievadi pilsētu:", bg="#ffc0cb").pack(pady=5)
        city_entry = tk.Entry(win)
        city_entry.pack()

        weather_label = tk.Label(win, text="", bg="#ffc0cb", justify=tk.LEFT)
        weather_label.pack(pady=10)

        def show_weather():
            city = city_entry.get().strip()
            if not city:
                messagebox.showerror("Kļūda", "Ievadi pilsētu!")
                return

            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},LV&appid={API_KEY}&units=metric"

            try:
                data = requests.get(url).json()

                if data.get("cod") != "200":
                    messagebox.showerror("Kļūda", "Pilsēta nav atrasta!")
                    return

                text = ""
                shown = set()

                for item in data["list"]:
                    date = item["dt_txt"].split()[0]

                    if date not in shown:
                        temp = item["main"]["temp"]
                        weather = item["weather"][0]["main"]

                        icon = "☀️" if weather == "Clear" else "☁️" if weather == "Clouds" else "🌧️"

                        text += f"{date}: {temp}°C {icon}\n"
                        shown.add(date)

                        if len(shown) >= 7:
                            break

                weather_label.config(text=text)

            except:
                messagebox.showerror("Kļūda", "API problēma!")

        tk.Button(win, text="Parādīt prognozi",
                  bg="#ff69b4", command=show_weather).pack()

    # =========================
    def run(self):
        self.create_database()
        self.login_gui()


if __name__ == "__main__":
    HotelApp().run()