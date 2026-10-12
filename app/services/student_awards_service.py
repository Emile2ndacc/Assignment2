from __future__ import annotations

from datetime import date

from app.models.award import Award
from app.models.redemption import Redemption
from app.models.student_appeal import StudentAppeal
from app.models.user import User
from app.repositories.student_awards import (
    AwardRepository,
    HoursLogRepository,
    RedemptionRepository,
    StudentAppealRepository,
)


class StudentAwardsService:
    AWARD_IMAGES = {
        "Movie Ticket": "img/rewards/movie-ticket.svg",
        "Gift Card": "img/rewards/gift-card.svg",
        "School Hoodie": "img/rewards/school-hoodie.svg",
    }

    def __init__(self, db):
        self.db = db
        self.award_repo = AwardRepository(db)
        self.hours_log_repo = HoursLogRepository(db)
        self.redemption_repo = RedemptionRepository(db)
        self.appeal_repo = StudentAppealRepository(db)

    def seed_awards(self) -> list[Award]:
        return self.award_repo.seed_defaults()

    def get_awards(self) -> list[Award]:
        return self.award_repo.list_catalog_awards()

    def log_hours(self, student_id: int, activity_description: str, hours: float, log_date: date | None = None) -> object:
        if not activity_description or not activity_description.strip():
            raise ValueError("Activity description is required")
        hours_value = float(hours)
        if hours_value <= 0:
            raise ValueError("Volunteer hours must be greater than zero")
        return self.hours_log_repo.create(
            student_id=student_id,
            activity_description=activity_description,
            hours=hours_value,
            log_date=log_date or date.today(),
        )

    def get_student_summary(self, user: User) -> dict:
        total_hours = self.hours_log_repo.get_total_hours(user.id)
        leaderboard = self.get_leaderboard()
        rank = next((entry["rank"] for entry in leaderboard if entry["id"] == user.id), len(leaderboard) + 1)
        redemptions = self.redemption_repo.get_by_student(user.id)
        pending_redemptions = sum(1 for redemption in redemptions if redemption.approval_status == "pending")
        approved = sum(1 for redemption in redemptions if redemption.approval_status == "approved")
        return {
            "total_hours": total_hours,
            "rank": rank,
            "pending_redemptions": pending_redemptions,
            "approved_redemptions": approved,
            "is_student": user.role == "regular_user",
        }

    def get_recent_logs(self, student_id: int) -> list[object]:
        return self.hours_log_repo.get_recent_for_student(student_id)

    def get_award_catalog(self, student_id: int) -> list[dict]:
        awards = self.award_repo.list_catalog_awards()
        total_hours = self.hours_log_repo.get_total_hours(student_id)
        catalog = []
        for award in awards:
            latest = self.redemption_repo.get_latest_for_student_and_award(student_id, award.id)
            if latest is None:
                status = "available" if total_hours >= award.milestone_hours else "locked"
            elif latest.approval_status == "approved":
                status = "approved"
            elif latest.approval_status == "rejected":
                status = "rejected"
            else:
                status = "pending"
            catalog.append({
                "id": award.id,
                "name": award.name,
                "description": award.description or "",
                "image_path": self.AWARD_IMAGES[award.name],
                "milestone_hours": award.milestone_hours,
                "eligible": total_hours >= award.milestone_hours,
                "status": status,
                "can_redeem": total_hours >= award.milestone_hours and status not in {"pending", "approved"},
            })
        return catalog

    def get_student_redemptions(self, student_id: int) -> list[Redemption]:
        return self.redemption_repo.get_by_student(student_id)

    def get_student_appeals(self, student_id: int) -> dict[int, StudentAppeal]:
        return {
            appeal.redemption_id: appeal
            for appeal in self.appeal_repo.get_for_student(student_id)
        }

    def get_personal_awards(self, student_id: int) -> list[Redemption]:
        return [
            redemption
            for redemption in self.redemption_repo.get_by_student(student_id)
            if redemption.approval_status == "approved"
        ]

    def get_leaderboard(self) -> list[dict]:
        return self.hours_log_repo.get_leaderboard()

    def request_redemption(self, student_id: int, award_id: int, notes: str | None = None) -> Redemption:
        award = self.award_repo.get_catalog_award_by_id(award_id)
        if award is None:
            raise ValueError("Award not found")

        total_hours = self.hours_log_repo.get_total_hours(student_id)
        if total_hours < award.milestone_hours:
            remaining = max(award.milestone_hours - total_hours, 0.0)
            raise ValueError(f"You need {remaining:.1f} more volunteer hours to redeem this award.")

        latest = self.redemption_repo.get_latest_for_student_and_award(student_id, award_id)
        if latest and latest.approval_status == "pending":
            raise ValueError("A pending redemption for this award already exists.")
        if latest and latest.approval_status == "approved":
            raise ValueError("This award has already been redeemed and approved.")

        return self.redemption_repo.create(student_id, award_id, notes)

    def get_pending_redemptions(self) -> list[dict]:
        redemptions = self.redemption_repo.get_pending()
        details = []
        for redemption in redemptions:
            student = self.db.get(User, redemption.student_id)
            award = self.db.get(Award, redemption.award_id)
            details.append({
                "id": redemption.id,
                "student": student,
                "award": award,
                "notes": redemption.notes,
                "redeemed_date": redemption.redeemed_date,
            })
        return details

    def resolve_redemption(self, redemption_id: int, admin_id: int, decision: str) -> Redemption:
        status = decision.lower()
        if status not in {"approved", "rejected"}:
            raise ValueError("Decision must be approved or rejected")
        redemption = self.redemption_repo.get_by_id(redemption_id)
        if redemption is None:
            raise ValueError("Redemption not found")
        if redemption.approval_status != "pending":
            raise ValueError("This redemption has already been reviewed.")
        return self.redemption_repo.update_status(redemption_id, status, admin_id)

    def submit_appeal(self, student_id: int, redemption_id: int, reason: str) -> StudentAppeal:
        cleaned_reason = reason.strip()
        if not cleaned_reason:
            raise ValueError("Please explain why you are appealing this decision.")
        redemption = self.redemption_repo.get_by_id(redemption_id)
        if redemption is None or redemption.student_id != student_id:
            raise ValueError("That award request was not found for your account.")
        if redemption.approval_status != "rejected":
            raise ValueError("Only denied award requests can be appealed.")
        if self.appeal_repo.get_by_redemption(redemption_id) is not None:
            raise ValueError("An appeal has already been submitted for this award request.")
        return self.appeal_repo.submit(redemption_id, cleaned_reason)

    def get_pending_appeals(self) -> list[dict[str, object]]:
        return self.appeal_repo.get_pending()

    def resolve_appeal(
        self,
        appeal_id: int,
        admin_id: int,
        decision: str,
        admin_notes: str | None = None,
    ) -> StudentAppeal:
        status = decision.lower()
        if status not in {"approved", "rejected"}:
            raise ValueError("Decision must be approved or rejected")
        return self.appeal_repo.resolve(appeal_id, admin_id, status, admin_notes)
