s=open('stand_template_v2.html',encoding='utf-8').read()
css='''.dg{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:14px}
@media (max-width:860px){.dg{grid-template-columns:1fr}}
.dg figure{margin:0;background:var(--panel2);border-radius:10px;padding:10px 10px 12px;display:flex;flex-direction:column;gap:6px;min-width:0}
.dg figcaption{font-size:13px;color:var(--muted);padding:0 4px}
.dg svg{width:100%;height:auto;display:block}
.dg svg text{font-family:var(--sans);fill:var(--fg)}
</style>'''
s=s.replace('</style>',css,1)
sec='''  <div class="card">
    <h2>구성 · 이렇게 생겼습니다 (AI 설계 결과로 그림)</h2>
    <div class="dg">
      <figure><svg id="dgA" viewBox="0 0 660 500" role="img" aria-label="분해 조립도"></svg><figcaption>분해 조립도 · 옆판과 방열판 무늬는 계산 결과를 그대로 그렸습니다.</figcaption></figure>
      <figure><svg id="dgB" viewBox="0 0 520 500" role="img" aria-label="옆에서 본 힘과 열의 길"></svg><figcaption>옆에서 본 모습 · <b style="color:var(--cyan);font-weight:500">힘의 길</b>은 옆판을 타고 앞발·뒷발로, <b style="color:var(--hot);font-weight:500">열의 길</b>은 방열판을 타고 아래 금속으로.</figcaption></figure>
    </div>
  </div>

  <div class="card">
    <div class="sec"><span class="pill">① 구조</span>'''
s=s.replace('''  <div class="card">
    <div class="sec"><span class="pill">① 구조</span>''',sec,1)
js=r'''
/* 구성 그림 */
function mkImg(w,h,fn){const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d'),im=g.createImageData(w,h);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const col=fn(x,y);if(!col)continue;const p=(y*w+x)*4;im.data[p]=col[0];im.data[p+1]=col[1];im.data[p+2]=col[2];im.data[p+3]=col[3]??255}
  g.putImageData(im,0,0);return c.toDataURL()}
function buildDiagram(){
  const nx=ST.nelx,ny=ST.nely,sx=dec(ST.ai.x),hx=dec(HT.ai.x),N=HN;
  const solidAt=(i,j)=>{for(let k=0;k<ST.nelz;k++)if(sx[i+nx*(j+ny*k)]>0.5)return true;return false};
  const frameImg=col=>mkImg(nx,ny,(x,y)=>solidAt(x,ny-1-y)?col:null);
  const plateImg=mkImg(N,N,(x,y)=>hx[x*N+y]>0.5?[205,214,222]:[38,52,68]);
  const shades=[[96,110,126],[122,136,152],[150,163,178],[178,190,203],[224,231,238]].map(frameImg);
  const T=tv,Nn=nv,P0=[2*xL(ST.y0+0.5),2*(ST.y0+0.5)];
  /* ---- 분해 조립도 ---- */
  {const s=2,ox=250,oy=430,P=(x,y,z)=>[ox+s*(x+0.55*z),oy-s*(y+0.32*z)];let o='';
   o+=`<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="#8b9bb0"/></marker></defs>`;
   const tbl=[P(-70,0,-70),P(140,0,-70),P(140,0,70),P(-70,0,70)];o+=`<polygon points="${tbl.map(p=>p.join(',')).join(' ')}" fill="#1b2735" stroke="#223042"/>`;
   const frame=z0=>{let r='';[4,2,0,-2,-4].forEach((dz,q)=>{const p=P(0,100,z0+dz);r+=`<image href="${shades[q]}" x="0" y="0" width="${nx}" height="${ny}" preserveAspectRatio="none" style="image-rendering:auto" transform="matrix(${s*2},0,0,${s*2},${p[0]+s*0.55*0},${p[1]})"/>`});return r};
   o+=frame(44);
   /* 연결 막대 */
   {const a=P(110,3,-40),b=P(110,3,40);o+=`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#8a97a6" stroke-width="9" stroke-linecap="round"/>`}
   /* 방열판 (앞으로 35 mm 빼서) */
   const ex=d=>[-Nn[0]*d,-Nn[1]*d];
   const e1=ex(38),tl=[P0[0]+84*T[0]+e1[0],P0[1]+84*T[1]+e1[1]];const pp=P(tl[0],tl[1],-40);
   const a=s*0.55,b=-s*0.32,c=-T[0]*s,d=T[1]*s;
   const corner=(u,v)=>{const w=[tl[0]-v*T[0],tl[1]-v*T[1]];return P(w[0],w[1],-40+u)};
   o+=`<polygon points="${[corner(0,0),corner(80,0),corner(80,80),corner(0,80)].map(p=>p.join(',')).join(' ')}" fill="#1c2836" transform="translate(4,4)" opacity=".7"/>`;
   o+=`<image href="${plateImg}" width="${N}" height="${N}" preserveAspectRatio="none" transform="matrix(${a*0.8},${b*0.8},${c*0.8},${d*0.8},${pp[0]},${pp[1]})"/>`;
   /* 받침 턱 속 금속 */
   {const q=[P0[0]+1*T[0],P0[1]-1];const m1=P(q[0],q[1],-10),m2=P(q[0],q[1],10);o+=`<line x1="${m1[0]}" y1="${m1[1]}" x2="${m2[0]}" y2="${m2[1]}" stroke="#f5b942" stroke-width="8" stroke-linecap="round"/>`}
   o+=frame(-44);
   /* 폰 */
   const e2=ex(95),pt=[P0[0]+160*T[0]+e2[0],P0[1]+160*T[1]+e2[1]],pb=[P0[0]+e2[0],P0[1]+e2[1]];
   const ph=[P(pt[0],pt[1],-38),P(pt[0],pt[1],38),P(pb[0],pb[1],38),P(pb[0],pb[1],-38)];
   const off=[-Nn[0]*8,-Nn[1]*8],ph2=[[pt[0]+off[0],pt[1]+off[1],-38],[pt[0]+off[0],pt[1]+off[1],38],[pb[0]+off[0],pb[1]+off[1],38],[pb[0]+off[0],pb[1]+off[1],-38]].map(q=>P(...q));
   o+=`<polygon points="${ph.map(p=>p.join(',')).join(' ')}" fill="#0a121a" stroke="#3a4c60"/>`;
   o+=`<polygon points="${ph2.map(p=>p.join(',')).join(' ')}" fill="#101b26" stroke="#3a4c60"/>`;
   {const sc=ph2.map((p,i)=>{const cx=(ph2[0][0]+ph2[2][0])/2,cy=(ph2[0][1]+ph2[2][1])/2;return[cx+(p[0]-cx)*0.9,cy+(p[1]-cy)*0.92]});o+=`<polygon points="${sc.map(p=>p.join(',')).join(' ')}" fill="#1f5d73" opacity=".75"/>`}
   /* 조립 방향 점선 */
   {const m=P(P0[0]+60*T[0],P0[1]+60*T[1],0),m2=P(P0[0]+60*T[0]+e2[0]*0.55,P0[1]+60*T[1]+e2[1]*0.55,0);o+=`<line x1="${m2[0]}" y1="${m2[1]}" x2="${m[0]}" y2="${m[1]}" stroke="#8b9bb0" stroke-dasharray="4 4" marker-end="url(#ah)"/>`}
   /* 라벨 */
   const lab=(p,tx,ty,t1,t2,col)=>`<line x1="${p[0]}" y1="${p[1]}" x2="${tx}" y2="${ty}" stroke="${col}" stroke-width="1"/><circle cx="${p[0]}" cy="${p[1]}" r="3" fill="${col}"/><text x="${tx+(tx>p[0]?4:-4)}" y="${ty-4}" font-size="14" font-weight="500" text-anchor="${tx>p[0]?'start':'end'}" style="fill:${col}">${t1}</text><text x="${tx+(tx>p[0]?4:-4)}" y="${ty+13}" font-size="12" text-anchor="${tx>p[0]?'start':'end'}" style="fill:#8b9bb0">${t2}</text>`;
   o+=lab(P(pt[0]-40*T[0],pt[1]-40*T[1]+0,-20),70,40,'폰','게임 중 발열 5 W (가정)','#e6edf3');
   o+=lab(corner(40,25),70,150,'② 등판 방열판','알루미늄 나뭇가지 무늬 + PLA 틀','#f2643a');
   o+=lab(P(2*xL(30)+14,58,-44),40,330,'① 옆판 × 2','PLA 3D 출력 · AI 구조','#3fc1d6');
   o+=lab(P(P0[0]+1,P0[1]-1,8),150,478,'③ 받침 턱 속 금속','열이 빠지는 곳','#f5b942');
   o+=lab(P(110,3,30),560,470,'④ 연결 막대','두 옆판 고정','#8b9bb0');
   $('dgA').innerHTML=o}
  /* ---- 옆에서 본 힘·열의 길 ---- */
  {const s=2.15,ox=150,oy=455,P=(x,y)=>[ox+s*x,oy-s*y];let o='';
   o+=`<defs><marker id="ac" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="#3fc1d6"/></marker><marker id="ah2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="#f2643a"/></marker>
   <linearGradient id="hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2643a"/><stop offset="1" stop-color="#f5b942"/></linearGradient></defs>`;
   {const a=P(-60,0),b=P(130,0);o+=`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#2c3b4e" stroke-width="2"/>`}
   {const p=P(0,100);o+=`<image href="${shades[4]}" width="${nx}" height="${ny}" preserveAspectRatio="none" opacity=".92" transform="matrix(${s*2},0,0,${s*2},${p[0]},${p[1]})"/>`}
   const L=(t,d)=>[P0[0]+t*T[0]-d*Nn[0],P0[1]+t*T[1]-d*Nn[1]];
   const poly=(pts,f,extra='')=>`<polygon points="${pts.map(q=>P(...q).join(',')).join(' ')}" fill="${f}" ${extra}/>`;
   o+=poly([L(2,0.2),L(88,0.2),L(88,2.2),L(2,2.2)],'url(#hg)');
   o+=poly([L(0,3),L(160,3),L(160,11),L(0,11)],'#0e1822','stroke="#3a4c60"');
   o+=poly([L(4,11),L(156,11),L(156,11.8),L(4,11.8)],'#1f5d73');
   {const q=P(P0[0]-1,P0[1]-2);o+=`<rect x="${q[0]-7}" y="${q[1]-5}" width="14" height="10" rx="2" fill="#f5b942"/>`}
   /* 힘 */
   for(const t of[62,78,94]){const a=L(t,30),b=L(t,13);const A=P(...a),B=P(...b);o+=`<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#3fc1d6" stroke-width="2.5" marker-end="url(#ac)"/>`}
   {const t=P(...L(95,30));o+=`<text x="${t[0]-6}" y="${t[1]-8}" font-size="14" font-weight="500" text-anchor="end" style="fill:#3fc1d6">터치 5 N</text>`}
   const top=P(2*xL(46)+4,92),fr=P(14,4),rr=P(112,4),mid=P(2*xL(26)+12,52);
   o+=`<path d="M${top[0]},${top[1]} Q${P(86,52)[0]},${P(86,52)[1]} ${rr[0]},${rr[1]}" fill="none" stroke="#3fc1d6" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ac)"/>`;
   o+=`<path d="M${top[0]},${top[1]} Q${mid[0]},${mid[1]} ${fr[0]},${fr[1]}" fill="none" stroke="#3fc1d6" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ac)"/>`;
   {const p=P(84,62);o+=`<text x="${p[0]+8}" y="${p[1]}" font-size="13" style="fill:#3fc1d6">힘의 길</text><text x="${p[0]+8}" y="${p[1]+16}" font-size="12" style="fill:#8b9bb0">앞발·뒷발로 나눠 전달</text>`}
   {const a=P(2,1),b=P(16,1),c=P(104,1),d=P(120,1);o+=`<line x1="${a[0]}" y1="${a[1]+4}" x2="${b[0]}" y2="${b[1]+4}" stroke="#f5b942" stroke-width="5"/><line x1="${c[0]}" y1="${c[1]+4}" x2="${d[0]}" y2="${d[1]+4}" stroke="#f5b942" stroke-width="5"/>`}
   /* 열 */
   for(const t of[40,80,120]){const A=P(...L(t,18)),B=P(...L(t,4));o+=`<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#f2643a" stroke-width="2" marker-end="url(#ah2)" opacity=".9"/>`}
   {const A=P(...L(70,-4)),B=P(...L(10,-4));o+=`<line x1="${A[0]}" y1="${A[1]}" x2="${B[0]}" y2="${B[1]}" stroke="#f2643a" stroke-width="2.5" marker-end="url(#ah2)"/>`}
   {const q=P(P0[0]-1,P0[1]-2);o+=`<line x1="${q[0]}" y1="${q[1]+8}" x2="${q[0]}" y2="${q[1]+30}" stroke="#f5b942" stroke-width="2.5" marker-end="url(#ah2)"/>`}
   {const p=P(...L(122,24));o+=`<text x="${p[0]-6}" y="${p[1]}" font-size="13" text-anchor="end" style="fill:#f2643a">열의 길</text><text x="${p[0]-6}" y="${p[1]+16}" font-size="12" text-anchor="end" style="fill:#8b9bb0">폰 → 방열판 → 아래 금속</text>`}
   {const q=P(P0[0]-1,P0[1]-2);o+=`<text x="${q[0]-12}" y="${q[1]+28}" font-size="12" text-anchor="end" style="fill:#f5b942">바닥 금속판·팬으로 배출 (가정)</text>`}
   {const p=P(...L(150,22));o+=`<text x="${p[0]-4}" y="${p[1]}" font-size="13" text-anchor="end" style="fill:#e6edf3">폰</text>`}
   {const p=P(2*xL(50)+2,100);o+=`<text x="${p[0]+10}" y="${p[1]-8}" font-size="12" style="fill:#8b9bb0">등받이 65°</text>`}
   $('dgB').innerHTML=o}}
try{buildDiagram()}catch(e){console.error(e)}
'''
s=s.replace("V=init3();if(!V)",js+"V=init3();if(!V)",1)
open('stand_template_v2.html','w',encoding='utf-8').write(s)
