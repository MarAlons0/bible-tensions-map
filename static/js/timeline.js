const LINE_COLORS = [
  '#0C447C','#712B13','#2E7D32','#6A1E8A','#B45309',
  '#00838F','#C62828','#4527A0','#558B2F','#E65100',
  '#1565C0','#AD1457','#00695C','#F9A825','#283593',
  '#6D4C41','#37474F','#0277BD','#2E7D32','#4E342E',
];

let currentOrder = 'scholarly';

// --- Chart ---

async function fetchChartData(tensionIds, order) {
  const tParam = tensionIds.length ? `tensions=${tensionIds.join(',')}` : '';
  const oParam = `order=${order}`;
  const qs = [tParam, oParam].filter(Boolean).join('&');
  const res = await fetch(`/api/timeline-chart?${qs}`);
  return res.json();
}

async function renderTimelineChart() {
  const checked = Array.from(
    document.querySelectorAll('.tension-pick:checked')
  ).map(el => el.value);

  if (!checked.length) { Plotly.purge('timeline-chart'); return; }

  const data = await fetchChartData(checked, currentOrder);

  const xLabel = currentOrder === 'scholarly'
    ? 'Books in scholarly composition order →'
    : 'Books in canonical order →';

  const traces = data.traces.map((t, i) => ({
    type: 'scatter',
    mode: 'lines+markers',
    name: `${t.tension_id} — ${t.tension_name}`,
    x: t.x,
    y: t.y,
    line: { color: LINE_COLORS[i % LINE_COLORS.length], width: 2 },
    marker: { size: 7, color: LINE_COLORS[i % LINE_COLORS.length] },
    customdata: t.notes.map(note => [t.tension_id, t.tension_name, t.pole_a, t.pole_b, note]),
    hovertemplate:
      '<b>%{x}</b><br>' +
      '%{customdata[0]} — %{customdata[1]}<br>' +
      'Score: %{y}<br>' +
      '<i>%{customdata[4]}</i><extra></extra>',
    connectgaps: false,
  }));

  const layout = {
    xaxis: {
      title: xLabel,
      tickangle: -45,
      tickfont: { size: 10 },
    },
    yaxis: {
      title: 'Score',
      range: [-5.5, 5.5],
      zeroline: true, zerolinecolor: '#ccc', zerolinewidth: 1,
      gridcolor: '#eee',
      tickvals: [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
    },
    legend: { orientation: 'h', y: -0.35, font: { size: 11 } },
    margin: { t: 20, b: 120, l: 60, r: 20 },
    paper_bgcolor: '#f8f8f6',
    plot_bgcolor: '#ffffff',
    shapes: [{
      type: 'line', x0: 0, x1: 1, xref: 'paper', y0: 0, y1: 0,
      line: { color: '#bbb', dash: 'dot', width: 1 },
    }],
    annotations: [
      { xref: 'paper', yref: 'y', x: -0.01, y: 4.5, text: 'Pole B',
        showarrow: false, font: { size: 10, color: '#aaa' }, textangle: -90 },
      { xref: 'paper', yref: 'y', x: -0.01, y: -4.5, text: 'Pole A',
        showarrow: false, font: { size: 10, color: '#aaa' }, textangle: -90 },
    ],
  };

  Plotly.react('timeline-chart', traces, layout, { responsive: true, displayModeBar: false });
}

// --- Book list sort ---

function sortBookList(order) {
  const list = document.getElementById('timeline-list');
  const items = Array.from(list.querySelectorAll('.timeline-item'));

  items.sort((a, b) => {
    if (order === 'scholarly') {
      return Number(a.dataset.dateEstimate) - Number(b.dataset.dateEstimate);
    } else {
      return Number(a.dataset.canonicalOrder) - Number(b.dataset.canonicalOrder);
    }
  });

  // Re-append in sorted order (moves DOM nodes, no clone needed)
  items.forEach(item => list.appendChild(item));
}

// --- Toggle ---

function setOrder(order) {
  currentOrder = order;

  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.order === order);
  });

  const hint = document.getElementById('toggle-hint');
  hint.textContent = order === 'scholarly'
    ? 'Earliest composed → latest'
    : 'Genesis → Malachi';

  sortBookList(order);
  renderTimelineChart();
}

// --- Init ---

function initTimeline() {
  // Start in scholarly order — sort the server-rendered canonical list immediately
  sortBookList('scholarly');
  renderTimelineChart();

  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => setOrder(btn.dataset.order));
  });

  document.querySelectorAll('.tension-pick').forEach(cb => {
    cb.addEventListener('change', renderTimelineChart);
  });
}
