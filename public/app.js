const $ = s => document.querySelector(s);
let category = 'all', nextOffset = 0, loading = false, requestNumber = 0, currentDay = '';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const categoryName = item => item.categoryId === '13' ? 'gadio' : item.categoryId === '12' ? 'GADIO pro' : item.category;
const duration = seconds => seconds ? `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2,'0')}` : '';
let catalog;
async function staticData(offset, selectedCategory) {
  catalog ??= fetch('data/radios-all.json', {cache:'no-cache'}).then(r => { if (!r.ok) throw new Error('Data unavailable'); return r.json(); }).catch(e => {catalog = null; throw e;});
  const snapshot = await catalog;
  const today = new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const [year,month,day] = today.split('-').map(Number);
  const oldYear = year - 10;
  const oldDay = Math.min(day,new Date(Date.UTC(oldYear,month,0)).getUTCDate());
  const date = `${oldYear}-${String(month).padStart(2,'0')}-${String(oldDay).padStart(2,'0')}`;
  const cutoff = Date.UTC(oldYear,month-1,oldDay+1) / 1000 - 8*3600 - 1;
  const rows = snapshot.items.filter(i => i.publishedTimestamp <= cutoff && (selectedCategory === 'all' || i.categoryId === selectedCategory)).sort((a,b)=>b.publishedTimestamp-a.publishedTimestamp);
  return {today,date,items:rows.slice(offset,offset+21),hasMore:rows.length>offset+21,nextOffset:offset+21};
}
function card(item, featured) {
  return `<article class="episode${featured ? ' featured' : ''}"><div class="episode-meta"><time datetime="${item.date}">${item.date}</time><span>${esc(categoryName(item))}${item.vol ? ' vol.' + esc(item.vol) : ''}</span></div><a class="cover" href="${esc(item.url)}" target="_blank" rel="noopener" aria-label="收听：${esc(item.title)}"><img src="${esc(item.image)}" alt="${esc(item.title)}" ${featured ? 'fetchpriority="high"' : 'loading="lazy"'}><span class="audio-icon" aria-hidden="true">▶</span><span class="duration">${duration(item.duration)}</span></a><h2><a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.title)}</a></h2><p>${esc(item.description)}</p></article>`;
}
function imageFallbacks() {
  document.querySelectorAll('img').forEach(img => { img.onerror = () => { img.parentElement.classList.add('image-failed'); img.alt = '节目封面暂不可用'; }; });
}
async function load(reset = false) {
  if (loading && !reset) return;
  const number = ++requestNumber;
  loading = true;
  $('#more').disabled = true;
  if (reset) { nextOffset = 0; $('#episodes').innerHTML = ''; $('#status').hidden = false; $('#status').textContent = '正在调谐十年前的电波…'; $('#more').hidden = true; }
  try {
    let data;
    if (window.GADIO_STATIC) data = await staticData(nextOffset,category);
    else {
      const response = await fetch(`/api/radios?offset=${nextOffset}&category=${category}`, {signal: AbortSignal.timeout(25000)});
      data = await response.json();
      if (!response.ok) throw new Error(data.error);
    }
    if (number !== requestNumber) return;
    currentDay = data.today;
    $('#episodes').insertAdjacentHTML('beforeend', data.items.map((item, i) => card(item, reset && i === 0)).join(''));
    if (reset) $('#rewind').innerHTML = data.items.slice(3,6).map(item => `<a class="rewind-item" href="${esc(item.url)}" target="_blank" rel="noopener"><img src="${esc(item.image)}" alt="${esc(item.title)}" loading="lazy"><p>${esc(item.title)}</p><small>${item.date} · ${esc(categoryName(item))}</small></a>`).join('');
    $('#status').hidden = data.items.length > 0 || !reset;
    if (!data.items.length && reset) $('#status').textContent = '这个栏目在十年前的今天，还没有可收听的节目。';
    nextOffset = data.nextOffset;
    $('#more').hidden = !data.hasMore;
    $('#more').innerHTML = '更多节目 <span>↓</span>';
    imageFallbacks();
  } catch (error) {
    if (number !== requestNumber) return;
    $('#status').hidden = false;
    $('#status').innerHTML = '电波暂时中断，请稍后再试。<button id="retry">重新连接</button>';
    $('#retry').onclick = () => load(reset);
  } finally {
    if (number === requestNumber) { loading = false; $('#more').disabled = false; }
  }
}
document.querySelectorAll('[data-category]').forEach(button => button.addEventListener('click', () => {
  category = button.dataset.category;
  document.querySelectorAll('.filters button').forEach(b => { b.classList.toggle('selected',b.dataset.category === category); b.setAttribute('aria-pressed',String(b.dataset.category === category)); });
  load(true);
}));
$('#more').onclick = () => load();
function checkDay() {
  const today = new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  if (!document.hidden && !loading && currentDay && today !== currentDay) load(true);
}
document.addEventListener('visibilitychange',checkDay);
setInterval(checkDay,60000);
load(true);
