// Value-level differential probe (axis 5-13).
// Usage: cd <register-checkout> && go run /path/to/probe.go [cases.json]
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/varwof/register/semantics"
)

type probe struct {
	ID        string `json:"id"`
	Evaluated string `json:"evaluated"`
	Applied   string `json:"applied"`
}

func main() {
	cases := "probes.json"
	if len(os.Args) > 1 {
		cases = os.Args[1]
	}
	raw, err := os.ReadFile(cases)
	if err != nil {
		panic(err)
	}
	var probes []probe
	if err := json.Unmarshal(raw, &probes); err != nil {
		panic(err)
	}
	out := make([]map[string]any, 0, len(probes))
	for _, p := range probes {
		m := map[string]any{"id": p.ID, "lang": "go"}
		for _, side := range []struct{ text, rk, ck string }{
			{p.Evaluated, "raw_eval", "canon_eval"}, {p.Applied, "raw_app", "canon_app"}} {
			if err := semantics.ValidateRawParams(side.text); err != nil {
				m[side.rk] = strings.SplitN(err.Error(), ":", 2)[0]
			} else {
				m[side.rk] = "ok"
			}
			dec := json.NewDecoder(strings.NewReader(side.text))
			dec.UseNumber()
			var v any
			if err := dec.Decode(&v); err != nil {
				m[side.ck] = "ERR:decode"
				continue
			}
			if b, err := semantics.CanonicalJSON(v); err != nil {
				m[side.ck] = "ERR:" + strings.SplitN(err.Error(), ":", 2)[0]
			} else {
				m[side.ck] = string(b)
			}
		}
		m["same"] = m["canon_eval"] == m["canon_app"] && !strings.HasPrefix(fmt.Sprint(m["canon_eval"]), "ERR")
		out = append(out, m)
	}
	b, _ := json.Marshal(out)
	fmt.Println(string(b))
}
