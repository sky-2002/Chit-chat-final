import smtplib
from flask import Flask, render_template, request, redirect
import json
from numpy import NaN, nan
import pandas as pd
from pandas.core.algorithms import mode
import csv_classes
from flask.helpers import flash, url_for
from werkzeug.utils import secure_filename
import os
import time
from PIL import Image

def to_str(number):
    return str(number)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "files/"
all_users = pd.read_csv("csv_files/All_users.csv")

#------------------------Display all main pages-----------
@app.route("/")
def home():
    # displays home page
    return render_template("home.html")

@app.route("/login",methods=["GET","POST"])
def login():
    # displays login page
    return render_template("test_login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    # displays signup page
    return render_template("test_signup.html")
#---------------------------------------------------------

#--------------------Signup---------------------------------------

@app.route("/signup_process",methods=["POST"])
def signup_process():
    # this function signs the user up
    
    all_users = pd.read_csv("csv_files/All_users.csv")

    # Json processing
    jsonStr = request.get_json()
    jsonObj = json.loads(jsonStr)
    response = ""

    # Creating variables for username and password
    username = jsonObj['Username']
    password = jsonObj['Password']
    email = jsonObj['Email']
    all_names = [a for a in all_users.Name]
    all_emails = [b for b in all_users.Email]

     # check for blank username and password
    if username.strip()=='':
        response+=f"Please enter a valid username<br>"
        return response
    
    if email.strip()=='':
        response+=f"Please enter a valid email<br>"
        return response
    
    if ("@" not in email):
        response+=f"Please enter a valid email<br>"
        return response

    # check for blank password
    if password.strip()=='':
        response+=f"Please enter a valid password<br>"
        return response

    # This checks if the username exists in all users list, i.e. if user is signed up or not
    if (username not in all_names) and (email not in all_emails):

        # create user and add in All_users.csv file
        user = csv_classes.user(username,password,email)
        my_users=[user]
        my_list = pd.DataFrame([[p.name,p.password,p.email,p.logged_in,p.signed_up] for p in my_users],columns=["Name","Password","Email","Logged_in","Signed_up"])
        all_users = all_users.append(my_list,ignore_index=True)
        
        # converting password to string
        all_users = all_users.astype({'Password':str})
        all_users.to_csv("csv_files/All_users.csv",index=False)

        # signep up successfully, give link to login
        response+=f'''<h5>Signed up as {username}, Proceed to <a href="/login">Login</a></h5>'''
        return response

    #username is new but mail id already used
    elif (username not in all_names) and (email in all_emails):
        response+='''<h5>Account with this email id already exists. <a href="/forgot_password">Forgot Password?</a></h5>'''
        return response

    #username and mail id both already used
    elif (username in all_names) and (email in all_emails):
        response+='''<h5>Account with this email id already exists. <a href="/forgot_password">Forgot Password?</a></h5>'''
        return response
    
    
    # username is there but signing up with a new mail id , now checking password
    elif (username in all_names) and (email not in all_emails):
        user_row_index = all_users.loc[all_users.Name==username].index[0] 
        user_pass = all_users.iloc[user_row_index,1]

        # this will check if the username is getting repeated
        
        if user_pass!=password:
            response+="<h5>Please enter a different username, this one already exists..</h5>"
            return response
        else:
            # if username is already present, give login link
            response+='''<h5>Already Signed up , Proceed to <a href="/login">Login</a></h5>'''
            return response

#--------------------------------------------------------------------------------------------------

#-------------------------Login---------------------------------------------------------

@app.route("/login_process",methods=["POST"])
def login_process():

    all_users = pd.read_csv("csv_files/All_users.csv")
    # Json processing
    response=""
    jsonStr = request.get_json()
    jsonObj = json.loads(jsonStr)

    # Creating variables for username and password
    username = jsonObj['Username']
    password = jsonObj['Password']
    all_names = [a for a in all_users.Name]
    
    # checks is user is signed up
    if username not in all_names:
        response += f"<h5>Please sign up first , <a href='/signup'>click here</a> to sign up</h5>"
        return response

    else:
        # if username is present in all users, check password
        user_row_index = all_users.loc[all_users.Name==username].index[0]
        user_pass = all_users.iloc[user_row_index,1]

        # if password is correct, set logged_in to True, we will set this to False after logout
        if user_pass==password:
            all_users.loc[user_row_index,'Logged_in'] = True
            all_users.to_csv('csv_files/All_users.csv',index=False)
        else:
            response+=f"<h5>Password incorrect, try again..</h5>"
            return response
    
    logged_in = True
    # give link to dashboard, along with username, username will help us locate its row in dataframe
    response+=f'''<h5>Hello {username} ,<a href="{url_for('dashboard',username=username,logged_in=logged_in)}">Click here to see Dashboard</a></h5>'''
    return response

#-----------------------------------------------------------------------------------------------

#--------------------------Forgot Password----------------------------------------------------------
@app.route('/forgot_password')
def forgot_pass():
    return render_template("forgot_password.html")


def send_mail(email, password,user):
    my_email = "noreplychitchat54@gmail.com"
    my_pass = "Chitchat54"
    subject="Forgot Password?"
    
    
    text=f"Hello {user},\nThank you for using ChitChat.\n\nYour username: {user}\nYour account password is: {password}\n\nIf you did not not intiate this process we recommend you to change your password.\nRegards,\nTeam ChitChat"
    
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(user=my_email, password=my_pass)
        connection.sendmail(from_addr=my_email,
                            to_addrs=email,
                            msg = 'Subject: {}\n\n{}'.format(subject, text))

@app.route("/submitJSON1_", methods=["POST"])
def processJSON1_():
    response=""
    jsonStr = request.get_json()
    jsonObj = json.loads(jsonStr)
    email = jsonObj['temp1']

    file = pd.read_csv('csv_files/All_users.csv')
    for index, row in file.iterrows():
        if row["Email"] == email:
            
            send_mail(row['Email'], row['Password'],row['Name'])
            response+='''<h5>Your password has been sent to your email address.<br><a href="/login">Login here</a></h5>'''
            return response
    response+= '''<h5>There is no account associated with this email.<br><a href="/signup">Register here</a></h5>'''
    return response




#-----------------------------------------------------------------------------------------------

#--------------------------Dashboard----------------------------------------------------------
 
@app.route("/dashboard/<username>/<logged_in>",methods=["POST","GET"])
def dashboard(username,logged_in):

    # we set this to none, so as to reset it after checking if user has logged in
    logged_in=None

    all_users=pd.read_csv("csv_files/All_users.csv")
    user_row_index = all_users.loc[all_users.Name==username].index[0]
    user_logged_in = all_users.iloc[user_row_index,3]

    # this checks in the dataframe , if the user is logged in or not
    if user_logged_in==True:
        logged_in=True
    # if user is logged in , display dashboard    
    if logged_in:
        return render_template('dash.html',username=username)
    # else show error page
    else:
        return render_template("test_dash_error.html")
#----------------------------------------------------------------------------------

#---------------------------------View and clear inbox------------------------------
@app.route("/view_inbox/<username>",methods=["POST","GET"])
def view_inbox(username):
    response = csv_classes.view_inbox_or_sent(username,'csv_files/inbox.csv','From')
    return response

@app.route('/clear_inbox/<username>',methods=["GET","POST"])
def clear_inbox(username):
    response=csv_classes.clear_inbox_or_sent(username,'csv_files/inbox.csv','To')
    return response
#-----------------------------------------------------------------------------------

#-------------------------------View and clear sent---------------------------------
@app.route("/view_sent/<username>",methods=["POST","GET"])                         
def view_sent(username):
    response = csv_classes.view_inbox_or_sent(username,'csv_files/sent.csv','To')
    return response

@app.route('/clear_sent/<username>',methods=["GET","POST"])
def clear_sent(username):
    response=csv_classes.clear_inbox_or_sent(username,'csv_files/sent.csv','From')
    return response
#-----------------------------------------------------------------------------------

#---------------------------Logout and delete account-------------------------------
@app.route("/logout_process/<username>",methods=["POST","GET"])
def logout_process(username):

    username = username
    all_users = pd.read_csv("csv_files/All_users.csv")

    # fetches the index of the row where Name = username
    user_row_index = all_users.loc[all_users.Name==username].index[0]

    # .loc selects row with user_row_index and column Logged_in and sets it to false
    all_users.loc[user_row_index,'Logged_in'] = False
    all_users.to_csv("csv_files/All_users.csv",index=False)

    return redirect(url_for('home'))

@app.route('/delete_account/<username>',methods=["GET","POST"])
def delete_account(username):
    all_users = pd.read_csv("csv_files/All_users.csv")
    user_row_index = all_users.loc[all_users.Name==username].index[0]
    
    all_users.drop(user_row_index,axis=0,inplace=True)
    all_users.to_csv("csv_files/All_users.csv",index=False)

    return redirect(url_for("home"))


#---------------------------------------------------------------------------------------------------

#----------------------------Message with attachments-----------------------------------------------

@app.route('/image_form/<username>',methods=["GET","POST"])
def image_form(username):
    return render_template('image_form.html',username=username)

@app.route('/image_process/<username>',methods=["POST","GET"])
def image_process(username):
    response=""
    
    all_users = pd.read_csv("csv_files/All_users.csv")
    all_names = [nm for nm in all_users.Name]

    # getting form data
    to = request.form['to']
    subject = request.form['subject']
    message = request.form['message']
    time_sent = time.ctime()

    
    if subject.strip()=='':
        subject="No Subject"

    if message.strip()=='':
        message="  "
    
    # this will check for wrong usernames entered
    if to not in all_names:
        return render_template("form_user_error.html",username=username)

    # loading files
    if request.method == 'POST':
        f = request.files['file']
        if f:
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            file_loc = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        else:
            file_loc = None
            
    
    # adding data to all message files
    for f in ["csv_files/Messages.csv","csv_files/inbox.csv","csv_files/sent.csv"]:
        csv_classes.add_to_messages(subject,to,username,message,time_sent,f,file_loc)
    return render_template("form_user_success.html",username=username)


#---------------------------------------------------------------------------------------------------

#----------------------------Statistics-----------------------------------------------
@app.route('/stats/<username>',methods=["POST","GET"])

def stats1(username):
    
    all_messages = pd.read_csv('csv_files/Messages.csv')
    my_received = all_messages[all_messages.To==username]
    my_sent = all_messages[all_messages.From==username]
    received = len(my_received)
    sent = len(my_sent)

    all_users = pd.read_csv('csv_files/All_users.csv')
    active_users = all_users[all_users.Logged_in==True]
    active = len(active_users)

    my_friends = [nm for nm in my_received.From if nm!=username]
    
    are_online = {}
    for nm in my_friends:
        friend_row = all_users[all_users.Name==nm].index[0]
        friend_values = all_users.iloc[friend_row,3]
        
        are_online[nm]=friend_values

    return render_template('stats.html',received=received,sent=sent,active=active,friends = are_online)
    
#------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
