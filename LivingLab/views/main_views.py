from flask import Blueprint, request, render_template, jsonify
from flask_socketio import emit
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.callbacks.base import BaseCallbackHandler
from flask_socketio import SocketIO
import torch

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

# 파인튜닝된 모델 로드
MODEL_NAME = "finetuned_model"  # 파인튜닝된 모델 이름
MODEL_PATH = "finetuned_model/finetuned_model"  # 파인튜닝된 모델의 상대 경로
QUANTIZE_4BIT = True  # 4비트 양자화 여부 설정
attn_implementation = "flash"  # 주의 메커니즘 구현 설정

quantization_config = None
if QUANTIZE_4BIT:
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

loaded_model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=quantization_config,
    attn_implementation=attn_implementation,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# LoRA 어댑터 로드
loaded_model.load_adapter("finetuned_model")

prompt = ChatPromptTemplate.from_template("{topic}")
chain = prompt | loaded_model | StrOutputParser()


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