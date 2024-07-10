import sqlite3
import csv
connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())
    

cur = connection.cursor()

with open("db_Inventory.csv", "r") as file:
        
        for index, row in enumerate(csv.reader(file)):
            cur.execute("""
                INSERT INTO Inventory (Item_Name, Serial_Num, Inventory_Date, Used_Date, PO_Num, Ticket_Num, Asset_Tag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [*row[1:]])
            
id = 0
for row in cur.execute("SELECT * from Inventory"):
    print(row)
    id += 1
    if id > 15:
        break
connection.commit()
connection.close()