from __future__ import annotations

from dataclasses import dataclass

from ui.postit.layout import POSTIT_EXTERNAL_ROW_GAP_TIGHT, POSTIT_FOOTER_HEIGHT
from ui.postit.layout_helpers import build_postit_column_metrics
from ui.theme import THEME


@dataclass(frozen=True)
class WorkOrderLayoutMetrics:
    image_shell_frame_width: int

    @property
    def image_column_total_height(self) -> int:
        return (
            THEME.work_order_toolbar_panel_min_height
            + THEME.work_order_toolbar_to_image_overlap
            + (THEME.image_shell_margin * 2)
            + THEME.work_order_image_preview_min_height
            + (self.image_shell_frame_width * 2)
        )

    @property
    def postit_bar_total_height(self) -> int:
        return build_postit_column_metrics(
            has_footer=True,
            external_row_gap=POSTIT_EXTERNAL_ROW_GAP_TIGHT,
            external_row_height=POSTIT_FOOTER_HEIGHT,
        ).column_height

    @property
    def change_note_wrap_overhead(self) -> int:
        return build_postit_column_metrics(
            body_height=0,
            has_footer=True,
            external_row_gap=POSTIT_EXTERNAL_ROW_GAP_TIGHT,
            external_row_height=POSTIT_FOOTER_HEIGHT,
        ).column_height

    @property
    def available_change_note_wrap_height(self) -> int:
        return (
            self.image_column_total_height
            - THEME.work_order_column_spacing
            - self.postit_bar_total_height
            - THEME.work_order_bottom_safe_reserve
        )

    @property
    def target_change_note_wrap_height(self) -> int:
        return max(
            THEME.memo_min_height,
            self.available_change_note_wrap_height
            + THEME.work_order_bottom_match_adjust
            - THEME.work_order_change_note_visual_trim,
        )

    @property
    def change_note_body_height(self) -> int:
        body_height = self.target_change_note_wrap_height - self.change_note_wrap_overhead
        return max(
            THEME.memo_min_height,
            THEME.work_order_change_note_body_min_height,
            body_height,
        )


def build_work_order_layout_metrics(*, image_shell_frame_width: int) -> WorkOrderLayoutMetrics:
    return WorkOrderLayoutMetrics(image_shell_frame_width=image_shell_frame_width)


__all__ = ['WorkOrderLayoutMetrics', 'build_work_order_layout_metrics']
