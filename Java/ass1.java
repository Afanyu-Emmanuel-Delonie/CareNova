class OrderProcessor {
    private final PaymentGateway paymentGateway;

    OrderProcessor(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

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

    private void processPayment(double total) {
        paymentGateway.charge(total);
    }
}
