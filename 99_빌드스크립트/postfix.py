"""pptxgenjs 결과 후처리: 그림 1800 px 이하, 문단 속성(pPr) 하나로 · 맨 앞, 슬라이드 내 도형 id 중복 제거.
모바일 PowerPoint 가 문단 안 중복 pPr 이 있으면 파일을 닫음(v164~v170 11쪽)."""
import zipfile,io,re,sys
from PIL import Image
src,dst=sys.argv[1],sys.argv[2]
def fixp(m):
    p=m.group(0); first=[True]
    def k(x):
        if first[0]: first[0]=False; return x.group(0)
        return ''
    body=re.sub(r'<a:pPr\b[^>]*?(/>|>.*?</a:pPr>)',k,p)
    pp=re.search(r'<a:pPr\b[^>]*?(/>|>.*?</a:pPr>)',body)
    if pp and not body.startswith('<a:p>'+pp.group(0)):
        body=body.replace(pp.group(0),'',1).replace('<a:p>','<a:p>'+pp.group(0),1)
    return body
zi=zipfile.ZipFile(src); zo=zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED); bad=0
for it in zi.infolist():
    d=zi.read(it.filename)
    if it.filename.startswith('ppt/media/') and it.filename.endswith('.png'):
        im=Image.open(io.BytesIO(d))
        if max(im.size)>1800:
            r=1800/max(im.size); im=im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
        b=io.BytesIO(); im.save(b,'PNG',optimize=True); d=b.getvalue() if len(b.getvalue())<len(d) else d
    if re.match(r'ppt/(slides|notesSlides)/\w+\.xml$',it.filename):
        s=re.sub(r'<a:p>.*?</a:p>',fixp,d.decode('utf8'),flags=re.S)
        if it.filename.startswith('ppt/slides/'):
            seen=set(); n=[1000]
            def f(m):
                i=m.group(1)
                if i in seen: n[0]+=1; return '<p:cNvPr id="%d"'%n[0]
                seen.add(i); return m.group(0)
            s=re.sub(r'<p:cNvPr id="(\d+)"',f,s)
            bad+=s.count('</a:r><a:pPr')+s.count('</a:pPr><a:pPr')
        d=s.encode('utf8')
    zo.writestr(it,d)
zo.close(); print('pPr 이상 남은 수', bad)
