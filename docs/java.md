# Java Programming Language Guide

## Introduction

Java is a high-level, class-based, object-oriented programming language that is designed to have as few implementation dependencies as possible. It was originally developed by James Gosling at Sun Microsystems and released in 1995 as part of Sun Microsystems' Java platform.

### Key Features

Java is known for several distinctive characteristics:

- **Platform Independence**: Write once, run anywhere (WORA)
- **Object-Oriented**: Everything is an object in Java
- **Robust**: Strong memory management and exception handling
- **Secure**: Built-in security features
- **Multithreaded**: Support for concurrent programming
- **High Performance**: Just-in-time compilation

## History and Evolution

Java was initially called Oak and was developed for handheld devices and set-top boxes. The language evolved significantly over the years:

### Major Versions

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| Java 1.0 | January 1996 | Initial release |
| Java 1.1 | February 1997 | Inner classes, JavaBeans |
| Java 1.2 | December 1998 | Collections framework, Swing |
| Java 1.3 | May 2000 | HotSpot JVM |
| Java 1.4 | February 2002 | Assert keyword, regular expressions |
| Java 5 | September 2004 | Generics, autoboxing, enums |
| Java 6 | December 2006 | Scripting support |
| Java 7 | July 2011 | Diamond operator, try-with-resources |
| Java 8 | March 2014 | Lambda expressions, Stream API |
| Java 9 | September 2017 | Module system |
| Java 11 | September 2018 | LTS release, var keyword |
| Java 17 | September 2021 | Current LTS, records, sealed classes |

## Basic Syntax

### Hello World Program

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

### Variable Declaration

```java
// Primitive types
int number = 42;
double price = 19.99;
boolean isActive = true;
char grade = 'A';

// Reference types
String name = "Java";
List<String> languages = new ArrayList<>();
```

### Control Structures

#### Conditional Statements

```java
if (condition) {
    // code block
} else if (anotherCondition) {
    // code block
} else {
    // code block
}

switch (variable) {
    case VALUE1:
        // code
        break;
    case VALUE2:
        // code
        break;
    default:
        // default code
}
```

#### Loops

```java
// For loop
for (int i = 0; i < 10; i++) {
    System.out.println(i);
}

// Enhanced for loop
for (String item : collection) {
    System.out.println(item);
}

// While loop
while (condition) {
    // code block
}

// Do-while loop
do {
    // code block
} while (condition);
```

## Object-Oriented Programming

### Classes and Objects

```java
public class Person {
    private String name;
    private int age;
    
    // Constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Getter methods
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
    
    // Setter methods
    public void setName(String name) {
        this.name = name;
    }
    
    public void setAge(int age) {
        this.age = age;
    }
}
```

### Inheritance

```java
public class Student extends Person {
    private String studentId;
    
    public Student(String name, int age, String studentId) {
        super(name, age);
        this.studentId = studentId;
    }
    
    public String getStudentId() {
        return studentId;
    }
}
```

### Interfaces

```java
public interface Drawable {
    void draw();
    
    default void print() {
        System.out.println("Printing...");
    }
}

public class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing a circle");
    }
}
```

## Exception Handling

Java provides robust exception handling mechanisms:

```java
try {
    // Risky code
    int result = divide(10, 0);
} catch (ArithmeticException e) {
    System.err.println("Division by zero: " + e.getMessage());
} catch (Exception e) {
    System.err.println("General exception: " + e.getMessage());
} finally {
    // Cleanup code
    System.out.println("Cleanup completed");
}
```

### Custom Exceptions

```java
public class CustomException extends Exception {
    public CustomException(String message) {
        super(message);
    }
}
```

## Collections Framework

Java provides a comprehensive collections framework:

### Common Collections

- **List**: Ordered collection (ArrayList, LinkedList, Vector)
- **Set**: Unique elements (HashSet, TreeSet, LinkedHashSet)
- **Map**: Key-value pairs (HashMap, TreeMap, LinkedHashMap)
- **Queue**: FIFO operations (LinkedList, PriorityQueue)

```java
// List example
List<String> fruits = new ArrayList<>();
fruits.add("Apple");
fruits.add("Banana");
fruits.add("Orange");

// Set example
Set<Integer> numbers = new HashSet<>();
numbers.add(1);
numbers.add(2);
numbers.add(3);

// Map example
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.put("Bob", 87);
scores.put("Charlie", 92);
```

## Modern Java Features

### Lambda Expressions (Java 8+)

```java
// Traditional approach
Comparator<String> comp1 = new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.compareTo(b);
    }
};

// Lambda expression
Comparator<String> comp2 = (a, b) -> a.compareTo(b);

// Method reference
Comparator<String> comp3 = String::compareTo;
```

### Stream API (Java 8+)

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

List<String> filteredNames = names.stream()
    .filter(name -> name.length() > 4)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
```

### Records (Java 14+)

```java
public record Point(int x, int y) {
    // Compact constructor
    public Point {
        if (x < 0 || y < 0) {
            throw new IllegalArgumentException("Coordinates must be non-negative");
        }
    }
}
```

### Pattern Matching (Java 17+)

```java
public String formatValue(Object obj) {
    return switch (obj) {
        case String s -> "String: " + s;
        case Integer i -> "Integer: " + i;
        case Double d -> "Double: " + d;
        case null -> "null value";
        default -> "Unknown type: " + obj.getClass().getSimpleName();
    };
}
```

## Multithreading

Java provides built-in support for multithreading:

### Creating Threads

```java
// Extending Thread class
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread running: " + Thread.currentThread().getName());
    }
}

// Implementing Runnable interface
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable running: " + Thread.currentThread().getName());
    }
}

// Using threads
Thread thread1 = new MyThread();
Thread thread2 = new Thread(new MyRunnable());

thread1.start();
thread2.start();
```

### Synchronization

```java
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}
```

## Best Practices

### Coding Standards

1. **Naming Conventions**
   - Classes: PascalCase (e.g., `MyClass`)
   - Methods and variables: camelCase (e.g., `myMethod`)
   - Constants: UPPER_SNAKE_CASE (e.g., `MAX_SIZE`)
   - Packages: lowercase (e.g., `com.example.myapp`)

2. **Code Organization**
   - One public class per file
   - Logical package structure
   - Proper imports (avoid wildcards)

3. **Documentation**
   - Use Javadoc for public APIs
   - Meaningful variable and method names
   - Clear comments for complex logic

### Performance Tips

- Use StringBuilder for string concatenation in loops
- Prefer ArrayList over Vector for single-threaded applications
- Use primitive collections when possible
- Implement proper equals() and hashCode() methods
- Consider using lazy initialization for expensive objects

### Security Considerations

- Validate all input data
- Use parameterized queries to prevent SQL injection
- Avoid serialization of sensitive data
- Use secure random number generators
- Follow the principle of least privilege

## Common Design Patterns

### Singleton Pattern

```java
public class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

### Factory Pattern

```java
public interface Shape {
    void draw();
}

public class Circle implements Shape {
    @Override
    public void draw() {
        System.out.println("Drawing Circle");
    }
}

public class ShapeFactory {
    public static Shape createShape(String type) {
        return switch (type.toLowerCase()) {
            case "circle" -> new Circle();
            case "rectangle" -> new Rectangle();
            default -> throw new IllegalArgumentException("Unknown shape: " + type);
        };
    }
}
```

### Observer Pattern

```java
public interface Observer {
    void update(String message);
}

public class Subject {
    private List<Observer> observers = new ArrayList<>();
    
    public void addObserver(Observer observer) {
        observers.add(observer);
    }
    
    public void notifyObservers(String message) {
        for (Observer observer : observers) {
            observer.update(message);
        }
    }
}
```

## Testing

### JUnit Example

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class CalculatorTest {
    
    @Test
    public void testAddition() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(2, 3));
    }
    
    @Test
    public void testDivisionByZero() {
        Calculator calc = new Calculator();
        assertThrows(ArithmeticException.class, () -> calc.divide(10, 0));
    }
}
```

## Conclusion

Java continues to be one of the most popular programming languages in the world, powering everything from enterprise applications to Android mobile apps. Its strong ecosystem, platform independence, and continuous evolution make it an excellent choice for developers.

### Key Takeaways

- Java's "write once, run anywhere" philosophy provides excellent portability
- Strong object-oriented programming support with modern functional programming features
- Robust memory management and garbage collection
- Extensive standard library and third-party ecosystem
- Active community and regular updates with new features

### Further Learning

To continue your Java journey, consider exploring:

- **Spring Framework**: For enterprise application development
- **Android Development**: Mobile app development with Java/Kotlin
- **Maven/Gradle**: Build automation tools
- **JPA/Hibernate**: Object-relational mapping
- **Microservices**: Using Spring Boot and related technologies

---

*This guide provides a comprehensive overview of Java programming language fundamentals and advanced concepts. For the most up-to-date information, refer to the official Oracle Java documentation.*