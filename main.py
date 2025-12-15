import pandas as pd

MAX_DAILY_CAPACITY = 200

def load_data():
    orders = pd.read_csv("orders.csv")
    inventory_df = pd.read_csv("inventory.csv")
    inventory = dict(zip(inventory_df.ProductCode, inventory_df.AvailableStock))
    return orders, inventory

def process_orders(orders, inventory):
    # Sort by OrderDate ASC, then Priority (Urgent first)
    orders["PriorityRank"] = orders["Priority"].apply(
        lambda x: 0 if x == "Urgent" else 1
    )
    orders = orders.sort_values(by=["OrderDate", "PriorityRank"])

    daily_capacity = {}
    logs = []

    for _, order in orders.iterrows():
        order_id = order["OrderID"]
        date = order["OrderDate"]
        product = order["ProductCode"]
        requested_qty = order["Quantity"]
        priority = order["Priority"]

        daily_capacity.setdefault(date, MAX_DAILY_CAPACITY)

        inv_before = inventory.get(product, 0)
        cap_before = daily_capacity[date]

        fulfilled_qty = min(requested_qty, inv_before, cap_before)
        remaining_qty = requested_qty - fulfilled_qty

        inventory[product] = inv_before - fulfilled_qty
        daily_capacity[date] = cap_before - fulfilled_qty

        inv_after = inventory[product]
        cap_after = daily_capacity[date]

        # Decision logic
        if fulfilled_qty == 0:
            if inv_before == 0:
                decision = "Escalate"
                reason = "No inventory available"
            else:
                decision = "Delay"
                reason = "No production capacity available"

        elif fulfilled_qty < requested_qty:
            decision = "Split"
            reason = "Partially fulfilled due to stock or capacity constraints"

        else:
            decision = "Approve"
            reason = "Fully fulfilled within stock and capacity limits"

        logs.append({
            "OrderID": order_id,
            "OrderDate": date,
            "ProductCode": product,
            "Priority": priority,
            "RequestedQty": requested_qty,
            "FulfilledQty": fulfilled_qty,
            "RemainingQty": remaining_qty,
            "InventoryBefore": inv_before,
            "InventoryAfter": inv_after,
            "CapacityBefore": cap_before,
            "CapacityAfter": cap_after,
            "Decision": decision,
            "Reason": reason
        })

    return pd.DataFrame(logs)

def main():
    orders, inventory = load_data()
    decision_log = process_orders(orders, inventory)

    decision_log.to_csv("decision_log.csv", index=False)

    print("\n=== AI Ops Order Decisions ===\n")
    print(decision_log)

if __name__ == "__main__":
    main()
