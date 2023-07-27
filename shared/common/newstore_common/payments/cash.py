import json
import logging
import os
from decimal import Decimal

from newstore_common.utils import CachedProperty

logger = logging.getLogger(__name__)
logging.basicConfig()


class CashRounding:

    def __init__(self):
        pass

    @CachedProperty
    def get_configuration(self):
        """Gets store mappings from json"""
        current_path = os.path.dirname(os.path.abspath(__file__))
        mapping_filepath = os.path.join(current_path, 'cash_mapping.json')

        with open(mapping_filepath) as json_file:
            mappings = json.load(json_file)
            logger.debug(f'loaded store mappings: {mappings}')
            return mappings

    def round_amount(self, currency_code, amount):
        """Aligns amount to country specific payable cash amount"""

        logger.info(f"calculating rounding for currency: {currency_code} and amount {amount}")
        # Gets configuration
        mapping = self.get_configuration.get(currency_code, None)
        if not mapping:
            logger.info(f"no mapping found for country {currency_code}")
            return amount

        # Initializes from arguments and configuration
        amount = round(amount, 2)
        lower_boundary = mapping["LowerBoundary"]
        upper_boundary = mapping["UpperBoundary"]
        base_precision = mapping["BasePrecision"]

        # Example DK => 0.5
        # Example CA => 0.05
        min_cash_unit = mapping["MinCashUnit"]

        # Checks whether alignment is needed
        # Use of Decimal because of python precision limitation withs small float numbers and modulo operator
        # Example DK => 99.63 => remainder 0.13 => not 0.0 => Alignment required
        # Example CA => 99.63 => remainder 0.03 => not 0.0 => Alignment required
        remainder = float(Decimal(str(round(amount, 2))) % Decimal(str(min_cash_unit)))
        if remainder == 0.0:
            return amount

        # Calculates base depending at configured base precision
        # Example DK => 99.63 => base 99.00
        # Example CA => 99.63 => base 99.60
        base_cutoff = 1 / base_precision
        base_amount = round(int(amount * base_cutoff) / base_cutoff, 2)

        # Calculates the remainder relative to the base
        # Example DK => 99.63 => remainder 0.63
        # Example CA => 99.63 => remainder 0.03
        remainder = round(amount - base_amount, 2)
        alignment_direction = 1
        if remainder < 0:
            # Negate alignment direction because of negative amount
            alignment_direction = -1
            # Always use positive remainder to determine correct position within boundaries
            remainder = abs(remainder)

            # Performs alignment within the configured boundaries
        # Example DK => 99.00 - 99.24
        if remainder < lower_boundary:
            # Example DK => 99.00
            return round(base_amount, 2)
        # Example DK => 99.25 - 99.74
        elif lower_boundary <= remainder <= upper_boundary:
            # Example DK => 99.50
            return round(base_amount + (min_cash_unit * alignment_direction), 2)
        # Example DK => 99.75 - 99.99
        else:
            # Example DK => 100.00
            return round(base_amount + (2 * min_cash_unit * alignment_direction), 2)
