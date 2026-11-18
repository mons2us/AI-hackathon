# 브라우저 전용 버전 (claude.ai Artifact / 정적 호스팅)

`app/server.py` 없이 브라우저만으로 도는 입력 단계 GUI.

```
python app/artifact/build.py         # dist/ 생성 (약 4분): index.html + data/ + ex/
python app/artifact/test_parity.py   # 브라우저 엔진(src/engine.js) = Python 결과 확인 (node 필요)
cd app/artifact/dist && python -m http.server 8790
```

- 미리 계산(build.py): 템플릿 10 × 핸들바 5규격(22.2/25.4/28.6/31.8/35.0) × 폰 4종 — STEP, 메시, 도면(DXF + 벡터), FEM(1차 설계 성능, 응력·처짐 장), 폰 회전 공간.
- 브라우저(src/engine.js): 문장 규칙, 스케치·이미지 매칭(sketch.py와 같은 알고리즘, 후보 순위 50/50 일치), 명세 조립(build_spec과 100/100 일치), 판정, 히트맵, 도면 표제란, 인계 zip.
- 차이: 목록에 없는 핸들바 직경은 가장 가까운 규격 형상을 쓰고 가정에 적는다. 직접 입력한 폰 무게의 성능은 4개 무게 해석값에서 보간한다. problem.npz는 zip의 spec.json에서 다시 만든다(README.txt).
