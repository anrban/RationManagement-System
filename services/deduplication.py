from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from models import Beneficiary


def check_for_duplicates(new_beneficiary: dict, db: Session, threshold: int = 90):
    """
    Fuzzy-match name + address against existing records.
    Returns potential duplicates above similarity threshold.
    """
    all_beneficiaries = db.query(Beneficiary).filter(
        Beneficiary.verification_status != "duplicate"
    ).all()

    duplicates = []
    for existing in all_beneficiaries:
        name_score = fuzz.token_sort_ratio(new_beneficiary["name"], existing.name)
        address_score = fuzz.token_sort_ratio(
            new_beneficiary.get("address", ""), existing.address or ""
        )
        combined = (name_score * 0.6) + (address_score * 0.4)

        if combined >= threshold:
            duplicates.append({
                "id": str(existing.id),
                "name": existing.name,
                "national_id": existing.national_id,
                "similarity_score": round(combined, 2),
            })

    return duplicates
