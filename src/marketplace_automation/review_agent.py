from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from .io_utils import (
    markdown_table,
    parse_int,
    read_csv,
    write_csv,
    write_json,
    write_text,
)
from .models import ReviewRow
from .schemas import REVIEWS_REQUIRED, validate_rows


REPLY_COLUMNS = [
    "review_id",
    "date",
    "marketplace",
    "sku",
    "rating",
    "sentiment",
    "topic",
    "urgency",
    "needs_support_ticket",
    "manual_review_required",
    "approval_status",
    "compliance_flags",
    "reply_draft",
]

TICKET_COLUMNS = [
    "ticket_id",
    "review_id",
    "marketplace",
    "sku",
    "priority",
    "reason",
    "support_message",
]

TOPIC_RULES = {
    "side_effect": [
        "аллерг",
        "сыпь",
        "тошнит",
        "тошнота",
        "голова",
        "самочувств",
        "давление",
    ],
    "delivery": ["доставка", "курьер", "задерж", "поздно", "пункт выдачи"],
    "packaging": ["упаков", "помят", "разбит", "вскрыт", "банка", "крышка"],
    "taste": ["вкус", "запах", "горьк", "сладк", "кисл"],
    "effect": ["энерг", "эффект", "бодр", "сон", "устал"],
    "price": ["цена", "дорого", "скидк", "стоимость"],
}

NEGATIVE_WORDS = ["плохо", "ужас", "не помог", "нет эффекта", "разочар", "верните", "дорого"]
POSITIVE_WORDS = ["отлич", "понрав", "эффект", "работает", "удобно", "вкусно", "рекоменд"]

BANNED_MEDICAL_CLAIMS = [
    "лечит",
    "вылечит",
    "гарантирует эффект",
    "избавит от болезни",
    "ставит диагноз",
]


def classify_review(row: Mapping[str, Any]) -> dict[str, Any]:
    review = ReviewRow.from_mapping(row)
    rating = review.rating
    text = review.text.strip()
    lower = text.lower()
    topic = detect_topic(lower)
    sentiment = detect_sentiment(rating, lower)
    urgency = detect_urgency(rating=rating, topic=topic, sentiment=sentiment, text=lower)
    needs_ticket = (
        topic == "side_effect"
        or urgency == "high"
        or (topic in {"delivery", "packaging"} and sentiment != "positive")
    )
    reply = build_reply_draft(
        rating=rating,
        sentiment=sentiment,
        topic=topic,
        has_photo=review.has_photo,
    )
    compliance_flags = detect_compliance_flags(reply=reply, topic=topic)
    manual_review_required = (
        urgency in {"high", "medium"} or topic in {"side_effect", "effect"}
    )
    return {
        "review_id": review.review_id,
        "date": review.date,
        "marketplace": review.marketplace,
        "sku": review.sku,
        "rating": rating,
        "sentiment": sentiment,
        "topic": topic,
        "urgency": urgency,
        "needs_support_ticket": str(needs_ticket).lower(),
        "manual_review_required": str(manual_review_required).lower(),
        "approval_status": build_approval_status(
            topic=topic,
            urgency=urgency,
            manual_review_required=manual_review_required,
        ),
        "compliance_flags": "; ".join(compliance_flags),
        "reply_draft": reply,
    }


def detect_topic(text: str) -> str:
    for topic, keywords in TOPIC_RULES.items():
        if any(keyword in text for keyword in keywords):
            return topic
    return "general"


def detect_sentiment(rating: int, text: str) -> str:
    if rating <= 2 or any(word in text for word in NEGATIVE_WORDS):
        return "negative"
    if rating >= 4 or any(word in text for word in POSITIVE_WORDS):
        return "positive"
    return "neutral"


def detect_urgency(*, rating: int, topic: str, sentiment: str, text: str) -> str:
    if topic == "side_effect":
        return "high"
    if rating <= 2 and sentiment == "negative":
        return "high"
    if topic in {"delivery", "packaging"} and sentiment != "positive":
        return "medium"
    if rating == 3 or "нет эффекта" in text:
        return "medium"
    return "low"


def build_reply_draft(*, rating: int, sentiment: str, topic: str, has_photo: bool) -> str:
    if topic == "side_effect":
        reply = (
            "Здравствуйте! Спасибо, что сообщили о реакции. Нам важно разобраться в ситуации. "
            "Пожалуйста, прекратите прием при плохом самочувствии и обратитесь к врачу для индивидуальной консультации. "
            "Передадим информацию ответственному специалисту и проверим партию товара."
        )
    elif topic in {"delivery", "packaging"}:
        photo_part = "Фото поможет быстрее проверить случай. " if has_photo else ""
        reply = (
            "Здравствуйте! Спасибо за обратную связь. Нам жаль, что возникла проблема с доставкой или упаковкой. "
            f"{photo_part}Передадим информацию в поддержку маркетплейса и проверим отгрузку."
        )
    elif sentiment == "positive":
        reply = (
            "Здравствуйте! Спасибо за отзыв. Рады, что продукт вам подошел. "
            "Будем благодарны, если вы продолжите делиться впечатлениями после курса приема."
        )
    elif topic == "taste":
        reply = (
            "Здравствуйте! Спасибо за честный отзыв. Вкус может восприниматься индивидуально. "
            "Мы передадим комментарий команде продукта при следующей проверке формулы."
        )
    elif topic == "price":
        reply = (
            "Здравствуйте! Спасибо за обратную связь. Мы следим за балансом цены, состава и качества сырья. "
            "Рекомендуем отслеживать акции на карточке товара."
        )
    else:
        reply = (
            "Здравствуйте! Спасибо за отзыв. Мы передадим комментарий команде качества и учтем его в работе с карточкой товара."
        )
    return sanitize_reply(reply)


def sanitize_reply(reply: str) -> str:
    lowered = reply.lower()
    for claim in BANNED_MEDICAL_CLAIMS:
        if claim in lowered:
            raise ValueError(f"Unsafe medical claim in reply: {claim}")
    return reply


def detect_compliance_flags(*, reply: str, topic: str) -> list[str]:
    flags = ["no_banned_medical_claims_detected"]
    if topic in {"side_effect", "effect"}:
        flags.append("health_context")
    if topic == "side_effect" and "врач" in reply.lower():
        flags.append("doctor_referral_present")
    if topic == "side_effect" and "прекратите прием" in reply.lower():
        flags.append("stop_use_if_unwell")
    return flags


def build_approval_status(
    *,
    topic: str,
    urgency: str,
    manual_review_required: bool,
) -> str:
    if topic == "side_effect":
        return "quality_or_medical_review_required"
    if urgency == "high":
        return "support_lead_approval_required"
    if manual_review_required:
        return "operator_approval_required"
    return "standard_reply_candidate"


def build_support_ticket(classified: Mapping[str, Any]) -> dict[str, Any] | None:
    if classified.get("needs_support_ticket") != "true":
        return None
    review_id = str(classified.get("review_id", ""))
    topic = str(classified.get("topic", ""))
    priority = "P1" if classified.get("urgency") == "high" else "P2"
    reason = {
        "side_effect": "Возможная индивидуальная реакция. Передать ответственному за качество или профильному специалисту.",
        "delivery": "Проблема с доставкой. Подготовить обращение в поддержку маркетплейса.",
        "packaging": "Повреждение упаковки. Проверить фулфилмент и обращение в поддержку маркетплейса.",
    }.get(topic, "Негативный отзыв требует ручной проверки.")
    return {
        "ticket_id": f"T-{review_id}",
        "review_id": review_id,
        "marketplace": classified.get("marketplace", ""),
        "sku": classified.get("sku", ""),
        "priority": priority,
        "reason": reason,
        "support_message": (
            f"Проверьте отзыв {review_id} по SKU {classified.get('sku', '')}. "
            f"Тема: {topic}. Приоритет: {priority}. Черновик ответа подготовлен."
        ),
    }


def render_review_digest(classified_rows: list[Mapping[str, Any]], tickets: list[Mapping[str, Any]]) -> str:
    urgency_counts = Counter(row["urgency"] for row in classified_rows)
    topic_counts = Counter(row["topic"] for row in classified_rows)
    high_priority = [row for row in classified_rows if row["urgency"] == "high"][:8]
    digest_columns = [
        "review_id",
        "marketplace",
        "sku",
        "rating",
        "topic",
        "urgency",
        "approval_status",
        "reply_draft",
    ]
    return "\n".join(
        [
            "# Дайджест по отзывам",
            "",
            f"- Обработано отзывов: {len(classified_rows)}",
            f"- Обращения в поддержку: {len(tickets)}",
            f"- Высокая срочность: {urgency_counts.get('high', 0)}",
            f"- Средняя срочность: {urgency_counts.get('medium', 0)}",
            f"- Низкая срочность: {urgency_counts.get('low', 0)}",
            "",
            "## Темы",
            "",
            markdown_table(
                [{"topic": topic, "count": count} for topic, count in topic_counts.most_common()],
                ["topic", "count"],
            ),
            "",
            "## Приоритетные отзывы",
            "",
            markdown_table(high_priority, digest_columns),
            "",
        ]
    )


def run_review_agent(input_path: Path, out_dir: Path) -> dict[str, Path]:
    rows = read_csv(input_path)
    validate_rows(rows, required_columns=REVIEWS_REQUIRED, dataset_name="reviews")
    classified_rows = [classify_review(row) for row in rows]
    tickets = [
        ticket
        for ticket in (build_support_ticket(row) for row in classified_rows)
        if ticket is not None
    ]
    replies_path = out_dir / "review_replies.csv"
    tickets_path = out_dir / "support_tickets.csv"
    digest_path = out_dir / "review_digest.md"
    json_path = out_dir / "review_agent_payload.json"
    write_csv(replies_path, classified_rows, REPLY_COLUMNS)
    write_csv(tickets_path, tickets, TICKET_COLUMNS)
    write_text(digest_path, render_review_digest(classified_rows, tickets))
    write_json(json_path, {"replies": classified_rows, "tickets": tickets})
    return {
        "replies": replies_path,
        "tickets": tickets_path,
        "digest": digest_path,
        "json": json_path,
    }
