# src/utils/tag_normalizer.py

import re

# ---------------------------------------------------------------------------
# Spam / irrelevant tags to filter out before classification
# ---------------------------------------------------------------------------
SPAM_TAGS = {
    "seen live", "spotify", "favourite", "favorites", "awesome", "great",
    "love", "cool", "good", "best", "beautiful", "amazing", "nice",
    "my favourite", "owned", "under 2000 listeners", "all",
    "american", "british", "swedish", "german", "french", "italian",
    "canadian", "australian", "norwegian", "japanese", "irish",
}

# ---------------------------------------------------------------------------
# Genre taxonomy: canonical name → tag variants that map to it
# ---------------------------------------------------------------------------
GENRE_TAXONOMY: dict[str, list[str]] = {
    "Rock": [
        "rock", "classic rock", "hard rock", "indie rock", "alternative rock",
        "progressive rock", "soft rock", "psychedelic rock", "garage rock",
        "art rock", "glam rock", "blues rock", "southern rock", "arena rock",
        "post rock", "post-rock", "math rock", "stoner rock", "desert rock",
    ],
    "Metal": [
        "metal", "heavy metal", "thrash metal", "death metal", "black metal",
        "doom metal", "power metal", "progressive metal", "metalcore",
        "deathcore", "symphonic metal", "nu metal", "nu-metal", "post metal",
        "post-metal", "sludge metal", "groove metal", "speed metal",
        "melodic death metal", "folk metal",
    ],
    "Pop": [
        "pop", "indie pop", "synth pop", "synthpop", "electropop", "dream pop",
        "chamber pop", "baroque pop", "art pop", "bubblegum pop", "k-pop",
        "j-pop", "pop rock", "teen pop", "dance pop",
    ],
    "Electronic": [
        "electronic", "electronica", "edm", "techno", "house", "trance",
        "dubstep", "drum and bass", "dnb", "drum n bass", "ambient electronic",
        "electro", "idm", "intelligent dance music", "trip hop", "breakbeat",
        "jungle", "garage", "uk garage", "synthwave", "vaporwave",
        "future bass", "chillwave", "downtempo",
    ],
    "Hip-Hop": [
        "hip hop", "hip-hop", "hiphop", "rap", "trap", "gangsta rap",
        "conscious hip hop", "underground hip hop", "east coast hip hop",
        "west coast hip hop", "southern hip hop", "alternative hip hop",
        "lo-fi hip hop", "lo fi hip hop",
    ],
    "R&B/Soul": [
        "r&b", "rnb", "soul", "neo soul", "funk", "motown", "rhythm and blues",
        "contemporary r&b", "new jack swing",
    ],
    "Jazz": [
        "jazz", "smooth jazz", "bebop", "fusion", "acid jazz", "jazz fusion",
        "free jazz", "swing", "big band", "jazz blues",
    ],
    "Classical": [
        "classical", "classical music", "baroque", "orchestral", "opera",
        "symphony", "chamber music", "contemporary classical", "minimalism",
        "neo classical", "neoclassical",
    ],
    "Folk/Acoustic": [
        "folk", "acoustic", "singer songwriter", "singer-songwriter",
        "folk rock", "contemporary folk", "americana", "country folk",
        "indie folk", "freak folk", "traditional folk", "bluegrass",
        "country", "alt country",
    ],
    "Punk": [
        "punk", "punk rock", "post punk", "post-punk", "hardcore punk",
        "hardcore", "emo", "pop punk", "emo pop", "skate punk", "anarcho punk",
        "new wave",
    ],
    "Ambient/Instrumental": [
        "ambient", "instrumental", "post rock", "post-rock", "drone",
        "new age", "meditation", "space rock", "film score", "soundtrack",
        "background music",
    ],
    "Alternative": [
        "alternative", "indie", "alternative rock", "alt rock", "grunge",
        "shoegaze", "noise rock", "lo-fi", "lo fi", "britpop",
    ],
}

# ---------------------------------------------------------------------------
# Mood taxonomy: canonical mood → tag variants
# ---------------------------------------------------------------------------
MOOD_TAXONOMY: dict[str, list[str]] = {
    "Energetic": [
        "energetic", "energy", "upbeat", "fast", "intense", "powerful",
        "driving", "aggressive", "adrenaline", "workout", "running",
        "party", "dance", "dancefloor", "club", "hype",
    ],
    "Happy": [
        "happy", "joyful", "cheerful", "fun", "feel good", "feelgood",
        "positive", "uplifting", "sunny", "bright", "playful", "carefree",
        "optimistic", "euphoric",
    ],
    "Melancholic": [
        "melancholic", "melancholy", "sad", "sadness", "emotional", "heartbreak",
        "heartbroken", "longing", "nostalgia", "nostalgic", "bittersweet",
        "tearjerker", "sorrowful", "depressing", "depressed", "lonely",
        "loneliness", "wistful",
    ],
    "Dark/Heavy": [
        "dark", "heavy", "dark atmosphere", "sinister", "ominous", "gloomy",
        "gothic", "brooding", "haunting", "bleak", "oppressive", "brutal",
        "aggressive", "angry", "rage",
    ],
    "Chill/Calm": [
        "chill", "calm", "relaxing", "relax", "chillout", "mellow",
        "laid back", "laid-back", "smooth", "peaceful", "quiet", "soft",
        "easy listening", "lounge", "coffee", "study", "focus",
    ],
    "Romantic": [
        "romantic", "romance", "love song", "love songs", "sensual",
        "passionate", "intimate", "tender", "sweet", "seductive",
    ],
}

# ---------------------------------------------------------------------------
# Pre-computed reverse lookup dicts for O(1) classification
# genre_tag → canonical_genre
# mood_tag → canonical_mood
# ---------------------------------------------------------------------------
_GENRE_REVERSE: dict[str, str] = {}
for _genre, _variants in GENRE_TAXONOMY.items():
    for _v in _variants:
        _GENRE_REVERSE[_v] = _genre

_MOOD_REVERSE: dict[str, str] = {}
for _mood, _variants in MOOD_TAXONOMY.items():
    for _v in _variants:
        _MOOD_REVERSE[_v] = _mood


# ---------------------------------------------------------------------------
# Tag cleaning
# ---------------------------------------------------------------------------
def clean_tag(raw_tag: str) -> str:
    """Lowercase, strip whitespace, normalise hyphens/underscores to spaces."""
    tag = raw_tag.lower().strip()
    tag = re.sub(r"[-_]+", " ", tag)
    tag = re.sub(r"\s+", " ", tag)
    return tag


# ---------------------------------------------------------------------------
# Tag normalization (filter spam + weight threshold)
# ---------------------------------------------------------------------------
def normalize_tags(raw_tags: list[dict]) -> list[tuple[str, int]]:
    """
    Given a list of Last.fm tag dicts [{"name": ..., "count": ...}],
    return [(cleaned_tag, count)] for tags with count >= 5, excluding spam.
    """
    result = []
    for tag_dict in raw_tags:
        name = tag_dict.get("name", "")
        try:
            count = int(tag_dict.get("count", 0))
        except (ValueError, TypeError):
            count = 0
        cleaned = clean_tag(name)
        if count >= 5 and cleaned not in SPAM_TAGS:
            result.append((cleaned, count))
    return result


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
def classify_genre(cleaned_tags: list[str]) -> str | None:
    """Return the first matching canonical genre, or None."""
    for tag in cleaned_tags:
        genre = _GENRE_REVERSE.get(tag)
        if genre:
            return genre
    return None


def classify_mood(cleaned_tags: list[str]) -> str | None:
    """Return the first matching canonical mood, or None."""
    for tag in cleaned_tags:
        mood = _MOOD_REVERSE.get(tag)
        if mood:
            return mood
    return None
