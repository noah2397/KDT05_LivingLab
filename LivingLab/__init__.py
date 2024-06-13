from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    print(f'__name__ : {__name__}')
    
    app.config.from_pyfile('config.py')  # 설정 내용 로딩
    
    from .views import main_views
    app.register_blueprint(main_views.bp)
    
    socketio.init_app(app)
    
    return app


