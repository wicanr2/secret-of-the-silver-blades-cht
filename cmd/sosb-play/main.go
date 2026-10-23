// Command sosb-play 是《Secret of the Silver Blades》繁中覆繪的可遊玩視窗（secret-of-the-silver-blades-cht）。
//
// 以 session 從原版目錄開機（bootroot 複製到可寫存檔目錄，原版唯讀），每個主機畫格推進
// 原版節奏的指令數，以 apps/sosb.Live 疊上路徑 A、B、C 的中文，2× 或 3× 輸出（F2 切換）。
// F12 即時切換中文／原版（原版看不到這個鍵），F2 切換 2×／3×，F11 全螢幕，F3 靜音，F10 截圖，F9 查驗題答案顯示，
// F5 翻閱已讀手札（PgUp／PgDn 翻頁，←／→ 換則，Esc 關閉）。
// 滑鼠移到視窗頂端時出現切換列（主專案規格 011），點項目等同按對應的功能鍵。
//
// 沒給 -save 時是發行模式（主專案規格 012）：資料從發行包找，原版第一次匯入到使用者資料目錄。
// 自動模式（-frames）供收據使用：依 -script 送鍵，結束時印記憶體與畫面雜湊，
// 並可輸出 -shot（中文合成 RGBA）與 -shot-original（原版合成 RGBA）。
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/audio"
	"github.com/hajimehoshi/ebiten/v2/inpututil"

	"github.com/wicanr2/dosgolem/apps/sosb"
	"github.com/wicanr2/dosgolem/apps/sosb/bgm"
	"github.com/wicanr2/dosgolem/audio/mixer"
	"github.com/wicanr2/dosgolem/bootroot"
	"github.com/wicanr2/dosgolem/host"
	"github.com/wicanr2/dosgolem/internal/machine"
	"github.com/wicanr2/dosgolem/session"
	"github.com/wicanr2/dosgolem/xlate"
)

const (
	windowTitle = "銀色匕首之謎"
	// startEXESHA256 是 G1 盤點的 START.EXE v1.30（secret-of-the-silver-blades-cht docs/re/001）。
	startEXESHA256 = "b6c08c3b0a6e0a6ebac76406f2d9abba7d7a3c8d62d4b0ac121778b9c9136036"
)

func stepsPerHostFrame(clock int) uint64 {
	return machine.ScaleSteps(machine.DefaultVGAFrameEvery, clock) * 70 / 60
}

// observer 把 session 的觀測事件轉給 sosb.Live 與音訊混音器；寫入守衛同時服務 demo 控制（主專案規格 018）
// 與無敵開關（主專案規格 017）。
type observer struct {
	live  *sosb.Live
	mix   *mixer.Mixer
	cheat *sosb.Invincible
}

// GuardRange 回兩者監看範圍的聯集（session 一回合只收一段範圍）；GuardWrite 依位址分派，任一要求還原就還原。
func (o observer) GuardRange(mem session.GuardMemory) (uint32, uint32) {
	lo, hi := o.cheat.GuardRange(mem)
	if d := o.live.Demo; d != nil {
		dl, dh := d.GuardRange(mem)
		switch {
		case dl > dh:
		case lo > hi:
			lo, hi = dl, dh
		default:
			lo, hi = min(lo, dl), max(hi, dh)
		}
	}
	return lo, hi
}
func (o observer) GuardWrite(addr uint32, old, new uint8) bool {
	if d := o.live.Demo; d != nil && d.GuardWrite(addr, old, new) {
		return true
	}
	return o.cheat.GuardWrite(addr, old, new)
}

func (o observer) BeforeStep(v session.StepView) error { return o.live.BeforeStep(v) }
func (o observer) VideoWrite(w machine.VideoWrite)     { o.live.VideoWrite(w.Offset) }
func (o observer) VideoModeChange(machine.ModeChange)  { o.live.ModeChange() }
func (o observer) Frame(indexed []byte, palette [256][3]uint8) {
	o.live.Frame(indexed, palette)
}
func (o observer) OPLWrite(w machine.OPLWrite)           { o.mix.OPLWrite(w) }
func (o observer) SpeakerSample(s machine.SpeakerSample) { o.mix.SpeakerSample(s) }
func (o observer) PITChannel2(c machine.PIT2Change)      { o.mix.PITChannel2(c) }

var namedKeys = map[ebiten.Key]string{
	ebiten.KeyEnter: "Enter", ebiten.KeyNumpadEnter: "Enter", ebiten.KeyEscape: "Escape",
	ebiten.KeyBackspace: "Backspace", ebiten.KeyTab: "Tab",
	ebiten.KeyArrowUp: "Up", ebiten.KeyArrowDown: "Down", ebiten.KeyArrowLeft: "Left", ebiten.KeyArrowRight: "Right",
	ebiten.KeyHome: "Home", ebiten.KeyEnd: "End", ebiten.KeyPageUp: "PgUp", ebiten.KeyPageDown: "PgDn",
	ebiten.KeyInsert: "Insert", ebiten.KeyDelete: "Delete",
	ebiten.KeyNumpad0: "KP0", ebiten.KeyNumpad1: "KP1", ebiten.KeyNumpad2: "KP2", ebiten.KeyNumpad3: "KP3",
	ebiten.KeyNumpad4: "KP4", ebiten.KeyNumpad5: "KP5", ebiten.KeyNumpad6: "KP6", ebiten.KeyNumpad7: "KP7",
	ebiten.KeyNumpad8: "KP8", ebiten.KeyNumpad9: "KP9", ebiten.KeyNumpadDecimal: "KPDot",
	ebiten.KeyF1: "F1", ebiten.KeyF2: "F2", ebiten.KeyF3: "F3", ebiten.KeyF4: "F4", ebiten.KeyF5: "F5",
	ebiten.KeyF6: "F6", ebiten.KeyF7: "F7", ebiten.KeyF8: "F8", ebiten.KeyF9: "F9", ebiten.KeyF10: "F10",
	ebiten.KeyF11: "F11", ebiten.KeyF12: "F12",
}

func init() {
	for k := ebiten.KeyA; k <= ebiten.KeyZ; k++ {
		namedKeys[k] = string(rune('A' + (k - ebiten.KeyA)))
	}
}

type game struct {
	owner    *session.Owner
	scale    int // 輸出倍率 2 或 3（F2 切換，比照拯救地球）
	live     *sosb.Live
	chinese  bool
	frame    int
	frames   int
	script   map[int][]scriptAction
	shot     string
	shotOrig string
	shotDir  string
	budget   uint64
	mix      *mixer.Mixer
	ring     *mixer.Ring
	player   *audio.Player
	muted    bool
	pressing bool
	focused  bool
	samples  []float32
	missing  map[rune]bool
	bar      toolbar           // 視窗頂端切換列（主專案規格 011）
	barText  map[string]string // host-text 的 toolbar.* 文字
	music    *bgm.Player       // 遊戲中配樂（規格 014）；nil 表示沒有素材
	cheat    *sosb.Invincible  // 我方無敵（主專案規格 017），預設關
	langs    []*sosb.LangPack  // 已載入的語言（規格 015），索引 lang 為目前語言
	lang     int
	langDir  string      // 語言選擇記錄的目錄
	mainFont *xlate.Font // -font（切換列在英文版用它）
	cursorX  int         // 游標邏輯位置（切換列懸停用）
	cursorY  int
	// 主專案規格 019：CPU 模擬速度。chunk 是 1x 的每格預算；delayAccel 為 false 時不登記 TP Delay（等價性對照用）。
	speed        speedControl
	speedPath    string
	chunk        uint64
	delayAccel   bool
	tpRegistered bool
	lastSteps    uint64
	accelSteps   uint64
	perf         perfStats
	// 主專案規格 020：切換列字級。
	barSize     barSize
	barSizePath string
	barFonts    barFonts
}

func (g *game) hostInput(u *session.CapturedUpdate) []hostAction {
	in := frameInput{Chars: ebiten.AppendInputChars(nil), Held: map[string]int{},
		Ctrl: ebiten.IsKeyPressed(ebiten.KeyControl), Alt: ebiten.IsKeyPressed(ebiten.KeyAlt)}
	for k, name := range namedKeys {
		if d := inpututil.KeyPressDuration(k); d > 0 && (in.Held[name] == 0 || d < in.Held[name]) {
			in.Held[name] = d
		}
	}
	menuWasOpen := g.bar.menuOpen()
	keys, acts := mapKeys(in, g.panelMode())
	if menuWasOpen { // 選單展開時鍵盤只處理 Esc（主專案規格 019 §3.3）
		keys, acts = nil, nil
		if in.Held["Escape"] == 1 {
			g.bar.speeds, g.bar.sizes = false, false
		}
	}
	u.BIOSKeys = append(u.BIOSKeys, keys...)
	cx, cy := ebiten.CursorPosition()
	dx, dy := dosPoint(cx, cy, g.scale)
	g.cursorX, g.cursorY = dx, dy
	g.bar.track(dx, dy)
	if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) && !g.pressing && menuWasOpen {
		if g.bar.speeds {
			g.clickSpeed(dx, dy)
		}
		if g.bar.sizes {
			g.clickBarFont(dx, dy)
		}
	} else if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) && !g.pressing && g.bar.takesPointer(dx, dy) {
		// 切換列範圍內的點擊由前端處理，不送進遊戲（規格 011 §2.3）
		if a := toolbarClick(g.toolbarItems(), dx, dy); a != 0 {
			acts = append(acts, a)
		}
	} else if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) && !g.pressing {
		if ev := mouseEvent(host.MouseEventDown, dx, dy); ev.Target == host.MouseTargetCanvas {
			u.PointerDown, g.pressing = &ev, true
		}
	}
	if inpututil.IsMouseButtonJustReleased(ebiten.MouseButtonLeft) && g.pressing {
		ev := mouseEvent(host.MouseEventUp, dx, dy)
		u.PointerUp, g.pressing = &ev, false
	}
	focused := ebiten.IsFocused()
	if g.focused && !focused && g.pressing {
		u.FocusLost, g.pressing = true, false
	}
	g.focused = focused
	return acts
}

func (g *game) apply(acts []hostAction) {
	for _, a := range acts {
		switch a {
		case actToggle:
			g.chinese = !g.chinese
		case actMute:
			g.muted = !g.muted
			if g.player != nil {
				g.player.SetVolume(map[bool]float64{true: 0, false: 1}[g.muted])
			}
		case actMusic:
			g.music.Toggle()
		case actCheat:
			if sosb.CheatVerified { // 位址未驗證前停用（apps/sosb cheat.go）
				g.cheat.On = !g.cheat.On
			}
		case actSpeed:
			g.bar.speeds, g.bar.sizes = !g.bar.speeds, false
		case actBarFont:
			g.bar.sizes, g.bar.speeds = !g.bar.sizes, false
		case actLang:
			g.nextLang()
		case actLangCycle:
			g.cycleLang()
		case actScale:
			g.scale = 5 - g.scale // 2 ↔ 3
			if !ebiten.IsFullscreen() {
				ebiten.SetWindowSize(320*g.scale, 200*g.scale)
			}
		case actFullscreen:
			ebiten.SetFullscreen(!ebiten.IsFullscreen())
		case actShot:
			g.screenshot()
		case actAnswers:
			g.live.SetHideAnswers(!g.live.HideAnswers())
		case actJournal:
			if g.chinese && g.live.Journal != nil {
				g.live.Guide.Close() // 與攻略面板、地圖互斥（規格 008 §2.1、009 §2.3）
				g.live.Map.Close()
				g.live.Journal.ToggleBrowse()
			}
		case actGuide:
			if g.chinese && g.live.Guide != nil {
				if g.live.Journal.Browsing() {
					g.live.Journal.ToggleBrowse()
				}
				g.live.Map.Close()
				g.live.Guide.Toggle()
			}
		case actMap:
			if g.chinese && g.live.Map != nil {
				if g.live.Journal.Browsing() {
					g.live.Journal.ToggleBrowse()
				}
				g.live.Guide.Close()
				g.live.Map.Toggle()
			}
		case actReveal:
			g.live.Map.ToggleReveal()
		case actCloseJournal:
			if g.live.Map.Open() {
				g.live.Map.Close()
			} else if g.live.Guide.Open() {
				g.live.Guide.Close()
			} else if g.live.Journal.Browsing() {
				g.live.Journal.ToggleBrowse()
			}
		case actPageUp, actPageDown, actPrevEntry, actNextEntry:
			d := map[hostAction]int{actPageUp: -1, actPageDown: 1, actPrevEntry: -1, actNextEntry: 1}[a]
			switch {
			case g.live.Map.Open() && (a == actPageUp || a == actPageDown):
				g.live.Map.TurnList(d)
			case g.live.Map.Open():
			case g.live.Guide.Open() && (a == actPageUp || a == actPageDown):
				g.live.Guide.TurnPage(d)
			case g.live.Guide.Open():
				g.live.Guide.NextChapter(d)
			case a == actPageUp || a == actPageDown:
				g.live.Journal.TurnPage(d)
			default:
				g.live.Journal.NextEntry(d)
			}
		}
	}
}

func (g *game) panelMode() panelMode {
	if g.chinese && (g.live.Guide.Open() || g.live.Map.Open()) {
		return panelBrowse // 攻略面板與手札翻閱同一組鍵（規格 008 §2.1）
	}
	switch j := g.live.Journal; {
	case !g.chinese || !j.Open():
		return panelNone
	case j.Browsing():
		return panelBrowse
	}
	return panelAuto
}

func (g *game) compose() []byte {
	return g.live.Compose(g.scale, g.chinese, func(r rune) {
		if !g.missing[r] {
			g.missing[r] = true
			fmt.Fprintf(os.Stderr, "sosb-play: 字型缺字 %q（U+%04X）\n", r, r)
		}
	})
}

func (g *game) screenshot() {
	rgba := g.compose()
	if rgba == nil {
		return
	}
	img := &image.NRGBA{Pix: rgba, Stride: 4 * 320 * g.scale, Rect: image.Rect(0, 0, 320*g.scale, 200*g.scale)}
	name := fmt.Sprintf("sosb-%s.png", time.Now().Format("20060102-150405.000"))
	if g.frames > 0 { // 自動模式：以畫格命名，收據重跑得到同名檔
		name = fmt.Sprintf("sosb-f%06d.png", g.frame)
	}
	err := os.MkdirAll(g.shotDir, 0o755)
	if err == nil {
		var f *os.File
		if f, err = os.Create(filepath.Join(g.shotDir, name)); err == nil {
			err = png.Encode(f, img)
			if cerr := f.Close(); err == nil {
				err = cerr
			}
		}
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, "sosb-play: 截圖失敗：", err)
	}
}

func (g *game) Update() error {
	g.frame++
	var u session.CapturedUpdate
	var acts []hostAction
	for _, a := range g.script[g.frame] {
		if a.bar {
			g.bar.forced, g.bar.shown = true, true
		} else if a.toggle {
			acts = append(acts, actToggle)
		} else if a.lang {
			acts = append(acts, actLang)
		} else if a.cheat {
			acts = append(acts, actCheat)
		} else if a.speed != 0 {
			g.setSpeed(a.speed)
		} else if a.size != 0 {
			g.setBarSize(barSize(a.size - 1))
		} else if a.act != 0 {
			acts = append(acts, a.act)
		} else if a.key != nil {
			u.BIOSKeys = append(u.BIOSKeys, *a.key)
		}
	}
	if g.frames == 0 {
		acts = append(acts, g.hostInput(&u)...)
	}
	g.apply(acts)
	if len(u.BIOSKeys) > 0 && g.live.Demo.Running() {
		// demo 中的按鍵不送進遊戲，改為中止 demo 回選單（主專案規格 018 §3.2）
		g.live.Demo.RequestAbort()
		u.BIOSKeys = nil
	}
	g.registerDelay()
	// 1x 一次推進整格；大於 1x 時分段推進，互動模式超過單格上限就不再跑下一段（主專案規格 019 §3.2）
	start, capped, stopped := time.Now(), false, false
	for remaining := g.budget; remaining > 0; {
		n := remaining
		if g.speed.set > 1 && n > g.chunk {
			n = g.chunk
		}
		view, err := g.owner.View()
		if err != nil {
			return err
		}
		u.StartedPanel, u.Layout, u.SourceGeneration = view.Panel, view.Layout, view.SourceGeneration
		if _, err := g.owner.Deliver(u); err != nil {
			return err
		}
		u = session.CapturedUpdate{}
		tick, err := g.owner.Advance(session.InstructionBudget(n))
		if err != nil {
			return err
		}
		g.lastSteps, g.accelSteps = tick.MachineStepsAfter, g.accelSteps+tick.Accelerated
		g.samples = g.mix.Render(g.samples[:0], tick.MachineStepsBefore, tick.MachineStepsAfter)
		g.music.Mix(g.samples)
		if g.ring != nil {
			g.ring.Push(g.samples)
		}
		if tick.Phase == session.PhaseStopped {
			stopped = true
			break
		}
		if tick.Steps < n {
			break
		}
		remaining -= n
		if remaining > 0 && g.speed.adaptive && time.Since(start) > speedFrameCap {
			capped = true
			break
		}
	}
	if g.perf.on {
		g.perf.adv = append(g.perf.adv, time.Since(start))
		g.perf.pctSum, g.perf.pcN = g.perf.pctSum+g.owner.ClockPercent(), g.perf.pcN+1
	}
	if stopped {
		return ebiten.Termination
	}
	if p := g.speed.observe(time.Since(start), capped); p != g.owner.ClockPercent() {
		if err := g.applyClock(p); err != nil {
			return err
		}
	}
	if g.frames > 0 && g.chinese {
		g.live.AuditFlash(g.frame, g.scale)
	}
	if g.frames > 0 && g.frame >= g.frames {
		return g.finish()
	}
	return nil
}

// flashWindow、flashListed：閃現量尺的窗（畫格）與結束時列出的行數（主專案規格 021 §2、§3）。
const flashWindow, flashListed = 8, 60

func (g *game) finish() error {
	write := func(path string, overlay bool) error {
		if path == "" {
			return nil
		}
		rgba := g.live.Compose(g.scale, overlay, nil)
		if rgba == nil {
			return errors.New("尚無畫格可截圖")
		}
		g.drawBar(rgba) // 腳本動作 bar 時含切換列（規格 011 §3 第 3 項）
		return os.WriteFile(path, rgba, 0o600)
	}
	if err := write(g.shot, true); err != nil {
		return err
	}
	if err := write(g.shotOrig, false); err != nil {
		return err
	}
	g.perf.report(g.speed.base)
	if a := g.live.Flash; a != nil {
		fmt.Fprintf(os.Stderr, "sosb-play: 閃現 %d 次\n", a.Count())
		// 同一對畫格、同一列的格子併成一行：第 a 格原樣呈現、第 b 格被換，列 y 的欄位
		lines, ev := 0, a.Events()
		for i := 0; i < len(ev) && lines < flashListed; lines++ {
			j, cols := i, ""
			for ; j < len(ev) && ev[j].Shown == ev[i].Shown && ev[j].Frame == ev[i].Frame && ev[j].CY == ev[i].CY; j++ {
				cols += fmt.Sprintf(" %d", ev[j].CX)
			}
			fmt.Fprintf(os.Stderr, "sosb-play: 閃現 第 %d 格原樣呈現、第 %d 格被換 列 %d 欄%s\n", ev[i].Shown, ev[i].Frame, ev[i].CY, cols)
			i = j
		}
	}
	fmt.Fprintf(os.Stderr, "sosb-play: CPU 速度 設定 %dx、時脈 %d%%、TP Delay 登記 %v、快轉 %d 步\n",
		g.speed.set, g.owner.ClockPercent(), g.tpRegistered && g.speed.ready, g.accelSteps)
	if d := g.live.Demo; d != nil {
		fmt.Fprintf(os.Stderr, "sosb-play: demo 控制 逾時寫入擋下 %d 次、中止 %d 次、中止後返回 %d 次（最近 %d 步）、執行中 %v、錯誤 %v\n",
			d.TimeoutsCleared, d.Aborts, d.AbortReturns, d.LastAbortSteps, d.Running(), d.Err)
	} else if g.live.DemoErr != nil {
		fmt.Fprintln(os.Stderr, "sosb-play:", g.live.DemoErr)
	}
	if g.live.BindErr != nil {
		fmt.Fprintln(os.Stderr, "sosb-play:", g.live.BindErr)
	} else {
		fmt.Fprintf(os.Stderr, "sosb-play: 攔截點綁定於 #%d：A %05X（%d 次）C %05X\n", g.live.BoundAt, g.live.A.Entry, len(g.live.A.Hits), g.live.C.Entry)
		if g.live.B != nil {
			fmt.Fprintf(os.Stderr, "sosb-play: B %05X（%d 次）\n", g.live.B.Entry, len(g.live.B.Hits))
		}
		tally := func(name string, hs []sosb.Hit) {
			c := map[string]int{}
			for _, h := range hs {
				r := h.Rejected
				if r == "" {
					r = "覆繪"
				}
				c[r]++
			}
			fmt.Fprintf(os.Stderr, "sosb-play: %s %v\n", name, c)
		}
		tally("A", g.live.A.Hits)
		if g.live.B != nil {
			tally("B", g.live.B.Hits)
		}
		fmt.Fprintf(os.Stderr, "sosb-play: Layer stamps=%d\n", len(g.live.Layer.Stamps))
	}
	if g.cheat.On {
		fmt.Fprintf(os.Stderr, "sosb-play: 無敵 還原 %d 次、移除有害效果 %d 筆；隊伍 %s\n", g.cheat.Restored, g.cheat.Removed, g.cheat.Report)
	}
	if d, err := g.owner.Digest(); err == nil {
		fmt.Fprintf(os.Stderr, "sosb-play: frames=%d steps=%d memory_sha256=%x indexed_sha256=%x\n", g.frame, d.Steps, d.MemorySHA256, d.IndexedSHA256)
	}
	return ebiten.Termination
}

func (g *game) toolbarItems() []toolbarItem {
	return toolbarItems(g.barText, toolbarState{scale: g.scale, hasHD: g.live.HDItems > 0, chinese: g.chinese, muted: g.muted,
		hasMusic: g.music != nil, music: g.music.Enabled(),
		fullscreen: ebiten.IsFullscreen(), answers: !g.live.HideAnswers(),
		journal: g.live.Journal.Browsing(), guide: g.live.Guide.Open(), mapOpen: g.live.Map.Open(), langs: len(g.langs),
		cheat: g.cheat.On, noJournal: g.live.Journal == nil, noGuide: g.live.Guide == nil,
		speed: g.speed.label(), size: g.barText[barSizeKeys[g.barSize]]})
}

// drawBar 在切換列顯示時把它疊到 rgba 上（截圖 F10 不含切換列）。
func (g *game) drawBar(rgba []byte) {
	if rgba == nil || !g.bar.shown {
		return
	}
	if g.perf.on {
		defer func(t time.Time) { g.perf.draw = append(g.perf.draw, time.Since(t)) }(time.Now())
	}
	items := g.toolbarItems()
	missing := func(r rune) {
		if !g.missing[r] {
			g.missing[r] = true
			fmt.Fprintf(os.Stderr, "sosb-play: 字型缺字 %q（U+%04X）\n", r, r)
		}
	}
	glyph, _ := g.barGlyphs()
	drawToolbar(rgba, g.scale, glyph, items, toolbarHit(items, g.cursorX, g.cursorY), missing)
	if g.bar.speeds {
		menu := speedMenu(g.speed.set, g.speed.actual(), items)
		drawDropMenu(rgba, g.scale, glyph, menu, dropMenuHit(menu, g.cursorX, g.cursorY), missing)
	}
	if g.bar.sizes {
		menu := barFontMenu(g.barText, g.barSize, items)
		drawDropMenu(rgba, g.scale, glyph, menu, dropMenuHit(menu, g.cursorX, g.cursorY), missing)
	}
}

func (g *game) Draw(screen *ebiten.Image) {
	rgba := g.compose()
	g.drawBar(rgba)
	if b := screen.Bounds(); rgba != nil && len(rgba) == 4*b.Dx()*b.Dy() {
		screen.WritePixels(rgba)
	}
}

func (g *game) Layout(_, _ int) (int, int) { return 320 * g.scale, 200 * g.scale }

// fail 是致命錯誤：stderr、錯誤紀錄（發行模式）與 Windows 對話框（launcher.go）。
func fail(err error) { fatal(err) }

func main() {
	original := flag.String("original", "", "唯讀原版目錄（含 START.EXE）")
	save := flag.String("save", "", "可寫存檔目錄：不存在或為空時由原版複製；已有 START.EXE（雜湊相符）則沿用，存檔保留")
	textDir := flag.String("text-dir", "", "譯文目錄（ui-text-*、ecl-text-* TSV）")
	journalMaps := flag.String("journal-maps", "", "手札地圖頁目錄（NN-K.png，主專案規格 022）；不指定時地圖則只顯示正文")
	fontPath := flag.String("font", "", "16×16 GOLEMFNT")
	frames := flag.Int("frames", 0, "自動模式：跑這麼多畫格後結束（0＝互動）")
	script := flag.String("script", "", "自動模式腳本：畫格:動作[,…]（鍵名、單一字元、toggle）")
	shot := flag.String("shot", "", "自動模式結束時輸出中文合成 RGBA")
	shotOrig := flag.String("shot-original", "", "自動模式結束時輸出原版合成 RGBA")
	shotDir := flag.String("shot-dir", "", "F10 截圖目錄（預設存檔目錄旁的 screenshots）")
	clock := flag.Int("clock", 50, "機器時脈比例 10–100")
	speedFlag := flag.Int("speed", 0, "CPU 模擬速度倍率 1、2、4、8、16、32（主專案規格 019）；0 表示讀取前端偏好，自動模式為 1")
	delayAccel := flag.Bool("delay-accel", true, "登記 Turbo Pascal Delay 精確快轉（dosgolem 規格 429）；關閉只供等價性對照")
	perfFlag := flag.Bool("perf", false, "自動模式結束時印每格模擬與繪製耗時、畫出 fps（主專案規格 019 §4）")
	flashFlag := flag.Bool("flash-audit", false, "自動模式每畫格量測閃現：原版內容先原樣呈現、之後才被疊字或 HD 換掉（主專案規格 021）")
	adaptiveFlag := flag.Bool("speed-adaptive", false, "自動模式也調節實際倍率（只供量測，結果不可重播）")
	barFontFlag := flag.Int("barfont", 0, "切換列字級 1 小、2 中、3 大（主專案規格 020）；0 表示讀取前端偏好，自動模式為中")
	adlib := flag.Bool("adlib", true, "模擬 AdLib")
	audioOn := flag.Bool("audio", true, "互動模式播放聲音（容器內沒有音訊裝置時關閉）")
	hideAnswers := flag.Bool("hide-answers", false, "開機時隱藏查驗題答案（F9 切換）")
	original0 := flag.Bool("original-view", false, "開機時顯示原版（F12 切換）")
	invPath := flag.String("inventory", "", "結束時把印字路徑盤點（issue #11）寫成這個 TSV；含原文，只放工作區")
	scaleFlag := flag.Int("scale", 2, "起始倍率（2 或 3；F2 切換）")
	musicDir := flag.String("music-dir", "", "配樂目錄（music.tsv 與 <曲目>.opl；主專案規格 014）；選曲表讀 text-dir 的 music-cues.tsv")
	noMusic := flag.Bool("no-music", false, "開機時配樂關閉（切換列或 F4 可再打開）")
	langFlag := flag.String("lang", "", "起始語言代碼（主專案規格 015；預設為上次的選擇或 zh-TW）")
	langFonts := flag.String("lang-fonts", "", "繁中以外語言的字型：代碼=路徑，逗號分隔（發行模式另找 font/sosb-<代碼>.golemfnt）")
	cheatOn := flag.Bool("cheat", false, "開機時開啟我方無敵（主專案規格 017；F1 或切換列切換）")
	hdDir := flag.String("hd", "", "HD 主題目錄（theme.json；主專案規格 010，只在 3× 顯示）")
	showVersion := flag.Bool("version", false, "印版號與 dosgolem commit 後結束")
	flag.Parse()
	if *speedFlag != 0 && !validSpeed(*speedFlag) {
		fail(fmt.Errorf("-speed 須為 1、2、4、8、16、32"))
	}
	if *barFontFlag < 0 || *barFontFlag > 3 {
		fail(fmt.Errorf("-barfont 須為 1、2、3"))
	}
	if *showVersion {
		fmt.Print(versionString())
		return
	}
	// 沒給 -save 是發行模式（主專案規格 012 §3.1）：資料從發行包找，原版第一次匯入到使用者資料目錄的 game/。
	release := *save == ""
	stateDir := *save // 手札已讀、地圖走過、攻略位置等前端檔的目錄
	var gameDir, startName string
	if release {
		data, err := userDataDir()
		if err != nil {
			fail(err)
		}
		logDir, stateDir = data, data
		if *textDir == "" {
			if *textDir, err = resourcePath("text"); err != nil {
				fail(err)
			}
		}
		if *fontPath == "" {
			if *fontPath, err = releaseFont(); err != nil {
				fail(err)
			}
		}
		if *hdDir == "" {
			*hdDir = releaseHD()
		}
		if *musicDir == "" {
			*musicDir = releaseMusic()
		}
		if gameDir, startName, err = prepareGame(*original, data); err != nil {
			fail(err)
		}
	} else if *original == "" || *textDir == "" || *fontPath == "" {
		flag.Usage()
		os.Exit(2)
	}
	if *clock < 10 || *clock > 100 {
		fail(fmt.Errorf("-clock 須在 10–100"))
	}
	if *scaleFlag != 2 && *scaleFlag != 3 {
		fail(fmt.Errorf("-scale 須為 2 或 3"))
	}
	font, err := sosb.LoadFontScaled(*fontPath)
	if err != nil {
		fail(err)
	}
	ui, ecl, err := sosb.LoadTextDir(*textDir)
	if err != nil {
		fail(err)
	}
	keys, err := parseScript(*script)
	if err != nil {
		fail(err)
	}
	sum, _ := hex.DecodeString(startEXESHA256)
	var want [32]byte
	copy(want[:], sum)
	saveRoot := *save
	if release {
		saveRoot = gameDir
	} else if _, err := os.Stat(filepath.Join(saveRoot, "START.EXE")); err != nil {
		startName = "START.EXE"
		out, err := bootroot.Prepare(bootroot.BootRootInput{OriginalRoot: *original, SaveRoot: *save,
			Required: []bootroot.RequiredFile{{Name: "START.EXE", SHA256: want}}})
		if err != nil {
			fail(err)
		}
		saveRoot = out.SaveRoot
	}
	if startName == "" {
		startName = "START.EXE"
	}
	if err := installSoSB(saveRoot); err != nil {
		fail(err)
	}
	exe, err := os.ReadFile(filepath.Join(saveRoot, startName))
	if err != nil {
		fail(err)
	}
	if got := sha256.Sum256(exe); got != want {
		fail(errors.New("START.EXE 雜湊不符"))
	}
	live := sosb.NewLive(font, ui, ecl)
	if *hdDir != "" {
		if err := live.AddHD(*hdDir); err != nil {
			fail(err)
		}
	}
	live.Inventory = *invPath != ""
	live.ControlDemo = true
	if *flashFlag && *frames > 0 {
		live.Flash = xlate.NewFlashAudit(320, 200, flashWindow)
	}
	if live.Answers, live.QuizFormat, err = sosb.LoadQuizDir(*textDir); err != nil {
		fail(err)
	}
	live.SetHideAnswers(*hideAnswers)
	hostText, err := os.ReadFile(filepath.Join(*textDir, "host-text.zh-TW.tsv"))
	if err != nil {
		fail(err)
	}
	barText, err := sosb.LoadHostText(hostText)
	if err != nil {
		fail(err)
	}
	if err := checkToolbarText(barText); err != nil {
		fail(err)
	}
	if live.Journal, err = sosb.LoadJournalDir(*textDir); err != nil {
		fail(err)
	}
	if *journalMaps != "" {
		if live.Journal.Maps, err = sosb.LoadJournalMaps(*journalMaps); err != nil {
			fail(err)
		}
	}
	if live.Guide, err = sosb.LoadGuideDir(*textDir); err != nil {
		fail(err)
	}
	if live.Guide != nil {
		posPath := filepath.Join(stateDir, "sosb-walkthrough-pos.txt")
		ch, page, err := sosb.ReadGuidePos(posPath)
		if err != nil {
			fail(err)
		}
		if ch != 0 || page != 0 {
			live.Guide.SetPos(ch, page)
		}
		live.Guide.OnMove = func(ch, page int) {
			if err := sosb.WriteGuidePos(posPath, ch, page); err != nil {
				fmt.Fprintln(os.Stderr, "sosb-play: 攻略位置寫入失敗：", err)
			}
		}
	}
	if live.Map, err = sosb.LoadAutoMapDir(*textDir); err != nil {
		fail(err)
	}
	if cues, err := os.ReadFile(filepath.Join(*textDir, "music-cues.tsv")); err == nil {
		if live.Music, err = sosb.LoadMusicCues(cues); err != nil {
			fail(err)
		}
	} else if !os.IsNotExist(err) {
		fail(err)
	}
	if live.Map != nil {
		visitedPath := filepath.Join(stateDir, "sosb-map-visited.txt")
		v, err := sosb.ReadVisited(visitedPath)
		if err != nil {
			fail(err)
		}
		live.Map.SetVisited(v)
		live.Map.OnVisit = func(key string, x, y int) {
			if err := sosb.AppendVisited(visitedPath, key, x, y); err != nil {
				fmt.Fprintln(os.Stderr, "sosb-play: 地圖走過格子寫入失敗：", err)
			}
		}
	}
	seenPath := filepath.Join(stateDir, "sosb-journal-seen.txt")
	if live.Journal.Seen, err = sosb.ReadJournalSeen(seenPath); err != nil {
		fail(err)
	}
	live.Journal.OnSeen = func(n int) {
		if err := sosb.AppendJournalSeen(seenPath, n); err != nil {
			fmt.Fprintln(os.Stderr, "sosb-play: 已讀手札寫入失敗：", err)
		}
	}
	s := host.OutputScale2
	layout := host.MouseLayout{Epoch: 1, Scale: s, ChromeHeight: 18 * int(s), Canvas: host.Canvas{Width: 320, Height: 200},
		FrameWidth: 320 * int(s), FrameHeight: 18*int(s) + 200*int(s)}
	budget := stepsPerHostFrame(*clock)
	fontsByLang, err := parseLangFonts(*langFonts)
	if err != nil {
		fail(err)
	}
	langs, err := loadLangs(*textDir, font, fontsByLang, release)
	if err != nil {
		fail(err)
	}
	langIdx, err := pickLang(langs, *langFlag, stateDir)
	if err != nil {
		fail(err)
	}
	live.SetLang(langs[langIdx])
	barText = langs[langIdx].Host
	if len(langs) > 1 {
		hostKeysReserved["F8"] = actLang
	}
	mix := mixer.New(budget * 60)
	cheat := &sosb.Invincible{On: *cheatOn}
	owner, err := session.New(session.Config{InitialScale: s, InitialLayout: layout, AdLib: *adlib, ClockPercent: *clock,
		Observer: observer{live: live, mix: mix, cheat: cheat}})
	if err != nil {
		fail(err)
	}
	defer owner.Close()
	if _, err := owner.BootOriginal(session.BootInput{EXE: exe, ExpectedEXESHA256: want, SaveRoot: saveRoot}); err != nil {
		fail(err)
	}
	dir := *shotDir
	if dir == "" {
		dir = filepath.Join(filepath.Dir(filepath.Clean(saveRoot)), "screenshots")
	}
	g := &game{owner: owner, live: live, scale: *scaleFlag, chinese: !*original0, frames: *frames, script: keys, shot: *shot, shotOrig: *shotOrig,
		shotDir: dir, budget: budget, mix: mix, focused: true, missing: map[rune]bool{}, barText: barText,
		langs: langs, lang: langIdx, langDir: stateDir, mainFont: font, cheat: cheat,
		chunk: budget, delayAccel: *delayAccel, speedPath: filepath.Join(stateDir, "sosb-speed.txt"),
		barSizePath: filepath.Join(stateDir, "sosb-barfont.txt"), barSize: barMedium}
	g.speed = speedControl{base: *clock, set: 1, pct: *clock, adaptive: *frames == 0 || *adaptiveFlag}
	g.perf = perfStats{on: *perfFlag, start: time.Now()}
	switch {
	case *speedFlag != 0:
		g.speed.set = *speedFlag
	case *frames == 0:
		g.speed.set = readSpeed(g.speedPath)
	}
	switch {
	case *barFontFlag != 0:
		g.barSize = barSize(*barFontFlag - 1)
	case *frames == 0:
		g.barSize = readBarSize(g.barSizePath)
	}
	if g.barFonts, err = loadBarFonts(font, *fontPath); err != nil {
		fail(err)
	}
	if *musicDir != "" {
		if g.music, err = bgm.Load(*musicDir, live.Music); err != nil {
			fail(err)
		}
		if *noMusic {
			g.music.Toggle()
		}
	}
	if *frames == 0 && *audioOn {
		g.ring = mixer.NewRing(200)
		player, err := audio.NewContext(mixer.SampleRate).NewPlayerF32(g.ring)
		if err != nil {
			fail(err)
		}
		player.SetBufferSize(50 * time.Millisecond)
		player.Play()
		g.player = player
	}
	ebiten.SetWindowTitle(windowTitle)
	ebiten.SetWindowSize(320*g.scale, 200*g.scale)
	ebiten.SetTPS(60)
	clearErrorLog()
	err = ebiten.RunGame(g)
	if live.Inv != nil {
		ovrName, _ := findFold(saveRoot, "GAME.OVR")
		ovr, _ := os.ReadFile(filepath.Join(saveRoot, ovrName))
		if werr := live.Inv.WriteTSV(*invPath, ovr); werr != nil {
			fmt.Fprintln(os.Stderr, "sosb-play: 盤點寫入失敗：", werr)
		} else {
			fmt.Fprintf(os.Stderr, "sosb-play: 盤點 %d 筆寫到 %s\n", len(live.Inv.Events), *invPath)
		}
	}
	if err != nil {
		fail(err)
	}
}
