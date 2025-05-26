#gemini
from flask import Flask,request,render_template
from google import genai
import google.generativeai as genai1
import os
import sqlite3
import datetime
import requests

gemini_api_key = os.getenv("gemini_api_key")

genmini_client = genai.Client(api_key=gemini_api_key)
genmini_model = "gemini-2.0-flash"

os.environ["GOOGLE_API_KEY"] = "AIzaSyDkxn6-Gb73-_Gkvhyc6sImOumIJkATemY"

#genai.configure(api_key="AIzaSyDkxn6-Gb73-_Gkvhyc6sImOumIJkATemY")

# gemini_api_key = os.getenv("AIzaSyDkxn6-Gb73-_Gkvhyc6sImOumIJkATemY")

genai1.configure(api_key=gemini_api_key)
model = genai1.GenerativeModel("gemini-2.0-flash")

gemini_telegram_token = os.getenv('GEMINI_TELEGRAM_TOKEN')

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

@app.route("/start_telegram",methods=["GET","POST"])
def start_telegram():

    domain_url = os.getenv('WEBHOOK_URL')

    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{gemini_telegram_token}/deleteWebhook"
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    
    # Set the webhook URL for the Telegram bot
    set_webhook_url = f"https://api.telegram.org/bot{gemini_telegram_token}/setWebhook?url={domain_url}/telegram"
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    print('webhook:', webhook_response)
    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot is running. Please check with the telegram bot. @dsai_wendy_gemini_bot"
    else:
        status = "Failed to start the telegram bot. Please check the logs."
    
    return(render_template("telegram.html", status=status))

@app.route("/telegram",methods=["GET","POST"])
def telegram():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text == "/start":
            r_text = "Welcome to the Gemini Telegram Bot! You can ask me any finance-related questions."
        else:
            # Process the message and generate a response
            system_prompt = "You are a financial expert.  Answer ONLY questions related to finance, economics, investing, and financial markets. If the question is not related to finance, state that you cannot answer it."
            prompt = f"{system_prompt}\n\nUser Query: {text}"
            r = genmini_client.models.generate_content(
                model=genmini_model,
                contents=prompt
            )
            r_text = r.text
        
        # Send the response back to the user
        send_message_url = f"https://api.telegram.org/bot{gemini_telegram_token}/sendMessage"
        requests.post(send_message_url, data={"chat_id": chat_id, "text": r_text})
    # Return a 200 OK response to Telegram
    # This is important to acknowledge the receipt of the message
    # and prevent Telegram from resending the message
    # if the server doesn't respond in time
    return('ok', 200)

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