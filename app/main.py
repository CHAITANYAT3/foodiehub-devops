from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

menu = [
    {"id": 1, "name": "Pizza", "category": "Pizza", "price": 250},
    {"id": 2, "name": "Burger", "category": "Burger", "price": 120},
    {"id": 3, "name": "Pasta", "category": "Pasta", "price": 180},
    {"id": 4, "name": "Sandwich", "category": "Snacks", "price": 100},
]

orders = []
next_order_id = 1


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/menu")
def get_menu():
    category = request.args.get("category")

    if category:
        filtered_menu = [
            item for item in menu
            if item["category"].lower() == category.lower()
        ]
        return jsonify(filtered_menu)

    return jsonify(menu)


@app.route("/api/orders", methods=["POST"])
def create_order():
    global next_order_id

    data = request.get_json(silent=True)

    if not data or not data.get("items"):
        return jsonify({"error": "Order items are required"}), 400

    order = {
        "id": next_order_id,
        "items": data["items"],
        "status": "pending",
    }

    orders.append(order)
    next_order_id += 1

    return jsonify(order), 201


@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)


@app.route("/api/orders/<int:order_id>")
def get_order(order_id):
    for order in orders:
        if order["id"] == order_id:
            return jsonify(order)

    return jsonify({"error": "Order not found"}), 404


@app.route("/api/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    data = request.get_json(silent=True) or {}

    for order in orders:
        if order["id"] == order_id:
            if not data.get("status"):
                return jsonify({"error": "Status is required"}), 400

            order["status"] = data["status"]
            return jsonify(order)

    return jsonify({"error": "Order not found"}), 404


@app.route("/metrics")
def metrics():
    return (
        "# HELP food_ordering_orders_total Total orders created\n"
        "# TYPE food_ordering_orders_total gauge\n"
        f"food_ordering_orders_total {len(orders)}\n",
        200,
        {"Content-Type": "text/plain; version=0.0.4"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
