"""Verification queue for missing accounts."""
from datetime import datetime
from typing import Optional

from instagram_audit.core import AccountIdentity, MissingAccount, VerificationStatus
from instagram_audit.storage import VerificationDAO


class VerificationQueue:
    """Manages the verification queue for missing accounts."""

    def __init__(self, dao: VerificationDAO):
        self.dao = dao

    def add_missing_account(
        self,
        account: AccountIdentity,
        last_seen: datetime,
        first_missing: datetime,
    ) -> int:
        """Add a missing account to the queue."""
        missing = MissingAccount(
            account=account,
            last_seen=last_seen,
            first_missing=first_missing,
            verification_status=VerificationStatus.PENDING,
        )
        return self.dao.add_to_queue(missing)

    def mark_blocked(self, queue_id: int, notes: Optional[str] = None) -> None:
        """Mark account as blocked."""
        self.dao.update_status(queue_id, VerificationStatus.BLOCKED, notes=notes)

    def mark_deactivated(self, queue_id: int, notes: Optional[str] = None) -> None:
        """Mark account as deactivated."""
        self.dao.update_status(queue_id, VerificationStatus.DEACTIVATED, notes=notes)

    def mark_renamed(
        self, queue_id: int, new_username: str, notes: Optional[str] = None
    ) -> None:
        """Mark account as renamed with new username."""
        self.dao.update_status(
            queue_id, VerificationStatus.RENAMED, new_username=new_username, notes=notes
        )

    def mark_unfollowed(self, queue_id: int, notes: Optional[str] = None) -> None:
        """Mark account as unfollowed (intentional unfollow)."""
        self.dao.update_status(queue_id, VerificationStatus.UNFOLLOWED, notes=notes)

    def mark_unknown(self, queue_id: int, notes: Optional[str] = None) -> None:
        """Mark account status as unknown."""
        self.dao.update_status(queue_id, VerificationStatus.UNKNOWN, notes=notes)

    def get_pending(self) -> list[tuple[int, MissingAccount]]:
        """Get all pending verifications."""
        return self.dao.get_pending()

    def process_interactively(self) -> None:
        """Interactively process pending verifications."""
        pending = self.get_pending()

        if not pending:
            print("No pending verifications.")
            return

        print(f"\n{len(pending)} accounts need verification:\n")

        for queue_id, missing in pending:
            print(f"Account: @{missing.account.username}")
            print(f"  PK: {missing.account.pk}")
            if missing.account.full_name:
                print(f"  Name: {missing.account.full_name}")
            print(f"  Last seen: {missing.last_seen.strftime('%Y-%m-%d')}")
            print(f"  First missing: {missing.first_missing.strftime('%Y-%m-%d')}")
            print()

            print("What happened to this account?")
            print("  1) Blocked you")
            print("  2) Deactivated/deleted account")
            print("  3) Renamed (changed username)")
            print("  4) You unfollowed them")
            print("  5) Unknown")
            print("  s) Skip for now")
            print()

            choice = input("Choice: ").strip().lower()

            if choice == "1":
                notes = input("Notes (optional): ").strip() or None
                self.mark_blocked(queue_id, notes)
                print("Marked as blocked.\n")

            elif choice == "2":
                notes = input("Notes (optional): ").strip() or None
                self.mark_deactivated(queue_id, notes)
                print("Marked as deactivated.\n")

            elif choice == "3":
                new_username = input("New username: ").strip()
                if new_username:
                    notes = input("Notes (optional): ").strip() or None
                    self.mark_renamed(queue_id, new_username, notes)
                    print(f"Marked as renamed to @{new_username}.\n")
                else:
                    print("Skipped (no username provided).\n")

            elif choice == "4":
                notes = input("Notes (optional): ").strip() or None
                self.mark_unfollowed(queue_id, notes)
                print("Marked as unfollowed.\n")

            elif choice == "5":
                notes = input("Notes (optional): ").strip() or None
                self.mark_unknown(queue_id, notes)
                print("Marked as unknown.\n")

            elif choice == "s":
                print("Skipped.\n")

            else:
                print("Invalid choice, skipping.\n")

        print("Verification complete!")
