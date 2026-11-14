"""형상 정리 전(11-13 버전) vs 후 비교: 놀고 있는 재료 비율 + 같은 형상 전후 그림 → docs/groups/*_clean_cmp.png
실행: python experiments/clean_compare.py"""
import sys, json, numpy as np, matplotlib.pyplot as plt
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import group_figures as G
from fp08 import problems, shapes, labels
import _shapes_v1 as old   # 11-13 버전 형상 생성기 (비교용)
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'groups')+'/'
def idle_frac(p, o, r):
    """설계 재료 중 '놀고 있는' 칸 비율: 기본 하중들의 변형 에너지 밀도가 설계 재료 중앙값의 0.1% 미만"""
    g=p.grid; m=(o&(p.label==0)); ks=p.kscale(o.astype(float)); E=np.zeros(g.ne)
    for u in r['U'].values():
        ue=u[g.edof]; e=np.einsum('ei,ij,ej->e',ue,p.KE,ue)*ks
        E+=e/(np.median(e[m])+1e-300)
    return float((E[m]<1e-3*len(r['U'])).mean())
def run_fem(p,o): r=labels.fem_label(p,o,p.default_cond); return r
stats={}
for k in problems.GROUPS:
    p=problems.get(k); cv=shapes.Canvas(p); cvo=old.Canvas(p)
    raw=[]; idle_old=[]; idle_new=[]; dead_old=[]
    for i in range(24):
        a,ma=old.make_shape(p,k,i,cvo); b,mb=shapes.make_shape(p,k,i,cv)
        if not (ma['connected'] and mb['connected']): continue
        ra=run_fem(p,a); rb=run_fem(p,b)
        idle_old.append(idle_frac(p,a,ra)); idle_new.append(idle_frac(p,b,rb))
        df=(a.sum()-shapes.drop_dead_blobs(cv,a).sum())/a.sum(); dead_old.append(df); raw.append((df,i,a,ma,ra))
    stats[k]=dict(n=len(idle_old), idle_before=float(np.mean(idle_old)), idle_after=float(np.mean(idle_new)),
                  dead_shapes_before=int(sum(d>0 for d in dead_old)), dead_mass_before=float(np.mean(dead_old)))
    print(k,stats[k],flush=True)
    raw.sort(key=lambda t:-t[0]); pick=raw[:2]
    fig=plt.figure(figsize=(9,3.1*len(pick)))
    for r_,(df,i,a,ma,ra) in enumerate(pick):
        b=shapes.clean_shape(cv,a); rb=run_fem(p,b)
        for c,(o,res,lab) in enumerate([(a,ra,'정리 전'),(b,rb,'정리 후 (같은 형상)')]):
            e=res['eval']; v=f"f_min {e['f_min']:.0f} Hz" if 'f_min' in e else f"흔들림 {e['utop_fb']:.2f} mm"
            ax=fig.add_subplot(len(pick),2,2*r_+c+1,projection='3d')
            if c==0:
                keep=shapes.drop_dead_blobs(cv,a); G.mesh(ax,p,keep,'#e8833a'); G.mesh(ax,p,a&~keep,'#2f6fed')
            else: G.mesh(ax,p,o&(p.label==0),'#e8833a')
            G.mesh(ax,p,p.label==1,'#5F5E5A'); G.mesh(ax,p,p.label==3,'#7F77DD')
            G.frame(ax,p); ax.view_init(*G.VIEW[problems.PRODUCT_OF[k]])
            ax.set_title(f"{lab} #{i} {G.FAM[ma['family']]}\n{e['mass_g']:.0f} g · {v} · {'합격' if e['pass'] else '불합격'}",fontsize=10,color='#0d7a5f' if e['pass'] else '#d9455f')
    plt.tight_layout(); plt.savefig(OUT+f'{k}_clean_cmp.png',dpi=80,bbox_inches='tight'); plt.close(fig)
json.dump(stats,open(OUT+'clean_stats.json','w'),indent=1)
