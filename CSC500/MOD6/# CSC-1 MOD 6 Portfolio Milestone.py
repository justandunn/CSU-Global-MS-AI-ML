# CSC- MOD 6 Portfolio Milestone

class ItemToPurchase:
    def __init__(self, item_name="none", item_price=0, item_quantity=0, item_description="none"):
        self.item_name = item_name
        self.item_price = item_price
        self.item_quantity = item_quantity
        self.item_description = item_description
    
    def print_item_cost(self):
        total_cost = self.item_price * self.item_quantity
        print(f"{self.item_name} {self.item_quantity} @ ${self.item_price} = ${total_cost}")
    
    def print_item_description(self):
        print(f"{self.item_name}: {self.item_description}")

class ShoppingCart:
    def __init__(self, customer_name="none", current_date="January 1, 2020"):
        self.customer_name = customer_name
        self.current_date = current_date
        self.cart_items = []
    
    def add_item(self, item):
        self.cart_items.append(item)
    
    def remove_item(self, item_name):
        for item in self.cart_items:
            if item.item_name == item_name:
                self.cart_items.remove(item)
                return
        print("Item not found in cart. Nothing removed.")
    
    def get_cost_of_cart(self):
        return sum(item.item_price * item.item_quantity for item in self.cart_items)
    
    def print_total(self):
        print(f"{self.customer_name}'s Shopping Cart - {self.current_date}")
        if not self.cart_items:
            print("SHOPPING CART IS EMPTY")
        else:
            total_items = sum(item.item_quantity for item in self.cart_items)
            print(f"Number of Items: {total_items}")
            for item in self.cart_items:
                item.print_item_cost()
            print(f"Total: ${self.get_cost_of_cart()}")

def main():
    cart = ShoppingCart("John Doe", "February 1, 2020")
    print_menu(cart)

def print_menu(cart):
    while True:
        print("\nMENU")
        print("a - Add item to cart")
        print("r - Remove item from cart")
        print("c - Change item quantity")
        print("i - Output items' descriptions")
        print("o - Output shopping cart")
        print("q - Quit")
        choice = input("Choose an option: ").strip().lower()
        
        if choice == 'a':
            name = input("Enter item name: ")
            desc = input("Enter item description: ")
            price = float(input("Enter item price: "))
            quantity = int(input("Enter item quantity: "))
            cart.add_item(ItemToPurchase(name, price, quantity, desc))
        elif choice == 'r':
            name = input("Enter item name to remove: ")
            cart.remove_item(name)
        elif choice == 'o':
            cart.print_total()
        elif choice == 'i':
            cart.print_descriptions()
        elif choice == 'q':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()