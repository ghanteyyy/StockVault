from decimal import Decimal, ROUND_HALF_UP

D = Decimal

charges = {
    "broker": {
        "min_brokerage": D("10.00"),
        "slabs": [
            (D("50000"), D("0.0036")),
            (D("500000"), D("0.0033")),
            (D("2000000"), D("0.0031")),
            (D("10000000"), D("0.0027")),
            (D("Infinity"), D("0.0024")),
        ],
    },
    "sebon_fee_rate": D("0.00015"),  # 0.015%
    "dp_charge": D("25.00"),
    "capital_gains_tax": {
        "365 days or less (5%)": D("0.05"),   # Holding ≤ 1 year
        "More than 365 days (3.75%)": D("0.0375"),   # Holding > 1 year
        "institutional": D("0.10"),
    },
}


def money(value):
    """
    Round monetary values to two decimal places.
    """

    return D(value).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def get_brokerage(transaction_amount):
    transaction_amount = D(str(transaction_amount))

    for upper_limit, rate in charges["broker"]["slabs"]:
        if transaction_amount <= upper_limit:
            commission = transaction_amount * rate

            return money(
                max(commission, charges["broker"]["min_brokerage"])
            )

    raise ValueError("Unable to determine brokerage rate")


def calculate_trade_charges(transaction_amount):
    transaction_amount = D(str(transaction_amount))

    brokerage = get_brokerage(transaction_amount)
    sebon_fee = money(
        transaction_amount * charges["sebon_fee_rate"]
    )

    dp_charge = charges["dp_charge"]

    return {
        "brokerage": brokerage,
        "sebon_fee": sebon_fee,
        "dp_charge": dp_charge,
    }


def buy_shares_calculation(share_quantity, price_per_share, buy_type="secondary"):
    quantity = D(str(share_quantity))
    price = D(str(price_per_share))
    buy_type = buy_type.strip().lower()

    gross_purchase_amount = money(quantity * price)

    # Primary-market purchase: IPO/FPO/right share application
    if buy_type in {"ipo", "fpo", "right"}:
        return {
            "gross_purchase_amount": gross_purchase_amount,
            "brokerage_commission": D("0.00"),
            "sebon_commission": D("0.00"),
            "dp_charge": D("0.00"),
            "total_amount": gross_purchase_amount,
        }

    if buy_type != "secondary":
        raise ValueError("buy_type must be secondary, ipo, fpo, or right")

    trade_charges = calculate_trade_charges(
        gross_purchase_amount
    )

    total_amount = money(
        gross_purchase_amount
        + trade_charges["brokerage"]
        + trade_charges["sebon_fee"]
        + trade_charges["dp_charge"]
    )

    return {
        "gross_purchase_amount": gross_purchase_amount,
        "brokerage_commission": trade_charges["brokerage"],
        "sebon_commission": trade_charges["sebon_fee"],
        "dp_charge": trade_charges["dp_charge"],
        "total_amount": total_amount,
    }


def sell_share_calculation(buy_type, share_quantity, purchase_price, selling_price, cgt_type):
    """
    purchase_price must be the raw per-share purchase price.

    For holdings acquired in multiple transactions, use the official
    WACC/cost basis from MeroShare instead of rebuilding it here.
    """

    buy_type = buy_type.strip().lower()
    quantity = D(str(share_quantity))
    purchase_price = D(str(purchase_price))
    selling_price = D(str(selling_price))

    if cgt_type not in charges["capital_gains_tax"]:
        raise ValueError(
            f"Invalid CGT type. Use one of: "
            f"{list(charges['capital_gains_tax'])}"
        )

    # Calculate acquisition cost
    purchase_result = buy_shares_calculation(
        share_quantity=quantity,
        price_per_share=purchase_price,
        buy_type=buy_type,
    )
    purchase_cost = purchase_result["total_amount"]

    # Calculate selling charges
    gross_selling_amount = money(quantity * selling_price)
    selling_charges = calculate_trade_charges(
        gross_selling_amount
    )

    net_amount_before_cgt = money(
        gross_selling_amount
        - selling_charges["brokerage"]
        - selling_charges["sebon_fee"]
        - selling_charges["dp_charge"]
    )

    gain_before_tax = money(net_amount_before_cgt - purchase_cost)

    # CGT cannot be negative
    taxable_gain = max(gain_before_tax, D("0.00"))
    capital_gain_tax = money(taxable_gain * charges["capital_gains_tax"][cgt_type])
    final_receivable_amount = money(net_amount_before_cgt - capital_gain_tax)
    profit_after_tax = money(final_receivable_amount - purchase_cost)

    return {
        "gross_purchase_amount": purchase_result["gross_purchase_amount"],
        "total_purchase_cost": purchase_cost,
        "gross_selling_amount": gross_selling_amount,
        "brokerage_commission": selling_charges["brokerage"],
        "sebon_commission": selling_charges["sebon_fee"],
        "dp_charge": selling_charges["dp_charge"],
        "gain_before_tax": gain_before_tax,
        "taxable_gain": money(taxable_gain),
        "capital_gain_tax": capital_gain_tax,
        "profit_after_tax": profit_after_tax,
        "final_receivable_amount": final_receivable_amount,
        "purchase_details": purchase_result,
    }
