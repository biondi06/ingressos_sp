from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium_driver import SeleniumDriver

app = Flask(__name__)
CORS(app)  # Habilitando CORS para permitir requisições do frontend

@app.route('/start-bot', methods=['POST'])
def start_bot():
    data = request.get_json()

    # Verificação dos dados recebidos
    url = data.get('url')
    cpf = data.get('cpf')
    number_of_tickets = int(data.get('numberOfTickets'))
    username = data.get('username')
    password = data.get('password')
    sections_without_discount = data.get('sectionsWithoutDiscount')

    if not url or not cpf or not number_of_tickets or not username or not password or not sections_without_discount:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    try:
        # Inicializando o SeleniumDriver com os dados recebidos
        bot = SeleniumDriver(url)

        bot.accept_cookies()
        target_section_found = bot.define_target_section(desired_sections=sections_without_discount)

        if target_section_found == "none":
            return jsonify({'error': 'Nenhuma seção disponível.'}), 400

        target_section_tab_was_found = bot.go_to_section_tab(target_section_found)
        
        if not target_section_tab_was_found:
            return jsonify({'error': 'Seção não encontrada.'}), 400

        tickets_were_added = bot.add_tickets_to_cart(number_of_tickets, is_without_discount=True)
        if not tickets_were_added:
            return jsonify({'error': 'Falha ao adicionar ingressos ao carrinho.'}), 400

        success = bot.log_in(username, password)

        if success:
            return jsonify({'message': 'Ingressos comprados com sucesso!'})
        else:
            return jsonify({'error': 'Erro no login ou na compra.'}), 500

    except ValueError:
        return jsonify({'error': 'Número de ingressos inválido.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota padrão para evitar erro 404 no favicon
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
