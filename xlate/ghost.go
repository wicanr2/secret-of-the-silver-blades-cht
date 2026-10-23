package xlate

// 殘影疊字（spec 202 §2.7）：某處原版墨跡與一筆疊字顯示時完全相同，那筆疊字的譯文就仍然適用，
// 不管呼叫端是否已經移除它。原版用還原顯存之類不經印字常式的方式把同一段原文放回來時，
// 譯文跟著回來，不會先露出一格原文。

// GhostKeep、GhostFrames 是殘影的數量上限與保留的 Frame 次數（spec 202 §2.7）。
const (
	GhostKeep   = 64
	GhostFrames = 600
)

// ghost 是一筆疊字與它最後一次 Frame 時底下的原版內容：逐格指紋與錨定格（有墨跡的格）。
type ghost struct {
	s       *Stamp
	hashes  []uint64
	anchors []bool
	age     int
	valid   bool
}

// snapshotGhost 記下 s 底下的原版內容；不能轉殘影時回 nil：圖面、尚未顯示、或沒有任何未透明的錨定格
// （整塊純色無從判斷原文是否回來）。Layer 管理的疊字用定色時的指紋與錨定格（spec 202 §2.3）；
// 呼叫端自行管理的（frozen）沒有那份紀錄，以這一幀的畫面記。
func snapshotGhost(s *Stamp, frozen bool, indexed []uint8, w, h int) *ghost {
	if s.Art || s.Hidden || s.Cells <= 0 || s.State != Shown { // 隱藏的不記殘影（spec 202 §2.10）
		return nil
	}
	g := &ghost{s: s, hashes: s.hashes, anchors: s.anchors}
	if frozen || len(s.hashes) != s.Cells || len(s.anchors) != s.Cells {
		if !frozen {
			return nil // 舊快照還原、格數變了：下一幀重新定色後再記
		}
		g.hashes, g.anchors = s.cellHashes(indexed, w, h), s.cellAnchors(indexed, w, h)
	}
	for i, a := range g.anchors {
		if a && !s.transparent(i) {
			return g
		}
	}
	return nil
}

// matches 回每個未透明錨定格的指紋是否都與記下時相同。
func (g *ghost) matches(indexed []uint8, w, h int) bool {
	for i, a := range g.anchors {
		if a && !g.s.transparent(i) && fnv(g.s.cellRegion(indexed, w, h, i)) != g.hashes[i] {
			return false
		}
	}
	return true
}

// removedSinceFrame 回上一次 Frame 時已顯示、之後被移除的疊字。
func (l *Layer) removedSinceFrame() []*ghost {
	if len(l.prevShown) == 0 {
		return nil
	}
	now := make(map[*Stamp]bool, len(l.Stamps))
	for _, s := range l.Stamps {
		now[s] = true
	}
	var out []*ghost
	for _, g := range l.prevShown {
		if !now[g.s] {
			out = append(out, g)
		}
	}
	return out
}

// frameGhosts 在 Frame 開頭呼叫：把上一幀之後被移除的疊字轉成殘影，再依這一幀的原版畫面判斷每個殘影是否有效。
func (l *Layer) frameGhosts(indexed []uint8, w, h int) {
	seen := make(map[*Stamp]bool, len(l.ghosts))
	for _, g := range l.ghosts {
		seen[g.s] = true
	}
	for _, g := range l.removedSinceFrame() {
		if !seen[g.s] { // 同一筆移除又加回、再移除：只留一個殘影
			l.ghosts = append(l.ghosts, g)
		}
	}
	if n := len(l.ghosts) - GhostKeep; n > 0 {
		l.ghosts = append(l.ghosts[:0], l.ghosts[n:]...)
	}
	keep := l.ghosts[:0]
	for _, g := range l.ghosts {
		if g.age++; g.age > GhostFrames {
			continue
		}
		g.valid = g.matches(indexed, w, h)
		keep = append(keep, g)
	}
	l.ghosts = keep
}

// rememberShown 在 Frame 結束時記下每筆顯示中的疊字與它底下的原版內容。
func (l *Layer) rememberShown(indexed []uint8, w, h int) {
	l.prevShown = l.prevShown[:0]
	for _, s := range l.Stamps {
		if g := snapshotGhost(s, l.Frozen != nil && l.Frozen(s), indexed, w, h); g != nil {
			l.prevShown = append(l.prevShown, g)
		}
	}
}

// ghostsToDraw 回 Draw 要先畫的疊字：上一次 Frame 之後被移除的（合成用的原版畫面就是那一幀，它們仍有效），
// 與這一幀有效、目前沒有加回的殘影。
func (l *Layer) ghostsToDraw() []*Stamp {
	var out []*Stamp
	for _, g := range l.removedSinceFrame() {
		out = append(out, g.s)
	}
	if len(l.ghosts) == 0 {
		return out
	}
	now := make(map[*Stamp]bool, len(l.Stamps))
	for _, s := range l.Stamps {
		now[s] = true
	}
	for _, g := range l.ghosts {
		if g.valid && !now[g.s] {
			out = append(out, g.s)
		}
	}
	return out
}

// ForgetGhosts 清除全部殘影與上一幀的集合（spec 202 §2.7）。換語言、切換答案顯示、視訊模式改變時呼叫：
// 同樣的原文這時應換成不同的呈現。
func (l *Layer) ForgetGhosts() {
	l.ghosts, l.prevShown = nil, nil
}
