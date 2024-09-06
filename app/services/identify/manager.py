from pathlib import Path

from numpy import ndarray

from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.identify.pinecone_container import PineconeContainer
from app.shared.utils import apply_mask

PROJECT_PATH = Path.cwd()


def identify_cap(
    cap: ndarray, pinecone_con: PineconeContainer, image_vectorizer: ImageVectorizer
) -> list[dict]:
    """Identify a cap from the Pinecone database.

    Args:
    ----
        cap: The cap.
        pinecone_con: The Pinecone connection.
        image_vectorizer: The class that transforms imgs to vectors
        model: The Keras model.

    Returns:
    -------
        The cap model with all the information.

    """
    img = apply_mask(cap)
    vector = image_vectorizer.image_to_vector(img=img)
    result = pinecone_con.query_database(vector=vector)
    return [cap.to_dict() for cap in result]
