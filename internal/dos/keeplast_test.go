package dos

import "testing"

func TestKeepLastBoundsLogs(t *testing.T) {
	var s []int
	for i := 0; i < 1000; i++ {
		s = append(s, i)
		s = keepLast(s, 100)
		if len(s) >= 200 {
			t.Fatalf("第 %d 筆後長度 %d，上限 100 時不該到 200", i, len(s))
		}
	}
	if s[len(s)-1] != 999 {
		t.Fatalf("最後一筆要是最新的，得 %d", s[len(s)-1])
	}
	var all []int
	for i := 0; i < 1000; i++ {
		all = keepLast(append(all, i), 0)
	}
	if len(all) != 1000 {
		t.Fatalf("LogKeep 為 0（預設）時全留，得 %d 筆", len(all))
	}
}
