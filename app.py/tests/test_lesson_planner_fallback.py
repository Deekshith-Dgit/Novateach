import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import ai_generator
from modeles.lesson_plan import LearningBlueprint
from planners.lesson_planner import plan_lesson


VALID_BLUEPRINT = {
    "topic": "Cell structure",
    "subject": "Biology",
    "academic_level": "Class 9",
    "difficulty": "standard",
    "learning_objectives": ["Identify key cell structures."],
    "prerequisites": [],
    "concepts": [
        {
            "name": "Cell membrane",
            "description": "A boundary that regulates movement.",
        }
    ],
    "concept_sequence": ["Cell membrane"],
    "teaching_strategy": {},
}


def provider_client(content: str):
    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content=content)
                        )
                    ]
                )
            )
        )
    )


class LessonPlannerFallbackTests(unittest.TestCase):
    def test_invalid_primary_shape_uses_fallback_provider(self):
        clients = [
            provider_client('["not", "a", "lesson object"]'),
            provider_client(json.dumps(VALID_BLUEPRINT)),
        ]

        with patch.object(
            ai_generator,
            "_create_client",
            side_effect=clients,
        ) as create_client:
            blueprint = plan_lesson(
                topic="Cell structure",
                subject="Biology",
                academic_level="Class 9",
                difficulty="standard",
                learner_profile={},
            )

        self.assertEqual(blueprint.topic, "Cell structure")
        self.assertEqual(create_client.call_count, 2)
        create_client.assert_any_call("token_harbor")
        create_client.assert_any_call("groq")

    def test_valid_response_is_returned_as_blueprint(self):
        with patch.object(
            ai_generator,
            "_create_client",
            return_value=provider_client(json.dumps(VALID_BLUEPRINT)),
        ):
            blueprint = plan_lesson(
                topic="Cell structure",
                subject="Biology",
                academic_level="Class 9",
                difficulty="standard",
                learner_profile={},
            )

        self.assertIsInstance(blueprint, LearningBlueprint)


if __name__ == "__main__":
    unittest.main()
