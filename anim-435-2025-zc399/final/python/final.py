"""
Prop Rig Generating Tool (procedural prop generation based on environment and CLI flags)

- Create a group based on an asset name set in an environment variable, along with two child groups
- Create a UI with the following buttons:
    --create group   → creates the group based on an asset name from env variable along with two child groups and move into GRP geom group
    --place locators → creates three locators: LOC root, LOC base, LOC move at pivot point of the group.
    --build rig     → creates create a joint hierarchy with each joint at the matching locator position under GRP_rig. Each time the button is pressed again, it will not add new joints, but will move the existing joints to the correct locator position under GRP_rig.

Notes / references:
- os.getenv: https://docs.python.org/3/library/os.html#os.getenv
- argparse.ArgumentParser / add_argument: https://docs.python.org/3/library/argparse.html
- maya.cmds.file: see Autodesk Maya cmds.file docs
- General Maya Python workflow: Chad Vernon, "Python Scripting for Maya Artists"
"""
#Imports###########
import os
import maya.cmds as cmds
import argparse
import maya.standalone
import logging

#Activate Maya Standalone#######
maya.standalone.initialize()

#Activate Logging###########
LOG = logging.getLogger(__name__)

if not LOG.handlers:  # Safety for multiple reloads
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s :: %(message)s'
    )
    handler.setFormatter(formatter)
    LOG.addHandler(handler)
    LOG.setLevel(logging.INFO)

#Functions#########
Win = "PropRigs"

#Asset Names from Environment Variable#########
def get_asset_name():
    """Retrieve the asset name from the environment variable 'ASSET'."""
    asset_name = os.getenv("ASSET", "defaultAsset")
    if not asset_name:
        LOG.error("ASSET environment variable is not set.")
    return asset_name
#Locator Creation#########

def create_locators(asset_name):
    """Create locators at the pivot point of the group."""
    root_locator = cmds.spaceLocator(name=f"LOC_{asset_name}_root")[0]
    base_locator = cmds.spaceLocator(name=f"LOC_{asset_name}_base")[0]
    move_locator = cmds.spaceLocator(name=f"LOC_{asset_name}_move")[0]
    
    # Position locators at the pivot point of the group
    grp_name = f"GRP_{asset_name}"
    if cmds.objExists(grp_name):
        pivot = cmds.xform(grp_name, query=True, worldSpace=True, rotatePivot=True)
        for locator in [root_locator, base_locator, move_locator]:
            cmds.xform(locator, worldSpace=True, translation=pivot)
    else:
        LOG.warning(f"Group {grp_name} does not exist. Locators created at origin.")
    
    return root_locator, base_locator, move_locator
#Joint Creation#########    
def create_joints(asset_name):
    """Create joints at the locator positions under GRP_rig."""
    rig_grp_name = f"GRP_{asset_name}_rig"
    if not cmds.objExists(rig_grp_name):
        LOG.error(f"Rig group {rig_grp_name} does not exist. Please create the group first.")
        return
    
    locators = {
        "root": f"LOC_{asset_name}_root",
        "base": f"LOC_{asset_name}_base",
        "move": f"LOC_{asset_name}_move"
    }
    
    joints = {}
    for key, locator in locators.items():
        if cmds.objExists(locator):
            pos = cmds.xform(locator, query=True, worldSpace=True, translation=True)
            joint = cmds.joint(name=f"JNT_{asset_name}_{key}", position=pos)
            cmds.parent(joint, rig_grp_name)
            joints[key] = joint
        else:
            LOG.warning(f"Locator {locator} does not exist. Joint not created.")
    
    return joints
#UI Creation#########
def build_ui():
    """Build the UI for the Prop Rig Generating Tool."""
    if cmds.window(Win, exists=True):
        cmds.deleteUI(Win)
    
    cmds.window(Win, title="Prop Rig Generating Tool", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
    
    cmds.button(label="Create Group", height=30, command=lambda *_: create_group_ui())
    cmds.separator(h=6, style="in")
    cmds.button(label="Place Locators", height=30, command=lambda *_: place_locators_ui())
    cmds.separator(h=6, style="in")
    cmds.button(label="Build Rig", height=30, command=lambda *_: build_rig_ui())
    cmds.separator(h=6, style="in")
    cmds.button(label="Close", height=30, command=lambda *_: cmds.deleteUI(Win))
    
    cmds.showWindow(Win)
#Group Creation#########
def get_group_names(asset_name):
    root_grp_name = f"GRP_{asset_name}"
    geom_grp_name = f"GRP_{asset_name}_geom"    
    rig_grp_name = f"GRP_{asset_name}_rig"
    return root_grp_name, geom_grp_name, rig_grp_name

#Bind all geometry in GRP_geom to JNTs under GRP_rig#########
def create_group_ui():
    asset_name = get_asset_name()
    root_grp_name, geom_grp_name, rig_grp_name = get_group_names(asset_name)
    
    if not cmds.objExists(root_grp_name):
        cmds.group(empty=True, name=root_grp_name)
        cmds.group(empty=True, name=geom_grp_name, parent=root_grp_name)
        cmds.group(empty=True, name=rig_grp_name, parent=root_grp_name)
        LOG.info(f"Created groups: {root_grp_name}, {geom_grp_name}, {rig_grp_name}")
    else:
        LOG.warning(f"Group {root_grp_name} already exists.")

