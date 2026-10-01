import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import api
import utils.database as database
from services.profile_service import load_profile


class ExploreInterestPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path_patch = patch.object(
            database,
            "DATABASE_PATH",
            Path(self.temp_dir.name) / "novateach-test.db",
        )
        self.database_path_patch.start()
        database.create_tables()
        database.create_user(
            username="learner",
            name="Learner",
            password_hash="test-hash",
        )
        database.update_user_profile(
            username="learner",
            name="Learner",
            full_profile=json.dumps(
                {
                    "username": "learner",
                    "name": "Learner",
                }
            ),
        )

    def tearDown(self):
        self.database_path_patch.stop()
        self.temp_dir.cleanup()

    def test_saved_and_later_interests_round_trip_in_profile(self):
        database.update_saved_explore_interest(
            "learner",
            "Ethics",
            "Philosophy",
            "saved",
        )
        database.update_saved_explore_interest(
            "learner",
            "Ethics",
            "Philosophy",
            "later",
        )

        profile = load_profile("learner")
        self.assertIsNotNone(profile)
        self.assertEqual(
            profile.get_personalization_summary()["saved_interests"],
            [
                {
                    "topic": "Ethics",
                    "subject": "Philosophy",
                    "status": "later",
                }
            ],
        )

    def test_removing_interest_preserves_other_profile_fields(self):
        user = database.load_user("learner")
        profile_data = {
            "username": "learner",
            "name": "Learner",
            "understanding_strategy": "Examples",
            "saved_interests": [
                {
                    "topic": "Ethics",
                    "subject": "Philosophy",
                    "status": "saved",
                }
            ],
        }
        database.update_user_profile(
            username="learner",
            name=user["name"],
            full_profile=json.dumps(profile_data),
        )

        interests = database.update_saved_explore_interest(
            "learner",
            "Ethics",
            "Philosophy",
            "remove",
        )
        profile = load_profile("learner")

        self.assertEqual(interests, [])
        self.assertEqual(profile.understanding_strategy, "Examples")
        self.assertEqual(profile.saved_interests, [])

    def test_api_saved_interests_are_returned_in_dashboard_profile(self):
        api.update_explore_interest(
            api.ExploreInterestData(
                username="learner",
                topic="Socialization",
                subject="Sociology",
                status="later",
            )
        )

        dashboard = api.get_dashboard("learner")

        self.assertEqual(
            dashboard["profile"]["saved_interests"],
            [
                {
                    "topic": "Socialization",
                    "subject": "Sociology",
                    "status": "later",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
