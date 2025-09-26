from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12799494",
        password="CLs6xYMIJL",
        database="sql12799494"
    )
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
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
        return redirect(url_for("index"))

    # Handle Stock Add/Remove/Delete via query params
    action = request.args.get("action")
    product_id = request.args.get("id")
    if action and product_id:
        cursor.execute("SELECT Quantity FROM Products WHERE Id=%s", (product_id,))
        product = cursor.fetchone()
        if product:
            qty = product["Quantity"]
            if action == "add_stock":
                add_qty = int(request.args.get("qty", 0))
                qty += add_qty
            elif action == "remove_stock":
                remove_qty = int(request.args.get("qty", 0))
                if remove_qty <= qty:
                    qty -= remove_qty
            elif action == "delete":
                cursor.execute("DELETE FROM Products WHERE Id=%s", (product_id,))
                conn.commit()
                return redirect(url_for("index"))
            cursor.execute("UPDATE Products SET Quantity=%s WHERE Id=%s", (qty, product_id))
            conn.commit()
            return redirect(url_for("index"))

    # Fetch products for display
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    overall_total = sum(p["Quantity"] * p["CostPrice"] for p in products)
    conn.close()
    return render_template("index.html", products=products, overall_total=overall_total)

if __name__ == "__main__":
    app.run(debug=True)
