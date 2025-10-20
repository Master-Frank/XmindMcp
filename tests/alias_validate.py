import json
import os
from xmind_core_engine import create_mind_map, analyze_mind_map

# 使用 topics 别名的结构，验证归一化与引擎兼容
sample = [
    {
        "title": "Alias Root",
        "topics": [
            {"title": "Child1"},
            {"title": "Child2", "topics": [{"title": "Grandchild"}]}
        ]
    }
]

s = json.dumps(sample, ensure_ascii=False)
out_file = os.path.abspath(os.path.join("output", "Alias_Test.xmind"))

res = create_mind_map("Alias Test", s, out_file)
print("CREATE:", json.dumps(res, ensure_ascii=False))

if isinstance(res, dict) and res.get("status") == "success":
    ana = analyze_mind_map(out_file)
    print("ANALYZE:", json.dumps(ana, ensure_ascii=False))
else:
    print("Creation failed. Result:", json.dumps(res, ensure_ascii=False))