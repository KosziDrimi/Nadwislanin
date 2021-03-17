from flask import Flask, render_template, url_for, flash, redirect
from flask_login import login_user, login_required, logout_user, UserMixin, LoginManager
from forms import ReservationForm, LoginForm, ConfirmationForm, EmailForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
import datetime


app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")


mail = Mail(app)

db = SQLAlchemy(app)
Migrate(app,db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        

class Reservation(db.Model):

    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    duration = db.Column(db.String)
    numbers = db.Column(db.String)
    feedback = db.Column(db.Text)
    new = db.Column(db.Boolean)
    confirmation = db.Column(db.Text)
    email_text = db.Column(db.Text)
    
    def __init__(self, name, email, date, time, duration, numbers, feedback, new=True, confirmation=None, email_text=None):
      
        self.name = name
        self.email = email
        self.date = date
        self.time = time
        self.duration = duration
        self.numbers = numbers
        self.feedback = feedback
        self.new = new
        self.confirmation = confirmation 
        self.email_text = email_text
        
    def __repr__(self):
        return f"""Reservation details: {self.id}
             {self.name} {self.email}
             {self.date} {self.time}
             {self.duration} {self.numbers}
             {self.feedback} {self.new}"""
        

@app.route('/')
def index():
    return render_template('index.html')
                           
    
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    
    form = ReservationForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        date = form.date.data
        time = form.time.data
        duration = form.duration.data
        numbers = form.numbers.data
        feedback = form.feedback.data
        
        new_res = Reservation(name, email, date, time, duration, numbers, feedback)
        db.session.add(new_res)
        db.session.commit()
        
        return render_template('thankyou.html', new_res=new_res)

    return render_template('reservation.html', form=form)


@app.route('/admin')
@login_required
def res_list():
    result = Reservation.query.filter_by(new=True).all()
    return render_template('new_list.html', result=result)


@app.route('/<int:res_id>', methods=['GET', 'POST'])
@login_required
def show(res_id):
    res = Reservation.query.get_or_404(res_id)
    
    form = ConfirmationForm()

    if form.validate_on_submit():
        confirmation = form.confirmation.data
        
        res.new = False
        res.confirmation = confirmation
        db.session.commit()

        return redirect(url_for('res_list_conf', res=res))
    
    return render_template('single.html', res=res, form=form)


@app.route('/<int:res_id>/mail', methods=['GET', 'POST'])
@login_required
def email(res_id):
    res = Reservation.query.get_or_404(res_id)
    
    form = EmailForm()
    
    if form.validate_on_submit():
        email_text = form.email_text.data
        
        res.email_text = email_text
        db.session.commit()
        
        msg = Message('Dziękujemy za zapytanie', recipients=[res.email])
        msg.cc=[msg.sender]
        msg.html = f'''<b> Witaj {res.name}! <br> Dziękujemy za zainteresowanie rezerwacją 
        Nadwiślanina w dniu {res.date} o godzinie {res.time}. <br> {res.email_text}
        <br> Pozdrawiamy - załoga Nadwiślanina. <b>'''
        mail.send(msg)
        
        return redirect(url_for('show', res_id=res.id))
    
    return render_template('single_mail.html', res=res, form=form)

     
@app.route('/<int:res_id>/conf')
@login_required
def show_conf(res_id):
    res = Reservation.query.get_or_404(res_id)
    return render_template('single_conf.html', res=res)


@app.route('/confirmed')
@login_required
def res_list_conf():  
    today = datetime.date.today()
    result = Reservation.query.filter(Reservation.confirmation!=None, Reservation.date>today).order_by(Reservation.date).all()
    return render_template('conf_list.html', result=result)


@app.route('/confirmed_old')
@login_required
def passed():  
    today = datetime.date.today()
    result = Reservation.query.filter(Reservation.confirmation!=None, Reservation.date>today).order_by(Reservation.date).all()
    old = Reservation.query.filter(Reservation.confirmation!=None, Reservation.date<today).order_by(Reservation.date).all()
    return render_template('conf_list_old.html', result=result, old=old)    


@app.route('/<int:res_id>/update', methods=['GET', 'POST'])
@login_required
def update(res_id):
    res = Reservation.query.get_or_404(res_id)
    res.new = False
    db.session.commit()
    return redirect(url_for('res_list_done', res=res))


@app.route('/done')
@login_required
def res_list_done():
    result = Reservation.query.filter_by(new=False, confirmation=None).all()
    return render_template('done_list.html', result=result)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano!')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    user = User.query.first()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
    
        if username == user.username and password == user.password:
            
            login_user(user)
            flash('Zalogowano!')
            
            return redirect(url_for('res_list'))
        
    return render_template('login.html', form=form)


@app.errorhandler(404)
def error_404(error):
    return render_template('404.html') , 404

@app.errorhandler(403)
def error_403(error):
    return render_template('403.html') , 403


if __name__ == '__main__':
    app.run(debug=True)

