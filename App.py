from flask import Flask, render_template, request, session, flash

import mysql.connector
import base64, os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaa'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route('/UserLogin')
def UserLogin():
    return render_template('UserLogin.html')


@app.route('/NewPatient')
def NewPatient():
    return render_template('NewPatient.html')


@app.route('/NewUser')
def NewUser():
    return render_template('NewUser.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb ")
            data = cur.fetchall()
            flash("you are successfully Login")
            return render_template('AdminHome.html', data=data)

        else:
            flash("UserName or Password Incorrect!")
            return render_template('AdminLogin.html')


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb  ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/PatientInfo")
def PatientInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM patienttb  ")
    data = cur.fetchall()
    return render_template('PatientInfo.html', data=data)


@app.route("/Record")
def Record():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM predicttb  ")
    data = cur.fetchall()
    return render_template('Record.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['uname']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + name + "','" + mobile + "','" + email + "','" + address + "','" + username + "','" + password + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")

    return render_template('NewUser.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['sname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:
            flash('Username or Password is wrong')
            return render_template('UserLogin.html', data=data)

        else:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and password='" + password + "'")
            data = cur.fetchall()
            flash("you are successfully logged in")
            return render_template('UserHome.html', data=data)


@app.route('/UserHome')
def UserHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
    cur = conn.cursor()
    cur.execute("SELECT username FROM regtb  where username='" + session['sname'] + "' ")
    data = cur.fetchall()
    return render_template('UserHome.html', data=data)


@app.route("/newpatient", methods=['GET', 'POST'])
def newpatient():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        aano = request.form['aano']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into patienttb values('','" + name + "','" + mobile + "','" + email + "','" + address + "','" + aano + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")
    return render_template('NewPatient.html')


@app.route('/Predict')
def Predict():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
    cur = conn.cursor()
    cur.execute("SELECT aadharNo FROM patienttb  ")
    data = cur.fetchall()
    return render_template('Predict.html', data=data)


@app.route("/imupload", methods=['GET', 'POST'])
def imupload():
    if request.method == 'POST':
        rname = request.form['rname']
        file = request.files['file']
        import random
        fnew = random.randint(1111, 9999)
        savename = str(fnew) + ".jpg"
        file.save("static/upload/" + savename)
        org = "static/upload/" + savename

        import tensorflow as tf
        classifierLoad = tf.keras.models.load_model('diabetic.h5')

        import numpy as np
        from keras.preprocessing import image
        test_image = image.load_img('./static/upload/' + savename, target_size=(200, 200))
        # test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis=0)
        result = classifierLoad.predict(test_image)
        print(result)

        out = ''
        re = ""
        if result[0][0] == 1:
            print("NoDR")
            out = "NoDR"
            re = ''


        elif result[0][1] == 1:
            print("Mild")
            out = "Mild"
            re = 'Possibly, diabetes medication or insulin therapy'

        elif result[0][2] == 1:
            print("Moderate")
            out = "Moderate"
            re = 'Short-acting (regular) insulin'
        elif result[0][3] == 1:
            print("Severe")
            out = "Severe"
            re = 'canagliflozin-metformin (Invokamet, Invokamet XR)'
        elif result[0][4] == 1:
            print("ProliferativeDR")
            out = "ProliferativeDR"
            re = 'Ranibizumab (Lucentis) and aflibercept (Eylea) are the main medications used to treat proliferative diabetic retinopathy (PDR)'

        else:
            out = "Nill"
            re = 'Nill'

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into predicttb values('','" + session[
                'sname'] + "','" + rname + "','" + savename + "','" + out + "','" + re + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")
        return render_template('Predict.html', res=out, org=org)


@app.route('/PredictInfo')
def PredictInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='2diabeticdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM predicttb where UserName='" + session['sname'] + "' ")
    data = cur.fetchall()
    return render_template('PredictInfo.html', data=data)


def sendmail(Mailid, message):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "sampletest685@gmail.com"
    toaddr = Mailid

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    body = message

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "hneucvnontsuwgpj")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
