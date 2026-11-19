#!/usr/bin/env python3
"""
SVG 科研图标检索、下载、命名空间清洗、改色与内联工具。

统一对接两大免鉴权开源图标源：
1. Iconify（通用工程/流程图图标）：聚合 Lucide (`lucide:`)、Phosphor (`ph:`)、
   Heroicons (`heroicons:`)、Tabler (`tabler:`) 等 30 万+ 矢量图标。
2. Bioicons（生命科学/生物医学图标）：覆盖 2,800+ 纯矢量 SVG（含 1,375 个
   Servier Medical Art 与 634 个 DBCLS 图标：细胞、亚细胞器、RNA/DNA、测序与实验仪器）。

CLI 用法：
  # 1) 同时检索通用图标与生物图标
  python scripts/fetch_icon.py search "database" --limit 8
  python scripts/fetch_icon.py search "rna" --source bioicons --limit 10

  # 2) 下载并清洗后保存独立 SVG（支持改色与线宽）
  python scripts/fetch_icon.py fetch lucide:database --color "#316F98" -o db.svg
  python scripts/fetch_icon.py fetch bioicons:dna-2 -o dna.svg

  # 3) 直接输出可嵌进主图的内联 <g> 片段（自动缩放对齐至 (x, y) 的 size×size 框内）
  python scripts/fetch_icon.py fetch lucide:filter --inline-g --x 12 --y 24 --size 14 --color "#303030"

Python 脚本内直接调用：
  from scripts.fetch_icon import inline_icon_g
  g_svg = inline_icon_g("lucide:database", x=10, y=18, size=14, color="#316F98")
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "bio-plot-icons"
BIOICONS_INDEX_URL = "https://bioicons.com/icons/icons.json"
BIOICONS_INDEX_CACHE = CACHE_DIR / "bioicons_index.json"
BIOICONS_TTL_SEC = 7 * 24 * 3600
ICONIFY_API = "https://api.iconify.design"
DEFAULT_ICONIFY_PREFIXES = "lucide,ph,heroicons,tabler"
USER_AGENT = "bioinformatics-plotting-standards/1.0"

NUM_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"


def _http_get(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_bioicons_index(force_refresh: bool = False) -> list[dict]:
    """加载 Bioicons 官方索引（本地缓存 7 天，避免重复请求）。"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if (
        not force_refresh
        and BIOICONS_INDEX_CACHE.exists()
        and (time.time() - BIOICONS_INDEX_CACHE.stat().st_mtime) < BIOICONS_TTL_SEC
    ):
        return json.loads(BIOICONS_INDEX_CACHE.read_text(encoding="utf-8"))
    raw = _http_get(BIOICONS_INDEX_URL, timeout=20)
    data = json.loads(raw.decode("utf-8"))
    BIOICONS_INDEX_CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def search_iconify(query: str, prefixes: str = DEFAULT_ICONIFY_PREFIXES, limit: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"query": query, "prefixes": prefixes, "limit": limit})
    url = f"{ICONIFY_API}/search?{params}"
    data = json.loads(_http_get(url, timeout=12).decode("utf-8"))
    results = []
    for icon_id in data.get("icons", [])[:limit]:
        prefix = icon_id.split(":", 1)[0]
        lic_hint = "ISC" if prefix == "lucide" else "MIT"
        results.append({
            "source": "iconify",
            "id": icon_id,
            "category": prefix,
            "license": lic_hint,
            "author": prefix,
        })
    return results


def search_bioicons(query: str, limit: int = 10) -> list[dict]:
    tokens = [t.lower() for t in re.split(r"[\s_\-/]+", query.strip()) if t]
    if not tokens:
        return []
    index = load_bioicons_index()
    scored: list[tuple[int, dict]] = []
    for item in index:
        name = item.get("name", "")
        cat = item.get("category", "")
        author = item.get("author", "")
        nl, cl = name.lower(), cat.lower()
        score = 0
        for tok in tokens:
            if tok == nl:
                score += 10
            elif tok in nl:
                score += 5
            elif tok in cl:
                score += 2
            elif tok in author.lower():
                score += 1
        if score > 0:
            # 轻微偏好 Servier / DBCLS / CC-0 的高质量生医矢量图标
            if item.get("license") == "cc-0":
                score += 1
            scored.append((score, item))
    scored.sort(key=lambda x: (-x[0], len(x[1].get("name", ""))))
    results = []
    for _, item in scored[:limit]:
        author_slug = item["author"].replace(" ", "_")
        full_id = f"bioicons:{item['license']}/{item['category']}/{author_slug}/{item['name']}"
        results.append({
            "source": "bioicons",
            "id": full_id,
            "short_id": f"bioicons:{item['name']}",
            "category": item["category"],
            "license": item["license"],
            "author": item["author"],
        })
    return results


def _resolve_bioicon_entry(spec: str) -> dict:
    """将 `bioicons:dna-2` 或完整路径 `bioicons:cc-by-3.0/Nucleic_acids/Servier/dna-2` 解析为条目字典。"""
    body = spec.split(":", 1)[1].strip()
    if body.count("/") == 3:
        lic, cat, author_slug, name = body.split("/")
        return {
            "license": lic,
            "category": cat,
            "author": author_slug.replace("_", " "),
            "author_slug": author_slug,
            "name": name.removesuffix(".svg"),
        }
    target = body.removesuffix(".svg").lower()
    index = load_bioicons_index()
    exact = [d for d in index if d["name"].lower() == target]
    if not exact:
        fuzzy = [d for d in index if target in d["name"].lower()]
        if not fuzzy:
            raise ValueError(f"Bioicons 中未找到图标 '{body}'，请先运行 `search` 确认准确名称。")
        exact = fuzzy
    # 优先选 cc-0，其次 Servier / DBCLS
    exact.sort(key=lambda d: (0 if d["license"] == "cc-0" else 1, 0 if d["author"] in ("Servier", "DBCLS") else 1))
    picked = dict(exact[0])
    picked["author_slug"] = picked["author"].replace(" ", "_")
    return picked


def download_raw_svg(icon_id: str, force_refresh: bool = False) -> tuple[str, dict]:
    """下载原始 SVG 并缓存至 ~/.cache/bio-plot-icons/svg/，返回 (svg_text, meta)。"""
    svg_cache_dir = CACHE_DIR / "svg"
    svg_cache_dir.mkdir(parents=True, exist_ok=True)

    if icon_id.startswith("bioicons:"):
        entry = _resolve_bioicon_entry(icon_id)
        rel_path = f"icons/{entry['license']}/{entry['category']}/{entry['author_slug']}/{entry['name']}.svg"
        url = "https://bioicons.com/" + urllib.parse.quote(rel_path, safe="/")
        canonical_id = f"bioicons:{entry['license']}/{entry['category']}/{entry['author_slug']}/{entry['name']}"
        meta = {
            "id": canonical_id,
            "source": "bioicons",
            "license": entry["license"],
            "author": entry["author"],
            "url": url,
        }
    else:
        if ":" not in icon_id:
            icon_id = f"lucide:{icon_id}"
        prefix, name = icon_id.split(":", 1)
        url = f"{ICONIFY_API}/{urllib.parse.quote(prefix)}/{urllib.parse.quote(name)}.svg"
        canonical_id = f"{prefix}:{name}"
        meta = {
            "id": canonical_id,
            "source": "iconify",
            "license": "ISC" if prefix == "lucide" else "MIT",
            "author": prefix,
            "url": url,
        }

    key_hash = hashlib.sha1(canonical_id.encode("utf-8")).hexdigest()[:16]
    cache_file = svg_cache_dir / f"{key_hash}.svg"
    if not force_refresh and cache_file.exists():
        return cache_file.read_text(encoding="utf-8"), meta

    raw = _http_get(url, timeout=15).decode("utf-8", errors="replace")
    if "<svg" not in raw.lower():
        raise RuntimeError(f"下载的内容不是有效 SVG（{url}）")
    cache_file.write_text(raw, encoding="utf-8")
    return raw, meta


def _parse_viewbox(root) -> tuple[float, float, float, float]:
    vb = root.get("viewBox")
    if vb:
        nums = [float(x) for x in NUM_RE.findall(vb)]
        if len(nums) == 4 and nums[2] > 0 and nums[3] > 0:
            return nums[0], nums[1], nums[2], nums[3]
    w_s = root.get("width") or "24"
    h_s = root.get("height") or "24"
    w = float((NUM_RE.findall(w_s) or ["24"])[0])
    h = float((NUM_RE.findall(h_s) or ["24"])[0])
    return 0.0, 0.0, max(w, 1.0), max(h, 1.0)


def _is_neutral_white_or_none(val: str) -> bool:
    v = val.strip().lower()
    return v in ("", "none", "transparent", "#fff", "#ffffff", "white", "rgb(255,255,255)")


def sanitize_and_recolor(
    svg_text: str,
    prefix: str,
    color: str | None = None,
    stroke_width: float | None = None,
    source: str = "iconify",
) -> tuple[str, tuple[float, float, float, float]]:
    """
    清洗外部 SVG 使其可安全内联到主图：
    1. 剥离 XML 声明、注释、metadata、Inkscape/Sodipodi 非标准编辑节点；
    2. 为所有 id / url(#...) / href="#..." 与 CSS 类名 (.cls-1 等) 加上唯一前缀，防止多个图标互相污染；
    3. 按需统一改色（Iconify 替换 currentColor/显式色，Bioicons 单色着色保留白色与透明镂空）。
    返回 (inner_svg_markup, (vb_x, vb_y, vb_w, vb_h))。
    """
    from lxml import etree

    parser = etree.XMLParser(remove_comments=True, recover=True)
    root = etree.fromstring(svg_text.encode("utf-8"), parser=parser)
    vb = _parse_viewbox(root)

    # 移除非渲染元数据节点
    drop_local = {"metadata", "title", "desc", "namedview"}
    for el in list(root.iter()):
        tag = el.tag
        if not isinstance(tag, str):
            continue
        local = etree.QName(tag).localname.lower()
        ns_uri = etree.QName(tag).namespace or ""
        if local in drop_local or "sodipodi" in ns_uri or "inkscape" in ns_uri:
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)

    # 剥离非标准编辑属性（inkscape:* / sodipodi:*）
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in list(el.attrib):
            if "inkscape" in attr or "sodipodi" in attr:
                del el.attrib[attr]

    # 1) 收集并重写所有 id 与 <style> 中的 class 选择器，避免与主图或其他图标冲突
    id_map: dict[str, str] = {}
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        old_id = el.get("id")
        if old_id:
            new_id = f"{prefix}_{old_id}"
            id_map[old_id] = new_id
            el.set("id", new_id)

    class_map: dict[str, str] = {}
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if etree.QName(el.tag).localname.lower() == "style" and el.text:
            css = el.text
            for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_-]*)", css):
                cname = m.group(1)
                class_map[cname] = f"{prefix}_{cname}"
            if class_map:
                css = re.sub(
                    r"\.([A-Za-z_][A-Za-z0-9_-]*)",
                    lambda m: "." + class_map.get(m.group(1), m.group(1)),
                    css,
                )
            if id_map:
                css = re.sub(
                    r"url\(\s*['\"]?#([^)'\"]+)['\"]?\s*\)",
                    lambda m: f"url(#{id_map.get(m.group(1), m.group(1))})",
                    css,
                )
            if color:
                css = _recolor_css(css, color)
            el.text = css

    # 更新节点上的 class / url(#...) / href="#..." 引用并按需改色
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if class_map and el.get("class"):
            cls_tokens = el.get("class").split()
            el.set("class", " ".join(class_map.get(c, c) for c in cls_tokens))
        for attr in list(el.attrib):
            val = el.attrib[attr]
            if id_map:
                if "url(#" in val:
                    val = re.sub(
                        r"url\(\s*['\"]?#([^)'\"]+)['\"]?\s*\)",
                        lambda m: f"url(#{id_map.get(m.group(1), m.group(1))})",
                        val,
                    )
                elif attr.endswith("href") and val.startswith("#"):
                    ref_id = val[1:]
                    if ref_id in id_map:
                        val = "#" + id_map[ref_id]
                el.attrib[attr] = val

        # 改色与线宽
        if color:
            _recolor_element(el, color, source=source)
        if stroke_width is not None and el.get("stroke-width") is not None:
            el.set("stroke-width", f"{stroke_width:g}")

    # 若 Iconify 图标使用 currentColor 且未显式指定颜色，默认替换为柔和炭灰 #303030
    default_col = color or "#303030"
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in ("fill", "stroke"):
            if (el.get(attr) or "").strip().lower() == "currentcolor":
                el.set(attr, default_col)

    # 序列化内部子节点并去除冗余 xmlns 声明
    parts = []
    for child in root:
        chunk = etree.tostring(child, encoding="unicode")
        chunk = re.sub(r'\s+xmlns(?::[a-zA-Z0-9_-]+)?="[^"]*"', "", chunk)
        parts.append(chunk)
    return "\n".join(parts), vb


def _recolor_css(css: str, color: str) -> str:
    def _repl(m):
        prop, val = m.group(1), m.group(2)
        if _is_neutral_white_or_none(val) or "url(" in val.lower():
            return m.group(0)
        return f"{prop}:{color}"

    return re.sub(r"\b(fill|stroke)\s*:\s*([^;}\n]+)", _repl, css, flags=re.I)


def _recolor_element(el, color: str, source: str) -> None:
    for attr in ("fill", "stroke"):
        val = el.get(attr)
        if val is not None and not _is_neutral_white_or_none(val) and "url(" not in val.lower():
            el.set(attr, color)
    style = el.get("style")
    if style:
        el.set("style", _recolor_css(style, color))
    # 某些 Iconify 实心图标根节点带 fill="currentColor"，子节点无 fill 属性
    if source == "iconify" and el.tag.endswith(("path", "circle", "rect", "polygon", "ellipse")):
        if el.get("fill") is None and el.get("stroke") is None and (el.get("style") or "") == "":
            pass  # 由外层 <g fill="..."> 统一继承


def inline_icon_g(
    icon_id: str,
    x: float = 0.0,
    y: float = 0.0,
    size: float = 16.0,
    color: str | None = None,
    stroke_width: float | None = None,
    prefix: str | None = None,
) -> str:
    """
    获取并清洗图标，返回可直接嵌入主 SVG 的 `<g>` 字符串。
    图标按原始宽高比等比缩放入以 (x, y) 为左上角、边长为 size 的正方形盒子内并居中。
    """
    raw_svg, meta = download_raw_svg(icon_id)
    safe_prefix = prefix or ("ic_" + hashlib.sha1(f"{meta['id']}_{x}_{y}".encode()).hexdigest()[:6])
    inner, (vx, vy, vw, vh) = sanitize_and_recolor(
        raw_svg,
        prefix=safe_prefix,
        color=color,
        stroke_width=stroke_width,
        source=meta["source"],
    )
    scale = size / max(vw, vh)
    ox = x + (size - vw * scale) / 2.0 - vx * scale
    oy = y + (size - vh * scale) / 2.0 - vy * scale

    extra_fill = f' fill="{color}"' if (meta["source"] == "iconify" and color) else ""
    lic_attr = f' data-icon="{meta["id"]}" data-license="{meta["license"]}"'
    return (
        f'<g{lic_attr} transform="translate({ox:.2f},{oy:.2f}) scale({scale:.5f})"{extra_fill}>\n'
        f"{inner}\n"
        f"</g>"
    )


def build_standalone_svg(
    icon_id: str,
    color: str | None = None,
    stroke_width: float | None = None,
    prefix: str | None = None,
) -> tuple[str, dict]:
    raw_svg, meta = download_raw_svg(icon_id)
    safe_prefix = prefix or ("ic_" + hashlib.sha1(meta["id"].encode()).hexdigest()[:6])
    inner, (vx, vy, vw, vh) = sanitize_and_recolor(
        raw_svg,
        prefix=safe_prefix,
        color=color,
        stroke_width=stroke_width,
        source=meta["source"],
    )
    extra_fill = f' fill="{color}"' if (meta["source"] == "iconify" and color) else ""
    svg = (
        f'<svg xmlns="{SVG_NS}" xmlns:xlink="{XLINK_NS}" '
        f'viewBox="{vx:g} {vy:g} {vw:g} {vh:g}" width="{vw:g}pt" height="{vh:g}pt"{extra_fill}>\n'
        f"{inner}\n"
        f"</svg>\n"
    )
    return svg, meta


def main() -> None:
    ap = argparse.ArgumentParser(description="Search and fetch cleaned SVG icons from Iconify and Bioicons.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_s = sub.add_parser("search", help="Search icons across Iconify and/or Bioicons")
    sp_s.add_argument("query", help="Search keyword (e.g. database, dna, cell, microscope, filter)")
    sp_s.add_argument("--source", choices=["all", "iconify", "bioicons"], default="all")
    sp_s.add_argument("--prefixes", default=DEFAULT_ICONIFY_PREFIXES, help="Iconify prefixes")
    sp_s.add_argument("--limit", type=int, default=8, help="Max results per source")

    sp_f = sub.add_parser("fetch", help="Download, sanitize, optionally recolor, and output SVG or inline <g>")
    sp_f.add_argument("icon_id", help="Iconify ID (e.g. lucide:database) or Bioicons ID (e.g. bioicons:dna-2)")
    sp_f.add_argument("-o", "--out", help="Output file path (prints to stdout if omitted)")
    sp_f.add_argument("--color", help="Recolor hex (e.g. '#316F98'); omit on Bioicons to keep native colors")
    sp_f.add_argument("--stroke-width", type=float, help="Override stroke-width for line icons")
    sp_f.add_argument("--inline-g", action="store_true", help="Emit inline <g transform=...> snippet for embedding")
    sp_f.add_argument("--x", type=float, default=0.0, help="Target box left x (pt) when --inline-g")
    sp_f.add_argument("--y", type=float, default=0.0, help="Target box top y (pt) when --inline-g")
    sp_f.add_argument("--size", type=float, default=16.0, help="Target box width/height (pt) when --inline-g")
    sp_f.add_argument("--prefix", help="Custom ID/CSS class namespace prefix")

    args = ap.parse_args()

    if args.cmd == "search":
        rows = []
        if args.source in ("all", "iconify"):
            try:
                rows.extend(search_iconify(args.query, prefixes=args.prefixes, limit=args.limit))
            except Exception as e:
                print(f"[warn] Iconify search failed: {e}", file=sys.stderr)
        if args.source in ("all", "bioicons"):
            try:
                rows.extend(search_bioicons(args.query, limit=args.limit))
            except Exception as e:
                print(f"[warn] Bioicons search failed: {e}", file=sys.stderr)
        if not rows:
            print(f"No icons found for {args.query!r}", file=sys.stderr)
            sys.exit(1)
        for r in rows:
            extra = f" (short: {r['short_id']})" if "short_id" in r else ""
            print(f"[{r['source']:8s}] {r['id']}{extra}  | cat={r['category']} | lic={r['license']} | by={r['author']}")
        return

    if args.cmd == "fetch":
        if args.inline_g:
            _, meta = download_raw_svg(args.icon_id)
            out_txt = inline_icon_g(
                args.icon_id,
                x=args.x,
                y=args.y,
                size=args.size,
                color=args.color,
                stroke_width=args.stroke_width,
                prefix=args.prefix,
            )
        else:
            out_txt, meta = build_standalone_svg(
                args.icon_id,
                color=args.color,
                stroke_width=args.stroke_width,
                prefix=args.prefix,
            )

        if "cc-by" in meta["license"].lower():
            print(
                f"[license] {meta['id']} uses {meta['license'].upper()} (author: {meta['author']}) — "
                "remember to credit Bioicons / author in thesis figure caption or acknowledgments.",
                file=sys.stderr,
            )

        if args.out:
            p = Path(args.out)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(out_txt, encoding="utf-8")
            print(f"Wrote {p} ({meta['id']})", file=sys.stderr)
        else:
            print(out_txt)


if __name__ == "__main__":
    main()
