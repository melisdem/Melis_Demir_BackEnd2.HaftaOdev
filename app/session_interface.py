# bu dosyayı session'ımızı özelleştirmek için kullanıyoruz
# yani flask'ın default session özelliklerini değil de kendi ayarlarımızı kullanabilmek ve
# daha sonra bunları database'lerde kullanabilmek için (anladığım kadarıyla)
# ayrıca özelleştirdiğimiz bu ıd'ler, sign'lar ve salt'larla kırılması daha zor
# bir session oluşturmuş oluyoruz

from flask.sessions import SessionMixin, SessionInterface
import uuid
import json
from itsdangerous import Signer, BadSignature, want_bytes
class MySession(dict, SessionMixin):
    def __init__(self, initial=None, sessionId = None):
        self.initial = initial
        self.sessionId= sessionId
        super(MySession, self).__init__(initial or ())

    # MySession class'ımda methodları yeniden tanımlıyorum
    # bu super'den methodları default olarak alıyorum
    def __setitem__(self,key, value):
        super(MySession, self).__setitem__(key, value)

    def __getitem__(self, item):
        return  super(MySession,self).__getitem__(item)

    def __delitem__(self,key):
        super(MySession, self).__delitem__(key)


class MySessionInterface(SessionInterface):
    session_class = MySession
    salt = "my-session"
    container = dict()
    # dict sunucumun hafızasına kaydediyor

    def __init__(self):
        pass

    def open_session(self, app, request) :
        signedSessionId = request.cookies.get(app.session_cookie_name)
        if not signedSessionId:
            # uuid ile sessionId'ye unique bir değer atıyorum, uuid4 ile string'e çeviriyorum
            sessionId = str(uuid.uuid4())
            return self.session_class(sessionId=sessionId)

        # save session'da imzalı bir session oluşturduk
        # imzasını çözüp üstünde o şekilde işlem yapabiliriz
        # key_derivation ise sign ve salt'ı nasıl hmap'leyeceğimizi söylüyor
        signer = Signer(app.secret_key, salt=self.salt, key_derivation="hmac")
        # unsign'da hata varsa yani data değiştirilmişse, ya da başka hatalar çıkarsa ayıklamak için
        try:
            sessionId = signer.unsign(signedSessionId).decode()
        except BadSignature:
            sessionId = str(uuid.uuid4())
            return self.session_class(sessionId=sessionId)

        # daha önce oluşan session'ları container sözlüğüne kaydettik
        #eğer yoksa yenisini oluşturuyor if not signedSessionId
        # container'ın içinde data varsa onları da alalım
        initialSessionValueAsJson = self.container.get(sessionId)
        try:
            # json'lı session data'sını sözlüğe dönüştürüyorum
            initialSessionValue = json.loads(initialSessionValueAsJson)
        except:
            sessionId = str(uuid.uuid4())
            return self.session_class(sessionId=sessionId)
        return self.session_class(initialSessionValue, sessionId=sessionId)


    def save_session(self, app, session, response):
        # session'ı json olarak kullanmak daha kolay olduğundan
        # json'a çeviriyoruz'
        sessionAsJson = json.dumps(dict(session))

        self.container[session.sessionId] = sessionAsJson

        # session'ı sign ediyoruz
        # app'te atadığımız secret key'ikullanıyoruz yine
        # salt bizim data'mızın önüne şifreli bir string ekleyerek kırılması daha güç bir
        # data oluşturuyor
        signer = Signer(app.secret_key, salt= self.salt, key_derivation="hmac")
        signedSessionId = signer.sign(want_bytes(session.sessionId))
        # want_bytes byteı stringe dönüştürüyor, decodeun tam tersi
        response.set_cookie(app.session_cookie_name, signedSessionId)
