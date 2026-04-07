// Section color palette
const SECTION_COLORS = {
  'Pentateuch':      '#0C447C',
  'Historical Books':'#2E7D32',
  'Wisdom / Poetry': '#6A1E8A',
  'Major Prophets':  '#B45309',
  'Minor Prophets':  '#C62828',
};

function colorForValue(val) {
  return SECTION_COLORS[val] || '#888';
}

async function fetchBiplotData(xId, yId, colorBy) {
  const res = await fetch(`/api/biplot?x=${xId}&y=${yId}&color=${colorBy}`);
  return res.json();
}

async function renderBiplot() {
  const xId    = document.getElementById('x-axis').value;
  const yId    = document.getElementById('y-axis').value;
  const colorBy = document.getElementById('color-by').value;

  const data = await fetchBiplotData(xId, yId, colorBy);
  if (!data.points.length) return;

  // Group points by color_val for separate traces (so legend works)
  const groups = {};
  data.points.forEach(pt => {
    const key = pt.color_val || 'Unknown';
    if (!groups[key]) groups[key] = [];
    groups[key].push(pt);
  });

  const traces = Object.entries(groups).map(([groupName, pts]) => ({
    type: 'scatter',
    mode: 'markers+text',
    name: groupName,
    x: pts.map(p => p.x),
    y: pts.map(p => p.y),
    text: pts.map(p => p.book_name),
    textposition: 'top center',
    textfont: { size: 10 },
    marker: {
      size: 12,
      color: colorForValue(groupName),
      opacity: 0.85,
      line: { width: 1, color: '#fff' },
    },
    customdata: pts.map(p => [p.book_id, p.note_x, p.note_y, p.book_name]),
    hovertemplate:
      '<b>%{customdata[3]}</b><br>' +
      `${data.x_tension.id}: %{x} — %{customdata[1]}<br>` +
      `${data.y_tension.id}: %{y} — %{customdata[2]}<br>` +
      '<extra></extra>',
  }));

  // Quadrant annotations
  const xt = data.x_tension;
  const yt = data.y_tension;
  const annotations = [
    { x: -4.5, y: 4.5,  text: `${xt.pole_a}<br>${yt.pole_b}`,  showarrow: false, font: {size: 9, color: '#aaa'}, align: 'left' },
    { x:  4.5, y: 4.5,  text: `${xt.pole_b}<br>${yt.pole_b}`,  showarrow: false, font: {size: 9, color: '#aaa'}, align: 'right' },
    { x: -4.5, y: -4.5, text: `${xt.pole_a}<br>${yt.pole_a}`,  showarrow: false, font: {size: 9, color: '#aaa'}, align: 'left' },
    { x:  4.5, y: -4.5, text: `${xt.pole_b}<br>${yt.pole_a}`,  showarrow: false, font: {size: 9, color: '#aaa'}, align: 'right' },
  ];

  const layout = {
    xaxis: {
      title: `${xt.id} — ${xt.name}<br><small>${xt.pole_a} ← → ${xt.pole_b}</small>`,
      range: [-5.8, 5.8], zeroline: true, zerolinecolor: '#ccc', gridcolor: '#eee',
    },
    yaxis: {
      title: `${yt.id} — ${yt.name}`,
      range: [-5.8, 5.8], zeroline: true, zerolinecolor: '#ccc', gridcolor: '#eee',
    },
    annotations,
    margin: { t: 30, b: 80, l: 80, r: 40 },
    legend: { orientation: 'h', y: -0.2 },
    paper_bgcolor: '#f8f8f6',
    plot_bgcolor: '#ffffff',
    shapes: [
      { type: 'line', x0: 0, x1: 0, y0: -5.8, y1: 5.8, line: { color: '#ccc', dash: 'dot' } },
      { type: 'line', x0: -5.8, x1: 5.8, y0: 0, y1: 0, line: { color: '#ccc', dash: 'dot' } },
    ],
  };

  Plotly.react('biplot', traces, layout, {responsive: true, displayModeBar: false});

  // Click → navigate to book detail
  document.getElementById('biplot').on('plotly_click', evt => {
    const pt = evt.points[0];
    if (pt.customdata) window.location.href = `/book/${pt.customdata[0]}`;
  });
}

function initBiplot() {
  renderBiplot();

  document.getElementById('update-biplot').addEventListener('click', renderBiplot);

  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('x-axis').value = btn.dataset.x;
      document.getElementById('y-axis').value = btn.dataset.y;
      renderBiplot();
    });
  });
}
