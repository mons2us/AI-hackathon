/* FormProof input stage — page logic (browser-only build of app/static/index.html). */
(function () {
'use strict';
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const S = {mode: 'sketch', strokes: [], cur: null, bgImg: null, image: null, imageName: '', last: null, rep: null, geoCache: {}, out: null};
const toast = m => { const t = $('#toast'); t.textContent = m; t.hidden = false; clearTimeout(t._h); t._h = setTimeout(() => { t.hidden = true; }, 4200); };
const setStep = n => $$('#steps .step').forEach((e, i) => { e.classList.toggle('on', i === n); e.classList.toggle('done', i < n); });
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const fmt = (v, d = 1) => (typeof v === 'number' ? v.toFixed(d) : v);
const tick = () => new Promise(r => setTimeout(r, 16));

/* ---------- data */
async function gunzip(b64) {
  const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  if (typeof DecompressionStream === 'undefined') throw new Error('이 브라우저는 압축 해제를 지원하지 않습니다. 최신 Chrome·Edge·Safari에서 열어 주세요.');
  const s = new Blob([bin]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Uint8Array(await new Response(s).arrayBuffer());
}
async function loadGeo(tid, bar) {
  const key = `${tid}_${bar.toFixed(1)}`;
  if (!S.geoCache[key]) S.geoCache[key] = fetch(`data/geo/${key}.json`).then(r => { if (!r.ok) throw new Error('형상 데이터를 불러오지 못했습니다: ' + key); return r.json(); });
  return S.geoCache[key];
}

/* ---------- downloads (artifact capability; plain link when opened as a normal page) */
let DL = null;
try { window.claude && window.claude.use && window.claude.use('downloads').then(x => { DL = x; }).catch(() => {}); } catch (e) { /* not in a viewer */ }
async function save(filename, data) {
  if (DL) {
    try { await DL.save({filename, data}); toast(`${filename} 저장`); }
    catch (e) { if (e && e.code === 'declined') return; toast(e && e.code === 'rate_limited' ? '저장 창이 이미 열려 있습니다. 잠시 후 다시 눌러 주세요.' : '이 화면에서는 파일 저장을 쓸 수 없습니다.'); }
    return;
  }
  const blob = data instanceof Blob ? data : new Blob([data]);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

/* ---------- text chips */
const EX = ['자갈길에서도 폰이 안 흔들리게, 최대한 가볍게', 'S25 울트라, 로드 바이크, 튼튼하게', '앞으로 길게 뻗어서 보강대 넣어줘', '여름 땡볕에서도 변형 없고 화면 각도는 자유롭게', '따릉이에 달 거야, 230g 폰'];
EX.forEach(t => { const b = document.createElement('button'); b.className = 'chip'; b.textContent = t;
  b.onclick = () => { const a = $('#text'); a.value = a.value ? a.value.replace(/\s*$/, ', ') + t : t; }; $('#chips').appendChild(b); });

/* ---------- sketch pad */
const pad = $('#pad'), ctx = pad.getContext('2d', {willReadFrequently: true});
function redraw() {
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, pad.width, pad.height);
  if (S.bgImg) { const r = Math.min(pad.width / S.bgImg.width, pad.height / S.bgImg.height) * 0.92, w = S.bgImg.width * r, h = S.bgImg.height * r;
    ctx.drawImage(S.bgImg, (pad.width - w) / 2, (pad.height - h) / 2, w, h); }
  ctx.strokeStyle = '#111'; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const s of S.strokes) { ctx.beginPath(); s.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); if (s.length === 1) ctx.lineTo(s[0][0] + 0.1, s[0][1]); ctx.stroke(); }
}
const pt = e => { const r = pad.getBoundingClientRect(); return [(e.clientX - r.left) * pad.width / r.width, (e.clientY - r.top) * pad.height / r.height]; };
pad.addEventListener('pointerdown', e => { pad.setPointerCapture(e.pointerId); S.cur = [pt(e)]; S.strokes.push(S.cur); redraw(); });
pad.addEventListener('pointermove', e => { if (!S.cur) return; const p = pt(e), q = S.cur[S.cur.length - 1]; if (Math.hypot(p[0] - q[0], p[1] - q[1]) > 1.5) { S.cur.push(p); redraw(); } });
['pointerup', 'pointercancel', 'pointerleave'].forEach(n => pad.addEventListener(n, () => { S.cur = null; }));
$('#undo').onclick = () => { if (S.strokes.length) S.strokes.pop(); else S.bgImg = null; redraw(); };
$('#clear').onclick = () => { S.strokes = []; S.bgImg = null; $('#example').value = ''; redraw(); };
$('#example').onchange = e => { if (!e.target.value) return; const im = new Image(); im.onload = () => { S.bgImg = im; S.strokes = []; redraw(); }; im.src = e.target.value; };
redraw();
const hasSketch = () => S.strokes.length > 0 || !!S.bgImg;

/* ---------- image attach */
function setMode(m) {
  S.mode = m;
  $('#mSketch').classList.toggle('on', m === 'sketch'); $('#mImage').classList.toggle('on', m === 'image');
  $('#sketchBox').hidden = m !== 'sketch'; $('#imageBox').hidden = m !== 'image';
}
$('#mSketch').onclick = () => setMode('sketch');
$('#mImage').onclick = () => setMode('image');
function loadFile(f) {
  if (!f) return;
  const rd = new FileReader();
  rd.onload = () => { S.image = rd.result; S.imageName = f.name;
    $('#dropInner').innerHTML = ''; const im = document.createElement('img'); im.src = S.image; const sm = document.createElement('small'); sm.textContent = `${f.name} · 다시 눌러 바꾸기`;
    $('#dropInner').append(im, sm); };
  rd.readAsDataURL(f);
}
$('#file').onchange = e => loadFile(e.target.files[0]);
const drop = $('#drop');
['dragover', 'dragenter'].forEach(n => drop.addEventListener(n, e => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach(n => drop.addEventListener(n, e => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', e => loadFile(e.dataTransfer.files[0]));

/* ---------- pixels -> gray (pipeline.decode_image) */
function grayOf(source, w, h) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const c = cv.getContext('2d', {willReadFrequently: true});
  c.fillStyle = '#fff'; c.fillRect(0, 0, w, h); c.drawImage(source, 0, 0, w, h);
  const d = c.getImageData(0, 0, w, h).data;
  let k = 1;
  if (Math.max(w, h) > 1200) k = Math.ceil(Math.max(w, h) / 1200);
  const W = Math.ceil(w / k), H = Math.ceil(h / k), g = new Float32Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = ((y * k) * w + x * k) * 4;
    g[y * W + x] = ((d[i] * 19595 + d[i + 1] * 38470 + d[i + 2] * 7471 + 0x8000) >> 16) / 255;
  }
  return {g, w: W, h: H};
}
const loadImage = src => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error('이미지를 읽지 못했습니다')); im.src = src; });

/* ---------- 3D viewer (bike scene from master 06_발표/scene/scene.html) */
const V3 = {};
function init3d() {
  if (typeof THREE === 'undefined') { $('#ovl3d').textContent = '3D 엔진(three.js)을 불러오지 못했습니다. 측면도·도면 탭은 그대로 쓸 수 있습니다.'; return; }
  const host = $('#three');
  THREE.Object3D.DefaultUp.set(0, 0, 1);
  const R = new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true});
  R.setPixelRatio(Math.min(window.devicePixelRatio, 2)); R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
  R.outputEncoding = THREE.sRGBEncoding; host.appendChild(R.domElement);
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(25, 1, 5, 20000); cam.up.set(0, 0, 1);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a9399, 0.75));
  const sun = new THREE.DirectionalLight(0xffffff, 1.15); sun.position.set(400, 700, 2600); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -1600, right: 1600, top: 1600, bottom: -1600, near: 100, far: 6000}); sun.shadow.bias = -0.0005; scene.add(sun);
  const fill = new THREE.DirectionalLight(0xdfe9ff, 0.35); fill.position.set(-1200, 900, 600); scene.add(fill);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), new THREE.ShadowMaterial({opacity: 0.18})); ground.position.z = -903; ground.receiveShadow = true; scene.add(ground);
  const M = (c, r = 0.5, m = 0.1) => new THREE.MeshStandardMaterial({color: c, roughness: r, metalness: m});
  const frameMat = M(0x1f2a33, 0.35, 0.35), darkMat = M(0x15191d, 0.8, 0), alMat = M(0x9aa3ab, 0.3, 0.8), tireMat = M(0x202326, 0.9, 0);
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  function tube(a, b, r, mat, seg = 24) { const d = new THREE.Vector3().subVectors(b, a); const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, d.length(), seg), mat);
    m.position.copy(a).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(V(0, 1, 0), d.clone().normalize()); m.castShadow = m.receiveShadow = true; return m; }
  const bike = new THREE.Group(); scene.add(bike);
  const S0 = V(-90, 0, -40), dH = V(0.309, 0, -0.951), Hb = S0.clone().addScaledVector(dH, 150), A = V(125, 0, -563), Rr = V(-875, 0, -563), BB = V(-455, 0, -633), ST = V(-607, 0, -136), SAD = V(-650, 0, -40);
  const TT = S0.clone().addScaledVector(dH, 25);
  [[ST, TT, 16], [BB, Hb, 20], [BB, ST, 16], [S0, Hb, 19]].forEach(p => bike.add(tube(p[0], p[1], p[2], frameMat)));
  for (const s of [-38, 38]) { bike.add(tube(V(BB.x, s * 0.6, BB.z), V(Rr.x, s, Rr.z), 9, frameMat)); bike.add(tube(V(ST.x, s * 0.4, ST.z - 20), V(Rr.x, s, Rr.z), 8, frameMat)); bike.add(tube(V(Hb.x, s * 0.8, Hb.z), V(A.x, s * 1.2, A.z), 11, frameMat)); }
  bike.add(tube(ST, SAD, 13, alMat));
  const saddle = new THREE.Mesh(new THREE.BoxGeometry(260, 70, 40), darkMat); saddle.position.set(SAD.x - 10, 0, SAD.z + 18); saddle.castShadow = true; bike.add(saddle);
  bike.add(tube(S0, V(0, 0, 0), 17, frameMat)); bike.add(tube(V(0, -30, 0), V(0, 30, 0), 22, frameMat));
  bike.add(tube(V(0, -360, 0), V(0, -230, 0), 17.5, darkMat)); bike.add(tube(V(0, 230, 0), V(0, 360, 0), 17.5, darkMat));
  for (const s of [-1, 1]) bike.add(tube(V(0, s * 215, 0), V(70, s * 235, -40), 7, darkMat));
  function wheel(c) { const g = new THREE.Group(); const t = new THREE.Mesh(new THREE.TorusGeometry(326, 15, 20, 120), tireMat); t.rotation.x = Math.PI / 2; t.castShadow = true; g.add(t);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(305, 8, 12, 120), alMat); rim.rotation.x = Math.PI / 2; g.add(rim); g.add(tube(V(0, -35, 0), V(0, 35, 0), 18, alMat));
    for (let i = 0; i < 24; i++) { const a = i / 24 * Math.PI * 2, s = i % 2 ? 35 : -35; g.add(tube(V(0, s, 0), V(300 * Math.cos(a), 0, 300 * Math.sin(a)), 1.2, alMat, 6)); } g.position.copy(c); return g; }
  bike.add(wheel(A)); bike.add(wheel(Rr));
  const ring = new THREE.Mesh(new THREE.CylinderGeometry(95, 95, 6, 48), alMat); ring.position.set(BB.x, -60, BB.z); bike.add(ring);
  bike.add(tube(V(BB.x, -66, BB.z), V(BB.x + 60, -70, BB.z - 160), 9, alMat)); bike.add(tube(V(BB.x, 66, BB.z), V(BB.x - 60, 70, BB.z + 160), 9, alMat));
  const handlebar = new THREE.Group(); scene.add(handlebar);
  const ctl = new THREE.OrbitControls(cam, R.domElement); ctl.enableDamping = true; ctl.dampingFactor = 0.12;
  Object.assign(V3, {R, scene, cam, ctl, bike, ground, M, tube, V, darkMat, alMat, handlebar, mount: null, holder: null, bar: null});
  setBar(31.8);
  const fit = () => { const w = host.clientWidth, h = host.clientHeight; if (!w || !h) return; R.setSize(w, h, false); R.domElement.style.width = w + 'px'; R.domElement.style.height = h + 'px'; cam.aspect = w / h; cam.updateProjectionMatrix(); };
  new ResizeObserver(fit).observe(host); fit();
  view('full');
  (function loop() { requestAnimationFrame(loop); ctl.update(); R.render(scene, cam); })();
}
function setBar(d) {
  if (!V3.handlebar) return;
  if (V3.bar) { V3.handlebar.remove(V3.bar); V3.bar.geometry.dispose(); }
  V3.bar = V3.tube(V3.V(0, -360, 0), V3.V(0, 360, 0), d / 2, V3.alMat, 48); V3.handlebar.add(V3.bar);
}
function view(kind) {
  if (!V3.cam) return;
  const {cam, ctl} = V3, close = kind === 'close';
  if (close) { cam.fov = 20; cam.position.set(420, 560, -60); ctl.target.set(70, 50, 5); }
  else { cam.fov = 25; cam.position.set(1500, 2600, 700); ctl.target.set(-380, 0, -420); }
  cam.updateProjectionMatrix(); ctl.update(); $('#vClose').classList.toggle('on', close); V3.kind = kind;
}
function showMount(mesh, spec) {
  if (!V3.scene) return;
  const {scene, M} = V3;
  if (V3.mount) { scene.remove(V3.mount); V3.mount.geometry.dispose(); }
  if (V3.holder) scene.remove(V3.holder);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(mesh.verts, 3)); g.setIndex(new THREE.BufferAttribute(mesh.idx, 1)); g.computeVertexNormals();
  g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(mesh.verts.length), 3));
  V3.matShape = V3.matShape || M(0x2aa3a6, 0.45, 0.05);
  V3.matField = V3.matField || new THREE.MeshStandardMaterial({color: 0xffffff, roughness: 0.6, metalness: 0, vertexColors: true});
  V3.mount = new THREE.Mesh(g, V3.matShape); V3.mount.castShadow = V3.mount.receiveShadow = true; scene.add(V3.mount);
  const geo = spec.geometry, ph = geo.phone, ys = geo.y_sym;
  const hold = new THREE.Group(); scene.add(hold); V3.holder = hold;      // phone only: the holder that grips it is part of the CAD mesh
  const pg = new THREE.Group(); pg.position.set(ph.cog[0], ys, ph.cog[1]); hold.add(pg);
  const body = new THREE.Mesh(new THREE.BoxGeometry(ph.H, ph.W - 0.6, ph.D), M(0x2b2f36, 0.35, 0.6)); body.castShadow = true; pg.add(body);
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(ph.H - 10, ph.W - 8), new THREE.MeshStandardMaterial({color: 0x0b2540, emissive: 0x05182b, emissiveIntensity: 0.4, roughness: 0.2})); scr.position.z = ph.D / 2 + 0.1; pg.add(scr);
  hold.visible = $('#vPhone').classList.contains('on');
  setBar(geo.bar_d);
  view('close');
}
$('#vBike').onclick = e => { const on = !e.target.classList.contains('on'); e.target.classList.toggle('on', on); if (V3.bike) { V3.bike.visible = on; V3.ground.visible = on; } };
$('#vPhone').onclick = e => { const on = !e.target.classList.contains('on'); e.target.classList.toggle('on', on); if (V3.holder) V3.holder.visible = on; };
$('#vClose').onclick = () => view(V3.kind === 'close' ? 'full' : 'close');
$$('.tab').forEach(t => t.onclick = () => { $$('.tab').forEach(x => x.classList.toggle('on', x === t)); $$('.pane').forEach(p => { p.hidden = p.id !== t.dataset.pane; }); });

/* ---------- heat maps: per-element FEM fields of the 1st design (precomputed), scaled to this request's phone mass */
const RAMP = [[44, 75, 214], [34, 184, 214], [63, 207, 107], [242, 194, 48], [224, 52, 43]];
function ramp(t) { t = Math.max(0, Math.min(1, t)) * 4; const i = Math.min(3, Math.floor(t)), f = t - i, a = RAMP[i], b = RAMP[i + 1]; return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f]; }
function fieldNow() {
  const o = S.out; if (!o || S.hm === 'shape' || !o.fields) return null;
  const [q, cs] = S.hm.split(':'), f = o.fields.cases[cs][q];
  return {q, cs, data: f.u8, max: f.max * o.kMass, shape: o.fields.shape, h: o.fields.h, origin: o.fields.origin};
}
function applyField() {
  const o = S.out; if (!o) return;
  const F = fieldNow();
  $('#hm').hidden = !F;
  if (F) {
    const lim = o.spec.constraints.find(c => c.id === 'stress').value;
    $('#hmTitle').textContent = (F.q === 'vm' ? '응력 (von Mises)' : '처짐') + ' · ' + (F.cs === 'shock_vertical' ? '위아래' : '옆') + ` 충격 ${o.rep.summary.shock_g} g`;
    $('#hmMax').textContent = F.q === 'vm' ? `${F.max.toFixed(1)} MPa` : `${F.max.toFixed(2)} mm`;
    $('#hmNote').textContent = F.q === 'vm'
      ? `기준 ≤ ${lim} MPa → ${F.max <= lim ? '충족' : '빨간 쪽이 기준을 넘는 곳 (최적화 대상)'}. 폰 홀더는 해석에서 강체로 두어 회색으로 표시`
      : '핸들바에 고정된 클램프에서 멀수록 많이 움직입니다. 해석 격자 2 mm, 폰+클램프 질량을 홀더 위에 집중';
  }
  if (V3.mount) {
    V3.mount.material = F ? V3.matField : V3.matShape;
    if (F) {
      const [nx, ny, nz] = F.shape, pos = o.mesh.verts, col = V3.mount.geometry.attributes.color, ys = o.spec.geometry.y_sym;
      for (let v = 0; v < pos.length / 3; v++) {
        const i = Math.floor((pos[3 * v] - F.origin[0]) / F.h), j = Math.floor(Math.abs(pos[3 * v + 1] - ys) / F.h), k = Math.floor((pos[3 * v + 2] - F.origin[2]) / F.h);
        let best = 0;
        for (let dk = -1; dk <= 1; dk++) for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
          const I = i + di, J = j + dj, K = k + dk;
          if (I < 0 || J < 0 || K < 0 || I >= nx || J >= ny || K >= nz) continue;
          const u = F.data[(K * ny + J) * nx + I];
          if (u > best) best = u;
        }
        const c = best ? ramp((best - 1) / 254) : [150, 156, 166];
        col.setXYZ(v, c[0] / 255, c[1] / 255, c[2] / 255);
      }
      col.needsUpdate = true;
    }
  }
  drawSide();
}
S.hm = 'shape';
$$('#modes button').forEach(b => b.onclick = () => { S.hm = b.dataset.m; $$('#modes button').forEach(x => x.classList.toggle('on', x === b)); applyField(); });

/* ---------- side view (export.side_preview, drawn from the precomputed label raster) */
function drawSide() {
  const o = S.out; if (!o) return;
  const sd = o.geo.side, cv = $('#sideCv'), c = cv.getContext('2d');
  const W = cv.width, H = cv.height, padL = 64, padB = 46, padT = 30, padR = 18;
  const x0 = sd.origin[0], z0 = sd.origin[1], x1 = x0 + sd.nx * sd.h, z1 = z0 + sd.nz * sd.h;
  const sc = Math.min((W - padL - padR) / (x1 - x0), (H - padT - padB) / (z1 - z0));
  const ox = padL, oy = padT + (z1 - z0) * sc;
  const X = x => ox + (x - x0) * sc, Z = z => oy - (z - z0) * sc;
  c.clearRect(0, 0, W, H);
  const col = ['', css('--side-design'), css('--side-first'), css('--side-solid'), css('--side-rigid')];
  for (let r = 0; r < sd.nz; r++) for (let q = 0; q < sd.nx; q++) {
    const v = +sd.cells[r * sd.nx + q]; if (!v) continue;
    c.fillStyle = col[v]; c.fillRect(Math.floor(ox + q * sd.h * sc), Math.floor(padT + r * sd.h * sc), Math.ceil(sd.h * sc) + 1, Math.ceil(sd.h * sc) + 1);
  }
  const F = fieldNow();
  if (F) {                                   // heat map: largest value across the width at each (x, z)
    const [nx, ny, nz] = F.shape;
    for (let k = 0; k < nz; k++) for (let i = 0; i < nx; i++) {
      let best = 0;
      for (let j = 0; j < ny; j++) { const u = F.data[(k * ny + j) * nx + i]; if (u > best) best = u; }
      if (!best) continue;
      const rgb = ramp((best - 1) / 254);
      c.fillStyle = `rgb(${rgb[0] | 0},${rgb[1] | 0},${rgb[2] | 0})`;
      c.fillRect(Math.floor(ox + i * sd.h * sc), Math.floor(padT + (nz - 1 - k) * sd.h * sc), Math.ceil(sd.h * sc) + 1, Math.ceil(sd.h * sc) + 1);
    }
  }
  if (o.p.requirements.includes('free_angle')) {
    const ko = o.geo.keepout[o.pk].xz;
    c.fillStyle = css('--side-keep');
    for (let r = 0; r < sd.nz; r++) for (let q = 0; q < sd.nx; q++) if (ko[r * sd.nx + q] === '1') c.fillRect(ox + q * sd.h * sc, padT + r * sd.h * sc, sd.h * sc + 0.5, sd.h * sc + 0.5);
  }
  c.fillStyle = css('--side-sup');
  for (const [x, z] of sd.supports) { c.beginPath(); c.arc(X(x), Z(z), 2.2, 0, 7); c.fill(); }
  c.strokeStyle = css('--line'); c.fillStyle = css('--ink2'); c.lineWidth = 1; c.font = `12px ${css('--f-num')}`;
  c.strokeRect(ox, padT, (x1 - x0) * sc, (z1 - z0) * sc);
  c.textAlign = 'center'; c.textBaseline = 'top';
  for (let x = Math.ceil(x0 / 20) * 20; x <= x1; x += 20) { c.fillText(String(x), X(x), oy + 6); }
  c.textAlign = 'right'; c.textBaseline = 'middle';
  for (let z = Math.ceil(z0 / 20) * 20; z <= z1; z += 20) { c.fillText(String(z), ox - 6, Z(z)); }
  c.font = `12px ${css('--f-ui')}`; c.textAlign = 'center'; c.textBaseline = 'alphabetic';
  c.fillText('x (앞) mm', ox + (x1 - x0) * sc / 2, H - 8);
  c.save(); c.translate(16, padT + (z1 - z0) * sc / 2); c.rotate(-Math.PI / 2); c.fillText('z (위) mm', 0, 0); c.restore();
  c.textAlign = 'left'; c.fillStyle = css('--ink');
  c.fillText(`${o.rep.template.id} ${o.rep.template.name} — 1차 설계 / 설계 영역 (격자 ${sd.h} mm, 반쪽 모델 측면 투영)`, ox, 18);
  const items = [['--side-design', '설계 영역'], ['--side-first', '1차 설계'], ['--side-solid', '지킬 곳'], ['--side-rigid', '폰 홀더(해석: 강체)'], ['--side-sup', '고정(핸들바)']];
  if (o.p.requirements.includes('free_angle')) items.push(['--side-keep', '폰 회전 공간(비울 곳)']);
  $('#sideLegend').innerHTML = items.map(([v, t]) => `<span><i style="background:var(${v})"></i>${t}</span>`).join('');
}
const themeChanged = () => drawSide();
try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeChanged); } catch (e) { /* old browsers */ }
new MutationObserver(themeChanged).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});

/* ---------- run */
const STAGES = ['선 추출', '핸들 원 찾기 · 축척', '템플릿 비교', '설계 명세 · 물리 조건', 'CAD · 도면 불러오기', '1차 성능 계산'];
const stage = i => { $('#stage').textContent = STAGES[i]; return tick(); };
async function run(template) {
  const text = $('#text').value.trim();
  let req = {text};
  if (template && S.last) { req = Object.assign({}, S.last, {text, template}); }
  else {
    if (S.mode === 'sketch' && hasSketch()) req.sketch = (S.bgImg && !S.strokes.length) ? S.bgImg.src : pad.toDataURL('image/png');   // untouched example: match the original pixels
    if (S.mode === 'image' && S.image) req.image = S.image;
    if (!req.sketch && !req.image && !text) { toast('문장을 쓰거나, 스케치를 그리거나, 이미지를 올려 주세요.'); return; }
    S.last = Object.assign({}, req);
  }
  setStep(1); $('#go').disabled = true; $('#empty').hidden = true; $('#busy').hidden = false;
  const t0 = performance.now();
  try {
    await stage(0);
    const parsed = FP.parseText(text);
    let match = S.last && template ? S.last.match : null;
    if (!template && (req.sketch || req.image)) {
      const im = await loadImage(req.sketch || req.image);
      const {g, w, h} = grayOf(im, im.naturalWidth, im.naturalHeight);
      const photo = !!req.image && FP.looksLikePhoto(g);
      await stage(1);
      const pts = FP.inkPoints(g, w, h, photo);
      await stage(2);
      match = FP.matchPoints(pts);
      delete match.ring;
      match.source = photo ? '사진(에지 검출)' : (req.sketch ? '스케치' : '스케치 이미지');
      S.last.match = match;
    }
    let tid, how;
    if (template) { tid = template; how = match ? '후보 선택' : '지정'; }
    else if (match) { tid = match.candidates[0].id; how = `${match.source} 매칭`; }
    else { tid = FP.templateFromHint(parsed.shape_hint); how = '텍스트'; }
    await stage(3);
    const {p, barAsked} = FP.resolveParams(tid, parsed.params);
    await stage(4);
    const geo = await loadGeo(tid, p.bar_d);
    await stage(5);
    const input = {text, sketch: !!req.sketch, image: !!req.image, template: template || null};
    const {rep, spec} = FP.design({text, geo, tplId: tid, how, match, parsed, p, barAsked, input});
    const pk = p.phone in FP.T.ev.PHONES ? p.phone : 'default', cad = geo.cad[pk];
    const bin = await gunzip(cad.mesh.data);
    const mesh = {verts: new Float32Array(bin.buffer, 0, cad.mesh.nv * 3), idx: new Uint32Array(bin.buffer, cad.mesh.nv * 12, cad.mesh.nt * 3)};
    rep.seconds = +((performance.now() - t0) / 1000).toFixed(2);
    rep.files = ['spec.json', 'initial_design.npy', 'design_1st.step', 'design_1st_drawing.dxf', 'design_1st_drawing.svg', 'design_1st.stl', 'report.json'];
    const lines = FP.titleLines(spec, cad, rep.first_design_check, rep.cad.mass_g);
    const fields = {shape: geo.fields.shape, h: geo.fields.h, origin: geo.fields.origin, cases: {}};
    for (const [cs, f] of Object.entries(geo.fields.cases)) { fields.cases[cs] = {}; for (const q of ['vm', 'disp']) fields.cases[cs][q] = {max: f[q].max, u8: await gunzip(f[q].data)}; }
    const kMass = spec.point_masses[0].mass_kg / geo.fem.default.mass_kg;
    S.out = {rep, spec, geo, cad, p, mesh, lines, pk, fields, kMass, thumb: req.sketch || req.image};
    render(S.out);
    setStep(2);
  } catch (err) {
    console.error(err);
    const m = String(err && err.message || err);
    toast(m.includes('no strokes') ? '스케치나 이미지에서 선을 찾지 못했습니다. 조금 더 진하게 그려 주세요.' : m);
    setStep(S.out ? 2 : 0); if (!S.out) $('#empty').hidden = false;
  } finally { $('#busy').hidden = true; $('#go').disabled = false; }
}
$('#go').onclick = () => run();

const QN = {natural_frequency_hz: ['1차 고유진동수', 'Hz'], von_mises_max_mpa: ['충격 최대 응력', 'MPa'], layer_normal_tension_mpa: ['층간 인장 응력', 'MPa'],
  min_member_thickness_mm: ['최소 부재 두께', 'mm'], phone_clearance_mm: ['폰 회전·기울기 간격', 'mm'], joint_rot_stiffness_Nm_per_rad: ['관절 회전 강성', 'N·m/rad'],
  joint_hold_torque_Nm: ['관절 유지 토크', 'N·m'], parked_surface_temp_c: ['주차 표면온도', '°C']};
const ARM = {straight: '곧은 팔', L: 'L자 팔', truss: '트러스', low: '낮은 팔', stalk: '기둥형', under: '아래 우회'};
const escH = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function render(o) {
  const {rep, spec, geo} = o, s = rep.summary, t = rep.template, c = rep.first_design_check;
  const items = [['제품', s.product], ['노면', s.road], ['진동 · 충격', `${s.vib} · ${s.shock_g} g`], ['폰', `${s.phone} (+클램프 ${s.point_mass_g} g)`],
    ['핸들바', `Ø${s.bar_d} mm`], ['목표', s.objective], ['안전율', s.safety_factor], ['재료', s.material]];
  if (s.requirements.length) items.push(['추가 요구', s.requirements.join(' · '), 'wide']);
  $('#reqs').innerHTML = items.map(([k, v, w]) => `<div class="req ${w || ''}"><small>${k}</small><b>${escH(v)}</b></div>`).join('');
  $('#reqSub').textContent = rep.text.fired.length ? `문장에서 ${rep.text.fired.length}개 조건을 읽었습니다` : '문장 조건 없음 → 기본값 사용';
  $('#questions').innerHTML = rep.text.questions.map(q => `<div class="q">${q}</div>`).join('');
  const m = t.match;
  $('#tplTag').className = 'tag blue'; $('#tplTag').textContent = `${t.id} ${t.name} · ${t.chosen_by}`;
  const fl = m ? [`입력: ${m.source}`, m.frame === 'ring' ? `핸들 원 기준 축척 (원 검출 ${Math.round(m.ring_score * 100)}%)` : '윤곽 상자 기준 (원 미검출)', `후보 ${m.candidates.length}개 비교`] : ['입력: 문장'];
  fl.push(`명세 · 해석 격자 ${rep.problem.elements.design.toLocaleString()} 요소`, `STEP ${rep.cad.mass_g} g`, `도면 ${rep.drawing.sheet} ${rep.drawing.scale}`);
  $('#flow').innerHTML = fl.map(x => `<span class="ok">✓ ${x}</span>`).join('');
  if (m) {
    $('#cands').innerHTML = `<div class="cand input"><img src="${o.thumb}" alt="입력"><div class="t">입력</div><div class="s">${m.source}</div></div>` +
      m.candidates.map((x, i) => `<button class="cand ${x.id === t.id ? 'on' : ''}" data-id="${x.id}"><img src="ex/${x.id}.png" alt=""><div class="t">${x.id} ${x.name}</div><div class="s">${i === 0 ? '가장 비슷함' : '유사도 ' + Math.round(x.confidence * 100) + '%'}</div></button>`).join('');
    $$('#cands button.cand').forEach(b => b.onclick = () => { if (b.dataset.id !== t.id) run(b.dataset.id); });
  } else {
    $('#cands').innerHTML = `<div class="note" style="grid-column:1/-1">문장에서 형태를 골랐습니다: <b>${t.id} ${t.name}</b> — ${t.desc}. 스케치나 이미지를 넣으면 비슷한 후보를 비교합니다.</div>`;
  }
  showMount(o.mesh, spec);
  applyField();
  $('#pdraw').innerHTML = FP.drawingSvg(o.cad, o.lines);
  $('#kMass').textContent = `${fmt(rep.cad.mass_g)} g`; $('#kMassSub').textContent = `본체 ${fmt(rep.cad.bracket_mass_g)} + 폰 홀더 ${fmt(rep.cad.holder_mass_g)}`; $('#kTime').textContent = `${fmt(rep.seconds, 2)} s`;
  const ck = c.checks, rows = [];
  const lim = x => +x.limit.split(' ')[1];
  if (ck.f1) { const v = ck.f1.value, l = lim(ck.f1); rows.push(['1차 고유진동수', `${fmt(v)} Hz`, `기준 ≥ ${l}`, Math.min(v / l, 1), ck.f1.pass]); }
  if (ck.stress) { const v = ck.stress.value, l = lim(ck.stress); rows.push(['충격 최대 응력', `${fmt(v)} MPa`, `기준 ≤ ${l}`, Math.min(l / v, 1), ck.stress.pass]); }
  if (ck.interlayer) { const v = ck.interlayer.value, l = lim(ck.interlayer); rows.push(['층간 인장 응력', `${fmt(v)} MPa`, `기준 ≤ ${l}`, Math.min(l / Math.max(v, 1e-6), 1), ck.interlayer.pass]); }
  $('#metrics').innerHTML = rows.map(([n, v, l, r, ok]) => `<div class="metric"><div class="row"><span>${n}</span><b class="num" style="color:${ok ? 'var(--green)' : 'var(--red)'}">${v}</b></div>
    <div class="bar"><i class="${ok ? '' : 'bad'}" style="width:${Math.max(r * 100, 3)}%"></i></div><div class="row" style="color:var(--ink3);font-size:11.5px"><span>${l}</span><span>${ok ? '충족' : '최적화 대상'}</span></div></div>`).join('') +
    `<div class="note">1차 설계는 스케치 형상(팔 두께 ${rep.design_vars.arm_t} mm)을 그대로 옮긴 것입니다. 해석값은 같은 형상을 미리 FEM으로 계산해 둔 결과입니다${c.note ? ' (' + c.note + ')' : ''}. 기준을 맞추는 일은 다음 단계(물리 최적화)가 합니다.</div>`;
  $('#perfTag').className = 'tag ' + (c.pass ? 'green' : 'amber'); $('#perfTag').textContent = c.pass ? '기준 충족' : '최적화 전 · 미충족';
  const dv = rep.design_vars;
  $('#vars').innerHTML = [['핸들바 직경', `Ø${dv.bar_d} mm`], ['클램프 폭', `${dv.width} mm`], ['도달 거리 (핸들 중심 → 받침)', `${dv.reach} mm`], ['받침 높이 (핸들 중심 기준)', `${dv.pad_top} mm`],
    ['팔 형식', ARM[dv.arm] || dv.arm], ['팔 두께', `${dv.arm_t} mm`], ['폰 + 클램프', `${dv.point_mass_g} g`], ['재료', dv.material]].map(([k, v]) => `<tr><td>${k}</td><td class="num">${v}</td></tr>`).join('');
  $('#loadsSub').textContent = `하중: 노면 진동 ${s.vib}, 위아래·옆 충격 ${s.shock_g} g, 폰 ${s.point_mass_g} g`;
  const reqWarn = rep.handoff_requirements.flatMap(h => h.warnings);
  $('#cons').innerHTML = rep.criteria.map(x => { const [q, op, ...v] = x.rule.split(' '); const nm = QN[q] || [q, ''];
    return `<div class="con ${x.requirement ? 'req' : ''}"><b>${nm[0]} ${op} ${escH(v.join(' '))} ${nm[1]}</b><small>${escH(x.why || '')}${x.requirement ? ' · 사용자 요구' : ''}</small></div>`; }).join('') +
    reqWarn.map(w => `<div class="warn">${w}</div>`).join('');
  $('#assumpList').innerHTML = rep.assumptions.map(a => `<li>${escH(a)}</li>`).join('');
  $$('#files button').forEach(b => { b.disabled = false; });
  $('#handoff').disabled = false;
}

/* ---------- files */
async function handoffFiles(o) {
  const {rep, spec, geo, cad, mesh, lines} = o;
  const dxf = FP.fillDxf(new TextDecoder().decode(await gunzip(cad.dxf)), lines);
  const readme = [
    'FormProof 입력 단계 → 물리 최적화 인계 패키지 (브라우저 버전에서 생성)',
    '',
    `템플릿 ${rep.template.id} ${rep.template.name} · ${rep.template.chosen_by} · 핸들바 Ø${spec.geometry.bar_d} · ${spec.geometry.phone.name} ${rep.summary.point_mass_g} g`,
    '',
    'spec.json                 설계 명세 (formproof.spec/0.1): 영역·격자·재료·지지·하중·기준·근거·가정',
    'design_1st.step           1차 설계 B-rep (CadQuery)',
    'design_1st_drawing.dxf    2D 도면 (제3각법, 표제란 포함)',
    'design_1st_drawing.svg    같은 도면의 SVG',
    'design_1st.stl            1차 설계 CAD 메시 (mm)',
    'initial_design.npy        해석 격자 위 1차 설계 밀도 (0/1)',
    'report.json               입력 해석·매칭·1차 성능·물리 조건 요약',
    '',
    '해석 문제(problem.npz)는 spec.json에서 바로 다시 만듭니다 (10_입력_1차설계 폴더에서):',
    '  python -c "from formproof_input.compile import Problem, load_spec; Problem(load_spec(\'spec.json\')).to_npz(\'problem.npz\')"',
    '팀 opt3d.py 머리말 대신:  from formproof_input.adapter import opt3d_namespace; globals().update(opt3d_namespace("spec.json"))',
  ].join('\r\n');
  return [
    {name: 'spec.json', data: JSON.stringify(spec, null, 1)},
    {name: 'initial_design.npy', data: await gunzip(geo.npy)},
    {name: 'design_1st.step', data: await gunzip(cad.step)},
    {name: 'design_1st_drawing.dxf', data: dxf},
    {name: 'design_1st_drawing.svg', data: FP.drawingSvg(cad, lines)},
    {name: 'design_1st.stl', data: FP.stlBinary(mesh.verts, mesh.idx)},
    {name: 'report.json', data: JSON.stringify(rep, null, 1)},
    {name: 'README.txt', data: readme},
  ];
}
$('#handoff').onclick = async () => {
  const o = S.out; if (!o) return;
  try {
    const zip = FP.zip(await handoffFiles(o));
    await save(`formproof_${o.rep.template.id}_handoff.zip`, new Blob([zip], {type: 'application/zip'}));
    setStep(3);
  } catch (e) { console.error(e); toast('인계 패키지를 만들지 못했습니다: ' + e.message); }
};
$$('#files button').forEach(b => b.onclick = async () => {
  const o = S.out; if (!o) return;
  const f = b.dataset.f;
  if (f === 'spec') return save('spec.json', JSON.stringify(o.spec, null, 1));
  if (f === 'report') return save('report.json', JSON.stringify(o.rep, null, 1));
  if (f === 'svg') return save('design_1st_drawing.svg', FP.drawingSvg(o.cad, o.lines));
  if (f === 'side') { const cv = $('#sideCv'); const blob = await new Promise(r => cv.toBlob(r, 'image/png')); return save('side_view.png', blob); }
});

/* ---------- boot */
init3d();
fetch('data/tables.json').then(r => r.json()).then(tab => {
  FP.init(tab);
  for (const t of tab.templates) { const o = document.createElement('option'); o.value = `ex/hand_${t.id}.png`; o.textContent = `예시 ${t.id} ${t.name}`; $('#example').appendChild(o); }
  $('#go').disabled = false; $('#go').textContent = '1차 설계 만들기';
  // open in a working state: example sketch T07 + the default sentence
  $('#example').value = 'ex/hand_T07.png';
  const im = new Image(); im.onload = () => { S.bgImg = im; redraw(); run(); }; im.src = 'ex/hand_T07.png';
}).catch(e => { console.error(e); $('#go').textContent = '엔진을 불러오지 못했습니다'; toast('데이터를 불러오지 못했습니다: ' + e.message); });
})();
