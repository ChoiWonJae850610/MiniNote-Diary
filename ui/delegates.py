import json
import os
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QStyledItemDelegate, QComboBox, QLineEdit
)


def get_project_root() -> str:
    # ui/ 기준 상위 폴더가 프로젝트 루트   입니다.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_units(project_root: str) -> List[Dict[str, str]]:
    """
    db/units.json 구조:
    {
      "units": [{"unit":"m","label":"미터"}, ...]
    }
    """
    path = os.path.join(project_root, "db", "units.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        units = data.get("units", [])
        if isinstance(units, list):
            # normalize
            out = []
            for u in units:
                if not isinstance(u, dict):
                    continue
                unit = str(u.get("unit", "")).strip()
                label = str(u.get("label", "")).strip()
                if unit or label:
                    out.append({"unit": unit, "label": label})
            return out
    except Exception:
        pass
    return []


class UnitComboDelegate(QStyledItemDelegate):
    """
    표시: label(있으면) / 없으면 unit
    저장되는 값: unit (콤보 itemData)
    """
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        self.project_root = project_root

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.setEditable(False)
        combo.setInsertPolicy(QComboBox.NoInsert)

        units = load_units(self.project_root)
        for u in units:
            unit = u.get("unit", "").strip()
            label = u.get("label", "").strip()
            if not unit and not label:
                continue
            display = label if label else unit
            # itemData = unit(우선) / unit이 비면 display를 저장
            combo.addItem(display, unit if unit else display)

        return combo

    def setEditorData(self, editor, index):
        current_val = (index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or "").strip()
        # itemData(unit) 기준으로 매칭
        for i in range(editor.count()):
            if str(editor.itemData(i) or "") == current_val:
                editor.setCurrentIndex(i)
                return
        # 못 찾으면 display 텍스트로도 매칭 시도
        for i in range(editor.count()):
            if editor.itemText(i) == current_val:
                editor.setCurrentIndex(i)
                return
        # 기본 0
        if editor.count() > 0:
            editor.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        unit_val = str(editor.currentData() or "").strip()
        model.setData(index, unit_val, Qt.EditRole)


class NumericDelegate(QStyledItemDelegate):
    """
    숫자만 입력(실수). 빈 값 허용.
    """
    def __init__(self, decimals: int = 4, parent=None):
        super().__init__(parent)
        self.decimals = decimals

    def createEditor(self, parent, option, index):
        le = QLineEdit(parent)
        v = QDoubleValidator(0.0, 1e15, self.decimals, le)
        v.setNotation(QDoubleValidator.StandardNotation)
        le.setValidator(v)
        le.setPlaceholderText("숫자")
        le.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return le

    def setEditorData(self, editor, index):
        editor.setText(str(index.data(Qt.EditRole) or index.data(Qt.DisplayRole) or ""))

    def setModelData(self, editor, model, index):
        text = editor.text().strip()
        model.setData(index, text, Qt.EditRole)