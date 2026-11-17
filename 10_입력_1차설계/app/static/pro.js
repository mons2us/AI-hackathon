/* FormProof 툴형 화면 (?ui=pro): index.html 의 기능은 그대로 쓰고 배치 · 표시만 바꿈.
   - 단계별 배치 (body.st-input · st-spec · st-design · st-opt · st-done)
   - 설계 사양 단계: AI 가 읽은 요구 → 물리 조건 (설계 사양 행의 인용 · 근거 그대로)
   - 최적화: 진행 띠 · 분포 창(응력 · 온도) 크게 · 과정 그래프 크게, 흔들림 창은 숨김(물리 AI 가 예측하지 않음)
   - 결과: 결과 띠 + 1차 ↔ 최적 비교(같은 색 척도) 기본, 계산 기록(실제로 일어난 단계 · 측정값만), 상태 표시줄 */
(function(){
if(new URLSearchParams(location.search).get('ui')!=='pro')return;
const B=document.body;B.classList.add('pro');
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const strip=h=>String(h||'').replace(/<[^>]+>/g,'');

// ---------- 화면 요소 추가
$('#steps').insertAdjacentHTML('beforeend','<span class="step"><i>5</i>제작 파일</span>');
$('header.top .brand').insertAdjacentHTML('afterend','<span class="hproj" id="hProj"></span>');
$('header.top .brand-r').insertAdjacentHTML('beforebegin','<button class="hbtn" id="hLeft" hidden>입력 · 설계 사양</button>');
$('.wrap').insertAdjacentHTML('beforeend','<footer class="sbar"><span class="sdot" id="sbDot"></span><span id="sbMsg">준비됨</span><span class="sr" id="sbR">단위 mm</span></footer>');
$('#vMain').insertAdjacentHTML('beforeend','<div class="pban" id="optBan" hidden></div><div class="resbar" id="resBar" hidden></div><div class="reqmap" id="reqMap" hidden></div>');
$('#optimize').insertAdjacentHTML('beforebegin','<div class="plog" id="plog" hidden><div class="plh">계산 기록</div><div id="plogB"></div></div>');
SMALL.forEach(s=>$(s).insertAdjacentHTML('beforeend','<span class="ftag"></span>'));
$('#hLeft').onclick=()=>{B.classList.toggle('showleft');$('#hLeft').classList.toggle('on',B.classList.contains('showleft'));relayout();};
['#optBan','#resBar','#reqMap'].forEach(s=>$(s).addEventListener('pointerdown',e=>e.stopPropagation()));

// ---------- 단계별 배치
const STAGES=['input','spec','design','opt','done'];
function relayout(){requestAnimationFrame(()=>{if(window.V3&&V3.box)fitSmall();if(typeof spark==='function')spark();});}
function stage(s){
  STAGES.forEach(x=>B.classList.remove('st-'+x));B.classList.add('st-'+s);
  $('#reqMap').hidden=!(s==='spec'&&S.spec);
  $('#hLeft').hidden=!['design','opt','done'].includes(s);
  if(!['design','opt','done'].includes(s)){B.classList.remove('showleft');$('#hLeft').classList.remove('on');}
  if(s!=='opt')$('#optBan').hidden=true;
  if(s!=='done')$('#resBar').hidden=true;
  relayout();
}
const _setStep=window.setStep;
window.setStep=function(n){if(n===3&&S._done)n=4;_setStep(n);stage(STAGES[n]);};

// ---------- 상태 표시줄 (머리줄 단계 설명과 같은 내용)
const _guide=window.guide;
window.guide=function(a,b){_guide(a,b);$('#sbMsg').innerHTML=`<b>${a}</b>${b}`;};
function busy(on){$('#sbDot').classList.toggle('run',!!on);}

// ---------- 분포 창 꼬리표 (AI 예측 · 정밀 계산 · 1차 설계)
const _setPhase=window.setPhase;
window.setPhase=function(a,b){_setPhase(a,b);
  $$('.vp .ftag').forEach(e=>{e.textContent=b==='1차 설계'?'정밀 시뮬레이션':b;e.className='ftag'+(b==='AI 예측'?'':' fem');});};

// ---------- 계산 기록: 실제로 일어난 단계와 측정값만
function plog(html,run){const b=$('#plogB');$('#plog').hidden=false;
  if(b.lastElementChild&&b.lastElementChild.classList.contains('run'))b.lastElementChild.remove();
  b.insertAdjacentHTML('beforeend',`<div class="${run?'run':''}"><i>${run?'▶':'✓'}</i><span>${html}</span></div>`);}
function plogReset(){$('#plogB').innerHTML='';$('#plog').hidden=true;}

// ---------- 설계 사양: AI 가 읽은 요구 → 물리 조건
const _showSpec=window.showSpec;
window.showSpec=function(data,animate){
  _showSpec(data,animate);
  const rows=data.rows||[],G=[];
  rows.forEach(r=>{let g=G.find(x=>x.group===r.group);if(!g){g={group:r.group,rows:[],quote:null,from:r.from||[],basis:r.basis,source:r.source};G.push(g);}g.rows.push(r);if(!g.quote&&r.quote)g.quote=r.quote;});
  const val=r=>r.text!=null&&r.value==null?esc(r.text):`${esc(r.item)} ${OPS[r.op]||''} ${r.value} ${esc(r.unit)}`;
  $('#reqMap').innerHTML=`<div class="mh">AI가 읽은 요구 → 물리 조건</div><div class="ms">항목 ${rows.length}개 · 근거가 <em class="k4" style="font-style:normal;font-weight:700;border-radius:999px;padding:1px 8px;background:var(--red-s);color:var(--red)">확인 필요</em>인 값은 왼쪽 표에서 고쳐 쓸 수 있습니다</div>`+
    G.map((g,i)=>`<div class="mr${animate?' in':''}" style="animation-delay:${animate?60*i:0}ms"><span class="qt"><q>${esc(g.quote&&g.quote!=='?'?g.quote:(g.quote==='?'?'스케치의 ‘?’':g.group))}</q><small>${g.from.map(esc).join(' · ')}</small></span><span class="ar">→</span>
      <b>${g.rows.map(val).join(' · ')}<span class="src">${esc(g.source)}</span></b><em class="k${BASIS[g.basis]??3}">${BASIS_TXT[g.basis]||esc(g.basis)}</em></div>`).join('');
  if(animate){plogReset();plog(`설계 사양 · 항목 <b>${rows.length}개</b> · 항목마다 근거 표시`);}
  if(!S.rep)stage('spec');
};
const _confirm=$('#bConfirm').onclick;
$('#bConfirm').onclick=()=>{_confirm();if(S.spec&&S.spec.confirmed)plog('설계 사양 확정');};

// ---------- 1차 설계
const _run=window.run;
window.run=async function(){busy(true);guide('3 1차 설계','3D 형상을 만들고 정밀 시뮬레이션으로 판정하는 중');await _run();busy(false);};
$('#go').onclick=()=>window.run();
const _render=window.render;
window.render=function(rep){
  S._done=false;$('#resBar').hidden=true;
  const r=_render(rep);
  $('#hProj').innerHTML=`<b>${esc($('#tplTag').textContent)}</b>`;
  const rows=(S.rows||[]).filter(m=>!m.ref),nf=rows.filter(m=>!m.ok).length;
  plog(`1차 설계 · 정밀 시뮬레이션 판정 · ${nf?`<b>미충족 ${nf}개</b>`:'<b>모두 충족</b>'}${typeof rep.seconds==='number'?` · ${rep.seconds.toFixed(1)} s`:''}`);
  return r;
};

// ---------- 물리 최적화
const _opt=$('#optimize').onclick;
$('#optimize').onclick=async()=>{
  if(!S.rep||!S.sel||!S.sel.size||S.opt)return;
  S._done=false;S._refNote=null;S._aiLogged=false;$('#resBar').hidden=true;
  plog(`물리 최적화 시작 · 고른 기준 <b>${S.sel.size}개</b>`);busy(true);
  ban('<span class="big">준비 중</span><span class="t">형상 AI × 물리 AI</span>');
  await _opt();busy(false);
};
function ban(h){const b=$('#optBan');b.innerHTML=h;b.hidden=false;}
const _applyFrame=window.applyFrame;
window.applyFrame=function(f){
  const r=_applyFrame(f);
  if(f.stage!=='pick'&&f.stage!=='refine'){
    const rp=f.stage==='ai';
    ban(`<span class="big">${f.it}${rp?'':' / '+f.iters}</span><span class="t">AI 탐색 중 · 형상 AI × 물리 AI${rp?'<em>(계산 기록 재생)</em>':''}<small>무게 ${fmt(f.mass_g)} g · 값은 AI 예측</small></span>`);
    plog(`AI 탐색 <b>${f.it}회</b>${rp?' <em>(계산 기록 재생)</em>':''}`,true);
  }
  return r;
};
const _applyRefine=window.applyRefine;
window.applyRefine=function(f){
  const O=S.opt;
  if(O&&!S._aiLogged){S._aiLogged=true;plog(`AI 탐색 <b>${O.aiMax||'–'}회</b> 완료 <em>(계산 기록 재생)</em>`);}
  const r=_applyRefine(f);
  if(f.note&&f.note!==S._refNote){S._refNote=f.note;plog(esc(f.note));}
  ban(`<span class="big">${f.stage==='pick'?'후보':'정밀'}</span><span class="t">${f.stage==='pick'?'AI 후보 정밀 계산 → 선택':'정밀 최적화 중'}<em>(계산 기록 재생)</em><small>${esc(f.note||'')} · 무게 ${fmt(f.mass_g)} g</small></span>`);
  // 흔들림 창: 물리 AI 가 예측하지 않음 → 이 단계에서는 숨김 (검증에서 정밀 계산 분포로 채움)
  return r;
};
const _finish=window.finishOpt;
window.finishOpt=async function(r){
  const g=r.gate||{};S._done=true;
  ban('<span class="big">검증</span><span class="t">최종 형상 정밀 시뮬레이션 판정</span>');
  await _finish(r);
  const O=S.optLast||{},rows=(S.rows||[]).filter(m=>!m.ref),ok=rows.filter(m=>m.ok).length,n=rows.length;
  plog(`최종 검증 · 정밀 시뮬레이션 <b>${ok}/${n}</b> 충족 · ${fmt(g.mass_g)} g`);
  const dw=g.drawing;
  if(dw&&dw.mass_g)plog(`A3 제작 도면 ${dw.cached?'(같은 형상 · 저장된 도면)':`생성 <b>${dw.seconds} s</b>`} · 출력용 몸체 ${fmt(dw.mass_g)} g`);
  const m0=O.m0,m1=g.mass_g,d=m0?((m1-m0)/m0*100):null,rb=$('#resBar');
  rb.className='resbar'+(ok===n?'':' bad');
  rb.innerHTML=`<span class="big">${ok} / ${n}</span><span class="t">${ok===n?'목표 모두 충족':'미충족 '+(n-ok)+'개'} · 무게 <s>${fmt(m0)}</s> → <em>${fmt(m1)} g${d!=null?` (${d<0?'−':'+'}${Math.abs(d).toFixed(1)} %)`:''}</em></span><span class="tg">정밀 시뮬레이션 검증</span>`;
  rb.hidden=false;$('#optBan').hidden=true;busy(false);
  if(V3.cmp&&!V3.cmp.on)cmpToggle(true);
  stage('done');
};
const _vd=$('#vDraw').onclick;$('#vDraw').onclick=()=>{_vd();B.classList.toggle('drawing',!!V3.drawing);};
const _cmp=window.cmpToggle;
window.cmpToggle=function(on){_cmp(on);B.classList.toggle('cmpon',!!(V3.cmp&&V3.cmp.on));relayout();};

// ---------- 3D: 어두운 화면에 맞춰 자전거 · 전체 보기 색
if(window.V3&&V3.bike){
  const lift=o=>o.traverse(m=>{if(m.isMesh&&m.material&&m.material.color){const c=m.material.color;if(c.r+c.g+c.b<0.45){m.material=m.material.clone();m.material.color.setHex(0x5f6b7c);}}});
  lift(V3.bike);
}
window.NAV_BG=0x1b2433;window.NAV_INK='#cbd5e1';
stage('input');guide('1 입력','만들 제품과 조건을 문장, 스케치, 사진으로 넣습니다');
})();
