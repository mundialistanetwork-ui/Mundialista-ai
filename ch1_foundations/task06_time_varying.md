\# Task 6: Why Flat Poisson Isn't Enough



\## Q1: If goals were truly uniform across 90 minutes, what fraction would fall in each half?

If goals were uniform, exactly 50% would fall in the first half (minutes 1-45) and 50% in the second half (minutes 46-90), since each half is 45 minutes.



\## Q2: In reality, 53-55% of goals occur in the second half. What does this tell us?

This tells us the assumption of a constant λ throughout the match is wrong. The real goal-scoring rate is higher in the second half than the first half, meaning λ changes over time.



\## Q3: Three reasons why goal-scoring intensity increases in the final 10 minutes:

1\. Tired defenders make more mistakes and leave gaps in the defense

2\. Losing teams push everyone forward desperately seeking an equalizer, creating open play

3\. Substitutions bring fresh attacking players onto the pitch against tired defenders



\## Q4: What is an "inhomogeneous Poisson process"?

An inhomogeneous (or non-homogeneous) Poisson process is a Poisson process where the rate parameter λ changes over time instead of staying constant. In football terms, instead of saying "Jamaica scores at 1.3 goals per 90 minutes evenly," we say "Jamaica scores at different rates during different phases of the match." The total expected goals stays the same, but the timing of when goals are likely shifts based on a time-varying rate function λ(t).



\## Q5: What must be true about the SUM of all λ(t) values?

The sum of all 90 individual minute-by-minute λ(t) values must equal the total expected goals for the match (e.g., 1.3). This ensures that even though we redistribute when goals are likely to happen, the overall expected number of goals remains correct.

