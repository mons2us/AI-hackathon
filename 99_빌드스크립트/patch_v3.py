s=open('stand_template_v3.html',encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert a in s,a[:60]; s=s.replace(a,b,cnt)
# 범례 CSS
R('.dg svg text{font-family:var(--sans);fill:var(--fg)}','''.dg svg text{font-family:var(--sans);fill:var(--fg)}
.lg{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:12.5px;color:var(--muted);padding:2px 2px 4px}
.lg span{display:inline-flex;align-items:center;gap:6px}
.lg .c{display:inline-block;font-size:11px;font-weight:500;color:#06222a;background:var(--cyan);border-radius:4px;padding:0 6px;line-height:18px}
.lg .i{display:inline-block;font-size:11px;color:var(--muted);border:1px dashed var(--dim);border-radius:4px;padding:0 6px;line-height:16px}''')
R('<h2>구성 · 이렇게 생겼습니다 (AI 설계 결과로 그림)</h2>','''<h2>구성 · 이렇게 생겼습니다</h2>
    <div class="lg"><span><b class="c">계산</b>계산 결과를 그대로 그림 (옆판 모양, 방열판 무늬)</span><span><b class="i">설명용</b>이해를 돕기 위해 그린 것 (점선 · 흐린 글씨)</span><span><b class="i">입력</b>계산에 넣은 조건 (터치 힘, 발 위치, 열 빠지는 곳)</span></div>''')
R('<figcaption>분해 조립도 · 옆판과 방열판 무늬는 계산 결과를 그대로 그렸습니다.</figcaption>','<figcaption>분해 조립도 · 폰·연결 막대·금속·배치 간격은 설명용입니다.</figcaption>')
R('''<figcaption>옆에서 본 모습 · <b style="color:var(--cyan);font-weight:500">힘의 길</b>은 옆판을 타고 앞발·뒷발로, <b style="color:var(--hot);font-weight:500">열의 길</b>은 방열판을 타고 아래 금속으로.</figcaption>''',
'''<figcaption>옆에서 본 모습 · 점선 화살표(힘의 길·열의 길)는 계산 결과를 보고 흐름을 개념적으로 표시한 것입니다. 실제 계산된 힘·온도 분포는 위 3D 화면의 색과 아래 비교 그림에 있습니다.</figcaption>''')
# 라벨 함수: kind 'c'(계산) / 'i'(설명용)
R("const lab=(p,tx,ty,t1,t2,col,right)=>{","const lab=(p,tx,ty,t1,t2,col,right,kind)=>{const ill=kind==='i',dash=ill?' stroke-dasharray=\"3 3\"':'',op=ill?' opacity=\".75\"':'';const badge=kind==='c'?`<rect x=\"${tx+150-34}\" y=\"${ty-19}\" width=\"34\" height=\"16\" rx=\"3\" fill=\"#3fc1d6\"/><text x=\"${tx+150-17}\" y=\"${ty-7}\" font-size=\"10.5\" font-weight=\"500\" text-anchor=\"middle\" style=\"fill:#06222a\">계산</text>`:`<rect x=\"${tx+150-40}\" y=\"${ty-19}\" width=\"40\" height=\"16\" rx=\"3\" fill=\"none\" stroke=\"#5d6f84\" stroke-dasharray=\"3 2\"/><text x=\"${tx+150-20}\" y=\"${ty-7}\" font-size=\"10.5\" text-anchor=\"middle\" style=\"fill:#8b9bb0\">설명용</text>`;")
R('return `<line x1="${p[0]}" y1="${p[1]}" x2="${jx}" y2="${ty}" stroke="${col}" stroke-width="1"/><line x1="${x0}" y1="${ty}" x2="${x1}" y2="${ty}" stroke="${col}" stroke-width="1"/><circle cx="${p[0]}" cy="${p[1]}" r="3" fill="${col}"/><text x="${x0}" y="${ty-6}" font-size="14" font-weight="500" style="fill:${col}">${t1}</text>',
  'return `<g${op}><line x1="${p[0]}" y1="${p[1]}" x2="${jx}" y2="${ty}" stroke="${col}" stroke-width="1"${dash}/><line x1="${x0}" y1="${ty}" x2="${x1}" y2="${ty}" stroke="${col}" stroke-width="1"${dash}/><circle cx="${p[0]}" cy="${p[1]}" r="3" fill="${col}"/><text x="${x0}" y="${ty-6}" font-size="14" font-weight="500" style="fill:${col}">${t1}</text>${badge}')
R('<text x="${x0}" y="${ty+15}" font-size="12" style="fill:#8b9bb0">${t2}</text>`};','<text x="${x0}" y="${ty+15}" font-size="12" style="fill:#8b9bb0">${t2}</text></g>`};')
R("'폰','게임 중 발열 5 W (가정)','#e6edf3',1);","'폰','발열 5 W는 가정','#e6edf3',1,'i');")
R("'② 등판 방열판','알루미늄 무늬 + PLA 틀','#f2643a',1);","'② 등판 방열판','무늬 = 열 계산 결과','#f2643a',1,'c');")
R("'① 옆판 × 2','PLA 3D 출력 · AI 구조','#3fc1d6');","'① 옆판 × 2','모양 = 구조 계산 결과','#3fc1d6',0,'c');")
R("'③ 받침 턱 속 금속','열이 빠지는 곳','#f5b942');","'③ 받침 턱 속 금속','열 빠지는 곳 (입력 조건)','#f5b942',0,'i');")
R("'④ 연결 막대','두 옆판 고정','#8b9bb0',1);","'④ 연결 막대','계산에 포함 안 됨','#8b9bb0',1,'i');")
# 설명용 도형 점선·흐리게
R('o+=`<polygon points="${ph.map(p=>p.join(\',\')).join(\' \')}" fill="#0a121a" stroke="#3a4c60"/>`;','o+=`<g opacity=".8"><polygon points="${ph.map(p=>p.join(\',\')).join(\' \')}" fill="#0a121a" stroke="#5d6f84" stroke-dasharray="5 4"/>`;')
R('o+=`<polygon points="${ph2.map(p=>p.join(\',\')).join(\' \')}" fill="#101b26" stroke="#3a4c60"/>`;','o+=`<polygon points="${ph2.map(p=>p.join(\',\')).join(\' \')}" fill="#101b26" stroke="#5d6f84" stroke-dasharray="5 4"/>`;')
R('o+=`<polygon points="${sc.map(p=>p.join(\',\')).join(\' \')}" fill="#1f5d73" opacity=".75"/>`}','o+=`<polygon points="${sc.map(p=>p.join(\',\')).join(\' \')}" fill="#1f5d73" opacity=".75"/></g>`}')
R('stroke="#8a97a6" stroke-width="9" stroke-linecap="round"/>`}','stroke="#8a97a6" stroke-width="9" stroke-linecap="round" stroke-dasharray="2 3" opacity=".8"/>`}')
# 옆 모습: 입력/개념 표시
R('font-size="14" font-weight="500" text-anchor="end" style="fill:#3fc1d6">터치 5 N</text>`}','font-size="14" font-weight="500" text-anchor="end" style="fill:#3fc1d6">터치 5 N</text><text x="${t[0]-6}" y="${t[1]+8}" font-size="11" text-anchor="end" style="fill:#8b9bb0">입력 조건</text>`}')
R('style="fill:#3fc1d6">힘의 길</text>','style="fill:#3fc1d6">힘의 길 <tspan style="fill:#8b9bb0;font-size:11px">(개념 표시)</tspan></text>')
R('text-anchor="end" style="fill:#f2643a">열의 길</text>','text-anchor="end" style="fill:#f2643a">열의 길 <tspan style="fill:#8b9bb0;font-size:11px">(개념 표시)</tspan></text>')
R('{const p=P(...L(150,22));o+=`<text x="${p[0]-4}" y="${p[1]}" font-size="13" text-anchor="end" style="fill:#e6edf3">폰</text>`}','{const p=P(...L(150,22));o+=`<text x="${p[0]-4}" y="${p[1]}" font-size="13" text-anchor="end" style="fill:#e6edf3">폰 <tspan style="fill:#8b9bb0;font-size:11px">(설명용)</tspan></text>`}')
R('{const p=P(0,100);o+=`<image','{const p=P(0,100),q=P(60,100);o+=`<rect x="${q[0]-17}" y="${q[1]-14}" width="34" height="16" rx="3" fill="#3fc1d6"/><text x="${q[0]}" y="${q[1]-2}" font-size="10.5" font-weight="500" text-anchor="middle" style="fill:#06222a">계산</text><text x="${q[0]+22}" y="${q[1]-2}" font-size="12" style="fill:#8b9bb0">옆판 모양</text>`;o+=`<image')
# 3D 화면 안내
R('<div class="tag" id="tag"></div>','<div class="tag" id="tag"></div>\n      <div class="tag" style="top:56px;bottom:auto;font-size:11.5px;color:var(--muted)">계산 결과: 옆판·방열판 형상과 색 · 설명용: 폰·연결 막대·금속 막대</div>')
# 계산 조건 문구
R('3D 선형 탄성 유한요소(60×50×4 요소, 2 mm), 위상 최적화 <span id="itS">—</span>회 반복(약 <span id="tS2">—</span>초).','3D 선형 탄성 유한요소, 형상은 2 mm 격자(60×50×4 요소)에서 위상 최적화 <span id="itS">—</span>회 반복(약 <span id="tS2">—</span>초). 흔들림 수치는 같은 형상을 1 mm 격자(4.8만 요소)로 다시 계산한 값(2 mm 격자는 차이를 과대평가해 교체). 1 mm 격자에서 처음부터 다시 최적화해도 차이는 1.33배로 비슷.')
open('stand_template_v3.html','w',encoding='utf-8').write(s)
