import sqlite3
import pytest
from hotel3 import HotelApp  # pieņemam, ka tavs OOP kods ir hotel3.py


# ===================================
# Fixture: izveido aplikācijas instanci
# ===================================
@pytest.fixture
def app():
    app = HotelApp()
    app.create_database()
    return app


# ===================================
# Pozitīvie testi
# ===================================
def test_add_client(app, monkeypatch):
    # Ievads: derīgs klients
    inputs = iter(["Anna", "12345678"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    app.add_client()

    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE name=?", ("Anna",))
    result = cursor.fetchone()
    conn.close()
    assert result is not None


def test_add_room(app, monkeypatch):
    inputs = iter(["101", "50.5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    app.add_room()

    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms WHERE room_number=?", (101,))
    result = cursor.fetchone()
    conn.close()
    assert result is not None


def test_make_reservation(app, monkeypatch):
    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()

    # izveido klientu un numuru
    cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", ("Test", "123"))
    client_id = cursor.lastrowid
    cursor.execute("INSERT INTO rooms (room_number, price) VALUES (?, ?)", (1, 50))
    room_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # simulē input
    inputs = iter([str(client_id), str(room_id), "2025-01-01", "2025-01-05"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    app.make_reservation()

    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservations WHERE client_id=?", (client_id,))
    result = cursor.fetchone()
    conn.close()
    assert result is not None


# ===================================
# Negatīvie testi
# ===================================
def test_add_client_invalid_name(app, monkeypatch):
    # Vārds ar cipariem → neder
    inputs = iter(["Ann4", "12345678"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    app.add_client()

    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE name=?", ("Ann4",))
    result = cursor.fetchone()
    conn.close()
    assert result is None


def test_add_room_invalid_price(app, monkeypatch):
    # Cena nav skaitlis → neder
    inputs = iter(["102", "abc"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    app.add_room()

    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms WHERE room_number=?", (102,))
    result = cursor.fetchone()
    conn.close()
    assert result is None


def test_make_reservation_wrong_dates(app, monkeypatch):
    # Sagatavo klientu un numuru
    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", ("Test2", "123"))
    client_id = cursor.lastrowid
    cursor.execute("INSERT INTO rooms (room_number, price) VALUES (?, ?)", (2, 60))
    room_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Nepareizi datumi: check_out < check_in
    inputs = iter([str(client_id), str(room_id), "2025-01-05", "2025-01-01"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    app.make_reservation()

    conn = sqlite3.connect("hotel_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservations WHERE client_id=?", (client_id,))
    result = cursor.fetchone()
    conn.close()
    assert result is None