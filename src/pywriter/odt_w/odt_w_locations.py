"""Provide a class for ODT invisibly tagged location descriptions export.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import *
from pywriter.odt_w.odt_writer import OdtWriter


class OdtWLocations(OdtWriter):
    """ODT location descriptions file writer.

    Export a location sheet with invisibly tagged descriptions.
    """
    DESCRIPTION = _('Location descriptions')
    SUFFIX = '_locations'

    _fileHeader = f'''{OdtWriter._CONTENT_XML_HEADER}<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>
'''

    _locationTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$AKA</text:h>
<text:section text:style-name="Sect1" text:name="LcID:$ID">
<text:p text:style-name="Text_20_body">$Desc</text:p>
</text:section>
'''

    _fileFooter = OdtWriter._CONTENT_XML_FOOTER

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId: str -- location ID.
        
        Special formatting of alternate name. 
        Extends the superclass method.
        """
        locationMapping = super()._get_locationMapping(lcId)
        if self.novel.locations[lcId].aka:
            locationMapping['AKA'] = f' ("{self.novel.locations[lcId].aka}")'
        return locationMapping
