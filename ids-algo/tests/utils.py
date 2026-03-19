from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json

BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "temp"
DEFAULT_INPUT_FILE = BASE_DIR / "temp" / "input.json"

def createMdInOutput(content:str, filename: str):
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename: test_name - timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    finalfilename = f"{filename}-{timestamp}.md"
    output_path = output_dir / finalfilename
    
    # Save markdown file
    output_path.write_text(content, encoding="utf-8")
    
    print(f"✅ Markdown documentation saved to: {output_path}")
    print(f"📄 File: {finalfilename}")

def to_jsonable(obj):
    """Recursively convert result classes to JSON-serializable dicts."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # list → list
    if isinstance(obj, list):
        return [to_jsonable(i) for i in obj]

    # dict → dict
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}

    # dataclass or any object with __dict__
    if hasattr(obj, "__dict__"):
        return {k: to_jsonable(v) for k, v in vars(obj).items()}

    # fallback
    return str(obj)


def to_json(obj, **kwargs):
    """Return a JSON string."""
    return json.dumps(to_jsonable(obj), ensure_ascii=False, **kwargs)


def createJsonTempFile(obj:object, filename: str):

    content = to_json(obj, indent=2)
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "temp"
    output_dir.mkdir(exist_ok=True)
    
    finalfilename = f"{filename}.json"
    output_path = output_dir / finalfilename
    
    # Save file
    output_path.write_text(content, encoding="utf-8")
    
    print(f"✅ Json temp file saved to: {output_path}")
    print(f"📄 File: {finalfilename}")


def load_input_entries(filename: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load structured parser inputs from the temp directory."""
    if filename:
        candidate = Path(filename.strip())
        if candidate.is_absolute():
            raise RuntimeError("Filename must be relative to the temp directory.")
        target = BASE_DIR / "temp" / candidate
    else:
        target = DEFAULT_INPUT_FILE

    try:
        raw_content = target.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Input file not found: {target}") from exc

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {target}: {exc}") from exc

    if not isinstance(data, list):
        raise RuntimeError(f"Expected a list of entries in {target}.")

    return data


def normalize_ifc_version(version_str: str) -> str:
    """标准化IFC版本字符串，移除非字母数字字符并转换为大写"""
    if not version_str:
        return ""
    # 只保留字母和数字，转换为大写
    return "".join(c for c in version_str if c.isalnum()).upper()