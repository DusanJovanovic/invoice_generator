import requests
import weasyprint
from flask import Flask, make_response, render_template
from flask_caching import Cache

CACHE_TIMEOUT = 3600
CREDENTIALS = ("user", "api_user_password1234")
REQUEST_TIMEOUT = 30

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})


# Function to fetch all customers and cache the information
@cache.memoize(timeout=CACHE_TIMEOUT)
def fetch_all_customers():
    url = "https://assessment.codeflex.it/customers"
    response = requests.get(url, auth=CREDENTIALS, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        customers = response.json()
        return {customer["id"]: customer for customer in customers}
    return None


# Function to fetch customer orders from the API
def fetch_customer_orders(customer_no):
    url = f"https://assessment.codeflex.it/customer_orders/{customer_no}"
    response = requests.get(url, auth=CREDENTIALS, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch order components from the API
def fetch_order_components(order_no):
    url = f"https://assessment.codeflex.it/order_components/{order_no}"
    response = requests.get(url, auth=CREDENTIALS, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch info from selected customer
def fetch_customer_info(customer_no):
    return fetch_all_customers()[customer_no]


# Helpere function for stack boxes
def stack_boxes(order_components):
    # Sort order components by weight in descending order
    sorted_components = sorted(
        order_components, key=lambda x: x["weight"], reverse=True
    )

    # Initialize list of stacks
    stacks = []

    # Iterate through order components
    for component in sorted_components:
        placed = False
        # Try to place the component on an existing stack
        for stack in stacks:
            max_capacity = stack[-1]["max_weight_capacity"]
            if max_capacity >= component["weight"]:
                if (
                    max_capacity - component["weight"]
                    < component["max_weight_capacity"]
                ):
                    component["max_weight_capacity"] = (
                        max_capacity - component["weight"]
                    )
                stack.append(component)
                placed = True
                break
        # If unable to place on an existing stack, create a new stack
        if not placed:
            stacks.append([component])

    return stacks


# Route to display all customers
@app.route("/")
def show_customers():
    customer_data = fetch_all_customers()
    if customer_data:
        return render_template(
            "customers.html",
            customers=list(customer_data.values()),
        )
    return "Failed to fetch customer data."


# Route to display customer orders
@app.route("/customer_orders/<int:customer_no>")
def show_customer_orders(customer_no):
    orders = fetch_customer_orders(customer_no)
    customer = fetch_customer_info(customer_no)
    if orders:
        return render_template(
            "customer_orders.html",
            orders=orders,
            customer=customer,
        )
    else:
        return "Failed to fetch customer orders."


# Route to display invoice for a specific order
@app.route("/invoice/<int:customer_no>/<string:order_no>")
def show_invoice(customer_no, order_no):
    order_components = fetch_order_components(order_no)
    if order_components:
        # Calculate total price
        total_price = sum(
            item["unit_price"] * item["quantity_in_box"] for item in order_components
        )
        customer_info = fetch_customer_info(customer_no)
        if customer_info:
            return render_template(
                "invoice.html",
                order_components=order_components,
                total_price=total_price,
                customer_info=customer_info,
                order_no=order_no,
            )
        return "Customer not found."
    return "Failed to fetch invoice components."


# Route to download the invoice as PDF
@app.route("/download_invoice/<int:customer_no>/<string:order_no>")
def download_invoice(customer_no, order_no):
    order_components = fetch_order_components(order_no)
    total_price = sum(
        item["unit_price"] * item["quantity_in_box"] for item in order_components
    )
    customer_info = fetch_customer_info(customer_no)

    # Generate HTML for invoice
    invoice_html = render_template(
        "invoice.html",
        order_components=order_components,
        total_price=total_price,
        customer_info=customer_info,
        order_no=order_no,
    )

    # Convert HTML to PDF
    pdf = weasyprint.HTML(string=invoice_html).write_pdf()

    # Prepare response as PDF
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename=invoice_{order_no}.pdf"

    return response


# Route to display stacks for a specific order
@app.route("/stacks/<int:customer_no>/<string:order_no>")
def view_stacks(customer_no, order_no):
    order_components = fetch_order_components(order_no)
    if not order_components:
        return "Failed to fetch order components."
    print(847328798)

    customer_info = fetch_customer_info(customer_no)
    # Stack the boxes
    stacks = stack_boxes(order_components)
    return render_template(
        "stacks.html",
        order_no=order_no,
        stacks=stacks,
        customer_info=customer_info,
    )


# Route to download stacks as PDF
@app.route("/download_stacks/<int:customer_no>/<string:order_no>")
def download_stacks(customer_no, order_no):
    order_components = fetch_order_components(order_no)
    if not order_components:
        return "Failed to fetch order components."
    print(847328798)
    customer_info = fetch_customer_info(customer_no)
    # Stack the boxes
    stacks = stack_boxes(order_components)
    stack_template = render_template(
        "stacks.html",
        order_no=order_no,
        stacks=stacks,
        customer_info=customer_info,
    )

    # Convert HTML to PDF
    pdf = weasyprint.HTML(string=stack_template).write_pdf()

    # Prepare response as PDF
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename=stack{order_no}.pdf"

    return response


if __name__ == "__main__":
    app.run(port=5001, debug=True)
