from django.core.exceptions import ValidationError
import datetime

# validates the rating a user gives to a movie
def validate_score(score):
    if score < 1 or score > 10:
        raise ValidationError(f'{score} is not a valid score. A score is a number between 1 and 10.')

# validates the year a movie came out
def validate_year(year):
    start_year = 1900
    current_year = datetime.datetime.today().year
    if year < start_year or year > current_year:
        raise ValidationError(f'{year} is not a valid year. Please enter a number between {start_year} and {current_year}.')

# validates a movie's runtime, we do not allow time travel
def validate_runtime(runtime):
    if runtime < 0:
        raise ValidationError('Runtime must be a positive number.')
