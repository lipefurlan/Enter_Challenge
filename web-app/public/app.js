const API = '';  // mesmo host — FastAPI serve o frontend e a API

let allClients = [];

// ------------------------------------------------------------------ //
// Inicialização: carrega lista de clientes da API
// ------------------------------------------------------------------ //
async function loadClients() {
  try {
    const res = await fetch(`${API}/api/clients`);
    allClients = await res.json();
    renderClientList(allClients);
  } catch (err) {
    document.getElementById('client-list').innerHTML =
      '<p class="empty-msg">Erro ao carregar clientes.</p>';
  }
}

function renderClientList(clients) {
  const container = document.getElementById('client-list');

  if (!clients.length) {
    container.innerHTML = '<p class="empty-msg">Nenhum cliente cadastrado.</p>';
    return;
  }

  container.innerHTML = clients.map(c => `
    <label class="client-item" id="item-${c.id}">
      <input type="checkbox" value="${c.id}" onchange="onCheckChange()" />
      <div class="client-info">
        <div class="client-name">${c.name}</div>
        <div class="client-email">${c.email} &nbsp;·&nbsp; Assessor: ${c.advisor_name}</div>
      </div>
    </label>
  `).join('');

  // Sincroniza visual da label com checkbox
  document.querySelectorAll('.client-item input').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.closest('.client-item').classList.toggle('selected', cb.checked);
    });
  });
}

function onCheckChange() {
  const anyChecked = getSelectedIds().length > 0;
  document.getElementById('btn-generate').disabled = !anyChecked;
}

function getSelectedIds() {
  return [...document.querySelectorAll('.client-item input:checked')].map(cb => cb.value);
}

// ------------------------------------------------------------------ //
// Gera relatórios para os clientes selecionados
// ------------------------------------------------------------------ //
document.getElementById('btn-generate').addEventListener('click', async () => {
  const ids = getSelectedIds();
  if (!ids.length) return;

  setLoading(true, `Gerando relatórios para ${ids.length} cliente(s)...`);

  try {
    const res = await fetch(`${API}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_ids: ids }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro desconhecido');
    }

    const results = await res.json();
    renderResults(results);
    setLoading(false, `${results.filter(r => r.status === 'success').length} relatório(s) gerado(s) com sucesso.`);
  } catch (err) {
    setLoading(false, `Erro: ${err.message}`);
  }
});

// ------------------------------------------------------------------ //
// Renderiza resultados com links de download
// ------------------------------------------------------------------ //
function renderResults(results) {
  const card = document.getElementById('results-card');
  const list = document.getElementById('results-list');
  card.style.display = 'block';

  list.innerHTML = results.map(r => {
    if (r.status === 'success') {
      return `
        <div class="result-item success">
          <div>
            <div class="result-name">✅ ${r.client_name}</div>
            <div class="result-status">${r.filename}</div>
          </div>
          <a class="btn-download" href="/api/download/${r.filename}" download="${r.filename}">
            Baixar .pdf
          </a>
        </div>`;
    } else {
      return `
        <div class="result-item error">
          <div>
            <div class="result-name">❌ ${r.client_name}</div>
            <div class="tag-error">${r.error}</div>
          </div>
        </div>`;
    }
  }).join('');
}

// ------------------------------------------------------------------ //
// Helpers de UI
// ------------------------------------------------------------------ //
function setLoading(loading, msg) {
  const btn = document.getElementById('btn-generate');
  const wrap = document.getElementById('progress-wrap');
  const bar = document.getElementById('progress-bar');
  const statusMsg = document.getElementById('status-msg');

  btn.disabled = loading;
  wrap.style.display = loading ? 'block' : 'none';
  bar.style.width = loading ? '70%' : '0%';
  statusMsg.textContent = msg || '';
}

// ------------------------------------------------------------------ //
// Bootstrap
// ------------------------------------------------------------------ //
loadClients();