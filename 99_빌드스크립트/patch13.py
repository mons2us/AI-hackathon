t=open('make_ss_v13.js').read()
def rep(a,b):
    global t
    assert a in t,a[:80]; t=t.replace(a,b)
rep("out/FormProof_첨부자료_삼성양식_v12.pptx","out/FormProof_첨부자료_삼성양식_v13.pptx")
# cover chips
old=t[t.index("const fl=['아이디어·기존 제품'"):t.index("txt(s,'2026.11  ·  팀장")]
rep(old,"""const fl=['입력','3D 설계 생성','성능 확인','재설계','결과'],fw0=[1.4,2.0,1.6,1.4,1.4];
let fx=0.8;fl.forEach((t,i)=>{const w=fw0[i];s.addShape(pres.shapes.RECTANGLE,{x:fx,y:5.75,w,h:0.55,fill:{color:(i===2||i===3)?HX.dk2:HX.accent1},line:{color:'FFFFFF',width:1}});txt(s,t,{x:fx,y:5.75,w,h:0.55,fontSize:12.5,bold:true,color:'FFFFFF',align:'center',valign:'middle'});fx+=w;if(i<4){txt(s,i===2?'⇄':'›',{x:fx,y:5.75,w:0.45,h:0.55,fontSize:i===2?18:20,color:'FFFFFF',align:'center',valign:'middle'});fx+=0.45}});
""")
# slide 3 native figure
rep("pic(s,'shots/g1_s3.png',0.6,1.6,8.9,8.9*625/1950);","""{const X0=0.6,Y0=1.6,GW=0.2,CWg=(8.9-4*GW)/5,CHg=2.85,IW=CWg-0.16,IH=IW*840/1100;
const G=[['1 · 입력','텍스트 요청',null,'빠진 조건은 AI가 질문'],['2 · 3D 설계 생성','형상 + 물리 조건','shots/f4_hu_shape.png',null],['3 · 성능 확인','힘·열 흐름 계산','shots/f4_hu_flow.png','힘·온도 집중부와 불필요 재료 파악'],['4 · 재설계','조건 유지 구조 재설계','shots/f4_ai_flow.png','접이 구조 유지, 옆판 경량화, 방열 경로 배치'],['5 · 결과','제작 파일 출력','shots/f4_ai_shape.png',null]];
G.forEach((g,k)=>{const x=X0+k*(CWg+GW),core=k===2||k===3;
 s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:Y0,w:CWg,h:CHg,rectRadius:0.08,fill:{color:core?HX.dk2:HX.lt2},line:{color:core?HX.dk2:HX.lt2,width:0}});
 txt(s,g[0],{x:x+0.08,y:Y0+0.07,w:CWg-0.16,h:0.22,fontSize:8.5,bold:true,color:core?HX.accent6:HX.accent1,valign:'middle'});
 txt(s,g[1],{x:x+0.08,y:Y0+0.3,w:CWg-0.16,h:0.42,fontSize:11,bold:true,color:core?'FFFFFF':HX.dk1,valign:'top',lineSpacingMultiple:1.0});
 const iy=Y0+0.76,ix=x+0.08;
 if(g[2])pic(s,g[2],ix,iy,IW,IH);
 if(k===0){s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:ix,y:iy,w:IW,h:IH+0.12,rectRadius:0.08,fill:{color:'FFFFFF'},line:{color:'A7B0C0',width:1}});
  txt(s,'“게임·영상 오래 보면 폰이 뜨거워. 가볍고 접히는 거치대 만들어줘”',{x:ix+0.06,y:iy+0.04,w:IW-0.12,h:IH+0.04,fontSize:8.5,color:HX.dk1,valign:'middle',lineSpacingMultiple:1.1})}
 if(g[3])txt(s,g[3],{x:x+0.08,y:iy+IH+0.2,w:CWg-0.16,h:0.55,fontSize:8.5,color:core?'D9E0F2':HX.accent5,lineSpacingMultiple:1.1});
 if(k===1){const P=(px,py)=>[ix+px/1100*IW,iy+py/840*IH];const OR='F5A800',BL='3B9BFF';
  let [a,b]=P(430,470),[c,d]=P(430,680);s.addShape(pres.shapes.LINE,{x:a,y:b,w:0,h:d-b,line:{color:OR,width:2.5,endArrowType:'triangle'}});
  [a,b]=P(110,120);[c,d]=P(250,195);s.addShape(pres.shapes.LINE,{x:a,y:b,w:c-a,h:d-b,line:{color:OR,width:2.5,endArrowType:'triangle'}});
  [[70,760],[500,770]].forEach(q=>{const [u,v]=P(q[0],q[1]);s.addShape(pres.shapes.ISOSCELES_TRIANGLE,{x:u,y:v,w:0.11,h:0.09,fill:{color:BL},line:{color:BL,width:0}})});
  [[340,70],[740,110]].forEach(q=>{const [u,v]=P(q[0],q[1]);const r=62/1100*IW;s.addShape(pres.shapes.OVAL,{x:u-r,y:v-r,w:2*r,h:2*r,fill:{type:'none'},line:{color:'FFFFFF',width:1.25,dashType:'dash'}})});
  txt(s,[{text:'→ ',options:{color:OR,bold:true}},{text:'하중  '},{text:'▲ ',options:{color:BL}},{text:'고정',options:{breakLine:true}},{text:'◌ ',options:{bold:true}},{text:'접이부 유지'}],{x:x+0.08,y:iy+IH+0.2,w:CWg-0.16,h:0.5,fontSize:8.5,color:HX.accent5,lineSpacingMultiple:1.15})}
 if(k===4){let cx=ix;['STEP','STL','도면'].forEach(f=>{const w=0.12+f.length*0.085;s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:cx,y:iy+IH+0.08,w,h:0.2,rectRadius:0.03,fill:{color:'FFFFFF'},line:{color:'A7B0C0',width:0.75}});txt(s,f,{x:cx,y:iy+IH+0.08,w,h:0.2,fontSize:7.5,bold:true,align:'center',valign:'middle'});cx+=w+0.05});
  txt(s,'옆판 약 1/3↓\\n온도 상승 약 70%↓',{x:x+0.08,y:iy+IH+0.34,w:CWg-0.16,h:0.45,fontSize:9.5,bold:true,color:HX.accent1,lineSpacingMultiple:1.1})}
 if(k<4)s.addShape(pres.shapes.ISOSCELES_TRIANGLE,{x:x+CWg+0.05,y:Y0+0.45,w:0.12,h:0.1,rotate:90,fill:{color:'A7B0C0'},line:{color:'A7B0C0',width:0}});
});}""")
# slide 4 native framework
rep("pic(s,'shots/fw_s4.png',0.6,1.62,12.13,12.13*720/2150);","""{const Y=1.62,H=3.45,GP=0.3,U=(12.13-3*GP)/6.0,W=[1.02*U,1.25*U,2.65*U,1.08*U];let X=[0.6];for(let i=1;i<4;i++)X.push(X[i-1]+W[i-1]+GP);
const bl=(arr,col,fs)=>arr.map((b,i)=>({text:b,options:{bullet:{indent:11},breakLine:i<arr.length-1,color:col,fontSize:fs}}));
const plain=[[0,'입력','요청·자료',['텍스트·음성','스케치·이미지','문서·STEP'],[['해커톤','hk']]],[1,'3D 설계 생성','형상 + 물리 조건',['하중·고정 위치','빠진 조건 질문','CAD 형상 생성'],[['해커톤','hk']]],[3,'결과','제작 파일',['제작 형상 변환','설계 파일·도면','성능 리포트'],[['3D 화면','ok'],['파일 출력','hk']]]];
plain.forEach(p=>{const x=X[p[0]],w=W[p[0]];s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:Y,w,h:H,rectRadius:0.1,fill:{color:HX.lt2},line:{color:HX.lt2,width:0}});
 txt(s,p[1],{x:x+0.18,y:Y+0.16,w:w-0.3,h:0.26,fontSize:11,bold:true,color:HX.accent1,valign:'middle'});
 txt(s,p[2],{x:x+0.18,y:Y+0.48,w:w-0.3,h:0.42,fontSize:17,bold:true,valign:'middle'});
 txt(s,bl(p[3],'3A4250',13),{x:x+0.18,y:Y+1.05,w:w-0.3,h:1.5,lineSpacingMultiple:1.3});
 let cx=x+0.18;p[4].forEach(c=>{cx+=chip(s,cx,Y+H-0.45,c[0],c[1],9.5)+0.06});});
{const x=X[2],w=W[2];s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:Y,w,h:H,rectRadius:0.1,fill:{color:HX.dk2},line:{color:HX.dk2,width:0}});
 txt(s,'물리 기반 AI (핵심)',{x:x+0.18,y:Y+0.16,w:w-0.3,h:0.26,fontSize:11,bold:true,color:HX.accent6,valign:'middle'});
 const SW=(w-0.36-0.75)/2,SY=Y+0.55,SH=2.3;
 [[x+0.18,'① 성능 확인','계산 + 검증',['구조·열 해석','자동 검증']],[x+0.18+SW+0.75,'② 재설계','구조 개선',['Topology 최적화','조건 조합 탐색','물리 AI 가속']]].forEach(q=>{
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:q[0],y:SY,w:SW,h:SH,rectRadius:0.08,fill:{color:'FFFFFF',transparency:92},line:{color:HX.accent6,width:0.75,transparency:50}});
  txt(s,q[1],{x:q[0]+0.14,y:SY+0.12,w:SW-0.25,h:0.24,fontSize:10.5,bold:true,color:HX.accent6,valign:'middle'});
  txt(s,q[2],{x:q[0]+0.14,y:SY+0.42,w:SW-0.25,h:0.34,fontSize:15,bold:true,color:'FFFFFF',valign:'middle'});
  txt(s,bl(q[3],'D9E0F2',12.5),{x:q[0]+0.14,y:SY+0.9,w:SW-0.25,h:1.3,lineSpacingMultiple:1.3})});
 const ax=x+0.18+SW;txt(s,'→\\n미충족',{x:ax,y:SY+0.45,w:0.75,h:0.6,fontSize:10,bold:true,color:HX.accent6,align:'center',valign:'middle'});
 txt(s,'←\\n재확인',{x:ax,y:SY+1.2,w:0.75,h:0.6,fontSize:10,bold:true,color:HX.accent6,align:'center',valign:'middle'});
 let cx=x+0.18;[['엔진·최적화','ok'],['물리 AI·자동 검증','hk']].forEach(c=>{cx+=chip(s,cx,Y+H-0.45,c[0],c[1],9.5)+0.06});}
for(let i=0;i<3;i++)s.addShape(pres.shapes.ISOSCELES_TRIANGLE,{x:X[i]+W[i]+0.08,y:Y+0.6,w:0.16,h:0.13,rotate:90,fill:{color:'A7B0C0'},line:{color:'A7B0C0',width:0}});
let lx=0.6;lx+=chip(s,lx,Y+H+0.2,'사전 검증','ok',9.5)+0.08;txt(s,'개념 검증 완료',{x:lx,y:Y+H+0.2,w:1.4,h:0.25,fontSize:10.5,color:HX.accent5,valign:'middle'});lx+=1.45;
lx+=chip(s,lx,Y+H+0.2,'해커톤','hk',9.5)+0.08;txt(s,'해커톤 기간 개발',{x:lx,y:Y+H+0.2,w:1.6,h:0.25,fontSize:10.5,color:HX.accent5,valign:'middle'});
txt(s,'↺ 사용자 수정 요청 시 재설계',{x:8.7,y:Y+H+0.2,w:4.03,h:0.25,fontSize:10.5,color:HX.accent5,align:'right',valign:'middle'});}""")
open('make_ss_v13.js','w').write(t); print('ok')
