/* FormProof input stage — browser engine.
   Same algorithms as formproof_input (Python): text_rules, requirements, sketch matcher, build_spec
   for the request-dependent parts, fem.judge_constraints. Geometry-dependent results (CAD, drawing,
   FEM of the 1st design) are precomputed by app/artifact/build.py for every template x bar diameter.
   Runs in the browser and in node (parity tests: app/artifact/test_parity.py). */
(function (root) {
'use strict';
const FP = {};
let T = null;                       // tables.json
FP.init = tables => { T = tables; FP.T = T; prepRefs(); };

/* ------------------------------------------------------------------ python-compatible formatting */
const pyf = x => (Number.isInteger(x) ? x.toFixed(1) : String(x));            // str(float)
const fx = (x, n) => x.toFixed(n);                                              // f"{x:.nf}"
const fe = (x, n) => { const s = x.toExponential(n); return s.replace(/e([+-])(\d)$/, 'e$10$2'); };   // f"{x:.ne}"
const fg = x => String(+x.toPrecision(6));                                      // f"{x:g}" (no exponent range here)
const fsign0 = x => (x >= 0 ? '+' : '-') + Math.abs(x).toFixed(0);              // f"{x:+.0f}"
const round = (x, n) => +x.toFixed(n);
const clone = o => JSON.parse(JSON.stringify(o));
FP.pyf = pyf; FP.round = round;

/* ------------------------------------------------------------------ text rules (text_rules.py) */
FP.parseText = function (text) {
  const t = text || '';
  const params = {}, fired = [];
  for (const r of T.rules) {
    if (new RegExp(r.rx, 'i').test(t)) {
      for (const [k, v] of Object.entries(r.effect)) {
        if (k in params && params[k] !== v) continue;
        params[k] = v;
      }
      fired.push({rule: r.id, effect: r.effect, why: r.why});
    }
  }
  let m = t.match(/(\d{2}(?:\.\d)?)\s*mm?\s*(?:핸들|바|클램프)|(?:핸들|바|클램프)[^\d]{0,6}(\d{2}(?:\.\d)?)/);
  if (m) {
    const d = parseFloat(m[1] || m[2]);
    if (d >= 20 && d <= 40) {
      params.bar_d = d;
      fired.push({rule: 'bar_explicit', effect: {bar_d: d}, why: `핸들 직경 ${pyf(d)} mm 직접 입력`});
    }
  }
  m = t.match(/(\d{3})\s*g/);
  if (m && +m[1] >= 100 && +m[1] <= 400) {
    params.phone_mass_kg = +m[1] / 1000;
    fired.push({rule: 'phone_mass_explicit', effect: {phone_mass_kg: params.phone_mass_kg}, why: '폰 무게 직접 입력'});
  }
  const reqs = FP.detectRequirements(t);
  if (reqs.length) {
    params.requirements = reqs;
    for (const r of reqs) {
      const L = T.requirements[r];
      fired.push({rule: 'req_' + r, effect: {requirement: r}, why: L.name + ' → ' + L.physics});
    }
  }
  const hint = {};
  for (const h of T.shape_hints) {
    if (new RegExp(h.rx).test(t)) {
      Object.assign(hint, h.effect);
      fired.push({rule: 'shape_' + h.id, effect: h.effect, why: '스케치가 없을 때 템플릿 선택에 사용'});
    }
  }
  const questions = [];
  if (!('phone' in params) && !('phone_mass_kg' in params)) questions.push('어떤 폰을 올리나요? (기본: 폰 200 g + 클램프 50 g 가정)');
  if (!('bar_d' in params)) questions.push('핸들바 굵기(클램프 위치 직경)는? (기본: 31.8 mm)');
  if (!('road' in params)) questions.push('주로 달리는 길은? (기본: 자갈길 기준으로 보수 설계)');
  return {params, shape_hint: hint, fired, questions};
};

FP.detectRequirements = text => Object.keys(T.requirements).filter(k => new RegExp(T.requirements[k].triggers).test(text || ''));

FP.templateFromHint = function (hint) {
  const tpls = T.templates;
  if (!hint || !Object.keys(hint).length) return tpls[0].id;
  const want = Object.assign({arm: T.default.arm, pad_x0: 80.0, pad_z0: 16.0}, hint);
  const dist = t => {
    const p = Object.assign({arm: T.default.arm}, t.params);
    return Math.abs(p.pad_x0 - want.pad_x0) / 40 + Math.abs(p.pad_z0 - want.pad_z0) / 20
      + (p.arm === want.arm ? 0 : ('arm' in hint ? 1.5 : 0.3));
  };
  let best = tpls[0], bd = dist(best);
  for (const t of tpls.slice(1)) { const d = dist(t); if (d < bd) { best = t; bd = d; } }
  return best.id;
};

FP.nearestBar = d => T.bars.reduce((a, b) => (Math.abs(b - d) < Math.abs(a - d) ? b : a));

/* ------------------------------------------------------------------ image helpers (scipy.ndimage subset) */
// numpy.round: half to even
const rint = x => { const f = Math.floor(x), d = x - f; return d > 0.5 ? f + 1 : d < 0.5 ? f : (f % 2 === 0 ? f : f + 1); };

function dilate(img, w, h, it) {            // binary_dilation, cross structure, border 0
  let a = img;
  for (let k = 0; k < it; k++) {
    const b = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x;
      b[i] = a[i] || (x > 0 && a[i - 1]) || (x < w - 1 && a[i + 1]) || (y > 0 && a[i - w]) || (y < h - 1 && a[i + w]) ? 1 : 0;
    }
    a = b;
  }
  return a;
}
function erode(img, w, h, it) {             // binary_erosion, cross structure, border 0
  let a = img;
  for (let k = 0; k < it; k++) {
    const b = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x;
      b[i] = a[i] && x > 0 && a[i - 1] && x < w - 1 && a[i + 1] && y > 0 && a[i - w] && y < h - 1 && a[i + w] ? 1 : 0;
    }
    a = b;
  }
  return a;
}

function plot(ux, uy, n, w, h, width) {     // sketch._plot
  const img = new Uint8Array(w * h);
  for (let i = 0; i < n; i++) {
    const c = rint(ux[i]), r = rint(h - 1 - uy[i]);
    if (c >= 0 && c < w && r >= 0 && r < h) img[r * w + c] = 1;
  }
  return width > 1 ? dilate(img, w, h, Math.floor(width / 2)) : img;
}

function label(mask, w, h, conn8) {          // connected components, labels in raster order of first pixel
  const lab = new Int32Array(w * h); let n = 0;
  const stack = [];
  for (let s = 0; s < w * h; s++) {
    if (!mask[s] || lab[s]) continue;
    n++; lab[s] = n; stack.push(s);
    while (stack.length) {
      const i = stack.pop(), x = i % w, y = (i - x) / w;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        if (!conn8 && dx && dy) continue;
        const X = x + dx, Y = y + dy;
        if (X < 0 || Y < 0 || X >= w || Y >= h) continue;
        const j = Y * w + X;
        if (mask[j] && !lab[j]) { lab[j] = n; stack.push(j); }
      }
    }
  }
  return {lab, n};
}

// skimage.morphology.skeletonize (Zhang-Suen, skimage's LUT)
const SKEL_LUT = [0,0,0,1,0,0,1,3,0,0,3,1,1,0,1,3,0,0,0,0,0,0,0,0,2,0,2,0,3,0,3,3,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,3,0,2,2,
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,2,0,0,0,2,0,0,0,3,0,0,0,0,0,0,0,3,0,0,0,3,0,2,0,
  0,0,3,1,0,0,1,3,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
  2,3,1,3,0,0,1,3,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,0,1,0,0,0,1,0,0,0,0,0,0,0,0,3,3,0,1,0,0,0,0,2,2,0,0,2,0,0,0];
function skeletonize(img, w, h) {
  const W = w + 2, H = h + 2;
  let sk = new Uint8Array(W * H);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) sk[(y + 1) * W + x + 1] = img[y * w + x];
  const cl = sk.slice();
  let removed = true;
  while (removed) {
    removed = false;
    for (let pass = 0; pass < 2; pass++) {
      const first = pass === 0;
      for (let r = 1; r < H - 1; r++) for (let c = 1; c < W - 1; c++) {
        const i = r * W + c;
        if (!sk[i]) continue;
        const nb = SKEL_LUT[sk[i - W - 1] + 2 * sk[i - W] + 4 * sk[i - W + 1] + 8 * sk[i + 1] + 16 * sk[i + W + 1]
          + 32 * sk[i + W] + 64 * sk[i + W - 1] + 128 * sk[i - 1]];
        if (nb === 0) continue;
        if (nb === 3 || (nb === 1 && first) || (nb === 2 && !first)) { cl[i] = 0; removed = true; }
      }
      sk.set(cl);
    }
  }
  const out = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) out[y * w + x] = sk[(y + 1) * W + x + 1];
  return out;
}

function circlePerimeter(rad) {             // skimage.draw.circle_perimeter(0, 0, r), bresenham, with duplicates
  const rr = [], cc = [];
  let c = 0, r = rad, d = 3 - 2 * rad;
  while (r >= c) {
    rr.push(r, -r, r, -r, c, -c, c, -c);
    cc.push(c, c, -c, -c, r, r, -r, -r);
    if (d < 0) d += 4 * c + 6; else { d += 4 * (c - r) + 10; r -= 1; }
    c += 1;
  }
  return [rr, cc];
}

function prominentPeaks(acc, rows, cols, md) {   // skimage.feature.peak._prominent_peaks, min distance md
  let mx = 0;
  for (let i = 0; i < acc.length; i++) if (acc[i] > mx) mx = acc[i];
  const thr = 0.5 * mx;
  const t1 = new Float64Array(rows * cols), img_max = new Float64Array(rows * cols);
  for (let x = 0; x < cols; x++) for (let y = 0; y < rows; y++) {
    let m = 0;
    for (let k = -md; k <= md; k++) { const Y = y + k; if (Y >= 0 && Y < rows) { const v = acc[Y * cols + x]; if (v > m) m = v; } }
    t1[y * cols + x] = m;
  }
  for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
    let m = 0;
    for (let k = -md; k <= md; k++) { const X = x + k; if (X >= 0 && X < cols) { const v = t1[y * cols + X]; if (v > m) m = v; } }
    img_max[y * cols + x] = m;
  }
  const mask = new Uint8Array(rows * cols);
  for (let i = 0; i < mask.length; i++) mask[i] = (acc[i] === img_max[i] && acc[i] > thr) ? 1 : 0;
  const {lab, n} = label(mask, cols, rows, true);
  if (!n) return [];
  const sy = new Float64Array(n + 1), sx = new Float64Array(n + 1), cnt = new Float64Array(n + 1), imax = new Float64Array(n + 1).fill(-Infinity);
  for (let i = 0; i < lab.length; i++) {
    const L = lab[i]; if (!L) continue;
    const x = i % cols, y = (i - x) / cols;
    sy[L] += y; sx[L] += x; cnt[L]++;
    if (img_max[i] > imax[L]) imax[L] = img_max[i];
  }
  const order = [];
  for (let L = 1; L <= n; L++) order.push(L);
  order.sort((a, b) => imax[a] - imax[b] || a - b);        // stable ascending ...
  order.reverse();                                          // ... then reversed (python sorted()[::-1])
  const peaks = [];
  for (const L of order) {
    const yi = rint(sy[L] / cnt[L]), xi = rint(sx[L] / cnt[L]);
    const a = img_max[yi * cols + xi];
    if (!(a > thr)) continue;
    for (let dy = -md; dy <= md; dy++) for (let dx = -md; dx <= md; dx++) {
      let Y = yi + dy, X = xi + dx;
      if (!(Y > 0 && Y < rows)) continue;
      if (X < 0) { Y = rows - Y; X += cols; } else if (X >= cols) { Y = rows - Y; X -= cols; }
      img_max[Y * cols + X] = 0;
    }
    peaks.push([a, xi, yi]);
  }
  return peaks;
}

function findRing(px, py, n) {               // sketch.find_ring
  let lox = Infinity, loy = Infinity, hix = -Infinity, hiy = -Infinity;
  for (let i = 0; i < n; i++) { lox = Math.min(lox, px[i]); hix = Math.max(hix, px[i]); loy = Math.min(loy, py[i]); hiy = Math.max(hiy, py[i]); }
  const span = Math.max(hix - lox, hiy - loy, 1e-9), s = 240.0 / span;
  const w = Math.trunc((hix - lox) * s) + 17, h = Math.trunc((hiy - loy) * s) + 17;
  const ux = new Float64Array(n), uy = new Float64Array(n);
  for (let i = 0; i < n; i++) { ux[i] = (px[i] - lox) * s + 8; uy[i] = (py[i] - loy) * s + 8; }
  let img = plot(ux, uy, n, w, h, 1);
  img = erode(dilate(img, w, h, 2), w, h, 2);
  img = dilate(skeletonize(img, w, h), w, h, 1);
  const ex = [], ey = [];                    // np.nonzero order: rows then cols
  for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) if (img[r * w + c]) { ex.push(r); ey.push(c); }
  let peaks = [];
  const acc = new Float64Array(w * h);
  for (let rad = 6; rad < 60; rad++) {
    const [cr, cc] = circlePerimeter(rad), nc = cr.length, inc = 1.0 / nc;
    acc.fill(0);
    for (let p = 0; p < ex.length; p++) {
      const x = ex[p], y = ey[p];
      for (let c = 0; c < nc; c++) {
        const tx = cr[c] + x, ty = cc[c] + y;
        if (tx >= 0 && tx < h && ty >= 0 && ty < w) acc[tx * w + ty] += inc;
      }
    }
    for (const [a, xi, yi] of prominentPeaks(acc, h, w, 3)) peaks.push([a, xi, yi, rad]);
  }
  if (!peaks.length) return null;
  peaks = peaks.map((p, i) => [...p, i]).sort((A, B) => B[0] - A[0] || B[4] - A[4]);   // argsort(accum)[::-1]
  const keep = [], nb = new Uint8Array(peaks.length);
  let npts = 0;
  for (let i = 0; i < peaks.length; i++) {
    if (npts >= 20) { nb[i] = 1; continue; }
    if (nb[i]) continue;
    for (let j = i + 1; j < peaks.length; j++)
      if (Math.abs(peaks[j][1] - peaks[i][1]) <= 3 && Math.abs(peaks[j][2] - peaks[i][2]) <= 3) nb[j] = 1;
    npts++;
  }
  for (let i = 0; i < peaks.length; i++) if (!nb[i]) keep.push(peaks[i]);
  let arc = keep.map(p => p[0] * p[3] * (p[0] >= 0.55 ? 1 : 0));
  if (Math.max(...arc) <= 0) arc = keep.map(p => p[0] * p[3]);
  let best = 0;
  for (let i = 1; i < arc.length; i++) if (arc[i] > arc[best]) best = i;
  const [frac, bcx, bcy, brad] = keep[best];
  let cx = (bcx - 8) / s + lox, cy = (h - 1 - bcy - 8) / s + loy, r = brad / s;
  for (const band of [0.15, 0.08]) {       // Kasa circle fit in a narrowing annulus
    let S = [0, 0, 0, 0, 0, 0, 0, 0, 0], B = [0, 0, 0], m = 0;
    for (let i = 0; i < n; i++) {
      const d = Math.hypot(px[i] - cx, py[i] - cy);
      if (Math.abs(d - r) > band * r) continue;
      m++;
      const a = [2 * px[i], 2 * py[i], 1], b = px[i] * px[i] + py[i] * py[i];
      for (let u = 0; u < 3; u++) { B[u] += a[u] * b; for (let v = 0; v < 3; v++) S[u * 3 + v] += a[u] * a[v]; }
    }
    if (m < 12) break;
    const sol = solve3(S, B);
    if (!sol) break;
    cx = sol[0]; cy = sol[1]; r = Math.sqrt(sol[2] + cx * cx + cy * cy);
  }
  return {cx, cy, r, score: frac};
}
function solve3(A, b) {
  const M = [[A[0], A[1], A[2], b[0]], [A[3], A[4], A[5], b[1]], [A[6], A[7], A[8], b[2]]];
  for (let i = 0; i < 3; i++) {
    let p = i;
    for (let k = i + 1; k < 3; k++) if (Math.abs(M[k][i]) > Math.abs(M[p][i])) p = k;
    if (Math.abs(M[p][i]) < 1e-300) return null;
    [M[i], M[p]] = [M[p], M[i]];
    for (let k = 0; k < 3; k++) if (k !== i) { const f = M[k][i] / M[i][i]; for (let j = i; j < 4; j++) M[k][j] -= f * M[i][j]; }
  }
  return [M[0][3] / M[0][0], M[1][3] / M[1][1], M[2][3] / M[2][2]];
}

/* ---- features on the comparison canvas */
function edt(img, w, h) {                    // distance to the nearest ink pixel (distance_transform_edt(img < .5))
  const INF = 1e20, f = new Float64Array(Math.max(w, h)), d = new Float64Array(Math.max(w, h));
  const v = new Int32Array(Math.max(w, h)), z = new Float64Array(Math.max(w, h) + 1);
  const g = new Float64Array(w * h);
  const dt1 = (len) => {
    let k = 0; v[0] = 0; z[0] = -INF; z[1] = INF;
    for (let q = 1; q < len; q++) {
      let s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
      while (s <= z[k]) { k--; s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]); }
      k++; v[k] = q; z[k] = s; z[k + 1] = INF;
    }
    k = 0;
    for (let q = 0; q < len; q++) { while (z[k + 1] < q) k++; d[q] = (q - v[k]) * (q - v[k]) + f[v[k]]; }
  };
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) f[y] = img[y * w + x] > 0.5 ? 0 : INF;
    dt1(h);
    for (let y = 0; y < h; y++) g[y * w + x] = d[y];
  }
  const out = new Float64Array(w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) f[x] = g[y * w + x];
    dt1(w);
    for (let x = 0; x < w; x++) out[y * w + x] = Math.sqrt(d[x]);
  }
  return out;
}

const reflect = (i, n) => { while (i < 0 || i >= n) i = i < 0 ? -i - 1 : 2 * n - i - 1; return i; };
function corr1d(a, w, h, k, axis) {          // scipy correlate1d, mode reflect, float32 output
  const r = (k.length - 1) / 2, out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let s = 0;
    for (let j = -r; j <= r; j++) s += k[j + r] * (axis === 0 ? a[reflect(y + j, h) * w + x] : a[y * w + reflect(x + j, w)]);
    out[y * w + x] = s;
  }
  return out;
}
const GAUSS1 = (() => { const k = []; let s = 0; for (let x = -4; x <= 4; x++) { const v = Math.exp(-0.5 * x * x); k.push(v); s += v; } return k.map(v => v / s); })();
function orientHist(img, W, H, gx = 4, gy = 3, bins = 8) {
  const b = corr1d(corr1d(img, W, H, GAUSS1, 0), W, H, GAUSS1, 1);
  const sx = corr1d(corr1d(b, W, H, [-1, 0, 1], 1), W, H, [1, 2, 1], 0);
  const sy = corr1d(corr1d(b, W, H, [-1, 0, 1], 0), W, H, [1, 2, 1], 1);
  const hist = new Float64Array(gy * gx * bins);
  const PI = Math.fround(Math.PI);
  for (let y = 0; y < H; y++) {
    const yb = Math.min(Math.floor(y * gy / H), gy - 1);
    for (let x = 0; x < W; x++) {
      const i = y * W + x, mag = Math.fround(Math.hypot(sx[i], sy[i]));
      let a = Math.fround(Math.atan2(sy[i], sx[i]));
      a = Math.fround(a - Math.floor(a / PI) * PI);
      const k = Math.min(Math.trunc(Math.fround(Math.fround(a / PI) * bins)), bins - 1);
      hist[(yb * gx + Math.min(Math.floor(x * gx / W), gx - 1)) * bins + k] += mag;
    }
  }
  let nrm = 0;
  for (const v of hist) nrm += v * v;
  nrm = Math.sqrt(nrm) + 1e-9;
  return hist.map(v => v / nrm);
}
function feat(img) {
  const M = T.matcher, f = new Float32Array(img.length);
  for (let i = 0; i < img.length; i++) f[i] = img[i] ? 1 : 0;
  return {img: f, dt: edt(f, M.W, M.H), hist: orientHist(f, M.W, M.H)};
}
function chamfer(a, dtb, trim = 0.9) {
  const d = [];
  for (let i = 0; i < a.length; i++) if (a[i] > 0.5) d.push(dtb[i]);
  if (!d.length) return 1e3;
  d.sort((x, y) => x - y);
  const n = Math.max(1, Math.trunc(d.length * trim));
  let s = 0;
  for (let i = 0; i < n; i++) s += d[i];
  return s / n;
}

function canonicalMap(px, py, n, cx, cy, radius, mirror) {
  const M = T.matcher, ux = new Float64Array(n), uy = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let x = (px[i] - cx) / radius * M.R_PX; const y = (py[i] - cy) / radius * M.R_PX;
    if (mirror) x = -x;
    ux[i] = x + M.C0[0]; uy[i] = y + M.C0[1];
  }
  return plot(ux, uy, n, M.W, M.H, 2);
}
function bboxMap(px, py, n) {
  const M = T.matcher;
  let lox = Infinity, loy = Infinity, hix = -Infinity, hiy = -Infinity;
  for (let i = 0; i < n; i++) { lox = Math.min(lox, px[i]); hix = Math.max(hix, px[i]); loy = Math.min(loy, py[i]); hiy = Math.max(hiy, py[i]); }
  const sx = Math.max(hix - lox, 1e-9), sy = Math.max(hiy - loy, 1e-9);
  const s = Math.min((M.W - 2 * M.PAD) / sx, (M.H - 2 * M.PAD) / sy);
  const ox = (M.W - s * sx) / 2, oy = (M.H - s * sy) / 2;
  const ux = new Float64Array(n), uy = new Float64Array(n);
  for (let i = 0; i < n; i++) { ux[i] = (px[i] - lox) * s + ox; uy[i] = (py[i] - loy) * s + oy; }
  return plot(ux, uy, n, M.W, M.H, 2);
}

function prepRefs() {
  const M = T.matcher;
  M._refs = {};
  for (const frame of ['ring', 'bbox']) {
    M._refs[frame] = M.refs[frame].map(r => {
      const bytes = typeof atob === 'function' ? Uint8Array.from(atob(r.bits), c => c.charCodeAt(0)) : Uint8Array.from(Buffer.from(r.bits, 'base64'));
      const img = new Uint8Array(M.W * M.H);
      for (let i = 0; i < img.length; i++) img[i] = (bytes[i >> 3] >> (7 - (i & 7))) & 1;
      return Object.assign({t: r.t, phone: r.phone}, feat(img));
    });
  }
}

/* ---- user image -> ink points */
function gaussianSmooth(g, w, h, sigma) {
  const lw = Math.trunc(4 * sigma + 0.5), k = [];
  let s = 0;
  for (let x = -lw; x <= lw; x++) { const v = Math.exp(-0.5 * x * x / (sigma * sigma)); k.push(v); s += v; }
  const kn = k.map(v => v / s);
  const conv = (a, axis) => {                 // mode constant (cval 0), like skimage canny
    const out = new Float64Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      let t = 0;
      for (let j = -lw; j <= lw; j++) {
        const X = axis ? x + j : x, Y = axis ? y : y + j;
        if (X >= 0 && X < w && Y >= 0 && Y < h) t += kn[j + lw] * a[Y * w + X];
      }
      out[y * w + x] = t;
    }
    return out;
  };
  return conv(conv(g, 0), 1);
}
function canny(g, w, h, sigma = 2.0, lo = 0.1, hi = 0.2) {
  const one = new Float64Array(w * h).fill(1);
  const sm = gaussianSmooth(g, w, h, sigma), bl = gaussianSmooth(one, w, h, sigma);
  for (let i = 0; i < sm.length; i++) sm[i] /= bl[i] + 2.220446049250313e-16;
  const at = (x, y) => sm[reflect(y, h) * w + reflect(x, w)];
  const gx = new Float64Array(w * h), gy = new Float64Array(w * h), mag = new Float64Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x;
    gx[i] = (at(x + 1, y - 1) + 2 * at(x + 1, y) + at(x + 1, y + 1)) - (at(x - 1, y - 1) + 2 * at(x - 1, y) + at(x - 1, y + 1));
    gy[i] = (at(x - 1, y + 1) + 2 * at(x, y + 1) + at(x + 1, y + 1)) - (at(x - 1, y - 1) + 2 * at(x, y - 1) + at(x + 1, y - 1));
    mag[i] = Math.hypot(gx[i], gy[i]);
  }
  const nms = new Float64Array(w * h);
  for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
    const i = y * w + x, m = mag[i];
    if (m === 0) continue;
    let a = Math.atan2(gy[i], gx[i]) * 180 / Math.PI; if (a < 0) a += 180;
    let n1, n2;
    if (a < 22.5 || a >= 157.5) { n1 = mag[i - 1]; n2 = mag[i + 1]; }
    else if (a < 67.5) { n1 = mag[i - w - 1]; n2 = mag[i + w + 1]; }
    else if (a < 112.5) { n1 = mag[i - w]; n2 = mag[i + w]; }
    else { n1 = mag[i - w + 1]; n2 = mag[i + w - 1]; }
    if (m >= n1 && m >= n2) nms[i] = m;
  }
  const low = new Uint8Array(w * h);
  for (let i = 0; i < low.length; i++) low[i] = nms[i] >= lo ? 1 : 0;
  const {lab, n} = label(low, w, h, true);
  const strong = new Uint8Array(n + 1);
  for (let i = 0; i < lab.length; i++) if (lab[i] && nms[i] >= hi) strong[lab[i]] = 1;
  const out = new Uint8Array(w * h);
  for (let i = 0; i < lab.length; i++) out[i] = lab[i] && strong[lab[i]] ? 1 : 0;
  return out;
}

FP.looksLikePhoto = (g) => { let m = 0; for (const v of g) if (v > 0.2 && v < 0.8) m++; return m / g.length > 0.15; };

FP.inkPoints = function (g, w, h, photo) {
  let ink;
  if (photo) ink = canny(g, w, h);
  else { ink = new Uint8Array(w * h); for (let i = 0; i < g.length; i++) ink[i] = g[i] < 0.5 ? 1 : 0; }
  const {lab, n} = label(ink, w, h, false);
  const size = new Int32Array(n + 1);
  for (let i = 0; i < lab.length; i++) size[lab[i]]++;
  const px = [], py = [];
  for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
    const L = lab[r * w + c];
    if (L && size[L] >= 6) { px.push(c); py.push(h - 1 - r); }
  }
  if (px.length < 10) throw new Error('no strokes found in the image');
  return {px: Float64Array.from(px), py: Float64Array.from(py), n: px.length};
};

FP.matchPoints = function ({px, py, n}, k = 3) {
  const M = T.matcher;
  const ring = findRing(px, py, n);
  let frame, score, queries = [];
  if (ring && ring.score >= M.ring_min) {
    frame = 'ring'; score = ring.score;
    const rx = new Float64Array(n), ry = new Float64Array(n);
    for (const a of M.rotations) {
      const th = a * Math.PI / 180, co = Math.cos(th), si = Math.sin(th);
      for (let i = 0; i < n; i++) {
        const x = px[i] - ring.cx, y = py[i] - ring.cy;
        rx[i] = x * co - y * si + ring.cx; ry[i] = x * si + y * co + ring.cy;
      }
      for (const m of [false, true]) queries.push({mir: m, rot: a, ...feat(canonicalMap(rx, ry, n, ring.cx, ring.cy, ring.r, m))});
    }
  } else {
    frame = 'bbox'; score = ring ? ring.score : 0;
    const q = bboxMap(px, py, n), f = new Uint8Array(q.length);
    for (let y = 0; y < M.H; y++) for (let x = 0; x < M.W; x++) f[y * M.W + x] = q[y * M.W + (M.W - 1 - x)];
    queries = [{mir: false, rot: 0, ...feat(q)}, {mir: true, rot: 0, ...feat(f)}];
  }
  const best = {};
  for (const q of queries) for (const r of M._refs[frame]) {
    let hd = 0;
    for (let i = 0; i < q.hist.length; i++) hd += (q.hist[i] - r.hist[i]) ** 2;
    const s = 0.5 * (chamfer(q.img, r.dt) + chamfer(r.img, q.dt)) + M.w_hist * Math.sqrt(hd);
    if (!(r.t in best) || s < best[r.t][0]) best[r.t] = [s, q.mir];
  }
  const ranked = Object.entries(best).map(([i, [s, m]]) => [s, +i, m]).sort((A, B) => A[0] - B[0] || A[1] - B[1] || (A[2] - B[2]));
  const s0 = ranked[0][0];
  const cands = ranked.slice(0, k).map(([s, i, m]) => ({id: T.templates[i].id, name: T.templates[i].name, score: round(s, 3), mirrored: m,
    confidence: round(Math.exp(-(s - s0) / 0.5), 3)}));
  return {frame, ring_score: round(score, 2), candidates: cands, ring};
};

FP.matchGray = (g, w, h, photo = false, k = 3) => FP.matchPoints(FP.inkPoints(g, w, h, photo), k);

/* ------------------------------------------------------------------ spec for this request (bike_mount.build_spec) */
FP.resolveParams = function (tplId, parsedParams) {
  const tpl = T.templates.find(t => t.id === tplId);
  const p = Object.assign(clone(T.default), clone(tpl.params), clone(parsedParams || {}));
  const asked = p.bar_d;
  p.bar_d = FP.nearestBar(asked);
  return {p, barAsked: asked};
};

FP.buildSpec = function (geo, p, meta, barAsked) {
  const E = T.ev, base = geo.spec, spec = clone(base);
  const g = spec.geometry, Y_SYM = g.y_sym;
  spec.template = Object.assign({id: geo.template, params: clone(p)}, meta || {});
  const known = p.phone in E.PHONES;
  const dims = known ? E.PHONES[p.phone].dims : E.PHONE_DEFAULT_DIMS;
  const [cogx, z_top] = g.phone.cog;
  spec.regions = base.regions.filter(r => r.name !== 'phone_sweep');
  if (p.requirements.includes('free_angle')) {
    const e_j = p.phone_clamp_t + dims[2] / 2;
    spec.regions.push({name: 'phone_sweep', role: 'keepout', minus: ['post'],
      shape: [{phone_sweep: {joint: [cogx, Y_SYM, z_top - e_j], H: dims[0], W: dims[1], D: dims[2], clamp_t: p.phone_clamp_t,
        margin: p.angle_margin, tilt_lo: p.angle_tilt[0], tilt_hi: p.angle_tilt[1], rot_deg: 360.0, rot_step: 15.0, tilt_step: 4.0}}],
      why: "요구 '화면 각도 자유롭게': 폰이 360° 회전·기울기 범위에서 지나가는 공간. 최적화 단계에서 비울 곳"});
  }
  const mat = E.MATERIALS[p.material];
  let road = E.ROADS[p.road], roadStatus = 'cited';
  if (!road) { road = E.ROADS[E.ROAD_FALLBACK]; roadStatus = 'fallback'; }
  const sf = p.safety_factor || E.FACTORS.safety_factor;
  const tmax = E.FACTORS.t_max;
  const f_min = road.f_hi / Math.sqrt(1.0 - 1.0 / tmax);
  let m_phone, phone_src, phone_name;
  if (known) { const ph = E.PHONES[p.phone]; m_phone = ph.mass; phone_src = ph.source; phone_name = ph.name; }
  else { m_phone = E.PHONE_DEFAULT_MASS; phone_src = 'team_v7'; phone_name = '기종 미지정(200 g 가정)'; }
  if (p.phone_mass_kg) { m_phone = p.phone_mass_kg; phone_src = 'user'; phone_name = '사용자 입력 폰'; }
  const m_total = m_phone + E.PHONE_CLAMP_MASS;
  g.holder = clone(geo.cad[known ? p.phone : 'default'].holder);
  g.phone = {name: phone_name, H: dims[0], W: dims[1], D: dims[2], mass_kg: round(m_total, 4), cog: [cogx, z_top],
    clamp_t: p.phone_clamp_t, dims_source: known ? phone_src : 'assumed'};
  const pm = spec.point_masses[0];
  pm.mass_kg = round(m_total, 4);
  pm.source = [phone_src, 'assumed:clamp_50g'];
  pm.note = `${phone_name} ${fx(m_phone * 1e3, 0)} g + 폰 클램프 ${fx(E.PHONE_CLAMP_MASS * 1e3, 0)} g, 클램프 상단에 집중`;
  spec.objective = {type: p.objective};
  spec.finish = {colour: p.colour};
  spec.requirements = [...p.requirements];
  const c = spec.constraints.filter(x => !x.requirement);
  const st = c.find(x => x.id === 'stress'), il = c.find(x => x.id === 'interlayer');
  st.value = round(mat.yield_mpa / sf, 1); st.derivation = `yield ${pyf(mat.yield_mpa)} / SF ${pyf(sf)}`;
  il.value = round(mat.interlayer_mpa / sf, 1); il.derivation = `interlayer ${pyf(mat.interlayer_mpa)} / SF ${pyf(sf)}, 옆으로 눕혀 출력(적층 방향 y)`;
  spec.constraints = c;
  const evk = [mat.source, road.source, 'sdof', 'team_v7', phone_src].filter(k => k in E.SOURCES);
  spec.evidence = {};
  for (const k of [...new Set(evk)].sort()) spec.evidence[k] = E.SOURCES[k];
  spec.assumptions = base.assumptions.slice(0, 5).concat([`안전율 ${pyf(sf)}, 진동 증폭 허용 ${fx(tmax, 2)}배는 선택값`])
    .concat(roadStatus === 'fallback' ? [`요청한 노면('${p.road}')은 측정 근거가 없어 자갈길 값으로 대체(보수적)`] : [])
    .concat(p.include_self_inertia ? [] : ['충격 하중에 거치대 자체 질량 관성 미포함(팀 v7과 동일) — 포함 권장']);
  // requirement conditions (_add_requirement_conditions)
  const req = new Set(p.requirements), ph = g.phone;
  if (req.has('free_angle')) {
    const m = ph.mass_kg, e = (ph.clamp_t + ph.D / 2) / 1000, [lo, hi] = p.angle_tilt;
    const I_p = m * ((ph.H / 1000) ** 2 + (ph.D / 1000) ** 2) / 12 + m * e ** 2;
    const k_req = (2 * Math.PI * f_min) ** 2 * I_p;
    const amax = Math.max(Math.abs(lo), Math.abs(hi));
    const torque = m * road.peak_g * 9.81 * e * Math.sin(amax * Math.PI / 180);
    spec.constraints.push(
      {id: 'pose_clearance', quantity: 'phone_clearance_mm', op: '>=', value: p.angle_margin,
        poses: {rotate_deg: 360, tilt_deg: [lo, hi]}, keep_out_region: 'phone_sweep', requirement: 'free_angle', source: ['assumed:target_range']},
      {id: 'joint_stiffness', quantity: 'joint_rot_stiffness_Nm_per_rad', op: '>=', value: round(k_req, 1),
        derivation: `(2π·${pyf(f_min)})² × I_joint, I_joint = m(H²+D²)/12 + m·e² = ${fe(I_p, 2)} kg·m² (세로, 관절이 폰 뒤 ${fx(e * 1000, 0)} mm)`,
        requirement: 'free_angle', source: ['sdof']},
      {id: 'joint_hold', quantity: 'joint_hold_torque_Nm', op: '>=', value: round(torque, 2),
        derivation: `m·${pyf(road.peak_g)} g·e·sin${fx(amax, 0)}°; 관절축이 폰 무게중심을 지나면 0`,
        requirement: 'free_angle', source: [road.source]});
    spec.assumptions.push(`각도 자유: 360° 회전 + 기울기 ${fsign0(lo)}~${fsign0(hi)}°, 간격 ${fg(p.angle_margin)} mm (목표 선택값)`);
  }
  if (req.has('sun_heat')) {
    spec.constraints.push({id: 'sun_heat', quantity: 'parked_surface_temp_c', op: '<=', value: `HDT(σ_1g) − ${fx(E.SUN.margin_k, 0)}`,
      hdt_table: mat.hdt, colour: p.colour,
      derivation: '햇빛 아래 주차 표면온도(에너지 평형) ≤ 정하중(폰 무게) 응력에서의 열변형온도 − 여유',
      requirement: 'sun_heat', source: [mat.source, 'energy_balance', E.ABSORPTANCE_SOURCE]});
    for (const k of ['energy_balance', E.ABSORPTANCE_SOURCE, 'prusa_asa_blog']) spec.evidence[k] = E.SOURCES[k];
  }
  if (barAsked != null && Math.abs(barAsked - p.bar_d) > 1e-9)
    spec.assumptions.push(`핸들바 Ø${pyf(barAsked)} mm 요청 → 미리 계산된 가장 가까운 규격 Ø${pyf(p.bar_d)} mm 형상 사용(브라우저 버전)`);
  return spec;
};

/* ------------------------------------------------------------------ 1st-design check (fem.evaluate results) */
FP.firstDesignCheck = function (geo, spec, p) {
  const E = T.ev, F = geo.fem;
  const m = spec.point_masses[0].mass_kg;
  let r, interp = false;
  const key = p.phone_mass_kg ? null : (p.phone in E.PHONES ? p.phone : 'default');
  if (key) r = clone(F[key]);
  else {                       // user-stated mass: modal fit 1/f^2 = a m + b, inertial loads ~ m (point mass only)
    interp = true;
    const ks = T.phone_keys, ref = F.default;
    r = clone(ref);
    r.mass_kg = m;
    r.freqs_hz = ref.freqs_hz.map((_, j) => {
      const xs = ks.map(k => F[k].mass_kg), ys = ks.map(k => 1 / F[k].freqs_hz[j] ** 2);
      const mx = xs.reduce((a, b) => a + b) / xs.length, my = ys.reduce((a, b) => a + b) / ys.length;
      let sxy = 0, sxx = 0;
      xs.forEach((x, i) => { sxy += (x - mx) * (ys[i] - my); sxx += (x - mx) ** 2; });
      const a = sxy / sxx, b = my - a * mx;
      return round(1 / Math.sqrt(a * m + b), 1);
    }).sort((x, y) => x - y);
    r.f1_hz = r.freqs_hz[0];
    const k = m / ref.mass_kg;
    for (const n of ['shock_vertical', 'shock_lateral']) {
      const s = ref[n];
      r[n] = {vm_max_mpa: round(s.vm_max_mpa * k, 1), vm_p999_mpa: round(s.vm_p999_mpa * k, 1),
        s_yy_tension_mpa: round(s.s_yy_tension_mpa * k, 1), tip_disp_mm: round(s.tip_disp_mm * k, 3)};
    }
    r.half_model_mass_kg = round(ref.half_model_mass_kg * m / ref.mass_kg, 4);
  }
  delete r.mass_kg; delete r.half_model_mass_kg;
  const ck = {};
  for (const c of spec.constraints) {
    let v;
    if (c.quantity === 'natural_frequency_hz') v = r.f1_hz;
    else if (c.quantity === 'von_mises_max_mpa') v = Math.max(...c.load_cases.map(n => r[n].vm_max_mpa));
    else if (c.quantity === 'layer_normal_tension_mpa') v = Math.max(...c.load_cases.map(n => r[n].s_yy_tension_mpa));
    else continue;
    ck[c.id] = {value: v, limit: `${c.op} ${pyf(c.value)}`, pass: c.op === '>=' ? v >= c.value : v <= c.value};
  }
  r.checks = ck;
  r.pass = Object.values(ck).every(x => x.pass) && r.connected;
  if (interp) r.note = '사용자 입력 폰 무게: 미리 계산한 4가지 무게의 해석값에서 보간(진동수 1/f²–질량 선형, 응력은 질량에 비례)';
  return r;
};

FP.handoffSummary = function (geo, spec, p) {
  const out = [];
  const pk = p.phone in T.ev.PHONES ? p.phone : 'default';
  for (const rid of spec.requirements) {
    const L = T.requirements[rid];
    const item = {id: rid, name: L.name, physics: L.physics, handoff: L.handoff,
      constraints: spec.constraints.filter(c => c.requirement === rid).map(c => ({id: c.id, rule: `${c.quantity} ${c.op} ${typeof c.value === 'number' ? pyf(c.value) : c.value}`, why: c.derivation || ''})),
      warnings: []};
    if (rid === 'free_angle') {
      const ko = geo.keepout[pk];
      item.keepout_elements = ko.elements;
      if (ko.clash) item.warnings.push(`폰이 지나가는 공간이 지켜야 할 부품(클램프·받침)과 ${ko.clash}개 요소에서 겹침 → 최적화 단계에서 관절 높이 또는 받침 위치(도달 거리) 조정 필요`);
    }
    if (rid === 'sun_heat') item.colour = (spec.finish || {}).colour;
    out.push(item);
  }
  return out;
};

/* ------------------------------------------------------------------ report (pipeline.design) */
FP.design = function ({text = '', geo, tplId, how, match, parsed, p, barAsked, input}) {
  const tpl = T.templates.find(t => t.id === tplId), E = T.ev;
  const rep = {input, text: parsed};
  rep.template = {id: tplId, name: tpl.name, desc: tpl.desc, chosen_by: how, match: match || null};
  const spec = FP.buildSpec(geo, p, {name: tpl.name, chosen_by: how}, barAsked);
  const check = FP.firstDesignCheck(geo, spec, p);
  rep.first_design_check = check;
  rep.handoff_requirements = FP.handoffSummary(geo, spec, p);
  const pk = p.phone in E.PHONES ? p.phone : 'default';
  rep.problem = clone(geo.problem);
  rep.problem.keepout = p.requirements.includes('free_angle') ? geo.keepout[pk].elements : 0;
  rep.problem.half_model_mass_kg = round(geo.fem.default.half_model_mass_kg * spec.point_masses[0].mass_kg / geo.fem.default.mass_kg, 4);
  rep.criteria = spec.constraints.map(c => ({id: c.id, rule: `${c.quantity} ${c.op} ${typeof c.value === 'number' ? pyf(c.value) : c.value}`,
    why: c.derivation || '', source: c.source || null, requirement: c.requirement || null}));
  rep.assumptions = spec.assumptions;
  const g = spec.geometry;
  rep.design_vars = {bar_d: g.bar_d, width: g.width, reach: g.mount_hole.x, pad_top: g.pad.z[1], arm: g.arm.style, arm_t: g.arm.t,
    phone: g.phone.name, point_mass_g: Math.round(spec.point_masses[0].mass_kg * 1e3), material: spec.material.name};
  const road = spec.load_cases.find(c => c.type === 'modal'), shock = spec.load_cases.find(c => c.name === 'shock_vertical');
  const sf = p.safety_factor || 1.5;
  rep.summary = {product: '자전거 폰 거치대',
    road: p.road === 'cobblestone' && 'road' in parsed.params ? '자갈·돌길 (측정값)' : p.road === 'cobblestone' ? '기본: 자갈길 기준' : `${p.road} → 자갈길 값으로 보수`,
    vib: `${pyf(road.excitation_hz[0])}–${pyf(road.excitation_hz[1])} Hz`, shock_g: shock.accel_g, phone: g.phone.name,
    point_mass_g: Math.round(spec.point_masses[0].mass_kg * 1e3), bar_d: g.bar_d, objective: p.objective === 'min_mass' ? '무게 최소' : p.objective,
    safety_factor: sf, material: spec.material.name, requirements: spec.requirements.map(r => T.requirements[r].name)};
  rep.cad = clone(geo.cad[pk].info);
  rep.drawing = {sheet: geo.cad[pk].drawing.sheet, scale: geo.cad[pk].drawing.scale, views: ['front', 'top', 'right', 'iso'],
    dxf: 'design_1st_drawing.dxf', svg: 'design_1st_drawing.svg'};
  return {rep, spec};
};

/* ------------------------------------------------------------------ drawing title block (drawing.make_drawing) */
FP.titleLines = function (spec, geo, check, massG) {      // geo: the per-phone CAD entry (has .drawing)
  const g = spec.geometry, tpl = spec.template, cons = {};
  spec.constraints.forEach(c => { cons[c.id] = c; });
  const pm = spec.point_masses[0];
  const road = spec.load_cases.find(c => c.type === 'modal'), shock = spec.load_cases.find(c => c.name === 'shock_vertical');
  const d = geo.drawing, mat = spec.material;
  const A = ['자전거 폰 거치대 — 1차 설계', `템플릿 ${tpl.id} ${tpl.name || ''} · 팔 ${g.arm.style}`, 'FormProof 입력 단계 산출 (물리 최적화 전)',
    `척도 ${d.scale} · 제3각법 · 단위 mm · ${d.sheet} · 팔 두께 ${fg(g.arm.t)}`];
  const B = [`재료 ${mat.name} (E ${fx(mat.E / 1000, 1)} GPa, 항복 ${fg(mat.yield_mpa)} MPa)`, massG ? `질량 ${fx(massG, 1)} g (CAD)` : '질량 -',
    `핸들바 Ø${pyf(g.bar_d)} · 폭 ${fg(g.width)} · M4 볼트 2개`,
    `폰+클램프 ${fx(pm.mass_kg * 1e3, 0)} g · 출력 색 ${(spec.finish || {}).colour === 'white' ? '흰색' : '검정'}`];
  const C = ['설계 조건 (물리 최적화 기준)', `노면 ${pyf(road.excitation_hz[0])}–${pyf(road.excitation_hz[1])} Hz, 충격 ${pyf(shock.accel_g)} g`,
    `1차 진동 ≥ ${pyf(cons.f1.value)} Hz · 응력 ≤ ${pyf(cons.stress.value)} MPa`, `층간 ≤ ${pyf(cons.interlayer.value)} MPa · 최소 두께 ${fg(cons.min_feature.value)}`];
  if (check) C.push(`1차 설계 판정: f1 ${pyf(check.f1_hz)} Hz, 응력 ${pyf(check.checks.stress.value)} MPa — ${check.pass ? '충족' : '미충족 → 최적화 대상'}`);
  return A.concat(B, C);
};

FP.fillDxf = (dxfText, lines) => dxfText.replace(/@@T(\d\d)@@/g, (_, i) => lines[+i] || '');

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
FP.drawingSvg = function (geo, lines, opts = {}) {
  const d = geo.drawing, H = d.H, W = d.W;
  const col = opts.colors || {OUTLINE: '#111', HIDDEN: '#666', CENTER: '#b03030', DIM: '#1d6b4f', TEXT: '#111', FRAME: '#111', paper: '#fff'};
  const sw = {OUTLINE: 0.35, HIDDEN: 0.18, CENTER: 0.18, DIM: 0.18, FRAME: 0.5, TEXT: 0.2};
  const dash = {HIDDEN: '1.6 0.9', CENTER: '6 1.2 1 1.2'};
  const parts = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}mm" height="${H}mm" font-family="${opts.font || "'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif"}">`,
    `<rect width="${W}" height="${H}" fill="${col.paper}"/>`];
  const Y = y => (H - y).toFixed(3);
  const groups = {};
  for (const p of d.prims) (groups[p.l] = groups[p.l] || []).push(p);
  for (const [layer, list] of Object.entries(groups)) {
    const c = col[layer] || col.TEXT;
    parts.push(`<g stroke="${c}" stroke-width="${sw[layer] || 0.25}" fill="none" stroke-linecap="round" stroke-linejoin="round"${dash[layer] ? ` stroke-dasharray="${dash[layer]}"` : ''}>`);
    for (const p of list) {
      if (p.k === 'pl') parts.push(`<${p.c ? 'polygon' : 'polyline'} points="${p.p.map(q => q[0].toFixed(3) + ',' + Y(q[1])).join(' ')}"/>`);
      else if (p.k === 'so') parts.push(`<polygon points="${p.p.map(q => q[0].toFixed(3) + ',' + Y(q[1])).join(' ')}" fill="${c}" stroke="none"/>`);
    }
    parts.push('</g>');
    for (const p of list) {
      if (p.k !== 'tx') continue;
      let s = p.s;
      const m = /^@@T(\d\d)@@$/.exec(s);
      if (m) s = lines[+m[1]] || '';
      if (!s) continue;
      const anchor = ['start', 'middle', 'end'][p.ha] || 'start';
      // dxf valign: 0 baseline, 1 bottom, 2 middle, 3 top
      const dy = [0, -0.2, 0.35, 1.0][p.va] * p.h;
      const tr = p.r ? ` transform="rotate(${-p.r} ${p.x.toFixed(3)} ${Y(p.y)})"` : '';
      parts.push(`<text x="${p.x.toFixed(3)}" y="${(H - p.y + dy).toFixed(3)}" font-size="${(p.h * 1.32).toFixed(2)}" text-anchor="${anchor}" fill="${c}"${tr}>${esc(s)}</text>`);
    }
  }
  parts.push('</svg>');
  return parts.join('');
};

/* ------------------------------------------------------------------ files */
FP.stlBinary = function (verts, idx) {
  const nt = idx.length / 3, buf = new ArrayBuffer(84 + nt * 50), dv = new DataView(buf);
  const head = 'FormProof 1st design (CAD mesh, mm)';
  for (let i = 0; i < 80; i++) dv.setUint8(i, i < head.length ? head.charCodeAt(i) : 32);
  dv.setUint32(80, nt, true);
  let o = 84;
  for (let t = 0; t < nt; t++) {
    const a = idx[3 * t] * 3, b = idx[3 * t + 1] * 3, c = idx[3 * t + 2] * 3;
    const ux = verts[b] - verts[a], uy = verts[b + 1] - verts[a + 1], uz = verts[b + 2] - verts[a + 2];
    const vx = verts[c] - verts[a], vy = verts[c + 1] - verts[a + 1], vz = verts[c + 2] - verts[a + 2];
    let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    const L = Math.hypot(nx, ny, nz) || 1; nx /= L; ny /= L; nz /= L;
    for (const v of [nx, ny, nz]) { dv.setFloat32(o, v, true); o += 4; }
    for (const k of [a, b, c]) for (let j = 0; j < 3; j++) { dv.setFloat32(o, verts[k + j], true); o += 4; }
    dv.setUint16(o, 0, true); o += 2;
  }
  return new Uint8Array(buf);
};

const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
const crc32 = u => { let c = 0xFFFFFFFF; for (let i = 0; i < u.length; i++) c = CRC[(c ^ u[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
FP.zip = function (files) {               // [{name, data: Uint8Array|string}] -> Uint8Array (stored, UTF-8 names)
  const enc = new TextEncoder(), chunks = [], central = [];
  let off = 0;
  const d = new Date(), dt = ((d.getFullYear() - 1980) << 9 | (d.getMonth() + 1) << 5 | d.getDate()), tm = (d.getHours() << 11 | d.getMinutes() << 5 | (d.getSeconds() >> 1));
  for (const f of files) {
    const name = enc.encode(f.name), data = typeof f.data === 'string' ? enc.encode(f.data) : f.data, crc = crc32(data);
    const h = new DataView(new ArrayBuffer(30));
    h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true); h.setUint16(8, 0, true);
    h.setUint16(10, tm, true); h.setUint16(12, dt, true); h.setUint32(14, crc, true); h.setUint32(18, data.length, true);
    h.setUint32(22, data.length, true); h.setUint16(26, name.length, true); h.setUint16(28, 0, true);
    chunks.push(new Uint8Array(h.buffer), name, data);
    const c = new DataView(new ArrayBuffer(46));
    c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true);
    c.setUint16(10, 0, true); c.setUint16(12, tm, true); c.setUint16(14, dt, true); c.setUint32(16, crc, true);
    c.setUint32(20, data.length, true); c.setUint32(24, data.length, true); c.setUint16(28, name.length, true);
    c.setUint32(42, off, true);
    central.push(new Uint8Array(c.buffer), name);
    off += 30 + name.length + data.length;
  }
  const csize = central.reduce((a, b) => a + b.length, 0);
  const e = new DataView(new ArrayBuffer(22));
  e.setUint32(0, 0x06054b50, true); e.setUint16(8, files.length, true); e.setUint16(10, files.length, true);
  e.setUint32(12, csize, true); e.setUint32(16, off, true);
  const all = chunks.concat(central, [new Uint8Array(e.buffer)]);
  const out = new Uint8Array(all.reduce((a, b) => a + b.length, 0));
  let p = 0;
  for (const a of all) { out.set(a, p); p += a.length; }
  return out;
};

FP._dbg = {findRing, skeletonize, dilate, erode, plot, prominentPeaks, circlePerimeter};
if (typeof module !== 'undefined' && module.exports) module.exports = FP; else root.FP = FP;
})(typeof window !== 'undefined' ? window : globalThis);
