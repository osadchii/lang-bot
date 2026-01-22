"""Tests for exercise service variety improvements."""

from bot.services.exercise_service import (
    AI_SUPPLEMENT_COUNT,
    MAX_EXERCISE_HISTORY,
    MIN_WORDS_FOR_VARIETY,
    ExerciseService,
    ExerciseType,
)


class TestSourceFormExclusion:
    """Tests for excluding source forms from target options."""

    def test_tense_variations_exclude_present(self, db_session):
        """Test that tense variations exclude present tense (source form)."""
        service = ExerciseService(db_session)
        variations = service._get_variations_for_type(ExerciseType.TENSES)

        tense_names = [v[0] for v in variations]
        assert "Ενεστωτας" not in tense_names
        assert "Αοριστος" in tense_names
        assert "Μελλοντας" in tense_names

    def test_conjugation_variations_exclude_first_singular(self, db_session):
        """Test that conjugation variations exclude 1st person singular (source form)."""
        service = ExerciseService(db_session)
        variations = service._get_variations_for_type(ExerciseType.CONJUGATIONS)

        person_ids = [v[0] for v in variations]
        assert "1st_singular" not in person_ids
        assert "2nd_singular" in person_ids
        assert "3rd_singular" in person_ids
        assert "1st_plural" in person_ids
        assert "2nd_plural" in person_ids
        assert "3rd_plural" in person_ids

    def test_case_variations_exclude_nominative(self, db_session):
        """Test that case variations exclude nominative (source form)."""
        service = ExerciseService(db_session)
        variations = service._get_variations_for_type(ExerciseType.CASES)

        case_names = [v[0] for v in variations]
        assert "Ονομαστικη" not in case_names
        assert "Γενικη" in case_names
        assert "Αιτιατικη" in case_names
        assert "Κλητικη" in case_names


class TestExerciseHistoryTracking:
    """Tests for exercise history tracking."""

    def test_select_avoids_recent_combinations(self, db_session):
        """Test that selection avoids recent word+variation combinations."""
        service = ExerciseService(db_session)

        words = [
            {"word": "γραφω", "translation": "писать"},
            {"word": "διαβαζω", "translation": "читать"},
        ]
        variations = [("A", "a"), ("B", "b")]
        # Mark all γραφω combinations as recent
        history = [("γραφω", "A"), ("γραφω", "B")]

        # Should select διαβαζω since γραφω combinations are in history
        for _ in range(10):
            word, var, _ = service._select_word_and_variation(words, variations, history)
            assert word["word"] == "διαβαζω"

    def test_select_falls_back_when_all_in_history(self, db_session):
        """Test that selection works when all combinations are in history."""
        service = ExerciseService(db_session)

        words = [{"word": "γραφω", "translation": "писать"}]
        variations = [("A", "a")]
        # Only combination is in history
        history = [("γραφω", "A")]

        # Should still select (fallback)
        word, var, new_history = service._select_word_and_variation(words, variations, history)
        assert word["word"] == "γραφω"
        assert var[0] == "A"

    def test_history_limited_to_max_size(self, db_session):
        """Test that history doesn't grow beyond max size."""
        service = ExerciseService(db_session)

        words = [{"word": f"word{i}", "translation": f"trans{i}"} for i in range(20)]
        variations = [("A", "a")]
        history = []

        for _ in range(15):
            _, _, history = service._select_word_and_variation(words, variations, history)

        assert len(history) <= MAX_EXERCISE_HISTORY

    def test_history_updated_correctly(self, db_session):
        """Test that history is updated with new selection."""
        service = ExerciseService(db_session)

        words = [{"word": "γραφω", "translation": "писать"}]
        variations = [("A", "a"), ("B", "b")]
        history = []

        word, var, new_history = service._select_word_and_variation(words, variations, history)

        assert len(new_history) == 1
        assert new_history[0] == (word["word"], var[0])

    def test_select_distributes_across_words(self, db_session):
        """Test that selection distributes across multiple words."""
        service = ExerciseService(db_session)

        words = [
            {"word": "word1", "translation": "trans1"},
            {"word": "word2", "translation": "trans2"},
            {"word": "word3", "translation": "trans3"},
        ]
        variations = [("A", "a")]
        history = []

        selected_words = set()
        for _ in range(10):
            word, _, history = service._select_word_and_variation(words, variations, history)
            selected_words.add(word["word"])

        # Should have selected all 3 words at some point
        assert len(selected_words) == 3


class TestAIWordSupplementation:
    """Tests for AI word supplementation constants."""

    def test_min_words_constant(self):
        """Test MIN_WORDS_FOR_VARIETY constant is set."""
        assert MIN_WORDS_FOR_VARIETY > 0
        assert MIN_WORDS_FOR_VARIETY == 3

    def test_ai_supplement_count_constant(self):
        """Test AI_SUPPLEMENT_COUNT constant is set."""
        assert AI_SUPPLEMENT_COUNT > 0
        assert AI_SUPPLEMENT_COUNT == 2

    def test_max_history_constant(self):
        """Test MAX_EXERCISE_HISTORY constant is set."""
        assert MAX_EXERCISE_HISTORY > 0
        assert MAX_EXERCISE_HISTORY == 10


class TestWordFiltering:
    """Tests for word filtering (nouns/verbs)."""

    def test_is_noun_with_article(self, db_session):
        """Test that words with articles are identified as nouns."""
        service = ExerciseService(db_session)

        assert service._is_noun("ο ανθρωπος")
        assert service._is_noun("η γυναικα")
        assert service._is_noun("το παιδι")
        assert service._is_noun("οι ανθρωποι")
        assert service._is_noun("τα παιδια")

    def test_is_noun_without_article(self, db_session):
        """Test that words without articles are not nouns."""
        service = ExerciseService(db_session)

        assert not service._is_noun("γραφω")
        assert not service._is_noun("καλος")

    def test_is_verb_with_verb_endings(self, db_session):
        """Test that words with verb endings are identified as verbs."""
        service = ExerciseService(db_session)

        assert service._is_verb("γραφω")
        assert service._is_verb("διαβαζω")
        assert service._is_verb("τρωω")
        assert service._is_verb("πινω")

    def test_is_verb_without_verb_endings(self, db_session):
        """Test that words without verb endings are not verbs."""
        service = ExerciseService(db_session)

        assert not service._is_verb("ο ανθρωπος")
        assert not service._is_verb("καλος")
