/* GoatCounter site: https://gadio2016.goatcounter.com/ */
const GOATCOUNTER_SITE = 'gadio2016';

if (/^[a-z0-9][a-z0-9-]*$/.test(GOATCOUNTER_SITE) && location.protocol !== 'file:') {
  const origin = `https://${GOATCOUNTER_SITE}.goatcounter.com`;
  const tracker = document.createElement('script');
  tracker.dataset.goatcounter = `${origin}/count`;
  tracker.src = 'assets/goatcounter-count.js';
  tracker.async = true;
  document.head.append(tracker);

  fetch(`${origin}/counter/TOTAL.json`, { signal: AbortSignal.timeout(8000) })
    .then(response => {
      if (!response.ok) throw new Error('Counter unavailable');
      return response.json();
    })
    .then(data => {
      if (typeof data.count !== 'string') return;
      document.querySelector('#visit-count-value').textContent = data.count;
      document.querySelector('#visit-count').hidden = false;
    })
    .catch(() => {});
}
