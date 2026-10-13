"""
The keyword rule: is a paper about multimodal tabular learning?

classify(title, abstract) returns two yes/no answers:

  image_table  the paper learns from images AND tabular data together
               (e.g. MRI scans + clinical variables, photos + a feature table)
  text_table   the paper learns from tables that contain text, or from
               structured records paired with text (e.g. EHR + clinical notes)

How it decides, in plain words
  * Split the abstract into sentences.
  * IMAGE + TABLE: some sentence mentions image data AND tabular data, and the
    paper calls itself multimodal (multimodal, cross-modal, modalities, fusion, ...).
    A hyphenated "image-tabular" / "vision-tabular" is enough on its own.
  * TEXT + TABLE: some sentence mentions text inside a table ("text fields",
    "string columns", "free-text", ...) OR pairs tabular data with text / notes /
    reports in a clearly multimodal paper.
  * A sentence does NOT count as evidence when it is only
      - a contrast:        "unlike images and text, tabular data ..."
      - a list of domains: "we test on image, text and tabular benchmarks"
      - about documents, charts or turning tables into text.
  * Never counted: tables drawn as images (screenshots, charts), table question
    answering, text-to-SQL, and "tabular" in the reinforcement-learning sense
    ("tabular MDP", "tabular setting").
"""
import re


def words(*phrases):
    """Regex that matches any of the phrases as whole words, ignoring case."""
    return re.compile(r"\b(?:" + "|".join(phrases) + r")\b", re.IGNORECASE)


# --- "tabular" as data, not as in reinforcement learning ("tabular MDP") ----------
RL_WORDS = ("setting|settings|case|cases|mdps?|markov|rl|reinforcement|episodic|q|q-learning|environments?|"
            "softmax|nas|polic(?:y|ies)|bandits?|games?|regime|problems?|function|value|methods?|algorithms?")
TABULAR = r"tabular(?!\W+(?:" + RL_WORDS + r")\b)"

# --- vocabularies -----------------------------------------------------------------
TABLE_DATA = words(
    TABULAR, "spreadsheets?",
    r"(?<!lookup )(?<!hash )(?<!truth )(?<!periodic )tables?",
    r"structured (?:EHRs?|electronic health records?|electronic health record \(EHR\) data|clinical data|patient data)",
    "EHRs?", "electronic health records?",
    "clinical (?:data|variables|features|factors|scores|measurements|covariates|records)",
    "non-imaging")
STRONG_TABLE_DATA = words(
    TABULAR, "spreadsheets?", "EHRs?", "electronic health records?",
    "structured (?:EHRs?|clinical data|patient data)")
IMAGE_DATA = words(
    r"images?(?! (?:reports?|studies))", r"imaging(?! (?:reports?|studies))", "imagery",
    "photos?", "photographs?", "MRIs?", "sMRI", "fMRI", "CT", "CXRs?", "X-rays?", "radiographs?",
    r"histopatholog\w*", "whole[- ]slide", "WSIs?", "fundus", r"dermoscop\w*", "ultrasound",
    r"mammogra\w*", "satellite", "remote sensing", "cell painting")
IMAGE_TABLE_COMPOUND = words("(?:image|imaging|vision|visual)-tabular", "tabular-(?:image|imaging|vision|visual)")
IMAGE_TEXT_COMPOUND = words("text-to-image", "text-image", "image-text", "image-to-text",
                            "vision-language", "visual-language", "text-guided")

MULTIMODAL = words(r"multi-?modal\w*", r"cross-?modal\w*", "modalit(?:y|ies)", "fusion", "fus(?:e|es|ed|ing)", "paired")
CLEARLY_MULTIMODAL = words(r"multi-?modal\w*", "fusion", "fus(?:e|es|ed|ing)")

TEXT_IN_TABLE = words(
    "text(?:ual)? (?:fields?|columns?|entries|cells?|attributes?|features?)",
    "string (?:columns?|entries|values|features?|attributes?|cells?|embeddings?|properties)", "string-valued",
    "high-cardinality strings?", "tabular-text(?:ual)?", "text(?:ual)?-tabular",
    "free[- ]text", "natural language (?:fields?|components?)")
TABLE_CONTEXT = words(TABULAR, "tables?", "columns?", "cells?", "mixed[- ]type", "spreadsheets?")
MIXED_FEATURE_TYPES = re.compile(  # "numerical, categorical and text features"
    r"\b(?:numeric(?:al)?|categorical)\b(?:,|\s+and|\s+or)[^.]{0,40}\b(?:text|textual|string)\b"
    r"\s+(?:features?|columns?|fields?|attributes?|values|properties|variables|data types)", re.IGNORECASE)
TEXT_DATA = words("free[- ]text", "clinical notes", "notes", "text", "texts", "textual", "reports", "natural language")
STRUCTURED_AND_UNSTRUCTURED = re.compile(r"\bstructured\b.*\bunstructured\b|\bunstructured\b.*\bstructured\b", re.IGNORECASE)

# --- things that rule a paper or sentence out -------------------------------------
NOT_TEXT_TABLE_TOPICS = words(
    "question[- ]answering", "QA", "text-to-SQL", "NL2SQL", "SQL", "table-to-text", "data-to-text",
    "table understanding", "table reasoning", "tabular reasoning", "table summari[sz]ation", "semi-structured",
    "documents?", "OCR", "table retrieval", "fact verification", "charts?")
TABLE_AS_IMAGE = words(
    "tables? as (?:an? )?images?", "table-as-image", "image-based table", "visual table", "table images?",
    "images? of tables", "table screenshots?", "charts?", "document images?", "images? within table cells",
    "table (?:recognition|detection|structure recognition)", "tabular-to-image", "table-to-image",
    r"(?:convert|transform|map)\w* [^.]{0,40}\b(?:tabular data|tables?) (?:in)?to images?")
DOCUMENT_LIKE = words("documents?", "figures", "equations", "paragraphs", "screenshots?", "web ?pages?",
                      "code snippets", "slides", "charts?", "data types")
CONTRAST = re.compile(
    r"\b(?:unlike|in contrast to|contrary to|compared (?:to|with)|non-image|non-visual|rather than|instead of|"
    r"cannot|counterparts?|lag\w* behind|less attention)\b|"
    r"\b(?:text|textual|images?|vision|visual)\s+or\s+tabular\b|\btabular\s+or\s+(?:text|textual|images?|vision|visual)\b",
    re.IGNORECASE)
EVALUATION_LIST = words("datasets", "data sets", "benchmarks", "tasks", "domains", "problems")
SERIALIZATION = re.compile(  # turning a table into text, e.g. "rows are serialized into prompts"
    r"\b(?:seriali[sz]\w*|(?:encoded|converted?|convert\w*|transform\w*|translat\w*) [^.]{0,60}\binto "
    r"(?:text|natural language|sentences|prompts))", re.IGNORECASE)
MODALITY_WORDS = words("images?", "imagery", "imaging", "vision", "visual", "text", "texts", "textual", "language",
                       "audio", "speech", "video", "tabular", "tables?", "records", "graphs?", "time[- ]series",
                       "temporal signals", "signals", "point clouds?", "depth", "3D")


def split_sentences(text):
    return re.split(r"(?<=[.;!?])\s+", text)


def is_usable_evidence(sentence, clearly_multimodal):
    """False for sentences that mention modalities without combining them."""
    if CONTRAST.search(sentence):
        return False
    modalities = {m.group(0).lower().rstrip("s") for m in MODALITY_WORDS.finditer(sentence)}
    if len(modalities) >= 4:
        return False                                  # a long list of data types
    if len(modalities) == 3 and not clearly_multimodal:
        return False                                  # "image, text and tabular data" in a non-multimodal paper
    if EVALUATION_LIST.search(sentence) or DOCUMENT_LIKE.search(sentence) or SERIALIZATION.search(sentence):
        return False
    return True


def classify(title, abstract):
    text = f"{title}. {abstract}".replace("\n", " ")
    text = IMAGE_TEXT_COMPOUND.sub(" ", text)          # "image-text pairs" are not image + table evidence
    sentences = split_sentences(text)
    multimodal = bool(MULTIMODAL.search(text))
    clearly_multimodal = bool(CLEARLY_MULTIMODAL.search(text))
    title_is_about_documents = bool(DOCUMENT_LIKE.search(title))

    # IMAGE + TABLE
    image_table = bool(IMAGE_TABLE_COMPOUND.search(text))
    if multimodal:
        for s in sentences:
            if IMAGE_DATA.search(s) and TABLE_DATA.search(s) and is_usable_evidence(s, clearly_multimodal):
                image_table = True
    if TABLE_AS_IMAGE.search(text) or title_is_about_documents:
        image_table = False

    # TEXT + TABLE
    text_table = False
    for s in sentences:
        text_inside_table = (TEXT_IN_TABLE.search(s) and TABLE_CONTEXT.search(s)) or MIXED_FEATURE_TYPES.search(s)
        if text_inside_table and not CONTRAST.search(s):
            text_table = True
        paired_with_text = TEXT_DATA.search(s) and TABLE_DATA.search(s) and is_usable_evidence(s, clearly_multimodal)
        explicitly_paired = clearly_multimodal or (STRUCTURED_AND_UNSTRUCTURED.search(s) and STRONG_TABLE_DATA.search(s))
        if paired_with_text and explicitly_paired:
            text_table = True
    if NOT_TEXT_TABLE_TOPICS.search(text) or title_is_about_documents:
        text_table = False

    return {"image_table": image_table, "text_table": text_table}


def is_tabular_paper(title, abstract):
    """Mentions tabular data at all (used as the denominator), excluding reinforcement learning."""
    text = f"{title}. {abstract}"
    mentions_tabular = re.search(r"\b" + TABULAR + r"\b", text, re.IGNORECASE)
    is_rl = re.search(r"\b(?:MDPs?|Markov decision|reinforcement learning|regret|Q-learning|bandits?)\b", text, re.IGNORECASE)
    return bool(mentions_tabular and not is_rl)
