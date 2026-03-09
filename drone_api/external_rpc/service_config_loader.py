import json
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def create_runtime_service_config(service_config_path: Path | str) -> Path:
    service_config_path = Path(service_config_path).resolve()
    service_config = json.loads(service_config_path.read_text())

    pdu_config_path = service_config.get("pdu_config_path")
    if pdu_config_path is None:
        raise RuntimeError(f"pdu_config_path is not set in {service_config_path}")

    pdu_path = Path(pdu_config_path)
    if not pdu_path.is_absolute():
        candidate_paths = [
            (service_config_path.parent / pdu_path).resolve(),
            (REPO_ROOT / pdu_path).resolve(),
        ]
        pdu_path = next((candidate for candidate in candidate_paths if candidate.exists()), candidate_paths[0])
    if not pdu_path.exists():
        raise RuntimeError(f"pdu_config_path does not exist: {pdu_path}")

    service_config["pdu_config_path"] = str(pdu_path)

    runtime_dir = Path(tempfile.gettempdir()) / "hakoniwa-drone-external-rpc"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    runtime_path = runtime_dir / service_config_path.name
    runtime_path.write_text(json.dumps(service_config, indent=2))
    return runtime_path
