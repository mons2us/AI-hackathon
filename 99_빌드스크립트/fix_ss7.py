s=open('make_ss_v6.js').read()
L=s.split('\n')
a=[k for k,l in enumerate(L) if l.startswith('const cellRow=')][0]
b=[k for k,l in enumerate(L) if l.startswith('// ───── 5. 사전 검증 ① 거치대')][0]
L[a:b]=[r"""const N5=5,CW=(12.13-0.4)/5,CY=2.88,CH=CW*560/600;
const cellRow=(s,key,caps)=>{for(let k=0;k<N5;k++){const x=0.6+k*(CW+0.1);
  if(key==='1'&&k===4){box(s,x,CY,CW,CH,{fill:'0E1A26'});const vh=CW*734/1280;s.addMedia({type:'video',path:'out/FormProof_설계과정영상_v7.mp4',cover:'data:image/jpeg;base64,'+fs.readFileSync('shots/vid7_cover.jpg').toString('base64'),x,y:CY+(CH-vh)/2,w:CW,h:vh})}
  else pic(s,'cells/d'+key+'_'+(k+1)+'.png',x,CY,CW,CH);
  txt(s,caps[k],{x,y:CY+CH+0.05,w:CW,h:0.24,fontSize:9.5,color:C.accent5,align:'center'})}};
const STG=['입력','생성형 AI','성능 확인','재설계','결과'];
const TAG=[['수동 정리','m'],['수동·템플릿','m'],['실제 계산','c'],['실제 계산','c'],['3D 화면','c']];
const stages=(s,y,items)=>{for(let k=0;k<N5;k++){const x=0.6+k*(CW+0.1);const core=k===2||k===3;
  box(s,x,y,CW,1.15,{fill:core?'E8ECF8':HX.lt2});
  txt(s,(k+1)+'. '+STG[k],{x:x+0.1,y:y+0.06,w:CW-0.2,h:0.26,fontSize:11,bold:true,color:core?C.accent1:C.text1,valign:'middle'});
  const t=TAG[k],tc=t[1]==='c'?HX.accent3:'A7B0C0',tw=0.12+t[0].length*0.1;s.addShape(pres.shapes.RECTANGLE,{x:x+CW-tw-0.08,y:y+0.09,w:tw,h:0.2,fill:{color:tc},line:{color:tc,width:0}});txt(s,t[0],{x:x+CW-tw-0.08,y:y+0.09,w:tw,h:0.2,fontSize:7.5,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
  txt(s,items[k],{x:x+0.1,y:y+0.38,w:CW-0.2,h:0.74,fontSize:9.5,color:C.accent5,lineSpacingMultiple:1.1});
  if(k===2)txt(s,'⇄',{x:x+CW-0.04,y:y+0.4,w:0.18,h:0.3,fontSize:13,bold:true,color:C.accent1,align:'center',valign:'middle'});
  else if(k<4)s.addImage({data:arr,x:x+CW-0.005,y:y+0.52,w:0.11,h:0.11})}};"""]
s='\n'.join(L)
import re
s=re.sub(r"stages\(s,1\.6,\['텍스트: [^\]]*\]\);","stages(s,1.6,['텍스트: “폰이 뜨거워지고 배터리도 빨리 닳아. 가볍고 접히는 거치대”','조건 정리(옆판 120×100×8 mm × 2 · 터치 5 N · 힌지 접이) → 처음 설계 23.4 g','3D FEM 힘 집중·변위 · 2D 열전도 온도 · 1 mm 격자 재확인','Topology 최적화 80회(구조·열) 약 2분 → 재확인: 5 N 변위 처음 이하','옆판 15.6 g · 방열판 온도 상승 약 70%↓ · 3D 화면·영상']);",s)
s=re.sub(r"cellRow\(s,'1',\[[^\]]*\]\);","cellRow(s,'1',['텍스트 요청','조건 정리 → 처음 설계 23.4 g','힘 집중·온도 확인','Topology 재설계 과정','AI 설계 15.6 g · 영상']);",s)
s=re.sub(r"stages\(s,1\.6,\['3D 얼굴 스캔[^\]]*\]\);","stages(s,1.6,['3D 얼굴 스캔(공개 모델) + AR 글래스 조사 문서(구성품·분해 자료·기준값)','얼굴 치수 4개·부품·기준값(42 °C, ±14 g) 정리 → 기본 설계 52.5 g','16개 항목 판정: 통과 12 · 주의 4 (코 하중 40.9 gf)','15.6만 조합 탐색 약 2.5초 → 재확인: 통과 14 · 주의 2','48.0 g · 코 하중 34.5 gf · 착용·부품 분해']);",s)
s=re.sub(r"cellRow\(s,'2',\[[^\]]*\]\);","cellRow(s,'2',['얼굴 스캔 + 조사 문서','기본 설계 52.5 g','16개 항목: 주의 4','15.6만 조합 탐색','48.0 g · 주의 2']);",s)
for x,y in [("const fl=['아이디어·기존 제품','3D 설계','성능 검증','더 나은 구조로 재설계','제작 파일'];","const fl=['아이디어·기존 제품','3D 설계','성능 확인','더 나은 구조로 재설계','제작 파일'];"),
 ("T(s,'FormProof 프레임워크','입력 → 요청 해석 → 3D 설계 생성 → 물리 기반 AI → 검증 절차 → 결과 제공');","T(s,'FormProof 프레임워크','입력 → 생성형 AI(요청 해석·3D 설계 생성) → 물리 기반 AI(성능 확인 ⇄ 재설계) → 결과');"),
 ("pic(s,'shots/fw_s1c.png',0.6,1.62,12.13,12.13*834/2250);","pic(s,'shots/fw_s2c.png',0.6,1.62,12.13,12.13*829/2250);"),
 ("T(s,'핵심 기술: 물리 기반 AI와 검증 절차','계산 → 판단 → 재배치를 반복하고, 검증을 통과한 결과만 검증 완료로 표시');","T(s,'핵심 기술: 성능 확인과 재설계','물리 엔진으로 확인하고 Topology 최적화로 재설계하는 과정을 반복, 검증을 통과한 결과만 검증 완료로 표시');"),
 ("label(s,'물리 기반 AI (재설계 엔진)',0.6,1.6,6);","label(s,'물리 기반 AI 구성',0.6,1.6,6);"),
 ("label(s,'검증 절차 (사전 검증 결과)',6.9,1.6,5.8);","label(s,'성능 확인의 검증 항목 (사전 검증 결과)',6.9,1.6,5.8);"),
 ("'텍스트 입력 · 프레임워크 단계별 사전 검증 (물리 기반 AI·검증은 실제 계산, 앞 단계는 수동·템플릿 → 해커톤에서 자동화)'","'텍스트 입력 · 성능 확인·재설계는 실제 계산, 입력·생성형 AI 단계는 수동·템플릿 (해커톤에서 자동화)'"),
 ("out/FormProof_첨부자료_삼성양식_v6.pptx","out/FormProof_첨부자료_삼성양식_v7.pptx")]:
  assert s.count(x)==1,x[:50]; s=s.replace(x,y)
s=s.replace("y:5.38,w:12.13,h:0.26,fontSize:9.5,color:C.accent1,bold:true}","y:5.4,w:12.13,h:0.26,fontSize:9.5,color:C.accent1,bold:true}")
open('make_ss_v7.js','w').write(s)
