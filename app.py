#gemini
from flask import Flask,request,render_template
import os
import sqlite3
import datetime
#os.environ["GOOGLE_API_KEY"] = "AIzaSyDkxn6-Gb73-_Gkvhyc6sImOumIJkATemY"

import google.generativeai as genai
#genai.configure(api_key="AIzaSyB9szziVsPc8wEmYJoDOIifUC-vv_tj1Vw")
#genai.configure(api_key="AIzaSyDkxn6-Gb73-_Gkvhyc6sImOumIJkATemY")

gemini_api_key = os.getenv("gemini_api_key")
# gemini_api_key = os.getenv("AIzaSyDkxn6-Gb73-_Gkvhyc6sImOumIJkATemY")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")
app = Flask(__name__)

first_time = 1
@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    global first_time
    if first_time==1:
        q = request.form.get("q")
        print(q)
        t = datetime.datetime.now()
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("insert into users(name,timestamp) values(?,?)",(q,t))
        conn.commit()
        c.close()
        conn.close()
        first_time=0

    # def main():
    # username = request.form.get('username', '')
    # if username:
    #     insert_user(username)
    # return render_template('main.html')

    return(render_template("main.html"))

@app.route("/gemini",methods=["GET","POST"])
def gemini():
    return(render_template("gemini.html"))

# @app.route("/gemini_reply",methods=["GET","POST"])
# def gemini_reply():
#     q = request.form.get('q')
#     print(q)
#     r = model.generate_content(q)
#     return(render_template("gemini_reply.html",r=r.text))

#From Chatgtp
@app.route("/gemini_reply", methods=['POST'])
def gemini_reply():
    q = request.form.get('q')
    if not q:
        return "Error: No query provided", 400
    try:
        r = model.generate_content(q)
        return render_template('gemini_reply.html', r=r.text)
    except Exception as e:
        return f"Error generating response: {e}", 500


@app.route("/paynow",methods=["GET","POST"])
def paynow():
    return(render_template("paynow.html"))

@app.route("/prediction",methods=["GET","POST"])
def prediction():
    return(render_template("prediction.html"))

@app.route("/prediction_reply",methods=["GET","POST"])
def prediction_reply():
    q = float(request.form.get("q"))
    print(q)
    return(render_template("prediction_reply.html",r=90.2 + (-50.6*q)))

@app.route("/user_log",methods=["GET","POST"])
def user_log():
    #read
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from users")
    r=""
    for row in c:
        print(row)
        r= r+str(row)
    c.close()
    conn.close()
    return(render_template("user_log.html",r=r))

@app.route("/delete_log",methods=["GET","POST"])
def delete_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("delete from users")
    conn.commit()
    c.close()
    conn.close()    
    return(render_template("delete_log.html"))

@app.route("/logout",methods=["GET","POST"])
def logout():
    global first_time
    first_time = 1
    return(render_template("index.html"))


if __name__ == "__main__":
    app.run()