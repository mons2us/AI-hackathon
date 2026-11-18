import sys,json,sherpa_onnx,soundfile as sf,librosa,glob,os
D=os.path.dirname(os.path.abspath(__file__))+'/asrmodel/sherpa-onnx-zipformer-korean-2024-06-24'
r=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{D}/encoder-epoch-99-avg-1.onnx',decoder=f'{D}/decoder-epoch-99-avg-1.onnx',joiner=f'{D}/joiner-epoch-99-avg-1.onnx',tokens=f'{D}/tokens.txt',num_threads=4,decoding_method='greedy_search')
def tr(p):
    a,sr=sf.read(p,dtype='float32')
    if a.ndim>1:a=a.mean(1)
    if sr!=16000:a=librosa.resample(a,orig_sr=sr,target_sr=16000)
    s=r.create_stream();s.accept_waveform(16000,a);r.decode_stream(s);return s.result.text
def cer(ref,hyp):
    import re
    a=re.sub(r'[^가-힣0-9a-zA-Z]','',ref);b=re.sub(r'[^가-힣0-9a-zA-Z]','',hyp)
    d=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        p=d[:];d[0]=i
        for j,y in enumerate(b,1):d[j]=min(p[j]+1,d[j-1]+1,p[j-1]+(x!=y))
    return d[-1]/max(1,len(a))
if __name__=='__main__':
    S=json.load(open(sys.argv[1])); pat=sys.argv[2]
    tot=0
    for i,(t,txt) in enumerate(S):
        h=tr(pat%i); c=cer(txt,h); tot+=c
        print(f'{i:2d} CER={c:.2f}\n  REF {txt}\n  ASR {h}')
    print('mean CER',tot/len(S))
