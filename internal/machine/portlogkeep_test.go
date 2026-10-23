package machine

import "testing"

func TestPortLogKeep(t *testing.T) {
	m := New()
	for i := 0; i < 500; i++ {
		m.Out8(0x80, uint8(i))
	}
	if len(m.PortLog) != 500 {
		t.Fatalf("PortLogKeep 為 0（預設）時全留，得 %d 筆", len(m.PortLog))
	}
	m.PortLog, m.PortLogKeep = nil, 64
	for i := 0; i < 500; i++ {
		m.Out8(0x80, uint8(i))
		if len(m.PortLog) >= 128 {
			t.Fatalf("上限 64 時長度不該到 128，得 %d", len(m.PortLog))
		}
	}
	if last := m.PortLog[len(m.PortLog)-1]; last.Val != uint8(499%256) {
		t.Fatalf("最後一筆要是最新的寫入，得 %d", last.Val)
	}
}
