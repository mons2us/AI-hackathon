s=open('stand_template_v2.html',encoding='utf-8').read()
def R(a,b):
    global s
    assert a in s,a[:50]; s=s.replace(a,b,1)
R("""  const frameImg=col=>mkImg(nx,ny,(x,y)=>solidAt(x,ny-1-y)?col:null);
  const plateImg=mkImg(N,N,(x,y)=>hx[x*N+y]>0.5?[205,214,222]:[38,52,68]);""",
"""  /* 부드러운 경계: 3x3 블러 후 확대 보간, 0.5 등고선 주변을 반투명 처리 */
  const smooth=(w,h,get,U)=>{const g=new Float32Array(w*h);for(let y=0;y<h;y++)for(let x=0;x<w;x++)g[x+w*y]=get(x,y);
    const b=new Float32Array(w*h);for(let y=0;y<h;y++)for(let x=0;x<w;x++){let sm=0,ww=0;for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const X=x+dx,Y=y+dy;if(X<0||Y<0||X>=w||Y>=h)continue;const q=(dx?1:2)*(dy?1:2);sm+=q*g[X+w*Y];ww+=q}b[x+w*y]=sm/ww}
    return (px,py)=>{const fx=Math.min(w-1.001,Math.max(0,px/U-0.5)),fy=Math.min(h-1.001,Math.max(0,py/U-0.5)),i=Math.floor(fx),j=Math.floor(fy),u=fx-i,v=fy-j,a=k=>b[k];
      return (1-v)*((1-u)*a(i+w*j)+u*a(i+1+w*j))+v*((1-u)*a(i+w*(j+1))+u*a(i+1+w*(j+1)))}};
  const UP=8,fs=smooth(nx,ny,(x,y)=>solidAt(x,ny-1-y)?1:0,UP);
  const aa=v=>Math.max(0,Math.min(1,(v-0.42)/0.16));
  const frameImg=col=>mkImg(nx*UP,ny*UP,(x,y)=>{const a=aa(fs(x,y));return a>0?[col[0],col[1],col[2],Math.round(a*255)]:null});
  const UPp=4,ps=smooth(N,N,(x,y)=>hx[x*N+y]>0.5?1:0,UPp);
  const plateImg=mkImg(N*UPp,N*UPp,(x,y)=>{const a=aa(ps(x,y)),A=[205,214,222],B=[38,52,68];return [0,1,2].map(i=>Math.round(B[i]+(A[i]-B[i])*a))});""")
s=s.replace('width="${nx}" height="${ny}" preserveAspectRatio="none" style="image-rendering:auto" transform="matrix(${s*2},0,0,${s*2},','width="${nx*UP}" height="${ny*UP}" preserveAspectRatio="none" transform="matrix(${s*2/UP},0,0,${s*2/UP},')
R('<image href="${plateImg}" width="${N}" height="${N}" preserveAspectRatio="none" transform="matrix(${a*0.8},${b*0.8},${c*0.8},${d*0.8},','<image href="${plateImg}" width="${N*UPp}" height="${N*UPp}" preserveAspectRatio="none" transform="matrix(${a*0.8/UPp},${b*0.8/UPp},${c*0.8/UPp},${d*0.8/UPp},')
R('<image href="${shades[4]}" width="${nx}" height="${ny}" preserveAspectRatio="none" opacity=".92" transform="matrix(${s*2},0,0,${s*2},','<image href="${shades[4]}" width="${nx*UP}" height="${ny*UP}" preserveAspectRatio="none" opacity=".92" transform="matrix(${s*2/UP},0,0,${s*2/UP},')
# 라벨: 왼쪽/오른쪽 여백에 밑줄형
R("""const lab=(p,tx,ty,t1,t2,col)=>`<line x1="${p[0]}" y1="${p[1]}" x2="${tx}" y2="${ty}" stroke="${col}" stroke-width="1"/><circle cx="${p[0]}" cy="${p[1]}" r="3" fill="${col}"/><text x="${tx+(tx>p[0]?4:-4)}" y="${ty-4}" font-size="14" font-weight="500" text-anchor="${tx>p[0]?'start':'end'}" style="fill:${col}">${t1}</text><text x="${tx+(tx>p[0]?4:-4)}" y="${ty+13}" font-size="12" text-anchor="${tx>p[0]?'start':'end'}" style="fill:#8b9bb0">${t2}</text>`;""",
"""const lab=(p,tx,ty,t1,t2,col,right)=>{const x0=right?tx:tx,x1=right?tx+150:tx+150,jx=right?x0:x1;return `<line x1="${p[0]}" y1="${p[1]}" x2="${jx}" y2="${ty}" stroke="${col}" stroke-width="1"/><line x1="${x0}" y1="${ty}" x2="${x1}" y2="${ty}" stroke="${col}" stroke-width="1"/><circle cx="${p[0]}" cy="${p[1]}" r="3" fill="${col}"/><text x="${x0}" y="${ty-6}" font-size="14" font-weight="500" style="fill:${col}">${t1}</text><text x="${x0}" y="${ty+15}" font-size="12" style="fill:#8b9bb0">${t2}</text>`};""")
R("o+=lab(P(pt[0]-40*T[0],pt[1]-40*T[1]+0,-20),70,40,'폰','게임 중 발열 5 W (가정)','#e6edf3');","o+=lab(P(pt[0]-40*T[0],pt[1]-40*T[1]+0,-20),490,60,'폰','게임 중 발열 5 W (가정)','#e6edf3',1);")
R("o+=lab(corner(40,25),70,150,'② 등판 방열판','알루미늄 나뭇가지 무늬 + PLA 틀','#f2643a');","o+=lab(corner(55,20),490,150,'② 등판 방열판','알루미늄 나뭇가지 무늬 + PLA 틀','#f2643a',1);")
R("o+=lab(P(2*xL(30)+14,58,-44),40,330,'① 옆판 × 2','PLA 3D 출력 · AI 구조','#3fc1d6');","o+=lab(P(2*xL(30)+14,58,-44),12,300,'① 옆판 × 2','PLA 3D 출력 · AI 구조','#3fc1d6');")
R("o+=lab(P(P0[0]+1,P0[1]-1,8),150,478,'③ 받침 턱 속 금속','열이 빠지는 곳','#f5b942');","o+=lab(P(P0[0]+1,P0[1]-1,-6),12,410,'③ 받침 턱 속 금속','열이 빠지는 곳','#f5b942');")
R("o+=lab(P(110,3,30),560,470,'④ 연결 막대','두 옆판 고정','#8b9bb0');","o+=lab(P(110,3,30),490,420,'④ 연결 막대','두 옆판 고정','#8b9bb0',1);")
R('const s=2,ox=250,oy=430,','const s=2,ox=290,oy=440,')
R('<text x="${q[0]-12}" y="${q[1]+28}" font-size="12" text-anchor="end" style="fill:#f5b942">바닥 금속판·팬으로 배출 (가정)</text>','<text x="${q[0]+10}" y="${q[1]+36}" font-size="12" style="fill:#f5b942">바닥 금속판·팬으로 배출 (가정)</text>')
open('stand_template_v2.html','w',encoding='utf-8').write(s)
