from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from selenium_driver import SeleniumDriver
import time

app = Flask(__name__)
CORS(app)  
socketio = SocketIO(app, cors_allowed_origins="*") 

@app.route('/start-bot', methods=['POST'])
def start_bot():
    data = request.get_json()

    url = data.get('url')
    cpf = data.get('cpf')
    number_of_tickets = int(data.get('numberOfTickets'))
    username = data.get('username')
    password = data.get('password')
    sections_without_discount = data.get('sectionsWithoutDiscount')

    if not url or not cpf or not number_of_tickets or not username or not password or not sections_without_discount:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    try:
        bot = SeleniumDriver(url)

        while True:
            try:
                bot.accept_cookies()
                socketio.emit('status_update', {'message': 'Cookies aceitos. Iniciando busca de setores.'})

                target_section_found = bot.define_target_section(desired_sections=sections_without_discount)

                if target_section_found == "none":
                    socketio.emit('status_update', {'message': 'Nenhuma seção disponível. Tentando novamente...'})
                    time.sleep(10) 
                    continue

                socketio.emit('status_update', {'message': f'Seção {target_section_found} encontrada. Tentando adicionar ingressos ao carrinho.'})

                target_section_tab_was_found = bot.go_to_section_tab(target_section_found)
                
                if not target_section_tab_was_found:
                    socketio.emit('status_update', {'message': 'Seção não encontrada. Tentando novamente...'})
                    time.sleep(10)
                    continue

                tickets_were_added = bot.add_tickets_to_cart(number_of_tickets, is_without_discount=True)
                if not tickets_were_added:
                    socketio.emit('status_update', {'message': 'Falha ao adicionar ingressos ao carrinho. Tentando novamente...'})
                    time.sleep(10)
                    continue

                socketio.emit('status_update', {'message': 'Ingressos adicionados ao carrinho. Tentando login...'})

                success = bot.log_in(username, password)

                if success:
                    socketio.emit('status_update', {'message': 'Ingressos comprados com sucesso!'})
                    break
                else:
                    socketio.emit('status_update', {'message': 'Erro no login. Tentando novamente...'})
                    time.sleep(10)
                    continue

            except Exception as e:
                socketio.emit('status_update', {'message': f'Erro: {str(e)}. Tentando novamente em 10 segundos...'})
                time.sleep(10)

        return jsonify({'message': 'Bot finalizado com sucesso!'})

    except ValueError:
        return jsonify({'error': 'Número de ingressos inválido.'}), 400
    except Exception as e:
        socketio.emit('status_update', {'message': f'Erro: {str(e)}'})
        return jsonify({'error': str(e)}), 500
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    socketio.run(app, debug=True)
