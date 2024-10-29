"""Model setup for RXNAAMapper"""

import logging

from lmabc.configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from rxn_aa_mapper.model import EnzymaticReactionLightningModule
from rxn_aa_mapper.tokenization import LMEnzymaticReactionTokenizer

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def download_bert_model():
    """Download and save the BERT model to the cache directory."""
    cache_dir = BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("rxnaamapper")
    model_path = cache_dir / "model"

    if not model_path.exists():
        logger.info("Downloading and saving BERT model...")
        model = EnzymaticReactionLightningModule(
            model_architecture={}, model_args={"model": "google-bert/bert-base-uncased"}
        )

        tokenizer = LMEnzymaticReactionTokenizer(
            vocabulary_file=str(cache_dir / "vocabulary.txt"),
            aa_sequence_tokenizer_filepath=str(cache_dir / "tokenizer.json"),
            aa_sequence_tokenizer_type="generic",
        )

        vocab_size = tokenizer.vocab_size
        model.model.resize_token_embeddings(vocab_size)

        model.model.save_pretrained(model_path, safe_serialization=False)
    else:
        logger.info(f"Model already exists at {model_path}")


if __name__ == "__main__":
    download_bert_model()
    logger.info("Model setup completed successfully!")
