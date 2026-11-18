import sys,json; sys.path.insert(0,'.'); sys.path.insert(0,'..')
import tts3
S=json.load(open(sys.argv[1])); sid=int(sys.argv[2]); out=sys.argv[3]; END=134.1
import os; os.makedirs(out,exist_ok=True)
for i,(t,txt) in enumerate(S):
    slot=(S[i+1][0] if i+1<len(S) else END)-t-0.25
    d=tts3.say(txt,f'{out}/c{i:02d}.wav',sid=sid,steps=20,speed=float(sys.argv[4]) if len(sys.argv)>4 else 1.0)
    print(f'{i:2d} t={t:6.1f} slot={slot:4.1f} dur={d:4.1f}','OVER' if d>slot else '',flush=True)
