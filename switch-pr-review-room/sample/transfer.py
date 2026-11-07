"""Deliberately buggy sample used to demo the reviewer and tester agents.

DO NOT use this code anywhere real. It has these problems on purpose:
  1. SQL injection: every argument is interpolated into the query string.
  2. Not atomic: the debit and credit run as two separate statements with
     no transaction, so a failure on the second one loses money.
  3. No amount validation: a negative amount reverses the transfer, and
     zero or non-numeric values pass through.
  4. No balance check (overdrafts allowed) and no rows-affected check.
  5. Always returns "ok", even if an account does not exist.
"""


def transfer(db, from_acct, to_acct, amount):
    query = f"UPDATE accounts SET balance = balance - {amount} WHERE id = '{from_acct}'"
    db.execute(query)
    query2 = f"UPDATE accounts SET balance = balance + {amount} WHERE id = '{to_acct}'"
    db.execute(query2)
    return "ok"
