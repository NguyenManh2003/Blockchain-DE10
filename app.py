from flask import Flask, request, jsonify, render_template
import hashlib, json, time, os
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FILE = 'proposals.json'

# Tải dữ liệu nếu có
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        proposals = json.load(f)
else:
    proposals = []

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(proposals, f, ensure_ascii=False, indent=2)

def calculate_hash(data):
    block_string = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create', methods=['POST'])
def create_proposal():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    minutes = int(data.get('minutes', 0))
    created_by = data.get('created_by', 'Ẩn danh')
    end_time = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()

    prev_hash = proposals[-1]['hash'] if proposals else '0'*64
    proposal = {
        'id': len(proposals) + 1,
        'title': title,
        'content': content,
        'created_by': created_by,
        'end_time': end_time,
        'status': 'Đang mở',
        'agree': [],
        'disagree': [],
        'prev_hash': prev_hash
    }
    proposal['hash'] = calculate_hash(proposal)
    proposals.append(proposal)
    save_data()
    return jsonify({'message': 'Tạo đề xuất thành công!'})

@app.route('/api/vote', methods=['POST'])
def vote():
    data = request.json
    id = data.get('id')
    vote = data.get('vote')
    voter = data.get('voter')
    for p in proposals:
        if p['id'] == id and p['status'] == 'Đang mở':
            if voter in p['agree'] or voter in p['disagree']:
                return jsonify({'error': 'Bạn đã biểu quyết rồi!'})
            if vote == 'agree':
                p['agree'].append(voter)
            elif vote == 'disagree':
                p['disagree'].append(voter)
            save_data()
            return jsonify({'message': 'Biểu quyết thành công!'})
    return jsonify({'error': 'Đề xuất không tồn tại hoặc đã đóng!'})

@app.route('/api/proposals')
def get_proposals():
    now = datetime.utcnow().isoformat()
    for p in proposals:
        if p['status'] == 'Đang mở' and p['end_time'] < now:
            p['status'] = 'Đã đóng'
    save_data()
    return jsonify(proposals)

if __name__ == '__main__':
    app.run(debug=True)