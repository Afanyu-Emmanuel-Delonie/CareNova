public class BankAccount {

    private String accountHolder;
    private double balance;

    // Constructor
    public BankAccount(String accountHolder, double initialBalance) {
        this.accountHolder = accountHolder;
        // if (initialBalance < 0) {
        //     throw new IllegalArgumentException("Initial balance cannot be negative");
        // }
        this.balance = initialBalance;
    }

    // Method to deposit money
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit amount must be greater than zero");
        }
        balance += amount;
    }

    // Method to withdraw money
    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be greater than zero");
        }
        if (amount > balance) {
            throw new IllegalArgumentException("Insufficient funds");
        }
        balance -= amount;
    }

    // Method to get current balance
    public double getBalance() {
        return balance;
    }

    // Method to get account holder name
    public String getAccountHolder() {
        return accountHolder;
    }

    public static void main(String[] args) {
        BankAccount account = new BankAccount("Alice", 1000.0);

        account.deposit(250.0);
        account.withdraw(100.0);

        System.out.println("Account Holder: " + account.getAccountHolder());
        System.out.println("Current Balance: " + account.getBalance());
    }
}
