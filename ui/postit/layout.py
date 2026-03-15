from __future__ import annotations

from ui.postit.layout_constants import *
from ui.postit.layout_helpers import embedded_tab_style, folder_tab_style, postit_section_height, postit_wrap_height
from ui.postit.layout_widgets import (
    FolderTabHeader,
    FooterSpacer,
    PostItSectionColumn,
    PostItTabButton,
    SectionContainer,
    SectionTitleBadge,
    make_postit_footer_spacer,
    make_postit_pager_host,
    make_postit_stack_host,
    make_static_postit_column,
)

POSTIT_WRAP_HEIGHT = postit_wrap_height(body_height=POSTIT_BODY_HEIGHT)
POSTIT_WRAP_HEIGHT_WITH_FOOTER = postit_wrap_height(body_height=POSTIT_BODY_HEIGHT, has_footer=True)
