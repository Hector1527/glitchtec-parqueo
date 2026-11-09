"""Renderiza YAML fuera del árbol de Git; no crea infraestructura ni aplica cambios."""
import argparse
from pathlib import Path
import re
import subprocess
import yaml

p = argparse.ArgumentParser()
p.add_argument("--registry", required=True, help="REGION-docker.pkg.dev/PROJECT/REPO")
p.add_argument("--tag", default="v1")
p.add_argument("--scale3", action="store_true")
p.add_argument("--rolling", action="store_true", help="Solo actualiza vehicles a --tag manteniendo la versión base")
args = p.parse_args()
if not re.fullmatch(r"[a-z0-9-]+-docker\.pkg\.dev/[a-z][a-z0-9-]+/[a-z0-9_-]+", args.registry):
    p.error("La ruta debe ser de Google Artifact Registry")
if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", args.tag):
    p.error("Etiqueta Docker inválida")
root = Path(__file__).resolve().parents[1]
overlay = root / ("k8s/overlays/scale3" if args.scale3 else "k8s/base")
text = subprocess.check_output(["kubectl", "kustomize", str(overlay)], encoding="utf-8")
docs = list(yaml.safe_load_all(text))
for doc in docs:
    if doc.get("kind") == "Deployment":
        name = doc["metadata"]["name"]
        for container in doc["spec"]["template"]["spec"]["containers"]:
            container["image"] = f"{args.registry}/{name}:{args.tag}"
        if name in ("vehicles", "tickets"):
            doc["spec"]["template"]["spec"]["containers"][0]["env"] = [{"name":"APP_VERSION", "value":args.tag}]
if args.rolling:
    previous = root / "k8s/rendered/app.yaml"
    if not previous.exists():
        p.error("Primero renderiza la versión base en app.yaml")
    old = list(yaml.safe_load_all(previous.read_text(encoding="utf-8")))
    new_vehicle = next(d for d in docs if d.get("kind")=="Deployment" and d["metadata"]["name"]=="vehicles")
    docs = [new_vehicle if d.get("kind")=="Deployment" and d["metadata"]["name"]=="vehicles" else d for d in old]
out = root / "k8s/rendered" / ("rolling.yaml" if args.rolling else "scale3.yaml" if args.scale3 else "app.yaml")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(yaml.safe_dump_all(docs, allow_unicode=True, sort_keys=False), encoding="utf-8")
print(out)
