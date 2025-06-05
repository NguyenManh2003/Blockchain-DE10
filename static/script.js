document.getElementById('createForm').addEventListener('submit', async e => {
    e.preventDefault();
    const title = document.getElementById('title').value.trim();
    const content = document.getElementById('content').value.trim();
    const minutes = document.getElementById('minutes').value;
    const created_by = document.getElementById('created_by').value.trim();

    if (!title || !content || !minutes) {
        alert('Vui lòng nhập đầy đủ thông tin!');
        return;
    }

    const res = await fetch('/api/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, minutes, created_by })
    });

    const data = await res.json();
    alert(data.message || data.error);
    loadProposals();
});

async function loadProposals() {
    const res = await fetch('/api/proposals');
    const data = await res.json();
    const list = document.getElementById('proposalList');
    list.innerHTML = '';

    data.forEach(p => {
        const div = document.createElement('div');
        div.className = 'proposal';
        div.innerHTML = `
            <h3>${p.title}</h3>
            <p>${p.content}</p>
            <p><strong>Người tạo:</strong> ${p.created_by}</p>
            <p><strong>Trạng thái:</strong> ${p.status}</p>
            <p><strong>Thời hạn:</strong> ${new Date(p.end_time).toLocaleString()}</p>
            ${p.status === 'Đang mở' ? `
                <input type="text" placeholder="Tên bạn" id="voter_${p.id}" />
                <button onclick="vote(${p.id}, 'agree')">Đồng ý</button>
                <button onclick="vote(${p.id}, 'disagree')">Không đồng ý</button>
            ` : `
                <p><strong>Đồng ý:</strong> ${p.agree.length} (${p.agree.length ? p.agree.join(', ') : 'Không có'})</p>
                <p><strong>Không đồng ý:</strong> ${p.disagree.length} (${p.disagree.length ? p.disagree.join(', ') : 'Không có'})</p>
                <p><strong>Hash:</strong> ${p.hash}</p>
            `}
        `;
        list.appendChild(div);
    });
}

async function vote(id, voteType) {
    const voter = document.getElementById(`voter_${id}`).value.trim();
    if (!voter) return alert('Vui lòng nhập tên bạn');
    const res = await fetch('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, vote: voteType, voter })
    });
    const data = await res.json();
    alert(data.message || data.error);
    loadProposals();
}

loadProposals();
setInterval(loadProposals, 10000);