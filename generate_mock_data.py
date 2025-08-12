import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:5000/api"

def create_customer(customer_data):
    response = requests.post(f"{BASE_URL}/customers", json=customer_data)
    response.raise_for_status()
    return response.json()

def create_contract(contract_data):
    response = requests.post(f"{BASE_URL}/contracts", json=contract_data)
    response.raise_for_status()
    return response.json()

def create_branch(branch_data):
    response = requests.post(f"{BASE_URL}/branches", json=branch_data)
    response.raise_for_status()
    return response.json()

def create_room(room_data):
    response = requests.post(f"{BASE_URL}/rooms", json=room_data)
    response.raise_for_status()
    return response.json()

def create_room_booking(booking_data):
    response = requests.post(f"{BASE_URL}/room-bookings", json=booking_data)
    response.raise_for_status()
    return response.json()

def generate_mock_data():
    print("Generating mock data...")

    # Generate Customers
    customers = []
    for i in range(10):
        customer_type = random.choice(["individual", "company"])
        customer_data = {
            "customer_name": f"Customer {i+1}",
            "customer_email": f"customer{i+1}@example.com",
            "customer_phone": "09" + "".join(random.choices("0123456789", k=8)),
            "customer_type": customer_type
        }
        if customer_type == "company":
            customer_data["company_name"] = f"Company {i+1} LLC"
            customer_data["tax_id"] = "TAX" + "".join(random.choices("0123456789", k=7))
        
        customer = create_customer(customer_data)
        customers.append(customer)
        print(f"Created customer: {customer['customer_name']}")

    # Generate Contracts
    contracts = []
    for customer in customers:
        if random.random() < 0.7:  # 70% of customers have contracts
            contract_type = random.choice(["VP ảo", "phòng họp", "chỗ ngồi cố định", "chỗ ngồi không cố định"])
            contract_value = random.randint(1000000, 50000000)
            signed_date = datetime.now() - timedelta(days=random.randint(30, 365))
            expiry_date = signed_date + timedelta(days=random.randint(90, 730))
            amount_paid = random.randint(0, contract_value)
            amount_outstanding = contract_value - amount_paid
            payment_date = datetime.now() + timedelta(days=random.randint(-10, 30))  # Some overdue, some upcoming

            contract_data = {
                "customer_id": customer["customer_id"],
                "contract_type": contract_type,
                "contract_value": contract_value,
                "contract_start_date": signed_date.strftime("%Y-%m-%d"),
                "contract_end_date": expiry_date.strftime("%Y-%m-%d"),
                "amount_paid": amount_paid,
                "last_payment_date": payment_date.strftime("%Y-%m-%d"),
                "status": "active" if amount_outstanding > 0 else "paid"
            }
            contract = create_contract(contract_data)
            contracts.append(contract)
            print(f"Created contract for {customer['customer_name']}: {contract['contract_type']}")

    # Generate Branches
    branches = []
    for i in range(3):
        branch_data = {
            "branch_name": f"Campusk Branch {i+1}",
            "address": f"123 Street {i+1}, District {i+1}, Ho Chi Minh City",
            "phone": "028" + "".join(random.choices("0123456789", k=7)),
            "email": f"branch{i+1}@campusk.vn",
            "manager_name": f"Manager {i+1}"
        }
        branch = create_branch(branch_data)
        branches.append(branch)
        print(f"Created branch: {branch['branch_name']}")

    # Generate Rooms
    rooms = []
    for branch in branches:
        for i in range(random.randint(5, 10)):  # 5-10 rooms per branch
            room_data = {
                "branch_id": branch["branch_id"],
                "room_number": f"{random.randint(100, 500)}",
                "area": round(random.uniform(15.0, 100.0), 1),
                "orientation": random.choice(["North", "South", "East", "West"]),
                "rental_price": random.randint(3000000, 20000000),
                "capacity": random.randint(1, 10),
                "amenities": ", ".join(random.sample(["Air conditioning", "WiFi", "Projector", "Whiteboard", "Coffee machine"], k=random.randint(1, 5))),
                "status": random.choice(["available", "occupied", "maintenance"])
            }
            room = create_room(room_data)
            rooms.append(room)
            print(f"Created room {room['room_number']} in {branch['branch_name']}")

    # Generate Room Bookings
    for _ in range(20):  # 20 random room bookings
        customer = random.choice(customers)
        room = random.choice(rooms)
        rental_start_date = datetime.now() + timedelta(days=random.randint(-60, 60))
        rental_end_date = rental_start_date + timedelta(days=random.randint(30, 365))
        monthly_rent = room["rental_price"]
        deposit_amount = monthly_rent * random.uniform(1, 3)

        booking_data = {
            "room_id": room["room_id"],
            "customer_id": customer["customer_id"],
            "rental_start_date": rental_start_date.strftime("%Y-%m-%d"),
            "rental_end_date": rental_end_date.strftime("%Y-%m-%d"),
            "monthly_rent": monthly_rent,
            "deposit_amount": deposit_amount,
            "status": random.choice(["active", "completed", "cancelled"])
        }
        try:
            booking = create_room_booking(booking_data)
            print(f"Created room booking for {customer['customer_name']} in room {room['room_number']}")
        except requests.exceptions.HTTPError as e:
            print(f"Error creating room booking: {e}")

    print("Mock data generation complete.")

if __name__ == "__main__":
    generate_mock_data()

