from sqlalchemy import create_engine
import pandas as pd
import os
import datetime

def get_db_engine():
    engine = create_engine('sqlite:///database.db', echo=False)
    return engine

def transform_df(df, po):
    output = pd.DataFrame(columns=['Item_Name','Serial_Num','Inventory_Date','Used_Date','PO_Num','Ticket_Num','Asset_Tag'])
    empty = [''] * df.shape[0]
    names = [df.columns[0]] * df.shape[0]
    serial = df[df.columns[0]].tolist()
    date = [datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")] * df.shape[0]
    if po == 'no':
        po_num = [''] * df.shape[0]
    else:
        po_num = [po.strip()] * df.shape[0]
    output['Item_Name'] = names
    output['Serial_Num'] = serial
    output['Inventory_Date'] = date
    output['Used_Date'] = empty
    output['PO_Num'] = po_num
    output['Ticket_Num'] = empty
    output['Asset_Tag'] = empty
    print(output)
    choice = input("Final confirmation before uploading, type 'yes' to upload, 'no' to cancel operation: ")
    if choice == "no":
        return
    else:
        engine = get_db_engine()
        try:
            output.to_sql('Inventory', con=engine, if_exists='append', index=False)
            print("Operation Successful!")
        except Exception as e:
            print("Operation Failed!")
            print(repr(e))
        return


def upload_csv(path = None):
    df = pd.DataFrame()
    if path is None:
        df = pd.read_csv('new_inventory.csv')
        df = df.dropna(axis=1, how='all')
    else:
        df = pd.read_csv(path)
        df = df.dropna(axis=1, how='all')
    print(df)
    choice = input("Confirm the data to be uploaded, type 'yes' to proceed and upload to database, 'no' to cancel operation: ")
    if choice == 'yes':
        po = input("Provide PO number for this upload, 'no' to upload without PO number: ")
        transform_df(df, po)
    else:
        return

def upload_xlsx(path = None):
    df = pd.DataFrame()
    if path is None:
        df = pd.read_excel('new_inventory.xlsx')
        df = df.dropna(axis=1, how='all')
    else:
        df = pd.read_excel(path)
        df = df.dropna(axis=1, how='all')
    print(df)
    choice = input("Confirm the data to be uploaded, type 'yes' to proceed and upload to database, 'no' to cancel operation: ")
    if choice == 'yes':
        po = input("Provide PO number for this upload, 'no' to upload without PO number: ")
        transform_df(df, po)
    else:
        return

if __name__ == "__main__":
    files = [x.casefold() for x in os.listdir()]
    if 'new_inventory.csv'.casefold() in files:
        choice = input("Found new_inventory.csv, type 'yes' to process and upload to database, 'no' to cancel operation: ")
        if choice == 'yes'.casefold():
            upload_csv()
        else:
            pass
    elif 'new_inventory.xlsx'.casefold() in files:
        choice = input("Found new_inventory.xlsx, type 'yes' to process and upload to database, 'no' to cancel operation: ")
        if choice == 'yes'.casefold():
            upload_xlsx()
        else:
            pass
    else:
        choice = input("No excel file found, please type the name of the file or type 'no' to cancel operation: ")
        if choice == 'no'.casefold():
            pass
        else:
            if 'csv' in choice.lower():
                upload_csv(choice)
            elif 'xlsx' in choice.lower():
                upload_xlsx(choice)
            else:
                print("File extension not recognized, please only pass in .csv or .xlsx files!")

    

