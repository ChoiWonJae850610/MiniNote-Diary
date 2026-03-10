from __future__ import annotations

import os

from PySide6.QtWidgets import QWidget

from ui.partner_dialog import PartnerDialog



def project_root_from_widget(widget: QWidget | None) -> str:
    current = widget
    while current is not None:
        path = getattr(current, 'project_root', None)
        if isinstance(path, str) and path:
            return path
        current = current.parentWidget()
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))



def open_partner_management(widget: QWidget | None) -> int:
    dialog = PartnerDialog(project_root=project_root_from_widget(widget), parent=widget)
    return dialog.exec()
