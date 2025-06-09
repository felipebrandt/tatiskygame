from flask import Flask, request, jsonify
import threading

app = Flask(__name__)


def acao_local(dados):
    print("🚀 Gatilho executado com os dados:", dados)


# Endpoint do Webhook
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        dados = request.get_json()
        print("📥 Dados recebidos no webhook:", dados)
        acao_local(dados)
        threading.Thread(target=acao_local, args=(dados,)).start()

        return jsonify({"status": "recebido", "dados": dados}), 200
    else:
        return 'oi'


if __name__ == '__main__':
    app.run()
