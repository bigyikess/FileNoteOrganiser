from flask import Flask, render_template, url_for, redirect, request, send_from_directory
from datetime import datetime
import os
import sqlite3

app = Flask(__name__)

def exe_sql(sql, action):
    conn = sqlite3.connect('file.db')
    cursor = conn.cursor()

    cursor.execute(sql)

    if action == 'w':
        conn.commit()
        conn.close()

    else:
        data = cursor.fetchall()
        conn.close()
        return data

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/form1", methods=["POST"])
def file1_input():
    name = request.form.get('name')
    file = request.files['file']
    file_type = file.filename.split('.')[-1]
    file.save(f"uploads/{file.filename}")
    file_path = f"uploads/{file.filename}"
    now = datetime.now()
    sql = f"""
    INSERT INTO File(name, type, date, filepath)
    VALUES ('{name}', '{file_type}', '{now.strftime("%d/%m/%Y %H:%M:%S")}', '{file_path}');
    """

    exe_sql(sql, 'w')

    return redirect(url_for('home'))

@app.route("/form2", methods=["POST"])
def file2_input():
    title = request.form.get('title')
    category = request.form.get('category')
    note = request.form.get('note')

    sql = """
    SELECT note_id
    FROM Note
    ORDER BY note_id DESC
    LIMIT 1;
    """
    new_id = exe_sql(sql, 'r')
    if new_id == []:
        new_id = 1
    else:
        new_id = new_id[0][0]

    #file closes after with block
    with open(f'note{new_id}.txt', 'w') as file:
        file.write(note)

    now = datetime.now()
    file_path = f"note{new_id}.txt"

    sql = f"""
    INSERT INTO Note(title, category, date, filepath)
    VALUES ('{title}', '{category}', '{now.strftime("%d/%m/%Y %H:%M:%S")}', '{file_path}');
    """

    exe_sql(sql, 'w')

    return redirect(url_for('home'))  

@app.route("/file", methods=["GET"])
def file():
    sort_by = request.args.get('sort')
    order = request.args.get('order')
    filter_type = request.args.get('type')

    where = "WHERE"
    order_by = "ORDER BY"

    if filter_type == "none" or filter_type == None:
        where = ""
    else:
        where += f" type = '{filter_type}'"

    if sort_by == "none" or sort_by == None:
        order_by = ""
    else:
        order_by += f" {sort_by}"
        if order == "reverse":
            order_by += " DESC"

    sql = f"""
    SELECT name, date, filepath, file_id
    FROM File
    {where}
    {order_by};
    """

    type_sql = f"""
    SELECT DISTINCT(type)
    FROM File;
    """

    data = exe_sql(sql, "r")
    types = exe_sql(type_sql, "r")
    
    
    return render_template("file.html", data=data, types=types, sort_by=sort_by, order=order, filter_type=filter_type)

@app.route("/uploads/<filename>")
def display_file(filename):

    return send_from_directory('uploads', filename)

@app.route("/note", methods=["GET"])
def note():
    sort_by = request.args.get('sort')
    order = request.args.get('order')
    category = request.args.get('category')

    where = "WHERE"
    order_by = "ORDER BY"

    if category == None or category == '':
        where = ""
    else:
        where += f" category = '{category}'"

    if sort_by == "none" or sort_by == None:
        order_by = ""
    else:
        order_by += f" {sort_by}"
        if order == "reverse":
            order_by += " DESC"

    sql = f"""
    SELECT note_id, title, category, date, filepath
    FROM Note
    {where}
    {order_by};
    """

    note_data = exe_sql(sql, "r")
    
    return render_template("note.html", note_data=note_data, sort_by=sort_by, order=order, category=category)

@app.route("/seenote", methods=["GET"])
def see_note():
    note_num = request.args.get('note_num')

    sql = f"""
    SELECT title, filepath
    FROM Note
    WHERE note_id = {note_num};
    """

    info = exe_sql(sql, "r")

    #file closes after with block
    with open(f"{info[0][1]}", "r") as file:
        contents = file.read()

    return render_template("seenote.html", contents=contents, title=info[0][0])

@app.route("/remove", methods=["POST"])
def remove():
    delete_type = request.form.get('type')
    delete_id = request.form.get('id')
    
    sql = f"""
    SELECT filepath
    FROM {delete_type.title()}
    WHERE {delete_type}_id = {delete_id};
    """

    filepath = exe_sql(sql, "r")[0][0]

    delete_sql = f"""
    DELETE
    FROM {delete_type.title()}
    WHERE {delete_type}_id = {delete_id};
    """

    exe_sql(delete_sql, "w")

    os.remove(filepath)
    if delete_type == 'file':
        return redirect(url_for('file'))
    else:
        return redirect(url_for('note'))

if __name__ == "__main__":
    app.run(debug=True)
