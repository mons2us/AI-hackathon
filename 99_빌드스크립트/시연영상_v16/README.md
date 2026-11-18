# 시연영상 v16 = v14 화면 + 도슨트 음성 (v15 음성 교체)
- TTS: Supertonic 3 (sherpa-onnx 1.12.40, int8, 화자 sid=0, 속도 1.05, steps 20) — 오프라인
- 대본 script_final.json: [시작 시각(초), 대사] 24줄. 2초 간격 프레임으로 강조 상자 전환 시점에 맞춤
- 외래어·숫자는 한글 표기(쓰리디, 에이쓰리, 십일 점 육, 서른한)로 입력 — 숫자/영문 표기보다 정확
- 검수: 한국어 ASR(sherpa-onnx zipformer-korean)로 다시 받아써 대본과 글자 오류율 비교
  - v15(mimic3 KSS): 평균 32 %
  - v16: 최종 영상 기준 평균 8.6 % (남은 차이 대부분은 ASR이 AI·3D·숫자로 표기한 것)
- 각 클립 앞뒤 무음 제거, 20 ms 페이드, 장면 시작에 배치 후 loudnorm -16 LUFS
