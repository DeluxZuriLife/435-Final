# Title: 
Final No. 1 
Prop Rig Generating Tool (procedural prop generation based on environment variables.) 
  This tool is a procedural prop rig set up designed to bridge git and Autodesk Maya. It assists rigging teams in rapidly preparing consistent prop structures before assets are imported into game engine. 
The tool relies on asset name (s) being declared using git commands via environmental variables. It generates a simple Maya User Interface that guides the artist through a repeatable workflow.

Here are the steps you should follow to execute this code: 
- Create a group based on an asset name set in an environment variable, along with two child groups
- Create a UI with the following buttons:
    --create group   → creates the group based on an asset name from env variable along with two child groups and move into GRP geom group
    --place locators → creates three locators: LOC root, LOC base, LOC move at pivot point of the group.
    --build rig     → creates create a joint hierarchy with each joint at the matching locator position under GRP_rig. Each time the button is pressed again, it will not add new joints, but will move the existing joints to the correct locator position under GRP_rig.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation
 1. Clone or download the project folder from Gitbash
           git clone <repository_url>
Since filepath's are different for everyone doing this will ensure that every machine, every workstation and every artist is on the same page in the studio. 
 
2. Open Git Bash and ensure there are environmental variables 
           export ASSET=trex
       
 3. Launch Maya from the same Gitbash Session 
           Environment variables are only inherited if Maya is launched from the shell where they were set: 
               "/c/Program Files/Autodesk/Maya2025/bin/maya.exe" 
           This may differ depending on your naming conventions and where you saved the maya software on your computer.  

## Usage

Using the Maya UI (inside Maya)

Open Maya

Load your script in the Script Editor

Run:

import final

execute the script 

A window labeled "PropRigsToolWin" will appear


##Recommended Artist Workflow

Select geometry in the scene

Click Create Group

Click Place Locators

Manually move the locators into position

Click Build Rig

(Optional) Repeat steps 4–5 to refine joint placement

(Optional) Click Bind to skin geometry to the rig

## Workflow Summary
Select Geometry
      ↓
Create Group
      ↓
Place Locators
      ↓
Move Locators (manual)
      ↓
Build Rig
      ↓
(optional) Bind


This design prioritizes:

Fast iteration

Consistent naming

Minimal user error

Pipeline safety across multiple machines

## Contributing

This project is intended for educational and pipeline-training purposes.
Contributions should prioritize:

Clarity

Deterministic behavior

Non-destructive workflows

Explicit logging

## License
