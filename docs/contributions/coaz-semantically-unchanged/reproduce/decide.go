// Decision-level differential probe (axes 9/10/11/13/17).
// Usage: cd <register-checkout> && go run /path/to/decide.go [decisions.json]
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/varwof/register/semantics"
)

type dprobe struct {
	ID    string         `json:"id"`
	Grant map[string]any `json:"grant"`
	Op    map[string]any `json:"op"`
}

func params(m map[string]any) map[string]any {
	raw, _ := json.Marshal(m)
	dec := json.NewDecoder(strings.NewReader(string(raw)))
	dec.UseNumber()
	var out map[string]any
	_ = dec.Decode(&out)
	return out
}

func main() {
	cases := "decisions.json"
	if len(os.Args) > 1 {
		cases = os.Args[1]
	}
	raw, _ := os.ReadFile(cases)
	var probes []dprobe
	_ = json.Unmarshal(raw, &probes)
	out := []map[string]any{}
	for _, p := range probes {
		g := semantics.Grant{ID: p.Grant["id"].(string)}
		if ps, ok := p.Grant["params"]; ok && ps != nil {
			if mm, ok := ps.(map[string]any); ok {
				g.Params = params(mm)
			}
		}
		if cs, ok := p.Grant["constraints"].([]any); ok {
			for _, c := range cs {
				g.Constraints = append(g.Constraints, c.(string))
			}
		}
		op := semantics.Operation{ID: p.Op["id"].(string)}
		if ps, ok := p.Op["params"]; ok && ps != nil {
			if mm, ok := ps.(map[string]any); ok {
				op.Params = params(mm)
			}
		}
		d := semantics.Authorize(g, op)
		out = append(out, map[string]any{"id": p.ID, "lang": "go", "verdict": d.Verdict, "reason": d.Reason})
	}
	b, _ := json.Marshal(out)
	fmt.Println(string(b))
}
