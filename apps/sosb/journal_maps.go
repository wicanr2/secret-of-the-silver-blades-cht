package sosb

import (
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"

	"github.com/wicanr2/dosgolem/xlate"
)

// 規格 022（主專案 docs/spec/022-journal-maps.md）：手札地圖則的圖面。圖檔由主專案 tools/journal_maps.py
// 從英文手札產生（原版衍生，不進版控），每張 912×504，是 3 倍的 304×168 邏輯點。
const (
	JournalMapW, JournalMapH = 912, 504
	journalMapX, journalMapY = 8, 16 // 圖面左上（邏輯像素）；第 0 列標題在 y=8
	journalMapPageY          = 184   // 多頁時的頁碼列
	journalMapBottom         = 192   // 地圖頁面板下緣
)

var journalMapName = regexp.MustCompile(`^([0-9]{1,3})-([0-9]{1,2})\.png$`)

// LoadJournalMaps 讀 dir 下的 NN-K.png（第 NN 則的第 K 頁）；目錄不存在回空表。
func LoadJournalMaps(dir string) (map[int][]*image.RGBA, error) {
	ents, err := os.ReadDir(dir)
	if os.IsNotExist(err) {
		return map[int][]*image.RGBA{}, nil
	}
	if err != nil {
		return nil, err
	}
	type page struct {
		k   int
		img *image.RGBA
	}
	by := map[int][]page{}
	for _, e := range ents {
		m := journalMapName.FindStringSubmatch(e.Name())
		if m == nil || e.IsDir() {
			continue
		}
		n, _ := strconv.Atoi(m[1])
		k, _ := strconv.Atoi(m[2])
		f, err := os.Open(filepath.Join(dir, e.Name()))
		if err != nil {
			return nil, err
		}
		src, err := png.Decode(f)
		f.Close()
		if err != nil {
			return nil, fmt.Errorf("sosb: 手札地圖 %s：%w", e.Name(), err)
		}
		if b := src.Bounds(); b.Dx() != JournalMapW || b.Dy() != JournalMapH {
			return nil, fmt.Errorf("sosb: 手札地圖 %s 是 %d×%d，要 %d×%d", e.Name(), b.Dx(), b.Dy(), JournalMapW, JournalMapH)
		}
		img := image.NewRGBA(image.Rect(0, 0, JournalMapW, JournalMapH))
		draw.Draw(img, img.Bounds(), src, src.Bounds().Min, draw.Src)
		by[n] = append(by[n], page{k, img})
	}
	out := make(map[int][]*image.RGBA, len(by))
	for n, ps := range by {
		sort.Slice(ps, func(a, b int) bool { return ps[a].k < ps[b].k })
		for _, p := range ps {
			out[n] = append(out[n], p.img)
		}
	}
	return out, nil
}

// drawMapImage 以面積平均把圖縮放進 scale 倍畫面的 (x0,y0) 起、dw×dh 的範圍（scale=3 時一比一）。
func drawMapImage(dst []uint8, scale int, img *image.RGBA, x0, y0, dw, dh int) {
	w := 320 * scale
	sw, sh := img.Bounds().Dx(), img.Bounds().Dy()
	for y := 0; y < dh; y++ {
		sy0, sy1 := y*sh/dh, max((y+1)*sh/dh, y*sh/dh+1)
		for x := 0; x < dw; x++ {
			sx0, sx1 := x*sw/dw, max((x+1)*sw/dw, x*sw/dw+1)
			var r, g, b, n int
			for sy := sy0; sy < sy1; sy++ {
				i := img.PixOffset(sx0, sy)
				for sx := sx0; sx < sx1; sx++ {
					r, g, b, n = r+int(img.Pix[i]), g+int(img.Pix[i+1]), b+int(img.Pix[i+2]), n+1
					i += 4
				}
			}
			putRGB(dst, w, x0+x, y0+y, [3]uint8{uint8(r / n), uint8(g / n), uint8(b / n)})
		}
	}
}

// drawMapPage 畫地圖頁：面板 [8,312)×[8,192)，標題、圖面、頁碼（規格 022 §4）。
func (j *JournalPanel) drawMapPage(dst []uint8, scale int, font *xlate.Font, missing func(rune)) {
	w := 320 * scale
	for y := journalY * scale; y < journalMapBottom*scale; y++ {
		for x := journalX * scale; x < (journalX+8*journalCols)*scale; x++ {
			putRGB(dst, w, x, y, journalBG)
		}
	}
	lines := j.Lines()
	drawLine(dst, scale, font, journalX, journalY, journalCols, lines[0], journalTitle, missing)
	drawMapImage(dst, scale, j.maps[j.page], journalMapX*scale, journalMapY*scale, 304*scale, 168*scale)
	if len(j.pages) > 1 {
		drawLine(dst, scale, font, journalX, journalMapPageY, journalCols, lines[journalRows-1], journalPage, missing)
	}
}

// Contains 回邏輯像素 (x, y) 是否在目前顯示的面板內（地圖頁比文字頁高，規格 022 §4；收據判斷差異位置用）。
func (j *JournalPanel) Contains(x, y int) bool {
	if j.Open() && j.n != 0 && j.maps != nil && j.page < len(j.maps) {
		return x >= journalX && x < journalX+8*journalCols && y >= journalY && y < journalMapBottom
	}
	return InJournalPanel(x, y)
}
