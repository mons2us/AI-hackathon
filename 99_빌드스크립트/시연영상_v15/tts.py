import sys,sherpa_onnx,soundfile as sf
D='/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/ttsmodel/vits-mimic3-ko_KO-kss_low'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f'{D}/ko_KO-kss_low.onnx',tokens=f'{D}/tokens.txt',data_dir=f'{D}/espeak-ng-data',noise_scale=0.667,noise_scale_w=0.8,length_scale=1.0),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg)
def say(text,out,speed=1.0):
    a=tts.generate(text,sid=0,speed=speed); sf.write(out,a.samples,a.sample_rate); return len(a.samples)/a.sample_rate
if __name__=='__main__':
    print(say(sys.argv[1],sys.argv[2],float(sys.argv[3]) if len(sys.argv)>3 else 1.0))
