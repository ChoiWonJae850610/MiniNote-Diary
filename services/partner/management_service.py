from __future__ import annotations

from typing import Iterable

from services.partner.repository import PartnerRecord, PartnerRepository


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

    def create_partner(self, partners: list[PartnerRecord], record: PartnerRecord) -> PartnerRecord:
        created = PartnerRecord(
            id=self.next_partner_id(partners),
            name=record.name,
            owner=record.owner,
            phone=record.phone,
            address=record.address,
            memo=record.memo,
            types=list(record.types or []),
        )
        next_rows = list(partners)
        next_rows.append(created)
        self.save_partners(next_rows)
        return created

    def update_partner(self, partners: list[PartnerRecord], partner_id: str, record: PartnerRecord) -> PartnerRecord:
        updated = PartnerRecord(
            id=partner_id,
            name=record.name,
            owner=record.owner,
            phone=record.phone,
            address=record.address,
            memo=record.memo,
            types=list(record.types or []),
        )
        next_rows: list[PartnerRecord] = []
        replaced = False
        for item in partners:
            if item.id == partner_id:
                next_rows.append(updated)
                replaced = True
            else:
                next_rows.append(item)
        if not replaced:
            next_rows.append(updated)
        self.save_partners(next_rows)
        return updated

    def delete_partner(self, partners: list[PartnerRecord], partner_id: str) -> list[PartnerRecord]:
        next_rows = [row for row in partners if row.id != partner_id]
        self.save_partners(next_rows)
        return next_rows

    def prune_partners_to_active_types(self, partners: list[PartnerRecord]) -> bool:
        active_types = set(self.list_types())
        changed = False
        for row in partners:
            original = list(row.types or [])
            row.types = [name for name in original if name in active_types]
            if row.types != original:
                changed = True
        if changed:
            self.save_partners(partners)
        return changed
