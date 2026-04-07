// Blue = Pole A (-5), gray = 0, coral = Pole B (+5)
const COLORSCALE = [
  [0.0,  '#0C447C'],
  [0.25, '#85B7EB'],
  [0.5,  '#e0e0e0'],
  [0.75, '#F0997B'],
  [1.0,  '#712B13'],
];

let currentSection = 'All';

async function fetchHeatmapData(section) {
  const params = section && section !== 'All' ? `?section=${encodeURIComponent(section)}` : '';
  const res = await fetch(`/api/heatmap${params}`);
  return res.json();
}

async function renderHeatmap(section) {
  const data = await fetchHeatmapData(section);
  if (!data.books.length) return;

  const tensionLabels = data.tensions.map(t => t.id);
  const tensionNames  = data.tensions.map(t => t.name);
  const bookNames     = data.books.map(b => b.name);

  // Build hover text: "T01 — Name\nScore: N\nNote"
  const hoverText = data.z.map((row, bi) =>
    row.map((score, ti) => {
      const t = data.tensions[ti];
      const note = data.notes[bi][ti];
      if (score === null) return `${t.id} — ${t.name}<br>n/a`;
      return `${t.id} — ${t.name}<br>Score: ${score > 0 ? '+' : ''}${score}<br>${note}`;
    })
  );

  const trace = {
    type: 'heatmap',
    z: data.z,
    x: tensionLabels,
    y: bookNames,
    text: hoverText,
    hovertemplate: '%{text}<extra></extra>',
    colorscale: COLORSCALE,
    zmin: -5,
    zmax: 5,
    xgap: 1,
    ygap: 1,
    showscale: true,
    colorbar: {
      thickness: 12,
      len: 0.6,
      tickvals: [-5, -2.5, 0, 2.5, 5],
      ticktext: ['Pole A (−5)', '', '0', '', 'Pole B (+5)'],
      tickfont: { size: 10 },
    },
  };

  const layout = {
    margin: { t: 30, b: 60, l: 110, r: 60 },
    xaxis: {
      tickangle: -45,
      tickfont: { size: 11 },
      fixedrange: true,
    },
    yaxis: {
      tickfont: { size: 11 },
      autorange: 'reversed',
    },
    plot_bgcolor: '#f8f8f6',
    paper_bgcolor: '#f8f8f6',
  };

  Plotly.react('heatmap', [trace], layout, {responsive: true, displayModeBar: false});

  // Click on tension column header → show detail panel
  document.getElementById('heatmap').on('plotly_click', evt => {
    const pt = evt.points[0];
    showTensionDetail(pt.x, data, bookNames);
  });
}

function showTensionDetail(tensionId, data, bookNames) {
  const ti = data.tensions.findIndex(t => t.id === tensionId);
  if (ti < 0) return;
  const tension = data.tensions[ti];

  const detail = document.getElementById('tension-detail');
  detail.style.display = 'block';
  document.getElementById('tension-detail-title').textContent =
    `${tension.id} — ${tension.name}  |  Pole A: ${tension.pole_a}  /  Pole B: ${tension.pole_b}`;

  const scores = data.z.map(row => row[ti]);
  const colors = scores.map(s => {
    if (s === null) return '#ccc';
    return s < 0 ? '#85B7EB' : s > 0 ? '#F0997B' : '#e0e0e0';
  });

  const barTrace = {
    type: 'bar',
    orientation: 'h',
    x: scores,
    y: bookNames,
    marker: { color: colors },
    hovertext: data.notes.map(row => row[ti] || ''),
    hovertemplate: '%{y}: %{x}<br>%{hovertext}<extra></extra>',
  };

  Plotly.react('tension-bar-chart', [barTrace], {
    margin: { t: 10, b: 30, l: 110, r: 20 },
    xaxis: { range: [-5, 5], zeroline: true, zerolinecolor: '#aaa' },
    yaxis: { autorange: 'reversed', tickfont: { size: 11 } },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
  }, {responsive: true, displayModeBar: false});
}

function initHeatmap() {
  renderHeatmap('All');

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const section = btn.dataset.section;
      currentSection = section;
      renderHeatmap(section);
      // Also filter book cards
      document.querySelectorAll('.book-card').forEach(card => {
        card.style.display = (section === 'All' || card.dataset.section === section) ? '' : 'none';
      });
    });
  });
}
