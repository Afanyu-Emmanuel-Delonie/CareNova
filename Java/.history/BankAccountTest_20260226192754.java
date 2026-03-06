import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class BankAccountTest {

    private BankAccount account;

    @BeforeEach
    public void setUp() {
        account = new BankAccount("John Doe", -1000.00);
    }

    @Test
    public void testInitialBalance() {
        assertEquals(1000.00, account.getBalance(),
                "Initial balance should be 1000.00");
    }

    @Test
    public void testAccountHolder() {
        assertEquals("John Doe", account.getAccountHolder(),
                "Account holder should be John Doe");
    }

    @Test
    public void testDeposit() {
        account.deposit(500.00);
        assertEquals(1500.00, account.getBalance(),
                "Balance after deposit should be 1500.00");
    }

    @Test
    public void testWithdraw() {
        account.withdraw(200.00);
        assertEquals(800.00, account.getBalance(),
                "Balance after withdrawal should be 800.00");
    }

    @Test
    public void testDepositNegativeAmount() {
        assertThrows(IllegalArgumentException.class, () -> account.deposit(-100.00),
                "Depositing a negative amount should throw IllegalArgumentException");
    }

    @Test
    public void testWithdrawInsufficientFunds() {
        assertThrows(IllegalArgumentException.class, () -> account.withdraw(5000.00),
                "Withdrawing more than balance should throw IllegalArgumentException");
    }

    @Test
    public void testNegativeInitialBalance() {
        assertThrows(IllegalArgumentException.class, () -> new BankAccount("Jane Doe", -500.00),
                "Negative initial balance should throw IllegalArgumentException");
    }

    @AfterEach
    public void tearDown() {
        System.out.println("Test completed.");
    }
}
