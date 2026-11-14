"""선택된 무작위 형상을 브라우저에서 넘겨 보는 뷰어(HTML, 파일 하나) 생성.

python experiments/make_viewer.py <data 폴더> <출력 폴더>
- 그룹마다 <그룹>.html (형상 데이터를 gzip+base64로 넣음, 인터넷 불필요) + index.html
- 그룹마다 <그룹>_shapes.npz (idx, occ 비트, meta) — 파이썬으로 직접 열어 보기용
표시: 칸(복셀) 경계를 한 번 흐리게(가우시안 근사) 한 뒤 표면 그물(surface nets)로 그려 깍둑 모양을 줄임.
     "칸 원본" 체크 시 흐림 없이 그림. 표시만 바뀌고 데이터·FEM은 칸 그대로.
"""
import os, sys, json, gzip, base64
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from fp08 import problems, datagen, shapes

NAMES = {'bike_pad50': '거치대 · 받침 50 mm', 'bike_pad80': '거치대 · 받침 80 mm (시연 기본)',
         'bike_pad120': '거치대 · 받침 120 mm', 'bike_pad80_free': '거치대 · 받침 80 mm · 화면 각도 자유(기둥 60 mm)', 'tvfeet_L300': 'TV 양발형 · 발끝 300 mm (다리 하나)',
         'tvfeet_L220': 'TV 양발형 · 발끝 220 mm (넘어짐 불합격 그룹)', 'tvped': 'TV 중앙형(받침대형)'}
FAM = {'A': 'A 직접 부재', 'B': 'B 트러스', 'Ctri': 'C 삼각 판', 'Cquad': 'C 사각 판', 'D': 'D 열린 껍데기'}


def b64gz(a):
    return base64.b64encode(gzip.compress(np.ascontiguousarray(a).tobytes(), 9)).decode()


def build(data, group, outdir, n_dropped=300):
    p = problems.get(group); g = p.grid
    idx, occ, meta = datagen.load_shapes(data, group)
    sel = json.load(open(os.path.join(data, group, 'selection.json'), encoding='utf-8'))
    reason = json.load(open(os.path.join(data, group, 'drop_reason.json'), encoding='utf-8'))
    # 제외된 예시 (허공 가지 / 울퉁불퉁 / 끊김) 일부도 함께 — 걸러낸 기준을 눈으로 확인
    cand, cmeta = {}, {}
    d = os.path.join(data, group, 'cand')
    for f in sorted(os.listdir(d)):
        if f.endswith('.npz'):
            z = np.load(os.path.join(d, f)); ms = json.loads(str(z['meta']))
            for i, o, m in zip(z['idx'], z['occ'], ms):
                cmeta[int(i)] = m
                r = reason.get(str(int(i)))
                if r in ('tips', 'rough', 'broken_over_quota'):
                    cand.setdefault(r, []).append((int(i), o, m))
    drop = []
    for r, L in cand.items():
        drop += [(i, o, dict(m, drop=r)) for i, o, m in L[:n_dropped // 3]]
    allidx = list(map(int, idx)) + [i for i, _, _ in drop]
    allocc = np.concatenate([np.packbits(occ, axis=1)[:, :], np.stack([o for _, o, _ in drop])]) if drop else np.packbits(occ, axis=1)
    meta = [dict(cmeta.get(int(i), {}), **m) for i, m in zip(idx, meta)]     # 품질 지표(가지·울퉁)는 후보 단계에서 계산
    allmeta = [dict(m, keep=1) for m in meta] + [m for _, _, m in drop]
    M = [[int(i), m.get('family', ''), round(m.get('vf', 0), 4), m.get('tips', -1), round(m.get('rough', 0), 1),
          int(bool(m.get('connected', True))), int(m.get('keep', 0)), m.get('drop', '')] for i, m in zip(allidx, allmeta)]
    np.savez_compressed(os.path.join(outdir, f'{group}_shapes.npz'), idx=np.array(list(map(int, idx))),
                        occ_bits=np.packbits(occ, axis=1), ne=g.ne, shape=np.array([g.nx, g.ny, g.nz]), h=g.h,
                        label=p.label, meta=json.dumps(meta, ensure_ascii=False))
    cfg = dict(group=group, name=NAMES[group], nx=g.nx, ny=g.ny, nz=g.nz, h=g.h, sym=int(p.sym_axis),
               ne=g.ne, nbytes=int(allocc.shape[1]), n=len(M), fam=FAM,
               sel={k: v for k, v in sel.items() if k != 'keep'})
    html = TEMPLATE.replace('__CFG__', json.dumps(cfg, ensure_ascii=False)) \
        .replace('__META__', json.dumps(M, ensure_ascii=False)) \
        .replace('__LABEL__', b64gz(p.label.astype(np.int8))).replace('__OCC__', b64gz(allocc))
    with open(os.path.join(outdir, f'{group}.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    return dict(group=group, keep=len(meta), dropped_shown=len(drop), sel=cfg['sel'])


TEMPLATE = r'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>무작위 형상 뷰어</title>
<style>
body{margin:0;font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;background:#f6f7f9;color:#1d2330}
header{padding:12px 16px;background:#fff;border-bottom:1px solid #e3e6ec;position:sticky;top:0;z-index:5}
h1{font-size:18px;margin:0 0 6px} .bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px}
select,button,input{font-size:13px;padding:3px 6px} #grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;padding:12px 16px}
.t{background:#fff;border:1px solid #e3e6ec;border-radius:8px;padding:4px;cursor:pointer} .t canvas{width:100%;display:block}
.c{font-size:11.5px;color:#5b6475;padding:2px 4px} .drop{border-color:#d9455f} .drop .c{color:#d9455f}
#modal{position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;align-items:center;justify-content:center;z-index:9}
#box{background:#fff;border-radius:10px;padding:10px;max-width:95vw} #big{cursor:grab;display:block;max-width:92vw}
.note{font-size:12px;color:#5b6475;margin-top:4px} .leg span{display:inline-block;width:10px;height:10px;margin:0 3px 0 8px;vertical-align:middle}
</style></head><body>
<header><h1 id="ttl"></h1>
<div class="bar">
 보기 <select id="show"><option value="keep">선택된 형상</option><option value="drop">제외된 예시</option><option value="all">전부</option></select>
 형식 <select id="fam"><option value="">전체</option></select>
 정렬 <select id="sort"><option value="idx">번호</option><option value="vf">재료 비율 ↑</option><option value="-vf">재료 비율 ↓</option><option value="-rough">울퉁불퉁 ↓</option><option value="-tips">허공 가지 ↓</option></select>
 <label><input type="checkbox" id="raw"> 칸 원본(다듬지 않음)</label>
 <button id="prev">◀</button><span id="pg"></span><button id="next">▶</button> 한 쪽 <select id="per"><option>24</option><option>48</option><option>96</option></select>
 <span class="leg"><span style="background:#e8833a"></span>설계(무작위) <span style="background:#5F5E5A"></span>고정부품 <span style="background:#7F77DD"></span>강체</span>
</div><div class="note" id="sel"></div></header>
<div id="grid"></div>
<div id="modal"><div id="box"><canvas id="big" width="900" height="600"></canvas>
<div class="note" id="bigc"></div><div class="note">마우스로 끌어서 회전 · 바깥을 누르면 닫기</div></div></div>
<script>
const CFG=__CFG__, META=__META__, LB64="__LABEL__", OB64="__OCC__";
let LABEL, OCC, view=[], page=0;
async function gun(b){const bin=Uint8Array.from(atob(b),c=>c.charCodeAt(0));
 const s=new Blob([bin]).stream().pipeThrough(new DecompressionStream('gzip'));return new Uint8Array(await new Response(s).arrayBuffer());}
// ---- 장(field) 만들기: 거울 복원 + 1칸 여백, 재료 종류(1 설계 2 고정 3 강체)
function field(k, raw){
 const {nx,ny,nz,sym}=CFG; const off=k*CFG.nbytes;
 const bit=e=>(OCC[off+(e>>3)]>>(7-(e&7)))&1;
 const F=[nx,ny,nz]; F[sym]*=2; const X=F[0]+2,Y=F[1]+2,Z=F[2]+2;
 const typ=new Uint8Array(X*Y*Z), v=new Float32Array(X*Y*Z);
 for(let kk=0;kk<nz;kk++)for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
  const e=(kk*ny+j)*nx+i, L=LABEL[e]; let t=0;
  if(L==1)t=2; else if(L==3)t=3; else if(L==0&&bit(e))t=1;
  if(!t)continue;
  for(const m of [0,1]){let c=[i,j,kk]; const n=[nx,ny,nz][sym];
   c[sym]= m? n-1-c[sym] : n+c[sym];
   const q=((c[2]+1)*Y+(c[1]+1))*X+(c[0]+1); typ[q]=t; v[q]=1;}}
 if(!raw){ // [1,4,1]/6 흐림을 세 축에 한 번씩 (1칸 두께 판도 사라지지 않게 약하게)
  const tmp=new Float32Array(v.length); const st=[1,X,X*Y], dm=[X,Y,Z];
  for(let a=0;a<3;a++){const s=st[a];
   for(let q=0;q<v.length;q++){const c=a==0?q%X:a==1?Math.floor(q/X)%Y:Math.floor(q/(X*Y));
    const l=c>0?v[q-s]:0, r=c<dm[a]-1?v[q+s]:0; tmp[q]=(l+4*v[q]+r)/6;}
   v.set(tmp);}}
 return {v,typ,X,Y,Z,raw};
}
// ---- 표면 그물(surface nets): 등위면 0.5 (원본은 0.5 경계 = 칸 모양)
function mesh(f){
 const {v,typ,X,Y,Z}=f, iso=f.raw?0.5:0.4, V=[], C=[], Q=[]; const vid=new Int32Array(X*Y*Z).fill(-1);
 const E=[[0,1],[2,3],[4,5],[6,7],[0,2],[1,3],[4,6],[5,7],[0,4],[1,5],[2,6],[3,7]];
 const co=[[0,0,0],[1,0,0],[0,1,0],[1,1,0],[0,0,1],[1,0,1],[0,1,1],[1,1,1]];
 for(let z=0;z<Z-1;z++)for(let y=0;y<Y-1;y++)for(let x=0;x<X-1;x++){
  let m=0, val=[], tt=0;
  for(let c=0;c<8;c++){const q=((z+co[c][2])*Y+(y+co[c][1]))*X+(x+co[c][0]); val.push(v[q]); if(v[q]>iso)m|=1<<c; tt=Math.max(tt,typ[q]==3?3:typ[q]==2?2:typ[q]);}
  if(m==0||m==255)continue;
  let px=0,py=0,pz=0,n=0;
  for(const [a,b] of E){const ia=val[a]>iso, ib=val[b]>iso; if(ia==ib)continue;
   const t=(iso-val[a])/(val[b]-val[a]); px+=co[a][0]+t*(co[b][0]-co[a][0]); py+=co[a][1]+t*(co[b][1]-co[a][1]); pz+=co[a][2]+t*(co[b][2]-co[a][2]); n++;}
  vid[(z*Y+y)*X+x]=V.length/3; V.push(x+px/n,y+py/n,z+pz/n); C.push(tt||1);}
 const st=[1,X,X*Y];
 for(let z=1;z<Z-1;z++)for(let y=1;y<Y-1;y++)for(let x=1;x<X-1;x++){
  const q=(z*Y+y)*X+x;
  for(let a=0;a<3;a++){const q2=q+st[a]; if((v[q]>iso)==(v[q2]>iso))continue;
   const b=(a+1)%3, c=(a+2)%3; const s1=st[b], s2=st[c];
   const cs=[q,q-s1,q-s1-s2,q-s2].map(t=>vid[t]); if(cs.some(t=>t<0))continue; Q.push(cs);}}
 return {V,C,Q};
}
const COL={1:[232,131,58],2:[95,94,90],3:[127,119,221]};
function draw(cv, M, yaw, pitch){
 const ctx=cv.getContext('2d'), W=cv.width, H=cv.height; ctx.fillStyle='#fff'; ctx.fillRect(0,0,W,H);
 const {V,C,Q}=M; if(!V.length)return;
 const cy=Math.cos(yaw), sy=Math.sin(yaw), cp=Math.cos(pitch), sp=Math.sin(pitch);
 const n=V.length/3, P=new Float32Array(n*3); let mn=[1e9,1e9],mx=[-1e9,-1e9];
 for(let i=0;i<n;i++){const x=V[3*i],y=V[3*i+1],z=V[3*i+2];
  const x1=cy*x-sy*y, y1=sy*x+cy*y; const y2=cp*y1-sp*z, z2=sp*y1+cp*z; // 화면: x1 가로, z2 세로(위), y2 깊이
  P[3*i]=x1;P[3*i+1]=-z2;P[3*i+2]=y2; mn[0]=Math.min(mn[0],x1);mx[0]=Math.max(mx[0],x1);mn[1]=Math.min(mn[1],-z2);mx[1]=Math.max(mx[1],-z2);}
 const s=0.92*Math.min(W/(mx[0]-mn[0]),H/(mx[1]-mn[1])), ox=(W-s*(mx[0]+mn[0]))/2, oy=(H-s*(mx[1]+mn[1]))/2;
 const order=Q.map((q,k)=>[ (P[3*q[0]+2]+P[3*q[1]+2]+P[3*q[2]+2]+P[3*q[3]+2]), k]).sort((a,b)=>b[0]-a[0]);
 const Ld=[0.35,-0.75,0.55];
 for(const [,k] of order){const q=Q[k];
  const a=q[0]*3,b=q[1]*3,c=q[2]*3,d=q[3]*3;
  const ux=P[c]-P[a],uy=P[c+1]-P[a+1],uz=P[c+2]-P[a+2], vx=P[d]-P[b],vy=P[d+1]-P[b+1],vz=P[d+2]-P[b+2];
  let nx=uy*vz-uz*vy, ny=uz*vx-ux*vz, nz=ux*vy-uy*vx; const l=Math.hypot(nx,ny,nz)||1;
  const sh=0.35+0.65*Math.abs((nx*Ld[0]+ny*Ld[1]+nz*Ld[2])/l);
  const col=COL[Math.max(C[q[0]],C[q[1]],C[q[2]],C[q[3]])]||COL[1];
  ctx.fillStyle=`rgb(${col[0]*sh|0},${col[1]*sh|0},${col[2]*sh|0})`; ctx.strokeStyle=ctx.fillStyle;
  ctx.beginPath(); for(const t of q)ctx.lineTo(ox+s*P[3*t],oy+s*P[3*t+1]); ctx.closePath(); ctx.fill(); ctx.stroke();}
}
const YAW0=CFG.group.startsWith('bike')?-0.55:-0.75, PITCH0=0.45;
function cap(m){const fam=CFG.fam[m[1]]||m[1];
 return `#${m[0]} · ${fam} · 재료 ${(100*m[2]).toFixed(1)}% · 가지 ${m[3]} · 울퉁 ${m[4]}`+(m[5]?'':' · 끊김')+(m[6]?'':` · 제외(${({tips:'허공 가지',rough:'울퉁불퉁',broken_over_quota:'끊김 초과'})[m[7]]||m[7]})`);}
function refresh(){
 const sh=document.getElementById('show').value, fam=document.getElementById('fam').value, so=document.getElementById('sort').value;
 view=META.map((m,k)=>[m,k]).filter(([m])=>(sh=='all'||(sh=='keep')==!!m[6])&&(!fam||m[1]==fam));
 const key={idx:m=>m[0],vf:m=>m[2],'-vf':m=>-m[2],'-rough':m=>-m[4],'-tips':m=>-m[3]}[so];
 view.sort((a,b)=>key(a[0])-key(b[0])); page=0; render();}
let token=0;
function render(){
 const per=+document.getElementById('per').value, g=document.getElementById('grid'); g.innerHTML='';
 const np=Math.max(1,Math.ceil(view.length/per)); page=Math.min(page,np-1);
 document.getElementById('pg').textContent=` ${page+1} / ${np} 쪽 (${view.length}개) `;
 const items=view.slice(page*per,(page+1)*per), my=++token, raw=document.getElementById('raw').checked;
 const cvs=items.map(([m,k])=>{const d=document.createElement('div'); d.className='t'+(m[6]?'':' drop');
  const c=document.createElement('canvas'); c.width=300; c.height=200; d.appendChild(c);
  const p=document.createElement('div'); p.className='c'; p.textContent=cap(m); d.appendChild(p);
  d.onclick=()=>openBig(m,k); g.appendChild(d); return [c,k];});
 let i=0; (function step(){ if(my!=token||i>=cvs.length)return; const [c,k]=cvs[i++]; draw(c,mesh(field(k,raw)),YAW0,PITCH0); requestAnimationFrame(step);})();
}
let BIG=null, yaw=YAW0, pitch=PITCH0;
function openBig(m,k){BIG=mesh(field(k,document.getElementById('raw').checked)); yaw=YAW0; pitch=PITCH0;
 document.getElementById('bigc').textContent=cap(m); document.getElementById('modal').style.display='flex'; draw(document.getElementById('big'),BIG,yaw,pitch);}
(function(){const c=document.getElementById('big'); let d=null;
 c.onmousedown=e=>{d=[e.clientX,e.clientY,yaw,pitch]; c.style.cursor='grabbing';};
 window.onmouseup=()=>{d=null;c.style.cursor='grab';};
 window.onmousemove=e=>{if(!d)return; yaw=d[2]+(e.clientX-d[0])*0.01; pitch=Math.max(-1.5,Math.min(1.5,d[3]+(e.clientY-d[1])*0.01)); draw(c,BIG,yaw,pitch);};
 document.getElementById('modal').onclick=e=>{if(e.target.id=='modal')e.target.style.display='none';};})();
(async()=>{
 document.getElementById('ttl').textContent=`${CFG.name} — 무작위 형상 ${META.filter(m=>m[6]).length}개 (${CFG.group})`;
 const s=CFG.sel; document.getElementById('sel').textContent=`후보 ${s.n_cand}개 → ${s.n_keep}개 선택 · 제외: 허공 가지(골격 끝점 > ${s.max_tips}) ${s.dropped.tips||0}, 울퉁불퉁(상위 10%) ${s.dropped.rough||0}, 끊김 초과 ${s.dropped.broken_over_quota||0}, 비율 맞추며 안 뽑힘 ${s.dropped.not_sampled||0} · 선택 형식 ${JSON.stringify(s.family_keep)} · 표시는 칸 경계를 다듬은 모습(데이터·FEM은 칸 그대로)`;
 const fs=document.getElementById('fam'); for(const [k,v] of Object.entries(CFG.fam)){const o=document.createElement('option');o.value=k;o.textContent=v;fs.appendChild(o);}
 LABEL=new Int8Array((await gun(LB64)).buffer); OCC=await gun(OB64);
 for(const id of ['show','fam','sort']) document.getElementById(id).onchange=refresh;
 document.getElementById('per').onchange=render; document.getElementById('raw').onchange=render;
 document.getElementById('prev').onclick=()=>{page=Math.max(0,page-1);render();};
 document.getElementById('next').onclick=()=>{page++;render();};
 refresh();})();
</script></body></html>'''

INDEX = '''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>08 무작위 형상</title>
<style>body{font-family:"Malgun Gothic",sans-serif;max-width:860px;margin:24px auto;color:#1d2330}td,th{border-bottom:1px solid #ddd;padding:6px 8px;font-size:14px}table{border-collapse:collapse;width:100%}</style></head><body>
<h2>FormProof 08 — 학습용 무작위 형상 (그룹당 5,000개)</h2>
<p>그룹 이름을 누르면 뷰어가 열립니다 (인터넷 불필요, Chrome·Edge 권장). 썸네일을 누르면 크게 보고 마우스로 돌려 볼 수 있습니다.
보이는 표면은 칸 경계를 한 번 다듬은 모습이고, 학습·FEM 데이터는 칸 그대로입니다("칸 원본" 체크로 비교).</p>
<table><tr><th>그룹</th><th>후보 → 선택</th><th>제외 (허공 가지 / 울퉁불퉁 / 끊김 초과)</th><th>선택된 형식</th></tr>__ROWS__</table>
<p style="font-size:13px;color:#5b6475">파이썬으로 보기: <code>np.load("그룹_shapes.npz")</code> → occ_bits(np.unpackbits 후 [:ne]), label(0 설계 1 고정 2 빈곳 3 강체), shape(nx,ny,nz, 요소 번호 e=(k*ny+j)*nx+i), meta.
같은 번호는 <code>fp08.shapes.make_shape(problem, 그룹, 번호)</code>로 언제든 똑같이 다시 만들어짐.</p>
<p style="font-size:13px;color:#5b6475">생성 __DATE__ · 코드 sosopapa 브랜치 08_물리AI_최적형상/fp08 · 뷰어 experiments/make_viewer.py</p></body></html>'''

if __name__ == '__main__':
    data, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rows = ''
    for k in problems.GROUPS:
        r = build(data, k, out)
        s = r['sel']; dr = s['dropped']
        rows += (f'<tr><td><a href="{k}.html">{NAMES[k]}</a></td><td>{s["n_cand"]:,} → {s["n_keep"]:,}</td>'
                 f'<td>{dr.get("tips",0)} / {dr.get("rough",0)} / {dr.get("broken_over_quota",0)}</td>'
                 f'<td style="font-size:12px">{", ".join(f"{FAM[f]} {n}" for f, n in s["family_keep"].items())}</td></tr>')
        print(k, r['keep'], r['dropped_shown'], flush=True)
    import datetime
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(
        INDEX.replace('__ROWS__', rows).replace('__DATE__', datetime.date.today().isoformat()))
