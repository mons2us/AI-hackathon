"""실제 진행 단계 알림 — 파이프라인이 단계를 시작할 때 step() 을 부르면 GUI 서버가 그 이름 · 경과 시간을 화면에 보여 준다.
(예전 GUI 는 0.45 s 마다 단계 이름을 넘기는 가짜 표시라, 2.7 s 이후의 모든 시간이 '초기 성능 계산'으로 보였다.)"""
import threading
import time

_local = threading.local()


def set_listener(fn):
    """fn(name, detail) 을 이 스레드의 단계 알림으로 등록 (None = 해제)."""
    _local.fn = fn
    _local.t = {}


def step(name, detail=""):
    fn = getattr(_local, "fn", None)
    if fn:
        fn(name, detail)


class timed:
    """with timed('복셀 FEM 풀이'): ... — 단계 알림 + 걸린 시간 기록 (progress.timings())."""

    def __init__(self, name, detail=""):
        self.name, self.detail = name, detail

    def __enter__(self):
        step(self.name, self.detail)
        self.t0 = time.time()
        return self

    def __exit__(self, *a):
        t = getattr(_local, "t", None)
        if t is not None:
            t[self.name] = round(t.get(self.name, 0.0) + time.time() - self.t0, 2)


def timings():
    return dict(getattr(_local, "t", {}) or {})
