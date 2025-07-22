from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from gpt4all import GPT4All
from utils.scrapper import fetch_genecards_summary
from utils.formater import format_context

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'  # Change this to a real secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS

# Initialize the model globally
model = GPT4All("mistral-7b-openorca.Q4_0.gguf", model_path="./")

def ask_local_gpt(context, user_question):
    with model.chat_session():
        full_prompt = f"{context}\n\nQuestion: {user_question}\nAnswer:"
        response = model.generate(full_prompt, max_tokens=500)
        return response.strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/change_gene', methods=['POST'])
def change_gene():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        gene = data.get('gene', '').strip().upper()
        
        if not gene:
            return jsonify({'error': 'Gene name is required'}), 400
        
        summary = fetch_genecards_summary(gene)
        pubmed = "PubMed abstract or other data could go here"
        context = format_context(gene, summary, pubmed)
        
        session['current_gene'] = gene
        session['chat_history'] = [{
            'sender': 'system',
            'message': f"Now discussing gene {gene}"
        }]
        session['context'] = context
        session.modified = True
        
        return jsonify({
            'success': True, 
            'gene': gene,
            'message': f"Gene changed to {gene}"
        })
        
    except Exception as e:
        print(f"Error in change_gene: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        question = data.get('question', '').strip()
        current_gene = session.get('current_gene')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        if not current_gene:
            return jsonify({'error': 'No gene selected'}), 400
        
        answer = ask_local_gpt(session.get('context', ''), question)
        
        session['chat_history'].extend([
            {'sender': 'user', 'message': question},
            {'sender': 'assistant', 'message': answer}
        ])
        session.modified = True
        
        return jsonify({
            'answer': answer,
            'current_gene': current_gene
        })
        
    except Exception as e:
        print(f"Error in ask_question: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)