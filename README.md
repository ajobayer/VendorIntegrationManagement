# Usage:
## modify_manifest.py [OPTIONS] [OUTPUT-FILE] [BRANCHLIST-FILE
    Modifies manifest files to put static references to a list of
    projects.
## Example: modify_manifest.py -i default.xml -s static.xml -p projects.xm
    modify_manifest.py takes at least 2 arguments
     * static-manifest sha-1 revision manifest.
     * input source-manifest as source of projectnames.
     * selected-projects manifest with project names (optional).

# Description:
## INPUT:

    -- source --
    A normal default.xml file from the branch you're starting from.

    project1 revision=branch
    project2 revision=branch
    project3 revision=branch
    project4 revision=branch
    project5 revision=branch
    project6 revision=branch

    -- selected-projects --
    A manifest, but the only thing that's read from this is which projects it
    contains. Those projects will be given SHA1s.

    project3 ???
    project5 ???

    -- static-manifest --
    A manifest_static.xml from the freeze you want to use.

    project1 revision=0c01eb
    project2 revision=ce36a6
    project3 revision=cd508c
    project4 revision=df980d
    project5 revision=879585
    project6 revision=842a26

## OUTPUT:

    -- output --
    project3 and 5 gets a SHA1.

    project1 revision=branch
    project2 revision=branch
    project3 revision=cd508c
    project4 revision=branch
    project5 revision=879585
    project6 revision=branch

    -- branchlist --
    This is a modified "selected-projects" with the SHA1s inserted.

    project3 revision=cd508c
    project5 revision=879585
