"""헤더 CRC(CIC 6102)를 원본과 같은 값으로 맞춘다.

에뮬레이터(Project64 등)는 헤더 CRC로 게임 설정 DB를 찾는다. 한글판은 코드가 바뀌어
CRC가 달라지므로 원본 게임으로 인식되지 않는다. 쓰지 않는 공간(글리프 캐시 헬퍼 코드 뒤)에
보정 워드 11개를 넣어 실제 체크섬이 원본 헤더 값과 같아지게 만든다(실기 IPL3 검사도 통과).

보정 블록: prep 3워드 + 하위 5비트가 0인 워드 8개.
하위 5비트가 0이면 rol 회전이 없어 t5 증가량 = t6 증가량, 그리고 워드가 모두 t2보다 작으면
t2 ^= w 가 되어 t2 변화량 = t3 변화량이 된다. 그러면 블록 끝 상태 중 t6,t5,t2,t4,t3는
합 D와 XOR X만으로 정해지고, 남은 조건은 t1 하나(32비트)라 탐색으로 맞출 수 있다.
"""
import numpy as np
from numba import njit, prange

M = 0xffffffff
SEED = 0xF8CA4DDC


def words(rom, a, b):
    return np.frombuffer(bytes(rom[a:b]), dtype='>u4').astype(np.int64)


@njit(cache=True)
def run(ws, t1, t2, t3, t4, t5, t6):
    M = 0xffffffff
    for i in range(ws.shape[0]):
        c = ws[i]
        k = (t6 + c) & M
        if k < t6:
            t4 = (t4 + 1) & M
        t6 = k
        t3 ^= c
        r = c & 31
        k2 = ((c << r) | (c >> (32 - r))) & M if r else c
        t5 = (t5 + k2) & M
        if t2 > c:
            t2 ^= k2
        else:
            t2 ^= (t6 ^ c)
        t1 = (t1 + (t5 ^ c)) & M
    return t1, t2, t3, t4, t5, t6


@njit(parallel=True, cache=True)
def search(seed0, nthr, per, D, X, T, t5s, NP):
    """앞 NP워드는 난수, 마지막 두 워드 a,b는 합 s·XOR x로 풀고 비트 분배를 전수 탐색"""
    M = 0xffffffff
    res = np.zeros((nthr, NP + 2), dtype=np.int64)
    found = np.zeros(nthr, dtype=np.int64)
    for th in prange(nthr):
        st = (np.uint64(seed0) ^ (np.uint64(th + 1) * np.uint64(0x9E3779B97F4A7C15))) | np.uint64(1)
        w = np.zeros(NP + 2, dtype=np.int64)
        for it in range(per):
            if found[th]:
                break
            S = 0
            Xp = 0
            t5 = t5s
            acc = 0
            for j in range(NP):
                st ^= st << np.uint64(13)
                st ^= st >> np.uint64(7)
                st ^= st << np.uint64(17)
                v = np.int64((st >> np.uint64(36)) & np.uint64(0x7ffffe0))  # 2^27 미만, 32의 배수
                w[j] = v
                S += v
                Xp ^= v
                t5 = (t5 + v) & M
                acc = (acc + (t5 ^ v)) & M
            if S > D:
                continue
            s = D - S
            x = X ^ Xp
            if s < x or s >= 0x80000000:
                continue
            m = s - x
            if m & 1:
                continue
            m >>= 1
            if m & x:
                continue
            need = (T - acc) & M
            # x의 비트를 a/b에 나눠 줌
            bits = np.zeros(32, dtype=np.int64)
            nb = 0
            for q in range(32):
                if (x >> q) & 1:
                    bits[nb] = 1 << q
                    nb += 1
            for sub in range(1 << nb):
                xa = 0
                for q in range(nb):
                    if (sub >> q) & 1:
                        xa |= bits[q]
                a = m | xa
                b = m | (x ^ xa)
                ta = (t5 + a) & M
                tb = (ta + b) & M
                if (((ta ^ a) + (tb ^ b)) & M) == need:
                    w[NP] = a
                    w[NP + 1] = b
                    for q in range(NP + 2):
                        res[th, q] = w[q]
                    found[th] = 1
                    break
    return found, res


def forge(rom, at, target, nwords=11, nprep=3):
    """rom[at:at+4*nwords] 를 보정 워드로 채워 crc(rom) == target 이 되게 한다"""
    import crc as _crc
    assert at % 4 == 0 and 0x1000 <= at and at + nwords * 4 <= 0x101000
    NP = nwords - nprep - 2
    pre = words(rom, 0x1000, at)
    suf = words(rom, at + nwords * 4, 0x101000)
    s0 = run(pre, SEED, SEED, SEED, SEED, SEED, SEED)
    nsuf = int(suf.shape[0])
    ssum = int(suf.sum())
    rng = np.random.default_rng(1)
    for attempt in range(1 << 24):
        z = rng.integers(0, 1 << 32, nprep).astype(np.int64)
        t1, t2, t3, t4, t5, t6 = run(z, *s0)
        if t2 < 0x80000000:
            continue
        D = int(rng.integers(1 << 24, 1 << 26)) << 5
        tot = t6 + D
        t6e = tot & M
        t4e = (t4 + (tot >> 32)) & M
        # 블록 끝 t3: crc1 = t6f ^ t4f ^ t3f
        t6f = (t6e + ssum) & M
        t4f = (t4e + ((t6e + ssum) >> 32)) & M
        t3f_need = target[0] ^ t6f ^ t4f
        X = t3f_need ^ t3 ^ int(np.bitwise_xor.reduce(suf)) if nsuf else t3f_need ^ t3
        if X & 31 or X >= 0x20000000:
            continue
        t5e = (t5 + D) & M
        t2e = t2 ^ X
        # 뒤쪽을 t1=0에서 돌려 G와 t2 최종을 구함
        g1, g2, _, _, g5, _ = run(suf, 0, t2e, 0, 0, t5e, t6e)
        t1e_need = (((target[1] ^ g5 ^ g2) - g1) & M)
        T = (t1e_need - t1) & M
        if (T - (NP + 2) * t5) & 31:  # 워드 하위 5비트가 0이면 t1 증가분의 하위 5비트는 t5로 고정
            continue
        found, res = search(int(rng.integers(1, 1 << 62)), 64, 3000000, D, X, T, t5, NP)
        if found.any():
            ws = [int(v) for v in z] + [int(v) for v in res[int(np.argmax(found))]]
            # 블록 워드가 모두 t2보다 작은지(분기 가정) 실제 계산으로 검증
            for i, v in enumerate(ws):
                rom[at + i * 4:at + i * 4 + 4] = v.to_bytes(4, 'big')
            if _crc.crc(rom) == tuple(target):
                return ws
    raise RuntimeError('forge failed')


if __name__ == '__main__':
    import sys, crc
    r = bytearray(open(sys.argv[1], 'rb').read())
    print([hex(v) for v in crc.crc(r)])
