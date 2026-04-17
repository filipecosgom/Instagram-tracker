const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function fmtDate(s) {
  if (!s) return '—';
  const [y, m, d] = s.split('-');
  return `${parseInt(d)} ${MONTHS[parseInt(m)-1]} ${y}`;
}

function renderUserList(users, cls) {
  if (!users.length) return `<div class="empty">None this period</div>`;
  return `<ul class="ulist">${users.map(u=>`<li><a href="https://instagram.com/${u}" target="_blank" rel="noopener noreferrer">@${u}</a></li>`).join('')}</ul>`;
}

function updateDetail(idx) {
  const s = DATA[idx];
  document.getElementById('d-gained-count').textContent = s.gained.length;
  document.getElementById('d-lost-count').textContent   = s.lost.length;
  document.getElementById('d-gained-body').innerHTML = renderUserList(s.gained, 'gain');
  document.getElementById('d-lost-body').innerHTML   = renderUserList(s.lost,   'loss');
}

function render() {
  const now = new Date();
  document.getElementById('footer-ts').textContent =
    `Generated ${now.toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'})}`;

  if (!DATA || DATA.length === 0) {
    document.getElementById('app').innerHTML = `
      <div class="no-data">
        <div class="nd-icon">📂</div>
        <h2>No snapshots yet</h2>
        <p>Drop your Instagram export ZIPs into <code>snapshots/input/</code><br>
           then run <code>python tracker.py</code></p>
      </div>`;
    return;
  }

  const latest = DATA[DATA.length - 1];
  const prev   = DATA.length > 1 ? DATA[DATA.length - 2] : null;
  const net    = latest.gained.length - latest.lost.length;

  document.getElementById('header-updated').textContent =
    `${DATA.length} snapshot${DATA.length !== 1 ? 's' : ''} · last: ${fmtDate(latest.date)}`;

  // ── Stats ──
  const statsHTML = `
    <div class="sl">This week</div>
    <div class="stats">
      <div class="stat s-total">
        <div class="stat-lbl">Total followers</div>
        <div class="stat-val">${latest.total.toLocaleString()}</div>
        <div class="stat-sub">${prev ? `${prev.total.toLocaleString()} on ${fmtDate(prev.date)}` : 'First snapshot'}</div>
      </div>
      <div class="stat s-gained">
        <div class="stat-lbl">Gained</div>
        <div class="stat-val">+${latest.gained.length}</div>
        <div class="stat-sub">${prev ? `since ${fmtDate(prev.date)}` : 'baseline'}</div>
      </div>
      <div class="stat s-lost">
        <div class="stat-lbl">Lost</div>
        <div class="stat-val">-${latest.lost.length}</div>
        <div class="stat-sub">${prev ? `since ${fmtDate(prev.date)}` : 'baseline'}</div>
      </div>
      <div class="stat s-net">
        <div class="stat-lbl">Net change</div>
        <div class="stat-val">${net > 0 ? '+' : ''}${net}</div>
        <div class="stat-sub">${prev ? `since ${fmtDate(prev.date)}` : 'baseline'}</div>
      </div>
    </div>`;

  // ── Chart ──
  const chartHTML = DATA.length > 1 ? `
    <div class="chart-section">
      <div class="sl">Growth over time</div>
      <div class="chart-box">
        <canvas id="chart" height="75"></canvas>
      </div>
    </div>` : '';

  // ── Snapshot selector ──
  const snapOptions = DATA.map((s,i) =>
    `<option value="${i}"${i===DATA.length-1?' selected':''}>${fmtDate(s.date)} — ${s.total} followers</option>`
  ).join('');
  const selectorHTML = DATA.length > 1 ? `
    <div class="snap-bar">
      <label>View snapshot</label>
      <select id="snap-sel">${snapOptions}</select>
    </div>` : '';

  // ── Detail tables ──
  const tablesHTML = `
    <div class="sl">Snapshot detail</div>
    <div class="tables">
      <div class="tcard tc-gain">
        <div class="tcard-head">
          <span class="tcard-title">New followers</span>
          <span class="tcard-count" id="d-gained-count">${latest.gained.length}</span>
        </div>
        <div id="d-gained-body">${renderUserList(latest.gained)}</div>
      </div>
      <div class="tcard tc-loss">
        <div class="tcard-head">
          <span class="tcard-title">Unfollowed</span>
          <span class="tcard-count" id="d-lost-count">${latest.lost.length}</span>
        </div>
        <div id="d-lost-body">${renderUserList(latest.lost)}</div>
      </div>
    </div>`;

  // ── History table ──
  const histRows = [...DATA].reverse().map((s, revIdx) => {
    const isFirst = revIdx === DATA.length - 1;
    const g = s.gained.length, l = s.lost.length, n = g - l;
    const gPill = g ? `<span class="pill g">+${g}</span>` : '—';
    const lPill = l ? `<span class="pill l">-${l}</span>` : '—';
    const nPill = isFirst ? '—'
      : n === 0 ? '<span class="pill n">±0</span>'
      : n > 0   ? `<span class="pill g">+${n}</span>`
      :           `<span class="pill l">${n}</span>`;
    return `<tr>
      <td class="col-date">${fmtDate(s.date)}</td>
      <td class="col-total">${s.total.toLocaleString()}</td>
      <td>${gPill}</td><td>${lPill}</td><td>${nPill}</td>
    </tr>`;
  }).join('');

  const histHTML = `
    <div class="hist-section">
      <div class="sl">All snapshots</div>
      <table class="hist-table">
        <thead><tr>
          <th>Date</th><th>Total</th><th>Gained</th><th>Lost</th><th>Net</th>
        </tr></thead>
        <tbody>${histRows}</tbody>
      </table>
    </div>`;

  document.getElementById('app').innerHTML =
    statsHTML + chartHTML + selectorHTML + tablesHTML + histHTML;

  // ── Chart.js ──
  if (DATA.length > 1) {
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: DATA.map(s => fmtDate(s.date)),
        datasets: [{
          data: DATA.map(s => s.total),
          borderColor: '#e8a020',
          backgroundColor: 'rgba(232,160,32,0.05)',
          borderWidth: 2,
          pointBackgroundColor: '#e8a020',
          pointBorderColor: '#0a0a0a',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          fill: true,
          tension: 0.35,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a1a1a',
            borderColor: '#1f1f1f',
            borderWidth: 1,
            titleColor: '#e8a020',
            bodyColor: '#f0ece4',
            titleFont: { family: "'Barlow Condensed'", weight: '600', size: 11 },
            bodyFont: { family: "'Barlow'", size: 13 },
            callbacks: {
              label: ctx => ` ${ctx.parsed.y.toLocaleString()} followers`
            }
          }
        },
        scales: {
          x: {
            grid: { color: '#161616' },
            ticks: { color: '#444', font: { family: "'Barlow Condensed'", size: 11 } }
          },
          y: {
            grid: { color: '#161616' },
            ticks: { color: '#444', font: { family: "'Barlow'", size: 11 } },
            suggestedMin: Math.min(...DATA.map(s => s.total)) - 15,
          }
        }
      }
    });
  }

  // ── Selector logic ──
  if (DATA.length > 1) {
    document.getElementById('snap-sel').addEventListener('change', function() {
      updateDetail(parseInt(this.value));
    });
  }
}

render();
