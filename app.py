from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "mysecretkeyofInventoNetDB123"  # Needed for session management

# ---------------- Database Connection ---------------- #
def get_db_connection():
    conn = mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12799494",
        password="CLs6xYMIJL",
        database="sql12799494"
    )
    return conn

# ---------------- Login Page ---------------- #
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_user = request.form["login"]
        password_user = request.form["password"]

        # Hash the password before checking
        hashed_password = hashlib.sha256(password_user.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM User_Invento WHERE login=%s AND password=%s", (login_user, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = user["login"]
            return redirect(url_for("inventory"))
        else:
            flash("Invalid login or password!", "danger")

    return render_template("login.html")

# ---------------- Inventory Page ---------------- #
@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Handle Add Product
    if request.method == "POST" and "add_product" in request.form:
        name = request.form["name"]
        quantity = int(request.form["quantity"])
        cost = float(request.form["cost"])
        selling = float(request.form["selling"])
        cursor.execute(
            "INSERT INTO Products (Name, Quantity, CostPrice, SellingPrice) VALUES (%s,%s,%s,%s)",
            (name, quantity, cost, selling)
        )
        conn.commit()
        return redirect(url_for("inventory"))

    # Handle Add/Remove Stock
    if request.method == "POST" and ("add_stock" in request.form or "remove_stock" in request.form):
        product_id = int(request.form["product_id"])
        qty_change = int(request.form["qty_change"])
        cursor.execute("SELECT Quantity FROM Products WHERE Id=%s", (product_id,))
        product = cursor.fetchone()
        if product:
            qty = product["Quantity"]
            if "add_stock" in request.form:
                qty += qty_change
            elif "remove_stock" in request.form:
                qty = max(0, qty - qty_change)
            cursor.execute("UPDATE Products SET Quantity=%s WHERE Id=%s", (qty, product_id))
            conn.commit()
        return redirect(url_for("inventory"))

    # Handle Delete
    action = request.args.get("action")
    product_id = request.args.get("id")
    if action == "delete" and product_id:
        cursor.execute("DELETE FROM Products WHERE Id=%s", (product_id,))
        conn.commit()
        return redirect(url_for("inventory"))

    # Fetch products
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    overall_total = sum(p["Quantity"] * p["CostPrice"] for p in products)
    conn.close()
    return render_template("inventory.html", products=products, overall_total=overall_total, user=session["user"])

# ---------------- Logout ---------------- #
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
