import json,math,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
nx,ny,nz=140,46,2
TB=[(48,18,59),(70,134,251),(26,228,182),(164,252,60),(250,187,57),(228,70,10),(122,4,3)]
def turbo(t):
    t=max(0,min(1,t))*6;i=min(5,int(t));f=t-i;a,b=TB[i],TB[i+1];return tuple(int(a[k]+(b[k]-a[k])*f) for k in range(3))
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-DemiLight.ttc',30)
def grid(x):
    return [[max(x[i+nx*(j+ny*k)] for k in range(nz)) for i in range(nx)] for j in range(ny)]
def render(x,en,lo,hi,s=10,label=None):
    g=grid(x);W,H=nx*s,ny*s
    mask=Image.new('L',(nx,ny));m=mask.load()
    for j in range(ny):
        for i in range(nx):m[i,ny-1-j]=int(255*g[j][i])
    mask=mask.resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(s*0.35)).point(lambda v:255 if v>127 else 0)
    col=Image.new('RGB',(nx,ny));c=col.load()
    for j in range(ny):
        for i in range(nx):
            if en is None:c[i,ny-1-j]=(215,222,230)
            else:
                v=max(en[i+nx*(j+ny*k)] for k in range(nz));t=(math.log10(v+1e-12)-lo)/(hi-lo) if v>0 else 0;c[i,ny-1-j]=turbo(t)
    col=col.resize((W,H),Image.BILINEAR)
    bg=Image.new('RGB',(W,H),(13,22,32));bg.paste(col,(0,0),mask)
    d=ImageDraw.Draw(bg)
    for cx in (36,104):d.ellipse([(cx-25)*s,(ny-24-17)*s,(cx+25)*s,(ny-24+17)*s],outline=(90,110,130),width=2)
    for xx in (0,W-3):d.rectangle([xx,(ny-37)*s,xx+3,(ny-27)*s],fill=(63,193,214))
    return bg
ai=json.load(open('gl_ai_0.3.json'));hu=json.load(open('gl_hu.json'))
vals=[]
for r in (ai,hu):
    for e,v in enumerate(r['en']):
        if r['x'][e]>0.5 and v>0:vals.append(math.log10(v))
vals.sort();lo,hi=vals[int(len(vals)*.05)],vals[int(len(vals)*.98)]
render(hu['x'],hu['en'],lo,hi).save('shots/gl_hu_e.png');render(ai['x'],ai['en'],lo,hi).save('shots/gl_ai_e.png')
render(hu['x'],None,0,1).save('shots/gl_hu.png');render(ai['x'],None,0,1).save('shots/gl_ai.png')
# 과정
fr=ai['frames'];s=5;tiles=[]
for f in fr:
    g=grid(f['x']);im=Image.new('RGB',(nx*s,ny*s+44),(13,22,32));p=im.load()
    for j in range(ny):
        for i in range(nx):
            v=g[j][i]
            for a in range(s):
                for b in range(s):p[i*s+a,(ny-1-j)*s+b]=(int(13+188*v),int(22+189*v),int(32+188*v))
    ImageDraw.Draw(im).text((nx*s/2-30,ny*s+4),f"{f['it']}회",font=font,fill=(139,155,176));tiles.append(im)
W=sum(t.size[0] for t in tiles)+20*(len(tiles)-1);strip=Image.new('RGB',(W,tiles[0].size[1]),(13,22,32))
x=0
for t in tiles:strip.paste(t,(x,0));x+=t.size[0]+20
strip.save('shots/gl_frames.png');print('ok',strip.size)
