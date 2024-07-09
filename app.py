from flask import Flask, render_template, request, flash, redirect, url_for
from helper import execute_search, fetch_all_data, list_all_items, assign_items, summary, unassign_items, get_summary

app = Flask(__name__)
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
    app.run(host="0.0.0.0", port=8000)