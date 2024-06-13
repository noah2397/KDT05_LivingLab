from flask import Blueprint, request, render_template, jsonify
from flask_socketio import emit
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.callbacks.base import BaseCallbackHandler
from flask_socketio import SocketIO

bp = Blueprint('main', __name__)
socketio = SocketIO()

class FileStreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, filename):
        self.filename = filename

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        with open(self.filename, 'a', encoding='utf-8') as file:
            file.write(token)
        # 실시간 업데이트
        socketio.emit('new_token', {'token': token})

filename = 'test.txt'
file_callback_handler = FileStreamingCallbackHandler(filename)
llm = ChatOllama(
    model="EEVE-Korean-10.8B:latest",
    callback_manager=CallbackManager([file_callback_handler]),
)
prompt = ChatPromptTemplate.from_template("{topic}")
chain = prompt | llm | StrOutputParser()

@bp.route('/', methods=['GET', 'POST'])
def index():
    # test.txt 파일 내용 없애기
    with open(filename, 'w', encoding='utf-8') as file:
        file.write('')
    response_text = ""
    if request.method == 'POST':
        topic = request.form['topic']
        print(topic)
        response_text = chain.invoke({"topic": topic})
    
    return render_template('index.html')

@bp.route('/get_file_content', methods=['GET'])
def get_file_content():
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    return jsonify({"content": content})


