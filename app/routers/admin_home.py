from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.services.student_awards_service import StudentAwardsService
from app.utilities.flash import flash

from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    service = StudentAwardsService(db)
    service.seed_awards()
    pending = service.get_pending_redemptions()
    leaderboard = service.get_leaderboard()
    awards = service.get_awards()
    return templates.TemplateResponse(
        request=request,
        name="admin-section.html",
        context={
            "user": user,
            "pending_redemptions": pending,
            "leaderboard": leaderboard,
            "award_count": len(awards),
            "page": "home",
        },
    )


@router.get("/admin/leaderboard", response_class=HTMLResponse)
async def admin_leaderboard_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    service = StudentAwardsService(db)
    return templates.TemplateResponse(
        request=request,
        name="admin-section.html",
        context={
            "user": user,
            "leaderboard": service.get_leaderboard(),
            "page": "leaderboard",
        },
    )


@router.get("/admin/redemptions", response_class=HTMLResponse)
async def admin_redemptions_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    service = StudentAwardsService(db)
    service.seed_awards()
    return templates.TemplateResponse(
        request=request,
        name="admin-section.html",
        context={
            "user": user,
            "pending_redemptions": service.get_pending_redemptions(),
            "page": "redemptions",
        },
    )


@router.post("/admin/redemptions/{redemption_id}/{decision}", response_class=HTMLResponse)
async def decide_redemption_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    redemption_id: int,
    decision: str,
):
    service = StudentAwardsService(db)
    try:
        service.resolve_redemption(redemption_id, user.id, decision)
        flash(request, f"Redemption {decision}.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(url=request.url_for("admin_redemptions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/admin/appeals", response_class=HTMLResponse)
async def admin_appeals_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    service = StudentAwardsService(db)
    return templates.TemplateResponse(
        request=request,
        name="admin_appeals.html",
        context={
            "user": user,
            "pending_appeals": service.get_pending_appeals(),
        },
    )


@router.post("/admin/appeals/{appeal_id}/{decision}", response_class=HTMLResponse)
async def decide_appeal_action(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    appeal_id: int,
    decision: str,
    admin_notes: str = Form(""),
):
    service = StudentAwardsService(db)
    try:
        service.resolve_appeal(appeal_id, user.id, decision, admin_notes or None)
        flash(request, f"Appeal {decision}.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(url=request.url_for("admin_appeals_view"), status_code=status.HTTP_303_SEE_OTHER)
