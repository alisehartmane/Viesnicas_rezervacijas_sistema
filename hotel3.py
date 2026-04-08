import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import bcrypt
import re
import requests

API_KEY = "da575ceee90ba971c7efb46ce0ce95a4"


class HotelApp:
    def __init__(self):
        self.conn = sqlite3.connect("hotel_final.db")
        self.cursor = self.conn.cursor()

    # =========================
    # DATUBĀZE
    # =========================
    def create_database(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number INTEGER NOT NULL,
            price REAL NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
        )
        """)

        conn.commit()
        conn.close()

    # =========================
    # LOGIN GUI
    # =========================
    def login_gui(self):

        def validate_password(pw):
            if len(pw) < 8:
                return "Parolei jābūt vismaz 8 simboliem!"
            if not re.search(r"[A-Z]", pw):
                return "Parolei jābūt vismaz 1 lielajam burtam!"
            if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", pw):
                return "Parolei jābūt vismaz 1 speciālajam simbolam!"
            return None

        def register():
            user = username_entry.get().strip()
            pw = password_entry.get().strip()

            if not user or not pw:
                messagebox.showerror("Kļūda", "Lauki nedrīkst būt tukši!")
                return

            pw_error = validate_password(pw)
            if pw_error:
                messagebox.showerror("Kļūda", pw_error)
                return

            pw_hash = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

            try:
                self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw_hash))
                self.conn.commit()
                messagebox.showinfo("OK", "Reģistrācija veiksmīga!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Kļūda", "Lietotājs jau eksistē!")

        def login():
            user = username_entry.get().strip()
            pw = password_entry.get().encode()

            self.cursor.execute("SELECT password FROM users WHERE username=?", (user,))
            result = self.cursor.fetchone()

            if result and bcrypt.checkpw(pw, result[0].encode()):
                messagebox.showinfo("OK", "Login veiksmīgs!")
                root.destroy()
            else:
                messagebox.showerror("Kļūda", "Nepareizi dati!")

        root = tk.Tk()
        root.title("Login")
        root.geometry("300x200")

        tk.Label(root, text="Lietotājvārds").pack()
        username_entry = tk.Entry(root)
        username_entry.pack()

        tk.Label(root, text="Parole").pack()
        password_entry = tk.Entry(root, show="*")
        password_entry.pack()

        tk.Button(root, text="Login", command=login).pack(pady=5)
        tk.Button(root, text="Reģistrēties", command=register).pack(pady=5)

        root.mainloop()

    # =========================
    # KLIENTI
    # =========================
    def add_client(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()

        name = input("Klienta vārds: ").strip()
        if not name.replace(" ", "").isalpha():
            print("❌ Vārdam jābūt tikai ar burtiem!")
            conn.close()
            return

        phone = input("Telefons: ").strip()
        if not phone.isdigit():
            print("❌ Telefona numuram jābūt tikai ar cipariem!")
            conn.close()
            return

        cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        conn.close()

        print("✅ Klients pievienots!")

    def show_clients(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        data = cursor.fetchall()
        print("\n--- Klienti ---")
        if not data:
            print("Nav klientu.")
        else:
            for row in data:
                print(row)
        conn.close()

    # =========================
    # NUMURI
    # =========================
    def add_room(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()

        number = input("Numura numurs: ").strip()
        if not number.isdigit():
            print("❌ Numura numuram jābūt tikai ar cipariem!")
            conn.close()
            return

        price = input("Cena: ").strip()
        try:
            price_float = float(price)
        except:
            print("❌ Cenai jābūt skaitlim!")
            conn.close()
            return

        cursor.execute("INSERT INTO rooms (room_number, price) VALUES (?, ?)", (number, price_float))
        conn.commit()
        conn.close()

        print("✅ Numurs pievienots!")

    def show_rooms(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms")
        data = cursor.fetchall()
        print("\n--- Numuri ---")
        if not data:
            print("Nav numuru.")
        else:
            for row in data:
                print(row)
        conn.close()

    # =========================
    # REZERVĀCIJAS
    # =========================
    def make_reservation(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()

        print("\nIzvēlies klientu:")
        self.show_clients()
        client_id = input("Klienta ID: ").strip()
        if not client_id.isdigit():
            print("❌ Nepareizs ID!")
            conn.close()
            return

        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        if not cursor.fetchone():
            print("❌ Klients neeksistē!")
            conn.close()
            return

        print("\nIzvēlies numuru:")
        self.show_rooms()
        room_id = input("Numura ID: ").strip()
        if not room_id.isdigit():
            print("❌ Nepareizs ID!")
            conn.close()
            return

        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        if not cursor.fetchone():
            print("❌ Numurs neeksistē!")
            conn.close()
            return

        check_in = input("Iebraukšanas datums (YYYY-MM-DD): ").strip()
        check_out = input("Izbraukšanas datums (YYYY-MM-DD): ").strip()

        try:
            dt_in = datetime.strptime(check_in, "%Y-%m-%d")
            dt_out = datetime.strptime(check_out, "%Y-%m-%d")
            if dt_out <= dt_in:
                print("❌ Izbraukšanas datums jābūt pēc ierašanās datuma!")
                conn.close()
                return
        except:
            print("❌ Nepareizs datuma formāts!")
            conn.close()
            return

        cursor.execute("""
        SELECT * FROM reservations
        WHERE room_id = ?
        AND NOT (check_out <= ? OR check_in >= ?)
        """, (room_id, check_in, check_out))

        if cursor.fetchone():
            print("❌ Numurs šajos datumos jau ir aizņemts!")
        else:
            cursor.execute("""
            INSERT INTO reservations (client_id, room_id, check_in, check_out)
            VALUES (?, ?, ?, ?)
            """, (client_id, room_id, check_in, check_out))
            conn.commit()
            print("✅ Rezervācija veikta!")

        conn.close()

    def show_reservations(self):
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()
        cursor.execute("""
        SELECT reservations.id, clients.name, rooms.room_number, check_in, check_out
        FROM reservations
        LEFT JOIN clients ON reservations.client_id = clients.id
        LEFT JOIN rooms ON reservations.room_id = rooms.id
        """)
        data = cursor.fetchall()
        print("\n--- Rezervācijas ---")
        if not data:
            print("Nav rezervāciju.")
        else:
            for row in data:
                print(row)
        conn.close()

    # =========================
    # DZĒŠANA
    # =========================
    def delete_client(self):
        self.show_clients()
        client_id = input("Ievadi klienta ID: ").strip()
        if not client_id.isdigit():
            print("❌ Nepareizs ID!")
            return
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        if not cursor.fetchone():
            print("❌ Klients neeksistē!")
            conn.close()
            return
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        conn.close()
        print("🗑️ Klients izdzēsts!")

    def delete_room(self):
        self.show_rooms()
        room_id = input("Ievadi numura ID: ").strip()
        if not room_id.isdigit():
            print("❌ Nepareizs ID!")
            return
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        if not cursor.fetchone():
            print("❌ Numurs neeksistē!")
            conn.close()
            return
        cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        conn.commit()
        conn.close()
        print("🗑️ Numurs izdzēsts!")

    def delete_reservation(self):
        self.show_reservations()
        res_id = input("Ievadi rezervācijas ID: ").strip()
        if not res_id.isdigit():
            print("❌ Nepareizs ID!")
            return
        conn = sqlite3.connect("hotel_final.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = ?", (res_id,))
        if not cursor.fetchone():
            print("❌ Rezervācija neeksistē!")
            conn.close()
            return
        cursor.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
        conn.commit()
        conn.close()
        print("🗑️ Rezervācija izdzēsta!")

    # =========================
    # LAIKS
    # =========================
    def weather_gui(self):
        def show_weather():
            city = city_entry.get().strip()
            if not city:
                messagebox.showerror("Kļūda", "Ievadi pilsētu!")
                return

            city_query = f"{city},LV"
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_query}&appid={API_KEY}&units=metric"

            try:
                response = requests.get(url)
                data = response.json()

                if data.get("cod") != "200":
                    messagebox.showerror("Kļūda", f"Pilsēta '{city}' nav atrasta!")
                    return

                forecast_text = ""
                dates_shown = set()
                for item in data["list"]:
                    dt_txt = item["dt_txt"].split()[0]
                    if dt_txt not in dates_shown:
                        temp = item["main"]["temp"]
                        weather = item["weather"][0]["main"]

                        if weather.lower() == "clear":
                            symbol = "☀️"
                        elif weather.lower() == "clouds":
                            symbol = "☁️"
                        elif weather.lower() == "rain":
                            symbol = "🌧️"
                        else:
                            symbol = "🌤️"

                        forecast_text += f"{dt_txt}: {temp}°C {symbol}\n"
                        dates_shown.add(dt_txt)
                        if len(dates_shown) >= 7:
                            break

                weather_label.config(text=forecast_text)

            except requests.exceptions.RequestException:
                messagebox.showerror("Kļūda", "Nav interneta pieslēguma vai API nav pieejama!")

        weather_window = tk.Tk()
        weather_window.title("Laika prognoze")
        weather_window.geometry("300x400")

        tk.Label(weather_window, text="Ievadi pilsētu:").pack(pady=5)
        city_entry = tk.Entry(weather_window)
        city_entry.pack()

        tk.Label(weather_window, text="Pievieno ,LV aiz pilsētas").pack(pady=2)
        tk.Button(weather_window, text="Parādīt prognozi", command=show_weather).pack(pady=5)

        weather_label = tk.Label(weather_window, text="", justify=tk.LEFT)
        weather_label.pack(pady=10)

        weather_window.mainloop()

    # =========================
    # START
    # =========================
    def run(self):
        self.create_database()
        self.login_gui()
        self.conn.close()

        while True:
            print("\n===== VIESNĪCAS SISTĒMA =====")
            print("1 - Pievienot klientu")
            print("2 - Pievienot numuru")
            print("3 - Veikt rezervāciju")
            print("4 - Parādīt rezervācijas")
            print("5 - Parādīt klientus")
            print("6 - Parādīt numurus")
            print("7 - Dzēst klientu")
            print("8 - Dzēst numuru")
            print("9 - Dzēst rezervāciju")
            print("10 - Laika prognoze")
            print("0 - Iziet")

            choice = input("Izvēle: ").strip()

            if choice == "1":
                self.add_client()
            elif choice == "2":
                self.add_room()
            elif choice == "3":
                self.make_reservation()
            elif choice == "4":
                self.show_reservations()
            elif choice == "5":
                self.show_clients()
            elif choice == "6":
                self.show_rooms()
            elif choice == "7":
                self.delete_client()
            elif choice == "8":
                self.delete_room()
            elif choice == "9":
                self.delete_reservation()
            if choice == "10":
                self.weather_gui()
            elif choice == "0":
                print("Programma beidzas.")
                break


if __name__ == "__main__":
    app = HotelApp()
    app.run()