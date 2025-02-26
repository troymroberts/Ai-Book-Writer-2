"""Provide a converter class for yWriter 7 universal import.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ff import YwCnvFf
from pywriter.converter.new_project_factory import NewProjectFactory
from pywriter.yw.yw7_file import Yw7File
from pywriter.odt_r.odt_r_proof import OdtRProof
from pywriter.odt_r.odt_r_manuscript import OdtRManuscript
from pywriter.odt_r.odt_r_notes import OdtRNotes
from pywriter.odt_r.odt_r_todo import OdtRTodo
from pywriter.odt_r.odt_r_scenedesc import OdtRSceneDesc
from pywriter.odt_r.odt_r_chapterdesc import OdtRChapterDesc
from pywriter.odt_r.odt_r_partdesc import OdtRPartDesc
from pywriter.odt_r.odt_r_characters import OdtRCharacters
from pywriter.odt_r.odt_r_locations import OdtRLocations
from pywriter.odt_r.odt_r_items import OdtRItems
from pywriter.ods_r.ods_r_scenelist import OdsRSceneList
from pywriter.ods_r.ods_r_charlist import OdsRCharList
from pywriter.ods_r.ods_r_loclist import OdsRLocList
from pywriter.ods_r.ods_r_itemlist import OdsRItemList


class Yw7Importer(YwCnvFf):
    """A converter for universal import.

    Support yWriter 7 projects and most of the Novel subclasses 
    that can be read or written by OpenOffice/LibreOffice.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES,
    EXPORT_TARGET_CLASSES, IMPORT_SOURCE_CLASSES, IMPORT_TARGET_CLASSES.

    Class constants:
        CREATE_SOURCE_CLASSES -- list of classes that - additional to HtmlImport
                        and HtmlOutline - can be exported to a new yWriter project.
    """
    EXPORT_SOURCE_CLASSES = [Yw7File]
    IMPORT_SOURCE_CLASSES = [OdtRProof,
                             OdtRManuscript,
                             OdtRSceneDesc,
                             OdtRChapterDesc,
                             OdtRPartDesc,
                             OdtRCharacters,
                             OdtRItems,
                             OdtRLocations,
                             OdtRNotes,
                             OdtRTodo,
                             OdsRCharList,
                             OdsRLocList,
                             OdsRItemList,
                             OdsRSceneList,
                             ]
    IMPORT_TARGET_CLASSES = [Yw7File]
    CREATE_SOURCE_CLASSES = []

    def __init__(self):
        """Change the newProjectFactory strategy.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
