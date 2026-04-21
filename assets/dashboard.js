const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function fmtDate(s) {
  if (!s) return '—';
  const [y, m, d] = s.split('-');
  return `${parseInt(d)} ${MONTHS[parseInt(m)-1]} ${y}`;
}

function renderUserList(users, cls, showTooltip = false) {
  if (!users.length) return `<div class="empty">None this period</div>`;
  
  return `<ul class="ulist">${users.map(u => {
    const follower = DATA.followers && DATA.followers[u];
    let tooltipAttr = '';
    
    if (showTooltip && follower) {
      const firstSeen = follower.first_seen || '—';
      const lastSeen = follower.last_seen || '—';
      const tooltipText = `First seen: ${fmtDate(firstSeen)}\\nLast seen: ${fmtDate(lastSeen)}`;
      tooltipAttr = ` title="${tooltipText}"`;
    }
    
    return `<li><a href="https://instagram.com/${u}" target="_blank" rel="noopener noreferrer"${tooltipAttr}>@${u}</a></li>`;
  }).join('')}</ul>`;
}

function updateDetail(idx) {
  const s = DATA.snapshots[idx];  // FIX: was DATA[idx]
  document.getElementById('d-gained-count').textContent = s.gained.length;
  document.getElementById('d-lost-count').textContent   = s.lost.length;
  document.getElementById('d-gained-body').innerHTML = renderUserList(s.gained, 'gain');
  document.getElementById('d-lost-body').innerHTML   = renderUserList(s.lost, 'loss');
}

function render() {
  const now = new Date();
  document.getElementById('footer-ts').textContent =
    `Generated ${now.toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'})}`;

  const snapshots = DATA.snapshots || DATA;
  const totalActive = DATA.totalActive || (snapshots.length > 0 ? snapshots[snapshots.length - 1].total : 0);
  const followersDict = DATA.followers || {};

  if (!snapshots || snapshots.length === 0) {
    document.getElementById('app').innerHTML = `
      <div class="no-data">
        <div class="nd-icon">📂</div>
        <h2>No snapshots yet</h2>
        <p>Drop your Instagram export ZIPs into <code>snapshots/input/</code><br>
           then run <code>python tracker.py</code></p>
      </div>`;
    return;
  }

  const latest = snapshots[snapshots.length - 1];
  const prev   = snapshots.length > 1 ? snapshots[snapshots.length - 2] : null;
  
  // Calculate "this week" stats (latest vs previous snapshot)
  const weekNet = latest.gained.length - latest.lost.length;
  
  // Calculate "since tracking started" stats
  const activeFollowers = Object.keys(followersDict).filter(u => followersDict[u].status === 'active');
  const lostFollowers = Object.keys(followersDict).filter(u => followersDict[u].status === 'lost');
  const totalGainedEver = activeFollowers.length + lostFollowers.length;
  const totalLostEver = lostFollowers.length;
  const totalNetEver = activeFollowers.length;

  document.getElementById('header-updated').textContent =
    `${snapshots.length} snapshot${snapshots.length !== 1 ? 's' : ''} · last: ${fmtDate(latest.date)}`;

  // ── Stats: This Week ──
  const statsWeekHTML = `
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
        <div class="stat-val">${weekNet > 0 ? '+' : ''}${weekNet}</div>
        <div class="stat-sub">${prev ? `since ${fmtDate(prev.date)}` : 'baseline'}</div>
      </div>
    </div>`;

  // ── Stats: Since Tracking Started ──
  const statsAllTimeHTML = `
    <div class="sl">Since tracking started</div>
    <div class="stats">
      <div class="stat s-total">
        <div class="stat-lbl">Active followers</div>
        <div class="stat-val">${activeFollowers.length.toLocaleString()}</div>
        <div class="stat-sub">currently following</div>
      </div>
      <div class="stat s-gained">
        <div class="stat-lbl">Total gained</div>
        <div class="stat-val">+${totalGainedEver}</div>
        <div class="stat-sub">all time</div>
      </div>
      <div class="stat s-lost">
        <div class="stat-lbl">Total lost</div>
        <div class="stat-val">-${totalLostEver}</div>
        <div class="stat-sub">all time</div>
      </div>
      <div class="stat s-net">
        <div class="stat-lbl">Net growth</div>
        <div class="stat-val">${totalNetEver > 0 ? '+' : ''}${totalNetEver}</div>
        <div class="stat-sub">total active</div>
      </div>
    </div>`;

  // ── Chart ──
  const chartHTML = snapshots.length > 1 ? `
    <div class="chart-section">
      <div class="sl">Growth over time</div>
      <div class="chart-box">
        <canvas id="chart" height="75"></canvas>
      </div>
    </div>` : '';

  // ── Snapshot selector ──
  const snapOptions = snapshots.map((s,i) =>
    `<option value="${i}"${i===snapshots.length-1?' selected':''}>${fmtDate(s.date)} — ${s.total} followers</option>`
  ).join('');
  const selectorHTML = snapshots.length > 1 ? `
    <div class="snap-bar">
      <label>View snapshot</label>
      <select id="snap-sel">${snapOptions}</select>
    </div>` : '';

  // ── Detail tables (gained/lost for selected snapshot) ──
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

  // ── Active followers list ──
  const activeFollowersHTML = `
    <div class="followers-section">
      <div class="sl">All active followers (${activeFollowers.length})</div>
      <div class="search-bar">
        <input 
          type="text" 
          id="follower-search" 
          placeholder="Search followers..."
          autocomplete="off"
        >
        <span class="search-count" id="search-count">${activeFollowers.length} of ${activeFollowers.length}</span>
      </div>
      <div class="tcard">
        <div class="tcard-body" id="active-followers-list">${renderUserList(activeFollowers, 'active', true)}</div>
      </div>
    </div>`;

  // ── History table ──
  const histRows = [...snapshots].reverse().map((s, revIdx) => {
    const isFirst = revIdx === snapshots.length - 1;
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
    statsWeekHTML + statsAllTimeHTML + chartHTML + selectorHTML + tablesHTML + activeFollowersHTML + histHTML;

  // ── Chart.js ──
  if (snapshots.length > 1) {
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: snapshots.map(s => fmtDate(s.date)),
        datasets: [{
          data: snapshots.map(s => s.total),
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
            suggestedMin: Math.min(...snapshots.map(s => s.total)) - 15,
          }
        }
      }
    });
  }

  // ── Selector logic ──
  if (snapshots.length > 1) {
    document.getElementById('snap-sel').addEventListener('change', function() {
      updateDetail(parseInt(this.value));
    });
  }

  // ── Search filter logic ──
  const searchInput = document.getElementById('follower-search');
  const searchCount = document.getElementById('search-count');
  const followersList = document.getElementById('active-followers-list');
  
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const query = this.value.toLowerCase().trim();
      const items = followersList.querySelectorAll('li');
      let visibleCount = 0;
      
      items.forEach(item => {
        const username = item.textContent.toLowerCase();
        if (username.includes(query)) {
          item.style.display = 'flex';
          visibleCount++;
        } else {
          item.style.display = 'none';
        }
      });
      
      searchCount.textContent = `${visibleCount} of ${activeFollowers.length}`;
      
      // Visual feedback when no results
      if (visibleCount === 0 && query.length > 0) {
        searchCount.style.color = 'var(--loss)';
      } else {
        searchCount.style.color = 'var(--muted)';
      }
    });
  }
}

render();
