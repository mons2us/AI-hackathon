# 시연영상 v15 = v14 + 도슨트 음성
- TTS: sherpa-onnx 1.12.40, 모델 vits-mimic3-ko_KO-kss_low (공개 저품질 한국어 모델, 오프라인)
- script.json: [시작 시각(초), 대사] 20개. 각 클립을 해당 장면 시작에 배치(adelay) 후 amix, loudnorm -16 LUFS
- 영상 트랙은 v14 그대로 복사
