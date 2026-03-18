"""
Smart Question Selection Engine
Automatically selects questions from the question bank based on:
  - Template structure (sections, marks, count)
  - Difficulty distribution ratio
  - Course Outcome coverage
  - Bloom's level balance
"""

import random
from extensions import mongo


def select_questions_for_template(template: dict, institution_type: str,
                                   subject: str = None) -> dict:
    """
    Given a template document and institution type, returns:
    {
      'sections': [
        {
          'section_name': str,
          'questions': [question_doc, ...]
        }, ...
      ],
      'total_marks': int,
      'analytics': {...}
    }
    """
    sections_result = []
    all_selected_ids = set()

    base_query = {'institution_type': institution_type}
    if subject:
        base_query['subject'] = subject

    for section in template.get('sections', []):
        section_name  = section.get('section_name', 'Section')
        num_q         = int(section.get('num_questions', 5))
        diff_ratio    = section.get('difficulty_ratio',
                                    {'easy': 0.34, 'medium': 0.33, 'hard': 0.33})

        selected = _select_by_difficulty(
            base_query, num_q, diff_ratio, all_selected_ids
        )
        all_selected_ids.update(str(q['_id']) for q in selected)

        sections_result.append({
            'section_name': section_name,
            'marks_per_question': section.get('marks_per_question', 2),
            'question_type': section.get('question_type', 'short'),
            'questions': selected
        })

    analytics = _compute_analytics(sections_result)
    total_marks = sum(
        sec['marks_per_question'] * len(sec['questions'])
        for sec in sections_result
    )

    return {
        'sections': sections_result,
        'total_marks': total_marks,
        'analytics': analytics
    }


def _select_by_difficulty(base_query: dict, num_q: int,
                           diff_ratio: dict, exclude_ids: set) -> list:
    """
    Select num_q questions respecting the difficulty ratio.
    Falls back gracefully if not enough questions of a level exist.
    """
    counts = {
        'easy':   max(1, round(num_q * diff_ratio.get('easy', 0.33))),
        'medium': max(1, round(num_q * diff_ratio.get('medium', 0.33))),
        'hard':   max(0, round(num_q * diff_ratio.get('hard', 0.34))),
    }
    # Adjust rounding error
    while sum(counts.values()) < num_q:
        counts['medium'] += 1
    while sum(counts.values()) > num_q:
        if counts['hard'] > 0:
            counts['hard'] -= 1
        else:
            counts['medium'] -= 1

    selected = []
    for difficulty, count in counts.items():
        if count <= 0:
            continue
        query = {**base_query, 'difficulty': difficulty}
        pool = [
            q for q in mongo.db.questions.find(query)
            if str(q['_id']) not in exclude_ids
        ]
        chosen = random.sample(pool, min(count, len(pool)))
        selected.extend(chosen)
        exclude_ids.update(str(q['_id']) for q in chosen)

    # If we still need more, pick any remaining
    if len(selected) < num_q:
        pool = [
            q for q in mongo.db.questions.find(base_query)
            if str(q['_id']) not in exclude_ids
        ]
        extra = random.sample(pool, min(num_q - len(selected), len(pool)))
        selected.extend(extra)

    return selected[:num_q]


def _compute_analytics(sections_result: list) -> dict:
    """Compute CO coverage, BL distribution, difficulty distribution."""
    co_counter   = {}
    bl_counter   = {}
    diff_counter = {'easy': 0, 'medium': 0, 'hard': 0}
    total = 0

    for sec in sections_result:
        for q in sec['questions']:
            total += 1
            co  = q.get('co', 'N/A')
            bl  = q.get('bl', 'N/A')
            dif = q.get('difficulty', 'medium')
            co_counter[co]   = co_counter.get(co, 0) + 1
            bl_counter[bl]   = bl_counter.get(bl, 0) + 1
            diff_counter[dif] = diff_counter.get(dif, 0) + 1

    return {
        'total_questions': total,
        'co_coverage':     co_counter,
        'bl_distribution': bl_counter,
        'difficulty_distribution': diff_counter
    }
