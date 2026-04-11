// Color palette — alternates between blue and coral families
const WC_COLORS = [
  '#0C447C', '#1565C0', '#1976D2', '#0288D1', '#0277BD',
  '#A0320A', '#C62828', '#AD1457', '#6A1E8A', '#B45309',
  '#2E7D32', '#00695C', '#37474F', '#4E342E', '#283593',
];

function wcColor() {
  return WC_COLORS[Math.floor(Math.random() * WC_COLORS.length)];
}

function buildBreadcrumb(testament, section, bookName) {
  const parts = ['Full Bible'];
  if (testament) parts.push(testament);
  if (section)   parts.push(section);
  if (bookName)  parts.push(bookName);
  return parts.join(' › ');
}

async function fetchAndRender(testament, section, bookId, bookName) {
  const params = new URLSearchParams();
  if (bookId)   params.set('book', bookId);
  else if (section)   params.set('section', section);
  else if (testament) params.set('testament', testament);

  const res  = await fetch('/api/wordcloud?' + params);
  const data = await res.json();

  document.getElementById('wc-breadcrumb').textContent =
    buildBreadcrumb(testament, section, bookName);

  const canvas  = document.getElementById('wc-canvas');
  const empty   = document.getElementById('wc-empty');
  const legend  = document.getElementById('wc-legend');

  if (!data.words || data.words.length < 3) {
    canvas.style.display = 'none';
    empty.style.display  = 'block';
    legend.innerHTML = '';
    return;
  }

  canvas.style.display = 'block';
  empty.style.display  = 'none';

  // Size canvas to its container
  const wrapper = canvas.parentElement;
  canvas.width  = wrapper.clientWidth  || 800;
  canvas.height = Math.max(420, Math.min(620, window.innerHeight * 0.55));

  // Scale weight to a reasonable font range
  const maxCount = data.words[0][1];
  const minCount = data.words[data.words.length - 1][1];
  const range    = Math.max(maxCount - minCount, 1);

  // Assign consistent colors per word (stable across re-renders)
  const colorMap = {};
  data.words.forEach(([word]) => {
    if (!colorMap[word]) colorMap[word] = WC_COLORS[Object.keys(colorMap).length % WC_COLORS.length];
  });

  WordCloud(canvas, {
    list: data.words,
    gridSize: Math.round(canvas.width / 60),
    weightFactor: size => {
      const norm = (size - minCount) / range;   // 0..1
      return Math.round(14 + norm * (canvas.width / 8));
    },
    fontFamily: 'system-ui, sans-serif',
    color: (word) => colorMap[word] || wcColor(),
    rotateRatio: 0.25,
    rotationSteps: 2,
    backgroundColor: '#f8f8f6',
    shrinkToFit: true,
    drawOutOfBound: false,
  });

  // Top-10 word legend
  legend.innerHTML = '<span class="wc-legend-label">Top words: </span>' +
    data.words.slice(0, 12).map(([w, n]) =>
      `<span class="wc-pill" style="background:${colorMap[w]}">${w} <em>${n}</em></span>`
    ).join('');
}

function initWordCloud() {
  const testamentEl = document.getElementById('wc-testament');
  const sectionEl   = document.getElementById('wc-section');
  const bookEl      = document.getElementById('wc-book');

  function getSelectedBookName() {
    const opt = bookEl.options[bookEl.selectedIndex];
    return opt && opt.value ? opt.text : '';
  }

  function render() {
    fetchAndRender(
      testamentEl.value,
      sectionEl.value,
      bookEl.value,
      getSelectedBookName()
    );
  }

  // Testament change → filter section and book dropdowns
  testamentEl.addEventListener('change', () => {
    const t = testamentEl.value;

    // Show/hide section optgroups
    document.getElementById('ot-section-group').style.display =
      (!t || t === 'Old Testament') ? '' : 'none';
    document.getElementById('ap-section-group').style.display =
      (!t || t === 'Apocrypha') ? '' : 'none';
    document.getElementById('nt-section-group').style.display =
      (!t || t === 'New Testament') ? '' : 'none';

    sectionEl.value   = '';
    sectionEl.disabled = !t;
    bookEl.value      = '';
    bookEl.disabled   = true;

    // Show/hide book options
    Array.from(bookEl.options).forEach(opt => {
      if (!opt.value) return;
      opt.style.display = (!t || opt.dataset.testament === t) ? '' : 'none';
    });

    render();
  });

  // Section change → filter book dropdown
  sectionEl.addEventListener('change', () => {
    const s = sectionEl.value;
    const t = testamentEl.value;

    bookEl.value   = '';
    bookEl.disabled = !s;

    Array.from(bookEl.options).forEach(opt => {
      if (!opt.value) return;
      const matchT = !t || opt.dataset.testament === t;
      const matchS = !s || opt.dataset.section   === s;
      opt.style.display = (matchT && matchS) ? '' : 'none';
    });

    render();
  });

  // Book change
  bookEl.addEventListener('change', render);

  // Initial render
  render();
}
