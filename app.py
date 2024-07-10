from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
import os
from helper import execute_search, fetch_all_data, list_all_items, assign_items, summary, unassign_items, get_summary, transform_df, get_db_engine

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    data = summary()
    return render_template("home.html", data = data)
    
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        name = request.form['item_name']
        serial = request.form['serial_num']
        po = request.form['po_num']
        ticket = request.form['ticket_num']
        tag = request.form['asset_tag']
        data = execute_search(name, serial, po, ticket, tag)
        return render_template('index.html', data = data, name = list_all_items())
    else:
        return render_template('index.html', data = fetch_all_data(), name = list_all_items())

@app.route('/assign', methods=['POST', 'GET'])
def assign():
    if request.method == "GET":
            return render_template('assign.html', data = fetch_all_data(), name = list_all_items(), summary = get_summary(fetch_all_data()))
    else:        
        serials = request.form['serial_num']
        serials = [x.strip() for x in serials.splitlines()]

        ticket_num = request.form['ticket_num']

        tags = request.form['asset_tag']
        tags = [x.strip() for x in tags.splitlines()]

        for t in tags:
            if len(t) != 6 or not t.isnumeric():
                flash("Asset tag format error!")
                return redirect(url_for('search'))

        if len(serials) != len(tags):
            flash("Serial number and asset tag length does not match!")
            return redirect(url_for('search'))
        try:
            data = assign_items(serial=serials, ticket=ticket_num, asset=tags)
        except LookupError:
            flash("Asset tag already exist in database!")
            return redirect(url_for('search'))
        except NameError:
            flash("Serial number not found in database!")
            return redirect(url_for('search'))
        except SyntaxError:
            flash("Item has already been assigned to another ticket!")
            return redirect(url_for('search'))

        
        return render_template('assign.html', data = data, name = list_all_items(), summary = get_summary(data))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'submit_button' in request.form and request.form['submit_button'] == 'Upload':
            if not os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv")):
                flash("Cannot upload before processing!")
                return render_template("upload.html", data = [])
            data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"))
            data = data.fillna('')
            engine = get_db_engine()
            try:
                data.to_sql('Inventory', con=engine, if_exists='append', index=False)
                flash("Operation Successful!")
            except Exception as e:
                flash("Operation Failed! \n" + repr(e))
            finally:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"))
            return render_template('index.html', data = fetch_all_data(), name = list_all_items())
        else:
                if 'file' not in request.files:
                    flash('ERROR! No files received!')
                    return render_template("upload.html", data = [])
                file = request.files['file']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    flash('No files selected !!')
                    return render_template("upload.html", data = [])
                if not (".csv" in file.filename or ".xlsx" in file.filename):
                    flash('Only upload .csv or .xlsx files please!!')
                    return render_template("upload.html", data = [])
                try:
                    
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    # if ".csv" in file.filename:
                    #     df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    #     df = df.dropna(axis=1, how='all')
                    # elif ".xlsx" in file.filename:
                    #     df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    #     df = df.dropna(axis=1, how='all')
                    # else:
                    #     flash('Only upload .csv or .xlsx files please!!')
                    #     return render_template("upload.html", data = [])
                    
                    # po = request.form['po_num']
                    # if len(po) < 3 or not "PO_" in po:
                    #     data = transform_df(df, "")
                    # else:
                    #     data = transform_df(df, po)

                    # for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    #     os.unlink(file_path)
                    data = pd.DataFrame()
                    data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], "temp.csv"), index=False, header=True)
                    
                    return render_template('upload.html', data = data.values)
                except Exception as e:
                    flash("Operation Failed! \n" + repr(e))
                    return render_template("upload.html", data = [])
    return render_template("upload.html", data = [])

@app.route('/unassign', methods=['POST', 'GET'])
def unassign():
    if request.method == "GET":
            return render_template('unassign.html')
    else:
        if "safety1" in request.form.keys() and "safety2" in request.form.keys():
            serials = request.form['serial_num']
            serials = [x.strip() for x in serials.splitlines()]
            try:
                data = unassign_items(serials)
            except NameError:
                flash("Serial number not found in database!")
                return render_template('index.html', data = fetch_all_data(), name = list_all_items())
            return render_template('index.html', data = data, name = list_all_items())
        else:
            flash("Safety check did not pass!")
            return render_template('unassign.html')
if __name__ == "__main__":
    try:
        os.mkdir(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']) )
    except:
        pass
    app.run(host="0.0.0.0", port=8000)