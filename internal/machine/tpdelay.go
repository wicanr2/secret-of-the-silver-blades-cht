package machine

import "github.com/wicanr2/dosgolem/internal/cpu"

// Turbo Pascal CRT 的 DelayLoop（`docs/spec/429` §2.2）有兩種寫法：
//
//	TP7：mov bx,4 / dec bx / jnz $-1 / cmp al,es:[di] / loope DelayLoop / ret      每圈 11 道指令，結束時 BX＝0
//	TP5：cmp al,es:[di] / jne done / loop DelayLoop / done: ret                     每圈 3 道指令，不動 BX
//
// 兩者都只讀 ES:DI。Delay 以開機校準的 DelayCnt 圈數等待，等待時主機把時間全花在這裡；
// 在下一個事件前把整圈快轉，結果與逐條執行相同。登記時依 loop 位址上的位元組判斷寫法。
type tpDelayForm struct {
	code    []byte
	perLoop uint64
	clearBX bool
}

var tpDelayForms = []tpDelayForm{
	{code: []byte{0xBB, 0x04, 0x00, 0x4B, 0x75, 0xFD, 0x26, 0x3A, 0x05, 0xE1, 0xF5, 0xC3}, perLoop: 11, clearBX: true},
	{code: []byte{0x26, 0x3A, 0x05, 0x75, 0x02, 0xE2, 0xF9, 0xC3}, perLoop: 3},
}

type tpDelay struct {
	loop, count uint32       // DelayLoop 與 DelayCnt 的線性位址；loop 為 0 表示未登記
	form        *tpDelayForm // 登記時依 loop 上的位元組判斷；兩種都不符時為 nil，不快轉
	baseCount   uint16       // 登記時的 DelayCnt
	basePct     int          // 登記時的時脈比例
	lastSteps   uint64       // 上一次抵達 loop 的 Steps 與 Cycles
	lastCycles  uint64
	cycPerLoop  uint64 // 實測一圈的週期數；0 表示還沒量到
}

// SetTPDelay 登記 DelayLoop 與 DelayCnt 的線性位址；loop 為 0 時取消。
func (m *Machine) SetTPDelay(loop, count uint32) {
	if loop == 0 {
		m.tpd = tpDelay{}
		return
	}
	m.tpd = tpDelay{loop: loop, count: count, baseCount: m.Peek16(count), basePct: m.ClockPercent()}
	for i := range tpDelayForms {
		f := &tpDelayForms[i]
		match := true
		for j, b := range f.code {
			if m.Peek8(loop+uint32(j)) != b {
				match = false
				break
			}
		}
		if match {
			m.tpd.form = f
			break
		}
	}
}

// rescaleTPDelay 依登記值與目前比例重算 DelayCnt。
func (m *Machine) rescaleTPDelay() {
	if m.tpd.loop == 0 || m.tpd.basePct == 0 {
		return
	}
	n := (uint64(m.tpd.baseCount)*uint64(m.ClockPercent()) + uint64(m.tpd.basePct)/2) / uint64(m.tpd.basePct)
	if n < 1 {
		n = 1
	}
	if n > 0xFFFF {
		n = 0xFFFF
	}
	m.Write16(m.tpd.count, uint16(n))
}

// accelTPDelay 在 Step 執行指令前呼叫；CS:IP 在 DelayLoop 開頭且條件成立時，
// 一次完成 k 圈並回每圈步數×k，否則回 0。
func (m *Machine) accelTPDelay() uint64 {
	c := m.CPU
	at := cpu.Addr(c.Seg[cpu.CS], c.IP)
	f := m.tpd.form
	if at != m.tpd.loop || f == nil {
		return 0
	}
	steps, cycles := m.Steps, c.Cycles
	known := m.tpd.cycPerLoop
	if m.tpd.lastSteps != 0 && steps-m.tpd.lastSteps == f.perLoop {
		known = cycles - m.tpd.lastCycles
		m.tpd.cycPerLoop = known
	}
	m.tpd.lastSteps, m.tpd.lastCycles = steps, cycles
	if known == 0 || m.RunLimit <= steps || m.CycleClock || len(m.cbQueue) > 0 || m.periodic.on ||
		len(m.timedKeys) > 0 || len(m.breaks) > 0 || m.onRead != nil || m.TraceSegs || m.WatchDSOn || m.Coverage != nil {
		return 0
	}
	cx := uint64(c.R[cpu.CX])
	if cx < 2 || m.Peek8(cpu.Addr(c.Seg[cpu.ES], c.R[cpu.DI])) != uint8(c.R[cpu.AX]) {
		return 0
	}
	for i, b := range f.code {
		if m.Peek8(at+uint32(i)) != b {
			return 0
		}
	}
	end := m.RunLimit
	if m.IRQ0Every > 0 && m.nextIRQ0 < end {
		end = m.nextIRQ0
	}
	if m.VGAFrameEvery > 0 && m.nextFrame < end {
		end = m.nextFrame
	}
	if len(m.keyQueue) > 0 && m.nextKey < end {
		end = m.nextKey
	}
	if end <= steps {
		return 0
	}
	k := (end - steps) / f.perLoop
	if k > cx-1 {
		k = cx - 1
	}
	if k == 0 {
		return 0
	}
	n := k * f.perLoop
	c.R[cpu.CX] -= uint16(k)
	if f.clearBX {
		c.R[cpu.BX] = 0
	}
	// cmp al,al：ZF、PF 為 1，CF、SF、OF、AF 為 0
	c.Flags = c.Flags&^(cpu.CF|cpu.SF|cpu.OF|cpu.AF) | cpu.ZF | cpu.PF
	m.Steps += n
	c.Cycles += known * k
	m.tpd.lastSteps, m.tpd.lastCycles = 0, 0
	m.DelayAccelerated += n
	return n
}
