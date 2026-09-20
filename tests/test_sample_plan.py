import unittest

from fontmaker.sample_plan import minimal_sample_syllables, required_component_keys
from fontmaker.syllable_split import component_keys_for


class MinimalSamplePlanTests(unittest.TestCase):
    def test_plan_uses_198_unique_complete_syllables(self):
        samples = minimal_sample_syllables()

        self.assertEqual(len(samples), 198)
        self.assertEqual(len(samples), len(set(samples)))
        self.assertTrue(all(0xAC00 <= ord(syllable) <= 0xD7A3 for syllable in samples))

    def test_plan_covers_all_286_required_components(self):
        covered = {
            key
            for syllable in minimal_sample_syllables()
            for key in component_keys_for(syllable).values()
        }

        self.assertEqual(len(required_component_keys()), 286)
        self.assertEqual(covered, required_component_keys())

    def test_plan_starts_with_an_easy_representative_syllable(self):
        self.assertEqual(minimal_sample_syllables()[0], "가")

