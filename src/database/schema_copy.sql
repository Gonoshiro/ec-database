-- members テーブル
IF OBJECT_ID('members', 'U') IS NULL
BEGIN
    CREATE TABLE members (
        member_id VARCHAR(50) PRIMARY KEY,
        prefecture NVARCHAR(50),
        shop_point INT DEFAULT 0,
        registration_date DATETIME2,
        group_id VARCHAR(50),
        company_name NVARCHAR(50),
        department_name NVARCHAR(50),
        created_at DATETIME2 DEFAULT SYSDATETIME(),
        updated_at DATETIME2 DEFAULT SYSDATETIME()
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_registration_date')
    CREATE INDEX idx_registration_date ON members(registration_date);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_group_id')
    CREATE INDEX idx_group_id ON members(group_id);
GO


-- orders テーブル
IF OBJECT_ID('orders', 'U') IS NULL
BEGIN
    CREATE TABLE orders (
        system_order_number VARCHAR(50) PRIMARY KEY,
        order_date DATETIME2,
        display_order_number VARCHAR(50) UNIQUE,
        delivery_status NVARCHAR(50),
        member_id NVARCHAR(50),
        receiver_post VARCHAR(50),
        receiver_address NVARCHAR(MAX),
        product_name NVARCHAR(MAX),
        product_sell_price INT,
        amount INT,
        variation_name NVARCHAR(MAX),
        product_custom_code NVARCHAR(MAX),
        variation_custom_code NVARCHAR(MAX),
        shipping_charge INT,
        message NVARCHAR(MAX),
        created_at DATETIME2 DEFAULT SYSDATETIME(),
        updated_at DATETIME2 DEFAULT SYSDATETIME()
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_order_date')
    CREATE INDEX idx_order_date ON orders(order_date);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_receiver_post')
    CREATE INDEX idx_receiver_post ON orders(receiver_post);
GO


-- products テーブル
IF OBJECT_ID('products', 'U') IS NULL
BEGIN
    CREATE TABLE products (
        product_id BIGINT IDENTITY(1,1) PRIMARY KEY,
        system_code VARCHAR(50) UNIQUE,
        custom_code VARCHAR(50),
        product_name NVARCHAR(MAX),
        product_group_code VARCHAR(50),
        product_group_name NVARCHAR(MAX),
        sell_price INT,
        consumer_price INT,
        tax_rate DECIMAL(5,2),
        quantity INT,
        display CHAR(1),
        maker VARCHAR(100),
        jan_code VARCHAR(20),
        category_main NVARCHAR(MAX),
        created_date DATETIME2,
        updated_date DATETIME2,
        snapshot_date DATE,
        created_at DATETIME2 DEFAULT SYSDATETIME(),
        updated_at DATETIME2 DEFAULT SYSDATETIME()
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_system_code')
    CREATE INDEX idx_system_code ON products(system_code);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_snapshot_date')
    CREATE INDEX idx_snapshot_date ON products(snapshot_date);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_display')
    CREATE INDEX idx_display ON products(display);
GO