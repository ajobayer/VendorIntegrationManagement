#!/usr/bin/env python

import logging
from optparse import OptionParser
import sys
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError


class ModmanError(Exception):
    pass


def tryparse(filepath):
    """Helper function that can construct an error message with the
    pathname of the file if there's problems with parsing.

    """

    try:
        return parse(filepath)
    except ExpatError as e:
        raise ModmanError("Failed to parse %s: %s" % (filepath, e))


def xmlmerge(sourcefile, replacefile, matchfile=None, keep_tags=False,
             tag="project", mattribute="name", rattribute="revision"):
    """Returns merge,match of xmlfiles: sourcefile, replacefile, matchfile.

    Merges values from "replacefile", to "sourcefile", matching "matchfile"
    where "tag" exists in "matchfile" and "sourcefile" and
    all "rattribute" values will be replaced if "mattribute" matches.
    Raises ModmanError on fatal errors.

    """

    sourcetree = tryparse(sourcefile)
    replacetree = tryparse(replacefile)
    if matchfile:
        matchtree = tryparse(matchfile)
    else:
        matchtree = tryparse(sourcefile)

    replacements = {}
    for element in replacetree.getElementsByTagName(tag):
        attribute = \
            element.attributes[mattribute].nodeValue.encode('utf-8')
        replacements[attribute] = \
            element.attributes[rattribute].nodeValue.encode('utf-8')

    nodes = {}
    for element in sourcetree.getElementsByTagName(tag):
        attribute = \
            element.attributes[mattribute].nodeValue.encode('utf-8')
        nodes[attribute] = element

    for element in matchtree.getElementsByTagName(tag):
        attribute = \
            element.attributes[mattribute].nodeValue.encode('utf-8')
        try:
            # Under assumption that a tag is not given as default revision.
            src_revision = nodes[attribute].getAttribute(rattribute)
            if not (keep_tags and src_revision.startswith("refs/tags/")):
                nodes[attribute].setAttribute(rattribute,
                                              replacements[attribute])
                element.setAttribute(rattribute, replacements[attribute])
        except KeyError:
            logging.error("Value revision missing for %s in %s" % (attribute,
                          replacefile))
    return sourcetree, matchtree


def _main(inargs):
    usage = """usage: %prog [OPTIONS] [OUTPUT-FILE] [BRANCHLIST-FILE]
    Modifies manifest files to put static references to a list of
    projects.
    Example:
    %prog -i default.xml -s static.xml -p projects.xml output.xml
    %prog takes at least 2 arguments
     * static-manifest sha-1 revision manifest.
     * input source-manifest as source of projectnames.
     * selected-projects manifest with project names (optional).
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--static", dest="static",
                      help="File containing static manifest with sha-1 "
                      "references. (For all projects mentioned in editlist)")
    parser.add_option("-i", "--input-source", dest="source",
                      help="File containing the manifest you want to modify.")
    parser.add_option("-p", "--projects", dest="project",
                      help="File containing manifest of projects to modify.")
    parser.add_option("-k", "--keep-tags", dest="keep_tags",
                      action="store_true",
                      help="Keep the revision, if revision in source manifest"
                      " is a tag.")

    logging.basicConfig(format='%(message)s', level=logging.INFO)

    (options, argv) = parser.parse_args(inargs)
    if not any([options.static, options.source]):
        parser.error("You did not give any arguments")
    if not options.static:
        parser.print_help()
        parser.error("You must specify a static sha1 file.")
    if not options.source:
        parser.print_help()
        parser.error("You must specify a target file.")

    try:
        mergeresult, branchresult = xmlmerge(options.source,
                                             options.static,
                                             options.project,
                                             options.keep_tags,
                                             "project", "name", "revision")
    except EnvironmentError as e:
        logging.error("Failed to read input: %s" % e)
        return 1
    except ModmanError as e:
        logging.error(e)
        return 1

    if len(argv) == 0:
        outputfile = "output.xml"
        branchlistfile = "branchlist.xml"
    elif len(argv) == 1:
        outputfile = argv[0]
        branchlistfile = "branchlist.xml"
    elif len(argv) >= 2:
        outputfile = argv[0]
        branchlistfile = argv[1]

    try:
        with file(outputfile, "w") as mergeoutput:
            mergeresult.writexml(mergeoutput, encoding="UTF-8")

        with file(branchlistfile, "w") as branchoutput:
            branchresult.writexml(branchoutput, encoding="UTF-8")
    except EnvironmentError as e:
        logging.error("Failed to write output: %s" % e)
        return 1

    logging.info("Done writing to %s and %s" % (outputfile, branchlistfile))
    return 0

if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
