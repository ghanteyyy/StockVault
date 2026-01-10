charges = {
    "broker": {
        "min_brokerage": 10,
        "slabs": [
            {"up_to": 50_000, "rate": 0.0036},
            {"up_to": 500_000, "rate": 0.0033},
            {"up_to": 2_000_000, "rate": 0.0031},
            {"up_to": 10_000_000, "rate": 0.0027},
            {"up_to": float('inf'), "rate": 0.0024},
        ],
    },
    "sebon_fee_rate": 0.00015,  # 0.015%
    "dp_charge": 25,            # per scrip per settlement
    "capital_gains_tax": {
        "Less than a year (7.5%)": 0.075,
        "More than a year (5%)": 0.05,
        "Institutional (10%)": 0.10,
    }
}


def format_price(value):
    """
    Format a number to 2 decimal places for currency
    """

    return round(value, 2)


def buy_shares_calculation(share_quantity, price_per_share, buy_type):
    if buy_type.lower() == 'ipo':
        return {'total_amount': format_price(share_quantity * price_per_share)}

    total_purchase_amount = share_quantity * price_per_share

    # Brokerage Commission Calculation
    brokerage_rate = 0

    for slab in charges["broker"]["slabs"]:
        if total_purchase_amount <= slab["up_to"]:
            brokerage_rate = slab["rate"]
            break

    brokerage_commission = total_purchase_amount * brokerage_rate
    brokerage_commission = max(brokerage_commission, charges["broker"]["min_brokerage"])  # Minimum brokerage is 10

    # SEBON Commission
    sebon_commission = total_purchase_amount * charges["sebon_fee_rate"]

    # DP Charge
    dp_charge = charges["dp_charge"]

    # Total Amount
    total_amount = total_purchase_amount + brokerage_commission + sebon_commission + dp_charge

    return {
        "total_purchase_amount": format_price(total_purchase_amount),
        "brokerage_commission": format_price(brokerage_commission),  # Fixed typo from original JS
        "sebon_commission": format_price(sebon_commission),
        "dp_charge": format_price(dp_charge),
        "total_amount": format_price(total_amount)
    }


def sell_share_calculation(buy_type, share_quantity, purchase_value, selling_price, cgt_value):
    secondary = None
    total_purchase_amount = share_quantity * purchase_value

    if buy_type == "secondary":
        brokerage_rate = 0

        for slab in charges["broker"]["slabs"]:
            if total_purchase_amount <= slab["up_to"]:
                brokerage_rate = slab["rate"]
                break

        brokerage_commission = total_purchase_amount * brokerage_rate
        brokerage_commission = max(brokerage_commission, charges["broker"]["min_brokerage"])  # Minimum brokerage is 10

        sebon_commission = total_purchase_amount * charges["sebon_fee_rate"]
        dp_charge = charges["dp_charge"]

        total_payable_amount = total_purchase_amount + brokerage_commission + sebon_commission + dp_charge

        secondary = {
            "secondary": {
                "total_payable_amount": format_price(total_payable_amount),
                "total_purchased_amount": format_price(total_purchase_amount),
                "brokerage_commission": format_price(brokerage_commission),
                "sebon_commission": format_price(sebon_commission),
                "dp_charge": format_price(dp_charge)
            }
        }

        total_purchase_amount = total_payable_amount

    total_selling_amount = share_quantity * selling_price

    # Brokerage Commission for Sale
    brokerage_rate = 0  # Default value (will be set in loop)
    for slab in charges["broker"]["slabs"]:
        if total_selling_amount <= slab["up_to"]:
            brokerage_rate = slab["rate"]
            break
    brokerage_commission = total_selling_amount * brokerage_rate

    sebon_commission = total_selling_amount * charges["sebon_fee_rate"]
    dp_charge = charges["dp_charge"]

    net_amount_before_cgt = total_selling_amount - brokerage_commission - sebon_commission - dp_charge

    capital_gain = net_amount_before_cgt - total_purchase_amount
    capital_gain_tax = charges["capital_gains_tax"][cgt_value] * capital_gain

    profit_amount = capital_gain - capital_gain_tax
    final_receivable_amount = net_amount_before_cgt - capital_gain_tax

    result = {
        "total_purchased_amount": format_price(total_purchase_amount),
        "total_selling_amount": format_price(total_selling_amount),
        "brokerage_commission": format_price(brokerage_commission),
        "sebon_commission": format_price(sebon_commission),
        "dp_charge": format_price(dp_charge),
        "profit_amount": format_price(profit_amount),
        "capital_gain_tax": format_price(capital_gain_tax),
        "final_receivable_amount": format_price(final_receivable_amount)
    }

    if secondary:
        result.update(secondary)

    return result
