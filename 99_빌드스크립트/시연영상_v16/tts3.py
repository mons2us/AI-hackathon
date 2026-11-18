import sherpa_onnx,soundfile as sf,numpy as np
D='/tmp/claude-0/-home-claude/e964ed80-ee1b-5f91-abd3-3081682a3ad7/scratchpad/ttsmodel/sherpa-onnx-supertonic-3-tts-int8-2026-05-11'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(
 duration_predictor=f'{D}/duration_predictor.int8.onnx',text_encoder=f'{D}/text_encoder.int8.onnx',vector_estimator=f'{D}/vector_estimator.int8.onnx',
 vocoder=f'{D}/vocoder.int8.onnx',tts_json=f'{D}/tts.json',unicode_indexer=f'{D}/unicode_indexer.bin',voice_style=f'{D}/voice.bin'),num_threads=2))
tts=sherpa_onnx.OfflineTts(cfg)
def say(text,out,sid=6,speed=1.0,steps=16):
    g=sherpa_onnx.GenerationConfig(); g.sid=sid; g.num_steps=steps; g.speed=speed; g.extra["lang"]="ko"
    a=tts.generate(text,g); x=np.array(a.samples,dtype=np.float32)
    sf.write(out,x,a.sample_rate); return len(x)/a.sample_rate
