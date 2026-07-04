import os, math, random, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

class ScratchCodingAI:
    def __init__(self, vocab_size=256, hidden_size=32):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.W1 = [[random.uniform(-0.1, 0.1) for _ in range(hidden_size)] for _ in range(vocab_size)]
        self.W2 = [[random.uniform(-0.1, 0.1) for _ in range(vocab_size)] for _ in range(hidden_size)]
        self.char_to_ix = {chr(i): i for i in range(256)}
        self.ix_to_char = {i: chr(i) for i in range(256)}

    def learn_from_internet(self):
        print("Scraping and training engine from open-source web texts...")
        try:
            r = requests.get("https://gutenberg.org", timeout=10)
            text_data = r.text[:3000]
            for i in range(len(text_data) - 1):
                x_idx = self.char_to_ix.get(text_data[i], 32)
                y_idx = self.char_to_ix.get(text_data[i+1], 32)
                hidden = self.W1[x_idx]
                raw_out = [sum(hidden[j] * self.W2[j][k] for j in range(self.hidden_size)) for k in range(self.vocab_size)]
                max_val = max(raw_out)
                exp_out = [math.exp(v - max_val) for v in raw_out]
                sum_exp = sum(exp_out)
                probs = [e / sum_exp for e in exp_out]
                probs[y_idx] -= 1.0
                for j in range(self.hidden_size):
                    for k in range(self.vocab_size):
                        self.W2[j][k] -= 0.01 * hidden[j] * probs[k]
        except Exception as e:
            print(f"Internet fetch training alert: {e}")

    def generate(self, user_input, max_chars=120):
        current_context = user_input
        output_string = ""
        for _ in range(max_chars):
            last_char = current_context[-1] if len(current_context) > 0 else ' '
            idx = self.char_to_ix.get(last_char, 32)
            hidden = self.W1[idx]
            raw_out = [sum(hidden[j] * self.W2[j][k] for j in range(self.hidden_size)) for k in range(self.vocab_size)]
            next_idx = raw_out.index(max(raw_out))
            next_char = self.ix_to_char.get(next_idx, ' ')
            output_string += next_char
            current_context += next_char
            if next_char == '}': break
        return output_string

scratch_ai = ScratchCodingAI()
scratch_ai.learn_from_internet()

@app.route('/compute', methods=['POST'])
def compute():
    prompt = request.json.get('prompt', '')
    generated_text = scratch_ai.generate(user_input=prompt)
    clean_code = f"def output_matrix_logic(data):\n    # Core Prompt Match: {prompt}\n    {generated_text}"
    return jsonify({'code': clean_code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
