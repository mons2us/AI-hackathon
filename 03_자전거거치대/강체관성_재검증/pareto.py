import json, glob, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family']='Noto Sans CJK JP'
import sys
items=json.load(open(sys.argv[1]))   # [{name, mass, frf_file, kind}]
fig,(a1,a2)=plt.subplots(1,2,figsize=(13,5.2))
for it in items:
    d=json.load(open(it['frf'])); c={'opt':'#0F7C80','llm':'#8a8f98','base':'#C0392B','old':'#E8A33D'}[it['kind']]
    a1.plot(d['freq'],d['T'],color=c,lw=2.2 if it['kind']=='opt' else 1.3,label=it['name'])
    a2.scatter(it['mass'],d['Tmax_band'],color=c,s=60,zorder=3); a2.annotate(it['name'],(it['mass'],d['Tmax_band']),textcoords='offset points',xytext=(5,4),fontsize=8.5)
a1.axvspan(34.6,45.6,color='#E8A33D',alpha=0.15); a1.text(40.1,a1.get_ylim()[1]*0.92 if a1.get_ylim()[1]<20 else 10,'자갈길 실측\n34.6–45.6 Hz',ha='center',fontsize=8.5,color='#9a6a12')
a1.set_yscale('log'); a1.set_xlabel('진동수 (Hz)'); a1.set_ylabel('폰 흔들림 / 핸들바 흔들림 (배)'); a1.axhline(1,color='#999',lw=0.8,ls='--'); a1.legend(fontsize=7.5,ncol=2)
a1.set_title('진동 전달 곡선 (위아래 흔들림, 감쇠비 3% 가정)',fontsize=11)
opt=sorted([it for it in items if it['kind']=='opt'],key=lambda x:x['mass'])
if len(opt)>1: a2.plot([o['mass'] for o in opt],[json.load(open(o['frf']))['Tmax_band'] for o in opt],color='#0F7C80',lw=1.5)
a2.set_xlabel('거치대 무게 (g)'); a2.set_ylabel('자갈길 구간 최대 흔들림 (배)'); a2.set_title('무게 ↔ 흔들림 — 청록 선 = AI 최적 설계들',fontsize=11); a2.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(sys.argv[2],dpi=140); print('ok')
