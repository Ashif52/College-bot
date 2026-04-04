import unittest

from chatbot.voicebot_service import (
    VoiceConversationState,
    _normalize_followup_answer,
    _prepare_query_text,
    _sanitize_voice_answer,
    normalize_outbound_phone,
    parse_yes_no,
)


class VoicebotServiceTests(unittest.TestCase):
    def test_normalize_phone_defaults_to_india(self):
        self.assertEqual(normalize_outbound_phone("9876543210"), "+919876543210")
        self.assertEqual(normalize_outbound_phone("+1 (415) 555-0199"), "+14155550199")

    def test_parse_yes_no(self):
        self.assertEqual(parse_yes_no("yes sure"), "yes")
        self.assertEqual(parse_yes_no("no thanks"), "no")
        self.assertEqual(parse_yes_no("maybe later"), "unknown")

    def test_followup_answer_normalization(self):
        self.assertEqual(
            _normalize_followup_answer("What is your current highest qualification?", "let's do"),
            "+2",
        )
        self.assertEqual(
            _normalize_followup_answer("What percentage did you score?", "ninety six"),
            "96%",
        )
        self.assertEqual(
            _normalize_followup_answer("Do you need hostel accommodation?", "yes"),
            "Yes",
        )

    def test_query_text_cleanup_and_retry(self):
        self.assertIsNone(_prepare_query_text("Just say do we have them into the"))
        self.assertEqual(_prepare_query_text("Is there a gym inside the campus?"), "Is there a gym inside the campus")

    def test_sanitize_voice_answer(self):
        answer = (
            "Yes, the campus has sports and fitness facilities including fitness centers. "
            "You can use them during your studies. (Source: https://example.com/page)"
        )
        cleaned = _sanitize_voice_answer(answer)
        self.assertNotIn("https://", cleaned)
        self.assertIn("Yes,", cleaned)
        self.assertLessEqual(cleaned.count("."), 2)

    def test_followup_then_query_loop(self):
        lead = {
            "course_of_interest": "MBA",
            "followup_q1": "What is your current qualification?",
            "followup_q2": "Which year did you pass out?",
        }
        state = VoiceConversationState(
            session_id="s1",
            lead=lead,
            followup_questions=[lead["followup_q1"], lead["followup_q2"]],
        )

        opening = state.opening_prompt()
        self.assertIn("MBA enquiry", opening)
        self.assertEqual(state.mode, "ASK_FOLLOWUPS")

        step = state.handle_transcript("BCom")
        self.assertIn("Is that correct", step.reply)
        self.assertEqual(state.mode, "CONFIRM_FOLLOWUP_ANSWER")

        step = state.handle_transcript("yes")
        self.assertIn(lead["followup_q2"], step.reply)
        self.assertEqual(len(state.followup_answers), 1)

        step = state.handle_transcript("2024")
        self.assertIn("question", step.reply.lower())
        self.assertEqual(state.mode, "ANY_QUERY_CONFIRM")

        step = state.handle_transcript("yes")
        self.assertEqual(state.mode, "QUERY_TEXT")
        self.assertIn("one short sentence", step.reply.lower())

        step = state.handle_transcript("Hostel facility?")
        self.assertTrue(step.needs_query_answer)
        self.assertEqual(step.query_text, "Hostel facility")

        followup = state.register_query_answer("Hostel facility?", "Yes, hostel is available.")
        self.assertIn("other query", followup)
        self.assertEqual(state.mode, "MORE_QUERY_CONFIRM")

        end_step = state.handle_transcript("no")
        self.assertTrue(end_step.should_end)
        self.assertTrue(state.completed)

    def test_followup_confirmation_retry(self):
        lead = {
            "course_of_interest": "MBA",
            "followup_q1": "What is your current highest qualification?",
        }
        state = VoiceConversationState(
            session_id="s2",
            lead=lead,
            followup_questions=[lead["followup_q1"]],
        )

        state.opening_prompt()
        step = state.handle_transcript("let's do")
        self.assertIn("+2", step.reply)
        self.assertEqual(state.mode, "CONFIRM_FOLLOWUP_ANSWER")

        step = state.handle_transcript("no")
        self.assertIn("Please answer again", step.reply)
        self.assertEqual(state.mode, "ASK_FOLLOWUPS")


if __name__ == "__main__":
    unittest.main()
