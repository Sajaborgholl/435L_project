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
    Name TEXT NOT NULL,
    Category TEXT NOT NULL CHECK(Category IN ('Food', 'Clothes', 'Accessories', 'Electronics')),
    Price REAL NOT NULL,
    Description TEXT,
    Stock INTEGER NOT NULL -- Represents the count of available items in stock
);

-- Sales Table
CREATE TABLE IF NOT EXISTS Sales (
    SaleID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    ProductID INTEGER,
    Quantity INTEGER NOT NULL,
    TotalAmount REAL NOT NULL, -- Represents the total cost of the sale
    SaleDate TEXT NOT NULL, -- ISO format (YYYY-MM-DD)
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Inventory(ProductID)
);

-- Historical Purchases Table
CREATE TABLE IF NOT EXISTS HistoricalPurchases (
    PurchaseID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    ProductID INTEGER,
    Quantity INTEGER NOT NULL,
    PurchaseDate TEXT NOT NULL, -- ISO format (YYYY-MM-DD)
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Inventory(ProductID)
);

-- Reviews Table
CREATE TABLE IF NOT EXISTS Reviews (
    ReviewID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    ProductID INTEGER,
    Rating INTEGER CHECK(Rating BETWEEN 1 AND 5),
    Comment TEXT,
    ReviewDate TEXT NOT NULL, -- ISO format (YYYY-MM-DD)
    Moderated INTEGER DEFAULT 0, -- 0 for unmoderated, 1 for moderated
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Inventory(ProductID)
);

-- API Logs Table (Optional for Tracking API Requests)
CREATE TABLE IF NOT EXISTS APILogs (
    LogID INTEGER PRIMARY KEY,
    Endpoint TEXT NOT NULL,
    RequestType TEXT NOT NULL CHECK(RequestType IN ('GET', 'POST', 'PUT', 'DELETE')),
    Timestamp TEXT NOT NULL -- ISO format (YYYY-MM-DD HH:MM:SS)
);
