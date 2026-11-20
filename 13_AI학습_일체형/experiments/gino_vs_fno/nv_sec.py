NV = '''<section id="s-nv"><h2>12. NVIDIA PhysicsNeMo 와 비교 — "Building Autonomous AI Engineers with NVIDIA PhysicsNeMo"</h2>
<p class="lead">NVIDIA AI Day Seoul 2026 (11월, COEX) 세션 · NVIDIA 와 삼성 반도체연구소 CSE 팀 공동. <b>영상은 직접 보지 못했고</b>, 삼성 반도체 기술 블로그의 세션 요약 · NVIDIA 발표문(DAC 2026) · NVIDIA 블로그 · PhysicsNeMo 공식 문서 · 릴리스 노트로 확인한 내용만 정리함. 영상에만 있는 내용(슬라이드 세부 · 데모)은 빠져 있을 수 있음.</p>

<div class="grid3">
<div class="card"><div class="k">세션 핵심 1 · AI Physics</div><h3>시뮬레이션 데이터 + 지배 방정식으로 학습</h3><p class="mut">열 · 기계 해석 사례. 우리 "물리 AI"와 같은 정의.</p></div>
<div class="card"><div class="k">세션 핵심 2 · 에이전트</div><h3>목표 → 해석 입력 → AI 또는 솔버 호출 → 평가 → 다음 후보</h3><p class="mut">에이전트는 도구를 지휘하고, 물리 계산은 AI 모델 · 정밀 솔버가 함 — 우리 판정 루프와 같은 구조를 에이전트가 돌림.</p></div>
<div class="card"><div class="k">세션 핵심 3 · 삼성 사례</div><h3>10억 칸 → 100만 칸, 18시간 → 41초</h3><p class="mut">AI 균질화(유효 물성 예측) + 거친 격자 + GPU. 32코어 CPU 대비 약 1,600배, 수직 열전도율 정확도 99.17%.</p></div>
</div>

<h3 style="margin-top:18px">삼성 CSE 팀 5단계 파이프라인 (세션 요약 기준)</h3>
<div class="box sv"><svg viewBox="0 0 1100 172" style="min-width:860px" role="img" aria-label="삼성 SciML 5단계 파이프라인">
<defs><marker id="ahn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--mut)"/></marker></defs>
<g font-size="12">
<rect x="10" y="30" width="190" height="80" rx="9" class="r-soft"/><text x="105" y="56" text-anchor="middle" font-weight="700">① 합성 레이아웃</text><text x="105" y="76" text-anchor="middle" font-size="11" class="t-m">반도체 형상 · 재료를</text><text x="105" y="92" text-anchor="middle" font-size="11" class="t-m">반영해 자동 생성</text>
<rect x="230" y="30" width="190" height="80" rx="9" class="r-opt"/><text x="325" y="56" text-anchor="middle" font-weight="700">② Warp GPU 솔버</text><text x="325" y="76" text-anchor="middle" font-size="11" class="t-o">학습 데이터 생성</text><text x="325" y="92" text-anchor="middle" font-size="11" class="t-o">(파이썬 GPU 시뮬레이션)</text>
<rect x="450" y="30" width="190" height="80" rx="9" class="r-ai"/><text x="545" y="56" text-anchor="middle" font-weight="700">③ PhysicsNeMo 학습</text><text x="545" y="76" text-anchor="middle" font-size="11" class="t-a">물리 인식 AI 모델</text>
<rect x="670" y="30" width="190" height="80" rx="9" class="r-ai"/><text x="765" y="56" text-anchor="middle" font-weight="700">④ 유효 물성 예측</text><text x="765" y="76" text-anchor="middle" font-size="11" class="t-a">복잡한 미세 구조 →</text><text x="765" y="92" text-anchor="middle" font-size="11" class="t-a">열 · 기계 유효 물성</text>
<rect x="890" y="30" width="200" height="80" rx="9" class="r-str"/><text x="990" y="56" text-anchor="middle" font-weight="700">⑤ 대규모 해석에 투입</text><text x="990" y="76" text-anchor="middle" font-size="11" class="t-s">미세 구조를 다 풀지 않고</text><text x="990" y="92" text-anchor="middle" font-size="11" class="t-s">거친 격자로 칩 전체</text>
</g>
<path d="M200,70 L228,70" class="ln" marker-end="url(#ahn)"/><path d="M420,70 L448,70" class="ln" marker-end="url(#ahn)"/><path d="M640,70 L668,70" class="ln" marker-end="url(#ahn)"/><path d="M860,70 L888,70" class="ln" marker-end="url(#ahn)"/>
<text x="10" y="138" font-size="11.5" class="t-m">별도 연구: 물리 제약을 넣은 기반 모델로 영역 분해(FP-DDM) — 큰 영역을 작은 조각으로 나눠 각 조각 응답을 예측하면서 전체를 일관되게.</text><text x="10" y="158" font-size="11.5" class="t-m">DAC 2026 발표, PhysicsNeMo 예제로 공개됐다고 함 (예제 페이지는 이번에 찾지 못함 · 확인 필요).</text>
</svg></div>

<h3 style="margin-top:18px">NVIDIA 스택 지도 — 우리 모듈과 짝짓기</h3>
<p class="lead">왼쪽 = NVIDIA 스택 계층(공식 문서 · 발표문 기준), 오른쪽 = 우리 통합 프레임워크 모듈. 선 색: <span class="chip c-ok">PhysicsNeMo 로 바로 대체 · 보강</span> <span class="chip c-plan">참고해 우리 쪽 개선</span> <span class="chip c-part">우리 고유 (NVIDIA 자료에 없음)</span></p>
<div class="box sv"><svg viewBox="0 0 1100 560" style="min-width:880px" role="img" aria-label="NVIDIA 스택과 우리 모듈 대응">
<g font-size="12">
<text x="20" y="24" font-size="14" font-weight="700">NVIDIA 스택</text><text x="700" y="24" font-size="14" font-weight="700">우리 통합 프레임워크</text>
<rect x="20" y="40" width="430" height="96" rx="10" class="r-lat"/><text x="34" y="62" font-weight="700" class="t-l">에이전트 · Agent Toolkit</text>
<text x="34" y="82" font-size="11">모델 Nemotron 3 Ultra · 하네스 NemoClaw · 보안 런타임 OpenShell</text><text x="34" y="100" font-size="11">스킬: PhysicsNeMo · CUDA-X 를 에이전트가 부르는 도구로</text><text x="34" y="118" font-size="11" class="t-m">PhysicsNeMo AI Physics 스킬 4종(26.08): 탐색 · ShardTensor · Curator · CFD</text>
<rect x="20" y="150" width="430" height="132" rx="10" class="r-ai"/><text x="34" y="172" font-weight="700" class="t-a">AI Physics 모델 · PhysicsNeMo</text>
<text x="34" y="192" font-size="11">모델: FNO · DeepONet · DoMINO · Transolver · GeoTransolver · MGN …</text><text x="34" y="210" font-size="11">불확실성: concrete dropout · 변분 GP 머리(스칼라 · 분포) · 앙상블</text><text x="34" y="228" font-size="11">가드레일: 형상 새로움(메시 특징 22개 GMM) · 잠재 kNN · PDE 잔차</text><text x="34" y="246" font-size="11">능동학습: 불확실성 · 균형 무작위 · 잠재 새로움 획득</text><text x="34" y="264" font-size="11">LoRA 미세조정 · 물리 손실(PhysicsInformer)</text>
<rect x="20" y="296" width="430" height="80" rx="10" class="r-card"/><text x="34" y="318" font-weight="700">데이터 · 형상</text>
<text x="34" y="338" font-size="11">PhysicsNeMo-Mesh: SDF 질의 · GPU 리메시 · 미분 가능한 형상 변형 · 미분 연산</text><text x="34" y="356" font-size="11">PhysicsNeMo Curator: 해석 결과 → 학습용 데이터 정리</text>
<rect x="20" y="390" width="430" height="80" rx="10" class="r-opt"/><text x="34" y="412" font-weight="700" class="t-o">솔버 · 가속</text>
<text x="34" y="432" font-size="11">Warp: 파이썬으로 쓰는 미분 가능한 GPU 시뮬레이션</text><text x="34" y="450" font-size="11">CUDA-X cuDSS · cuISS (희소 행렬 직접 · 반복 해법) · 파트너 솔버</text>
<rect x="20" y="484" width="430" height="60" rx="10" class="r-soft"/><text x="34" y="506" font-weight="700">대규모 · 배포</text>
<text x="34" y="526" font-size="11">ShardTensor 영역 병렬 · FP-DDM · 균질화 · NIM 배포 · GPU</text>
</g>
<g font-size="12">
<rect x="700" y="44" width="380" height="40" rx="8" class="r-card"/><text x="714" y="69">0 목표 · 기준 입력 (키워드 규칙 · 템플릿, LLM 없음)</text>
<rect x="700" y="94" width="380" height="40" rx="8" class="r-card"/><text x="714" y="119">D 역설계 엔진 (형상 AI 위 탐색 · BoTorch)</text>
<rect x="700" y="160" width="380" height="40" rx="8" class="r-card"/><text x="714" y="185">C 물리 AI (FNO · GINO 직접 구현)</text>
<rect x="700" y="210" width="380" height="40" rx="8" class="r-card"/><text x="714" y="235">신뢰도 판단 (지금 비어 있음)</text>
<rect x="700" y="260" width="380" height="40" rx="8" class="r-card"/><text x="714" y="285">판정 → 재학습 루프 (능동학습 5회, 스크립트)</text>
<rect x="700" y="310" width="380" height="40" rx="8" class="r-card"/><text x="714" y="335">A 형상 변환 · 형상 AI (복셀 · 점 · DeepSDF)</text>
<rect x="700" y="360" width="380" height="40" rx="8" class="r-card"/><text x="714" y="385">E CAD 재출력 (자유 몸체 + 파라메트릭 기능부)</text>
<rect x="700" y="410" width="380" height="40" rx="8" class="r-card"/><text x="714" y="435">B 데이터 생성 (팀 FEM · CPU 형상당 약 1분, LightTools)</text>
<rect x="700" y="490" width="380" height="40" rx="8" class="r-card"/><text x="714" y="515">대형 패널 (BLU P3: 대형 + 미세 형상)</text>
</g>
<g fill="none" stroke-width="2">
<path d="M450,88 C 560,88 590,64 698,64" style="stroke:var(--opt)"/><path d="M450,100 C 560,100 590,114 698,114" style="stroke:var(--opt)"/>
<path d="M450,192 C 560,192 590,180 698,180" style="stroke:var(--ai)"/><path d="M450,220 C 560,220 590,230 698,230" style="stroke:var(--ai)"/><path d="M450,246 C 560,246 590,280 698,280" style="stroke:var(--ai)"/>
<path d="M450,338 C 560,338 590,330 698,330" style="stroke:var(--opt)"/>
<path d="M450,432 C 560,432 590,430 698,430" style="stroke:var(--ai)"/>
<path d="M450,514 C 560,514 590,510 698,510" style="stroke:var(--opt)"/>
<path d="M600,380 L698,380" style="stroke:var(--str);stroke-dasharray:5 4"/>
</g>
<text x="596" y="376" font-size="11" text-anchor="end" class="t-s">NVIDIA 자료에 없음 →</text>
<text x="700" y="470" font-size="11" class="t-m">형상 AI(자유 형상 생성)도 NVIDIA 자료엔 없음</text><text x="700" y="484" font-size="11" class="t-m">(확산 모델 · TopoDiff 예제 정도)</text>
</svg></div>

<h3 style="margin-top:18px">모듈별 비교와 시사점</h3>
<div class="tw"><table><thead><tr><th>모듈</th><th>우리 지금</th><th>NVIDIA 스택 (확인한 자료)</th><th>시사점</th></tr></thead><tbody>
<tr><td>0 목표 입력</td><td>키워드 규칙 · 스케치 템플릿 매칭 (LLM · GPU 없이 CPU)</td><td>에이전트(LLM)가 설계 목표를 형상 · 재료 · 경계조건으로 변환</td><td><span class="chip c-plan">참고</span>입력부를 LLM 에이전트로 확장 가능. 사내 LLM 사용 정책 · 온프레미스 여부 확인 필요</td></tr>
<tr><td>A 형상 변환</td><td>복셀 · 표면 점 · DeepSDF 를 직접 구현</td><td>PhysicsNeMo-Mesh: SDF 질의 · 리메시 · 미분 가능한 형상 변형</td><td><span class="chip c-plan">참고</span>점군 · SDF 변환과 형상 미분을 Mesh 로 대체 검토. 형상 AI(자유 형상 생성)는 우리 몫</td></tr>
<tr><td>B 데이터 생성</td><td>팀 FEM(CPU, 형상당 약 1분) · LightTools</td><td>Warp GPU 솔버 · cuDSS · cuISS</td><td><span class="chip c-plan">참고</span>구조 · 열 FEM 을 GPU 로 옮기면 데이터 생성 병목 완화 기대 (효과 미측정). LightTools 대체 여부는 확인 필요</td></tr>
<tr><td>C 물리 AI</td><td>FNO · GINO 직접 학습 (neuraloperator)</td><td>Transolver · GeoTransolver · DoMINO · MGN 학습 레시피 · LoRA</td><td><span class="chip c-ok">대체</span>아키텍처 비교를 PhysicsNeMo 레시피로. GINO 는 PhysicsNeMo 모델 목록에 없음 (neuraloperator 쪽)</td></tr>
<tr><td>신뢰도 판단</td><td><b>없음</b> — AI 단독 탐색 9회 불합격의 핵심 원인</td><td>가드레일(형상 새로움 · 잠재 kNN · PDE 잔차) + 불확실성(GP 머리 · dropout · 앙상블) 이미 라이브러리</td><td><span class="chip c-ok">대체</span>다음 실험 1순위를 PhysicsNeMo UQ · 가드레일로 바로. 단, 문서도 "새로움 점수가 낮다고 정확하다는 보장 없음" 명시</td></tr>
<tr><td>판정 · 재학습</td><td>능동학습 5회 (회당 31형상, 스크립트)</td><td>능동학습 모듈(획득 전략 3종) + 에이전트가 정밀 솔버 호출</td><td><span class="chip c-ok">대체</span>루프 자동화. 획득 전략 중 "잠재 새로움"이 우리 과대평가 문제에 직접 대응</td></tr>
<tr><td>D 역설계</td><td>형상 AI 숫자 16개 위 기울기 탐색 · BoTorch · 하이브리드 정밀 마무리</td><td>에이전트가 다음 후보 선택 · DoMINO 설계 민감도. 완성된 형상 최적화 예제는 문서 예제 목록에 없음</td><td><span class="chip c-part">우리 고유</span>목표 → 형상 역설계 엔진과 하이브리드 경로는 우리가 만들어야 하는 차별점</td></tr>
<tr><td>E CAD 재출력</td><td>자유 몸체 + 파라메트릭 기능부 · 도면 · 3D 출력</td><td>확인한 자료에 없음</td><td><span class="chip c-part">우리 고유</span>제조 가능한 CAD · 도면까지 잇는 부분</td></tr>
<tr><td>대규모</td><td>2코어 CPU 실험</td><td>ShardTensor 영역 병렬 · FP-DDM · AI 균질화</td><td><span class="chip c-plan">참고</span>v12 의 "TV 대형 + 작은 서포터" 문제에 균질화 · 영역 분해 개념이 직접 대응. 광학(광선 수송)에 적용 가능한지 확인 필요</td></tr>
<tr><td>에이전트</td><td>없음 (GUI · 개발은 Claude Code)</td><td>Agent Toolkit: 모델 · 하네스 · 스킬 · 보안 런타임. 스킬은 Claude Code 마켓플레이스로도 배포된다는 보도</td><td><span class="chip c-plan">참고</span>우리 8단계를 스킬로 노출하면 같은 틀에 올라감. 배포 경로는 확인 필요</td></tr>
</tbody></table></div>

<h3 style="margin-top:18px">우리가 나아갈 방향 (제안)</h3>
<div class="box sv"><svg viewBox="0 0 1100 250" style="min-width:860px" role="img" aria-label="역할 분담 제안">
<g font-size="12.5">
<rect x="20" y="20" width="1060" height="60" rx="10" class="r-str"/><text x="550" y="46" text-anchor="middle" font-weight="700">우리가 만드는 층 (차별점)</text><text x="550" y="66" text-anchor="middle" font-size="11.5" class="t-s">모든 입력 → 초기 설계 · 형상 AI(자유 형상) · 목표 → 형상 역설계 · 하이브리드 판정 경로 · CAD · 도면 재출력 · 제품별 어댑터(광학 · 구조 · 열 …)</text>
<rect x="20" y="92" width="1060" height="60" rx="10" class="r-ai"/><text x="550" y="118" text-anchor="middle" font-weight="700">PhysicsNeMo 위에 올리는 층</text><text x="550" y="138" text-anchor="middle" font-size="11.5" class="t-a">물리 AI 모델 · 학습 레시피 · 불확실성 · 가드레일 · 능동학습 · 형상 메시 처리 · 분산 학습</text>
<rect x="20" y="164" width="1060" height="60" rx="10" class="r-opt"/><text x="550" y="190" text-anchor="middle" font-weight="700">GPU 솔버 · 하드웨어</text><text x="550" y="210" text-anchor="middle" font-size="11.5" class="t-o">Warp · CUDA-X 로 데이터 생성 가속 · 기존 상용 솔버(LightTools 등)는 판정 · 데이터용으로 유지 · NVIDIA GPU</text>
</g></svg></div>
<ol style="font-size:13.5px;margin-top:10px">
<li><b>바닥은 빌리고, 위를 만든다.</b> 모델 · 불확실성 · 가드레일 · 능동학습 · 메시 처리는 PhysicsNeMo 가 이미 라이브러리로 가짐. 우리 인력은 형상 역설계 · 하이브리드 경로 · CAD 재출력 · 다제품 어댑터에 집중.</li>
<li><b>GPU 확보 후 첫 실험:</b> FormProof 데이터(734 형상)로 GeoTransolver + 변분 GP 머리 + 형상 가드레일을 학습 → 지금 FNO · GINO 와 "탐색 끝 형상 정밀 판정 합격률"로 비교. 지금까지 실험의 빈칸(신뢰도)을 직접 채우는 실험.</li>
<li><b>데이터 생성 GPU화:</b> 구조 · 열 FEM 을 Warp 로 이식할지 검토. 삼성 사례 1,600배는 균질화 + 거친 격자 + GPU 를 합친 결과라 솔버 이식만의 효과로 보면 안 됨.</li>
<li><b>대형 패널은 균질화 · 영역 분해로:</b> BLU P3(패널 확장)에서 "대형 + 미세 형상" 문제에 같은 발상 검토 — 서포터 · 필름 미세 구조를 유효 광학 물성으로 바꿔 넣는 식. 광학 적용 가능성은 확인 필요.</li>
<li><b>에이전트화는 마지막 층:</b> 8단계를 스킬로 노출(초기 설계 만들기 · 물리 AI 예측 · 솔버 판정 · CAD 출력) → NVIDIA Agent Toolkit 이나 지금 쓰는 Claude Code 환경에서 호출. 판정 루프가 먼저 안정돼야 의미 있음.</li>
<li><b>사내 협업:</b> 같은 회사 반도체연구소 CSE 팀이 이미 NVIDIA 와 PhysicsNeMo 공동 연구 중 — 열 · 기계 해석 경험 공유 가능성 (접점은 확인 필요).</li>
</ol>
<p class="mut" style="margin-top:6px">출처: 삼성 반도체 기술 블로그(AI Day Seoul 2026 세션 요약) · NVIDIA 발표문 2026-07-26 (Agent Toolkit + PhysicsNeMo + CUDA-X) · NVIDIA 블로그 "Korea Advances Physical AI" · PhysicsNeMo 문서(가드레일 · 불확실성 · 릴리스 노트 26.03~26.08) · NVIDIA Warp 기술 블로그 · Agent Toolkit 구성 기사</p>
</section>
'''
