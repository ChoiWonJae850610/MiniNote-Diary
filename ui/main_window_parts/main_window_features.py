from __future__ import annotations

from ui.feature_page import FeaturePageConfig, FeatureSection
from ui.messages import FeatureConfigTexts


def _sections(items: tuple[tuple[str, tuple[str, ...]], ...]) -> list[FeatureSection]:
    return [FeatureSection(title, lines) for title, lines in items]


def build_feature_page_configs() -> list[FeaturePageConfig]:
    return [
        FeaturePageConfig(
            key='receipt',
            title=FeatureConfigTexts.RECEIPT_TITLE,
            subtitle=FeatureConfigTexts.RECEIPT_SUBTITLE,
            left_title=FeatureConfigTexts.RECEIPT_LEFT_TITLE,
            left_hint=FeatureConfigTexts.RECEIPT_LEFT_HINT,
            list_items=FeatureConfigTexts.RECEIPT_LIST_ITEMS,
            summary_items=FeatureConfigTexts.RECEIPT_SUMMARY_ITEMS,
            sections=_sections(FeatureConfigTexts.RECEIPT_SECTIONS),
            primary_button_text=FeatureConfigTexts.RECEIPT_PRIMARY,
            secondary_button_text=FeatureConfigTexts.RECEIPT_SECONDARY,
            helper_text=FeatureConfigTexts.RECEIPT_HELPER,
        ),
        FeaturePageConfig(
            key='complete',
            title=FeatureConfigTexts.COMPLETE_TITLE,
            subtitle=FeatureConfigTexts.COMPLETE_SUBTITLE,
            left_title=FeatureConfigTexts.COMPLETE_LEFT_TITLE,
            left_hint=FeatureConfigTexts.COMPLETE_LEFT_HINT,
            list_items=FeatureConfigTexts.COMPLETE_LIST_ITEMS,
            summary_items=FeatureConfigTexts.COMPLETE_SUMMARY_ITEMS,
            sections=_sections(FeatureConfigTexts.COMPLETE_SECTIONS),
            primary_button_text=FeatureConfigTexts.COMPLETE_PRIMARY,
            secondary_button_text=FeatureConfigTexts.COMPLETE_SECONDARY,
            helper_text=FeatureConfigTexts.COMPLETE_HELPER,
        ),
        FeaturePageConfig(
            key='sale',
            title=FeatureConfigTexts.SALE_TITLE,
            subtitle=FeatureConfigTexts.SALE_SUBTITLE,
            left_title=FeatureConfigTexts.SALE_LEFT_TITLE,
            left_hint=FeatureConfigTexts.SALE_LEFT_HINT,
            list_items=FeatureConfigTexts.SALE_LIST_ITEMS,
            summary_items=FeatureConfigTexts.SALE_SUMMARY_ITEMS,
            sections=_sections(FeatureConfigTexts.SALE_SECTIONS),
            primary_button_text=FeatureConfigTexts.SALE_PRIMARY,
            secondary_button_text=FeatureConfigTexts.SALE_SECONDARY,
            helper_text=FeatureConfigTexts.SALE_HELPER,
        ),
        FeaturePageConfig(
            key='inventory',
            title=FeatureConfigTexts.INVENTORY_TITLE,
            subtitle=FeatureConfigTexts.INVENTORY_SUBTITLE,
            left_title=FeatureConfigTexts.INVENTORY_LEFT_TITLE,
            left_hint=FeatureConfigTexts.INVENTORY_LEFT_HINT,
            list_items=FeatureConfigTexts.INVENTORY_LIST_ITEMS,
            summary_items=FeatureConfigTexts.INVENTORY_SUMMARY_ITEMS,
            sections=_sections(FeatureConfigTexts.INVENTORY_SECTIONS),
            primary_button_text=FeatureConfigTexts.INVENTORY_PRIMARY,
            secondary_button_text=FeatureConfigTexts.INVENTORY_SECONDARY,
            helper_text=FeatureConfigTexts.INVENTORY_HELPER,
        ),
        FeaturePageConfig(
            key='partner',
            title=FeatureConfigTexts.PARTNER_TITLE,
            subtitle=FeatureConfigTexts.PARTNER_SUBTITLE,
            left_title=FeatureConfigTexts.PARTNER_LEFT_TITLE,
            left_hint=FeatureConfigTexts.PARTNER_LEFT_HINT,
            list_items=FeatureConfigTexts.PARTNER_LIST_ITEMS,
            summary_items=FeatureConfigTexts.PARTNER_SUMMARY_ITEMS,
            sections=_sections(FeatureConfigTexts.PARTNER_SECTIONS),
            primary_button_text=FeatureConfigTexts.PARTNER_PRIMARY,
            secondary_button_text=FeatureConfigTexts.PARTNER_SECONDARY,
            helper_text=FeatureConfigTexts.PARTNER_HELPER,
        ),
    ]
