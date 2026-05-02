import tkinter as tk
from tkinter import messagebox, PhotoImage
import json, os

# ====================================================================
# FILE PATH SETUP
# ====================================================================
# We make sure JSON files are saved in the same folder as this script,
# no matter where we run the program from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where script is located
drivers_file = os.path.join(BASE_DIR, "drivers.json")
passengers_file = os.path.join(BASE_DIR, "passengers.json")
bookings_file = os.path.join(BASE_DIR, "bookings.json")

print("[DEBUG] JSON files will be saved in:", BASE_DIR)  # shows where files are created

# ====================================================================
# JSON UTILITIES (Load / Save / Reset)
# ====================================================================s
def load(f):
    """Load data from a JSON file. If file is missing/empty, return []."""
    if not os.path.exists(f):
        # Create empty list if file does not exist
        with open(f, "w") as file:
            file.write("[]")
    with open(f, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            # If file corrupted or empty, just return []
            return [] 


def save(f, d):
    """Save data (list/dict) to a JSON file."""
    with open(f, "w") as file:
        json.dump(d, file, indent=2)
    print(f"[DEBUG] Saved to {f}: {d}")   # Debugging info in terminal

def reset():
    """Clear all data files (drivers, passengers, bookings)."""
    for f in [drivers_file, passengers_file, bookings_file]:
        save(f, [])

# ====================================================================
# CAB BOOKING APP CLASS
# ====================================================================
class CabApp:
    def __init__(s, r):
        """Initialize the main window and show menu."""
        s.root, s.user = r, None
        r.title("🚕 Cab Booking App")
        r.geometry("750x600")
        r.configure(bg="#faffe6")

        #try to lod logo
        try:
            s.logo = PhotoImage(file="logo.png")
        except:
            s.logo = None
            
        # Styles for buttons/labels/titles
        s.btn_style = {"font": ("Arial", 12), "bg": "#4CAF50", "fg": "white", "activebackground": "#45a049", "width": 25}
        s.label_style = {"bg": "#e6f2ff", "font": ("Arial", 12)}
        s.title_style = {"bg": "#e6f2ff", "font": ("Arial", 16, "bold"), "fg": "#222"}

        s.menu()   # Show main menu

    # ------------------------------------------------
    # HELPER FUNCTIONS
    # ------------------------------------------------
    def clr(s): 
        """Clear all widgets from window."""
        [w.destroy() for w in s.root.winfo_children()]

    def show_logo(s):
        """Show logo or fallback text."""
        if s.logo:
            tk.Label(s.root, image=s.logo, bg="#e6f2ff").pack(pady=10)
        else:
            tk.Label(s.root, text="🚕 Cab Booking", font=("Arial", 18, "bold"), bg="#e6f2ff").pack(pady=10)


    # ------------------------------------------------
    # MAIN MENU
    # ------------------------------------------------
    def menu(s):
        """Show main menu with options."""
        s.clr(); s.show_logo()
        for txt, cmd in [
            ("👤 Passenger Login", s.passenger_login),
            ("🚖 Driver Login", s.driver_login),
            ("🔄 Reset All Data", lambda: reset() or messagebox.showinfo("Reset", "All data reset!")),
            ("📜 Terms & Conditions", s.terms),
            ("❌ Exit", s.root.quit)]:
            tk.Button(s.root, text=txt, **s.btn_style, command=cmd).pack(pady=5)

    def terms(s):
        """Show Terms & Conditions."""
        s.clr(); s.show_logo()
        terms = (
            "1. 🚖 Only online drivers will be listed\n"
            "2. 👤 Passengers must provide accurate info\n"
            "3. 💰 Fare = rate x km - discount\n"
            "4. ⚠️ Not responsible for disputes\n"
            "5. ❗ Drivers can cancel in emergencies"
        )
        tk.Label(s.root, text="📜 Terms & Conditions", **s.title_style).pack(pady=10)
        tk.Message(s.root, text=terms, width=600, **s.label_style).pack(pady=10)
        tk.Button(s.root, text="🔙 Back", **s.btn_style, command=s.menu).pack(pady=10)


    
    # ------------------------------------------------
    # LOGIN SYSTEM
    # ------------------------------------------------
    def passenger_login(s): s.login_ui("Passenger", passengers_file, s.passenger_dash, s.passenger_register)
    def driver_login(s): s.login_ui("Driver", drivers_file, s.driver_dash, s.driver_register)

    def login_ui(s, role, file, on_success, on_register):
        """Generic login screen for passengers/drivers."""
        s.clr(); s.show_logo()
        icon = "👤" if role == "Passenger" else "🚖"
        tk.Label(s.root, text=f"{icon} {role} Login", **s.title_style).pack(pady=10)

        # Input fields
        phone, pwd = tk.Entry(s.root), tk.Entry(s.root, show="*")
        for label, box in [("📱 Phone", phone), ("🔒 Password", pwd)]:
            tk.Label(s.root, text=label, **s.label_style).pack(); box.pack()

        def login():
            """Check entered credentials against stored JSON data."""
            for u in load(file):
                if u.get("phone") == phone.get() and u.get("password") == pwd.get():
                    s.user = u; return on_success()
            messagebox.showerror("Error", "Invalid credentials")

        for txt, cmd in [("✅ Login", login), ("📝 Register", on_register), ("🔙 Back", s.menu)]:
            tk.Button(s.root, text=txt, **s.btn_style, command=cmd).pack(pady=5)

    # ------------------------------------------------
    # REGISTRATION
    # ------------------------------------------------
    def register_ui(s, role, file, fields, is_driver=False):
        """Generic registration screen (passenger or driver)."""
        s.clr(); s.show_logo()
        tk.Label(s.root, text=f"📝 {role} Register", **s.title_style).pack(pady=10)

        #create entry fields
        e = {f: tk.Entry(s.root) for f in fields}
        for f in fields: tk.Label(s.root, text=f, **s.label_style).pack(); e[f].pack()

        def register():
            """Save new user to JSON file."""
            data = load(file)
            if any(u.get("phone") == e["Phone"].get() for u in data):
                return messagebox.showerror("Error", "Already registered")
            try:
                # Convert input to dictionary
                user = {k.lower(): e[k].get() for k in e}
                if is_driver:
                    user.update({
                        "fare": float(user["fare"]),
                        "discount": float(user["discount"]),
                        "status": "online"
                    })
                data.append(user)
                save(file, data)
                messagebox.showinfo("Success", "Registered")
                s.menu()
            except: 
                messagebox.showerror("Error", "Invalid Input")

        for txt, cmd in [("✅ Submit", register), ("🔙 Back", s.menu)]:
            tk.Button(s.root, text=txt, **s.btn_style, command=cmd).pack(pady=5)

    def passenger_register(s):
        """Passenger registration screen."""
        s.register_ui("Passenger", passengers_file, ["Name", "Phone", "Password"])
        
    def driver_register(s):
        """Driver registration screen."""
        s.register_ui("Driver", drivers_file,
            ["Name", "Phone", "Password", "Car", "Model", "Fuel", "Type", "Fare", "Discount"], is_driver=True)

    # ------------------------------------------------
    # PASSENGER DASHBOARD
    # ------------------------------------------------
    def passenger_dash(s):
        """Passenger dashboard: search drivers, view bookings."""
        s.clr(); s.show_logo()
        tk.Label(s.root, text=f"👤 Welcome {s.user['name']} (Passenger)", **s.title_style).pack(pady=10)
        tk.Button(s.root, text="🧾 My Bookings", **s.btn_style, command=s.view_passenger_bookings).pack(pady=5)

        # Show only online drivers
        drivers = [d for d in load(drivers_file) if d.get("status") == "online"]
        if not drivers:
            tk.Label(s.root, text="No online drivers.", fg="red", bg="#e6f2ff").pack(pady=10)
            return tk.Button(s.root, text="🔙 Back", **s.btn_style, command=s.menu).pack(pady=5)

        # Filter options (Model, Fuel, Type)
        filters = {k: tk.StringVar(value="All") for k in ["model", "fuel", "type"]}
        for k in filters:
            tk.Label(s.root, text=f"Filter by {k.capitalize()}", **s.label_style).pack()
            opts = sorted(set(d[k] for d in drivers)); tk.OptionMenu(s.root, filters[k], *["All"] + opts).pack()

        def show():
            """Apply filters and display matching drivers."""
            f = drivers
            for k, v in filters.items():
                if v.get() != "All": f = [d for d in f if d[k] == v.get()]

            s.clr(); s.show_logo()
            tk.Label(s.root, text="🚖 Available Cabs", **s.title_style).pack(pady=10)
            for d in f:
                frm = tk.Frame(s.root, bd=1, relief="solid", padx=10, pady=5, bg="white")
                frm.pack(padx=10, pady=5, fill="x")
                for line in [
                    f"Driver: {d['name']}",
                    f"Car: {d['car']} ({d['model']}) | Fuel: {d['fuel']} | Type: {d['type']}",
                    f"Fare: ₹{d['fare']}/km | Discount: {d['discount']}%"]:
                    tk.Label(frm, text=line, anchor="w", bg="white").pack(fill="x")
                tk.Button(frm, text="Book Now", bg="green", fg="white",
                          command=lambda d=d: s.book(d)).pack(anchor="e")
            tk.Button(s.root, text="🔙 Back", **s.btn_style, command=s.passenger_dash).pack(pady=10)

        tk.Button(s.root, text="🔍 Find Cabs", **s.btn_style, command=show).pack(pady=10)
        tk.Button(s.root, text="🚪 Logout", **s.btn_style, command=s.menu).pack(pady=5)


    # ------------------------------------------------
    # BOOKING SYSTEM
    # ------------------------------------------------
    def book(s, d):
        """Passenger books a cab and gets receipt."""
        s.clr(); s.show_logo()
        tk.Label(s.root, text=f"Booking {d['car']} ({d['model']})", **s.title_style).pack(pady=10)

        # Input fields
        from_entry = tk.Entry(s.root)
        to_entry = tk.Entry(s.root)
        km = tk.Entry(s.root)

        tk.Label(s.root, text="📍 From Location", **s.label_style).pack()
        from_entry.pack()
        tk.Label(s.root, text="🏁 To Location", **s.label_style).pack()
        to_entry.pack()
        tk.Label(s.root, text="📏 Enter distance in km", **s.label_style).pack()
        km.pack()

        def confirm():
            """Confirm booking, calculate fare, and save."""
            try:
                dist = float(km.get())
                from_loc = from_entry.get().strip()
                to_loc = to_entry.get().strip()
                if not from_loc or not to_loc:
                    return messagebox.showerror("Error", "Please enter both 'From' and 'To' locations.")

                # Fare calculation
                total = dist * d['fare']
                discount = total * d['discount'] / 100
                fare = total - discount

                if messagebox.askyesno("Confirm", f"Total fare: ₹{fare:.2f}. Confirm booking?"):
                    b = load(bookings_file)
                    booking = {
                        "passenger": s.user["phone"],
                        "driver": d["phone"],
                        "from": from_loc,
                        "to": to_loc,
                        "distance": dist,
                        "fare": fare,
                        "status": "Completed",
                        "rating": None
                    }
                    b.append(booking)
                    save(bookings_file, b)

                    # Show Receipt
                    receipt = tk.Toplevel(s.root)
                    receipt.title("🚕 Booking Receipt")
                    receipt.geometry("400x450")
                    receipt.configure(bg="white")

                    details = [
                        f"🚖 Cab Booking Receipt",
                        "-----------------------------",
                        f"👤 Passenger: {s.user['name']}",
                        f"🧑‍✈️ Driver: {d['name']}",
                        f"🚗 Car: {d['car']} ({d['model']})",
                        f"🛢 Fuel Type: {d['fuel']} | {d['type']}",
                        f"📍 From: {from_loc}",
                        f"🏁 To: {to_loc}",
                        f"📏 Distance: {dist} km",
                        f"💰 Base Fare: ₹{total:.2f}",
                        f"🎁 Discount: ₹{discount:.2f}",
                        f"✅ Total Fare: ₹{fare:.2f}",
                        f"📌 Status: Completed",
                        "-----------------------------",
                        "🙏 Thank you for booking with us!"
                    ]
                    for line in details:
                        tk.Label(receipt, text=line, font=("Arial", 11), anchor="w", bg="white").pack(anchor="w", padx=20, pady=2)

                    tk.Button(receipt, text="Close", command=lambda: [receipt.destroy(), s.rate_driver(d["phone"])]).pack(pady=10)

            except:
                messagebox.showerror("Error", "Please enter valid distance in km.")

        tk.Button(s.root, text="✅ Confirm", **s.btn_style, command=confirm).pack(pady=10)
        tk.Button(s.root, text="🔙 Back", **s.btn_style, command=s.passenger_dash).pack()

    # ------------------------------------------------
    # RATING SYSTEM
    # ------------------------------------------------
    def rate_driver(s, driver_phone):
        s.clr(); s.show_logo()
        tk.Label(s.root, text="⭐ Rate Your Ride", **s.title_style).pack(pady=10)
        tk.Label(s.root, text="Enter rating (1 to 5)", **s.label_style).pack()
        rating = tk.Entry(s.root); rating.pack()

        def submit():
            try:
                r = int(rating.get())
                if r < 1 or r > 5: raise ValueError
                bookings = load(bookings_file)
                for b in bookings:
                    if b['passenger'] == s.user['phone'] and b['driver'] == driver_phone and b['rating'] is None:
                        b['rating'] = r
                        break
                save(bookings_file, bookings)
                messagebox.showinfo("Thank You", "Your rating has been submitted.")
                s.passenger_dash()
            except:
                messagebox.showerror("Error", "Enter valid rating (1 to 5)")

        tk.Button(s.root, text="✅ Submit Rating", **s.btn_style, command=submit).pack(pady=10)

    # ------------------------------------------------
    # BOOKING HISTORY (Passenger / Driver)
    # ------------------------------------------------
    def view_passenger_bookings(s):
        """Show bookings for logged-in passenger."""
        s.clr(); s.show_logo()
        tk.Label(s.root, text="🧾 My Bookings", **s.title_style).pack(pady=10)
        for b in [b for b in load(bookings_file) if b['passenger'] == s.user['phone']]:
            line = f"From: {b.get('from', '?')} ➡ To: {b.get('to', '?')} | {b['distance']}km | ₹{b['fare']:.2f}"
            if b.get("rating") is not None: line += f" | ⭐ Rating: {b['rating']}"
            tk.Label(s.root, text=line, bg="#e6f2ff").pack()
        tk.Button(s.root, text="🔙 Back", **s.btn_style, command=s.passenger_dash).pack(pady=10)

    def driver_dash(s):
        """Driver dashboard: view bookings."""
        s.clr(); s.show_logo()
        tk.Label(s.root, text=f"🚖 Welcome {s.user['name']} (Driver)", **s.title_style).pack(pady=10)
        tk.Label(s.root, text=f"{s.user['car']} | {s.user['model']} | {s.user['fuel']} | ₹{s.user['fare']}/km | {s.user['discount']}% off", bg="#e6f2ff").pack()
        tk.Button(s.root, text="🧾 My Bookings", **s.btn_style, command=s.view_driver_bookings).pack(pady=5)
        tk.Button(s.root, text="🚪 Logout", **s.btn_style, command=s.menu).pack(pady=10)

    def view_driver_bookings(s):
        """Show bookings received for logged-in driver."""
        s.clr(); s.show_logo()
        tk.Label(s.root, text="📋 Bookings Received", **s.title_style).pack(pady=10)
        for b in [b for b in load(bookings_file) if b['driver'] == s.user['phone']]:
            line = f"From: {b.get('from', '?')} ➡ To: {b.get('to', '?')} | {b['distance']}km | ₹{b['fare']:.2f}"
            if b.get("rating") is not None: line += f" | ⭐ Rating: {b['rating']}"
            tk.Label(s.root, text=line, bg="#e6f2ff").pack()
        tk.Button(s.root, text="🔙 Back", **s.btn_style, command=s.driver_dash).pack(pady=10)

# ---------- Run ----------
if __name__ == '__main__':
    root = tk.Tk()
    app = CabApp(root)
    root.mainloop()
