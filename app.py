from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = "cab-booking-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

drivers_file = os.path.join(BASE_DIR, "drivers.json")
passengers_file = os.path.join(BASE_DIR, "passengers.json")
bookings_file = os.path.join(BASE_DIR, "bookings.json")


# =========================
# JSON FUNCTIONS
# =========================

def load(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# HOME PAGE
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# TERMS
# =========================

@app.route("/terms")
def terms():
    return render_template("terms.html")


# =========================
# PASSENGER LOGIN
# =========================

@app.route("/passenger/login", methods=["GET", "POST"])
def passenger_login():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]

        passengers = load(passengers_file)

        for user in passengers:
            if user.get("phone") == phone and user.get("password") == password:

                session["user"] = user
                session["role"] = "passenger"

                return redirect(url_for("passenger_dashboard"))

        flash("Invalid phone number or password.")

    return render_template("login.html", role="Passenger")


# =========================
# DRIVER LOGIN
# =========================

@app.route("/driver/login", methods=["GET", "POST"])
def driver_login():

    if request.method == "POST":

        phone = request.form["phone"]
        password = request.form["password"]

        drivers = load(drivers_file)

        for user in drivers:
            if user.get("phone") == phone and user.get("password") == password:

                session["user"] = user
                session["role"] = "driver"

                return redirect(url_for("driver_dashboard"))

        flash("Invalid phone number or password.")

    return render_template("login.html", role="Driver")


# =========================
# PASSENGER REGISTER
# =========================

@app.route("/passenger/register", methods=["GET", "POST"])
def passenger_register():

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        password = request.form["password"]

        passengers = load(passengers_file)

        if any(p.get("phone") == phone for p in passengers):
            flash("Phone number already registered.")
            return redirect(url_for("passenger_register"))

        passengers.append({
            "name": name,
            "phone": phone,
            "password": password
        })

        save(passengers_file, passengers)

        flash("Passenger registered successfully!")
        return redirect(url_for("passenger_login"))

    return render_template("register.html", role="Passenger")


# =========================
# DRIVER REGISTER
# =========================

@app.route("/driver/register", methods=["GET", "POST"])
def driver_register():

    if request.method == "POST":

        try:
            name = request.form["name"]
            phone = request.form["phone"]
            password = request.form["password"]
            car = request.form["car"]
            model = request.form["model"]
            fuel = request.form["fuel"]
            car_type = request.form["type"]

            fare = float(request.form["fare"])
            discount = float(request.form["discount"])

            drivers = load(drivers_file)

            if any(d.get("phone") == phone for d in drivers):
                flash("Phone number already registered.")
                return redirect(url_for("driver_register"))

            drivers.append({
                "name": name,
                "phone": phone,
                "password": password,
                "car": car,
                "model": model,
                "fuel": fuel,
                "type": car_type,
                "fare": fare,
                "discount": discount,
                "status": "online"
            })

            save(drivers_file, drivers)

            flash("Driver registered successfully!")
            return redirect(url_for("driver_login"))

        except ValueError:
            flash("Fare and discount must be valid numbers.")

    return render_template("register.html", role="Driver")


# =========================
# PASSENGER DASHBOARD
# =========================

@app.route("/passenger/dashboard")
def passenger_dashboard():

    if session.get("role") != "passenger":
        return redirect(url_for("passenger_login"))

    drivers = [
        d for d in load(drivers_file)
        if d.get("status") == "online"
    ]

    model = request.args.get("model", "All")
    fuel = request.args.get("fuel", "All")
    car_type = request.args.get("type", "All")

    filtered_drivers = drivers

    if model != "All":
        filtered_drivers = [
            d for d in filtered_drivers
            if d.get("model") == model
        ]

    if fuel != "All":
        filtered_drivers = [
            d for d in filtered_drivers
            if d.get("fuel") == fuel
        ]

    if car_type != "All":
        filtered_drivers = [
            d for d in filtered_drivers
            if d.get("type") == car_type
        ]

    models = sorted(set(d.get("model") for d in drivers))
    fuels = sorted(set(d.get("fuel") for d in drivers))
    types = sorted(set(d.get("type") for d in drivers))

    return render_template(
        "passenger_dashboard.html",
        drivers=filtered_drivers,
        models=models,
        fuels=fuels,
        types=types,
        selected_model=model,
        selected_fuel=fuel,
        selected_type=car_type
    )


# =========================
# BOOK CAB
# =========================

@app.route("/book/<driver_phone>", methods=["GET", "POST"])
def book(driver_phone):

    if session.get("role") != "passenger":
        return redirect(url_for("passenger_login"))

    drivers = load(drivers_file)

    driver = next(
        (d for d in drivers if d.get("phone") == driver_phone),
        None
    )

    if not driver:
        flash("Driver not found.")
        return redirect(url_for("passenger_dashboard"))

    if request.method == "POST":

        try:
            from_location = request.form["from"]
            to_location = request.form["to"]
            distance = float(request.form["distance"])

            if not from_location or not to_location:
                flash("Please enter both locations.")
                return redirect(url_for("book", driver_phone=driver_phone))

            base_fare = distance * driver["fare"]

            discount_amount = (
                base_fare * driver["discount"] / 100
            )

            final_fare = base_fare - discount_amount

            bookings = load(bookings_file)

            booking = {
                "passenger": session["user"]["phone"],
                "driver": driver["phone"],
                "from": from_location,
                "to": to_location,
                "distance": distance,
                "fare": final_fare,
                "status": "Completed",
                "rating": None
            }

            bookings.append(booking)

            save(bookings_file, bookings)

            return render_template(
                "receipt.html",
                booking=booking,
                driver=driver,
                passenger=session["user"],
                base_fare=base_fare,
                discount=discount_amount
            )

        except ValueError:
            flash("Please enter a valid distance.")

    return render_template("booking.html", driver=driver)


# =========================
# PASSENGER BOOKINGS
# =========================

@app.route("/passenger/bookings")
def passenger_bookings():

    if session.get("role") != "passenger":
        return redirect(url_for("passenger_login"))

    phone = session["user"]["phone"]

    bookings = [
        b for b in load(bookings_file)
        if b.get("passenger") == phone
    ]

    return render_template(
        "bookings.html",
        bookings=bookings,
        role="Passenger"
    )


# =========================
# DRIVER DASHBOARD
# =========================

@app.route("/driver/dashboard")
def driver_dashboard():

    if session.get("role") != "driver":
        return redirect(url_for("driver_login"))

    return render_template(
        "driver_dashboard.html",
        driver=session["user"]
    )


# =========================
# DRIVER BOOKINGS
# =========================

@app.route("/driver/bookings")
def driver_bookings():

    if session.get("role") != "driver":
        return redirect(url_for("driver_login"))

    phone = session["user"]["phone"]

    bookings = [
        b for b in load(bookings_file)
        if b.get("driver") == phone
    ]

    return render_template(
        "bookings.html",
        bookings=bookings,
        role="Driver"
    )


# =========================
# RATE DRIVER
# =========================

@app.route("/rate/<driver_phone>", methods=["POST"])
def rate_driver(driver_phone):

    if session.get("role") != "passenger":
        return redirect(url_for("passenger_login"))

    try:
        rating = int(request.form["rating"])

        if rating < 1 or rating > 5:
            raise ValueError

        bookings = load(bookings_file)

        for booking in bookings:

            if (
                booking["passenger"] == session["user"]["phone"]
                and booking["driver"] == driver_phone
                and booking.get("rating") is None
            ):
                booking["rating"] = rating
                break

        save(bookings_file, bookings)

        flash("Thank you! Your rating has been submitted.")

    except ValueError:
        flash("Rating must be between 1 and 5.")

    return redirect(url_for("passenger_bookings"))


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# =========================
# RESET DATA
# =========================

@app.route("/reset")
def reset():

    save(drivers_file, [])
    save(passengers_file, [])
    save(bookings_file, [])

    flash("All data has been reset.")

    return redirect(url_for("index"))


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
