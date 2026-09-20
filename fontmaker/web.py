"""Dependency-free local web interface for the Fontmaker MVP."""

import base64
import io
import json
import re
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from PIL import Image

from .font_export import export_ttf
from .image_pipeline import extract_ink, normalize_to_box
from .project import FontProject
from .sample_plan import describe_sample, minimal_sample_syllables

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"
STATIC = Path(__file__).resolve().parent / "static"


def _safe_project_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError("유효하지 않은 프로젝트 ID입니다.")
    return value


def _load_project(project_id: str) -> FontProject:
    folder = PROJECTS / _safe_project_id(project_id)
    data_path = folder / "project.json"
    if not data_path.exists():
        raise FileNotFoundError("프로젝트를 찾을 수 없습니다.")
    return FontProject(folder, json.loads(data_path.read_text(encoding="utf-8")))


class FontmakerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def _json(self, value: dict, status: int = HTTPStatus.OK) -> None:
        encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/samples":
            samples = minimal_sample_syllables()
            self._json(
                {
                    "count": len(samples),
                    "samples": [
                        {"syllable": syllable, "description": describe_sample(syllable)}
                        for syllable in samples
                    ],
                }
            )
            return
        if parsed.path == "/api/preview":
            try:
                query = parse_qs(parsed.query)
                project = _load_project(query["project"][0])
                image = project.render_text(query.get("text", ["가나다라마바사"])[0])
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                payload = buffer.getvalue()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (KeyError, ValueError, FileNotFoundError) as error:
                self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/export":
            try:
                project = _load_project(parse_qs(parsed.query)["project"][0])
                target = project.path / "exports" / "my-hangul-font.ttf"
                export_ttf(project, target)
                payload = target.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "font/ttf")
                self.send_header("Content-Disposition", 'attachment; filename="my-hangul-font.ttf"')
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (KeyError, ValueError, FileNotFoundError) as error:
                self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._body()
            if self.path == "/api/projects":
                name = str(body.get("name", "나의 한글 폰트")).strip() or "나의 한글 폰트"
                project_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
                project = FontProject.create(PROJECTS / project_id, name)
                self._json({"id": project_id, "name": project.data["name"]}, HTTPStatus.CREATED)
                return
            if self.path == "/api/components":
                project = _load_project(str(body["project"]))
                key = str(body["key"])
                encoded = str(body["image"]).split(",", 1)[-1]
                uploaded = Image.open(io.BytesIO(base64.b64decode(encoded)))
                ink, _ = extract_ink(uploaded)
                normalized, _ = normalize_to_box(ink, (64, 64), padding=6)
                project.save_component(key, normalized)
                self._json({"saved": key})
                return
            if self.path == "/api/syllables":
                project = _load_project(str(body["project"]))
                syllable = str(body["syllable"])
                encoded = str(body["image"]).split(",", 1)[-1]
                uploaded = Image.open(io.BytesIO(base64.b64decode(encoded)))
                saved = project.save_syllable(syllable, uploaded)
                self._json({"syllable": syllable, "saved": saved})
                return
            self._json({"error": "지원하지 않는 요청입니다."}, HTTPStatus.NOT_FOUND)
        except (KeyError, ValueError, OSError, json.JSONDecodeError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)


def run(port: int = 8000) -> None:
    PROJECTS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", port), FontmakerHandler)
    print(f"Fontmaker MVP: http://127.0.0.1:{port}")
    server.serve_forever()
