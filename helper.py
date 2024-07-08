import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def process_query(name, serial, po, ticket, tag):
    query = r"SELECT * FROM Inventory WHERE"
    a = False
    if not name == "Item Name":
        query += f" Item_Name = '{name}'"
        a = True
    if len(serial) > 1:
        temp = f" Serial_Num = '{serial}'"
        if a :
            query += " AND "
            query += temp
        else:
            query += temp
            a = True
    if len(po) > 1:
        temp = f" PO_Num = '{po}'"
        if a :
            query += " AND "
            query += temp
        else:
            query += temp
            a = True
    if len(ticket) > 1:
        temp = f" Ticket_Num = '{ticket}'"
        if a :
            query += " AND "
            query += temp
        else:
            query += temp
            a = True
    if len(tag) > 1:
        temp = f" Asset_Tag = '{tag}'"
        if a :
            query += " AND "
            query += temp
        else:
            query += temp
            a = True
    if not a:
        query = query[:-6]
    return query

def remove_header(data):
    if len(data) < 1:
        return data
    elif "Item_Name" in data[0][0]:
        return data[1:]
    else:
        return data

def fetch_all_data():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM Inventory').fetchall()
    conn.close()
    return remove_header(data)

def fetch_all_available():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM Inventory WHERE Ticket_Num = '' AND Asset_tag = ''").fetchall()
    conn.close()
    return remove_header(data)

def fetch_all_used():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM Inventory WHERE Ticket_Num != '' AND Asset_tag != ''").fetchall()
    conn.close()
    return remove_header(data)

def list_all_items():
    conn = get_db_connection()
    data = conn.execute('SELECT DISTINCT Item_Name FROM Inventory;').fetchall()
    conn.close()
    data = [x[0] for x in data if not "Item_Name" in x[0]]
    return remove_header(data)


def execute_search(item_name, serial_num, po_num, ticket_num, asset_tag):
    conn = get_db_connection()
    query = process_query(item_name, serial_num, po_num, ticket_num, asset_tag)
    data = conn.execute(query).fetchall()
    conn.close()
    return remove_header(data)

def find_items(lst):
    if len(lst) < 1:
        return fetch_all_data()
    conn = get_db_connection()
    query = "SELECT * FROM Inventory WHERE "
    for x in lst:
        query += f" Serial_Num = '{x}' OR "
    query = query[:-3]
    data = conn.execute(query).fetchall()
    conn.close()
    return remove_header(data)

def assign_items(serial, ticket, asset):
    conn = get_db_connection()
    for i in range(len(serial)):
        query = f"SELECT COUNT(*) FROM Inventory WHERE Asset_Tag = '{asset[i]}'"
        data = conn.execute(query).fetchall()[0][0]
        if data != 0 :
            raise LookupError()
        query = f"SELECT COUNT(*) FROM Inventory WHERE Serial_Num = '{serial[i]}'"
        data = conn.execute(query).fetchall()[0][0]
        if data != 1 :
            raise NameError()
        query = f"SELECT COUNT(*) FROM Inventory WHERE Serial_Num = '{serial[i]}' AND Asset_Tag = '' AND Ticket_Num = ''"
        data = conn.execute(query).fetchall()[0][0]
        if data != 1 :
            raise SyntaxError()
        query = f"UPDATE Inventory SET Used_Date = CURRENT_TIMESTAMP, Ticket_Num = '{ticket}', Asset_Tag = '{asset[i]}' WHERE Serial_Num = '{serial[i]}'"
        conn.execute(query)
    conn.commit()
    conn.close()
    data = find_items(serial)
    return data

def summary():
    conn = get_db_connection()
    item_names = list_all_items()
    output = {}
    for x in item_names:
        query = f"SELECT COUNT(*) FROM Inventory WHERE Item_Name = '{x}'"
        total = conn.execute(query).fetchall()[0][0]
        query = f"SELECT COUNT(*) FROM Inventory WHERE Item_Name = '{x}' AND Ticket_Num = '' AND Asset_tag = ''"
        ava = conn.execute(query).fetchall()[0][0]
        query = f"SELECT COUNT(*) FROM Inventory WHERE Item_Name = '{x}' AND Ticket_Num != '' AND Asset_tag != ''"
        used  = conn.execute(query).fetchall()[0][0]
        output[x] = [ava, used, total]
    return output

def unassign_items(lst):
    conn = get_db_connection()
    for s in lst:
        query = f"SELECT COUNT(*) FROM Inventory WHERE Serial_Num = '{s}'"
        data = conn.execute(query).fetchall()[0][0]
        if data != 1:
            raise NameError()
        query = f"UPDATE Inventory SET Used_Date = NULL, Ticket_Num = '', Asset_Tag = '' WHERE Serial_Num = '{s}'"
        conn.execute(query)
    conn.commit()
    conn.close()
    data = find_items(lst)
    return data

def get_summary(data):
    if len(data) > 100 :
        return "N/A"
    count = {}
    dix = {}
    for row in data:
        name = row[0]
        serial = row[1]
        tag = row[-1]
        if name in dix:
            dix[name] += f"\r\n\r\n\t{serial}\r\n\t{tag}"
        else:
            dix[name] = f"\t{serial}\r\n\t{tag}"
        if name in count:
            count[name] += 1
        else:
            count[name] = 1
    txt = ""
    for row in count:
        txt += f"\r\n{count[row]} x {row}\r\n"
        txt += f"\r\n{dix[row]}\r\n"
    return txt[2:]