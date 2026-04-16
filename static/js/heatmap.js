// Layered heatmap: Testament → Section → Book
// Click the ▶/▼ label on the y-axis to expand/collapse.
// Click a cell in a book row to see the tension detail bar chart.

const COLORSCALE = [
  [0.0,  '#0C447C'],
  [0.25, '#85B7EB'],
  [0.5,  '#e0e0e0'],
  [0.75, '#F0997B'],
  [1.0,  '#712B13'],
];

const TESTAMENT_ORDER = ['Old Testament', 'Apocrypha', 'New Testament'];

const SECTION_ORDER = {
  'Old Testament': ['Pentateuch', 'Historical Books', 'Wisdom Literature', 'Major Prophets', 'Minor Prophets'],
  'Apocrypha': ['Narrative', 'Wisdom', 'Prophetic & Liturgical', 'Additions to Daniel', 'Apocalyptic'],
  'New Testament': ['Gospels', 'Gospels & Acts', 'Pauline Epistles', 'General Epistles', 'Revelation'],
};

// Non-breaking space — SVG preserves these; regular spaces get collapsed.
const NB = '\u00A0';

let allData = null;
let expandedTestaments = new Set(); // both collapsed on load
let expandedSections   = new Set();
let labelToMeta = {};   // rebuilt each render: label string → row meta
let cellClickAttached  = false;

// --------------------------------------------------------------------------
// Aggregation helpers
// --------------------------------------------------------------------------

function median(values) {
  const nums = values.filter(v => v !== null && v !== undefined);
  if (!nums.length) return null;
  nums.sort((a, b) => a - b);
  const mid = Math.floor(nums.length / 2);
  return nums.length % 2 !== 0 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
}

function aggScores(books, tensions) {
  return tensions.map(t => median(books.map(b => b.scores[t.id] ?? null)));
}

function aggNotes(books, tensions, scores) {
  return tensions.map((t, i) => {
    if (scores[i] === null) return 'n/a';
    const n = books.filter(b => b.scores[t.id] !== null && b.scores[t.id] !== undefined).length;
    return `median of ${n} book${n !== 1 ? 's' : ''}`;
  });
}

// --------------------------------------------------------------------------
// Row builder
// --------------------------------------------------------------------------

function buildRows() {
  const tensions = allData.tensions;
  const rows = [];
  labelToMeta = {};

  for (const testament of TESTAMENT_ORDER) {
    const tBooks = allData.books.filter(b => b.testament === testament);
    if (!tBooks.length) continue;

    const expanded = expandedTestaments.has(testament);
    // Testament label — no indentation
    const label = `${expanded ? '▼' : '▶'} ${testament}`;
    const aScores = aggScores(tBooks, tensions);
    const aNotes  = aggNotes(tBooks, tensions, aScores);

    rows.push({ label, scores: aScores, notes: aNotes });
    labelToMeta[label] = { type: 'testament', id: testament };

    if (expanded) {
      for (const section of (SECTION_ORDER[testament] || [])) {
        const sBooks = tBooks.filter(b => b.section === section);
        if (!sBooks.length) continue;

        const sKey      = `${testament}::${section}`;
        const sExpanded = expandedSections.has(sKey);
        // Two non-breaking spaces for section indentation
        const sLabel = `${NB}${NB}${sExpanded ? '▼' : '▶'} ${section}`;
        const sScores = aggScores(sBooks, tensions);
        const sNotes  = aggNotes(sBooks, tensions, sScores);

        rows.push({ label: sLabel, scores: sScores, notes: sNotes });
        labelToMeta[sLabel] = { type: 'section', id: sKey };

        if (sExpanded) {
          for (const book of sBooks) {
            // Four non-breaking spaces for book indentation
            const bLabel  = `${NB}${NB}${NB}${NB}${book.name}`;
            const bScores = tensions.map(t => book.scores[t.id] ?? null);
            const bNotes  = tensions.map(t => book.notes[t.id] || '');
            rows.push({ label: bLabel, scores: bScores, notes: bNotes });
            labelToMeta[bLabel] = { type: 'book', id: book.id, name: book.name };
          }
        }
      }
    }
  }

  return rows;
}

// --------------------------------------------------------------------------
// Toggle helpers (used by both label clicks and cell clicks)
// --------------------------------------------------------------------------

function toggleMeta(meta) {
  if (meta.type === 'testament') {
    expandedTestaments.has(meta.id)
      ? expandedTestaments.delete(meta.id)
      : expandedTestaments.add(meta.id);
    renderHeatmap();
  } else if (meta.type === 'section') {
    expandedSections.has(meta.id)
      ? expandedSections.delete(meta.id)
      : expandedSections.add(meta.id);
    renderHeatmap();
  }
}

// --------------------------------------------------------------------------
// Make y-axis tick labels for aggregate rows clickable
// --------------------------------------------------------------------------

function attachYAxisClickHandlers() {
  // Plotly renders asynchronously; give it a tick to finish painting the SVG.
  requestAnimationFrame(() => {
    const tickEls = document.querySelectorAll('#heatmap .ytick > text');
    tickEls.forEach(el => {
      const rawLabel = el.textContent;
      const meta = labelToMeta[rawLabel];
      if (!meta || meta.type === 'book') return;

      // Replace the node to clear any prior listeners
      const fresh = el.cloneNode(true);
      el.parentNode.replaceChild(fresh, el);

      fresh.style.cursor = 'pointer';
      fresh.style.fontWeight = '700';

      fresh.addEventListener('click', e => {
        e.stopPropagation();
        toggleMeta(meta);
      });
    });
  });
}

// --------------------------------------------------------------------------
// Render
// --------------------------------------------------------------------------

function renderHeatmap() {
  const rows     = buildRows();
  const tensions = allData.tensions;

  const labels    = rows.map(r => r.label);
  const z         = rows.map(r => r.scores);
  const hoverText = rows.map(row =>
    row.scores.map((score, ti) => {
      const t = tensions[ti];
      if (score === null) return `${t.id} — ${t.name}<br>n/a`;
      const sign = score > 0 ? '+' : '';
      const val  = Number.isInteger(score) ? score : score.toFixed(1);
      return `${t.id} — ${t.name}<br>Score: ${sign}${val}<br>${row.notes[ti]}`;
    })
  );

  const height = Math.max(200, rows.length * 28 + 100);

  const trace = {
    type: 'heatmap',
    z,
    x: tensions.map(t => t.id),
    y: labels,
    text: hoverText,
    hovertemplate: '%{text}<extra></extra>',
    colorscale: COLORSCALE,
    zmin: -5,
    zmax: 5,
    xgap: 1,
    ygap: 2,
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
    height,
    margin: { t: 30, b: 60, l: 185, r: 60 },
    xaxis: { tickangle: -45, tickfont: { size: 11 }, fixedrange: true },
    yaxis: { tickfont: { size: 11 }, autorange: 'reversed', fixedrange: true },
    plot_bgcolor: '#f8f8f6',
    paper_bgcolor: '#f8f8f6',
  };

  Plotly.react('heatmap', [trace], layout, { responsive: true, displayModeBar: false });

  // Make aggregate y-axis labels clickable (SVG post-processing)
  attachYAxisClickHandlers();

  // Cell click handler — attached once; labelToMeta is always current
  if (!cellClickAttached) {
    document.getElementById('heatmap').on('plotly_click', evt => {
      const pt   = evt.points[0];
      const meta = labelToMeta[pt.y];
      if (!meta) return;

      if (meta.type === 'book') {
        showTensionDetail(pt.x, buildRows(), allData.tensions);
      } else {
        // Fallback: cell click on aggregate row also toggles
        toggleMeta(meta);
      }
    });
    cellClickAttached = true;
  }
}

// --------------------------------------------------------------------------
// Tension detail panel
// --------------------------------------------------------------------------

function showTensionDetail(tensionId, rows, tensions) {
  const ti = tensions.findIndex(t => t.id === tensionId);
  if (ti < 0) return;
  const tension = tensions[ti];

  document.getElementById('tension-detail').style.display = 'block';
  document.getElementById('tension-detail-title').textContent =
    `${tension.id} — ${tension.name}  |  Pole A: ${tension.pole_a}  /  Pole B: ${tension.pole_b}`;

  const scores = rows.map(r => r.scores[ti]);
  const labels = rows.map(r => r.label);
  const colors = scores.map(s =>
    s === null ? '#ccc' : s < 0 ? '#85B7EB' : s > 0 ? '#F0997B' : '#e0e0e0'
  );

  const barTrace = {
    type: 'bar',
    orientation: 'h',
    x: scores,
    y: labels,
    marker: { color: colors },
    hovertext: rows.map(r => r.notes[ti] || ''),
    hovertemplate: '%{y}: %{x}<br>%{hovertext}<extra></extra>',
  };

  const barHeight = Math.max(200, rows.length * 24 + 60);
  document.getElementById('tension-bar-chart').style.height = barHeight + 'px';

  Plotly.react('tension-bar-chart', [barTrace], {
    margin: { t: 10, b: 30, l: 185, r: 20 },
    xaxis: { range: [-5, 5], zeroline: true, zerolinecolor: '#aaa' },
    yaxis: { autorange: 'reversed', tickfont: { size: 11 } },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
  }, { responsive: true, displayModeBar: false });
}

// --------------------------------------------------------------------------
// Init
// --------------------------------------------------------------------------

async function initHeatmap() {
  const res = await fetch('/api/heatmap-full');
  allData = await res.json();
  renderHeatmap();
}
