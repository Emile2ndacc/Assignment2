from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.models.award import Award
from app.models.hours_log import HoursLog
from app.models.redemption import Redemption
from app.models.student_appeal import StudentAppeal
from app.models.user import User


class AwardRepository:
    CATALOG_AWARDS = (
        ("Movie Ticket", 20.0),
        ("Gift Card", 50.0),
        ("School Hoodie", 75.0),
    )

    def __init__(self, db: Session):
        self.db = db

    def list_awards(self) -> list[Award]:
        return self.db.exec(select(Award).order_by(Award.milestone_hours)).all()

    def list_catalog_awards(self) -> list[Award]:
        catalog_names = [name for name, _ in self.CATALOG_AWARDS]
        return self.db.exec(
            select(Award)
            .where(Award.name.in_(catalog_names))
            .order_by(Award.milestone_hours)
        ).all()

    def get_catalog_award_by_id(self, award_id: int) -> Award | None:
        catalog_names = [name for name, _ in self.CATALOG_AWARDS]
        return self.db.exec(
            select(Award).where(
                Award.id == award_id,
                Award.name.in_(catalog_names),
            )
        ).first()

    def get_by_id(self, award_id: int) -> Award | None:
        return self.db.get(Award, award_id)

    def seed_defaults(self) -> list[Award]:
        existing_names = {award.name for award in self.list_awards()}
        defaults = [
            Award(name=name, milestone_hours=milestone_hours)
            for name, milestone_hours in self.CATALOG_AWARDS
            if name not in existing_names
        ]
        if defaults:
            self.db.add_all(defaults)
            self.db.commit()

        return self.list_catalog_awards()


class HoursLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, student_id: int, activity_description: str, hours: float, log_date: date) -> HoursLog:
        log = HoursLog(
            student_id=student_id,
            activity_description=activity_description.strip(),
            hours=float(hours),
            log_date=log_date,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_recent_for_student(self, student_id: int, limit: int = 6) -> list[HoursLog]:
        return self.db.exec(
            select(HoursLog)
            .where(HoursLog.student_id == student_id)
            .order_by(HoursLog.log_date.desc(), HoursLog.id.desc())
            .limit(limit)
        ).all()

    def get_total_hours(self, student_id: int) -> float:
        total = self.db.exec(
            select(func.coalesce(func.sum(HoursLog.hours), 0.0)).where(HoursLog.student_id == student_id)
        ).one()
        return float(total or 0.0)

    def get_leaderboard(self) -> list[dict[str, Any]]:
        rows = self.db.exec(
            select(
                User.id,
                User.username,
                func.coalesce(func.sum(HoursLog.hours), 0.0).label("total_hours"),
            )
            .select_from(User)
            .outerjoin(HoursLog, HoursLog.student_id == User.id)
            .where(User.role == "regular_user")
            .group_by(User.id, User.username)
            .order_by(func.coalesce(func.sum(HoursLog.hours), 0.0).desc(), User.username)
        ).all()

        leaderboard: list[dict[str, Any]] = []
        for index, row in enumerate(rows, start=1):
            leaderboard.append({
                "id": row[0],
                "username": row[1],
                "total_hours": float(row[2] or 0.0),
                "rank": index,
            })
        return leaderboard


class RedemptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, student_id: int, award_id: int, notes: str | None = None) -> Redemption:
        redemption = Redemption(
            student_id=student_id,
            award_id=award_id,
            redeemed_date=date.today(),
            approval_status="pending",
            notes=notes.strip() if notes else None,
        )
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        return redemption

    def get_pending(self) -> list[Redemption]:
        return self.db.exec(
            select(Redemption)
            .where(Redemption.approval_status == "pending")
            .order_by(Redemption.redeemed_date.desc(), Redemption.id.desc())
        ).all()

    def get_by_student(self, student_id: int) -> list[Redemption]:
        return self.db.exec(
            select(Redemption)
            .where(Redemption.student_id == student_id)
            .order_by(Redemption.redeemed_date.desc(), Redemption.id.desc())
        ).all()

    def get_by_id(self, redemption_id: int) -> Redemption | None:
        return self.db.get(Redemption, redemption_id)

    def get_latest_for_student_and_award(self, student_id: int, award_id: int) -> Redemption | None:
        return self.db.exec(
            select(Redemption)
            .where(Redemption.student_id == student_id, Redemption.award_id == award_id)
            .order_by(Redemption.id.desc())
            .limit(1)
        ).first()

    def update_status(self, redemption_id: int, approval_status: str, admin_id: int | None = None) -> Redemption:
        redemption = self.db.get(Redemption, redemption_id)
        if redemption is None:
            raise ValueError("Redemption not found")
        if redemption.approval_status != "pending":
            raise ValueError("This redemption has already been reviewed.")
        redemption.approval_status = approval_status
        redemption.approved_by_admin_id = admin_id
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        return redemption


class StudentAppealRepository:
    def __init__(self, db: Session):
        self.db = db

    def submit(self, redemption_id: int, reason: str) -> StudentAppeal:
        redemption = self.db.get(Redemption, redemption_id)
        if redemption is None:
            raise ValueError("Redemption not found")
        appeal = StudentAppeal(
            redemption_id=redemption.id,
            student_id=redemption.student_id,
            award_id=redemption.award_id,
            reason=reason.strip(),
            status="pending",
        )
        self.db.add(appeal)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            if self.get_by_redemption(redemption_id) is not None:
                raise ValueError(
                    "An appeal has already been submitted for this award request."
                ) from exc
            raise
        self.db.refresh(appeal)
        return appeal

    def get_by_redemption(self, redemption_id: int) -> StudentAppeal | None:
        return self.db.exec(
            select(StudentAppeal).where(StudentAppeal.redemption_id == redemption_id)
        ).first()

    def get_by_id(self, appeal_id: int) -> StudentAppeal | None:
        return self.db.get(StudentAppeal, appeal_id)

    def get_for_student(self, student_id: int) -> list[StudentAppeal]:
        return self.db.exec(
            select(StudentAppeal)
            .where(StudentAppeal.student_id == student_id)
            .order_by(StudentAppeal.appeal_date.desc(), StudentAppeal.id.desc())
        ).all()

    def get_pending(self) -> list[dict[str, object]]:
        rows = self.db.exec(
            select(StudentAppeal, Redemption, User, Award)
            .join(Redemption, StudentAppeal.redemption_id == Redemption.id)
            .join(User, StudentAppeal.student_id == User.id)
            .join(Award, StudentAppeal.award_id == Award.id)
            .where(StudentAppeal.status == "pending")
            .order_by(StudentAppeal.appeal_date, StudentAppeal.id)
        ).all()
        return [
            {"appeal": appeal, "redemption": redemption, "student": student, "award": award}
            for appeal, redemption, student, award in rows
        ]

    def resolve(
        self,
        appeal_id: int,
        admin_id: int,
        status: str,
        admin_notes: str | None = None,
    ) -> StudentAppeal:
        appeal = self.db.get(StudentAppeal, appeal_id)
        if appeal is None:
            raise ValueError("Student appeal not found")
        if appeal.status != "pending":
            raise ValueError("This appeal has already been reviewed.")

        redemption = self.db.get(Redemption, appeal.redemption_id)
        if redemption is None:
            raise ValueError("The appealed redemption was not found")
        if redemption.approval_status != "rejected":
            raise ValueError("Only denied award requests can have an appeal decision.")

        appeal.status = status
        appeal.admin_id = admin_id
        appeal.admin_notes = admin_notes.strip() if admin_notes and admin_notes.strip() else None
        if status == "approved":
            redemption.approval_status = "approved"
            redemption.approved_by_admin_id = admin_id

        self.db.add(appeal)
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(appeal)
        return appeal
