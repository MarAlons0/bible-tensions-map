// Shared tension utilities — loaded on every page via base.html

function scoreToColor(score) {
  if (score === null) return '#ccc';
  if (score < 0) return '#85B7EB';
  if (score > 0) return '#F0997B';
  return '#e0e0e0';
}

function scoreLabel(score) {
  if (score === null) return 'n/a';
  return (score > 0 ? '+' : '') + score;
}
