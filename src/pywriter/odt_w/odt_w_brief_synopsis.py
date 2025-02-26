"""Provide a class for ODT brief synopsis export.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import *
from pywriter.odt_w.odt_writer import OdtWriter


class OdtWBriefSynopsis(OdtWriter):
    """ODT brief synopsis file writer.

    Export a brief synopsis with chapter titles and scene titles.
    """
    DESCRIPTION = _('Brief synopsis')
    SUFFIX = '_brf_synopsis'

    _fileHeader = f'''{OdtWriter._CONTENT_XML_HEADER}<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>
'''

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title</text:h>
'''

    _chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title</text:h>
'''

    _sceneTemplate = '''<text:p text:style-name="Text_20_body">$Title</text:p>
'''

    _fileFooter = OdtWriter._CONTENT_XML_FOOTER
