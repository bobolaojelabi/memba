from flask import render_template,redirect,flash,session,request,url_for
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash,check_password_hash
from membapp import app,db
from membapp.models import Party,Topics

@app.route('/admin/',methods=['POST','GET'])
def admin_home():
    if request.method == "GET":
        return render_template("admin/adminreg.html")
    else:
        #to get the content submitted by importting request
        data = request.form
        user = data.get('username')
        password = data.get('pwd')
        '''Convert the plain password to hashed value and insert into db'''
        hashed_pwd = generate_password_hash(password)
        if user != "" or password != "":
            query = f"INSERT INTO admin Set admin_username='{user}',admin_pwd='{hashed_pwd}'"
            db.session.execute(text(query))
            db.session.commit()
            flash("Regitration successful. Login here",category="success")
            return redirect("/admin/")
        else:
            flash("please complete all the fields",category="error")
            return redirect("/admin/")
        


@app.route("/admin/login/", methods=['POST','GET'])
def login():
    if request.method == "GET":
        return render_template("admin/adminlogin.html")
    else:
        #retrieving from the database
        data = request.form
        user = data.get("username")
        password = data.get("pwd")
        #write your SELECT query
        query = f"SELECT * FROM admin WHERE admin_username = '{user}'"
        result = db.session.execute(text(query))
        total = result.fetchone()#fetchone() or fetchmany(1)
        if total:#the username exist
            pwd_indb = total[2]#hashed pwd from the database
            #compare this hasded with the pwd coming from the form
            chk = check_password_hash(pwd_indb,password)#returns True or Flase

            if chk == True: #login is succesful, save his details in a session
                session['loggedin']=user
                return redirect("/admin/dashboard/")
            else:
                flash("Invalid Credentials")
                return redirect(url_for("login"))
        else:
            flash("Invalid Credentials")
            return redirect(url_for("login"))



# @app.route("/admin/login/", methods=['POST','GET'])
# def login():
#     if request.method == "GET":
#         return render_template("admin/adminlogin.html")
#     else:
#         #retrieving from the database
#         data = request.form
#         user = data.get("username")
#         password = data.get("pwd")
#         #write your SELECT query
#         query = f"SELECT * FROM admin WHERE admin_username = '{user}' and admin_pwd = '{password}'"
#         result = db.session.execute(text(query))
#         total = result.fetchall()#fetchone() or fetchmany(1)
#         if total:#the login deatils are correct
#             #log him in by saving his details in session
#             session['loggedin']=user
#             return redirect("/admin/dashboard/")
#         else:
#             flash("Invalid Credentials")
#             return redirect("admin/login")
        
@app.route("/admin/dashboard/")
def admin_dashboard():
    if session.get("loggedin") != None:
        return render_template("admin/index.html")
    else:
        return redirect("/admin/login/")

@app.route("/admin/logout/")
def admin_logout():
    if session.get("loggedin") != None:
        session.pop("loggedin",None)
    return redirect("/admin/login/")


@app.route("/admin/addparty",methods=["POST","GET"])
def add_party():
    if session.get("loggedin") == None:
        return redirect("/admin/login/")
    else:
        if request.method == "GET":
            return render_template("admin/addparty.html")
        else:
            #retrieve the form data
            partyname = request.form.get('partyname')
            code = request.form.get('partycode')
            contact = request.form.get('partycontact')
            #INSERT INTO THE PARTY TABLE USING ORM METHOD
            #step1: create an instance of party(ensure that party is imported from models)obj = classname(column1=value,column2=value)
            p = Party(party_name=partyname,party_shortcode=code,party_contact=contact)
            #step2: add to session
            db.session.add(p)
            #step3: commit the session
            db.session.commit()
            flash("party added")
            return redirect(url_for('parties'))
    
@app.route('/admin/parties/')
def parties():
    if session.get("loggedin") != None:
        #We will fetch db using ORM method
        data = db.session.query(Party).order_by(Party.party_name.desc()).limit(3).all()
        return render_template('admin/allparties.html',data=data)
    else:
        return redirect('/admin/login/')
    

@app.route('/admin/topics')
def all_topics():
    if session.get('loggedin') == None:
        return redirect('/admin/login/')
    else:
        query = db.session.query(Topics).all()
        #query = Topics.query.all()
        return render_template('admin/alltopics.html',query=query)
    
@app.route('/admin/topic/delete/<id>')
def delete_post(id):
    #retrieve the topic as an object
    topicobj = Topics.query.get_or_404(id)
    db.session.delete(topicobj)
    db.session.commit()
    flash("Successfully deleted")
    return redirect(url_for('all_topics'))

@app.route('/admin/topic/edit/<id>')
def edit_topic(id):
    if session.get('loggedin') != None:
        #fetch the topic of interest
        topic_deets =Topics.query.get(id)
        return render_template('admin/edit_topic.html',topic_deets=topic_deets)
    else:
        return redirect(url_for())
    
@app.route('/admin/update_topic',methods=['POST','GET'])
def update_topic():
    if session.get('loggedin') != None:
        newstatus = request.form.get('status')
        topicid = request.form.get('topicid')
        userobj = db.session.query(Topics).get(topicid)
        userobj.topic_status = newstatus
        db.session.commit()
        flash('topic successfully updated')
        return redirect('/admin/topics')
    else:
        return redirect('/admin/login')