// Before refactoring
public void processOrder(Order order) {
    // Calculate total
    double total = 0;
    for (Item item : order.getItems()) {
        total += item.getPrice() * item.getQuantity();
    }
    
    // Apply discount
    if (order.getCustomer().isPremium()) {
        total *= 0.9;
    }
    
    // Process payment
    paymentGateway.charge(total);
}

// After refactoring
public void processOrder(Order order) {
    double total = calculateTotal(order);
    total = applyDiscount(total, order.getCustomer());
    processPayment(total);
}

private double calculateTotal(Order order) {
    double total = 0;
    for (Item item : order.getItems()) {
        total += item.getPrice() * item.getQuantity();
    }
    return total;
}

private double applyDiscount(double total, Customer customer) {
    return customer.isPremium() ? total * 0.9 : total;
}

