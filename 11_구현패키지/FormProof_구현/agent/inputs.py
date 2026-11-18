"""입력 어댑터: 어떤 형태의 입력이든 조건 생성기(condition_generator.generate)가 받는 형태로 바꾼다.

  load_input(src) -> dict(kind, text, sketch_note, images, geometry_rho, meta)
    kind        : 'text' | 'pdf' | 'image' | 'step' | 'stl'
    text        : 조건 생성기에 넘길 요청 텍스트 (문서는 추출 본문)
    sketch_note : 이미지 · 도면에서 읽은 설명 (VLM 연결 전에는 빈 값 — 아래 TODO)
    images      : 원본 이미지 경로 목록 (VLM 입력용)
    geometry_rho: STEP · STL 입력을 엔진 격자(88 × 20 × 37, 반모델)로 바꾼 밀도 파일 경로 (기존 제품 개선 시 고정 영역 · 초기 형상)
    meta        : 쪽수, 파일명 등

구현 상태 (2026-11-16)
  text  : 완료
  pdf   : 완료 — pypdf 로 본문 추출. 특허 문서는 agent/patent.py 가 이어서 청구항 · 효과 주장을 뽑는다
  image : 경로만 전달. TODO(담당자): VLM(사내 멀티모달 LLM)으로 형태 · 부품 배치 설명 생성 → sketch_note
  step  : 완료(기본) — cadquery 로 STEP → STL → cad/vox.py 로 엔진 격자 밀도. 좌표 정렬(폰 기준 35° 좌표)은 입력 부품마다 확인 필요
  stl   : 완료(기본) — cad/vox.py
"""
import os, subprocess, sys, json, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _pdf_text(path, max_pages=40):
    from pypdf import PdfReader
    r = PdfReader(path); pages = r.pages[:max_pages]
    return '\n'.join((p.extract_text() or '') for p in pages), len(r.pages)

def _vox(stl, out, nx=88):
    subprocess.run([sys.executable, os.path.join(ROOT, 'cad', 'vox.py'), stl, out, str(nx)], check=True, cwd=os.path.join(ROOT, 'cad'))
    return out

def load_input(src, out_dir='runs/input'):
    os.makedirs(out_dir, exist_ok=True)
    if not os.path.exists(src): return dict(kind='text', text=src, sketch_note='', images=[], geometry_rho=None, meta={})
    ext = os.path.splitext(src)[1].lower(); name = os.path.basename(src)
    if ext == '.pdf':
        txt, n = _pdf_text(src); return dict(kind='pdf', text=txt, sketch_note='', images=[], geometry_rho=None, meta=dict(file=name, pages=n, chars=len(txt)))
    if ext in ('.png', '.jpg', '.jpeg'):
        return dict(kind='image', text='', sketch_note='', images=[src], geometry_rho=None, meta=dict(file=name, todo='VLM 연결 필요'))
    if ext in ('.step', '.stp'):
        import cadquery as cq
        stl = os.path.join(out_dir, name + '.stl'); cq.exporters.export(cq.importers.importStep(src), stl, tolerance=0.05)
        rho = _vox(os.path.abspath(stl), os.path.abspath(os.path.join(out_dir, name + '_rho.npy')))
        return dict(kind='step', text='', sketch_note='', images=[], geometry_rho=rho, meta=dict(file=name, stl=stl, note='좌표 정렬 확인 필요'))
    if ext == '.stl':
        rho = _vox(os.path.abspath(src), os.path.abspath(os.path.join(out_dir, name + '_rho.npy')))
        return dict(kind='stl', text='', sketch_note='', images=[], geometry_rho=rho, meta=dict(file=name))
    return dict(kind='text', text=open(src, encoding='utf-8', errors='ignore').read(), sketch_note='', images=[], geometry_rho=None, meta=dict(file=name))

if __name__ == '__main__':
    r = load_input(sys.argv[1]); r['text'] = r['text'][:500] + ('…' if len(r['text']) > 500 else ''); print(json.dumps(r, ensure_ascii=False, indent=1))
