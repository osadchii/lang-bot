"""Constants for the spaced repetition system."""

# SM-2 Algorithm Constants
DEFAULT_EASE_FACTOR = 2.5  # Starting ease factor for new cards
MIN_EASE_FACTOR = 1.3  # Minimum allowed ease factor
EASE_FACTOR_MODIFIER = 0.15  # How much ease factor changes per quality rating

# Initial intervals (in days)
INITIAL_INTERVAL_AGAIN = 0  # Show again in learning mode (minutes)
INITIAL_INTERVAL_REMEMBERED = 1  # 1 day
INITIAL_INTERVAL_EASY = 4  # 4 days

# Learning mode intervals (in minutes)
LEARNING_STEPS = [1, 10]  # Minutes for learning new cards

# Quality ratings (3-option system)
QUALITY_FORGOT = 0  # Completely forgot
QUALITY_REMEMBERED = 3  # Correct response
QUALITY_EASY = 5  # Perfect response

# Multipliers for interval calculation
EASE_BONUS = 1.3  # Bonus multiplier for "Easy" responses

# Maximum interval (in days)
MAX_INTERVAL_DAYS = 365  # 1 year

# Session settings
DEFAULT_CARDS_PER_SESSION = 20
MAX_NEW_CARDS_PER_DAY = 20
