import re
def rep(s,a,b,n=1):
  assert s.count(a)==n,(a[:50],s.count(a)); return s.replace(a,b)
# framework figure
f=open('fw_v14.html').read()
old=f[f.index('<div class="c"><span class="n">생성형 AI'):f.index('<div class="c core">')]
new='<div class="c"><span class="n">3D 설계 생성</span><b>형상 + 물리 조건</b><ul><li>요청 해석, 빠진 조건 질의</li><li>하중·고정 위치·재료·목표 정리</li><li>지킬 곳·비울 곳·바꿀 곳 지정</li><li>CAD 코드로 치수 수정 가능한 3D 형상</li></ul><div class="st"><i class="hk">해커톤 개발</i></div></div>\n  '
f=f.replace(old,new);open('fw_v15.html','w').write(f)
# docx
s=open('make_docx_v57.js').read()
s=rep(s,"['2. 생성형 AI','조건 정리 → 처음 설계 23.4 g','치수·부품·기준값 정리 → 기본 설계']","['2. 3D 설계 생성','형상 + 물리 조건(하중·접이·지킬 곳) → 처음 설계 23.4 g','형상 + 물리 조건(치수·부품·기준값) → 기본 설계']")
L=s.split('\n');i=[k for k,l in enumerate(L) if l.startswith("        B([run('생성형 AI(LLM 에이전트): '")][0]
L[i]="        B([run('3D 설계 생성: ',{bold:true}),run('요청을 3D 형상과 물리 조건(하중·고정 위치·재료·목표, 지킬 곳·비울 곳·바꿀 곳)으로 변환, 빠진 조건은 질문, LLM이 파이썬 CAD 코드(CadQuery)로 치수 수정 가능한 형상 생성, 실물 사진에서는 형상·치수 추출')]),"
s='\n'.join(L)
s=rep(s,"생성형 AI (LLM 에이전트: 요청 해석·조건 질의·도구 실행)","3D 설계 생성 (요청 해석·물리 조건 정의·CAD 코드 생성)")
s=rep(s,"입력·생성형 AI 단계는 해커톤에서 자동화","입력·3D 설계 생성 단계는 해커톤에서 자동화")
s=rep(s,"fw_v14.png","fw_v15.png");s=rep(s,"pv_grid_v4.png","pv_grid_v5.png");s=rep(s,"_v57.docx","_v58.docx")
open('make_docx_v58.js','w').write(s)
# pptx
t=open('make_ss_v9.js').read()
t=rep(t,"const STG=['입력','생성형 AI','성능 확인','재설계','결과'];","const STG=['입력','3D 설계 생성','성능 확인','재설계','결과'];")
t=rep(t,"'조건 정리 → 처음 설계 23.4 g'","'형상 + 물리 조건 → 처음 설계 23.4 g'")
t=rep(t,"'치수·부품·기준값 → 기본 설계'","'형상 + 물리 조건 → 기본 설계'")
t=rep(t,"T(s,'FormProof 프레임워크','입력 → 생성형 AI(요청 해석·3D 설계 생성) → 물리 기반 AI(성능 확인 ⇄ 재설계) → 결과');","T(s,'FormProof 프레임워크','입력 → 3D 설계 생성(형상 + 물리 조건) → 물리 기반 AI(성능 확인 ⇄ 재설계) → 결과');")
t=rep(t,"fw_s2c.png","fw_s3c.png")
t=rep(t,"out/FormProof_첨부자료_삼성양식_v9.pptx","out/FormProof_첨부자료_삼성양식_v10.pptx")
open('make_ss_v10.js','w').write(t)
m=open('mk_cells.py').read()
m=m.replace("STG5=['1. 입력','2. 생성형 AI','3. 성능 확인','4. 재설계','5. 결과']","STG5=['1. 입력','2. 3D 설계 생성','3. 성능 확인','4. 재설계','5. 결과']").replace("pv_grid_v4.png","pv_grid_v5.png")
open('mk_cells.py','w').write(m)
