from __future__ import annotations

from typing import Iterable

from services.partner_repository import PartnerRecord, PartnerRepository


class PartnerManagementService:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.repository = PartnerRepository(project_root)

    def list_types(self) -> list[str]:
        return self.repository.load_types()

    def save_types(self, types: Iterable[str]) -> None:
        self.repository.save_types(types)

    def list_partners(self) -> list[PartnerRecord]:
        return self.repository.load_partners()

    def save_partners(self, partners: list[PartnerRecord]) -> None:
        self.repository.save_partners(partners)

    def next_partner_id(self, partners: list[PartnerRecord]) -> str:
        return self.repository.next_partner_id(partners)
