from dataclasses import dataclass
from typing import Dict, Optional
import json
from pathlib import Path

MATRIX_PATH = Path(__file__).resolve().parents[1] / "config" / "services_matrix.json"

@dataclass
class EnvInfo:
    name: str
    base_url: str
    owner: Optional[str] = None

@dataclass
class ServiceInfo:
    name: str
    canonical: str
    secondary: Optional[str]
    endpoints: Dict[str, str]
    envs: Dict[str, EnvInfo]

def _load_matrix() -> dict:
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_service(name: str) -> ServiceInfo:
    m = _load_matrix()
    s = m["services"][name]
    envs = {
        env_name: EnvInfo(name=env_name, base_url=env["base_url"], owner=env.get("owner"))
        for env_name, env in s["environments"].items()
    }
    return ServiceInfo(
        name=name,
        canonical=s.get("canonical"),
        secondary=s.get("secondary"),
        endpoints=s["endpoints"],
        envs=envs
    )

def url(service: str, endpoint_key: str, prefer: str = "canonical") -> str:
    s = get_service(service)
    env_name = s.canonical if prefer == "canonical" else (s.secondary or s.canonical)
    base = s.envs[env_name].base_url
    ep = s.endpoints[endpoint_key]
    if not ep.startswith("/"):
        ep = "/" + ep
    return base + ep

def validate_contracts() -> Dict[str, Dict[str, str]]:
    report = {}
    m = _load_matrix()
    for svc_name, svc in m["services"].items():
        issues = []
        if not svc.get("canonical"):
            issues.append("missing_canonical")
        if "endpoints" not in svc:
            issues.append("missing_endpoints")
        else:
            for k, v in svc["endpoints"].items():
                if not v or not isinstance(v, str):
                    issues.append(f"invalid_endpoint:{k}")
        report[svc_name] = {"status": "ok" if not issues else "invalid", "issues": ", ".join(issues)}
    return report

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        print(url(sys.argv[1], sys.argv[2]))
    else:
        print(validate_contracts())
