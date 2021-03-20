from flask import render_template, url_for, flash, redirect, Blueprint, request
from flask_login import login_user, logout_user, login_required, LoginManager
from project.app import app, db
from project.models import User, Reservation
from project.forms import ReservationForm, LoginForm, ConfirmationForm, EmailForm
from flask_mail import Mail, Message
import datetime


app_routing = Blueprint('app_routing', __name__)


mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "app_routing.login"
login_manager.login_message = "Zaloguj się, aby mieć dostęp do tej strony."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app_routing.route('/')
def index():
    return render_template('index.html')
                           
    
@app_routing.route('/reserve', methods=['GET', 'POST'])
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


@app_routing.route('/admin')
@login_required
def res_list():
    result = Reservation.query.filter_by(new=True).all()
    return render_template('new_list.html', result=result)


@app_routing.route('/<int:res_id>', methods=['GET', 'POST'])
@login_required
def show(res_id):
    res = Reservation.query.get_or_404(res_id)
    
    form = ConfirmationForm()

    if form.validate_on_submit():
        confirmation = form.confirmation.data
        
        res.new = False
        res.confirmation = confirmation
        db.session.commit()

        return redirect(url_for('app_routing.res_list_conf', res=res))
    
    return render_template('single.html', res=res, form=form)


@app_routing.route('/<int:res_id>/mail', methods=['GET', 'POST'])
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
        flash('Wiadomość została wysłana!')
        
        return redirect(url_for('app_routing.show', res_id=res.id))
    
    return render_template('single_mail.html', res=res, form=form)

     
@app_routing.route('/<int:res_id>/conf')
@login_required
def show_conf(res_id):
    res = Reservation.query.get_or_404(res_id)
    return render_template('single_conf.html', res=res)


@app_routing.route('/confirmed')
@login_required
def res_list_conf():  
    today = datetime.date.today()
    result = Reservation.query.filter(Reservation.confirmation!=None, Reservation.date>today).order_by(Reservation.date).all()
    return render_template('conf_list.html', result=result)


@app_routing.route('/confirmed_old')
@login_required
def passed():  
    today = datetime.date.today()
    result = Reservation.query.filter(Reservation.confirmation!=None, Reservation.date>today).order_by(Reservation.date).all()
    old = Reservation.query.filter(Reservation.confirmation!=None, Reservation.date<today).order_by(Reservation.date).all()
    return render_template('conf_list_old.html', result=result, old=old)    


@app_routing.route('/<int:res_id>/update', methods=['GET', 'POST'])
@login_required
def update(res_id):
    res = Reservation.query.get_or_404(res_id)
    res.new = False
    db.session.commit()
    return redirect(url_for('app_routing.res_list_done', res=res))


@app_routing.route('/done')
@login_required
def res_list_done():
    result = Reservation.query.filter_by(new=False, confirmation=None).all()
    return render_template('done_list.html', result=result)


@app_routing.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano!')
    return redirect(url_for('app_routing.index'))


@app_routing.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    
    if form.validate_on_submit():
        
        user = User.query.filter_by(username=form.username.data, 
                        password=form.password.data, is_admin=True).first()
        
        if user is not None:
    
            login_user(user)
            flash('Zalogowano!')
        
            next = request.args.get('next')

            if next == None or not next[0]=='/':
                next = url_for('app_routing.res_list')

            return redirect(next)
        
        flash('Podana nazwa użytkownika lub hasło jest niepoprawne.')
        
    return render_template('login.html', form=form)


@app_routing.app_errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

@app_routing.app_errorhandler(403)
def error_403(error):
    return render_template('403.html'), 403

