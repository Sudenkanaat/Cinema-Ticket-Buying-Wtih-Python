import tkinter as tk
from tkinter import messagebox
import random
import string
import sqlite3

# User sınıfını tanımla
class User:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    # Belirli bir koltuk için bir bilet satın alma işlemi gerçekleştirme yöntemi
    def buy(self, seat, card):
        if seat.is_free():
            if card.validate(price=seat.get_price()):
                seat.occupy()
                # Bir Ticket nesnesi oluştur
                ticket = Ticket(user=self, price=seat.get_price(), seat_number=seat.seat_id, seat_class=seat.__class__.__name__, cinema_name=seat.cinema_name)
                ticket.show_details()
                return "Satın alma başarılı!"
            else:
                return "Kartınızla ilgili bir sorun oluştu!"
        else:
            return "Koltuk dolu!"

# Sinema koltuğunu temsil eden Seat sınıfını tanımla
class Seat:
    database = r"C:\sqlite_db\cinema1.db"

    def __init__(self, seat_id, cinema_name):
        self._seat_id = seat_id
        self._cinema_name = cinema_name

    @property
    def seat_id(self):
        return self._seat_id

    @property
    def cinema_name(self):
        return self._cinema_name

    # Koltuğun fiyatını veritabanından alma yöntemi
    def get_price(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT "price" FROM "Seat" WHERE "seat_id" = ? AND "cinema_name" = ?
        """, [self.seat_id, self.cinema_name])
        price = cursor.fetchall()[0][0]
        return price

    # Koltuğun boş olup olmadığını kontrol etme yöntemi
    def is_free(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT "taken" FROM "Seat" WHERE "seat_id" = ? AND "cinema_name" = ?
        """, [self.seat_id, self.cinema_name])
        result = cursor.fetchall()[0][0]

        if result == 0:
            return True
        else:
            return False

    # Koltuğu işgal etme yöntemi
    def occupy(self):
        if self.is_free():
            connection = sqlite3.connect(self.database)
            connection.execute("""
            UPDATE "Seat" SET "taken"=? WHERE "seat_id"=? AND "cinema_name"=?
            """, [1, self.seat_id, self.cinema_name])
            connection.commit()
            connection.close()

# Özel Seat sınıflarını tanımla (ImaxSeat, GoldClassSeat, StandardSeat)
# Bu sınıflar Seat sınıfından miras alır

class ImaxSeat(Seat):
    def get_price(self):
        base_price = super().get_price()
        return base_price * 2  # İmax fiyatını 2 katına çıkar

class GoldClassSeat(Seat):
    def get_price(self):
        base_price = super().get_price()
        return base_price * 1.5  # GoldClass fiyatını 1.5 katına çıkar

class StandardSeat(Seat):
    pass

# Kredi kartını temsil eden Card sınıfını tanımla
class Card:
    database = r"C:\sqlite_db\banking1.db"

    def __init__(self, type, number, cvc, holder):
        self._holder = holder
        self._cvc = cvc
        self._number = number
        self._type = type

    @property
    def holder(self):
        return self._holder

    @property
    def cvc(self):
        return self._cvc

    @property
    def number(self):
        return self._number

    @property
    def type(self):
        return self._type

    # Kartın geçerliliğini kontrol etme yöntemi
    def validate(self, price):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT "balance" FROM "Card" WHERE "number"=? and "cvc"=?
        """, [self.number, self.cvc])
        result = cursor.fetchall()

        if result:
            balance = result[0][0]
            if balance >= price:
                connection.execute("""
                UPDATE "Card" SET "balance" = ? WHERE "number"=? and "cvc"=?
                """, [balance - price, self.number, self.cvc])
                connection.commit()
                connection.close()
                return True

# Bir bilet nesnesini temsil eden Ticket sınıfını tanımla
class Ticket:
    def __init__(self, user, price, seat_number, seat_class, cinema_name):
        self._user = user
        self._price = price
        self._seat_number = seat_number
        self._seat_class = seat_class
        self._cinema_name = cinema_name

    @property
    def user(self):
        return self._user

    @property
    def price(self):
        return self._price

    @property
    def seat_number(self):
        return self._seat_number

    @property
    def seat_class(self):
        return self._seat_class

    @property
    def cinema_name(self):
        return self._cinema_name

    # Bilet detaylarını gösterme yöntemi
    def show_details(self):
        details_window = tk.Toplevel()
        details_window.title("Bilet Detayları")

        tk.Label(details_window, text="Ad:").grid(row=0, column=0)
        tk.Label(details_window, text=self.user.name).grid(row=0, column=1)

        tk.Label(details_window, text="Koltuk Numarası:").grid(row=1, column=0)
        tk.Label(details_window, text=str(self.seat_number)).grid(row=1, column=1)

        tk.Label(details_window, text="Koltuk Sınıfı:").grid(row=2, column=0)
        tk.Label(details_window, text=self.seat_class).grid(row=2, column=1)

        tk.Label(details_window, text="Sinema İsmi:").grid(row=3, column=0)
        tk.Label(details_window, text=self.cinema_name).grid(row=3, column=1)

        tk.Label(details_window, text="Fiyat:").grid(row=4, column=0)
        tk.Label(details_window, text=str(self.price)).grid(row=4, column=1)

        tk.Button(details_window, text="Tamam", command=details_window.destroy).grid(row=5, column=0, columnspan=2)


# Bilet satın alma işlemini gerçekleştiren fonksiyon
def buy_ticket():
    name = name_entry.get()
    seat_id = seat_entry.get()
    seat_class = seat_class_var.get()
    card_type = card_type_entry.get()
    card_number = card_number_entry.get()
    card_cvc = card_cvc_entry.get()
    card_holder = card_holder_entry.get()

    user = User(name=name)
    seat_class_map = {"Imax": ImaxSeat, "GoldClass": GoldClassSeat, "Standard": StandardSeat}
    seat = seat_class_map.get(seat_class, StandardSeat)(seat_id=seat_id)
    card = Card(type=card_type, number=card_number, cvc=card_cvc, holder=card_holder)

    result = user.buy(seat=seat, card=card)
    messagebox.showinfo("Sonuç", result)

# Veritabanından sinema isimlerini alacak fonksiyon
def get_cinema_names():
    connection = sqlite3.connect(Seat.database)
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT cinema_name FROM Seat")
    cinema_names = [row[0] for row in cursor.fetchall()]
    connection.close()
    return cinema_names

# Tkinter GUI oluşturma
root = tk.Tk()
root.title("Sinema Bilet Satın Alma")

# Kullanıcı giriş alanları
tk.Label(root, text="Tam Ad:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Koltuk Numarası:").grid(row=1, column=0)
seat_entry = tk.Entry(root)
seat_entry.grid(row=1, column=1)

tk.Label(root, text="Koltuk Sınıfı:").grid(row=2, column=0)
seat_classes = ["Imax", "GoldClass", "Standard"]
seat_class_var = tk.StringVar(root)
seat_class_var.set(seat_classes[0])
seat_class_menu = tk.OptionMenu(root, seat_class_var, *seat_classes)
seat_class_menu.grid(row=2, column=1)

tk.Label(root, text="Kart Tipi:").grid(row=3, column=0)
card_type_entry = tk.Entry(root)
card_type_entry.grid(row=3, column=1)

tk.Label(root, text="Kart Numarası:").grid(row=4, column=0)
card_number_entry = tk.Entry(root)
card_number_entry.grid(row=4, column=1)

tk.Label(root, text="Kart CVC:").grid(row=5, column=0)
card_cvc_entry = tk.Entry(root)
card_cvc_entry.grid(row=5, column=1)

tk.Label(root, text="Kart Sahibi Adı:").grid(row=6, column=0)
card_holder_entry = tk.Entry(root)
card_holder_entry.grid(row=6, column=1)

# Sinema isimleri için OptionMenu
tk.Label(root, text="Sinema İsmi:").grid(row=7, column=0)
cinema_names = get_cinema_names()
cinema_name_var = tk.StringVar(root)
cinema_name_var.set(cinema_names[0])
cinema_name_menu = tk.OptionMenu(root, cinema_name_var, *cinema_names)
cinema_name_menu.grid(row=7, column=1)

# Bilet Satın Alma Butonu
def buy_ticket():
    name = name_entry.get()
    seat_id = seat_entry.get()
    seat_class = seat_class_var.get()
    card_type = card_type_entry.get()
    card_number = card_number_entry.get()
    card_cvc = card_cvc_entry.get()
    card_holder = card_holder_entry.get()
    cinema_name = cinema_name_var.get()

    user = User(name=name)
    seat_class_map = {"Imax": ImaxSeat, "GoldClass": GoldClassSeat, "Standard": StandardSeat}
    seat = seat_class_map.get(seat_class, StandardSeat)(seat_id=seat_id, cinema_name=cinema_name)
    card = Card(type=card_type, number=card_number, cvc=card_cvc, holder=card_holder)

    result = user.buy(seat=seat, card=card)
    messagebox.showinfo("Sonuç", result)

buy_button = tk.Button(root, text="Bilet Satın Al", command=buy_ticket)
buy_button.grid(row=8, column=0, columnspan=2)

# Tkinter ana döngüsü
root.mainloop()