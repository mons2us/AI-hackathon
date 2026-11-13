from PIL import Image,ImageDraw,ImageFont
W,H=600,560;F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
NAVY=(15,30,90);BLUE=(20,40,160);LG=(242,244,249)
L=lambda f:Image.open(f).convert('RGB')
def cover(im,w=W,h=H,ax=.5,ay=.5):
  r=max(w/im.width,h/im.height);im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
  x=int((im.width-w)*ax);y=int((im.height-h)*ay);return im.crop((x,y,x+w,y+h))
def contain(im,w=W,h=H,bg=None):
  bg=bg or im.getpixel((2,2));r=min(w/im.width,h/im.height);im=im.resize((round(im.width*r),round(im.height*r)),Image.LANCZOS)
  o=Image.new('RGB',(w,h),bg);o.paste(im,((w-im.width)//2,(h-im.height)//2));return o
def card(lines,title,w=W,h=H):
  o=Image.new('RGB',(w,h),NAVY);d=ImageDraw.Draw(o);d.text((34,34),title,font=ImageFont.truetype(FB,34),fill=(175,192,245))
  y=110
  for t,sz in lines:
    d.text((34,y),t,font=ImageFont.truetype(F,sz),fill=(255,255,255));y+=sz+18
  return o
def frames(path,n,idx):
  im=L(path);fw=im.width//n;return [im.crop((i*fw,0,(i+1)*fw,im.height)) for i in idx]
C={}
C['1_1']=card([('“폰이 뜨거워져.',44),('가볍고 접히는',44),('방열 거치대',44),('만들어줘.”',44)],'텍스트 입력')
C['1_2']=contain(L('shots/domain_fold3.png'))
C['1_3']=cover(L('shots/f4_hu_flow.png'))
fr=frames('shots/fold_frames.png',5,[1,2,3,4]);t=Image.new('RGB',(fr[0].width*2+6,fr[0].height*2+6),(20,20,30))
for k,f in enumerate(fr): t.paste(f,((k%2)*(f.width+6),(k//2)*(f.height+6)))
C['1_4']=contain(t,bg=(20,20,30))
a,b=L('shots/f4_sH.png'),L('shots/f4_sI.png');t=Image.new('RGB',(a.width+b.width+8,a.height),(14,26,38));t.paste(a,(0,0));t.paste(b,(a.width+8,0))
C['1_5']=contain(t,bg=(14,26,38))
C['1_6']=cover(L('shots/f4_ai_flow.png'))
face=cover(L('shots/ff_wire_c.png'),300,H,.5,.4);doc=cover(L('ar/sum_parts.png').crop((372,80,1632,1320)),300,H,0,0)
o=Image.new('RGB',(W,H),'white');o.paste(face,(0,0));o.paste(doc,(300,0));ImageDraw.Draw(o).line((300,0,300,H),fill=(200,205,215),width=3);C['2_1']=o
C['2_2']=cover(L('ar/b_face_panel.png').crop((0,80,660,720)),W,H,.5,0)
C['2_3']=cover(L('ar/b_viewer0.png').crop((150,60,1350,800)),W,H,.5,.4)
C['2_4']=contain(L('ar/b_top0.png'),bg=(255,255,255))
sm=L('ar/hi_summary_opt.png');ck=L('ar/b_checks1.png');ck=ck.resize((1038,round(ck.height*1038/ck.width)));t=Image.new('RGB',(1038,sm.height+1300),'white');t.paste(sm,(0,0));t.paste(ck.crop((0,0,1038,1290)),(0,sm.height+10));C['2_5']=cover(t,W,H,.5,0)
v1=cover(L('ar/b_viewer1.png').crop((200,120,1300,760)),W,300,.5,.4);ex=cover(L('ar/b_viewer_exp1.png'),W,260,.4,.35)
o=Image.new('RGB',(W,H),'white');o.paste(v1,(0,0));o.paste(ex,(0,300));ImageDraw.Draw(o).line((0,300,W,300),fill=(200,205,215),width=3);C['2_6']=o
for k,v in C.items(): v.save(f'cells/c{k}.png')
# grid for docx
STG=['1. 입력','2. 요청 해석','3. 3D 설계 생성','4. 물리 기반 AI','5. 검증','6. 결과 제공']
CAP={'1':['텍스트 요청','설계 영역·조건 정리','처음 설계 23.4 g','재료 재배치 과정','처음 | AI (5 N 변위 이하)','AI 설계 15.6 g'],
     '2':['얼굴 스캔 + 조사 문서','얼굴 치수·부품 구성','기본 설계 52.5 g','하중·무게중심·온도 계산','16개 항목 판정','48.0 g 착용·부품 분해']}
G=16;LW=90;HH=60;CH=52
gw=LW+6*W+5*G;gh=HH+2*(H+CH)+G
g=Image.new('RGB',(gw,gh),'white');d=ImageDraw.Draw(g);fb=ImageFont.truetype(FB,30);fc=ImageFont.truetype(F,28)
for k in range(6):
  x=LW+k*(W+G);core=k in(3,4);d.rectangle((x,0,x+W,HH-8),fill=BLUE if core else (230,234,244));d.text((x+18,10),STG[k],font=fb,fill=(255,255,255) if core else (26,26,26))
for r,key in enumerate(['1','2']):
  y=HH+r*(H+CH+G);d.text((14,y+H//2-40),'①' if key=='1' else '②',font=ImageFont.truetype(FB,56),fill=BLUE)
  for k in range(6):
    x=LW+k*(W+G);g.paste(C[f'{key}_{k+1}'],(x,y));d.text((x+4,y+H+8),CAP[key][k],font=fc,fill=(60,66,80))
g.save('shots/pv_grid_v2.png');print(g.size)

# ---- 5-stage set
D={}
D['1_1']=C['1_1'];D['1_2']=C['1_3']
a,b=L('shots/f4_sH.png'),L('shots/st_cH.png');b=b.resize((round(b.width*a.height/b.height),a.height));t=Image.new('RGB',(a.width+b.width+8,a.height),(14,26,38));t.paste(a,(0,0));t.paste(b,(a.width+8,0))
D['1_3']=contain(t,bg=(14,26,38));D['1_4']=C['1_4'];D['1_5']=C['1_6']
D['2_1']=C['2_1'];D['2_2']=C['2_3']
sm=L('ar/hi_summary.png');tp=contain(L('ar/b_top0.png'),W,H-140,bg=(255,255,255));o=Image.new('RGB',(W,H),'white');o.paste(cover(sm,W,140,0,.5),(0,0));o.paste(tp,(0,140));D['2_3']=o
op=L('ar/hi_opt.png');o=Image.new('RGB',(W,H),'white');o.paste(contain(op,W,250,bg=(255,255,255)),(0,0));o.paste(contain(L('ar/b_top1.png'),W,H-260,bg=(255,255,255)),(0,260));ImageDraw.Draw(o).line((20,252,W-20,252),fill=(200,205,215),width=3);D['2_4']=o
D['2_5']=C['2_6']
for k,v in D.items(): v.save(f'cells/d{k}.png')
STG5=['1. 입력','2. 3D 설계 생성','3. 성능 확인','4. 재설계','5. 결과']
CAP5={'1':['텍스트 요청','처음 설계 23.4 g','힘 집중·온도 확인','Topology 재설계','AI 설계 15.6 g'],
      '2':['얼굴 스캔 + 조사 문서','기본 설계 52.5 g','16개 항목: 주의 4','15.6만 조합 탐색','48.0 g · 주의 2']}
gw=LW+5*W+4*G;g=Image.new('RGB',(gw,gh),'white');d=ImageDraw.Draw(g)
for k in range(5):
  x=LW+k*(W+G);core=k in(2,3);d.rectangle((x,0,x+W,HH-8),fill=BLUE if core else (230,234,244));d.text((x+18,10),STG5[k],font=fb,fill=(255,255,255) if core else (26,26,26))
for r,key in enumerate(['1','2']):
  y=HH+r*(H+CH+G);d.text((14,y+H//2-40),'①' if key=='1' else '②',font=ImageFont.truetype(FB,56),fill=BLUE)
  for k in range(5):
    x=LW+k*(W+G);g.paste(D[f'{key}_{k+1}'],(x,y));d.text((x+4,y+H+8),CAP5[key][k],font=fc,fill=(60,66,80))
g.save('shots/pv_grid_v3.png');print('grid5',g.size)

# ---- case 2 rebuilt from AR simulator visuals (minimal text)
E2={}
face=cover(L('shots/ff_wire_c.png'),300,H,.5,.4);t2=L('ar/sum_type2.png');fr=contain(t2.crop((60,150,380,300)),300,200,bg=(255,255,255));tp=contain(t2.crop((450,140,750,365)),300,330,bg=(255,255,255));ty=Image.new('RGB',(300,H),'white');ty.paste(fr,(0,15));ty.paste(tp,(0,220))
o=Image.new('RGB',(W,H),'white');o.paste(face,(0,0));o.paste(ty,(300,0));ImageDraw.Draw(o).line((300,0,300,H),fill=(210,214,222),width=3);E2['1']=o
E2['2']=contain(L('ar/b_viewer0.png').crop((90,30,1370,830)))
E2['3']=contain(L('ar/b_top0.png').crop((0,0,1408,1010)),bg=(255,255,255))
o=Image.new('RGB',(W,H),'white');dd=ImageDraw.Draw(o);ft=ImageFont.truetype(FB,30)
for k,f in enumerate(['ar/c_cut_iso0.png','ar/c_cut_iso1.png']):
  im=contain(L(f).crop((110,170,1200,790)),W,H//2-4);o.paste(im,(0,k*(H//2+4)))
  t='전' if k==0 else '후';dd.rectangle((10,k*(H//2+4)+10,58,k*(H//2+4)+54),fill=BLUE);dd.text((19,k*(H//2+4)+12),t,font=ft,fill=(255,255,255))
E2['4']=o
E2['5']=contain(L('ar/b_top1.png').crop((0,0,1408,1010)),bg=(255,255,255))
for k,v in E2.items(): v.save(f'cells/d2_{k}.png');D['2_'+k]=v
CAP5['2']=['얼굴 스캔 + 조사 문서','기본 설계','16개 항목: 주의 4','부품 배치 재설계','코 하중 34.5 gf · 주의 2']
g=Image.new('RGB',(gw,gh),'white');d=ImageDraw.Draw(g)
for k in range(5):
  x=LW+k*(W+G);core=k in(2,3);d.rectangle((x,0,x+W,HH-8),fill=BLUE if core else (230,234,244));d.text((x+18,10),STG5[k],font=fb,fill=(255,255,255) if core else (26,26,26))
for r,key in enumerate(['1','2']):
  y=HH+r*(H+CH+G);d.text((14,y+H//2-40),'①' if key=='1' else '②',font=ImageFont.truetype(FB,56),fill=BLUE)
  for k in range(5):
    x=LW+k*(W+G);g.paste(D[f'{key}_{k+1}'],(x,y));d.text((x+4,y+H+8),CAP5[key][k],font=fc,fill=(60,66,80))
g.save('shots/pv_grid_v5.png');print('grid v4')
