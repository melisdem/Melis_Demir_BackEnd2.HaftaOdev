from flask import Flask, render_template, request, redirect,url_for, abort, make_response, session
from itsdangerous import Signer, BadSignature
from .session_interface import MySessionInterface
app = Flask(__name__)
# default olarak import ettiğimiz session, encrypted olarak kaydediliyor.
# bunun için secret key'e ihtiyacımız var
app.secret_key = b"12345?"

app.session_interface = MySessionInterface()

# Anasayfaya yönlendirmek için
# https://www.w3schools.com/w3css/default.asp sitesindeki Portfolio Template'ini kullandım
# ama html ve css kodlarında da birçok değişiklik yaptım
@app.route("/")
def Index():
    return render_template("index.html")


# sayfaya dark-light modu eklemek istedim
# toggle_theme fonksiyonunu app'te tanımlayıp
# her route içinde tekrar çağırabilirdim, bunu tek bir butona atamak demek html dosyasında da butona onclick
# atamak demek olacaktı
# /toggle_theme olarak yönlendirince bunu yapmama gerek kalmadı
# çünkü bulunduğu sayfayı flask hatırlayabiliyormuş redirect(request.args.get("current_page"))
# kod bütünlüğü için bu yolu seçtim ama contact Me sayfasından tyForYourMsg sayfasına yönlendirdiğimde
# temayı değiştirince form dolu olmadığından contactMe sayfasına geri dönüyor, zaman kaybını önlemek için bunu es geçtim
# temayı sayfalar arası geçişte de hatırlayabilmesi için cookie kullandım
# bu cookie'yi sign ettim ki sign kısmında değişiklik olursa Bad Signature hatası versin
# w3-white ve w3-black template'in kullandığı html class isimleri, dark-light modunu
# base html kodunda body elemanının class'ı için bir jinja2 kodu ile ya w3-white yada w3-black olarak
# atamasını sağladım. Cookie'yi jinja2 ile html'de unsign edemediğim için direk sign edilmiş public value'yu kontrol ediyorum

@app.route("/toggle-theme")
def toggle_theme():
    response = make_response(redirect(request.args.get("current_page")))
    signer = Signer("secret_key!")
    themeCookie = request.cookies.get("theme")
    signed_white = signer.sign("w3-white").decode()
    signed_black = signer.sign("w3-black").decode()
    if themeCookie:
        try:
            if signer.unsign(themeCookie).decode() == "w3-white" or "w3-black":
                pass
        except BadSignature:
            print("Bad Signature")
            return redirect(url_for('BadSigned'))
        if themeCookie == signed_black:
            response.set_cookie("theme", signed_white)
        else:
            response.set_cookie("theme", signed_black)
    else:
        response.set_cookie("theme", signed_white)
    return response

# cookie değiştirlmişse try-except bloğunda yakalanacak ve bu url'ye yönlendirilecek
@app.route("/badSignature")
def BadSigned():
    return "<h1>BAD SİGNATURE, COOKİE HAS BEEN CHANGED</h1>"


# .../contact sayfasına yönlendirmek için
@app.route("/contact")
def Contact():
    return render_template("contact.html")


# contact kısmından mesaj gönderildiğinde mesajınıza geri döneceğim teşekkür ederim sayfası çıksın istedim
# ismi kaydediyorum ve isme özel teşekkür ediyorum
# ama tabii mesajı herhangi bir yere kaydetmiyorum
@app.route("/thankYouForYourMessage", methods=["POST", "GET"])
def ContactBack():
    # Eğer form doluysa teşekkür et, eğer değilse ve url'ye
    # /thankYouForYourMessage girilmişse /contact sayfasına yönlendir
    if request.form:
        # derste çoklu data tanımlarken kolaylık olsun diye sözlük kullanmıştık
        # burada bir örneğini kullanmak istedim, çoklu data olmasa bile
        ContextData = {"name" : request.form['Name']}
        return render_template("tyForYourMsg.html", **ContextData)
    else:
        return redirect(url_for('Contact'))


# .../login sayfasına yönlendirmek için
# kullanıcının her sayfada yetkisi olması için session kullandım
# sadece username == 'admin' and password == '12345' user'ı için çalışıyor
# nav bar'da kullanıcı adını ve girişini görebiliyoruz ve login, logout'a dönüşüyor
# bunları ayrıca base html'de jinja2 ile gösterimlerini değiştirdim
@app.route("/login", methods=["POST", "GET"])
def Login():
    if request.method == "POST":
        if request.form:
            if 'username' in request.form and 'password' in request.form:
                username = request.form['username']
                password = request.form['password']
                if username == 'admin' and password == '12345':
                    session['username'] = username
                    session.permanent = False
                    return redirect(url_for('Index'))
                else:
                    # kullanıcı adı veya şifre yanlış ise wrongName fonksiyonuna yönlendiriyorum
                    return redirect(url_for("wrongName"))
        # eğer server request'i anlamlandıramamış ise 400 hata kodu ver, bu özelliği import ettik "abort"
        abort(400)
    # eğer request.form yoksa login sayfasına geri dön
    return render_template("login.html")


# logout yaptığımda session siliniyor ve tekrar nav barda login görünüyor,
# nav bar'daki görünen kullanıcı da siliniyor
@app.route("/logout")
def Logout():
    session.pop("username", None)
    return render_template("logout.html")


# eğer username=admin ve password=12345 girilmemiş ise
# kullanıcı yanlış hatası versin
@app.route("/wrongUsername")
def wrongName():
    return render_template("wrongUsername.html")\


# projelerimin olduğu sayfaya yönlendirme
@app.route("/galery")
def Galery():
    return render_template("galery.html")