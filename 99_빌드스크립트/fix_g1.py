import sys
src,dst=sys.argv[1],sys.argv[2]
t=open(src).read()
R=[('<span class="n">1 · 요청 입력</span>','<span class="n">1 · 입력</span>'),
('이미지·STEP 입력 가능, AI의 조건 확인·정리','이미지·문서·STEP 입력 가능, 빠진 조건은 AI가 질문'),
('<div class="c"><span class="n">2 · 3D 설계</span><b>AI가 3D 설계 생성</b>','<div class="c"><span class="n">2 · 3D 설계 생성</span><b>형상 + 물리 조건</b>'),
('<p>요청 기반 첫 설계</p>','<p>하중·접이·지킬 곳 정의, 처음 설계</p>'),
('<div class="c"><span class="n">3 · 성능 확인</span>','<div class="c core"><span class="n">3 · 성능 확인</span>'),
('<span class="n">4 · 다시 설계</span>','<span class="n">4 · 재설계</span>'),
('<span class="n">5 · 출력</span><b>설계·도면 파일</b>','<span class="n">5 · 결과</span><b>설계 파일 + 성능 결과</b>'),
]
for a,b in R:
    assert a in t,(src,a); t=t.replace(a,b)
open(dst,'w').write(t)
