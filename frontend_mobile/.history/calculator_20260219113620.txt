// CalculatorTest.java
import org.junit.Test;
import static org.junit.Assert.*;

public class CalculatorTest {

    Calculator calc = new Calculator();

    // Test case 1: Testing addition
    @Test
    public void testAdd() {
        int result = calc.add(3, 5);
        assertEquals(8, result); // expected = 8, actual = result
    }

    // Test case 2: Testing subtraction
    @Test
    public void testSubtract() {
        int result = calc.subtract(10, 4);
        assertEquals(6, result);
    }

    // Test case 3: Testing multiplication
    @Test
    public void testMultiply() {
        int result = calc.multiply(3, 4);
        assertEquals(12, result);
    }

    // Test case 4: Testing division
    @Test
    public void testDivide() {
        double result = calc.divide(10, 2);
        assertEquals(5.0, result, 0.001); // 0.001 is the delta for double comparison
    }

    // Test case 5: Testing division by zero
    @Test(expected = ArithmeticException.class)
    public void testDivideByZero() {
        calc.divide(10, 0); // This should throw an exception
    }
}