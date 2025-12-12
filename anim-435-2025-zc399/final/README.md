# Title: 
Final No. 1 
Prop Rig Generating Tool (procedural prop generation based on environment and CLI flags)

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
 2. 
          }
Since filepath's are different for everyone doing this will ensure that every machine, every workstation and every artist is on the same page in the studio. 

 3. Load the code in GITBash 

 4. Make sure Maya is made visible to gitbash using the following commands: 
       alias mayapy="/c/Program Files/Autodesk/Maya2025/bin/mayapy.exe" 

## Usage
Using the Maya UI (inside Maya)

Open Maya

Load your script in the Script Editor

Run:

import final


A window labeled "Prop Rigs" will appear



## Contributing


## License
I am uploading this under the standard Github license. 
