# Agent and human contribution guide

Contributions should improve the research engine without making unsupported claims about prediction or causality.

## Suggested independent review tasks

1. Audit point-in-time behavior and propose tests for look-ahead leakage.
2. Review path aggregation for correlated-path double counting.
3. Propose a statistically defensible way to estimate edge uncertainty.
4. Review the API boundary for safe separation from broker execution.
5. Check documentation for claims that overstate causal identification.

## Contribution rules

- Include a failing test for every reported bug when practical.
- Preserve source timestamps and provenance.
- Do not add credentials, private financial data, or broker execution code.
- Do not call scenario scores predictions or investment recommendations.
- Document assumptions, limitations, and reproducibility details.
