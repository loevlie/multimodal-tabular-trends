"""
Examples of what the rule should and should not flag.

Usage:  python -m pytest test_rule.py      (or just: python test_rule.py)
"""
from rule import classify


def flags(abstract, title="A paper"):
    result = classify(title, abstract)
    return result["image_table"], result["text_table"]


def test_image_and_tabular_fusion():
    assert flags("We propose a multimodal fusion of MRI images and tabular clinical data.") == (True, False)


def test_hyphenated_image_tabular():
    assert flags("We study image-tabular learning with missing values.") == (True, False)


def test_tables_with_text_fields():
    assert flags("We benchmark AutoML on data tables that contain text fields.") == (False, True)


def test_ehr_plus_notes():
    assert flags("Our multimodal model combines structured EHR data and clinical notes.") == (False, True)


def test_list_of_domains_is_not_multimodal():
    assert flags("We evaluate our method on image, text and tabular datasets.") == (False, False)


def test_contrast_is_not_multimodal():
    assert flags("Unlike images and text, tabular data is heterogeneous. We study multimodal fusion.") == (False, False)


def test_reinforcement_learning_tabular():
    assert flags("We prove regret bounds in the tabular MDP setting with image observations.") == (False, False)


def test_table_screenshots_do_not_count():
    assert flags("A multimodal model that reads table images and tabular content.") == (False, False)


def test_table_question_answering_does_not_count():
    assert flags("Multimodal question answering over tables with free-text passages.") == (False, False)


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("ok ", name)
