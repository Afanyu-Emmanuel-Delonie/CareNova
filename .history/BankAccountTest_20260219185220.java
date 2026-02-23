import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

public class BankAccountTest {

    // Declaring the BankAccount object
    private BankAccount account;

    // @BeforeEach runs before every single test method
    // Used to set up a fresh BankAccount object before each test
    @BeforeEach
    public void setUp() {
        account = new BankAccount("John Doe", 1000.00);
    }

    // Test Case 1: Check that the account is created with the correct balance
    @Test
    public void testInitialBalance() {
        assertEquals(1000.00, account.getBalance(),
                "Initial balance should be 1000.00");
    }

    // Test Case 2: Check that the account holder name is correct
    @Test
    public void testAccountHolder() {
        assertEquals("John Doe", account.getAccountHolder(),
                "Account holder should be John Doe");
    }

    // Test Case 3: Test depositing a valid amount
    @Test
    public void testDeposit() {
        account.deposit(500.00);
        assertEquals(1500.00, account.getBalance(),
                "Balance after deposit should be 1500.00");
    }

    // Test Case 4: Test withdrawing a valid amount
    @Test
    public void testWithdraw() {
        account.withdraw(200.00);
        assertEquals(800.00, account.getBalance(),
                "Balance after withdrawal should be 800.00");
    }

    // Test Case 5: Test that depositing a negative amount throws an exception
    @Test
    public void testDepositNegativeAmount() {
        assertThrows(IllegalArgumentException.class, () -> {
            account.deposit(-100.00);
        }, "Depositing a negative amount should throw IllegalArgumentException");
    }

    // Test Case 6: Test that withdrawing more than balance throws an exception
    @Test
    public void testWithdrawInsufficientFunds() {
        assertThrows(IllegalArgumentException.class, () -> {
            account.withdraw(5000.00);
        }, "Withdrawing more than balance should throw IllegalArgumentException");
    }

    // Test Case 7: Test that creating an account with negative balance throws
    // exception
    @Test
    public void testNegativeInitialBalance() {
        assertThrows(IllegalArgumentException.class, () -> {
            new BankAccount("Jane Doe", -500.00);
        }, "Negative initial balance should throw IllegalArgumentException");
    }

    // @AfterEach runs after every test method
    // Used here to simply display a message (could also be used to clean up
    // resources)
    @AfterEach
    public void tearDown() {
        System.out.println("Test completed.");
    }
}