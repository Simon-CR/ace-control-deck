#!/usr/bin/env python3
"""Re-apply the ACE panel customisations after a Mainsail update.

Mainsail is installed with update_manager `type: web`: the release zip is extracted over
/home/simon/mainsail, which drops BOTH the custom iframe panel (it lives inside that tree)
and the nozzle node patched into the MMU panel bundle. The bundle's filename carries a
content hash, so it changes on every release and cannot be referenced by name.

Idempotent by design: safe to run at any time, does nothing when already applied. Driven by
ace-panel-patch.path, which fires whenever Mainsail's index.html is rewritten.
"""
import argparse, glob, hashlib, io, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Default source is one level up
PANEL_SRC = os.path.join(HERE, "..", "index.html")

# The MMU panel emits one of these per sensor dot. Quoting differs between Mainsail releases
# (backticks in 2.18, plain quotes in the 2.17 Happy-Hare fork), so match either.
TOOLHEAD = re.compile(
    r't\((\w+),\{attrs:\{"sensor-name":([`"])toolhead\2,'
    r'"sensor-text":e\.\$t\(([`"])Panels\.MmuPanel\.Toolhead\3\),'
    r'"y-position":350\}\}\)'
)

def get_sites():
    parser = argparse.ArgumentParser(description="Patch Mainsail to add ACE Deck")
    parser.add_argument("--mainsail-path", type=str, help="Path to mainsail directory")
    args = parser.parse_args()
    
    if args.mainsail_path:
        return [args.mainsail_path]
    
    # Try generic homedir paths
    home = os.path.expanduser("~")
    return [os.path.join(home, "mainsail"), os.path.join(home, "mainsail-hh")]


def restore_panel(site):
    """Put the custom iframe panel back; an update deletes it."""
    status = []
    if os.path.exists(PANEL_SRC):
        dest_dir = os.path.join(site, "ace")
        dest = os.path.join(dest_dir, "index.html")
        if not (os.path.exists(dest) and open(dest, "rb").read() == open(PANEL_SRC, "rb").read()):
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy(PANEL_SRC, dest)
            status.append("ace restored")
        else:
            status.append("ace current")
    else:
        status.append("no ace src")

    if os.path.exists(HELIX_PANEL_SRC):
        hdest = os.path.join(hdest_dir, "index.html")
        if not (os.path.exists(hdest) and open(hdest, "rb").read() == open(HELIX_PANEL_SRC, "rb").read()):
            os.makedirs(hdest_dir, exist_ok=True)
            shutil.copy(HELIX_PANEL_SRC, hdest)
        else:
    else:

    return ", ".join(status)


def patch_bundle(site):
    """Add a nozzle dot to the MMU panel, mirroring the toolhead node."""
    for path in glob.glob(os.path.join(site, "assets", "index-*.js")):
        s = io.open(path, encoding="utf-8").read()
        m = TOOLHEAD.search(s)
        if not m:
            continue
        if '"sensor-name":`nozzle`' in s or '"sensor-name":"nozzle"' in s:
            return path, "nozzle node already present"
        comp, q1 = m.group(1), m.group(2)
        # Literal label: no Panels.MmuPanel.Nozzle key exists in the locale tables.
        node = (',t(%s,{attrs:{"sensor-name":%snozzle%s,"sensor-text":%sNozzle%s,'
                '"y-position":395}})' % (comp, q1, q1, q1, q1))
        s = s[:m.end()] + node + s[m.end():]
        if not os.path.exists(path + ".preace"):
            shutil.copy(path, path + ".preace")
        io.open(path, "w", encoding="utf-8", newline="").write(s)
        return path, "nozzle node inserted"
    return None, "no MMU bundle found"


def bust_sw(site, bundle):
    """Workbox precaches assets/index-*.js with revision:null, so an in-place edit is never
    re-fetched. Give the entry a revision derived from the file so browsers pick it up."""
    sw = os.path.join(site, "sw.js")
    if not bundle or not os.path.exists(sw):
        return "no sw.js"
    name = os.path.basename(bundle)
    rev = hashlib.sha1(open(bundle, "rb").read()).hexdigest()[:12]
    s = io.open(sw, encoding="utf-8").read()
    prefix = 'self.skipWaiting();self.addEventListener("activate",()=>self.clients.claim());'
    if not s.startswith(prefix):
        s = prefix + s
    pat = re.compile(r'\{url:"assets/%s",revision:(null|"[^"]*")\}' % re.escape(name))
    m = pat.search(s)
    if not m:
        return "sw entry not found"
    if m.group(1) == '"%s"' % rev and s.startswith(prefix):
        io.open(sw, "w", encoding="utf-8", newline="").write(s)
        return "sw revision already current"
    s = s[:m.start()] + '{url:"assets/%s",revision:"%s"}' % (name, rev) + s[m.end():]
    io.open(sw, "w", encoding="utf-8", newline="").write(s)
    return "sw revision bumped"


def patch_route(site):
    """Add /acedeck route to Mainsail Vue router."""
    ver = "1"
    if os.path.exists(PANEL_SRC):
        ver = hashlib.md5(open(PANEL_SRC, "rb").read()).hexdigest()[:8]
    for path in glob.glob(os.path.join(site, "assets", "index-*.js")):
        preace = path + ".preace"
        if os.path.exists(preace):
            shutil.copy(preace, path)
        else:
            shutil.copy(path, preace)
        s = io.open(path, encoding="utf-8").read()
        target = "{name:`heightmap`,title:`Heightmap`"
        if target not in s:
            continue
        ace_comp_def = 'AceDeckComp=W({},function(){var e=this,t=e._self._c;return e._self._setupProxy,t(`div`,{staticClass:`fill-height`,style:{width:`100%`,height:`calc(100vh - 36px)`,position:`relative`,overflow:`hidden`}},[t(`iframe`,{attrs:{src:`/ace/index.html?v=' + ver + '`},style:{width:`100%`,height:`100%`,border:`none`,display:`block`/* iframe */}})])},[],!1,null,null,null,null).exports,'
        route_str = '{name:`acedeck`,title:`ACE Deck`,path:`/acedeck`,icon:kr,component:AceDeckComp,alwaysShow:!0,showInNavi:!0,position:35},'
        dj_pos = s.find("dj=[")
        if dj_pos != -1:
            s = s[:dj_pos] + ace_comp_def + s[dj_pos:]
        s = s.replace(target, route_str + target)
        io.open(path, "w", encoding="utf-8", newline="").write(s)
        return path, "routes cleanly inserted"
    return None, "no route table found"


def patch_locale(site):
    """Add Router translations so sidebar displays correctly."""
    for path in glob.glob(os.path.join(site, "assets", "en-*.js")):
        s = io.open(path, encoding="utf-8").read()
        target = "Dashboard:`Dashboard`,"
        if target in s:
            s = s.replace('"ACE Deck":`ACE Deck`,', '')
            s = s.replace(target, '"ACE Deck":`ACE Deck`,' + target)
            io.open(path, "w", encoding="utf-8", newline="").write(s)
            return path, "locale patched for ACE Deck"
    return None, "no en locale found"


def main():
    sites = get_sites()
    for site in sites:
        if not os.path.isdir(site):
            continue
        print("[%s]" % site)
        print("  ", restore_panel(site))
        bundle, msg = patch_bundle(site)
        print("  ", msg)
        bundle_r, msg_r = patch_route(site)
        print("  ", msg_r)
        loc, msg_loc = patch_locale(site)
        print("  ", msg_loc)
        print("  ", bust_sw(site, bundle or bundle_r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
