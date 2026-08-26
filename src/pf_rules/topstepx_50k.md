# TopstepX 50K Account Rules

Last updated: August 2026 (sourced from topstep.com)

## Trading Combine (Evaluation)

| Parameter              | Value                  |
|------------------------|------------------------|
| Account Size           | $50,000                |
| Profit Target          | $3,000                 |
| Maximum Loss Limit     | $2,000 (trailing, EOD) |
| Daily Loss Limit       | $1,000 (objective)     |
| Max Position Size      | 5 minis / 50 micros    |
| Consistency Target     | Best day < 50% of profit target |
| Subscription           | ~$49/month             |
| Minimum Days to Pass   | 2                      |

- **Maximum Loss Limit (MLL):** Trails your highest end-of-day balance. Starts at $48,000. Once MLL reaches $50,000 (starting balance), it locks and stops trailing. Hitting or going below MLL permanently closes the account.
- **Daily Loss Limit (DLL):** $1,000 max loss per trading day. Auto-liquidates for the day but does NOT count as a rule violation. **Not applicable on TopstepX platform** (removed Aug 2024 for new/reset accounts).
- **Consistency Target:** Best single day must stay below 50% of profit target ($1,500).
- **Micro-to-Mini Ratio:** 1 mini = 10 micros against position limit.

## Express Funded Account (XFA)

### Account Structure

| Parameter              | Value                  |
|------------------------|------------------------|
| Starting Balance       | $0                     |
| Max Loss Limit         | -$2,000                |
| Max Active XFAs        | 5 simultaneously       |
| Activation Fee         | $149 one-time          |

The XFA starts at $0. Balance can go negative down to -$2,000 (the MLL). If MLL rises to $0, the account locks at $0.

### Scaling Plan (XFA)

| Account Balance | Max Contracts (Minis) | Max Contracts (Micros) |
|-----------------|----------------------|------------------------|
| $0 – $1,500    | 2                    | 20                     |
| $1,500 – $2,000| 3                    | 30                     |
| $2,000+        | 5                    | 50                     |

Contract limits update at end of each trading day based on balance. They do not increase mid-session.

### Trading Hours & Products

- **Trading hours:** 5:00 PM CT – 3:10 PM CT (next day), Sunday–Friday
- **Position close deadline:** 3:10 PM CT daily
- **No overnight or weekend holds**
- **Permitted products:** CME Group futures (CME, NYMEX, COMEX, CBOT) — equity, FX, agricultural, energy, metals
- **Holiday schedules:** Must follow CME holiday trading schedules

### Payout Rules

Two payout paths available:

#### Standard Path

| Requirement         | Value                              |
|---------------------|------------------------------------|
| Winning Days        | 5 days with $150+ profit each      |
| Max Payout          | 50% of balance, up to $5,000       |
| Profit Split        | 90/10 (trader/Topstep)             |
| First $10K profits  | 100% to trader                     |
| Minimum Payout      | $125                               |

#### Consistency Path

| Requirement         | Value                              |
|---------------------|------------------------------------|
| Minimum Trading Days| 3 days                             |
| Consistency Target  | 40% (best day < 40% of total P&L)  |
| Max Payout          | 50% of balance, up to $6,000       |
| Profit Split        | 90/10 (trader/Topstep)             |

After payout approval, the amount is subtracted from account balance. After first payout, MLL is set to $0 (starting balance).

### Back2Funded

If you lose your XFA before first payout:

- **Reactivation fee:** $599 (50K)
- **Max reactivations:** 2 per XFA
- **Window:** 7 calendar days from account closure
- **Non-refundable**

## Key Restrictions

- All accounts must be under 1 Topstep profile (single profile policy)
- Automated trading allowed but at your own risk
- Prohibited: account stacking, exploitative strategies, unprofessional behavior
- At least one trade every 30 days to keep XFA open
- Up to 2 resets per account per calendar day

## Sources

- https://www.topstep.com/express-funded-account-rules
- https://help.topstep.com/en/articles/8284197-trading-combine-parameters
- https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan
