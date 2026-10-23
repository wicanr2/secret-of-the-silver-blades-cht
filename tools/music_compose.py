#!/usr/bin/env python3
"""遊戲中配樂（規格 014，#11）：以原版標題曲的動機與音色新編 13 首 OPL2 曲。在 sosb-tools 容器內以 python3 -I 執行。

  compose --vgm boot.vgm --out DIR   寫 DIR/<key>.opl、DIR/title.opl（原曲轉成同格式，供渲染對照）與 DIR/manifest.json
  master  --out DIR                  讀 DIR/<key>.wav、DIR/title.wav（dosgolem cmd/cok-opl-render 渲染），量 RMS 與峰值，
                                     寫 DIR/music.tsv（gain 使 RMS 等於標題曲的 0.7 倍）並把量測補進 manifest

架構移植自克萊恩英豪 workplace/music/work/compose.py（其規格 014 經使用者試聽通過）：每首由曲目表定義速度、拍號、
小節數、調式與和聲進行，伴奏織體與動機樂句由確定性規則排出，不用亂數。動機與音色見規格 014 §1。
"""
import argparse
import copy
import hashlib
import json
import math
import struct
import wave
from array import array
from pathlib import Path

OFF = [0, 1, 2, 8, 9, 10, 16, 17, 18]  # 聲道 → 調變運算子槽位，載波 +3
NOTE = 'C C♯ D E♭ E F F♯ G A♭ A B♭ B'.split()


def name(p):
    return f'{NOTE[p % 12]}{p // 12 - 1}'


# 動機：以錨點為 0 的半音數；音高與出處見規格 014 §1。錨點在原曲都是 G。
MOTIFS = {
    'A': dict(offsets=[15, 14, 12, 7, 3, 0], anchor=67, source='第 0 聲道第 1–6 音，0.03 秒起', pitches='B♭5 A5 G5 D5 B♭4 G4'),
    'B': dict(offsets=[7, 7, 7, 7, 8, 3], anchor=55, source='第 0 聲道 9.80 秒起', pitches='D4 D4 D4 D4 E♭4 B♭3'),
    'C': dict(offsets=[9, 7, 5, 0, -7, 0], anchor=43, source='第 0 聲道第 19–24 音，3.54 秒起', pitches='E3 D3 C3 G2 C2 G2'),
    'D': dict(offsets=[-1, 0, 2, 3], anchor=55, source='第 0 聲道 23.48 秒起', pitches='F♯3 G3 A3 B♭3'),
}
SCALES = {'minor': [0, 2, 3, 5, 7, 8, 10], 'major': [0, 2, 4, 5, 7, 9, 11], 'dorian': [0, 2, 3, 5, 7, 9, 10],
          'phrygian': [0, 1, 3, 5, 7, 8, 10]}
QUALITY = {'maj': [0, 4, 7], 'min': [0, 3, 7], 'dim': [0, 3, 6]}

# key、曲名、用途、BPM、拍數、小節數、主音（MIDI）、調式、調性、織體、8 小節和聲進行（音級；(音級, 性質) 指定三和弦性質，
# 'N' 是降二級大三和弦）、設計說明
SCORES = [
    ('town', '新維地格里城', '鎮上（GEO 1/10）', 92, 4, 32, 55, 'dorian', 'G 多利安調式', 'walk',
     [0, 3, 6, 0, 2, 3, 4, 0], '低音二拍行進、撥弦反拍和弦；主旋律用原曲音色，A 動機放慢成兩小節的問句，C 動機的大六度終止回答，'
     '再以 B 號角與 D 導音上行接回句首。'),
    ('ruins', '舊城廢墟', '舊維地格里城廢墟、黑圈幫總部（1/20、1/22）', 70, 4, 24, 55, 'minor', 'G 小調', 'sparse',
     [0, 0, 5, 'N', 0, 3, 5, (4, 'maj')], 'A 動機拆成前後兩半、錯開半拍，中間留白；低音持續音上偶有降二級和弦，句尾停在屬和弦不解決。'),
    ('well', '知識之井', '知識之井地區（1/21）', 66, 4, 24, 62, 'dorian', 'D 多利安調式', 'shimmer',
     [0, 5, 3, 0, 5, 6, (4, 'maj'), 0], '撥弦十六分音符分散和弦在高音區閃動；D 動機增值成上行的問句，A 動機倒影上行回答。'),
    ('mines', '礦坑', '礦坑（2/30–2/32）', 88, 4, 32, 60, 'minor', 'C 小調', 'pulse',
     [0, 0, 5, 6, 0, 3, (4, 'maj'), (4, 'maj')], 'B 動機的同音四連打當作鎬擊主題，低音八分音符反覆；A 動機以八分音符接在後面。'),
    ('depths', '地下城', '孿生城堡地下城、半蜘精靈基地（2/40–2/42、2/44）', 60, 4, 20, 55, 'phrygian', 'G 弗里吉安調式', 'sparse',
     [0, 0, 1, 0, 5, 1, 0, 4], 'A 動機倒影降入低音，半音鄰音與空五度交替；稀疏的鐘音落在弱拍。'),
    ('glacier', '冰河', '冰河裂縫、寒霜巨人村（3/50–3/52）', 108, 3, 40, 62, 'minor', 'D 小調', 'waltz',
     [0, 5, 3, 0, 6, 2, (4, 'maj'), 0], '三拍子，撥弦八分音符在高音區鋪成冷光；A 動機改成三拍句型，C 動機轉到小調回答。'),
    ('finale', '孿生城堡', '孿生城堡入口、中層、恐怖魔王的老巢（3/60–3/62）', 120, 4, 40, 55, 'minor', 'G 小調，末段 G 大調借用', 'drive',
     [0, 5, 3, (4, 'maj'), 0, 3, 5, (4, 'maj')], 'A、B、C 動機在原曲音色與木管間接力，最後一段把主旋律的三度升高，以大調回應。'),
    ('battle', '戰鬥', '一般戰鬥', 150, 4, 40, 55, 'minor', 'G 小調', 'drive',
     [0, 0, 5, 6, 0, 3, 5, (4, 'maj')], 'A 動機用八分音符，速度接近原曲的十六分音符瀑布；低音八分音符推進，第三段抽掉半數低音再重入。'),
    ('battle-boss', '強敵', '白龍、恐怖魔王、巫妖', 126, 4, 36, 60, 'minor', 'C 小調', 'drive',
     [0, 'N', 0, 3, 0, 5, 'N', (4, 'maj')], 'A 動機倒影落在低音，降二級和聲加重壓迫；低音八度加厚。'),
    ('victory', '勝利', '戰鬥勝利訊息', 120, 4, 4, 55, 'major', 'G 大調', 'fanfare',
     [3, 4, 0, 0, 0, 0, 0, 0], 'B 動機改大調成短號角，接 A 動機大調瀑布，以 IV、V、I 終止。'),
    ('defeat', '全滅', '隊伍全滅', 60, 4, 2, 55, 'minor', 'G 小調', 'lament',
     [0, 0, 0, 0, 0, 0, 0, 0], 'A 動機前四音放慢並降八度，上方和聲逐聲抽去，留下低音 G 與空五度。'),
    ('camp', '紮營', '營地選單', 72, 3, 32, 58, 'major', 'B♭ 大調', 'waltz-soft',
     [0, 3, 5, 4, 0, 1, 3, 4], '關係大調的三拍子；撥弦拆開和弦，木管以原調音高唱 A 動機，句間留一整拍呼吸。'),
    ('sanctuary', '神殿', '神殿選單', 60, 4, 24, 63, 'major', 'E♭ 大調', 'hymn',
     [0, 3, 0, 4, 5, 1, 4, 0], '四聲部聖詠以二分、全音符移動；A 動機四倍增值，B 動機的同音改成鐘聲。'),
]


def degree(root, mode, d):
    return root + SCALES[mode][d % 7] + 12 * (d // 7)


def chord_of(root, mode, spec):
    if spec == 'N':  # 降二級大三和弦
        return [root + 1 + i for i in QUALITY['maj']]
    if isinstance(spec, tuple):
        d, q = spec
        return [degree(root, mode, d) + i for i in QUALITY[q]]
    return [degree(root, mode, spec + x) for x in (0, 2, 4)]


def snap(p, root, mode, prefer):
    """不在調式音階內的音往 prefer 方向移半音（大調化往上，弗里吉安化往下）。"""
    if (p - root) % 12 in SCALES[mode]:
        return p
    return p + prefer if (p + prefer - root) % 12 in SCALES[mode] else p - prefer


def make_score(s):
    key, title, use, bpm, meter, bars, root, mode, tonality, texture, prog, design = s
    notes, quotes = [], []
    total, spb = bars * meter, 60 / bpm

    def add(ch, beat, dur, p, vel=80):
        end = min(beat + dur, total - .1)
        if beat < total and end > beat:
            notes.append(dict(channel=ch, start=beat * spb, end=end * spb, pitch=int(p), velocity=int(vel)))

    def quote(motif, ch, start, rhythm, how, shift=0, inv=False, prefer=1, vel=84, keep=False, frm=0, upto=None):
        """引用動機的 [frm:upto] 段：錨點移調 shift 半音；不在調式內的音依 prefer 調整（keep 保留原曲變化音）。
        inv 是音階內倒影：在 G 自然小調算出各音的音級，以第一音為軸翻轉，再放到移調後錨點的本曲調式上（錨點要是本曲主音）。"""
        m = MOTIFS[motif]
        offs = m['offsets'][frm:upto]
        base = m['anchor'] + shift
        if inv:
            degs = [SCALES['minor'].index(o % 12) + 7 * (o // 12) for o in offs]
            pitches = [degree(base, mode, 2 * degs[0] - d) for d in degs]
        else:
            pitches = [base + o for o in offs]
            if not keep:
                pitches = [snap(p, root, mode, prefer) for p in pitches]
        beat, onsets = start, []
        for p, dur in zip(pitches, rhythm):
            if beat >= total - .1:
                break
            add(ch, beat, dur * .85, p, vel)
            onsets.append(beat)
            beat += dur
        if onsets:
            quotes.append(dict(motif=motif, channel=ch, bar=round(start / meter + 1, 3), onsets_beats=onsets,
                               pitches_midi=pitches[:len(onsets)], pitch_sequence=[name(p) for p in pitches[:len(onsets)]], transformation=how))

    # 錨點移調：主音不是 G 時整段移過去；camp、sanctuary 是 G 小調的關係調，不移調只調整到音階內
    shift = {'well': -5, 'glacier': -5, 'mines': 5, 'battle-boss': 5}.get(key, 0)

    if key == 'victory':
        quote('B', 0, 0, [.25, .25, .25, .25, 1, .5], 'B 動機改大調短號角（E♭→E、B♭→B）', shift=12, prefer=1, vel=96)
        quote('A', 0, 4, [.25, .25, .25, .25, .25, 1], 'A 動機大調瀑布，只降一個八度', shift=0, prefer=1, vel=92)
        for ch, d in [(1, 4), (2, 2), (3, 0)]:
            add(ch, 6, 1.9, degree(root, mode, d), 90)
        for bar, deg in enumerate([3, 4, 0, 0]):
            c = chord_of(root, mode, deg)
            add(4, bar * 2 if bar < 3 else 6, 1.9, c[0] - 24, 88)
            for ch, p in zip([5, 6, 8], c):
                add(ch, bar * 2 if bar < 3 else 6, 1.9, p - 12, 80)
        return notes, quotes, 6 * spb + 2
    if key == 'defeat':
        quote('A', 0, 0, [1, 1, 1.5, 2.5], 'A 動機前四音放慢、降兩個八度', shift=-24, keep=True, vel=80, upto=4)
        for ch, p, dur in [(4, 43, 7.6), (5, 50, 5.6), (2, 58, 4.4), (3, 62, 2.6)]:
            add(ch, 0, dur, p, 76)
        return notes, quotes, 11.0

    for bar in range(bars):
        beat, section, pos = bar * meter, bar // 8, bar % 8
        spec = prog[pos]
        if bar == bars - 1:  # 末小節停在屬和弦，循環接回句首
            spec = (4, 'maj') if key not in ('sanctuary', 'camp', 'depths') else 4
        local = 'major' if key == 'finale' and section >= 4 else mode
        c = chord_of(root, local, spec)
        bass = c[0] - 24 if c[0] - 24 >= 31 else c[0] - 12
        if texture == 'walk':
            add(4, beat, 1.8, bass, 82)
            add(4, beat + 2, 1.8, bass + 7, 76)
            for b in (1, 3):
                for ch, p in zip((5, 6), c[1:]):
                    add(ch, beat + b, .45, p, 66)
            for j in range(8):
                if j % 2:
                    add(7, beat + j * .5, .3, c[(j // 2) % 3] + 12, 56)
        elif texture in ('waltz', 'waltz-soft'):
            soft = texture == 'waltz-soft'
            add(4, beat, 2.6, bass, 74 if soft else 80)
            for b in (1, 2):
                for ch, p in zip((5, 6), c[1:]):
                    add(ch, beat + b, .45, p - (12 if soft else 0), 58 if soft else 64)
            for j in range(6):
                if not soft or j % 2 == 0:
                    add(7, beat + j * .5, .3, c[[0, 1, 2, 1, 2, 1][j]] + (24 if not soft else 12), 54)
        elif texture == 'shimmer':
            add(4, beat, 3.8, bass, 72)
            for ch, p in zip((2, 3), c[1:]):
                add(ch, beat, 3.8, p - 12, 56)
            arp = [c[0] + 12, c[1] + 12, c[2] + 12, c[1] + 24]
            for j in range(16):
                add(5 + j % 3, beat + j * .25, .22, arp[j % 4], 50 + 8 * (j % 4 == 0))
        elif texture == 'pulse':
            for j, d in enumerate([0, 0, 7, 0, 12, 0, 7, 0]):
                if section == 2 and j % 2:
                    continue
                add(4, beat + j * .5, .38, bass + d, 84)
            for ch, p in zip((2, 3), c[1:]):
                add(ch, beat, 3.8, p - 12, 58)
            for j in range(4):  # 第四拍的鎬擊：和弦五音的十六分音符
                add(7, beat + 3 + j * .25, .2, c[2], 60 + 6 * (j == 0))
        elif texture == 'sparse':
            if bar % 2 == 0:
                add(4, beat, 7.6, root - 12, 76)
            if pos % 2 == 0:
                add(2, beat + 2, 1.7, c[1] - 12, 60)
            if pos in (1, 4, 7):
                add(8, beat + 1.5, .5, c[2] + 12, 50)
            if key == 'depths' and pos in (2, 6):
                add(6, beat + 3, .65, root + 1, 56)
            if key == 'ruins' and spec == 'N':
                for ch, p in zip((5, 6), c):
                    add(ch, beat, 3.6, p - 12, 54)
        elif texture == 'drive':
            heavy = key == 'battle-boss'
            for j in range(8):
                if section == 2 and j % 2:
                    continue
                d = [0, 0, 12, 0, 7, 0, 12, 7][j]
                add(4, beat + j * .5, .36, bass + d, 88 if heavy else 82)
            for b in ([0, 1.5, 3] if heavy else [0, 2, 3.5]):
                for ch, p in zip((5, 6), c[1:]):
                    add(ch, beat + b, .4, p - 12, 78)
            if heavy or key == 'finale':
                add(8, beat, 3.6, bass - 12 if bass >= 43 else bass, 74)
            for j in range(8):
                if section % 2 == 0 or j % 2 == 0:
                    add(7, beat + j * .5, .28, c[j % 3] + (12 if key == 'finale' else 0), 58)
        elif texture == 'hymn':
            for ch, lo, p in [(4, 36, c[0] - 24), (2, 48, c[2] - 12), (3, 55, c[1]), (5, 60, c[0] + 12)]:
                while p < lo:
                    p += 12
                while p > lo + 11:
                    p -= 12
                add(ch, beat, 3.8, p, 68)
            if pos in (0, 3, 6):
                add(8, beat + 2.5, 1.3, c[2] + 12, 50)

    # 每 8 小節一段的主題與回答
    for section in range((bars + 7) // 8):
        st, left = section * 8 * meter, total - section * 8 * meter
        if left < meter * 2:
            continue
        lead = 0 if section % 2 == 0 else 1
        if key == 'town':
            quote('A', lead, st, [1, .5, .5, 1, 1, 4], 'A 動機放慢成兩小節問句' + ('，木管接唱' if lead else ''), shift=-12, prefer=1)
            quote('C', lead, st + 2 * meter, [.5, .5, 1, 1, .5, 4.5], 'C 動機的大六度終止，升兩個八度', shift=24, keep=True)
            quote('B', 0, st + 4 * meter, [.25, .25, .25, .25, 1, 2], 'B 號角（多利安調式下 E♭ 成 E）', shift=12, prefer=1)
            quote('D', 1 - lead, st + 6 * meter, [1.5, 1, .5, 5], 'D 導音上行接回句首', shift=12, keep=True)
        elif key == 'ruins':
            quote('A', 0, st + .5, [1.5, 1, 3.5], 'A 動機前半，錯開半拍', shift=-12, keep=True, upto=3, vel=78)
            quote('A', 1, st + 2 * meter + .5, [1, 1, 4], 'A 動機後半，低八度回聲', shift=-12, keep=True, frm=3, vel=70)
            if left > 5 * meter:
                quote('B', 0, st + 5 * meter, [.5, .5, .5, .5, 2, 4], 'B 號角放慢一倍、遠處的弱音', shift=0, keep=True, vel=66)
        elif key == 'well':
            quote('D', 0, st, [2, 1, 1, 4], 'D 動機增值成上行問句', shift=shift + 12, keep=True, vel=78)
            quote('A', 1, st + 2 * meter, [1, .5, .5, 1, 1, 4], 'A 動機倒影成上行回答', shift=shift - 12, inv=True, prefer=-1, vel=72)
            if left > 6 * meter:
                quote('C', 0, st + 5 * meter, [1, 1, 1, 1, 1, 3], 'C 動機在多利安調式下原形回答', shift=shift + 24, keep=True, vel=74)
        elif key == 'mines':
            quote('B', 0, st, [.25, .25, .25, .25, 1, 2], 'B 動機原形：同音四連打當鎬擊', shift=shift, keep=True)
            quote('A', 1, st + 1 * meter, [.5, .5, .5, .5, .5, 1.5], 'A 動機八分音符下行', shift=shift - 12, keep=True, vel=76)
            quote('B', 0, st + 4 * meter, [.25, .25, .25, .25, 1, 2], 'B 動機上移四度再擊一次（D♭→D）', shift=shift + 5, prefer=1)
            quote('D', 1, st + 6 * meter, [1, 1, 1, 4], 'D 導音上行', shift=shift, keep=True, vel=76)
        elif key == 'depths':
            quote('A', 1, st, [2, 2, 3, 3, 2, 4], 'A 動機降兩個八度並增值，弗里吉安化（A→A♭）', shift=-24, prefer=-1, vel=76)
            if left > 16:
                quote('D', 0, st + 4 * meter, [2, 2, 2, 6], 'D 動機在弗里吉安調式下（導音降成 F）', shift=-12, prefer=-1, vel=72)
        elif key == 'glacier':
            quote('A', 0, st, [1, .5, .5, 1, 1, 2], 'A 動機改成三拍句型', shift=shift - 12, keep=True)
            quote('C', 1, st + 2 * meter, [1, 1, 1, 1, 1, 1], 'C 動機轉小調回答（E→E♭ 的對應音 B→B♭）', shift=shift + 24, prefer=-1, vel=76)
            quote('A', 0, st + 4 * meter, [.5, .5, .5, .5, 1, 3], 'A 動機原速十六分改八分', shift=shift, keep=True)
            quote('D', 1, st + 6 * meter, [1, 1, 1, 3], 'D 導音上行接回', shift=shift + 12, keep=True, vel=76)
        elif key in ('finale', 'battle', 'battle-boss'):
            inv = key == 'battle-boss'
            rhythm = [.5] * 6 if key == 'battle' else [1, .5, .5, .5, .5, 1]
            quote('A', 0, st, rhythm, 'A 動機' + ('音階內倒影、落在低音' if inv else '八分音符瀑布'), shift=shift - (36 if inv else 0), inv=inv,
                  keep=not inv, prefer=-1, vel=90)
            quote('B', 1, st + meter, [.25, .25, .25, .25, 1, 1], 'B 號角由第二聲部回答', shift=shift + (0 if inv else 12), keep=True, vel=86)
            quote('C', 0, st + 3 * meter, [.5, .5, .5, .5, .5, 1.5], 'C 動機轉小調（E→E♭）作切分終止', shift=shift + 24 - (12 if inv else 0), prefer=-1, vel=88)
            quote('A', 0, st + 5 * meter, [.5, .5, .5, .5, 1, 1], 'A 動機再現' + ('，升四度' if section % 2 else ''), shift=shift + (5 if section % 2 else 0) - (12 if inv else 0),
                  keep=section % 2 == 0, prefer=-1, vel=90)
            quote('D', 1, st + 7 * meter, [.5, .5, .5, 2.5], 'D 導音上行接回句首', shift=shift + 12, keep=True, vel=84)
        elif key == 'camp':
            quote('A', lead, st, [1, 1, 1, 1, 1, 1], 'A 動機以原調音高唱成三拍句' + ('，木管接唱' if lead else ''), prefer=-1, vel=74)
            quote('D', 1 - lead, st + 3 * meter, [1, 1, 1, 3], 'D 動機在大調下（F♯→F）', shift=12, prefer=-1, vel=70)
            quote('A', lead, st + 5 * meter, [1, 1, 1, 1, 1, 4], 'A 動機逆行接回', prefer=-1, vel=72)
        elif key == 'sanctuary':
            quote('A', 0, st, [2, 2, 2, 2, 4, 4], 'A 動機四倍增值，聖詠分句（A→A♭）', prefer=-1, vel=74)
            quote('B', 1, st + 4 * meter, [1, 1, 1, 1, 4, 8], 'B 動機同音改成鐘聲', shift=0, prefer=-1, vel=66)
    # 逆行：camp 第二次的 A 動機要倒過來
    if key == 'camp':
        for q in quotes:
            if q['transformation'].startswith('A 動機逆行'):
                rev = list(reversed(q['pitches_midi']))
                for n in notes:
                    for b, p, r in zip(q['onsets_beats'], q['pitches_midi'], rev):
                        if n['channel'] == q['channel'] and abs(n['start'] - b * spb) < 1e-9 and n['pitch'] == p:
                            n['pitch'] = r
                q['pitches_midi'], q['pitch_sequence'] = rev, [name(p) for p in rev]
    if key == 'finale':  # 第五段起主旋律的小三度升成大三度
        for n in notes:
            if n['start'] >= 32 * meter * spb and n['channel'] in (0, 1) and (n['pitch'] - root) % 12 == 3:
                n['pitch'] += 1
        for q in quotes:
            if q['onsets_beats'][0] >= 32 * meter:
                q['pitches_midi'] = [p + 1 if (p - root) % 12 == 3 else p for p in q['pitches_midi']]
                q['pitch_sequence'] = [name(p) for p in q['pitches_midi']]
                q['transformation'] += '，借用大三度'
    return notes, quotes, total * spb


def title_patch(vgm):
    """VGM 中第 0 聲道第一次 key-on 時的音色（原曲三個聲道同一組，規格 014 §1）。"""
    d = Path(vgm).read_bytes()
    i, regs = struct.unpack_from('<I', d, 0x34)[0] + 0x34, [0] * 256
    while i < len(d):
        c = d[i]
        if c == 0x5A:
            r, v = d[i + 1], d[i + 2]
            if r == 0xB0 and v & 0x20:
                return {f'{b:02x}': [regs[b], regs[b + 3]] for b in (0x20, 0x40, 0x60, 0x80, 0xE0)} | {'c0': regs[0xC0]}
            regs[r] = v
            i += 3
        elif c == 0x61:
            i += 3
        elif c == 0x66:
            break
        else:
            i += 1
    raise SystemExit('VGM 沒有第 0 聲道的 key-on')


def vgm_to_opl(vgm):
    d = Path(vgm).read_bytes()
    i, t, out = struct.unpack_from('<I', d, 0x34)[0] + 0x34, 0, []
    while i < len(d):
        c = d[i]
        if c == 0x5A:
            out.append(f'{t / 44100:.9f} {d[i + 1]:02x} {d[i + 2]:02x}\n')
            i += 3
        elif c == 0x61:
            t += struct.unpack_from('<H', d, i + 1)[0]
            i += 3
        elif c in (0x62, 0x63):
            t += 735 if c == 0x62 else 882
            i += 1
        elif 0x70 <= c <= 0x7F:
            t += (c & 15) + 1
            i += 1
        elif c == 0x66:
            break
        else:
            i += 1
    return '# 秒 暫存器 值；原版標題曲（VGM 轉出）\n' + ''.join(out)


ROLES = ['lead', 'reed', 'pad', 'pad', 'bass', 'plucked', 'plucked', 'plucked', 'bell']


def instrument(src, role, key):
    """由原曲音色衍生各角色；回 (暫存器, 修改說明)。lead 是原曲音色原樣。"""
    p, ch = copy.deepcopy(src), {}
    if role == 'reed':
        p['20'] = [0x21, 0x21]; p['40'] = [0x60, 0x86]; p['60'] = [0x85, 0x86]; p['80'] = [0x46, 0x46]; p['c0'] = 0x06
        ch = {'20': '持續音、兩個運算子一倍頻', '40': '調變 TL 27→32、載波 TL 1→6', '60': '短句木管起音', '80': '可控釋音', 'c0': '回授降到 3'}
    elif role == 'pad':
        p['20'] = [0x21, 0x21]; p['40'] = [0x26, 0x14]; p['60'] = [0x63, 0x74]; p['80'] = [0x57, 0x57]; p['c0'] = 0x04
        ch = {'20': '持續音、一倍頻', '40': '減少調變、降低音量', '60': '柔化起音', '80': '中等衰減與釋音', 'c0': '回授降到 2'}
    elif role == 'plucked':
        p['20'] = [0x21, 0x21]; p['40'] = [0x24, 0x12]; p['60'] = [0xA4, 0xB5]; p['80'] = [0x57, 0x48]; p['c0'] = 0x04
        ch = {'20': '一倍頻', '40': '調變與音量降低', '60': '撥弦快速起音與衰減', '80': '短衰減、短釋音', 'c0': '回授降到 2'}
    elif role == 'bass':
        p['20'] = [0x21, 0x21]; p['60'] = [0xF3, 0xF4]; p['80'] = [0x26, 0x26]
        ch = {'20': '持續音、調變改一倍頻', '60': '保留原曲起音，加衰減', '80': '低頻釋音加長'}
    elif role == 'bell':
        p['20'] = [0x07, 0x01]; p['40'] = [0x4f, 0x88]; p['60'] = [0xF2, 0xF2]; p['80'] = [0x24, 0x24]
        ch = {'20': '調變七倍頻的鐘音泛音', '40': '調變 TL 15、載波 TL 8', '60': '衰減', '80': '長釋音'}
    if key in ('camp', 'sanctuary', 'depths', 'well', 'ruins'):
        p['40'][1] = (p['40'][1] & 0xC0) | min(63, (p['40'][1] & 63) + 4)
        ch['40_quiet'] = '安靜曲目載波另降 3 dB'
    return p, ch


def to_opl(notes, patches, duration):
    writes, seq = [], 0

    def put(t, r, v):
        nonlocal seq
        writes.append((t, seq, r, v))
        seq += 1

    put(0, 0x01, 0x20)
    put(0, 0xBD, 0x00)
    for ch, p in enumerate(patches):
        for base in (0x20, 0x40, 0x60, 0x80, 0xE0):
            for i in (0, 1):
                put(0, base + OFF[ch] + 3 * i, p[f'{base:02x}'][i])
        put(0, 0xC0 + ch, p['c0'])
        put(0, 0xB0 + ch, 0)
    events = []
    for n in notes:
        f = 440 * 2 ** ((n['pitch'] - 69) / 12)
        block = 0
        while f * 2 ** (20 - block) / 49716 > 1023:
            block += 1
        fn = round(f * 2 ** (20 - block) / 49716)
        hi = ((fn >> 8) & 3) | (block << 2)
        events += [(n['end'], 0, n, hi, fn), (n['start'], 1, n, hi, fn)]
    for t, on, n, hi, fn in sorted(events, key=lambda e: (e[0], e[1], e[2]['channel'])):
        ch, p = n['channel'], patches[n['channel']]
        if not on:
            put(t, 0xB0 + ch, hi)
            continue
        att = round((100 - n['velocity']) * .24)  # 力度轉載波 TL；加法合成時兩個運算子一起
        for i in ((0, 1) if p['c0'] & 1 else (1,)):
            v = p['40'][i]
            put(t, 0x40 + OFF[ch] + 3 * i, (v & 0xC0) | min(63, (v & 63) + att))
        put(t, 0xA0 + ch, fn & 255)
        put(t, 0xB0 + ch, hi | 0x20)
    put(duration, 0xBD, 0)
    return '# 秒 暫存器 值；OPL2 九聲道旋律模式\n' + ''.join(f'{t:.9f} {r:02x} {v:02x}\n' for t, _, r, v in sorted(writes))


RIGHTS = '衍生自 SSI 原版標題曲的新編曲，隨可散布包私下分享給持有原版者，不公開上架。'


def compose(a):
    a.out.mkdir(parents=True, exist_ok=True)
    src = title_patch(a.vgm)
    (a.out / 'title.opl').write_text(vgm_to_opl(a.vgm))
    man = dict(spec='docs/spec/014-in-game-music.md', source=dict(vgm_sha256=hashlib.sha256(Path(a.vgm).read_bytes()).hexdigest(),
               title_patch={k: v for k, v in src.items()}), motifs=MOTIFS, rights=RIGHTS,
               generation='tools/music_compose.py：曲目表定義和聲與樂句，確定性九聲部編曲（不用亂數）；dosgolem cmd/cok-opl-render 渲染', tracks=[])
    for s in SCORES:
        key, title, use, bpm, meter, bars = s[:6]
        notes, quotes, length = make_score(s)
        for ch in range(9):  # 每聲道同時一音
            ns = sorted((n for n in notes if n['channel'] == ch), key=lambda n: n['start'])
            for x, y in zip(ns, ns[1:]):
                if x['end'] > y['start'] + 1e-9:
                    raise SystemExit(f'{key} 第 {ch} 聲道重疊：{x} {y}')
        ps = [instrument(src, r, key) for r in ROLES]
        ps[0] = (copy.deepcopy(src), {})
        loop = key not in ('victory', 'defeat')
        musical = bars * meter * 60 / bpm
        body = to_opl(notes, [p for p, _ in ps], musical if loop else length)
        (a.out / f'{key}.opl').write_text(body)
        man['tracks'].append(dict(key=key, title=title, purpose=use, loop=loop, loop_start=0.0, loop_end=round(musical, 6) if loop else None,
                                  length=round(musical if loop else length, 6), meter=f'{meter}/4', bars=bars, bpm=bpm, tonality=s[8], texture=s[9],
                                  design=s[11], notes=len(notes), motif_quotes=quotes,
                                  instruments=[dict(channel=c, role='lead' if c == 0 else ROLES[c], modifications=ps[c][1], registers=ps[c][0]) for c in range(9)],
                                  opl_sha256=hashlib.sha256(body.encode()).hexdigest()))
        print(f'{key:12s} {bpm:3d} BPM {bars:2d} 小節 {musical if loop else length:6.2f} 秒 {len(notes):4d} 音 {len(quotes):2d} 次動機')
    (a.out / 'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=1) + '\n')


def wav_stats(path):
    with wave.open(str(path), 'rb') as w:
        assert w.getsampwidth() == 2
        x = array('h', w.readframes(w.getnframes()))
    s = sum(v * v for v in x)
    return math.sqrt(s / max(1, len(x))) / 32768, max(abs(min(x)), max(x)) / 32768


def master(a):
    man = json.loads((a.out / 'manifest.json').read_text())
    t_rms, t_peak = wav_stats(a.out / 'title.wav')
    man['mastering'] = dict(title_rms_dbfs=round(20 * math.log10(t_rms), 2), title_peak_dbfs=round(20 * math.log10(t_peak), 2), target='標題曲 RMS × 0.7')
    rows = ['key\tloop\tloop_start\tloop_end\tlength\tgain']
    for t in man['tracks']:
        rms, peak = wav_stats(a.out / f"{t['key']}.wav")
        gain = .7 * t_rms / rms
        t.update(rms_dbfs=round(20 * math.log10(rms), 2), peak_dbfs=round(20 * math.log10(peak), 2), gain=round(gain, 3),
                 peak_after_gain_dbfs=round(20 * math.log10(peak * gain), 2), wav_sha256=hashlib.sha256((a.out / f"{t['key']}.wav").read_bytes()).hexdigest())
        le = t['loop_end'] if t['loop'] else 0
        rows.append(f"{t['key']}\t{int(t['loop'])}\t0.000\t{le:.3f}\t{t['length']:.3f}\t{gain:.3f}")
        print(f"{t['key']:12s} RMS {t['rms_dbfs']:6.2f} dBFS 峰值 {t['peak_dbfs']:6.2f} 增益 {gain:.3f} → 峰值 {t['peak_after_gain_dbfs']:6.2f}")
    (a.out / 'music.tsv').write_text('\n'.join(rows) + '\n')
    (a.out / 'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=1) + '\n')
    print(f'標題曲 RMS {man["mastering"]["title_rms_dbfs"]} dBFS 峰值 {man["mastering"]["title_peak_dbfs"]}')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('compose')
    c.add_argument('--vgm', required=True)
    c.add_argument('--out', required=True, type=Path)
    m = sub.add_parser('master')
    m.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    compose(a) if a.cmd == 'compose' else master(a)


if __name__ == '__main__':
    main()
