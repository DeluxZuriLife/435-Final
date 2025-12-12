"""
Prop Rig Generating Tool (Maya GUI)

Creates a simple rig structure for props using an ASSET name from environment variables.

Structure:
GRP_<ASSET>
    ┗ GRP_geom
    ┗ GRP_rig

Buttons:
[Create Group]   - Creates the group structure and parents selected geometry under GRP_geom
[Place Locators] - Creates LOC_root, LOC_base, LOC_move (artist positions them manually)
[Build Rig]      - Creates or updates JNT_root -> JNT_base -> JNT_move under GRP_rig,
                   matching locator positions each run (no duplicates)
[Bind] (extra)   - Binds all geometry under GRP_geom to the joints under GRP_rig

Doc refs used by this implementation:
- os.getenv (env vars): https://docs.python.org/3/library/os.html#os.getenv
- cmds.xform (query/set transforms): https://help.autodesk.com/cloudhelp/CHS/MayaCRE-Tech-Docs/Commands/xform.html
- cmds.joint (create/edit joints): https://download.autodesk.com/us/maya/2010help/commandspython/joint.html
- skinCluster concept (binding): https://help.autodesk.com/cloudhelp/2018/CHS/Maya-Tech-Docs/PyMel/generated/classes/pymel.core.nodetypes/pymel.core.nodetypes.SkinCluster.html
- Maya Python workflow guidance: https://www.chadvernon.com/python-scripting-for-maya-artists/
"""

import os
import logging
import maya.cmds as cmds

# -----------------------------
# Logging
# -----------------------------
LOG = logging.getLogger("prop_rig_tool")
if not LOG.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(name)s :: %(message)s"))
    LOG.addHandler(_h)
LOG.setLevel(logging.INFO)

# -----------------------------
# Constants / naming
# -----------------------------
WIN = "PropRigToolWin"

def _asset_name():
    """Read ASSET from environment. (Python os.getenv docs: https://docs.python.org/3/library/os.html#os.getenv)"""
    name = os.getenv("ASSET")
    if not name:
        LOG.warning("ASSET env var not set. Using fallback 'defaultAsset'. (Set in Git Bash: export ASSET=trex)")
        name = "defaultAsset"
    return name

def _grp_names(asset):
    root = f"GRP_{asset}"
    geom = "GRP_geom"
    rig  = "GRP_rig"
    return root, geom, rig

def _loc_names():
    return "LOC_root", "LOC_base", "LOC_move"

def _jnt_names():
    return "JNT_root", "JNT_base", "JNT_move"

# -----------------------------
# Core actions
# -----------------------------
def create_group(*_):
    asset = _asset_name()
    root, geom, rig = _grp_names(asset)

    # Create root group if needed
    if not cmds.objExists(root):
        root = cmds.group(empty=True, name=root)
        LOG.info(f"Created {root}")
    else:
        LOG.info(f"{root} already exists (no duplicate created).")

    # Ensure child groups exist under root (exact names required by spec)
    geom_path = f"{root}|{geom}"
    rig_path  = f"{root}|{rig}"

    if not cmds.objExists(geom_path):
        cmds.group(empty=True, name=geom, parent=root)
        LOG.info(f"Created {geom_path}")
    if not cmds.objExists(rig_path):
        cmds.group(empty=True, name=rig, parent=root)
        LOG.info(f"Created {rig_path}")

    # Move selected geometry under GRP_geom
    sel = cmds.ls(selection=True, long=True) or []
    if not sel:
        LOG.warning("No selection found. Nothing was moved into GRP_geom.")
        return

    # Parent only transforms (avoid shape nodes)
    moved = 0
    for node in sel:
        xform = node
        if cmds.nodeType(node) != "transform":
            parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
            if parents:
                xform = parents[0]

        if cmds.objExists(xform):
            try:
                cmds.parent(xform, geom_path)
                moved += 1
            except Exception as e:
                LOG.warning(f"Could not parent {xform} under {geom_path}: {e}")

    LOG.info(f"Moved {moved} item(s) under {geom_path}")

def place_locators(*_):
    asset = _asset_name()
    root, geom, rig = _grp_names(asset)

    if not cmds.objExists(root):
        LOG.error(f"{root} does not exist. Run [Create Group] first.")
        return

    loc_root, loc_base, loc_move = _loc_names()

    # Place locators at the root group pivot (xform doc: https://help.autodesk.com/cloudhelp/CHS/MayaCRE-Tech-Docs/Commands/xform.html)
    pivot = cmds.xform(root, query=True, worldSpace=True, rotatePivot=True)

    for loc in (loc_root, loc_base, loc_move):
        if not cmds.objExists(loc):
            cmds.spaceLocator(name=loc)
            LOG.info(f"Created {loc}")
        cmds.xform(loc, worldSpace=True, translation=pivot)

    LOG.info("Locators placed. Artist can now move LOC_root / LOC_base / LOC_move by hand.")

def build_rig(*_):
    asset = _asset_name()
    root, geom, rig = _grp_names(asset)
    rig_path = f"{root}|{rig}"

    if not cmds.objExists(rig_path):
        LOG.error(f"{rig_path} does not exist. Run [Create Group] first.")
        return

    loc_root, loc_base, loc_move = _loc_names()
    for loc in (loc_root, loc_base, loc_move):
        if not cmds.objExists(loc):
            LOG.error(f"{loc} not found. Run [Place Locators] first.")
            return

    jnt_root, jnt_base, jnt_move = _jnt_names()

    # Query locator positions
    p_root = cmds.xform(loc_root, query=True, worldSpace=True, translation=True)
    p_base = cmds.xform(loc_base, query=True, worldSpace=True, translation=True)
    p_move = cmds.xform(loc_move, query=True, worldSpace=True, translation=True)

    # Create or update joints (joint doc: https://download.autodesk.com/us/maya/2010help/commandspython/joint.html)
    # Rule: no duplicates; if joint exists, move it. If not, create it.

    def _ensure_joint(name, pos):
        if cmds.objExists(name):
            cmds.xform(name, worldSpace=True, translation=pos)
            LOG.info(f"Moved {name} to locator position.")
            return name
        cmds.select(clear=True)
        j = cmds.joint(name=name, position=pos)
        LOG.info(f"Created {j}")
        return j

    jr = _ensure_joint(jnt_root, p_root)
    jb = _ensure_joint(jnt_base, p_base)
    jm = _ensure_joint(jnt_move, p_move)

    # Ensure hierarchy JNT_root -> JNT_base -> JNT_move
    # Parent carefully (avoid breaking if already correct)
    try:
        if cmds.listRelatives(jb, parent=True) != [jr]:
            cmds.parent(jb, jr)
        if cmds.listRelatives(jm, parent=True) != [jb]:
            cmds.parent(jm, jb)
    except Exception as e:
        LOG.warning(f"Parenting joints failed: {e}")

    # Ensure the chain lives under GRP_rig (not under world)
    try:
        if cmds.listRelatives(jr, parent=True, fullPath=True) != [rig_path]:
            cmds.parent(jr, rig_path)
    except Exception as e:
        LOG.warning(f"Parenting {jr} under {rig_path} failed: {e}")

    LOG.info(f"Rig built/updated under {rig_path}. Press [Build Rig] again after moving locators to update.")

def bind_geom(*_):
    """
    Extra credit: Bind all geometry under GRP_geom to the skeleton in GRP_rig.
    Uses skinCluster concept: https://help.autodesk.com/cloudhelp/2018/CHS/Maya-Tech-Docs/PyMel/generated/classes/pymel.core.nodetypes/pymel.core.nodetypes.SkinCluster.html
    """
    asset = _asset_name()
    root, geom, rig = _grp_names(asset)
    geom_path = f"{root}|{geom}"
    rig_path  = f"{root}|{rig}"

    if not cmds.objExists(geom_path) or not cmds.objExists(rig_path):
        LOG.error("Groups missing. Run [Create Group] first.")
        return

    jnt_root, jnt_base, jnt_move = _jnt_names()
    for j in (jnt_root, jnt_base, jnt_move):
        if not cmds.objExists(j):
            LOG.error("Joints missing. Run [Build Rig] first.")
            return

    # Gather transforms under GRP_geom that have mesh shapes
    candidates = cmds.listRelatives(geom_path, allDescendents=True, fullPath=True, type="transform") or []
    geos = []
    for t in candidates:
        shapes = cmds.listRelatives(t, shapes=True, fullPath=True) or []
        if any(cmds.nodeType(s) == "mesh" for s in shapes):
            geos.append(t)

    if not geos:
        LOG.warning("No mesh geometry found under GRP_geom to bind.")
        return

    # Bind
    try:
        cmds.select(clear=True)
        cmds.select([jnt_root, jnt_base, jnt_move] + geos)
        # Typical smooth bind call:
        cmds.skinCluster(toSelectedBones=True)
        LOG.info(f"Bound {len(geos)} mesh transform(s) to joints.")
    except Exception as e:
        LOG.error(f"Bind failed: {e}")

# -----------------------------
# UI
# -----------------------------
def show_ui(*_):
    if cmds.window(WIN, exists=True):
        cmds.deleteUI(WIN)

    cmds.window(WIN, title="Prop Rig Generating Tool", widthHeight=(320, 220))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.button(label="Create Group", height=30, command=create_group)
    cmds.button(label="Place Locators", height=30, command=place_locators)
    cmds.button(label="Build Rig", height=30, command=build_rig)
    cmds.separator(h=8, style="in")
    cmds.button(label="Bind (Extra Credit)", height=30, command=bind_geom)
    cmds.separator(h=8, style="in")
    cmds.button(label="Close", height=28, command=lambda *_: cmds.deleteUI(WIN))

    cmds.showWindow(WIN)
    LOG.info("UI opened. Workflow: Create Group → Place Locators → (artist moves locators) → Build Rig.")

show_ui()
