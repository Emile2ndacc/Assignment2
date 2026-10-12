from datetime import date

from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import StudentDep
from app.dependencies.session import SessionDep
from app.services.student_awards_service import StudentAwardsService
from app.utilities.flash import flash

from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: StudentDep,
    db: SessionDep,
):
    return _render_student_page(request, user, db, "home")


@router.get("/app/hours", response_class=HTMLResponse)
async def student_hours_view(request: Request, user: StudentDep, db: SessionDep):
    return _render_student_page(request, user, db, "hours")


@router.get("/app/leaderboard", response_class=HTMLResponse)
async def student_leaderboard_view(request: Request, user: StudentDep, db: SessionDep):
    return _render_student_page(request, user, db, "leaderboard")


@router.get("/app/awards", response_class=HTMLResponse)
async def student_awards_view(request: Request, user: StudentDep, db: SessionDep):
    return _render_student_page(request, user, db, "awards")


@router.get("/app/activity", response_class=HTMLResponse)
async def student_award_activity_view(request: Request, user: StudentDep, db: SessionDep):
    return _render_student_page(request, user, db, "activity")


@router.get("/app/personal-awards", response_class=HTMLResponse)
async def student_personal_awards_view(request: Request, user: StudentDep, db: SessionDep):
    return _render_student_page(request, user, db, "personal_awards")


def _render_student_page(request: Request, user, db, page: str):
    service = StudentAwardsService(db)
    service.seed_awards()
    summary = service.get_student_summary(user)
    leaderboard = service.get_leaderboard()
    logs = service.get_recent_logs(user.id)
    awards = service.get_award_catalog(user.id)
    redemptions = service.get_student_redemptions(user.id)
    appeals = service.get_student_appeals(user.id)
    personal_awards = service.get_personal_awards(user.id)

    return templates.TemplateResponse(
        request=request,
        name="student-section.html",
        context={
            "user": user,
            "summary": summary,
            "leaderboard": leaderboard,
            "logs": logs,
            "awards": awards,
            "redemptions": redemptions,
            "appeals": appeals,
            "personal_awards": personal_awards,
            "today": date.today().isoformat(),
            "page": page,
        },
    )


@router.post("/app/log-hours", response_class=HTMLResponse)
async def log_hours_action(
    request: Request,
    user: StudentDep,
    db: SessionDep,
    activity_description: str = Form(...),
    hours: float = Form(...),
    log_date: str = Form(...),
):
    service = StudentAwardsService(db)
    try:
        service.log_hours(
            student_id=user.id,
            activity_description=activity_description,
            hours=hours,
            log_date=date.fromisoformat(log_date),
        )
        flash(request, "Volunteer hours were added to your record.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(url=request.url_for("student_hours_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/redeem/{award_id}", response_class=HTMLResponse)
async def redeem_award_action(
    request: Request,
    user: StudentDep,
    db: SessionDep,
    award_id: int,
    notes: str = Form(""),
):
    service = StudentAwardsService(db)
    try:
        service.request_redemption(user.id, award_id, notes or None)
        flash(request, "Award redemption submitted for review.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(url=request.url_for("student_awards_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/redemptions/{redemption_id}/appeal", response_class=HTMLResponse)
async def submit_appeal_action(
    request: Request,
    user: StudentDep,
    db: SessionDep,
    redemption_id: int,
    reason: str = Form(...),
):
    service = StudentAwardsService(db)
    try:
        service.submit_appeal(user.id, redemption_id, reason)
        flash(request, "Your appeal was submitted for admin review.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("student_award_activity_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )