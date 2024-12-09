import os
from flask import Flask, render_template, request, jsonify, session, redirect, abort
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)

# secret key
app.secret_key = os.urandom(24)

def get_db_connection():
    # connect to database.db
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    # home (garden) page
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # forget any user id
    session.clear()

    # submitted a form with POST
    if request.method == "POST":
        # ensure valid information
        if not request.form.get("username"):
            return "Error: Must provide username", 400
        if not request.form.get("password"):
            return "Error: Must provide password", 400

        # query database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        rows = cursor.fetchall()

        conn.close()

        # ensure username and password valid
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return "invalid username and/or password", 403

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect to home page
        return redirect("/")

    # get homepage
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Check for errors
        if not request.form.get("username"):
            return "Error: Must provide username", 400
        elif not request.form.get("password"):
            return "Error: Must provide password", 400
        elif request.form.get("password") != request.form.get("confirmation"):
            return "Error: Passwords must match", 400

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cursor.fetchall()

        if len(rows) > 0:
            conn.close()
            return "Error: Username already exists", 400

        # Insert new user into users table
        hash = generate_password_hash(request.form.get("password"), method='scrypt', salt_length=16)
        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (request.form.get("username"), hash))
        conn.commit()

        # Get the user's ID to remember them in the session
        cursor.execute("SELECT id FROM users WHERE username = ?", (request.form.get("username"),))
        user_id = cursor.fetchone()["id"]

        # Insert default values into progress, inventory, and shop tables
        cursor.execute("INSERT INTO progress (user_id, plant1_progress, plant2_progress) VALUES (?, 0, 0)", (user_id,))
        cursor.execute("INSERT INTO inventory (user_id, dandelion_amount, daffodil_amount, mushroom_amount) VALUES (?, 0, 0, 0)", (user_id,))
        cursor.execute("INSERT INTO shop (user_id, dandelion_amount, daffodil_amount, mushroom_amount) VALUES (?, 0, 0, 0)", (user_id,))
        conn.commit()

        # Close connection
        conn.close()

        session["user_id"] = user_id

        # Redirect to home page
        return redirect("/")

    else:  # If the user reached the route via GET
        return render_template("register.html")

@app.route("/inventory")
def inventory():

    # get user id
    user_id = session["user_id"]
    print(f"Debug: Retrieved user_id = {user_id}")  # for debugging (delete?)

    # ensure valid id
    if user_id is None:
        return "Error: User not logged in or session expired.", 400
    try:
        user_id = int(user_id)
    except ValueError:
        return "Error: Invalid user ID.", 400
    
    # connect to database
    conn = get_db_connection()
    cursor = conn.cursor()

    # get data from database
    try:
        cursor.execute(
            "SELECT dandelion_amount, daffodil_amount, mushroom_amount FROM inventory WHERE user_id = ?", (user_id,))
        inventory_data = cursor.fetchone()
    except:
        return "Error: Unable to retrieve data.", 400

    conn.close()

    # if DNE --> set to 0
    if inventory_data:
        inventory = {
            "dandelion_amount": inventory_data[0],
            "daffodil_amount": inventory_data[1],
            "mushroom_amount": inventory_data[2]
        }
    else:
        inventory = {
            "dandelion_amount": 0,
            "daffodil_amount": 0,
            "mushroom_amount": 0
        }

    # pass inventory data to html
    return render_template("inventory.html", inventory=inventory)

@app.route("/shop")
def shop():
    user_id = session.get("user_id")

    if user_id is None:
        return "Error: User not logged in or session expired.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # get shop data
    try:
        cursor.execute(
            "SELECT dandelion_amount, daffodil_amount, mushroom_amount FROM shop WHERE user_id = ?",
            (user_id,)
        )
        shop_data = cursor.fetchone()
    except:
        return "Error: Unable to retrieve shop data.", 400

    conn.close()

    # dictionary for shop items
    if shop_data:
        shop_inventory = {
            "dandelions": shop_data[0],
            "daffodils": shop_data[1],
            "mushrooms": shop_data[2],
        }
    else:
        shop_inventory = {"dandelions": 0, "daffodils": 0, "mushrooms": 0}

    plant_ascii = {
        "dandelion" : "     .--.     \n   .'_\\/_.    \n   '. /\\ .'   \n     \"||\"     \n      || /\\   \n   /\\ ||//\\)  \n  (/\\\\||/\\    \n,.,.,\\||/.,.,.",
        "daffodil" : "_ _\n(_\\_)\n(__<_{})\n (_/_)\\\n|\n \\ | /\\\n \\|//\n |/\n,.,.,|.,.,.",
        "mushroom" :  ".-\"\"\"-.\n/* * * *\\\\\n:_.-:`:-._;\n(_)\n,.\\|/(_)\\|/,."
    }

    # make a grid for plant ascii art
    plant_grid = []
    width = 3
    height = 4
    total_cells = width * height  # 3x4 grid
    for _ in range(total_cells):
        if shop_inventory["dandelions"] > 0:
            shop_inventory["dandelions"] -= 1
            plant_grid.append(plant_ascii["dandelion"])
        elif shop_inventory["daffodils"] > 0:
            shop_inventory["daffodils"] -= 1
            plant_grid.append(plant_ascii["daffodil"])
        elif shop_inventory["mushrooms"] > 0:
            shop_inventory["mushrooms"] -= 1
            plant_grid.append(plant_ascii["mushroom"])
        else:
            plant_grid.append("")  # empty if none

    # made a grid of the above list
    grid = []
    for i in range(0, len(plant_grid), height-1):
        # row = three elements
        row = plant_grid[i:i + width]
        grid.append(row)

    return render_template("shop.html", grid=grid)

@app.route("/plant-seed", methods=["POST"])
def plant_seed():
    user_id = session["user_id"]
    plant_id = request.json.get("plant_id")  # get which plant (1 or 2)

    if not user_id:
        return jsonify({"error": "Please log in"}), 400
    
    if not plant_id:
        return jsonify({"error": "Invalid plant"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # update progress
    column = f"plant{plant_id}_progress"  # choose correct progress column
    try:
        cursor.execute(f"UPDATE progress SET {column} = ? WHERE user_id = ?", (1, user_id))  # set to stage 1 (planted)
        conn.commit()
        conn.close()
    except:
        return jsonify({"error": "Unable to update"}), 400

    return jsonify({"success": True, "message": f"Planted seed in planter {plant_id}"}), 200

@app.route("/water-seed", methods=["POST"])
def water_seed():
    user_id = session["user_id"]
    plant_id = request.json.get("plant_id")

    if not user_id:
        return jsonify({"error": "Please log in"}), 400
    
    if not plant_id:
        return jsonify({"error": "Invalid plant"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    column = f"plant{plant_id}_progress" # choose correct plant (1 or 2)

    cursor.execute(f"SELECT {column} FROM progress WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()  # first (hopefully only) row
    if not result or result[0] == 0 or result[0] > 4: 
        return jsonify({"error": "Not ready to be watered"}), 400

    # update progress
    try:
        cursor.execute(f"UPDATE progress SET {column} = ? WHERE user_id = ?", (result[0]+1, user_id))  # go to next stage
        conn.commit()
        conn.close()
    except:
        return jsonify({"error": "Unable to update"}), 400
    
    return jsonify({"success": True, "message": f"Watered seed in planter {plant_id}"}), 200

@app.route("/harvest-seed", methods=["POST"])
def harvest_seed():
    data = request.get_json()  # used json to handle data with multiple fields
    
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    user_id = session.get("user_id")
    plant_id = data.get("plant_id")  # which planter
    plantType = data.get("plant_type")  # which plant type ('dandelion', 'daffodil'...)

    if not user_id:
        return jsonify({"error": "Please log in"}), 400

    if not plant_id or not plantType:
        return jsonify({"error": "Invalid data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    column = f"plant{plant_id}_progress"

    cursor.execute(f"SELECT {column} FROM progress WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()  # first row of result
    if not result or result[0] != 4: 
        return jsonify({"error": "Not ready to be harvested"}), 400

    if plantType == 'dandelion':
        plantColumn = 'dandelion_amount'
    elif plantType == 'daffodil':
        plantColumn = 'daffodil_amount'
    elif plantType == 'mushroom':
        plantColumn = 'mushroom_amount'
    else:
        plantColumn = None

    # get current amount
    cursor.execute(f"SELECT {plantColumn} FROM inventory WHERE user_id = ?", (user_id,))
    plantResult = cursor.fetchone()
    if not plantResult:
        return jsonify({"error": "Please log in"}), 200

    try:
        # update progress
        cursor.execute(f"UPDATE progress SET {column} = ? WHERE user_id = ?", (0, user_id))  # reset progress (empty)
        cursor.execute(f"UPDATE inventory SET {plantColumn} = ? WHERE user_id = ?", (plantResult[0] + 1, user_id))  # add 1 to inventory
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Harvested seed from {plant_id}"}), 200
    except:
        return jsonify({"error": "Unable to update"}), 500

@app.route("/send-to-shop", methods=["POST"])
def send_to_shop():
    try:
        # get json data from the request
        data = request.get_json()
        plant_type = data.get("plant_type")
        user_id = session.get("user_id")

        # log request (debugging, can delete)
        print(f"Received request to send {plant_type} for user {user_id}")

        # plant types to columns
        plant_columns = {
            "dandelion": "dandelion_amount",
            "daffodil": "daffodil_amount",
            "mushroom": "mushroom_amount"
        }
        plant_column = plant_columns.get(plant_type)

        if not plant_column:
            print("Invalid plant type provided.")
            return jsonify({"success": False, "error": "Invalid plant type"}), 400

        # update inventory
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {plant_column} FROM inventory WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            print("No inventory data found for user.")
            conn.close()
            return jsonify({"success": False, "error": "User not found in inventory"}), 400

        if result[0] <= 0:
            print(f"No {plant_type}s available to send.")
            conn.close()
            return jsonify({"success": False, "error": f"No {plant_type}s available to send"}), 400

        # log successful results
        print(f"User has {result[0]} {plant_type}s. Proceeding to update inventory and shop.")

        # decrease plant count; increase it in shop
        cursor.execute(f"UPDATE inventory SET {plant_column} = {plant_column} - 1 WHERE user_id = ?", (user_id,))
        cursor.execute(f"UPDATE shop SET {plant_column} = {plant_column} + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        print("Successfully updated inventory and shop.")
        return jsonify({"success": True}), 200
    except:
        return jsonify({"success": False, "error": "Failed to update"}), 500

if __name__ == "__main__":
    app.run(debug=True)
