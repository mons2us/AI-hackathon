import json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
L=json.load(open('lines.json')); M=json.load(open('marks.json')); dw=M['dw']
im=Image.open(sys.argv[1]+'opt_final_drawing.png').convert('RGB'); im.thumbnail((1580,890),Image.LANCZOS); w,h=im.size; ox,oy=(1600-w)//2,(900-h)//2
s=w/420; P=lambda x,y:(ox+x*s, oy+(297-y)*s)
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; FR='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fb=ImageFont.truetype(FB,24,index=1); fr=ImageFont.truetype(FR,19,index=1)
def frame(boxes,title,body,cpos):
    S=Image.new('RGB',(1600,900),'white'); S.paste(im,(ox,oy))
    ov=Image.new('RGBA',(1600,900),(8,14,28,105)); md=ImageDraw.Draw(ov)
    for (x0,y0,x1,y1) in boxes: a=P(x0,y1); b=P(x1,y0); md.rectangle([a[0]-6,a[1]-6,b[0]+6,b[1]+6],fill=(0,0,0,0))
    S=Image.alpha_composite(S.convert('RGBA'),ov); d=ImageDraw.Draw(S)
    for (x0,y0,x1,y1) in boxes: a=P(x0,y1); b=P(x1,y0); d.rounded_rectangle([a[0]-6,a[1]-6,b[0]+6,b[1]+6],radius=10,outline=(255,176,32),width=4)
    lines=body.split('\n'); bw=max(d.textlength(title,font=fb),*[d.textlength(l,font=fr) for l in lines])+48; bh=50+30*len(lines)
    x,y=cpos; d.rounded_rectangle([x,y,x+bw,y+bh],radius=14,fill=(17,26,43),outline=(255,176,32),width=2)
    d.text((x+22,y+12),title,font=fb,fill=(255,209,102))
    for i,l in enumerate(lines): d.text((x+22,y+50+30*i),l,font=fr,fill=(255,255,255))
    return S.convert('RGB')
frame([(20,10,410,287)],'제작 도면 자동 생성',f'최적 설계가 나오면 A3 도면을 자동으로 만듦\n이번 생성 시간 {dw["seconds"]:.0f}초 (3면도 · 등각도 · 구멍 표 · 표제란)',P(100,150)).save('dC.png')
frame([(270,10,410,58.6)],'표제란',f'도명 · 도번 · 재질 PETG · 질량 {dw["mass_g"]} g\n척도 1:1 · 3각법 · 단위 mm',P(150,108)).save('dA.png')
frame([(24,27,150,66),(40,85,240,175)],'정면도 + 구멍 표','볼트 · 나사 구멍의 지름 · 위치 · 수량',P(250,140)).save('dB.png')
o=1.0; t=lambda k:max(0,M[k]-o); c0=t('opt')+2.0; c1=t('aiplay')-0.3; cut=c1-c0
def T(k): v=t(k); return v if v<=c0 else v-cut
for a in (['-t',f'{c0:.2f}','-i','raw.mp4'],['-ss',f'{c1:.2f}','-i','raw.mp4']):
    pass
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','raw.mp4','-t',f'{c0:.2f}','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','pa.mp4'],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{c1:.2f}','-i','raw.mp4','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','pb.mp4'],check=True)
open('lc.txt','w').write("file pa.mp4\nfile pb.mp4\n")
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','lc.txt','-c','copy','main.mp4'],check=True)
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','main.mp4']))+6
R=T('regions'); ev=[]
def even(k,a,b):
    n=len(L[k])
    for j in range(n): ev.append((f'n_{k}_{j}.png',a+(b-a)*j/n,a+(b-a)*(j+1)/n))
even('in',0,T('spec')); even('spec',T('spec'),T('first'))
ev+=[('n_reg_0.png',T('first'),R+5.2),('n_reg_1.png',R+5.2,R+11.5),('n_reg_2.png',R+11.5,T('opt'))]
ev+=[('n_ai_0.png',T('opt'),T('opt')+3.5),('n_ai_1.png',T('opt')+3.5,T('refine')),('n_ai_2.png',T('refine'),T('done'))]
even('done',T('done'),T('cmp')); even('cmp',T('cmp'),T('draw')); even('draw',T('draw'),dur)
d0=T('draw')+1.5; dseq=[('dC.png',d0,d0+3.8),('dA.png',d0+3.8,d0+7.6),('dB.png',d0+7.6,999)]
inp=['-i','main.mp4']+sum([['-i',f] for f,_,_ in ev],[])+sum([['-i',f] for f,_,_ in dseq],[])
fl='[0:v]tpad=stop_mode=clone:stop_duration=6,pad=1600:1010:0:0:color=0x111a2b[v0];'; n=0
for i,(f,a,b) in enumerate(ev): fl+=f"[v{n}][{i+1}:v]overlay=0:900:enable='between(t,{a:.2f},{b:.2f})'[v{n+1}];"; n+=1
for j,(f,a,b) in enumerate(dseq): fl+=f"[v{n}][{len(ev)+1+j}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{n+1}];"; n+=1
subprocess.run(['ffmpeg','-y','-loglevel','error']+inp+['-filter_complex',fl.rstrip(';'),'-map',f'[v{n}]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r','30','mainc.mp4'],check=True)
print('cut',round(cut,1))
