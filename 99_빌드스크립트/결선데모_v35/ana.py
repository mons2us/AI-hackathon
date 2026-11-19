import json,numpy as np,librosa,soundfile as sf,re,sys
PH=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'phr.json'))
rows=[]
for seg,L in PH.items():
    for j,p in enumerate(L):
        y,sr=sf.read(p['wav']); y=y if y.ndim==1 else y.mean(1)
        f0,v,_=librosa.pyin(y,fmin=70,fmax=400,sr=sr,frame_length=1024)
        f=f0[v]; n=len(re.sub(r'[^가-힣]','',p['txt']))
        rms=20*np.log10(np.sqrt(np.mean(y**2))+1e-9)
        # 끝 억양: 마지막 유성 0.4초 중앙값 - 전체 중앙값 (반음)
        idx=np.where(v)[0]; t=librosa.frames_to_time(idx,sr=sr,hop_length=256)
        tail=f0[idx[t>t[-1]-0.4]] if len(idx) else []
        st=lambda a,b:12*np.log2(a/b)
        rows.append(dict(k=f'{seg}_{j}',txt=p['txt'][:26],dur=p['dur'],med=float(np.median(f)),rng=float(st(np.percentile(f,95),np.percentile(f,5))),
                         tail=float(st(np.median(tail),np.median(f))),db=float(rms),rate=n/p['dur']))
m=np.median([r['med'] for r in rows]); rm=np.median([r['rate'] for r in rows]); dm=np.median([r['db'] for r in rows])
print(f"기준: 음높이 중앙 {m:.0f} Hz · 속도 {rm:.1f} 음절/s · 음량 {dm:.1f} dB")
for r in rows:
    dp=12*np.log2(r['med']/m); flag=('음높이 ' if abs(dp)>1.5 else '')+('속도 ' if abs(r['rate']/rm-1)>0.12 else '')+('음량 ' if abs(r['db']-dm)>2 else '')
    print(f"{r['k']:8s} {dp:+5.1f}st 폭{r['rng']:4.1f} 끝{r['tail']:+5.1f} {r['rate']:4.1f}음절/s {r['db']-dm:+4.1f}dB {flag:10s} {r['txt']}")
