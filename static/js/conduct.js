async function loadConduct(catId) {
  const res = await fetch(`/api/conduct/${catId}`);
  const data = await res.json();

  const container = document.getElementById('conduct-entries');
  if (!data.entries.length) {
    container.innerHTML = '<p class="empty-state">No entries for this category.</p>';
    return;
  }

  container.innerHTML = data.entries.map(entry => `
    <div class="conduct-entry-row">
      <div class="conduct-entry-header">
        <a href="/book/${entry.book_id}" class="conduct-book-link">${entry.book_name}</a>
        <span class="tag">${entry.section || ''}</span>
        ${entry.dating ? `<span class="tag tag-dating">${entry.dating}</span>` : ''}
      </div>
      <p class="conduct-entry-text">${entry.description}</p>
    </div>
  `).join('');
}

function initConduct(firstCat) {
  loadConduct(firstCat);

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadConduct(btn.dataset.cat);
    });
  });
}
