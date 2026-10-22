import sys

class Product:
    def __init__(self, pid, name, quantity, purchase_price, selling_price):
        self.pid = pid
        self.name = name
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.selling_price = selling_price

    def get_value(self):
        return self.quantity * self.selling_price


class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, pid, name, quantity, purchase_price, selling_price):
        if pid in self.products:
            prod = self.products[pid]
            prod.quantity += quantity
            prod.purchase_price = min(prod.purchase_price, purchase_price)
            prod.selling_price = max(prod.selling_price, selling_price)
        else:
            self.products[pid] = Product(pid, name, quantity, purchase_price, selling_price)

    def delete_product(self, pid):
        if pid in self.products:
            del self.products[pid]
            return True
        return False

    def update_stock(self, pid, quantity):
        if pid in self.products:
            self.products[pid].quantity = quantity
            return True
        return False

    def get_total_value(self):
        return sum(p.get_value() for p in self.products.values())

    def __add__(self, other):
        merged = Inventory()
        for p in self.products.values():
            merged.add_product(p.pid, p.name, p.quantity, p.purchase_price, p.selling_price)
        for p in other.products.values():
            merged.add_product(p.pid, p.name, p.quantity, p.purchase_price, p.selling_price)
        return merged

    def __lt__(self, other):
        return self.get_total_value() < other.get_total_value()

    def __eq__(self, other):
        return self.get_total_value() == other.get_total_value()


def parse_inventory_file(lines, start_idx):
    inv = Inventory()
    n = int(lines[start_idx].strip())
    curr = start_idx + 1
    for _ in range(n):
        parts = lines[curr].strip().split()
        pid = parts[0]
        name = parts[1]
        qty = int(parts[2])
        pprice = float(parts[3])
        sprice = float(parts[4])
        inv.add_product(pid, name, qty, pprice, sprice)
        curr += 1
    return inv, curr


def run_inventory_system():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    inv_a, next_idx = parse_inventory_file(input_data, 0)
    inv_b, next_idx = parse_inventory_file(input_data, next_idx)

    q = int(input_data[next_idx].strip())
    curr = next_idx + 1

    for _ in range(q):
        if curr >= len(input_data):
            break
        
        line = input_data[curr].strip()
        if not line:
            curr += 1
            continue
            
        parts = line.split()
        op = parts[0].upper()

        if op == "MERGE":
            inv_a = inv_a + inv_b
            for pid in sorted(inv_a.products.keys()):
                p = inv_a.products[pid]
                print(f"{p.pid} {p.name} stock={p.quantity} purchase={int(p.purchase_price) if p.purchase_price.is_integer() else p.purchase_price} selling={int(p.selling_price) if p.selling_price.is_integer() else p.selling_price}")
        
        elif op == "COMPARE":
            if inv_a < inv_b:
                print("Inventory B is more valuable")
            elif inv_a == inv_b:
                print("Inventories are equal in value")
            else:
                print("Inventory A is more valuable")
                
        elif op == "ADD":
            target = parts[1]
            pid, name = parts[2], parts[3]
            qty, pprice, sprice = int(parts[4]), float(parts[5]), float(parts[6])
            if target == "A":
                inv_a.add_product(pid, name, qty, pprice, sprice)
            else:
                inv_b.add_product(pid, name, qty, pprice, sprice)
            print("Product Added")
            
        elif op == "DELETE":
            target = parts[1]
            pid = parts[2]
            success = inv_a.delete_product(pid) if target == "A" else inv_b.delete_product(pid)
            print("Product Deleted" if success else "Product Not Found")
            
        elif op == "UPDATE":
            target = parts[1]
            pid, qty = parts[2], int(parts[3])
            success = inv_a.update_stock(pid, qty) if target == "A" else inv_b.update_stock(pid, qty)
            print("Stock Updated" if success else "Product Not Found")
            
        curr += 1

if __name__ == "__main__":
    run_inventory_system()
