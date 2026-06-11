from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Configuração para salvar fotos localmente durante o teste
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulador de Banco de Dados (Dicionário na memória)
ordens_servico = {
    1: {
        "id": 1,
        "cliente": "Carlos Silva - Apto 402",
        "tecnico": "Rafael Souza",
        "status": "Agendado",
        "descricao": "Ajuste nas dobradiças do armário da cozinha e fixação do painel da TV.",
        "foto_previa": "projeto_cozinha.jpg",
        "foto_antes": None,
        "foto_depois": None,
        "inicio": None,
        "termino": None,
        "atividades": ""
    }
}

@app.route('/')
def dashboard():
    """Painel do Gestor - Mostra todas as OS e Indicadores"""
    return render_template('dashboard.html', ordens=ordens_servico.values())

@app.route('/os/<int:os_id>', methods=['GET', 'POST'])
def view_os(os_id):
    """Tela do Técnico - Onde ele executa o serviço pelo celular"""
    os_atual = ordens_servico.get(os_id)
    if not os_atual:
        return "Ordem de serviço não encontrada", 404

    if request.method == 'POST':
        acao = request.form.get('acao')
        
        # 1. Confirmação de Comparecimento / Início do serviço
        if acao == 'iniciar':
            os_atual['status'] = 'Em Atendimento'
            os_atual['inicio'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
        # 2. Salvando progresso e fotos (Antes e Depois)
        elif acao == 'salvar':
            os_atual['status'] = request.form.get('status')
            os_atual['atividades'] = request.form.get('atividades')
            
            # Processa upload da foto "Antes"
            if 'foto_antes' in request.files:
                file_antes = request.files['foto_antes']
                if file_antes.filename != '':
                    filename = f"os_{os_id}_antes_{file_antes.filename}"
                    file_antes.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    os_atual['foto_antes'] = filename

            # Processa upload da foto "Depois"
            if 'foto_depois' in request.files:
                file_depois = request.files['foto_depois']
                if file_depois.filename != '':
                    filename = f"os_{os_id}_depois_{file_depois.filename}"
                    file_depois.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    os_atual['foto_depois'] = filename
                    
            # Se concluiu, bota hora de término
            if os_atual['status'] == 'Concluído' and not os_atual['termino']:
                os_atual['termino'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        return redirect(url_for('view_os', os_id=os_id))

    return render_template('tecnico.html', os=os_atual)

if __name__ == '__main__':
    app.run(debug=True)