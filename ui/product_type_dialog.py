
from __future__ import annotations

from copy import deepcopy
from typing import Any
import uuid

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from services.product_type.service import ProductTypeService
from ui.dialogs.base import BaseThemedDialog
from ui.messages import Buttons, DialogTitles
from ui.window_policy import lock_window_size
from ui.theme import THEME
from ui.widget_factory import make_dialog_button


def _new_node_id() -> str:
    return uuid.uuid4().hex[:12]


class ProductTypeDialog(BaseThemedDialog):
    def __init__(self, project_root: str, parent=None):
        super().__init__(DialogTitles.PRODUCT_TYPE_MANAGE, parent)
        self.project_root = project_root
        self.service = ProductTypeService(project_root)
        self.nodes = deepcopy(self.service.get_tree())
        self.resize(THEME.product_type_dialog_width, THEME.product_type_dialog_height)

        info = QLabel('제품 타입을 계층으로 등록합니다. 예: 의류 > 상의 > 반팔', self)
        info.setWordWrap(True)
        self.body.addWidget(info)

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self._rename_selected)
        self.body.addWidget(self.tree, 1)

        tool_row = QHBoxLayout()
        tool_row.setContentsMargins(0, 0, 0, 0)
        tool_row.setSpacing(THEME.row_spacing)
        self.btn_add_root = make_dialog_button('최상위 추가', self, role='secondary')
        self.btn_add_child = make_dialog_button('하위 추가', self, role='secondary')
        self.btn_rename = make_dialog_button('이름 변경', self, role='secondary')
        self.btn_delete = make_dialog_button('삭제', self, role='secondary')
        for btn in (self.btn_add_root, self.btn_add_child, self.btn_rename, self.btn_delete):
            tool_row.addWidget(btn)
        self.body.addLayout(tool_row)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(THEME.row_spacing)
        action_row.addStretch(1)
        self.btn_save = make_dialog_button(Buttons.SAVE, self, role='confirm')
        self.btn_close = make_dialog_button(Buttons.CLOSE, self, role='close')
        action_row.addWidget(self.btn_save)
        action_row.addWidget(self.btn_close)
        action_row.addStretch(1)
        self.body.addLayout(action_row)

        self.btn_add_root.clicked.connect(self._add_root)
        self.btn_add_child.clicked.connect(self._add_child)
        self.btn_rename.clicked.connect(self._rename_selected)
        self.btn_delete.clicked.connect(self._delete_selected)
        self.btn_save.clicked.connect(self._save)
        self.btn_close.clicked.connect(self.reject)

        self._rebuild_tree()
        lock_window_size(self, width=THEME.product_type_dialog_width, height=THEME.product_type_dialog_height)

    def _prompt_name(self, title: str, current: str = '') -> str:
        value, ok = QInputDialog.getText(self, title, '이름', text=current)
        return value.strip() if ok else ''

    def _selected_item(self) -> QTreeWidgetItem | None:
        items = self.tree.selectedItems()
        return items[0] if items else None

    def _selected_path_ids(self) -> list[str]:
        item = self._selected_item()
        if item is None:
            return []
        return [str(v) for v in (item.data(0, Qt.UserRole + 1) or []) if str(v)]

    def _find_node_by_path_ids(self, path_ids: list[str]) -> dict[str, Any] | None:
        if not path_ids:
            return None
        nodes = self.nodes
        current = None
        for target_id in path_ids:
            current = next((node for node in nodes if str(node.get('id') or '') == target_id), None)
            if current is None:
                return None
            nodes = list(current.get('children') or [])
        return current

    def _add_root(self):
        name = self._prompt_name('최상위 타입 추가')
        if not name:
            return
        root = {'id': _new_node_id(), 'name': name, 'children': []}
        self.nodes.append(root)
        self._rebuild_tree(select_path_ids=[str(root.get('id') or '')])

    def _add_child(self):
        path_ids = self._selected_path_ids()
        if not path_ids:
            return
        name = self._prompt_name('하위 타입 추가')
        if not name:
            return
        node = self._find_node_by_path_ids(path_ids)
        if node is None:
            return
        child = {'id': _new_node_id(), 'name': name, 'children': []}
        node.setdefault('children', []).append(child)
        self._rebuild_tree(select_path_ids=path_ids + [str(child.get('id') or '')])

    def _rename_selected(self, *_args):
        path_ids = self._selected_path_ids()
        if not path_ids:
            return
        node = self._find_node_by_path_ids(path_ids)
        if node is None:
            return
        name = self._prompt_name('타입 이름 변경', current=str(node.get('name') or ''))
        if not name:
            return
        node['name'] = name
        self._rebuild_tree(select_path_ids=path_ids)

    def _delete_selected(self):
        path_ids = self._selected_path_ids()
        if not path_ids:
            return
        if self._delete_node_by_path_ids(self.nodes, path_ids):
            self._rebuild_tree()

    def _delete_node_by_path_ids(self, nodes, path_ids: list[str]) -> bool:
        if not path_ids:
            return False
        target_id = path_ids[0]
        for idx, node in enumerate(list(nodes)):
            if str(node.get('id') or '') != target_id:
                continue
            if len(path_ids) == 1:
                del nodes[idx]
                return True
            return self._delete_node_by_path_ids(node.get('children', []), path_ids[1:])
        return False

    def _rebuild_tree(self, *, select_path: list[str] | None = None, select_path_ids: list[str] | None = None, select_item=None):
        self.tree.clear()
        first = None
        def build(parent_item, nodes, path_prefix=None, id_prefix=None):
            nonlocal first
            path_prefix = list(path_prefix or [])
            id_prefix = list(id_prefix or [])
            for node in nodes:
                item = QTreeWidgetItem([str(node.get('name') or '')])
                item.setData(0, Qt.UserRole, str(node.get('id') or ''))
                current_ids = id_prefix + [str(node.get('id') or '')]
                item.setData(0, Qt.UserRole + 1, current_ids)
                if parent_item is None:
                    self.tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)
                if first is None:
                    first = item
                path = path_prefix + [str(node.get('name') or '')]
                build(item, list(node.get('children') or []), path, current_ids)
                if (select_item is not None and str(node.get('id') or '') == str(select_item.get('id') or '')) or (select_path and path == select_path) or (select_path_ids and current_ids == select_path_ids):
                    self.tree.setCurrentItem(item)
        build(None, self.nodes)
        self.tree.expandAll()
        if self.tree.currentItem() is None and first is not None:
            self.tree.setCurrentItem(first)

    def _save(self):
        self.service.save_tree(self.nodes)
        self.accept()
