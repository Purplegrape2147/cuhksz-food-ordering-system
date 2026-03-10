import requests
from ui import render_table, banner_title, section, success, error, info
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"


def to_local(ts):
    """Convert UTC timestamp string to China Standard Time (UTC+8)."""
    if not ts:
        return ts
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return (dt + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    except:
        return ts


def main():
    while True: # Home page loop
        banner_title("🍱  CUHK(SZ) FOOD ORDERING SYSTEM  🍱")
        section("Welcome", "👋")
        home_page_choice = input(" Choose login (L) or register (R): ").upper()

        # 0) Register account
        if home_page_choice == "R":
            section("Registering an Account ᕙ(  •̀ ᗜ •́  )ᕗ", "📝")

            username = input("Create username: ")
            password = input("Create password: ")
            name = input("Your name: ")
            address = input("Address: ")
            phone = input("Your phone number: ")

            resp = requests.post(f"{BASE_URL}/register", json={
                "username": username,
                "password": password,
                "name": name,
                "address": address,
                "phone": phone
            })

            if not resp.ok:
                error(resp.json().get("message"))
                continue

            success("Registration successful! Please log in.")
            continue

        # 1) Login
        elif home_page_choice == "L":
            while True: # Login loop
                section("Login", "🔑")
                username = input("Username: ")
                password = input("Password: ")
                resp = requests.post(f"{BASE_URL}/login", json={
                    "username": username,
                    "password": password
                })

                if resp.ok:
                    data = resp.json()
                    break

                error(resp.json().get("message"))
                retry = input("Retry login? (type Y to retry, anything else to return to home page): ").upper()
                if retry != "Y":
                    break

            if not resp.ok:
                continue

            success(f"Welcome, {data['name']}!  ({data['role']})")
            user_id = int(data["account_id"])
            addr_from_login = data.get("address")

            info("You are now logged in! Taking you to the main menu...")

            # Main Menu for Admin
            if data["role"] == "ADMIN":
                admin_menu(user_id)

            # Main Menu for User
            else:
                user_menu(user_id, addr_from_login)


#----------
#-- User --
#----------

def user_menu(user_id, addr_from_login):
    while True:  # Main menu loop
        banner_title("🍽️  User Main Menu  🍽️")
        print("(1) 🏪 Browse stores")
        print("(2) 🍛 View order history")
        print("(3) 👤 Update account information")
        print("(4) 🚪 Logout")

        choice = input("Choose an option (1/2/3/4): ")

        if choice == "1":
            browse_stores(user_id, addr_from_login)

        elif choice == "2":
            addr_from_login = view_user_order_history(user_id, addr_from_login)

        elif choice == "3":
            addr_from_login = update_account_info(user_id, addr_from_login)

        elif choice == "4":
            info("\nLogging out...")
            return

        else:
            error("Invalid choice.")


def browse_stores(user_id, addr_from_login):
    section("Browse Stores", "🏪")
    print("Which store to order from today?")

    # List stores
    resp = requests.get(f"{BASE_URL}/stores")
    if not resp.ok:
        error(f"Failed to load stores: {resp.text}")
        return
    stores = resp.json()

    print("\nAvailable stores:")
    print_store_table(stores)

    # Pick a store and view menu
    while True:
        try:
            store_id = int(input("\nEnter store id to view menu: "))
            break
        except ValueError:
            error("Please enter a number.")

    if store_id not in [s["StoreID"] for s in stores]:
        error("Invalid store ID.")
        return

    resp = requests.get(f"{BASE_URL}/menu/{store_id}")
    if not resp.ok:
        error(f"Failed to load menu: {resp.text}")
        return
    menu = resp.json()

    # if not menu:
    #     print("No menu items available yet in this store.")

    section(f"Menu for Store {store_id}", "🍱")

    menu_catalog = {item['MenuItemID']:
                        {"name": item['Name'],
                         "price": float(item['Price'])
                         } for item in menu
                    }

    # for item in menu:
    #     print(f"{item['MenuItemID']} - {item['Name']} : {item['Price']}")

    print_menu_table(menu)

    # Create an order
    # Add menu items to cart
    cart = []
    while True:
        sub_order = input(
            "\nEnter the id of the menu item you would like to eat, as well as the quantity (id, quantity) or press Enter to check out: ")
        if sub_order == "":
            break
        try:
            menu_item_id, quantity = [int(i) for i in sub_order.split(",")]
            if menu_item_id not in menu_catalog:
                error("This menu item ID isn't in this store's menu. Try again.")
                continue
            if quantity <= 0:
                error("You must order a positive quantity.")
                continue
            cart.append({"menu_item_id": menu_item_id, "quantity": quantity})
        except Exception:
            error("Write in the format (id, quantity), e.g. 1000, 1")

    if not cart:
        error("Your cart is still empty. Please add an item before checking out.")
        return

    # Calculate total price
    summary_rows = []
    total_price = 0

    for i in cart:
        name = menu_catalog[i["menu_item_id"]]["name"]
        price = menu_catalog[i["menu_item_id"]]["price"]
        quantity = i["quantity"]
        subtotal = price * quantity
        total_price += subtotal

        summary_rows.append({
            "Name": name,
            "Qty": quantity,
            "UnitPrice": f"¥{price}",
            "Subtotal": f"¥{subtotal}"
        })

    section("Order Summary", "🧾")
    headers = ["Name", "Qty", "UnitPrice", "Subtotal"]
    render_table(headers, summary_rows, border_style="bold")
    print(f" Total Price: ¥{total_price}")

    # Confirm the delivery address
    useDefault = input("\nUse default address (Y/N)?: ").upper()
    if useDefault == "Y":
        addr = addr_from_login
    else:
        addr = input("Enter your delivery address: ")

    # Create the order
    create = requests.post(f"{BASE_URL}/orders", json={
        "store_id": store_id,
        "user_id": user_id,
        "delivery_address": addr,
        "items": cart
    })
    if not create.ok:
        error(f"Failed to create order: {create.text}")
        return
    success("Order created successfully!")
    info(f"Order ID: {create.json().get('order_id', '(N/A)')}")


def view_user_order_history(user_id, addr_from_login):
    section("Your Order History", "📜")
    resp = requests.get(f"{BASE_URL}/users/{user_id}/orders")

    if not resp.ok:
        error(f"Failed to load order history: {resp.text}")
        return addr_from_login

    orders = resp.json()

    if not orders:
        info("You have no past orders. Go make your first one!")
        return addr_from_login

    print_user_order_history_table(orders)

    print("\nWhat would you like to do?")
    print("(1) View order breakdown")
    print("(2) Modify an UNSHIPPED order")
    print("(3) Confirm an order")
    print("(4) Back")

    action = input("Choose (1/2/3/4): ").strip()

    # (1) View order breakdown
    if action == "1":
        order_id = input("Enter an Order ID to view breakdown or press Enter to go back: ")
        view_order_breakdown(order_id, user_id)

    # (2) Modify an UNSHIPPED order
    elif action == "2":
        order_id = input("\nEnter an UNSHIPPED Order ID to modify or press Enter to go back: ")
        modify_unshipped_order(orders, order_id, user_id)

    # (3) Confirm order
    elif action == "3":
        order_id = input("\nEnter an Order ID to confirm receipt or press Enter to go back: ")
        confirm_order(order_id, user_id)

    # (4) Go back
    elif action == "4":
        return addr_from_login

    else:
        error("Invalid action.")

    return addr_from_login

def view_order_breakdown(order_id, user_id):
    if order_id:
        try:
            order_id = int(order_id)
        except ValueError:
            error("Invalid Order ID.")
            return

        detail_resp = requests.get(f"{BASE_URL}/orders/{order_id}", params={"user_id": user_id})

        if not detail_resp.ok:
            error(f"Failed to load order details: {detail_resp.text}")
            return

        # View order details (breakdown of items)
        order_details = detail_resp.json().get("items", [])
        section(f"Order Breakdown #{order_id}", "🍛")
        for item in order_details:
            item_paid = item["Quantity"] * item["UnitPrice"]
            print(f" - {item['Name']}  x{item['Quantity']}  ¥{item_paid}")

        info(f"Ordered at: {to_local(detail_resp.json().get('OrderTime'))}")


def modify_unshipped_order(orders, order_id, user_id):
    if not order_id:
        return

    try:
        mod_order_id = int(order_id)
    except ValueError:
        error("Invalid Order ID.")
        return

    match = None
    for order in orders:
        if order["OrderID"] == mod_order_id:
            match = order
            break

    if match is None:
        error("Order ID not found in your history.")
        return

    if match["Status"] != "UNSHIPPED":
        error("You can only modify UNSHIPPED orders!")
        return

    section(f"Modify Order {mod_order_id}", "🛠️")
    print(f"\nOrder {mod_order_id} is UNSHIPPED. Would you like to:")
    print("(A) Modify Address"
          "\n(C) Cancel Order")
    action = input("Type (A/C) or press Enter to return: ").strip().upper()

    # (A) Modify address
    if action == "A":
        mod_address = input("Where would you like this order to be delivered?: ")
        if not mod_address:
            info("You have not changed the address.")
            return
        mod_resp = requests.post(f"{BASE_URL}/orders/{mod_order_id}/edit_address", json={"user_id": user_id, "mod_address": mod_address})

        if not mod_resp.ok:
            try:
                msg = mod_resp.json().get("message")
            except Exception:
                msg = mod_resp.text
            error(f"Failed to modify address: {msg}")
        else:
            success("Delivery address updated successfully!")

    # (C) Cancel order
    elif action == "C":
        cancel_resp = requests.post(f"{BASE_URL}/orders/{mod_order_id}/cancel", json={"user_id": user_id})

        if not cancel_resp.ok:
            try:
                msg = cancel_resp.json().get("message")
            except Exception:
                msg = cancel_resp.text
            error(f"Failed to cancel order {msg}")
        else:
            success(cancel_resp.json().get("message", "Order cancelled."))

    else:
        info("No modification performed")


def confirm_order(order_id, user_id):
    if order_id:
        try:
            order_id = int(order_id)
        except ValueError:
            error("Invalid Order ID.")
            return

        confirm_resp = requests.post(f"{BASE_URL}/orders/{order_id}/confirm", json={"user_id": user_id})
        if not confirm_resp.ok:
            try:
                msg = confirm_resp.json().get("message")
            except Exception:
                msg = confirm_resp.text
            error(f"Failed to confirm order: {msg}")
        else:
            print("", confirm_resp.json().get("message"))


def update_account_info(user_id, addr_from_login):
    section("Update Account Information", "👤")
    info("Press Enter to keep current value.")

    new_name = input("New name: ")
    new_address = input("New address: ")
    new_phone = input("New phone: ")
    new_password = input("New password: ")

    update_data = {}
    if new_name:
        update_data["name"] = new_name
    if new_address:
        update_data["address"] = new_address
    if new_phone:
        update_data["phone"] = new_phone
    if new_password:
        update_data["password"] = new_password

    if not update_data:
        info("No changes made.")
        return addr_from_login

    resp = requests.post(f"{BASE_URL}/users/{user_id}/edit", json=update_data)
    if not resp.ok:
        error(resp.json().get("message", resp.text))
        return addr_from_login

    success("Account information modified successfully.")

    refreshed = requests.get(f"{BASE_URL}/users/{user_id}").json()

    return refreshed.get("Address", addr_from_login)



#-----------
#-- Admin --
#-----------
def admin_menu(user_id):
    while True:  # Main menu loop
        banner_title("🛠️ Admin Main Menu 🛠️")
        print("(1) 🍛 Manage unshipped orders")
        print("(2) 🛵 Manage delivery staff information")
        print("(3) 🏪 Manage store information")
        print("(4) 📜 View combined order history")
        print("(5) 👤 Update admin account information")
        print("(6) 🚪 Logout")

        choice = input("Choose an option (1/2/3/4/5/6): ")

        if choice == "1":
            manage_unshipped_orders()

        elif choice == "2":
            manage_delivery_staff_info()

        elif choice == "3":
            manage_store_info()

        elif choice == "4":
            view_combined_history()

        elif choice == "5":
            edit_admin_account(user_id)

        elif choice == "6":
            info("\nLogging out...")
            return

        else:
            error("Invalid choice. Try again.")


def manage_unshipped_orders():
    section("Manage Unshipped Orders", "🍛")

    resp = requests.get(f"{BASE_URL}/admin/orders/unshipped")

    if not resp.ok:
        error(f"Failed to load unshipped orders: {resp.text}")
        return

    unshipped_orders = resp.json()

    if not unshipped_orders:
        print("There are no unshipped orders to manage.")
        return

    print("\nUnshipped orders:")
    print_order_table(unshipped_orders)

    order_to_manage_input = input("\nChoose an order to manage, or press Enter to go back: ")

    if not order_to_manage_input:
        return

    if order_to_manage_input:
        try:
            order_to_manage = int(order_to_manage_input)
        except ValueError:
            error("Invalid Order ID.")
            return

    # Choose action
    print("\nWhat would you like to do?")
    print("(A) Assign a driver")
    print("(S) Mark as shipped")
    print("(C) Cancel (go back)")
    action = input("Choose (A/S/C): ").strip().upper()

    # Assign (A) a delivery staff
    if action == "A":
        # Get active drivers
        drivers_resp = requests.get(f"{BASE_URL}/admin/drivers/active")
        if not drivers_resp.ok:
            error(f"Failed to load drivers: {drivers_resp.text}")
            return

        drivers = drivers_resp.json()
        if not drivers:
            print("No active drivers available!")
            return

        print("\nAvailable Active Drivers:")
        # print("────────────────────────────────────────")
        # for driver in drivers:
        #     print(f"Driver ID: {driver['DriverID']} | Name: {driver['Name']}")
        # print("────────────────────────────────────────")

        print_driver_table(drivers)

        driver_id_input = input("\nEnter Driver ID to assign: ")
        try:
            driver_id = int(driver_id_input)
        except ValueError:
            error("Invalid Driver ID.")
            return

        assign_resp = requests.post(f"{BASE_URL}/admin/orders/{order_to_manage}/assign", json={"driver_id": driver_id})

        if not assign_resp.ok:
            error(f"Failed to assign driver: {assign_resp.text}")
        else:
            success(assign_resp.json().get("message"))

    # Mark SHIPPED (S) an order
    elif action == "S":
        ship_resp = requests.post(f"{BASE_URL}/admin/orders/{order_to_manage}/ship")

        if not ship_resp.ok:
            error(f"Failed to ship order: {ship_resp.text}")
        else:
            print(ship_resp.json().get("message"))

    else:
        print("Returning to admin menu...")


def manage_delivery_staff_info():
    section("Delivery Staff Management", "🛵")

    while True:
        # Show all drivers
        resp = requests.get(f"{BASE_URL}/admin/drivers")
        if not resp.ok:
            print("Error loading drivers")
            return
        drivers = resp.json()

        print("\nAll drivers: ")
        print_driver_table(drivers)

        print("Actions:")
        print("(1) Set active / inactive a driver")
        print("(2) Edit driver info")
        print("(3) Add new driver")
        print("(4) Back")

        choice = input("\nChoose (1/2/3/4): ").strip()

        # (1) Set active / inactive
        if choice == "1":
            driver_id = input("Enter Driver ID: ")

            if not driver_exists(driver_id, drivers):
                print("Driver ID does not exist! Please try again.")
                continue

            # Set status
            status = input("Set Active or Inactive? (A/I): ").strip().upper()
            if status not in ["A", "I"]:
                error("Invalid choice.")
                continue
            is_active = True if status == "A" else False

            resp = requests.post(f"{BASE_URL}/admin/drivers/{driver_id}/set_active", json={"is_active": is_active})
            print(resp.json().get("message"))

        # (2) Edit driver info
        elif choice == "2":
            driver_id = input("Enter Driver ID: ")

            if not driver_exists(driver_id, drivers):
                print("Driver ID does not exist! Please try again.")
                continue

            new_name = input("New name (or press Enter to skip): ").strip()
            new_phone = input("New phone (or press Enter to skip): ").strip()

            payload = {}
            if new_name:
                payload["name"] = new_name
            if new_phone:
                payload["phone"] = new_phone

            if not payload:
                print("No changes made.")
                continue

            resp = requests.post(f"{BASE_URL}/admin/drivers/{driver_id}/edit", json=payload)
            print(resp.json().get("message"))

        # (3) Add new driver
        elif choice == "3":
            name = input("Driver name: ")
            phone = input("Phone: ")

            if not name or not phone:
                print("Name and phone cannot be empty.")
                continue

            resp = requests.post(f"{BASE_URL}/admin/drivers/create", json={"name": name, "phone": phone})
            try:
                print(resp.json().get("message"))
            except:
                print("Server error:", resp.text)

        # (4) Go back
        elif choice == "4":
            return

        else:
            error("Invalid choice.")


def driver_exists(driver_id, drivers):
    for driver in drivers:
        if str(driver["DriverID"]) == str(driver_id):
            return True
    return False


def manage_store_info():
    section("Store Management", "🏪")

    while True:
        resp = requests.get(f"{BASE_URL}/admin/stores")
        if not resp.ok:
            print("Error loading stores.")
            return
        stores = resp.json()

        print("\nAll stores:")
        print_store_table(stores)

        print("Actions:")
        print("(1) Manage store menu information")
        print("(2) Add new store")
        print("(3) Edit store information")
        print("(4) Delete store")
        print("(5) Back")

        choice = input("\nChoose (1/2/3/4/5): ")

        # Manage store menu
        if choice == "1":
            store_id = input("\nEnter store ID to manage (or press Enter to go back): ").strip()
            if not store_id:
                continue

            if not store_exists(store_id, stores):
                error("Invalid Store ID.")
                continue

            manage_single_store_menu(store_id)

        # (2) Add new store
        elif choice == "2":
            name = input("Store name: ")
            location = input("Location: ")

            if not name or not location:
                print("Name and location cannot be empty.")
                continue

            resp = requests.post(f"{BASE_URL}/admin/stores/create", json={"name": name, "location": location})
            print(resp.json().get("message"))

        # (3) Edit store information
        elif choice == "3":
            store_id = input("Enter Store ID: ")

            # Check if the store exists
            if not store_exists(store_id, stores):
                error("Invalid Store ID.")
                continue

            new_name = input("New name (press Enter to skip): ")
            new_location = input("New location (press Enter to skip): ")

            payload = {}
            if new_name.strip():
                payload["name"] = new_name.strip()
            elif new_name != "":
                print("Name cannot be blank.")
                continue
            if new_location:
                payload["location"] = new_location # E.G. 8th college to Duan Family College Canteen

            if not payload:
                print("No changes made.")
                continue

            resp = requests.post(f"{BASE_URL}/admin/stores/{store_id}/edit", json=payload)
            print(resp.json().get("message"))

        # (4) Delete store
        elif choice == "4":
            store_id = input("Enter Store ID to delete: ")

            if not store_exists(store_id, stores):
                error("Invalid Store ID.")
                continue

            confirm = input("Are you sure you want to delete this store? (Y/N): ").upper()
            if confirm != "Y":
                print("Cancelled.")
                continue

            resp = requests.post(f"{BASE_URL}/admin/stores/{store_id}/delete")
            print(resp.json().get("message"))

        # (5) Go back
        elif choice == "5":
            return

        else:
            error("Invalid choice.")


def store_exists(store_id, stores):
    for store in stores:
        if str(store["StoreID"]) == str(store_id):
            return True
    return False


def manage_single_store_menu(store_id):
    while True:
        resp = requests.get(f"{BASE_URL}/admin/stores/{store_id}/menu")
        if not resp.ok:
            error("Error loading menu")
            continue
        menu = resp.json()

        print(f"\n📋 Menu for Store {store_id}")
        # if not menu:
        #     print("(No menu items yet.)")
        #
        # rows = []
        # for item in menu:
        #     rows.append([
        #         item["MenuItemID"],
        #         item["Name"],
        #         f"¥{item['Price']}"
        #     ])

        print_menu_table(menu)

        print("\nActions:")
        print("(1) Add menu item")
        print("(2) Edit menu item")
        print("(3) Delete menu item")
        print("(4) Back")

        choice = input("Choose (1/2/3/4): ").strip()

        if choice == "4":
            return

        # (1) Add menu item
        if choice == "1":
            name = input("Enter item name: ").strip()
            price_str = input("Enter price: ").strip()

            try:
                price = float(price_str)
                if price <= 0:
                    error("Price must be positive.")
                    continue
            except ValueError:
                error("Invalid price.")
                continue

            resp = requests.post(f"{BASE_URL}/admin/stores/{store_id}/menu/add", json={"name": name, "price": price})
            print(resp.json().get("message"))
            continue

        # (2) Edit menu item
        elif choice == "2":
            item_id = input("Enter Menu Item ID to edit: ").strip()
            new_name = input("New name (or press Enter to skip): ").strip()
            new_price = input("New price (or press Enter to skip): ").strip()

            payload = {}
            if new_name:
                payload["name"] = new_name
            if new_price:
                try:
                    payload["price"] = float(new_price)
                except ValueError:
                    error("Invalid price.")
                    continue

            resp = requests.post(f"{BASE_URL}/admin/menu/{item_id}/edit", json=payload)
            print(resp.json().get("message"))
            continue

        # (3) Delete menu item
        elif choice == "3":
            item_id = input("Enter Menu Item ID to delete: ").strip()
            confirm = input("Are you sure? (Y/N): ").upper()

            if confirm != "Y":
                continue

            resp = requests.post(f"{BASE_URL}/admin/menu/{item_id}/delete")
            print(resp.json().get("message"))
            continue

        else:
            error("Invalid choice.")


def view_combined_history():
    section("All Orders Overview", "📜")

    while True:
        section("Filter Order History", "🔎")
        print("(1) View ALL orders (may be long)")
        print("(2) Filter by status")
        print("(3) Filter by store")
        print("(4) Filter by user")
        print("(5) Back")

        choice = input("Choose (1/2/3/4/5): ")

        # (1) View all
        if choice == "1":
            resp = requests.get(f"{BASE_URL}/admin/orders")
            show_orders(resp)
            continue

        # (2) Filter by status
        elif choice == "2":
            status = input("Enter status to filter for (UNSHIPPED, SHIPPED, COMPLETED): ").upper()
            resp = requests.get(f"{BASE_URL}/admin/orders", params={"status": status})
            show_orders(resp)
            continue

        # (3) Filter by store
        elif choice == "3":
            store_id = input("Enter Store ID: ")
            resp = requests.get(f"{BASE_URL}/admin/orders", params={"store_id": store_id})
            show_orders(resp)
            continue

        # (4) Filter by user
        elif choice == "4":
            user_id = input("Enter User ID: ")
            resp = requests.get(f"{BASE_URL}/admin/orders", params={"user_id": user_id})
            show_orders(resp)
            continue

        elif choice == "5":
            return

        else:
            error("Invalid option.")


def show_orders(resp):
    if not resp.ok:
        print("Error loading order history:", resp.text)
        return

    orders = resp.json()
    print_order_table(orders)


def edit_admin_account(user_id):
    section("Edit Admin Account", "👤")
    info("Press Enter to keep current value.")

    new_name = input("New name: ")
    new_phone = input("New phone: ")
    new_password = input("New password: ")

    payload = {}
    if new_name:
        payload["name"] = new_name
    if new_phone:
        payload["phone"] = new_phone
    if new_password:
        payload["password"] = new_password

    if not payload:
        info("No changes made.")
        return

    resp = requests.post(f"{BASE_URL}/users/{user_id}/edit", json=payload)
    if not resp.ok:
        error(resp.text)
    else:
        success(resp.json().get("message", "Account updated."))


def print_store_table(stores):
    if not stores:
        print("No stores available.")
        return

    headers = ["StoreID", "Name", "Location"]
    rows = [
        {"StoreID": s["StoreID"], "Name": s["Name"], "Location": s["Location"]}
        for s in stores
    ]

    render_table(headers, rows, border_style="bold")


def print_menu_table(menu):
    if not menu:
        print("(No menu items yet.)")
        return

    headers = ["MenuItemID", "Name", "Price"]
    rows = [
        {"MenuItemID": item["MenuItemID"], "Name": item["Name"], "Price": f"¥{item['Price']}"}
        for item in menu
    ]

    render_table(headers, rows, border_style="bold")


def print_user_order_history_table(orders):
    if not orders:
        print("You have no past orders.")
        return

    headers = ["OrderID", "Store", "Status", "Driver", "DeliveryAddress", "Total"]

    rows = [
        {
            "OrderID": o["OrderID"],
            "Ordered": to_local(o["OrderTime"]),
            "Store": o["StoreName"],
            "Status": o["Status"],
            "Driver": o["DriverName"] if o["DriverName"] else "None",
            "DeliveryAddress": o["DeliveryAddress"],
            "Total": f"¥{o['TotalPrice']}",
        }
        for o in orders
    ]

    render_table(headers, rows, border_style="bold")


def print_order_table(orders):
    if not orders:
        print("No orders to display.")
        return

    headers = [
        "OrderID", "Ordered", "UserID", "UserName", "DeliveryAddress",
        "StoreID", "StoreName", "Status", "DriverName", "Total"
    ]

    rows = [
        {
            "OrderID": o["OrderID"],
            "Ordered": to_local(o["OrderTime"]),
            "UserID": o["UserID"],
            "UserName": o["UserName"],
            "DeliveryAddress": o["DeliveryAddress"],
            "StoreID": o["StoreID"],
            "StoreName": o["StoreName"],
            "Status": o["Status"],
            "DriverName": o["DriverName"] if o["DriverName"] else "None",
            "Total": f"¥{o['TotalPrice']}",
        }
        for o in orders
    ]

    render_table(headers, rows, border_style="bold")


def print_driver_table(drivers):
    if not drivers:
        print("No drivers found.")
        return

    headers = ["DriverID", "Name", "Phone", "IsActive"]
    rows = [
        {
            "DriverID": d["DriverID"],
            "Name": d["Name"],
            "Phone": d["Phone"],
            "IsActive": "Active" if d["IsActive"] == 1 else "Inactive",
        }
        for d in drivers
    ]

    render_table(headers, rows, border_style="bold")


def print_admin_store_menu_table(menu):
    headers = ["MenuItemID", "Name", "Price"]
    rows = [
        {"MenuItemID": item["MenuItemID"], "Name": item["Name"], "Price": f"¥{item['Price']}"}
        for item in menu
    ]

    render_table(headers, rows, border_style="bold")


if __name__ == "__main__":
    while True:
        main()
