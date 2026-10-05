# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=2.28"]
# ///
"""Phân tích một video (file trong máy hoặc link YouTube) bằng Gemini, chế độ agentic.

AI không nuốt cả video mà tự quay lại xem đúng đoạn cần (processing: "agentic").
Mỗi video là một DỰ ÁN: đầu vào ở inputs/<dự án>/, mỗi lần phân tích là một thư mục trong outputs/<dự án>/.

    uv run --script phan_tich.py <link|file|inputs/<dự án>> --che-do tom-tat
    uv run --script phan_tich.py <...> --che-do tim --hoi "lúc nào xuất hiện logo?"
    uv run --script phan_tich.py <...> --che-do tom-tat --so-sanh   # chạy cả static để so token
    uv run --script phan_tich.py <...> --che-do tom-tat --thu       # chỉ in sẽ làm gì, không gọi API, không tạo gì
    uv run --script phan_tich.py --ds                               # liệt kê dự án

Đầu vào nhận ba dạng:
- link YouTube, hoặc file nằm ngoài inputs/ → tìm dự án đã có cùng nguồn, chưa có thì tạo inputs/<ts>_<slug>/nguon.md
- thư mục inputs/<dự án>/ → dùng video trong đó, không có thì lấy nguồn ghi trong nguon.md
- file nằm trong inputs/<dự án>/ → dự án đó

Chạy ở gốc workspace (thư mục có inputs/ và outputs/). Key: biến môi trường GEMINI_API_KEY, hoặc dòng
GEMINI_API_KEY=... trong .env ở gốc workspace. Không bao giờ in key.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

GOC = Path.cwd()
INPUTS = GOC / "inputs"
OUTPUTS = GOC / "outputs"
CHE_DO = Path(__file__).resolve().parents[1] / "references" / "che-do.md"
MODEL_MAC_DINH = "gemini-3.7-flash"
MODEL_AGENTIC = {"gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"}
DUOI_VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".mpeg", ".mpg", ".wmv", ".flv", ".3gp"}

YT = re.compile(r"(?:youtube\.com/(?:watch\?v=|shorts/|live/)|youtu\.be/)([\w-]{11})")
DONG_NGUON = re.compile(r"^- \*\*Nguồn:\*\* (.+)$", re.M)


def doc_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    env = GOC / ".env"
    if not key and env.is_file():
        for dong in env.read_text(encoding="utf-8").splitlines():
            if dong.strip().startswith("GEMINI_API_KEY="):
                key = dong.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("✗ Thiếu GEMINI_API_KEY. Lấy ở aistudio.google.com/apikey, rồi tạo file .env ở gốc workspace "
                 "có một dòng GEMINI_API_KEY=<key>, hoặc export trong terminal.")
    return key


def doc_che_do() -> dict[str, str]:
    """Mỗi mục '## <tên>' trong che-do.md là một chế độ, khối ```text``` bên dưới là prompt."""
    txt = CHE_DO.read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip()
            for m in re.finditer(r"^## (\S+).*?```text\n(.*?)```", txt, re.S | re.M)}


def slug_cua(nguon: str) -> str:
    m = YT.search(nguon)
    if m:
        return "yt-" + m.group(1)
    ten = Path(nguon).stem.lower()
    return re.sub(r"[^a-z0-9]+", "-", ten).strip("-")[:40] or "video"


def nguon_cua(du_an: Path) -> str | None:
    f = du_an / "nguon.md"
    m = DONG_NGUON.search(f.read_text(encoding="utf-8")) if f.is_file() else None
    return m.group(1).strip() if m else None


def video_trong(du_an: Path) -> Path | None:
    vids = sorted(p for p in du_an.iterdir() if p.suffix.lower() in DUOI_VIDEO)
    return vids[0] if vids else None


def trong_inputs(p: Path) -> Path | None:
    """Thư mục dự án chứa p, nếu p nằm trong inputs/."""
    try:
        rel = p.resolve().relative_to(INPUTS.resolve())
    except ValueError:
        return None
    return INPUTS / rel.parts[0] if rel.parts else None


def chot_du_an(dau_vao: str, thu: bool) -> tuple[Path, str, bool]:
    """→ (thư mục dự án, nguồn video: link hoặc đường dẫn file, có phải dự án mới không)."""
    p = Path(dau_vao).expanduser()
    if not YT.search(dau_vao):
        du_an = trong_inputs(p) if p.exists() else None
        if du_an and p.is_dir():
            v = video_trong(du_an)
            nguon = str(v) if v else nguon_cua(du_an)
            if not nguon:
                sys.exit(f"✗ {du_an.relative_to(GOC)}/ không có file video, nguon.md cũng không ghi nguồn")
            return du_an, nguon, False
        if du_an:
            return du_an, str(p.resolve()), False
        if not p.is_file():
            sys.exit(f"✗ Không thấy file: {p}")
        dau_vao = str(p.resolve())
    # link YouTube, hoặc file nằm ngoài inputs/: dự án nào đã ghi đúng nguồn này thì dùng lại
    if INPUTS.is_dir():
        for d in sorted(INPUTS.iterdir()):
            if d.is_dir() and nguon_cua(d) == dau_vao:
                return d, dau_vao, False
    du_an = INPUTS / f"{datetime.now():%Y%m%d_%H%M%S}_{slug_cua(dau_vao)}"
    if not thu:
        du_an.mkdir(parents=True)
        ghi_chu = ("Link YouTube, phải để Công khai." if YT.search(dau_vao)
                   else "File nằm ngoài workspace, không chép vào. Dời file đi thì sửa dòng Nguồn.")
        (du_an / "nguon.md").write_text(
            f"# {slug_cua(dau_vao)}\n\n- **Nguồn:** {dau_vao}\n- **Tạo:** {datetime.now():%Y-%m-%d %H:%M}\n"
            f"- **Ghi chú:** {ghi_chu}\n\n## Người dùng muốn gì\n\n(agent ghi lại yêu cầu ở đây)\n",
            encoding="utf-8")
    return du_an, dau_vao, True


def liet_ke() -> None:
    if not INPUTS.is_dir() or not any(INPUTS.iterdir()):
        print("Chưa có dự án nào trong inputs/.")
        return
    for d in sorted(p for p in INPUTS.iterdir() if p.is_dir()):
        lan = sorted(p.name for p in (OUTPUTS / d.name).glob("*") if p.is_dir()) if (OUTPUTS / d.name).is_dir() else []
        v = video_trong(d)
        print(f"{d.name}\n    nguồn: {v.name if v else nguon_cua(d)}\n    {len(lan)} lần phân tích"
              + (f": {', '.join(lan)}" if lan else ""))


def khoi_video(client, nguon: str, processing: str) -> tuple[dict, str]:
    if YT.search(nguon):
        return {"type": "video", "uri": nguon, "processing": processing}, "YouTube (phải để Công khai)"
    p = Path(nguon)
    if not p.is_file():
        sys.exit(f"✗ Không thấy file: {p}")
    mime = mimetypes.guess_type(p.name)[0] or "video/mp4"
    print(f"⬆ Tải {p.name} ({p.stat().st_size / 1e6:.1f} MB) lên Gemini Files API…", flush=True)
    f = client.files.upload(file=str(p))
    while f.state.name == "PROCESSING":
        time.sleep(3)
        f = client.files.get(name=f.name)
    if f.state.name != "ACTIVE":
        sys.exit(f"✗ Google xử lý file không xong: {f.state.name}")
    return {"type": "video", "uri": f.uri, "mime_type": f.mime_type or mime, "processing": processing}, \
        f"File máy · {p.name} · Files API (Google tự xoá sau 48 giờ)"


def goi(client, model: str, video: dict, prompt: str) -> dict:
    t0 = time.time()
    kq = client.interactions.create(model=model, input=[video, {"type": "text", "text": prompt}])
    u = kq.usage
    return {
        "text": kq.output_text or "",
        "giay": round(time.time() - t0, 1),
        "token_vao": getattr(u, "total_input_tokens", None) if u else None,
        "token_ra": getattr(u, "total_output_tokens", None) if u else None,
        "token_tong": getattr(u, "total_tokens", None) if u else None,
        # Mỗi processing_call là một lần AI tự quay lại lấy một đoạn video / transcript / audio
        "lan_xem_lai": sum(1 for s in (kq.steps or []) if getattr(s, "type", "") == "processing_call"),
        "id": kq.id,
    }


def main() -> None:
    cac_che_do = doc_che_do()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", nargs="?", help="link YouTube công khai, file video, hoặc thư mục inputs/<dự án>")
    ap.add_argument("--che-do", choices=sorted(cac_che_do), help="kiểu phân tích")
    ap.add_argument("--hoi", default="", help="câu hỏi / thứ cần tìm (bắt buộc với tim, dem, hoi)")
    ap.add_argument("--model", default=MODEL_MAC_DINH)
    ap.add_argument("--so-sanh", action="store_true", help="chạy thêm static để so token (tốn gấp đôi)")
    ap.add_argument("--thu", action="store_true", help="chỉ in sẽ làm gì, không gọi API, không tạo thư mục")
    ap.add_argument("--ds", action="store_true", help="liệt kê dự án trong inputs/ và số lần đã phân tích")
    a = ap.parse_args()

    if a.ds:
        return liet_ke()
    if not a.video or not a.che_do:
        ap.error("cần <video> và --che-do (hoặc --ds để liệt kê dự án)")

    prompt = cac_che_do[a.che_do]
    if "{hoi}" in prompt:
        if not a.hoi:
            sys.exit(f"✗ Chế độ {a.che_do} cần --hoi \"...\"")
        prompt = prompt.replace("{hoi}", a.hoi)
    elif a.hoi:
        prompt += f"\n\nYêu cầu thêm của người dùng: {a.hoi}"
    if a.model not in MODEL_AGENTIC:
        print(f"⚠ {a.model} không nằm trong danh sách model có agentic {sorted(MODEL_AGENTIC)}", flush=True)

    key = None if a.thu else doc_key()  # kiểm key trước, để thiếu key không bỏ lại dự án rỗng
    du_an, nguon, moi = chot_du_an(a.video, a.thu)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ra = OUTPUTS / du_an.name / f"{ts}_{a.che_do}"

    if a.thu:
        print(f"Dự án: inputs/{du_an.name}/ ({'sẽ tạo mới' if moi else 'đã có'})\nNguồn: {nguon}\n"
              f"Kết quả: outputs/{du_an.name}/{ts}_{a.che_do}/\nModel: {a.model} · processing: agentic"
              f"{' + static' if a.so_sanh else ''}\nChế độ: {a.che_do}\n--- prompt ---\n{prompt}")
        return

    from google import genai
    client = genai.Client(api_key=key)
    video, kieu_nguon = khoi_video(client, nguon, "agentic")

    print(f"▶ {a.model} · agentic · {a.che_do}…", flush=True)
    ag = goi(client, a.model, video, prompt)
    st = None
    if a.so_sanh:
        print("▶ chạy lại kiểu static để so…", flush=True)
        st = goi(client, a.model, {**video, "processing": "static"}, prompt)

    ra.mkdir(parents=True)
    (ra / "bao-cao.md").write_text(ag["text"].rstrip() + "\n", encoding="utf-8")
    dong = [
        f"# {a.che_do} · {du_an.name}", "",
        f"- **Dự án:** `inputs/{du_an.name}/`",
        f"- **Video:** {nguon}",
        f"- **Kiểu nguồn:** {kieu_nguon}",
        f"- **Model:** {a.model} · processing `agentic`",
        f"- **Chế độ:** `{a.che_do}`" + (f" · hỏi: {a.hoi}" if a.hoi else ""),
        f"- **Ngày chạy:** {datetime.now():%Y-%m-%d %H:%M}",
        "", "## Số đo", "",
        "| Kiểu | Token vào | Token ra | Tổng | Lần AI quay lại xem | Giây |",
        "|---|---:|---:|---:|---:|---:|",
        f"| agentic | {ag['token_vao']} | {ag['token_ra']} | {ag['token_tong']} | {ag['lan_xem_lai']} | {ag['giay']} |",
    ]
    if st:
        dong.append(f"| static | {st['token_vao']} | {st['token_ra']} | {st['token_tong']} | – | {st['giay']} |")
        if ag["token_vao"] and st["token_vao"]:
            dong += ["", f"Agentic dùng **{ag['token_vao'] / st['token_vao']:.0%}** token vào so với static."]
        (ra / "bao-cao-static.md").write_text(st["text"].rstrip() + "\n", encoding="utf-8")
    dong += ["", "Mốc thời gian trong `bao-cao.md` là của AI. Mốc nào đem đi dùng (cắt clip, trích) thì mở video kiểm lại."]
    (ra / "RUN.md").write_text("\n".join(dong) + "\n", encoding="utf-8")
    (ra / "so-do.json").write_text(json.dumps({"agentic": {k: v for k, v in ag.items() if k != "text"},
                                               "static": {k: v for k, v in st.items() if k != "text"} if st else None},
                                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {ra.relative_to(GOC)}/  · token vào {ag['token_vao']} · AI quay lại xem {ag['lan_xem_lai']} lần")


if __name__ == "__main__":
    main()
