// Contribution heatmap with a spike-proof colour scale.
//
// GitHub's own calendar shades days relative to the busiest day, so a few
// exceptionally heavy days push everything else into the faintest green.
// This one ranks days instead: the shade thresholds are the quartiles of the
// days that had any contributions, so a typical active day lands mid-scale no
// matter how big the outliers are.
//
// usage: node render-heatmap.mjs <user> [outDir] [year]
//   writes heatmap-dark.svg and heatmap-light.svg into outDir (default ".")
//   year defaults to the last 12 months, like the profile graph.

import fs from 'node:fs'
import path from 'node:path'

const [user, outDir = '.', yearArg] = process.argv.slice(2)
if (!user) { console.error('usage: node render-heatmap.mjs <user> [outDir] [year]'); process.exit(1) }

const THEMES = {
  dark: {
    bg: '#0d1117', text: '#8b949e', title: '#e6edf3', border: '#30363d',
    levels: ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353'],
  },
  light: {
    bg: '#ffffff', text: '#57606a', title: '#1f2328', border: '#d0d7de',
    levels: ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'],
  },
}

async function fetchDays() {
  let url = `https://github.com/users/${user}/contributions`
  if (yearArg) url += `?from=${yearArg}-01-01&to=${yearArg}-12-31`
  const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
  if (!res.ok) throw new Error(`GET ${url} -> ${res.status}`)
  const html = await res.text()

  // Each <td data-date id=...> has a <tool-tip for=id> that carries the count.
  const dateById = new Map()
  for (const m of html.matchAll(/<td\b[^>]*>/g)) {
    const date = m[0].match(/data-date="([^"]+)"/)?.[1]
    const id = m[0].match(/\bid="([^"]+)"/)?.[1]
    if (date && id) dateById.set(id, date)
  }
  const days = new Map([...dateById.values()].map(d => [d, 0]))
  for (const m of html.matchAll(/<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)<\/tool-tip>/g)) {
    const date = dateById.get(m[1])
    const n = m[2].match(/^([\d,]+) contribution/)
    if (date && n) days.set(date, Number(n[1].replace(/,/g, '')))
  }
  if (!days.size) throw new Error('no days parsed -- GitHub changed the calendar markup?')
  return [...days].sort(([a], [b]) => a.localeCompare(b)).map(([date, count]) => ({ date, count }))
}

// Thresholds = quartiles of the non-zero days, so each green gets ~a quarter
// of the active days. Spikes only ever affect the top bucket.
function thresholds(days) {
  const v = days.map(d => d.count).filter(Boolean).sort((a, b) => a - b)
  if (!v.length) return [1, 1, 1]
  const q = p => v[Math.min(v.length - 1, Math.floor(p * v.length))]
  const t = [q(0.25), q(0.5), q(0.75)]
  // keep them strictly increasing so every level is reachable
  for (let i = 1; i < t.length; i++) if (t[i] <= t[i - 1]) t[i] = t[i - 1] + 1
  return t
}

const level = (n, t) => (n === 0 ? 0 : n <= t[0] ? 1 : n <= t[1] ? 2 : n <= t[2] ? 3 : 4)

function render(days, theme) {
  const th = THEMES[theme]
  const t = thresholds(days)
  const CELL = 11, GAP = 3, STEP = CELL + GAP
  const LEFT = 34, TOP = 44
  const first = new Date(days[0].date + 'T00:00:00Z')
  const startDow = first.getUTCDay()
  const weeks = Math.ceil((startDow + days.length) / 7)
  const W = LEFT + weeks * STEP + 12, H = TOP + 7 * STEP + 34
  const total = days.reduce((s, d) => s + d.count, 0)
  const active = days.filter(d => d.count).length
  const fmtDate = d => new Date(d + 'T00:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })

  let cells = '', months = '', lastMonth = -1
  days.forEach((d, i) => {
    const idx = startDow + i, x = LEFT + Math.floor(idx / 7) * STEP, y = TOP + (idx % 7) * STEP
    const lv = level(d.count, t)
    cells += `<rect x="${x}" y="${y}" width="${CELL}" height="${CELL}" rx="2.5" fill="${th.levels[lv]}"${lv ? '' : ` stroke="${th.border}" stroke-opacity=".35"`}><title>${d.count} on ${fmtDate(d.date)}</title></rect>`
    const dt = new Date(d.date + 'T00:00:00Z')
    if (dt.getUTCDate() <= 7 && dt.getUTCMonth() !== lastMonth && idx % 7 === 0) {
      lastMonth = dt.getUTCMonth()
      months += `<text x="${x}" y="${TOP - 8}">${dt.toLocaleString('en', { month: 'short', timeZone: 'UTC' })}</text>`
    }
  })
  const dows = [[1, 'Mon'], [3, 'Wed'], [5, 'Fri']].map(([r, l]) => `<text x="${LEFT - 6}" y="${TOP + r * STEP + 9}" text-anchor="end">${l}</text>`).join('')
  // "Less" (30px) + 5 swatches + "More" (~28px), right-aligned with a 14px margin
  const lx = W - 14 - 28 - 5 * STEP - 30
  const legend = th.levels.map((c, i) => `<rect x="${lx + 30 + i * STEP}" y="${H - 22}" width="${CELL}" height="${CELL}" rx="2.5" fill="${c}"/>`).join('')
  const range = ['0', `1–${t[0]}`, `${t[0] + 1}–${t[1]}`, `${t[1] + 1}–${t[2]}`, `${t[2] + 1}+`]

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" font-size="10" fill="${th.text}">
<rect width="${W}" height="${H}" rx="8" fill="${th.bg}" stroke="${th.border}"/>
<text x="${LEFT}" y="20" font-size="13" font-weight="600" fill="${th.title}">${total.toLocaleString('en')} contributions · ${active} active days</text>
${months}${dows}${cells}
<text x="${LEFT}" y="${H - 13}">Shades by rank among active days, not by the busiest day</text>
<text x="${lx}" y="${H - 13}">Less</text>${legend}<text x="${lx + 30 + 5 * STEP + 2}" y="${H - 13}">More</text>
<desc>Levels: ${range.join(' | ')}</desc>
</svg>
`
}

const days = await fetchDays()
fs.mkdirSync(outDir, { recursive: true })
for (const theme of Object.keys(THEMES)) fs.writeFileSync(path.join(outDir, `heatmap-${theme}.svg`), render(days, theme))
const t = thresholds(days)
console.log(`${days.length} days, ${days.filter(d => d.count).length} active, max ${Math.max(...days.map(d => d.count))}, levels 1–${t[0]} | ${t[0] + 1}–${t[1]} | ${t[1] + 1}–${t[2]} | ${t[2] + 1}+`)
