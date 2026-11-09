"""Comprueba contratos de la rúbrica en YAML renderizado; no necesita un clúster."""
from pathlib import Path
import sys
import yaml

root = Path(__file__).resolve().parents[1]
for filename, tickets_replicas in (("app.yaml", 1), ("scale3.yaml", 3), ("rolling.yaml", 1)):
    docs = list(yaml.safe_load_all((root/"k8s/rendered"/filename).read_text(encoding="utf-8")))
    deployments = {d["metadata"]["name"]: d for d in docs if d.get("kind") == "Deployment"}
    assert set(deployments) == {"postgres", "vehicles", "tickets", "frontend"}
    assert deployments["tickets"]["spec"]["replicas"] == tickets_replicas
    assert deployments["postgres"]["spec"]["replicas"] == 1
    assert deployments["postgres"]["spec"]["strategy"]["type"] == "Recreate"
    for name, d in deployments.items():
        assert d["metadata"]["namespace"] == "glitchtec"
        assert d["spec"]["selector"]["matchLabels"] == d["spec"]["template"]["metadata"]["labels"]
        for c in d["spec"]["template"]["spec"]["containers"]:
            assert "-docker.pkg.dev/" in c["image"] and "REPLACE" not in c["image"]
            assert all(probe in c for probe in ("startupProbe", "readinessProbe", "livenessProbe"))
            assert "requests" in c["resources"] and "limits" in c["resources"]
    services = {d["metadata"]["name"]: d for d in docs if d.get("kind") == "Service"}
    assert services["frontend"]["spec"]["type"] == "LoadBalancer"
    assert all(d["spec"].get("type", "ClusterIP") == "ClusterIP" for n,d in services.items() if n != "frontend")
    assert any(d.get("kind") == "PersistentVolumeClaim" for d in docs)
    assert any(d.get("kind") == "ConfigMap" for d in docs)
    print(f"OK {filename}: cuatro Deployments, imágenes AR, probes, recursos, DNS y PVC")
