from __future__ import annotations

from services.partner.repository import PartnerRecord, PartnerRepository
from services.partner.utils import (
    PARTNER_TYPE_DYEING,
    PARTNER_TYPE_FACTORY,
    PARTNER_TYPE_FABRIC,
    PARTNER_TYPE_FINISH,
    PARTNER_TYPE_OTHER,
    PARTNER_TYPE_TRIM,
)


class PartnerLookupService:
    _TYPE_ALIASES = {
        PARTNER_TYPE_FACTORY: {PARTNER_TYPE_FACTORY},
        PARTNER_TYPE_FABRIC: {PARTNER_TYPE_FABRIC},
        PARTNER_TYPE_TRIM: {PARTNER_TYPE_TRIM},
        PARTNER_TYPE_DYEING: {PARTNER_TYPE_DYEING, "나염"},
        PARTNER_TYPE_FINISH: {PARTNER_TYPE_FINISH},
    }

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.repository = PartnerRepository(project_root)

    def partners_for_type(self, partner_type: str) -> list[PartnerRecord]:
        partner_type = str(partner_type or '').strip()
        rows = self.repository.load_partners()
        if partner_type == PARTNER_TYPE_OTHER:
            # 작업지시서 상단 탭에서 전용 선택기가 있는 타입만 제외합니다.
            # 현재 기타 탭은 사용자 추가 타입과 기타/마감 계열까지 함께 보여줘야 합니다.
            excluded = {
                PARTNER_TYPE_FACTORY,
                PARTNER_TYPE_FABRIC,
                PARTNER_TYPE_TRIM,
                PARTNER_TYPE_DYEING,
                "나염",
            }
            return [
                row
                for row in rows
                if any(type_name not in excluded for type_name in (row.types or []))
                or PARTNER_TYPE_OTHER in (row.types or [])
            ]
        allowed = self._TYPE_ALIASES.get(partner_type, {partner_type})
        return [row for row in rows if any(type_name in allowed for type_name in (row.types or []))]
