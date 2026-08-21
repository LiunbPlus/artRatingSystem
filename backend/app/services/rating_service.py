import json
from typing import Optional

from app.repositories import rating_repository, work_repository


RATING_DIMENSIONS = ["创意", "表现力", "完成度"]


def get_dimensions(category: str) -> list[str]:
    return RATING_DIMENSIONS


def get_user_rating(work_id: int, user_id: int) -> Optional[dict]:
    return rating_repository.get_for_user(work_id, user_id)


def summary(work_id: int) -> dict:
    rows = rating_repository.get_for_work(work_id)
    if not rows:
        return {"count": 0, "dimensions": {}, "overall_avg": None}
    all_scores = [json.loads(row["scores_json"]) for row in rows]
    dimension_scores = {}
    for scores in all_scores:
        for dimension, score in scores.items():
            dimension_scores.setdefault(dimension, []).append(score)
    dimensions = {
        dimension: {
            "average": round(sum(scores) / len(scores), 2),
            "count": len(scores), "min": min(scores), "max": max(scores),
        }
        for dimension, scores in dimension_scores.items()
    }
    flattened = [score for scores in all_scores for score in scores.values()]
    return {
        "count": len(rows), "dimensions": dimensions,
        "overall_avg": round(sum(flattened) / len(flattened), 2) if flattened else None,
    }


def validate_and_rate(work_id: int, user_id: int, scores: dict) -> tuple[bool, str]:
    work = work_repository.get_by_id(work_id)
    if not work:
        return False, "作品不存在"
    if not isinstance(scores, dict):
        return False, "评分格式错误"
    for dimension in get_dimensions(work["category"]):
        if dimension not in scores:
            return False, f"缺少评分维度：{dimension}"
        score = scores[dimension]
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 1 <= score <= 10:
            return False, f"维度「{dimension}」评分必须在1-10之间"
    rating_repository.upsert(work_id, user_id, scores)
    return True, "评分提交成功"
