import pandas as pd
from datetime import datetime

MAX_DAILY_CAPACITY = 200

def load_data():
    orders = pd.read_csv("orders.csv")
    inventory = pd.read_csv("inventory.csv")
    inventory = dict(zip(inventory.ProductCode, inventory.AvailableStock))
    return orders, inventory

def process_orders(orders, inventory):
    daily_capacity = {}
    results = []

    # Urgent orders first
    orders = orders.sort_values(by="Priority", ascending=False)

    for _, order in orders.iterrows():
        order_id = order["OrderID"]
        product = order["ProductCode"]
        qty = order["Quantity"]
        date = order["OrderDate"]
        priority = order["Priority"]

        if date not in daily_capacity:
            daily_capacity[date] = MAX_DAILY_CAPACITY

        available_stock = inventory.get(product, 0)
        available_capacity = daily_capacity[date]

        decision = ""
        reason = ""

        if available_stock <= 0:
            decision = "Escalate"
            reason = f"No inventory available for product {product}"

        elif qty <= available_stock and qty <= available_capacity:
            decision = "Approve"
            inventory[product] -= qty
            daily_capacity[date] -= qty
            reason = "Sufficient inventory and production capacity available"

        elif qty > available_stock and available_stock > 0:
            decision = "Split"
            inventory[product] = 0
            daily_capacity[date] -= min(available_stock, available_capacity)
            reason = f"Partial stock available ({available_stock}), splitting order"

        elif qty > available_capacity:
            if priority == "Urgent" and available_capacity > 0:
                decision = "Split"
                daily_capacity[date] = 0
                inventory[product] -= available_capacity
                reason = "Urgent order partially fulfilled due to capacity limit"
            else:
                decision = "Delay"
                reason = "Insufficient production capacity for the day"

        else:
            decision = "Escalate"
            reason = "Unhandled edge case detected"

        results.append({
            "OrderID": order_id,
            "Decision": decision,
            "Reason": reason
        })

    return results

def main():
    orders, inventory = load_data()
    results = process_orders(orders, inventory)

    print("\n=== AI Ops Assistant Decisions ===\n")
    for r in results:
        print(f"{r['OrderID']} -> {r['Decision']} | {r['Reason']}")

    # Save log
    pd.DataFrame(results).to_csv("decision_log.csv", index=False)

if __name__ == "__main__":
    main()
