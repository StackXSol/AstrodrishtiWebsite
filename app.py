from ast import For
import code
import datetime
from distutils.log import error
import email
from heapq import merge
import json
import random
from xmlrpc.client import DateTime
from flask import Flask, jsonify, redirect, render_template, session, request
from flask_session import Session
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1 import Increment
from firebase_admin import credentials
from pyparsing import empty
import pyrebase
from razorpay import Client
import razorpay
import requests

#$testing
rz_client = razorpay.Client(auth=("rzp_test_Ww5UbkjQTQfkNY", "AZFiEtHfXlpBbKyVtUF6erwL"))

#live
#rz_client = razorpay.Client(auth=("rzp_live_mPA0XlwHVV6cAd", "CCBOmp2wI0XW0rDe9MCSZGdx"))

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
astro_url = 'https://api.vedicastroapi.com/json/prediction/dailysun'
Session(app)

def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    with smtplib.SMTP_SSL(host="mail.stackxsolutions.in") as smtp:
        smtp.login(user,pwd)
        smtp.sendmail(user,TO,message)
        smtp.quit()  

config = {
    "apiKey": "AIzaSyAHs2rZusPbs1BjngrenWT3NpCqEztRru0",
    "authDomain": "astrodrishti2.firebaseapp.com",
    "projectId": "astrodrishti2",
    "databaseURL": "https://astrodrishti2.firebaseio.com",
    "storageBucket": "astrodrishti2.appspot.com",
    "messagingSenderId": "1049927656681",
    "appId": "1:1049927656681:web:de5ac57143891dd1b4bc78",
    "measurementId": "G-X87JGEKJJ0"
}

cred = credentials.Certificate('fbadminconfig.json')
firebase_db = firebase_admin.initialize_app(cred,{
  'projectId': 'astrodrishti2',
  'storageBucket': 'astrodrishti2.appspot.com'
})
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firestore.client()

#authentications

@app.route("/sign-up")
def signup():      
    return render_template("SignUp.html")   


@app.route("/login")
def login():
    if not session.get("error"):  
        return render_template("login.html")
    else:        
        return render_template("login.html")

@app.route("/signout")
def signout():   
    session.clear()
    return redirect('/')


@app.route("/")
def index():    
    if not session.get("email"):    
        return render_template("index.html",email = session.get("email"), show1 = "", show2 = "hidden" )   
    
    return render_template("index.html",email = session.get("email"), show1 = "hidden", show2 = "" )

@app.route("/home")
def home():
    return render_template("Homescreen.html", email = session.get("email"))


@app.route("/horoscope")
def horoscope():
    if not session.get("email"):    
        return render_template("Horoscope.html",email = session.get("email"), show1 = "", show2 = "hidden" )    
    return render_template("Horoscope.html",email = session.get("email"), show1 = "hidden", show2 = "" )

@app.route("/horoscope/<sign>")
def detailed_horoscope(sign):
      
    nums = {"aries":1,"taurus":2,"gemini":3,"cancer":4,"leo":5,"virgo":6,"libra":7,"scorpio":8,"sagittarius":9,"capricorn":10,"aquarius":11,"pisces":12}   
    try:
        today = datetime.date.today()
        date = today.strftime("%d/%m/%Y") 
        PARAMS = {
        "zodiac": nums[sign],
        "show_same": True,
        "type":"big",
        "date": date,
        "api_key": '1bf48bd4-618d-51ce-a633-6c1bf042c0f7',
        
        }
        params2={
        "zodiac": nums[sign],
        "show_same": True,
        "type":"big",
        "week":'thisweek',
        "api_key": '1bf48bd4-618d-51ce-a633-6c1bf042c0f7',
        
        }
        r1 = requests.get(url = astro_url, params = PARAMS) 
        data1 = r1.json() 
        r2 = requests.get(url = 'https://api.vedicastroapi.com/json/prediction/weeklysun', params = params2) 
        data2 = r2.json() 

    except:
        return render_template("error404.html")
    if not session.get("email"):    
        return render_template("DetailedHoroscope.html",email = session.get("email"), show1 = "", show2 = "hidden", horo_data = data1, horo_data_weekly = data2 )    
    return render_template("DetailedHoroscope.html",email = session.get("email"), show1 = "hidden", show2 = "", horo_data = data1, horo_data_weekly = data2 )

@app.route("/predictions")
def predictions():
    if not session.get("email"):    
        return render_template("Predictions.html",email = session.get("email"), show1 = "", show2 = "hidden" )    
    return render_template("Predictions.html",email = session.get("email"), show1 = "hidden", show2 = "" )

@app.route("/askQuestion")
def ask():    
    key = db.collection("Astrologers").get()
    astrologers = []
    for astrologer in key:
        if(astrologer.to_dict()["Status"]):
            astrologers.append([astrologer.to_dict()["Name"],astrologer.to_dict()["astro_id"]])       
    if not session.get("email"):    
        return render_template("Ask_Questions.html",email = session.get("email"), show1 = "", show2 = "hidden", astrologers = astrologers, balance = -1) 
    balance = db.collection("Users").document("emails").collection(session.get("email")).document("Data").get() 
    print(balance.to_dict()["Wallet"])  
    return render_template("Ask_Questions.html",email = session.get("email"), show1 = "hidden", show2 = "", astrologers = astrologers, balance = balance.to_dict()["Wallet"])

@app.route("/aboutDevelopers")
def aboutDev():
    if not session.get("email"):    
        return render_template("aboutDevs.html",email = session.get("email"), show1 = "", show2 = "hidden" )    
    return render_template("aboutDevs.html",email = session.get("email"), show1 = "hidden", show2 = "" )

@app.route("/wallet")
def wallet():
    if not session.get("email"):    
        return render_template("wallet.html",email = session.get("email"), show1 = "", show2 = "hidden" )  
    balance_key = db.collection("Users").document("emails").collection(session.get("email")).document("Data").get()  
    try:
        return render_template("wallet.html",email = session.get("email"), show1 = "hidden", show2 = "" , balance = balance_key.to_dict()["Wallet"])
    except Exception as e:
        db.collection("Users").document("emails").collection(session.get("email")).document("Data").set({"Wallet":0}, merge=True)
        return render_template("wallet.html",email = session.get("email"), show1 = "hidden", show2 = "" , balance = 0)


@app.route("/addMoney")
def addMoney():
    if not session.get("email"):    
        return render_template("addMoney.html",email = session.get("email"), show1 = "", show2 = "hidden" )    
    balance_key = db.collection("Users").document("emails").collection(session.get("email")).document("Data").get()  
    try:
        return render_template("addMoney.html",email = session.get("email"), show1 = "hidden", show2 = "" , balance = balance_key.to_dict()["Wallet"])
    except Exception as e:
        db.collection("Users").document("emails").collection(session.get("email")).document("Data").set({"Wallet":0}, merge=True)
        return render_template("addMoney.html",email = session.get("email"), show1 = "hidden", show2 = "" , balance = 0)
    
@app.route("/notifications")
def notifications():
    if not session.get("email"):    
        return render_template("notification.html",email = session.get("email"), show1 = "", show2 = "hidden" )    
    return render_template("notification.html",email = session.get("email"), show1 = "hidden", show2 = "" )

@app.route("/orders")
def orders():
    if not session.get("email"):    
        return render_template("orders.html",email = session.get("email"), show1 = "", show2 = "hidden" )  
    
    key = db.collection("Users").document("Orders").collection(session.get("email")).get()

    orders = []

    for order in key:
        new_order = {"oid":order.to_dict()["Order ID"],"name":order.to_dict()["Name"],"dob":order.to_dict()["DOB"],"payid":order.to_dict()["Pay_id"],"link":order.to_dict()["url"]}
        orders.append(new_order)
    print(orders)
    return render_template("orders.html",email = session.get("email"), show1 = "hidden", show2 = "" ,orders = orders)

@app.route("/support")
def support():
    return render_template("CustomerSupport.html")

#backend

@app.route("/createUser", methods = ["POST"])
def createUser():
    email = request.form["email"]
    password = request.form["password"]
    phone = request.form["phone"]
    name = request.form["name"]
    try:
        auth.create_user_with_email_and_password(email, password)       
        session["email"] = email 
        db.collection("Users").document("emails").collection(email).document("Data").set({"Email":email,"Wallet":0,"Name":name,"Phone":phone,"fcm_token":""})
        return redirect('/home') 
    except Exception as e:
        json_object = json.loads(str(e).replace("[Errno 400 Client Error: Bad Request for url: https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyAHs2rZusPbs1BjngrenWT3NpCqEztRru0] ",""))
        return render_template("SignUp.html", error = json_object["error"]["message"].lower().capitalize()+", try login!")  
    

@app.route("/loginUser", methods = ["POST"])
def loginUser():
    email = request.form["email"]
    password = request.form["password"] 
    try:
        auth.sign_in_with_email_and_password(email,password)  
        session["email"] = email  
        return redirect('/home')
    except Exception as e:   
        try: 
            auth.send_password_reset_email(email);  
        except:
            json_object = json.loads(str(e).replace("[Errno 400 Client Error: Bad Request for url: https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyAHs2rZusPbs1BjngrenWT3NpCqEztRru0] ",""))
            return render_template("login.html", error = json_object["error"]["message"].lower().capitalize()+"!")
        json_object = json.loads(str(e).replace("[Errno 400 Client Error: Bad Request for url: https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyAHs2rZusPbs1BjngrenWT3NpCqEztRru0] ",""))
        return render_template("login.html", error = json_object["error"]["message"].lower().capitalize()+", reset link sent!")  

@app.route("/registerQuestion", methods = ["POST"])
def registerQuestion():
    name = request.form["name"]
    dob = request.form["dob"]
    lat = request.form["lat"]
    lon = request.form["lon"]
    time = request.form["time"]
    question = request.form["question"]
    astro_id = request.form["astrologer"]

    doc_id = str(datetime.datetime.now())  
    oid = random.randint(1000000, 9999999)

    order = {"Birthtime":time,"DOB":dob,"Email":session.get("email"), "Name" :name,"Lat":lat,"Lon":lon,"OID":int(oid),"Pay_id":"12121212","Question":question,"Status":False,"Type":"Question","astro_id":int(astro_id),"reviewed":"show"}
    uorder ={"Birthtime":time,"DOB":dob,"Name" :name,"Lat":lat,"Lon":lon,"Order ID":int(oid),"Pay_id":"12121212","Type":"Question","Question":question,"url":"/gettingReady"}
    db.collection("Orders").document(str(doc_id)).set(order) 
    db.collection("Users").document("Orders").collection(session.get("email")).document(str(oid)).set(uorder,merge=True)
    docs = db.collection("Astrologers").where("astro_id","==",int(astro_id)).stream()
    for i in docs:
           doc= i.id  
    db.collection("Astrologers").document(str(doc)).set({"CAPQ":Increment(1)}, merge=True)
    astro_mail_key = db.collection("Astrologers").document(str(doc)).get()
    astro_mail = astro_mail_key.to_dict()["email"]
    db.collection("Users").document("emails").collection(session.get("email")).document("Data").set({"Wallet":Increment(-49)},merge=True)
    send_email("info@stackxsolutions.in","StackX@123",session.get("email"),"Order Registered with OID: {0}".format(int(oid)),"We have recieved your order with OID: {0}.\nYou can download our app from playstore to get updated about your order and to avail more services.\nThankyou for using our services.\nTeam Astrodrishti(StackX)".format(int(oid)))   
    send_email("info@stackxsolutions.in","StackX@123",astro_mail,"New Question for you Registered with OID: {0}".format(int(oid)),"You can now login to your admin pannel and aswer this question, to get a good rating and move up in the list of all the astrologers.\nAll the very best.\nThankyou for using our services.\nTeam Astrodrishti(StackX)".format(int(oid)))   
    return render_template("orderPlaced.html", oid = oid) 

@app.route("/gettingReady")
def gettingReady():
    return render_template("gettingReady.html")

@app.route('/payment/<amount>')
def pay_now(amount):
    data = { "amount": int(amount)*100, "currency": "INR" }
    payment = rz_client.order.create(data=data)     
    return render_template("pay.html", id = payment["id"], email=session.get("email"), amount = amount);  

@app.route("/handlePayment", methods = ["POST"]) 
def handle_payment():    
    json = request.json
    try:
        db.collection("Users").document("emails").collection(json['email']).document("Data").set({'Wallet':Increment(int(json['amount']))}, merge=True)
    except Exception as e:
        db.collection("Users").document("emails").collection(json['email']).document("Data").set({'Wallet':int(json['amount'])}, merge=True)
    return {'link':'/wallet'}



if __name__ == "__main__":
    app.run(debug=True)