DROP TABLE IF EXISTS Inventory;

CREATE TABLE Inventory (
    Item_Name VARCHAR(255) NOT NULL ,
    Serial_Num VARCHAR(255) NOT NULL PRIMARY KEY UNIQUE,
    Inventory_Date datetime NOT NULL,
    Used_Date datetime DEFAULT '',
    PO_Num VARCHAR(255),
    Ticket_Num VARCHAR(255) DEFAULT '',
    Asset_Tag VARCHAR(255) DEFAULT '' 
);