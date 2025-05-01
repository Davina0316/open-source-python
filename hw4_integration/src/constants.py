# Regex pattern to extract numeric percentage
SPAM_PROBABILITY_PATTERN = r"\d+"

# Prompt for AI spam detection
SPAM_DETECTION_PROMPT = (
    "Please analyze the following email content and return the probability "
    "that it is spam as a number between 0 and 100. Just return the number.\n\n"
)