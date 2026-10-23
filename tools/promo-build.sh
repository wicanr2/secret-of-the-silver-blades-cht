#!/usr/bin/env bash
# 推廣影片組裝（規格 016，由克萊恩英豪移植）：依剪輯表把 workplace/promo/seg/<段>/ 的畫格與音訊剪成片段，加字卡與片尾，接成
# workplace/promo/sosb-promo.mp4（1920×1200、30 fps、H.264＋AAC）。前置：tools/promo-rec.sh 錄好各段。
#
# 剪輯表每列：段 開始秒 長度秒 字卡（-＝無） 背景曲（-＝無）。段有三種寫法：
#   <段名>                    一般片段，畫面與遊戲音訊取自該段
#   story:<底圖段>:<畫格>     故事字卡：該段該畫格壓暗當底圖，字卡欄是旁白（| 換行），只有背景曲
#   wipe:<原版段>:<HD 段>     HD 切換示範：兩段同時間軸，片段 40% 處以由左往右擦除從原版切到 HD
# 原版開場劇情沒有音樂（規格 014 §1），這幾段以新編配樂的渲染檔（workplace/music/out/<曲>.wav）墊底，
# 同一首曲子跨片段接續播放。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; P="$ROOT/workplace/promo"; FONTS=/usr/share/fonts/opentype/noto
CUTS='title	27.0	9.0	-	-
story:title:400	0	3.6	三百年前，法師艾達瑪為求長生墮落成巫妖「恐怖魔王」。|聖騎士奧斯沃夫率領「銀刃」討伐，山谷從此被冰河封住。	ruins
story:open:60	0	3.6	如今礦工小鎮新維地格里城打開了新礦坑，|怪物從地底一層接著一層湧出。	ruins
story:open:400	0	3.6	知識之井也被某種力量控制，|市長向你們求援：請在小鎮毀滅以前救救我們。	ruins
story:town:700	0	3.6	黑圈幫正逐步解開銀刃的封印，|你們必須接下銀刃的旗幟。	ruins
open	2.0	3.0	劇情全文繁體中文	well
open	12.2	3.0	人物對話	-
open	18.2	3.5	手札內文自動顯示	-
open	33.0	2.6	選單中文化	-
town	13.0	6.0	3D 探索	-
wipe:town-nohd:town	19.0	5.0	HD 切換：原版 → HD 重繪（3 倍畫面，F2 切換倍率）	-
town	33.0	2.3	地圖疊層：攻略點與圖例	-
town	36.0	4.0	軟體世界攻略對照	-
battle	0.6	7.0	戰鬥	-
wipe:battle-nohd:battle	7.6	5.0	HD 切換：戰鬥圖塊與人物	-
f12	1.4	5.2	F12 中文 ↔ 英文原版即時切換	-
langs	0.8	5.0	繁中・简中・日本語・한국어・English	-'
segs=$(printf '%s\n' "$CUTS" | cut -f1 | tr ':' '\n' | grep -v '^\(story\|wipe\|[0-9]*\)$' | sort -u)
for s in $segs; do test -f "$P/seg/$s/audio.s16le" || { echo "缺 $P/seg/$s" >&2; exit 1; }; done
test -f "$FONTS/NotoSansCJK-Bold.ttc"; test -f "$ROOT/workplace/music/out/finale.wav"
rm -rf "$P/build"; mkdir -p "$P/build"; printf '%s\n' "$CUTS" > "$P/build/cuts.tsv"
DR=(docker run --rm --network none -u "$(id -u):$(id -g)" --memory 2g --cpus 4 --pids-limit 512 --log-opt max-size=10m --log-opt max-file=3)
# 字卡（一般片段為透明 PNG，故事字卡為不透明整張）與片尾
timeout 300s "${DR[@]}" -i -v "$FONTS:/fonts:ro" -v "$P:/p" --entrypoint python sosb-img:r1 -I - <<'PY'
from PIL import Image, ImageDraw, ImageFilter, ImageFont
B = lambda n: ImageFont.truetype('/fonts/NotoSansCJK-Bold.ttc', n, index=3)  # TC
R = lambda n: ImageFont.truetype('/fonts/NotoSansCJK-Regular.ttc', n, index=3)
for i, line in enumerate(open('/p/build/cuts.tsv', encoding='utf-8').read().splitlines()):
    seg, cap = line.split('\t')[0], line.split('\t')[3].strip('-')
    if seg.startswith('story:'):
        _, bg, n = seg.split(':')
        im = Image.open(f'/p/seg/{bg}/frames/{int(n):06d}.png').convert('RGB').resize((1920, 1200), Image.NEAREST)
        im = Image.blend(im.filter(ImageFilter.GaussianBlur(3)), Image.new('RGB', im.size), 0.55)
        d = ImageDraw.Draw(im); f = B(60); lines = cap.split('|'); y = 600 - len(lines) * 50
        for s in lines:
            x = (1920 - d.textlength(s, font=f)) / 2
            d.text((x + 3, y + 3), s, font=f, fill=(0, 0, 0)); d.text((x, y), s, font=f, fill=(255, 236, 190))
            y += 100
        im.save(f'/p/build/cap{i:02d}.png'); continue
    im = Image.new('RGBA', (1920, 1200), (0, 0, 0, 0))
    if cap:
        d = ImageDraw.Draw(im); f = B(52)
        w = d.textlength(cap, font=f)
        d.rounded_rectangle((40, 1030, 40 + w + 64, 1130), 18, fill=(0, 0, 0, 190))
        d.text((72, 1050), cap, font=f, fill=(255, 230, 150, 255))
    im.save(f'/p/build/cap{i:02d}.png')
im = Image.new('RGB', (1920, 1200), (8, 10, 24)); d = ImageDraw.Draw(im)
def center(y, s, f, c):
    d.text(((1920 - d.textlength(s, font=f)) / 2, y), s, font=f, fill=c)
center(330, '銀色匕首之謎', B(150), (200, 225, 255))
center(530, 'Secret of the Silver Blades　繁體中文版', B(64), (235, 235, 235))
center(700, '原版 DOS 程式即時覆繪・HD 重繪・原版 AdLib 音效與新編配樂', R(42), (190, 200, 220))
center(770, '繁中・简中・日本語・한국어・English', R(42), (190, 200, 220))
center(1060, '原作 © 1990 TSR, Inc. / Strategic Simulations, Inc.　非官方玩家中文化', R(30), (130, 140, 160))
im.save('/p/build/end.png')
PY
FF=(timeout 600s "${DR[@]}" -v "$P:/p" -v "$ROOT/workplace/music/out:/m:ro" cok-ffmpeg:r1 ffmpeg -hide_banner -loglevel error -y)
ENC=(-c:v libx264 -preset slow -crf 18 -r 30 -c:a aac -b:a 192k -ar 48000 -ac 2)
# 渲染檔是增益 1 的原始響度，墊底時乘上 music.tsv 的 gain（與遊戲內同響度）
gain() { awk -F'\t' -v k="$1" '$1 == k {print $6; f = 1} END {if (!f) print 1}' "$ROOT/workplace/music/out/music.tsv"; }
i=0; : > "$P/build/list.txt"; declare -A BED
while IFS=$'\t' read -r seg start dur cap bed; do
  n=$(printf '%02d' "$i"); first=$(awk -v s="$start" 'BEGIN{printf "%d", s*30+0.5}'); frames=$(awk -v d="$dur" 'BEGIN{printf "%d", d*30+0.5}')
  fo=$(awk -v d="$dur" 'BEGIN{printf "%.2f", d-0.25}'); ce=$(awk -v d="$dur" 'BEGIN{printf "%.2f", d-0.2}')
  off=0; [[ "$bed" != - ]] && off="${BED[$bed]:-0}"
  [[ "$bed" != - ]] && BED[$bed]=$(awk -v a="$off" -v d="$dur" 'BEGIN{printf "%.3f", a+d}')
  bedf="[b]"; beds=(); [[ "$bed" != - ]] && beds=(-ss "$off" -t "$dur" -i "/m/$bed.wav")
  g=$(gain "$bed"); bv9=$(awk -v g="$g" 'BEGIN{printf "%.3f", 0.9*g}'); bv8=$(awk -v g="$g" 'BEGIN{printf "%.3f", 0.8*g}')
  case "$seg" in
  story:*)
    "${FF[@]}" -loop 1 -framerate 30 -t "$dur" -i "/p/build/cap$n.png" "${beds[@]}" \
      -filter_complex "[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st=$(awk -v d="$dur" 'BEGIN{printf "%.2f", d-0.4}'):d=0.4,format=yuv420p[v];[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=$bv9,afade=t=in:st=0:d=0.3,afade=t=out:st=$fo:d=0.25[a]" \
      -map "[v]" -map "[a]" -frames:v "$frames" "${ENC[@]}" "/p/build/c$n.mp4" ;;
  wipe:*)
    IFS=: read -r _ orig hd <<< "$seg"
    at=$(awk -v d="$dur" 'BEGIN{printf "%.2f", d*0.4}'); hdfirst=$(awk -v f="$first" -v a="$at" 'BEGIN{printf "%d", f+a*30+0.5}')
    "${FF[@]}" -framerate 30 -start_number "$first" -t "$dur" -i "/p/seg/$orig/frames/%06d.png" \
      -framerate 30 -start_number "$hdfirst" -t "$(awk -v d="$dur" -v a="$at" 'BEGIN{printf "%.2f", d-a}')" -i "/p/seg/$hd/frames/%06d.png" \
      -f s16le -ar 48000 -ac 2 -ss "$start" -t "$dur" -i "/p/seg/$hd/audio.s16le" -loop 1 -framerate 30 -i "/p/build/cap$n.png" \
      -filter_complex "[0:v]scale=1920:1200:flags=neighbor,format=rgba,setpts=PTS-STARTPTS[o];[1:v]scale=1920:1200:flags=neighbor,format=rgba,setpts=PTS-STARTPTS[h];[o][h]xfade=transition=wipeleft:duration=1.2:offset=$at[x];[3:v]fade=t=in:st=0.3:d=0.3:alpha=1[c];[x][c]overlay=0:0:enable='between(t,0.3,$ce)':shortest=1,fade=t=in:st=0:d=0.25,fade=t=out:st=$fo:d=0.25,format=yuv420p[v];[2:a]afade=t=in:st=0:d=0.15,afade=t=out:st=$fo:d=0.25[a]" \
      -map "[v]" -map "[a]" -frames:v "$frames" "${ENC[@]}" "/p/build/c$n.mp4" ;;
  *)
    amix="[1:a]anull"
    [[ "$bed" != - ]] && amix="[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=$bv8[b];[1:a][b]amix=inputs=2:duration=first:normalize=0"
    "${FF[@]}" -framerate 30 -start_number "$first" -i "/p/seg/$seg/frames/%06d.png" \
      -f s16le -ar 48000 -ac 2 -ss "$start" -t "$dur" -i "/p/seg/$seg/audio.s16le" -loop 1 -framerate 30 -i "/p/build/cap$n.png" \
      "${beds[@]}" -filter_complex "[0:v]scale=1920:1200:flags=neighbor,format=rgba[g];[2:v]fade=t=in:st=0.3:d=0.3:alpha=1[c];[g][c]overlay=0:0:enable='between(t,0.3,$ce)':shortest=1,fade=t=in:st=0:d=0.25,fade=t=out:st=$fo:d=0.25,format=yuv420p[v];$amix[m];[m]afade=t=in:st=0:d=0.15,afade=t=out:st=$fo:d=0.25[a]" \
      -map "[v]" -map "[a]" -frames:v "$frames" "${ENC[@]}" "/p/build/c$n.mp4" ;;
  esac
  echo "file 'c$n.mp4'" >> "$P/build/list.txt"; i=$((i+1))
done <<< "$CUTS"
"${FF[@]}" -loop 1 -framerate 30 -i /p/build/end.png -ss 0 -t 6 -i /m/finale.wav \
  -filter_complex "[0:v]fade=t=in:st=0:d=0.6,fade=t=out:st=5.2:d=0.8,format=yuv420p[v];[1:a]aresample=48000,volume=$(gain finale),afade=t=in:st=0:d=0.4,afade=t=out:st=4.5:d=1.5[a]" \
  -map "[v]" -map "[a]" -t 6 "${ENC[@]}" /p/build/end.mp4
echo "file 'end.mp4'" >> "$P/build/list.txt"
timeout 300s "${DR[@]}" -v "$P:/p" cok-ffmpeg:r1 ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i /p/build/list.txt \
  -c copy -movflags +faststart /p/sosb-promo.mp4
timeout 60s "${DR[@]}" -v "$P:/p:ro" cok-ffmpeg:r1 ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,duration -of compact /p/sosb-promo.mp4
