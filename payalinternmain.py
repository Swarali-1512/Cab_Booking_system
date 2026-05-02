# Galaxy Bus Reservation System (Multilingual: English, Hindi, Marathi)
# Humanized, consistent, and ready for practical project deployment

import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import random
from datetime import datetime

# === Color Theme ===
BG_COLOR = "#fff8e6"
BTN_GREEN = "green"
BTN_BLUE = "blue"
BTN_ORANGE = "orange"
BTN_RED = "red"

# === Database Setup ===
db_conn = sqlite3.connect("galaxy_bus.db")
db_cursor = db_conn.cursor()
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    ticket_no TEXT PRIMARY KEY,
    name TEXT,
    source TEXT,
    destination TEXT,
    seat TEXT,
    price REAL,
    date TEXT,
    time TEXT,
    travel_date TEXT
)
""")
db_conn.commit()

# === Language Data (English, Hindi, Marathi) ===
LANGUAGES = {
    'English': {
        'title': 'Galaxy Bus Reservation System', 'book_ticket': 'Book Ticket', 'view_tickets': 'View All Tickets', 'cancel_ticket': 'Cancel Ticket', 'exit': 'Exit',
        'receipt': 'Ticket Receipt', 'receipt_fields': ['Ticket No', 'Name', 'Source', 'Destination', 'Seat', 'Price', 'Booked Date', 'Time', 'Travel Date'],
        'entry_fields': ['Name', 'Source', 'Destination', 'Seat', 'Travel Date (dd-mm-yyyy)'],
        'confirm_booking': 'Confirm Booking', 'back': 'Back', 'error': 'Error', 'all_required': 'All fields required', 'success': 'Success', 'ticket_booked': 'Ticket booked successfully! Ticket No:',
        'ok': 'OK', 'all_tickets': 'All Booked Tickets', 'no_bookings': 'No bookings found.', 'clear_history': 'Clear All History', 'confirm': 'Confirm', 'clear_history_confirm': 'Clear all booking history?',
        'cleared': 'Cleared', 'history_cleared': 'All booking history cleared.', 'close': 'Close', 'seat': 'Seat', 'travel_date': 'Travel Date (dd-mm-yyyy)', 'cancelled': 'Cancelled', 'ticket_cancelled': 'Ticket cancelled successfully.'
    },
    'Hindi': {
        'title': 'गैलेक्सी बस आरक्षण प्रणाली', 'book_ticket': 'टिकट बुक करें', 'view_tickets': 'सभी टिकट देखें', 'cancel_ticket': 'टिकट रद्द करें', 'exit': 'बाहर निकलें',
        'receipt': 'टिकट रसीद', 'receipt_fields': ['टिकट नंबर', 'नाम', 'प्रस्थान', 'गंतव्य', 'सीट', 'कीमत', 'बुकिंग दिनांक', 'समय', 'यात्रा दिनांक'],
        'entry_fields': ['नाम', 'प्रस्थान', 'गंतव्य', 'सीट', 'यात्रा दिनांक (dd-mm-yyyy)'],
        'confirm_booking': 'बुकिंग पुष्टि करें', 'back': 'वापस', 'error': 'त्रुटि', 'all_required': 'सभी फ़ील्ड आवश्यक हैं', 'success': 'सफलता', 'ticket_booked': 'टिकट सफलतापूर्वक बुक हुआ! टिकट नंबर:',
        'ok': 'ठीक है', 'all_tickets': 'सभी बुक किए गए टिकट', 'no_bookings': 'कोई बुकिंग नहीं मिली।', 'clear_history': 'सभी इतिहास साफ करें', 'confirm': 'पुष्टि करें', 'clear_history_confirm': 'क्या आप सभी बुकिंग इतिहास साफ करना चाहते हैं?',
        'cleared': 'साफ़ किया गया', 'history_cleared': 'सभी बुकिंग इतिहास साफ किया गया।', 'close': 'बंद करें', 'seat': 'सीट', 'travel_date': 'यात्रा दिनांक (dd-mm-yyyy)', 'cancelled': 'रद्द', 'ticket_cancelled': 'टिकट सफलतापूर्वक रद्द किया गया।'
    },
    'Marathi': {
        'title': 'गॅलेक्सी बस आरक्षण प्रणाली', 'book_ticket': 'तिकीट बुक करा', 'view_tickets': 'सर्व तिकीट पहा', 'cancel_ticket': 'तिकीट रद्द करा', 'exit': 'बाहेर पडा',
        'receipt': 'तिकीट पावती', 'receipt_fields': ['तिकीट क्र.', 'नाव', 'स्रोत', 'गंतव्य', 'सीट', 'किंमत', 'बुकिंग दिनांक', 'वेळ', 'प्रवास दिनांक'],
        'entry_fields': ['नाव', 'स्रोत', 'गंतव्य', 'सीट', 'प्रवास दिनांक (dd-mm-yyyy)'],
        'confirm_booking': 'बुकिंग पुष्टी करा', 'back': 'मागे', 'error': 'चूक', 'all_required': 'सर्व फील्ड आवश्यक आहेत', 'success': 'यश', 'ticket_booked': 'तिकीट यशस्वीरित्या बुक झाले! तिकीट क्र. :',
        'ok': 'ठीक आहे', 'all_tickets': 'सर्व बुक केलेली तिकीट', 'no_bookings': 'कोणतीही बुकिंग आढळली नाही.', 'clear_history': 'सर्व इतिहास साफ करा', 'confirm': 'पुष्टी करा', 'clear_history_confirm': 'सर्व बुकिंग इतिहास साफ करायचा आहे का?',
        'cleared': 'साफ', 'history_cleared': 'सर्व बुकिंग इतिहास साफ केला.', 'close': 'बंद', 'seat': 'सीट', 'travel_date': 'प्रवास दिनांक (dd-mm-yyyy)', 'cancelled': 'रद्द', 'ticket_cancelled': 'तिकीट यशस्वीरित्या रद्द केले.'
    }
}

# === Print Receipt Window ===
def print_receipt(ticket_data, lang):
    receipt_win = tk.Toplevel()
    receipt_win.title(lang['receipt'])
    receipt_win.configure(bg=BG_COLOR)
    tk.Label(receipt_win, text=lang['receipt'], font=("Arial", 24, "bold"), bg=BG_COLOR).pack(pady=20)
    fields = lang['receipt_fields']
    for idx, field in enumerate(fields):
        tk.Label(receipt_win, text=f"{field}: {ticket_data[idx]}", font=("Arial", 16), bg=BG_COLOR).pack(pady=2)
    tk.Button(receipt_win, text=lang['ok'], font=("Arial", 16), bg=BTN_GREEN, fg="white", command=receipt_win.destroy).pack(pady=15)

# === Book Ticket ===
def book_ticket(lang):
    win = tk.Toplevel()
    win.title(lang['book_ticket'])
    win.attributes('-fullscreen', True)
    win.configure(bg=BG_COLOR)

    tk.Label(win, text=lang['book_ticket'], font=("Arial", 28, "bold"), bg=BG_COLOR).pack(pady=20)
    entries = {}
    for field in lang['entry_fields']:
        tk.Label(win, text=field+":", font=("Arial", 18), bg=BG_COLOR).pack()
        e = tk.Entry(win, font=("Arial", 18))
        e.pack(pady=5)
        entries[field] = e

    def confirm():
        vals = [entries[f].get().strip() for f in entries]
        if not all(vals):
            messagebox.showerror(lang['error'], lang['all_required'])
            return
        ticket_no = "TKT" + str(random.randint(1000, 9999))
        now = datetime.now()
        db_cursor.execute("INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (ticket_no, vals[0], vals[1], vals[2], vals[3], 200, now.strftime("%d-%m-%Y"), now.strftime("%H:%M:%S"), vals[4]))
        db_conn.commit()
        messagebox.showinfo(lang['success'], f"{lang['ticket_booked']} {ticket_no}")
        print_receipt((ticket_no, vals[0], vals[1], vals[2], vals[3], 200, now.strftime("%d-%m-%Y"), now.strftime("%H:%M:%S"), vals[4]), lang)
        win.destroy()

    tk.Button(win, text=lang['confirm_booking'], font=("Arial", 18), bg=BTN_GREEN, fg="white", command=confirm).pack(pady=10)
    tk.Button(win, text=lang['back'], font=("Arial", 18), bg=BTN_RED, fg="white", command=win.destroy).pack(pady=10)

# === View All Tickets ===
def view_all(lang):
    win = tk.Toplevel()
    win.title(lang['view_tickets'])
    win.attributes('-fullscreen', True)
    win.configure(bg=BG_COLOR)

    tk.Label(win, text=lang['all_tickets'], font=("Arial", 28, "bold"), bg=BG_COLOR).pack(pady=20)
    txt = scrolledtext.ScrolledText(win, width=120, height=30, font=("Courier", 12))
    txt.pack()

    def load_tickets():
        txt.config(state='normal')
        txt.delete('1.0', tk.END)
        db_cursor.execute("SELECT * FROM reservations")
        records = db_cursor.fetchall()
        if records:
            for r in records:
                formatted = "\n".join([f"{lang['receipt_fields'][i]}: {r[i]}" for i in range(len(r))])
                txt.insert(tk.END, formatted + "\n" + "-"*50 + "\n")
        else:
            txt.insert(tk.END, lang['no_bookings'] + "\n")
        txt.config(state='disabled')

    def clear_all():
        if messagebox.askyesno(lang['confirm'], lang['clear_history_confirm']):
            db_cursor.execute("DELETE FROM reservations")
            db_conn.commit()
            load_tickets()
            messagebox.showinfo(lang['cleared'], lang['history_cleared'])

    load_tickets()
    tk.Button(win, text=lang['clear_history'], font=("Arial", 18), bg=BTN_ORANGE, fg="white", command=clear_all).pack(pady=10)
    tk.Button(win, text=lang['close'], font=("Arial", 18), bg=BTN_RED, fg="white", command=win.destroy).pack(pady=10)

# === Cancel Ticket ===
def cancel_ticket(lang):
    win = tk.Toplevel()
    win.title(lang['cancel_ticket'])
    win.attributes('-fullscreen', True)
    win.configure(bg=BG_COLOR)

    tk.Label(win, text=lang['cancel_ticket'], font=("Arial", 28, "bold"), bg=BG_COLOR).pack(pady=20)
    tk.Label(win, text=lang['seat']+":", font=("Arial", 18), bg=BG_COLOR).pack()
    seat_entry = tk.Entry(win, font=("Arial", 18))
    seat_entry.pack(pady=5)
    tk.Label(win, text=lang['travel_date']+":", font=("Arial", 18), bg=BG_COLOR).pack()
    date_entry = tk.Entry(win, font=("Arial", 18))
    date_entry.pack(pady=5)

    def confirm_cancel():
        seat = seat_entry.get().strip()
        date = date_entry.get().strip()
        if not seat or not date:
            messagebox.showerror(lang['error'], lang['all_required'])
            return
        db_cursor.execute("DELETE FROM reservations WHERE seat=? AND travel_date=?", (seat, date))
        db_conn.commit()
        messagebox.showinfo(lang['cancelled'], lang['ticket_cancelled'])
        win.destroy()

    tk.Button(win, text=lang['cancel_ticket'], font=("Arial", 18), bg=BTN_ORANGE, fg="white", command=confirm_cancel).pack(pady=10)
    tk.Button(win, text=lang['back'], font=("Arial", 18), bg=BTN_RED, fg="white", command=win.destroy).pack(pady=10)

# === Main Window ===
def main_window(language):
    lang = LANGUAGES[language]
    root = tk.Tk()
    root.title(lang['title'])
    root.attributes('-fullscreen', True)
    root.configure(bg=BG_COLOR)

    tk.Label(root, text=lang['title'], font=("Arial", 28, "bold"), bg=BG_COLOR).pack(pady=30)
    tk.Button(root, text=lang['book_ticket'], font=("Arial", 18), bg=BTN_GREEN, fg="white", width=25, command=lambda: book_ticket(lang)).pack(pady=10)
    tk.Button(root, text=lang['view_tickets'], font=("Arial", 18), bg=BTN_BLUE, fg="white", width=25, command=lambda: view_all(lang)).pack(pady=10)
    tk.Button(root, text=lang['cancel_ticket'], font=("Arial", 18), bg=BTN_ORANGE, fg="white", width=25, command=lambda: cancel_ticket(lang)).pack(pady=10)
    tk.Button(root, text=lang['exit'], font=("Arial", 18), bg=BTN_RED, fg="white", width=25, command=root.destroy).pack(pady=10)

    root.mainloop()

# === Language Selection Window ===
def select_language_window():
    win = tk.Tk()
    win.title("Select Language")
    win.attributes('-fullscreen', True)
    win.configure(bg=BG_COLOR)

    tk.Label(win, text="Select Language", font=("Arial", 28, "bold"), bg=BG_COLOR).pack(pady=30)
    tk.Button(win, text="English", font=("Arial", 18), bg=BTN_BLUE, fg="white", width=25, command=lambda: [win.destroy(), main_window('English')]).pack(pady=10)
    tk.Button(win, text="Hindi", font=("Arial", 18), bg=BTN_BLUE, fg="white", width=25, command=lambda: [win.destroy(), main_window('Hindi')]).pack(pady=10)
    tk.Button(win, text="Marathi", font=("Arial", 18), bg=BTN_BLUE, fg="white", width=25, command=lambda: [win.destroy(), main_window('Marathi')]).pack(pady=10)
    tk.Button(win, text="Exit", font=("Arial", 18), bg=BTN_RED, fg="white", width=25, command=win.destroy).pack(pady=20)

    win.mainloop()

# === Login Window ===
def login_window():
    win = tk.Tk()
    win.title("Galaxy Bus Reservation Login")
    win.attributes('-fullscreen', True)
    win.configure(bg=BG_COLOR)

    tk.Label(win, text="Galaxy Bus Reservation", font=("Arial", 28, "bold"), bg=BG_COLOR).pack(pady=20)
    tk.Label(win, text="Username:", font=("Arial", 18), bg=BG_COLOR).pack()
    user_entry = tk.Entry(win, font=("Arial", 18))
    user_entry.pack(pady=5)
    tk.Label(win, text="Password:", font=("Arial", 18), bg=BG_COLOR).pack()
    pass_entry = tk.Entry(win, font=("Arial", 18), show="*")
    pass_entry.pack(pady=5)

    def login():
        u = user_entry.get()
        p = pass_entry.get()
        if not u or not p:
            messagebox.showerror("Error", "All fields required")
            return
        db_cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        if db_cursor.fetchone():
            win.destroy()
            select_language_window()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def register():
        u = user_entry.get()
        p = pass_entry.get()
        if not u or not p:
            messagebox.showerror("Error", "All fields required")
            return
        db_cursor.execute("SELECT * FROM users WHERE username=?", (u,))
        if db_cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
        else:
            db_cursor.execute("INSERT INTO users VALUES (?, ?)", (u, p))
            db_conn.commit()
            messagebox.showinfo("Success", "Registration successful")

    tk.Button(win, text="Login", font=("Arial", 18), bg=BTN_GREEN, fg="white", command=login).pack(pady=10)
    tk.Button(win, text="Register", font=("Arial", 18), bg=BTN_BLUE, fg="white", command=register).pack(pady=5)
    tk.Button(win, text="Exit", font=("Arial", 18), bg=BTN_RED, fg="white", command=win.destroy).pack(pady=10)

    win.mainloop()

# === Run ===
if __name__ == "__main__":
    login_window()
    db_conn.close()
