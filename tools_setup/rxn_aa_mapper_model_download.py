"""Model setup for RXNAAMapper"""


import logging
from pathlib import Path

import click
from rxn_aa_mapper.model import EnzymaticReactionLightningModule
from rxn_aa_mapper.tokenization import LMEnzymaticReactionTokenizer

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def download_bert_model(cache_dir):
    """Download and save the BERT model to the cache directory."""
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

@click.command()
@click.argument('cache_dir', type=click.Path(exists=True))
def main(cache_dir):
    """Main function to set up the model using a provided configuration."""
    
    download_bert_model(Path(cache_dir))
    logger.info("Model setup completed successfully!")

if __name__ == "__main__":
    main()
