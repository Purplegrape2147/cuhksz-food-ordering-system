from flask import Flask, request, jsonify
import sqlite3
import bcrypt
from pathlib import Path

app = Flask(__name__)

DB_PATH = Path(__file__).resolve().parent / "databases" / "food_ordering.db"


def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def clean_unicode(s: str) -> str:
    if not isinstance(s, str):
        return s
    return s.encode("utf-8", "surrogatepass").decode("utf-8", "replace")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    name = data["name"]
    address = data["address"]
    phone = data["phone"]

    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Account WHERE Username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Username already exists"}), 400

    # Generate a 5-digit AccountID
    cur.execute("SELECT MAX(AccountID) FROM Account;")
    max_id = cur.fetchone()[0] or 10000
    new_id = max_id + 1

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    cur.execute("""
        INSERT INTO Account (AccountID, Username, Password, Role, Name, Address, Phone)
        VALUES (?, ?, ?, 'USER', ?, ?, ?);
    """, (new_id, username, hashed_password, name, address, phone))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "account_id": new_id})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT AccountID, Role, Name, Address, Password
        FROM Account
        WHERE Username = ?;
    """, (username,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    stored_hash = row["Password"]

    ok = False

    # Try bcrypt
    try:
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            ok = True
    except Exception:
        if stored_hash == password:
            ok = True

    if not ok:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    return jsonify({
        "success": True,
        "account_id": row["AccountID"],
        "role": row["Role"],
        "name": row["Name"],
        "address": row["Address"]
    })


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Account WHERE AccountID = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify(dict(row))


@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_order_history(user_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.OrderID, o.Status, o.DeliveryAddress, o.OrderTime, a.Name AS UserName, s.Name AS StoreName, d.Name AS DriverName,
        COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0) AS TotalPrice
        FROM Orders o
        JOIN Account a ON o.UserID = a.AccountID
        JOIN Store s ON o.StoreID = s.StoreID
        LEFT JOIN Driver d ON o.DriverID = d.DriverID
        LEFT JOIN OrderItem oi on oi.OrderID = o.OrderID
        WHERE o.UserID = ?
        GROUP BY o.OrderID
        ORDER BY o.OrderID DESC;
    """, (user_id, ))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_account_information(user_id):
    data = request.get_json() or {}

    fields = []
    params = []

    if "name" in data and data["name"]:
        fields.append("Name = ?")
        params.append(data["name"])
    if "address" in data and data["address"]:
        fields.append("Address = ?")
        params.append(data["address"])
    if "phone" in data and data["phone"]:
        fields.append("Phone = ?")
        params.append(data["phone"])
    if "password" in data and data["password"]:
        hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
        fields.append("Password = ?")
        params.append(hashed_pw)

    if not fields:
        return jsonify({"success": False, "message": "No fields to update"}), 400

    params.append(user_id)

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE Account SET {', '.join(fields)} WHERE AccountID = ?", params)
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Account information updated successfully"})


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order_details(order_id):
    user_id = request.args.get("user_id", type=int)

    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Orders WHERE OrderID = ?", (order_id,))
    order_row = cur.fetchone()

    if order_row is None:
        conn.close()
        return jsonify({"success": False, "message": "Order not found"}), 404

    if order_row["UserID"] != user_id:
        conn.close()
        return jsonify({"success": False, "message": "You cannot view this order"}), 403

    cur.execute("""
        SELECT oi.OrderItemID, oi.Quantity, oi.UnitPrice, m.Name
        FROM OrderItem oi
        JOIN MenuItem m ON oi.MenuItemID = m.MenuItemID
        WHERE oi.OrderID = ?
    """, (order_id,))
    items = [dict(item) for item in cur.fetchall()]
    conn.close()

    return jsonify({
        "OrderID": order_id,
        "OrderTime": order_row["OrderTime"],
        "UserID": order_row["UserID"],
        "StoreID": order_row["StoreID"],
        "DeliveryAddress": order_row["DeliveryAddress"],
        "items": items
    })


@app.route("/orders/<int:order_id>/confirm", methods=["POST"])
def confirm_order(order_id):
    data = request.get_json()
    user_id = data.get("user_id")

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT UserID, Status FROM Orders WHERE OrderID = ?", (order_id, ))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return jsonify({"success": False, "message": "Order not found"}), 404

    if row["UserID"] != user_id:
        conn.close()
        return jsonify({"success": False, "message": "You cannot confirm this order"}), 403

    if row["Status"] != "SHIPPED":
        conn.close()
        return jsonify({"success": False, "message": "Wait until the order has been shipped to mark as complete"}), 400

    # Update order status
    cur.execute("""
        UPDATE Orders
        SET Status = 'COMPLETED'
        WHERE OrderID = ?;
    """, (order_id, ))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Order marked as completed. Thank you for using our service!"})


@app.route("/orders/<int:order_id>/edit_address", methods=["POST"])
def edit_address(order_id):
    data = request.get_json()
    user_id = data.get("user_id")
    mod_address = data.get("mod_address")

    if user_id is None or not mod_address:
        return jsonify({"success": False, "message": "User ID and changed address not found"}), 404

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT UserID, Status FROM Orders WHERE OrderID = ?", (order_id, ))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return jsonify({"success": False, "message": "Order not found"}), 404

    if row["UserID"] != user_id:
        conn.close()
        return jsonify({"success": False, "message": "You cannot modify this order"}), 403

    if row["Status"] != "UNSHIPPED":
        conn.close()
        return jsonify({"success": False, "message": "Only UNSHIPPED orders can be modified"}), 400

    # Modify address
    cur.execute("""
        UPDATE Orders
        SET DeliveryAddress = ?
        WHERE OrderID = ?;
    """, (mod_address, order_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Successfully modified delivery address"})


@app.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if user_id is None:
        return jsonify({"success": False, "message": "User ID not found"}), 404

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT UserID, Status FROM Orders WHERE OrderID = ?", (order_id, ))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return jsonify({"success": False, "message": "Order not found"}), 404

    if row["UserID"] != user_id:
        conn.close()
        return jsonify({"success": False, "message": "You cannot cancel this order"}), 403

    if row["Status"] != "UNSHIPPED":
        conn.close()
        return jsonify({"success": False, "message": "Only UNSHIPPED orders can be cancelled"}), 400

    # Delete order record
    cur.execute("DELETE FROM OrderItem WHERE OrderID = ?", (order_id,))
    cur.execute("DELETE FROM Orders WHERE OrderID = ?", (order_id, ))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Successfully cancelled order\n"})


@app.route("/stores", methods=["GET"])
def get_stores():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT StoreID, Name, Location FROM Store")
    rows = cur.fetchall()
    conn.close()

    stores = [dict(r) for r in rows]
    return jsonify(stores)


@app.route("/menu/<int:store_id>", methods=["GET"])
def get_menu(store_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT MenuItemID, Name, Price FROM MenuItem WHERE StoreID = ?", (store_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    store_id = data["store_id"]
    user_id = data["user_id"]
    address = data["delivery_address"]
    items = data.get("items", [])

    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Orders (StoreID, UserID, Status, DeliveryAddress) 
            VALUES (?, ?, 'UNSHIPPED', ?)
        """, (store_id, user_id, address)
        )
        order_id = cur.lastrowid

        if items:
            q_marks = ",".join("?" * len(items))
            ids = [i["menu_item_id"] for i in items]
            cur.execute(f"SELECT MenuItemID, Price FROM MenuItem WHERE MenuItemID IN ({q_marks})", ids)
            price_map = {row["MenuItemID"]: float(row["Price"]) for row in cur.fetchall()}

            for it in items:
                mid = it["menu_item_id"]
                qty = int(it["quantity"])
                if mid not in price_map or qty <= 0:
                    conn.rollback()
                    return jsonify({"success": False, "message": f"Invalid item/qty: {mid}, {qty}"}), 400
                cur.execute("""
                    INSERT INTO OrderItem (OrderID, MenuItemID, Quantity, UnitPrice) 
                    VALUES (?, ?, ?, ?) 
                """, (order_id, mid, qty, price_map[mid])
                )

        conn.commit()
        return jsonify({"success": True, "order_id": order_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route("/admin/orders/unshipped", methods=["GET"])
def get_unshipped_orders():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.OrderID, o.Status, o.DeliveryAddress, o.OrderTime,
               a.AccountID AS UserID, a.Name AS UserName,
               s.StoreID, s.Name AS StoreName,
               d.Name AS DriverName,
               COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0) AS TotalPrice
        FROM Orders o
        JOIN Account a ON o.UserID = a.AccountID
        JOIN Store s ON o.StoreID = s.StoreID
        LEFT JOIN Driver d ON o.DriverID = d.DriverID
        LEFT JOIN OrderItem oi ON oi.OrderID = o.OrderID
        WHERE o.Status = 'UNSHIPPED'
        GROUP BY o.OrderID
        ORDER BY o.OrderID ASC;
    """)
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/orders/<int:order_id>/assign", methods=["POST"])
def assign_driver(order_id):
    data = request.get_json()
    driver_id = data.get("driver_id")

    if driver_id is None:
        return jsonify({"success": False, "message": "Driver ID missing"}), 400

    conn = get_db_conn()
    cur = conn.cursor()

    # Check if the order exists and is UNSHIPPED
    cur.execute("SELECT Status FROM Orders WHERE OrderID = ?", (order_id,))
    row1 = cur.fetchone()

    if row1 is None:
        conn.close()
        return jsonify({"success": False, "message": "Order not found"}), 404
    if row1["Status"] != "UNSHIPPED":
        conn.close()
        return jsonify({"success": False, "message": "Order is not unshipped"}), 400

    # Check if the driver exists and is ACTIVE
    cur.execute("SELECT IsActive FROM Driver WHERE DriverID = ?", (driver_id,))
    row2 = cur.fetchone()

    if row2 is None:
        conn.close()
        return jsonify({"success": False, "message": "Driver not found"}), 404

    if row2["IsActive"] != 1:
        conn.close()
        return jsonify({"success": False, "message": "Driver is NOT active"}), 400

    # Assign driver
    cur.execute("""
        UPDATE Orders
        SET DriverID = ?
        WHERE OrderID = ?;
    """, (driver_id, order_id))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Driver assigned successfully"})


@app.route("/admin/orders/<int:order_id>/ship", methods=["POST"])
def mark_shipped(order_id):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT Status FROM Orders WHERE OrderID = ?", (order_id,))
    row = cur.fetchone()

    if row is None:
        return jsonify({"success": False, "message": "Order not found"}), 404
    if row["Status"] != "UNSHIPPED":
        return jsonify({"success": False, "message": "Order is not unshipped"}), 400

    cur.execute("""
        UPDATE Orders
        SET Status = 'SHIPPED'
        WHERE OrderID = ?;
    """, (order_id,))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Order marked as SHIPPED"})


@app.route("/admin/drivers", methods=["GET"])
def get_all_drivers():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Driver ORDER BY DriverID")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/drivers/active", methods=["GET"])
def get_active_drivers():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Driver WHERE IsActive = 1")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/drivers/<int:driver_id>/set_active", methods=["POST"])
def update_driver_active(driver_id):
    data = request.get_json()
    is_active = data.get("is_active")

    if is_active not in [True, False]:
        return jsonify({"success": False, "message": "is_active must be True/False"}), 400

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Driver WHERE DriverID = ?", (driver_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return jsonify({"success": False, "message": "Driver not found"}), 404

    cur.execute("""
        UPDATE Driver 
        SET IsActive = ? 
        WHERE DriverID = ?
    """,(1 if is_active else 0, driver_id))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Driver status updated"})


@app.route("/admin/drivers/create", methods=["POST"])
def create_driver():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")

    if not name or not phone:
        return jsonify({"success": False, "message": "Missing driver info"}), 400

    conn = get_db_conn()
    cur = conn.cursor()

    # Create new ID
    cur.execute("SELECT MAX(DriverID) FROM Driver")
    max_id = cur.fetchone()[0] or 200
    new_id = max_id + 1

    cur.execute("""
        INSERT INTO Driver (DriverID, Name, Phone, IsActive)
        VALUES (?, ?, ?, 1)
    """, (new_id, name, phone))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Driver added", "driver_id": new_id})


@app.route("/admin/drivers/<int:driver_id>/edit", methods=["POST"])
def edit_driver(driver_id):
    data = request.get_json() or {}
    name = data.get("name")
    phone = data.get("phone")

    if not name and not phone:
        return jsonify({"success": False, "message": "No fields to update"}), 400

    conn = get_db_conn()
    cur = conn.cursor()

    # Check driver exists
    cur.execute("SELECT * FROM Driver WHERE DriverID = ?", (driver_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"success": False, "message": "Driver not found"}), 404

    fields = []
    params = []

    if name:
        fields.append("Name = ?")
        params.append(clean_unicode(name))

    if phone:
        fields.append("Phone = ?")
        params.append(clean_unicode(phone))

    params.append(driver_id)

    sql = "UPDATE Driver SET " + ", ".join(fields) + " WHERE DriverID = ?"

    cur.execute(sql, params)
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Driver updated successfully"})


@app.route("/admin/stores", methods=["GET"])
def get_all_stores():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Store ORDER BY StoreID")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/stores/create", methods=["POST"])
def create_store():
    data = request.get_json()
    name = data.get("name")
    location = data.get("location")

    if not name or not location:
        return jsonify({"success": False, "message": "Missing name or location"}), 400

    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT MAX(StoreID) FROM Store")
    max_id = cur.fetchone()[0] or 100
    new_id = max_id + 1

    cur.execute("""
        INSERT INTO Store (StoreID, Name, Location)
        VALUES (?, ?, ?)
    """, (new_id, name, location))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Store added successfully", "store_id": new_id})


@app.route("/admin/stores/<int:store_id>/edit", methods=["POST"])
def edit_store(store_id):
    data = request.get_json() or {}
    name = data.get("name")
    location = data.get("location")

    if not name and not location:
        return jsonify({"success": False, "message": "No fields to update"}), 400

    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Store WHERE StoreID = ?", (store_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"success": False, "message": "Store not found"}), 404

    fields = []
    params = []

    if name:
        fields.append("Name = ?")
        params.append(name)
    if location:
        fields.append("Location = ?")
        params.append(location)

    params.append(store_id)

    cur.execute(f"UPDATE Store SET {', '.join(fields)} WHERE StoreID = ?", params)
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Store updated successfully"})


@app.route("/admin/stores/<int:store_id>/delete", methods=["POST"])
def delete_store(store_id):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Store WHERE StoreID = ?", (store_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"success": False, "message": "Store not found"}), 404

    # Delete store and its menu items
    cur.execute("DELETE FROM MenuItem WHERE StoreID = ?", (store_id,))
    cur.execute("DELETE FROM Store WHERE StoreID = ?", (store_id, ))

    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Store deleted successfully"})


@app.route("/admin/stores/<int:store_id>/menu", methods=["GET"])
def admin_get_menu(store_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT MenuItemID, Name, Price FROM MenuItem WHERE StoreID = ?", (store_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/admin/stores/<int:store_id>/menu/add", methods=["POST"])
def admin_add_menu_item(store_id):
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")

    if not name or price is None:
        return jsonify({"success": False, "message": "Name and price required"}), 400

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO MenuItem (StoreID, Name, Price)
        VALUES (?, ?, ?)
    """, (store_id, name, price))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Menu item added"})


@app.route("/admin/menu/<int:item_id>/edit", methods=["POST"])
def admin_edit_menu_item(item_id):
    data = request.get_json()
    new_name = data.get("name")
    new_price = data.get("price")

    if not new_name and new_price is None:
        return jsonify({"success": False, "message": "Nothing to update"}), 400

    conn = get_db_conn()
    cur = conn.cursor()

    # Check exist
    cur.execute("SELECT * FROM MenuItem WHERE MenuItemID = ?", (item_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"success": False, "message": "Menu item not found"}), 404

    fields = []
    params = []

    if new_name:
        fields.append("Name = ?")
        params.append(new_name)

    if new_price is not None:
        fields.append("Price = ?")
        params.append(new_price)

    params.append(item_id)

    cur.execute(f"UPDATE MenuItem SET {', '.join(fields)} WHERE MenuItemID = ?", params)
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Menu item updated"})


@app.route("/admin/menu/<int:item_id>/delete", methods=["POST"])
def admin_delete_menu_item(item_id):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM MenuItem WHERE MenuItemID = ?", (item_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"success": False, "message": "Menu item not found"}), 404

    cur.execute("DELETE FROM MenuItem WHERE MenuItemID = ?", (item_id,))
    conn.commit()
    conn.close()

    return (jsonify({"success": True, "message": "Menu item deleted"}))


@app.route("/admin/orders", methods=["GET"])
def admin_all_orders():
    status = request.args.get("status")
    store_id = request.args.get("store_id")
    user_id = request.args.get("user_id")

    conn = get_db_conn()
    cur = conn.cursor()

    query = """
        SELECT o.OrderID, o.UserID, o.Status, o.DeliveryAddress, o.OrderTime, a.Name AS UserName, 
               s.StoreID, s.Name AS StoreName, d.Name AS DriverName,
               COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0) AS TotalPrice
        FROM Orders o
        JOIN Account a ON o.UserID = a.AccountID
        JOIN Store s ON o.StoreID = s.StoreID
        LEFT JOIN Driver d ON o.DriverID = d.DriverID
        LEFT JOIN OrderItem oi ON oi.OrderID = o.OrderID
    """

    filters = []
    params = []

    if status:
        filters.append("o.Status = ?")
        params.append(status)

    if store_id:
        filters.append("o.StoreID = ?")
        params.append(store_id)

    if user_id:
        filters.append("o.UserID = ?")
        params.append(user_id)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " GROUP BY o.OrderID ORDER BY o.OrderID DESC"

    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True)
