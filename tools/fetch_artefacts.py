#!/usr/bin/env python3
"""Fetch freely licensed images from Wikimedia Commons for each Dow timeline event.

Reads plan.json, writes img/NNN-K.jpg and manifest.json next to this script.
Only keeps files hosted on Commons with a free license (public domain or CC).
Safe to re-run: images already downloaded are reused.
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request, html

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
UA = "DowTimelineArtefacts/1.0 (personal learning project; contact via claude.ai)"
WP = "https://en.wikipedia.org/w/api.php"
CM = "https://commons.wikimedia.org/w/api.php"
FREE = re.compile(r"public domain|^pd|cc0|cc[- ]by|no restrictions|attribution|gfdl|free art|copyrighted free use", re.I)
OK_MIME = {"image/jpeg", "image/png", "image/tiff", "image/svg+xml", "image/gif", "image/webp"}
SKIP_NAME = re.compile(r"(flag_of|coat_of_arms|seal_of|logo|icon|symbol|signature|locator|blank|question_book)", re.I)


def get(url, params, tries=4):
    q = url + "?" + urllib.parse.urlencode({**params, "format": "json", "formatversion": "2"})
    for i in range(tries):
        try:
            req = urllib.request.Request(q, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 ** i)
            err = e
    print("  API failed:", err, file=sys.stderr)
    return {}


def strip(s, n=320):
    s = html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()
    s = re.sub(r"\s+", " ", s)
    return (s[: n - 1] + "…") if len(s) > n else s


def info_for(titles):
    """Commons imageinfo for a list of File: titles."""
    d = get(CM, {"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
                 "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1100})
    return d.get("query", {}).get("pages", [])


def usable(p):
    if p.get("missing") or not p.get("imageinfo"):
        return None
    ii = p["imageinfo"][0]
    md = ii.get("extmetadata", {})
    lic = md.get("LicenseShortName", {}).get("value", "")
    if ii.get("mime") not in OK_MIME or not FREE.search(lic) or "fair use" in lic.lower():
        return None
    if SKIP_NAME.search(p["title"]):
        return None
    if ii.get("width", 0) < 400 and ii.get("mime") != "image/svg+xml":
        return None
    return {
        "file": p["title"],
        "thumb": ii.get("thumburl") or ii["url"],
        "page": ii.get("descriptionurl"),
        "license": strip(lic, 60),
        "artist": strip(md.get("Artist", {}).get("value", ""), 120),
        "date": strip(md.get("DateTimeOriginal", {}).get("value", ""), 40),
        "desc": strip(md.get("ImageDescription", {}).get("value", "")),
        "objname": strip(md.get("ObjectName", {}).get("value", ""), 120),
    }


def from_wiki(title):
    d = get(WP, {"action": "query", "titles": title, "prop": "pageimages", "piprop": "name", "redirects": 1})
    pages = d.get("query", {}).get("pages", [])
    name = pages[0].get("pageimage") if pages else None
    if name:
        for p in info_for(["File:" + name]):
            u = usable(p)
            if u:
                return u
    # Fall back to other images used on the article.
    d = get(WP, {"action": "query", "titles": title, "prop": "images", "imlimit": 25, "redirects": 1})
    pages = d.get("query", {}).get("pages", [])
    files = [i["title"] for i in (pages[0].get("images", []) if pages else [])
             if re.search(r"\.(jpe?g|png|tiff?)$", i["title"], re.I) and not SKIP_NAME.search(i["title"])]
    if files:
        cands = [usable(p) for p in info_for(files[:20])]
        cands = [c for c in cands if c]
        if cands:
            return cands[0]
    return from_search(title)


def from_search(q):
    d = get(CM, {"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6,
                 "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1100})
    pages = sorted(d.get("query", {}).get("pages", []), key=lambda p: p.get("index", 99))
    for p in pages:
        u = usable(p)
        if u:
            return u
    return None


def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        return True
    tmp = path + ".src"
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
                f.write(r.read())
            break
        except Exception as e:
            time.sleep(2 ** i)
    else:
        return False
    # Normalise to a ~1000px JPEG with macOS sips, falling back to Pillow, then to the raw file.
    try:
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", "1100", tmp, "--out", path],
                       check=True, capture_output=True)
    except Exception:
        try:
            from PIL import Image
            im = Image.open(tmp).convert("RGB")
            im.thumbnail((1100, 1100))
            im.save(path, "JPEG", quality=72, optimize=True, progressive=True)
        except Exception:
            os.replace(tmp, path)
    if os.path.exists(tmp):
        os.remove(tmp)
    return os.path.exists(path)


def main():
    plan = json.load(open(os.path.join(HERE, "plan.json")))
    out_path = os.path.join(HERE, "manifest.json")
    manifest = json.load(open(out_path)) if os.path.exists(out_path) else {}
    seen = {a["file"] for v in manifest.values() for a in v.get("items", [])}
    for n in sorted(plan, key=int):
        if n in manifest and manifest[n].get("items"):
            continue
        entry = {"items": [], "missed": []}
        if plan[n].get("quote"):
            entry["quote"] = plan[n]["quote"]
        for k, (kind, src) in enumerate(plan[n]["items"]):
            how, q = src.split(":", 1)
            hit = from_wiki(q) if how == "w" else from_search(q)
            time.sleep(0.25)
            if not hit or hit["file"] in seen:
                entry["missed"].append(src)
                continue
            fn = f"{int(n):03d}-{k + 1}.jpg"
            if not download(hit["thumb"], os.path.join(IMG, fn)):
                entry["missed"].append(src)
                continue
            seen.add(hit["file"])
            hit.update({"img": "img/" + fn, "type": kind, "source": src})
            entry["items"].append(hit)
        manifest[n] = entry
        print(n, len(entry["items"]), "found", "| missed:", entry["missed"], flush=True)
        json.dump(manifest, open(out_path, "w"), indent=1, ensure_ascii=False)
    total = sum(len(v["items"]) for v in manifest.values())
    empty = [n for n, v in manifest.items() if not v["items"]]
    print("DONE images:", total, "events without image:", empty)


if __name__ == "__main__":
    main()
