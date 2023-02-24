#import from 3rd party(flask)
from flask import render_template,redirect,flash,session,request,url_for
import os,random,string,json,requests

from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.sql import text
#to #initialize the app to load __iniit__
#import from local file
from membapp import app,db
from membapp.models import Party,User,Topics,ContactUs,Comments,State,Lga,Donation,Payment
from membapp.forms import ContactForm



def generate_name():
    filename = random.sample(string.ascii_lowercase,10)#will return a list
    return ''.join(filename)#will join every member of the list above together

#route creation

@app.route("/")
def home():
    contact = ContactForm()
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1.0/listall")
        if response:
            rspjson =json.loads(response.text)
        else:
            rspjson = dict()
    except:
        rspjson = dict()
    return render_template('user/home.html',contact=contact,rspjson=rspjson)

@app.route('/signup/')
def user_signup():
    #fetch all the party from party table so that wwe can display in a select drop down
    p = db.session.query(Party).all()
    return render_template("user/signup.html",party=p)

@app.route("/user/login/", methods=["POST","GET"])
def user_login():
    if request.method == "GET":
        return render_template("user/login.html")
    else:
            #retrieve the form data
        email = request.form.get('email')
        pwd = request.form.get('pwd')
             #run a query to know if the username exists on the database
        deets = User.query.filter(User.user_email == email).first()
        if deets != None:
            pwd_indb = deets.user_pwd
                    #compare the password coming from the form with the hasded password in the db
            chk = check_password_hash(pwd_indb,pwd)
                    #if the password checks above is right,we should log them in
            if chk:
                    #by keeping their details(user_id) in session['user']
                id = deets.user_id
                session['user'] = id
                    #and redirect tthem to the dashboard
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid Credentials")# for incorrect password
                return redirect(url_for('user_login'))
        else:
            flash("Invalid Credentials")#for if the username is incorrect
            return redirect(url_for('user_login'))


@app.route("/user/register",methods=["POST","GET"])
def register():
    #To do: retrieve all the form data and insert into user table
    data = request.form
    email = data.get('email')
    password = data.get('pwd')
    party = data.get('partyid')
    '''Convert the plain password to hashed value and insert into db'''
    hashed_pwd = generate_password_hash(password)
    #INSERT INTO THE PARTY TABLE USING ORM METHOD
    if email != "" or password != "" or party !="":
        #create an instance of party(ensure that party is imported from models)obj = classname(column1=value,column2=value)
        query = User(user_email=email,user_pwd=hashed_pwd,user_partyid=party,user_fullname="Peter obi")
            #step2: add to session
        db.session.add(query)
            #step3: commit the session
        db.session.commit()
            #set a session session['user'] = user_id
            #to get the id oof the record that has just been inserted
        userid = query.user_id
        session['user'] = userid#to keep th user_id
    #redirect them to profile/dashboard
        return redirect (url_for('dashboard'))
    else:
        flash("You must complete all the fields to ignup")
        return redirect(url_for('user_signup'))
    
@app.route("/check_username",methods=['POST','GET'])
def check_username():
    if request.method == 'GET':
        return "please complete the field"
    else:
        email = request.form.get('email')
        query = User.query.filter(User.user_email == email).first()
        if query == None:
            sendback = {'status':1,'feedback':"Email is avaliable,please register"}
            return json.dumps(sendback)
        else:
            sendback = {'stattus':0,'feedback':"You have registered already. click <a href='/login'>here</a>to login"}
            return json.dumps(sendback)

@app.route("/dashboard/")
def dashboard():
    #protect this route so that only logged in user can get here
    if session.get('user') !=None:
        #retrieve the details of the logged in user
        id = session['user']
        deets= db.session.query(User).get(id)
        return render_template('user/dashboard.html',deets=deets)
    else:
        return redirect(url_for('user_login'))


@app.route('/logout')
def user_logout():
    if session.get('user') != None:
        session.pop('user',None)
    return render_template('user/home.html')

@app.route('/profile',methods=['POST','GET'])
def profile():
     id = session.get('user')
         #prevent access to those who are not logged in
     if id == None:
         return redirect('user_login')
     else:
         if request.method == "GET":
                #write an ORM query to fetch the details of the loggedin user
            state_deets = State.query.all()   
            deets = db.session.query(User).get(id)
            allparties = Party.query.all()
                #deets = db.session.query(User).filter(User.user_id == id).first()
            return render_template('user/profile.html',deets=deets,state_deets=state_deets,allparties=allparties)
         else:
             #retrieve from data (fullname and phone), save them in a variable
             data = request.form
             fullname = data.get('fullname')
             phone = data.get('phone')
             #updatd query ising ORM methods
             userobj = db.session.query(User).get(id)
             userobj.user_fullname = fullname
             userobj.user_phone = phone
             db.session.commit()
             flash("profile updated")
             return redirect("/profile")

@app.route('/profile/picture',methods=['POST','GET'])
def profile_picture():
         #prevent access to those who are not logged in
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == "GET":
            return render_template('user/profile_picture.html')
        else:
            #retrieve the file
            file = request.files['pix']
            #toknow thw filename
            filename = file.filename
            filetype = file.mimetype
            allowed = ['.png','.jpg','.jpeg']
            if filename !="":
                name,ext = os.path.splitext(filename)#import os
                if ext.lower() in allowed:
                    newname = generate_name()+ ext
                    file.save("membapp/static/uploads/"+newname)
                    #update the usertable using ORM by keeping the name of the uploaded file for this user,
                    #fetching the details from the session then update it
                    id = session['user']
                    user = db.session.query(User).get(id)
                    user.user_pix = newname
                    db.session.commit()
                    flash("file uploaded"+filetype,category="success")
                    return redirect('/profile/picture')
                else:
                    flash("file extension not allowed",category="error")
                    return redirect('/profile/picture')
            else:
                flash("please choose a file",category="error")
                return redirect('/profile/picture')  

@app.route('/blog/',methods=['POST','GET'])
def blog():
    #fetch all the post from datadase
    articles = db.session.query(Topics).filter(Topics.topic_status=='1').all()
    return render_template('user/blog.html',articles=articles)

@app.route('/newtopic/',methods=['POST','GET'])
def newtopic():
    #check if logged in
    if session.get('user') != None:
        if request.method == 'GET':
            return render_template('user/newtopic.html')
        else:
            #retrieve form data and validate
            data = request.form
            post = data.get('content')
            if len(post) != 0:
                query = Topics(topic_title = post,topic_userid=session['user'])
                db.session.add(query)
                db.session.commit()
                if query.topic_id:
                    flash('post successfully submitted for approval',category="success")
                else:
                    flash('oops,something went wrong.Please try again',category="error")
                
            else:
                flash("You cannot submit an empty post",category="error")
                return redirect('/newtopic/')
            
            return redirect (url_for('blog'))

    else:
        return redirect(url_for('user_login'))
    

@app.route('/blog/<id>')
def blog_details(id):
    #fetch the topic with id id
    #blog_deets = db.session.query(Topics).filter(Topics.topic_id==id).first()
    #blog_deets = Topics.query.filter(Topics.topic_id == '1').first()
    #blog_deets = db.session.query.get(id)
    blog_deets = Topics.query.get_or_404(id)
    return render_template('user/blog_details.html',blog_deets=blog_deets)


@app.route('/demo/')
def demo():
    #method 1
    #query = db.session.query(Party).filter(Party.party_id > 1,Party.party_id <=6 ).all()
    #method 2
    #data = Party.query.filter(Party.party_id>1, Party.party_id <= 6).all()
    #query = User.query.filter(User.user_email == email, User.user_pwd == pwd).all()
    #method 1 of joining tables
    #data = db.session.query(User,Party).join(User).all()
    data = db.session.query(User.user_fullname,Party.party_name,Party.party_contact,Party.party_shortcode).join(Party).all()
    query = User.query.join(Party).filter(~Party.party_shortcode.in_(['Lp','APC'])).add_columns(Party).all()
    rsp = db.session.query(Party).all()
    result = db.session.query(User).get(1)
    return render_template("user/test.html",data=data,query=query,rsp=rsp,result=result)


#contact us
@app.route("/contact", methods=['POST','GET'])
def contact_us():
    contact = ContactForm()
    if request.method == 'GET':
        return render_template('user/contact_us.html',contact=contact)
    else:
        if contact.validate_on_submit():#True
            #retrieve form data and insert into db
            email = request.form.get('email')
            #or
            msg = contact.messages.data
            upload = contact.screenshot.data#request.files.get('screenshot)
            #insert into table message on the data base
            msg_deets = ContactUs(msg_email=email,msg_content=msg)
            db.session.add(msg_deets)
            db.session.commit()
            flash("thank you for contacting us")
            return redirect(url_for('contact_us'))
        else:#false
            return render_template('user/contact_us.html',contact=contact)
        

@app.route('/sendcomment')
def sendcomment():
    if session.get('user'):
        #retrieve the data coming from  the request
        usermessage = request.args.get('message')
        user = request.args.get('userid')
        topic = request.args.get('topicid')
        query = Comments(comment_text=usermessage,comment_userid=user,comment_topicid=topic)
        db.session.add(query)
        db.session.commit()
        commenter = query.commentby.user_fullname
        dateposted = query.comment_date
        sendback = f"<i>{usermessage} <br><br>by {commenter} on {dateposted}</i>"
        return sendback
    else:
        return "comment was not posted,you need to be loggd in"


@app.route('/ajaxcontact', methods=['POST','GET'])
def contact_ajax():
    form= ContactForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        msg = request.form.get('msg')
        #insert into  databade and send the feedback to AJAX/javascript
        deets = ContactUs(msg_email=email,msg_content=msg)
        return f"{email} and {msg}"
    else:
        return "you need to complete the form"
    
@app.route('/load_lga/<stateid>')
def load_lga(stateid):
    #select all the lga that are attach to the sateid
    lags = Lga.query.filter(Lga.lga_stateid==stateid).all()
    data2send = "<select class='form-control border-success'>"
    for s in lags:
        data2send = data2send+"<option>" +s.lga_name +"</option>"
    data2send = data2send + "</select>"
    return data2send

@app.route('/donate', methods=['POST','GET'])
def donate():
    if session.get('user') !=None:
        deets = User.query.get(session.get('user'))
    else:
        deets = None
    if request.method == 'GET':
        return render_template('user/donation_form.html',deets=deets)
    else:
        #retrieve the form data and insert into database
        #ref = int(random.random() * 100000000)
        amount = request.form.get('amount')
        fullname = request.form.get('fullname')
        data = Donation(don_donor=fullname,don_amt=amount,don_userid=session.get('user'))
        db.session.add(data)
        db.session.commit()
        session['donation_id'] = data.don_id
         #generate the ref no and keep in session
        refno = int(random.random() * 100000000)
        session['reference'] = refno
        return redirect('/confirm')
    
@app.route('/confirm',methods=['POST','GET'])
def confirm():
    if session.get('donation_id')!= None:
        if request.method =='GET':  
            donor = db.session.query(Donation).get(session['donation_id'])
            return render_template('user/confirm.html',donor=donor,refno=session['reference'])
        else:
            donor = db.session.query(Donation).get(session['donation_id'])
            p = Payment(pay_donid=session.get('donation_id'),pay_ref=session['reference'],pay_amount_deducted=donor.don_amt)
            db.session.add(p);db.session.commit()
            
            don = Donation.query.get(session['donation_id'])#details of the donation
            donor_name = don.don_donor
            amount = don.don_amt * 100#as to be in kobo 
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_fd0bceec247a01665ecdd9ad904ec899d069d99d"}
            data={"amount":amount,"reference":session['reference'],"email":donor_name}
            
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson= json.loads(response.text)
            if rspjson['status'] == True:
                url = rspjson['data']['authorization_url']
                return redirect(url)
            else:
                return redirect('/confirm')
    else:
        return redirect('/donate')
    

@app.route('/paystack')
def paystack():
    refid = session.get('reference')
    if refid ==None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type": "application/json","Authorization":"Bearer sk_test_fd0bceec247a01665ecdd9ad904ec899d069d99d"}
        verifyurl= "https://api.paystack.co/transaction/verify/"+str(refid)
        response= requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status']== True:
            #payment was successful
            return rspjson
        else:
            #payment was not successful
            return "payment was not successful"
