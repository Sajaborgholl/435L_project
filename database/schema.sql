-- Customers Table
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName TEXT NOT NULL,
    Username TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL,
    Age INTEGER,
    Address TEXT,
    Gender TEXT CHECK (Gender IN ('Male', 'Female', 'Other')),
    MaritalStatus TEXT CHECK (MaritalStatus IN ('Single', 'Married', 'Divorced', 'Widowed')),
    Wallet REAL DEFAULT 0,
    UserRole INTEGER DEFAULT 0 
);


-- Inventory Table
CREATE TABLE IF NOT EXISTS Inventory (
    ProductID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL CHECK(Category IN ('Food', 'Clothes', 'Accessories', 'Electronics')),
    Price REAL NOT NULL,
    Description TEXT,
    Stock INTEGER NOT NULL -- Represents the count of available items in stock
);

-- Sales Table
CREATE TABLE IF NOT EXISTS Sales (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerUsername TEXT NOT NULL,
    ProductID INTEGER,
    Quantity INTEGER NOT NULL,
    TotalPrice REAL NOT NULL, 
    SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (CustomerUsername) REFERENCES Customers(CustomerUsername),
    FOREIGN KEY (ProductID) REFERENCES Inventory(ProductID)
);

-- Historical Purchases Table
CREATE TABLE IF NOT EXISTS HistoricalPurchases (
    CustomerUsername TEXT PRIMARY KEY,
    PurchaseHistory TEXT -- Stores all purchases as a JSON string
);
CREATE TABLE IF NOT EXISTS Wishlist (
    CustomerUsername TEXT PRIMARY KEY,
    List TEXT, -- Stores the list of product IDs as a JSON string
    FOREIGN KEY (CustomerUsername) REFERENCES Customers(Username)
);

CREATE TABLE IF NOT EXISTS Reviews (
    ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductID INTEGER NOT NULL,
    CustomerUsername TEXT NOT NULL,
    Rating INTEGER NOT NULL CHECK (Rating BETWEEN 1 AND 5),
    Comment TEXT,
    Status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Flagged'
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ProductID) REFERENCES Inventory(ProductID),
    FOREIGN KEY (CustomerUsername) REFERENCES Customers(Username)
);

-- API Logs Table (Optional for Tracking API Requests)
CREATE TABLE IF NOT EXISTS APILogs (
    LogID INTEGER PRIMARY KEY,
    Endpoint TEXT NOT NULL,
    RequestType TEXT NOT NULL CHECK(RequestType IN ('GET', 'POST', 'PUT', 'DELETE')),
    Timestamp TEXT NOT NULL -- ISO format (YYYY-MM-DD HH:MM:SS)
);
