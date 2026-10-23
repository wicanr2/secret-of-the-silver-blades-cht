package sosb

import (
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wicanr2/dosgolem/xlate"
)

func writeMapPNG(t *testing.T, path string, w, h int, c color.RGBA) {
	t.Helper()
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	for i := 0; i < len(img.Pix); i += 4 {
		img.Pix[i], img.Pix[i+1], img.Pix[i+2], img.Pix[i+3] = c.R, c.G, c.B, 0xFF
	}
	f, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	if err := png.Encode(f, img); err != nil {
		t.Fatal(err)
	}
}

func TestLoadJournalMapsMissingDirIsEmpty(t *testing.T) {
	m, err := LoadJournalMaps(filepath.Join(t.TempDir(), "沒有"))
	if err != nil || len(m) != 0 {
		t.Fatalf("目錄不存在應回空表：%v %v", m, err)
	}
}

func TestLoadJournalMapsRejectsWrongSize(t *testing.T) {
	dir := t.TempDir()
	writeMapPNG(t, filepath.Join(dir, "01-1.png"), 640, 400, color.RGBA{1, 2, 3, 255})
	if _, err := LoadJournalMaps(dir); err == nil || !strings.Contains(err.Error(), "912×504") {
		t.Fatalf("尺寸不符要報錯，得 %v", err)
	}
}

func TestJournalMapPages(t *testing.T) {
	dir := t.TempDir()
	writeMapPNG(t, filepath.Join(dir, "01-2.png"), JournalMapW, JournalMapH, color.RGBA{200, 10, 10, 255})
	writeMapPNG(t, filepath.Join(dir, "01-1.png"), JournalMapW, JournalMapH, color.RGBA{10, 200, 10, 255})
	writeMapPNG(t, filepath.Join(dir, "readme.txt.png"), 1, 1, color.RGBA{}) // 不符命名規則的檔不讀
	maps, err := LoadJournalMaps(dir)
	if err != nil {
		t.Fatal(err)
	}
	j := &JournalPanel{
		Entries: map[int]JournalEntry{1: {Title: "地圖", Body: "（本則為地圖。）"}, 2: {Title: "文字", Body: "正文"}},
		Format:  JournalFormat{Title: "第{entry}則 {title}", Page: "{page}／{pages}", None: "無"},
		Maps:    maps,
	}
	if !j.OpenAuto(1, 0) {
		t.Fatal("OpenAuto(1) 失敗")
	}
	if len(j.pages) != 2 || len(j.maps) != 2 {
		t.Fatalf("第 1 則應有 2 頁圖：pages=%d maps=%d", len(j.pages), len(j.maps))
	}
	font := &xlate.Font{W: 16, H: 16, Glyphs: map[rune][]byte{}}
	for _, scale := range []int{2, 3} {
		j.page = 0
		dst := make([]uint8, 320*scale*200*scale*4)
		j.Draw(dst, scale, font, nil)
		at := func(x, y int) [3]uint8 {
			i := (y*320*scale + x) * 4
			return [3]uint8{dst[i], dst[i+1], dst[i+2]}
		}
		// 第 1 頁是 01-1（綠）；圖面在 [8,312)×[16,184)，比文字頁的下緣 128 還低
		if c := at(100*scale, 150*scale); c != [3]uint8{10, 200, 10} {
			t.Fatalf("%d 倍第 1 頁圖面顏色 %v", scale, c)
		}
		if c := at(4*scale, 150*scale); c != [3]uint8{} {
			t.Fatalf("%d 倍面板外不應畫：%v", scale, c)
		}
		j.TurnPage(1)
		j.Draw(dst, scale, font, nil)
		if c := at(311*scale, 183*scale); c != [3]uint8{200, 10, 10} {
			t.Fatalf("%d 倍第 2 頁右下角顏色 %v", scale, c)
		}
	}
	if !j.Contains(100, 150) || j.Contains(100, 195) {
		t.Fatal("地圖頁的面板範圍到 y=192")
	}
	j.CloseAuto()
	j.OpenAuto(2, 0)
	if j.maps != nil || len(j.pages) != 1 {
		t.Fatalf("沒有圖的手札照舊顯示正文：maps=%v pages=%d", j.maps != nil, len(j.pages))
	}
	if j.Contains(100, 150) {
		t.Fatal("文字頁的面板下緣是 128")
	}
}
