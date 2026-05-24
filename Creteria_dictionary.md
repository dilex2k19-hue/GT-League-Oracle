# Criteria Dictionary: public.match_features

This dictionary defines every column used in our features table[cite: 5]. It acts as our guide for understanding how reality is structured before feeding data to our Machine Learning models.

---

## 1. Core Identifiers & Metadata

### match_id
*   **Definition:** The unique identification string assigned to a single match record[cite: 5].
*   **Example:** `'GT-20260523-0041'`
*   **AI Value:** Prevents duplicate rows and uniquely logs the entry. It is a key identifier, not a pattern feature.

### timestamp
*   **Definition:** The exact date and calendar time when the match officially kicked off[cite: 5].
*   **Example:** `2026-05-23 14:15:00`
*   **AI Value:** Ensures we sort data chronologically so the system looks into the past, preventing future data leakage.

### home_player
*   **Definition:** The gaming handle/name of the competitor assigned to the Home side of the bracket[cite: 5].
*   **Example:** `'Siri'`
*   **AI Value:** Allows the program to lookup and separate this individual player's histories.

### away_player
*   **Definition:** The gaming handle/name of the competitor assigned to the Away side of the bracket[cite: 5].
*   **Example:** `'Mamba'`
*   **AI Value:** Allows the program to lookup and separate the opponent's historical records.

---

## 2. Home Player Form (Last 10 Matches Overall)

### home_win_rate_l10
*   **Definition:** The percentage of matches won by the Home player over their last 10 games overall[cite: 5].
*   **Example:** `0.70` (Won 7 out of 10 matches).
*   **AI Value:** Measures general winning momentum and baseline current skill level.

### home_draw_rate_l10
*   **Definition:** The percentage of matches tied by the Home player over their last 10 games overall[cite: 5].
*   **Example:** `0.20` (Drew 2 out of 10 matches).
*   **AI Value:** Identifies defensive or risk-averse playstyles prone to stalling.

### home_loss_rate_l10
*   **Definition:** The percentage of matches lost by the Home player over their last 10 games overall[cite: 5].
*   **Example:** `0.10` (Lost 1 out of 10 matches).
*   **AI Value:** Flags clear negative performance slumps.

### home_avg_goals_l10
*   **Definition:** The average number of goals scored per match by the Home player over their last 10 games overall[cite: 5].
*   **Example:** `2.40` goals per match.
*   **AI Value:** Quantifies general offensive power and high-scoring potential.

### home_avg_conceded_l10
*   **Definition:** The average number of goals allowed by the Home player over their last 10 games overall[cite: 5].
*   **Example:** `1.20` goals allowed per match.
*   **AI Value:** Quantifies defensive vulnerability or tightness.

### home_over25_rate_l10
*   **Definition:** The percentage of the Home player's last 10 games that resulted in 3 or more total goals combined[cite: 5].
*   **Example:** `0.80` (8 out of 10 matches ended Over 2.5).
*   **AI Value:** Directly alerts the AI to high-scoring game styles for Over 2.5 betting.

### home_win_streak_current
*   **Definition:** The consecutive number of victories the Home player holds up to this match kickoff[cite: 5].
*   **Example:** `3` (Won 3 straight games; resets to 0 on any loss or draw).
*   **AI Value:** Tracks hot streaks or strong psychological confidence.

### home_over_streak_current
*   **Definition:** The consecutive number of matches played by the Home player that ended Over 2.5 goals[cite: 5].
*   **Example:** `4` (Last 4 games had 3+ goals).
*   **AI Value:** Captures sudden shifts toward high-tempo, chaotic match play.

---

## 3. Home Player Side Split (Strictly Home Games)

### home_win_rate_side_l10
*   **Definition:** The percentage of matches won by the Home player over their last 10 matches *strictly where they played as Home*[cite: 5].
*   **Example:** `0.80` (Won 8 out of 10 home matches).
*   **AI Value:** Isolates specific comfort levels on the Home court bracket side.

### home_avg_goals_side_l10
*   **Definition:** The average number of goals scored by the Home player over their last 10 matches *strictly where they played as Home*[cite: 5].
*   **Example:** `3.10` goals per match.
*   **AI Value:** Discovers if a player behaves much more aggressively when given Home positioning.

---

## 4. Away Player Form (Last 10 Matches Overall)

### away_win_rate_l10
*   **Definition:** The percentage of matches won by the Away player over their last 10 games overall[cite: 5].
*   **Example:** `0.50` (Won 5 out of 10 matches).
*   **AI Value:** Provides the current baseline recent strength of the opponent.

### away_draw_rate_l10
*   **Definition:** The percentage of matches tied by the Away player over their last 10 games overall[cite: 5].
*   **Example:** `0.30` (Drew 3 out of 10 matches).
*   **AI Value:** Evaluates the opponent's tendency to split points or lock up.

### away_loss_rate_l10
*   **Definition:** The percentage of matches lost by the Away player over their last 10 games overall[cite: 5].
*   **Example:** `0.20` (Lost 2 out of 10 matches).
*   **AI Value:** Indicates if the opponent is currently drop-prone.

### away_avg_goals_l10
*   **Definition:** The average number of goals scored per match by the Away player over their last 10 games overall[cite: 5].
*   **Example:** `1.80` goals per match.
*   **AI Value:** Evaluates if the opponent can contribute sufficient goals for Over 2.5 setups.

### away_avg_conceded_l10
*   **Definition:** The average number of goals allowed by the Away player over their last 10 games overall[cite: 5].
*   **Example:** `1.90` goals allowed per match.
*   **AI Value:** Uncovers weak defensive capabilities in the Away player.

### away_over25_rate_l10
*   **Definition:** The percentage of the Away player's last 10 games that resulted in 3 or more total goals combined[cite: 5].
*   **Example:** `0.60` (6 out of 10 matches ended Over 2.5).
*   **AI Value:** Measures the frequency of high-scoring games occurring around the opponent.

### away_win_streak_current
*   **Definition:** The consecutive number of victories the Away player holds up to this match kickoff[cite: 5].
*   **Example:** `0` (Lost or drew their last match).
*   **AI Value:** Checks the opponent's immediate psychological momentum.

### away_over_streak_current
*   **Definition:** The consecutive number of matches played by the Away player that ended Over 2.5 goals[cite: 5].
*   **Example:** `0` (Their last match ended under 2.5 goals).
*   **AI Value:** Tracks if the opponent is currently involved in low-scoring, tighter matchups.

---

## 5. Away Player Side Split (Strictly Away Games)

### away_win_rate_side_l10
*   **Definition:** The percentage of matches won by the Away player over their last 10 matches *strictly where they played as Away*[cite: 5].
*   **Example:** `0.30` (Won only 3 out of 10 away matches).
*   **AI Value:** Identifies players who struggle severely when traveling or assigned the Away layout.

### away_avg_goals_side_l10
*   **Definition:** The average number of goals scored by the Away player over their last 10 matches *strictly where they played as Away*[cite: 5].
*   **Example:** `1.10` goals per match.
*   **AI Value:** Evaluates if an opponent drops their attacking intensity when on the Away bracket side.

---

## 6. All-Time Head-to-Head (H2H) Context

### h2h_matches_played
*   **Definition:** The absolute total number of direct meetings between these two specific players recorded in the past[cite: 5].
*   **Example:** `24` matches.
*   **AI Value:** Establishes the credibility weight of the H2H data history.

### h2h_home_wins
*   **Definition:** The total number of all-time meetings won by the current `home_player` when facing the current `away_player`[cite: 5].
*   **Example:** `14` wins.
*   **AI Value:** Highlights historical mental superiority or tactical advantage for the Home player.

### h2h_away_wins
*   **Definition:** The total number of all-time meetings won by the current `away_player` when facing the current `home_player`[cite: 5].
*   **Example:** `6` wins.
*   **AI Value:** Highlights historical mental dominance for the Away player.

### h2h_draws
*   **Definition:** The total number of all-time head-to-head matches between these two that ended in a tie[cite: 5].
*   **Example:** `4` draws.
*   **AI Value:** Shows if the specific pairing styles frequently gridlock each other.

### h2h_avg_goals
*   **Definition:** The average combined total goals scored per match when these two specific players meet[cite: 5].
*   **Example:** `3.45` goals.
*   **AI Value:** A highly predictive indicator of match tempo specifically when these two square off.

### h2h_over25_rate
*   **Definition:** The percentage of all historical face-offs between these two that ended with 3 or more total goals[cite: 5].
*   **Example:** `0.75` (75% of past matchups went Over 2.5).
*   **AI Value:** Offers direct market historical alignment for the specific matchup.

---

## 7. Comparative Differences

### win_rate_diff
*   **Definition:** The exact mathematical value of `home_win_rate_l10` minus `away_win_rate_l10`[cite: 5].
*   **Example:** `0.70 - 0.50 = 0.20` (Positive means Home has an edge; negative favors Away).
*   **AI Value:** Machine learning tree models find direct mathematical margins extremely easy to split on.

### avg_goals_diff
*   **Definition:** The exact mathematical value of `home_avg_goals_l10` minus `away_avg_goals_l10`[cite: 5].
*   **Example:** `2.40 - 1.80 = 0.60`
*   **AI Value:** Instantly highlights relative attacking superiority margins.

### over25_rate_diff
*   **Definition:** The exact mathematical value of `home_over25_rate_l10` minus `away_over25_rate_l10`[cite: 5].
*   **Example:** `0.80 - 0.60 = 0.20`
*   **AI Value:** Highlights discrepancies in how often both players trigger high-scoring match paces.

---

## 8. General Match Context

### match_hour
*   **Definition:** The specific hour component extracted from the timestamp representing local kickoff hour (0-23)[cite: 5].
*   **Example:** `16` (4:00 PM).
*   **AI Value:** Identifies diurnal performance variations (e.g., players who decline late at night).

---

## 9. Machine Learning Target Labels

### target_home_win
*   **Definition:** The true training label indicating if the Home player won the match[cite: 5].
*   **Example:** `1` (True, Home won), `0` (False, it was a draw or Away won).
*   **AI Value:** What the AI attempts to predict for the Home Win model.

### target_away_win
*   **Definition:** The true training label indicating if the Away player won the match[cite: 5].
*   **Example:** `1` (True, Away won), `0` (False, it was a draw or Home won).
*   **AI Value:** What the AI attempts to predict for the Away Win model.

### target_over25
*   **Definition:** The true training label indicating if combined goals equaled or exceeded 3[cite: 5].
*   **Example:** `1` (Total goals >= 3), `0` (Total goals < 3).
*   **AI Value:** What the AI attempts to predict for our Over 2.5 Goals model.

---

## 10. Volume & Fatigue Tracking

### home_daily_matches_played
*   **Definition:** The running total count of matches the Home player has completed on this specific calendar date prior to this match[cite: 5].
*   **Example:** `7` matches.
*   **AI Value:** Captures human mental strain, exhaustion, or active emotional tilt.

### away_daily_matches_played
*   **Definition:** The running total count of matches the Away player has completed on this specific calendar date prior to this match[cite: 5].
*   **Example:** `1` match.
*   **AI Value:** Flags if the opponent enters the match completely fresh and clear-headed.

---

## 11. Recent Head-to-Head (Last 5 Meetings)

### h2h_l5_played
*   **Definition:** The actual count of recent matches played between these two up to a maximum cap of 5[cite: 5].
*   **Example:** `5` matches seen.
*   **AI Value:** Acts as a confidence boundary indicator for the recent matchup trend.

### h2h_l5_home_wins
*   **Definition:** The total number of wins by the current `home_player` within the last 5 direct head-to-head meetings[cite: 5].
*   **Example:** `1` win.
*   **AI Value:** Exposes if old historical metrics are failing to match modern performance adjustments.

### h2h_l5_away_wins
*   **Definition:** The total number of wins by the current `away_player` within the last 5 direct head-to-head meetings[cite: 5].
*   **Example:** `4` wins.
*   **AI Value:** Flags an opponent who has recently mastered or decoded the Home player's strategy.

### h2h_l5_draws
*   **Definition:** The total number of recent matches between these two that ended in stalemate within the 5-game window[cite: 5].
*   **Example:** `0` draws.
*   **AI Value:** Tracks recent stalemating likelihoods for tactical setups.

### h2h_l5_avg_goals
*   **Definition:** The average total combined goals across *only* the last 5 direct encounters[cite: 5].
*   **Example:** `4.20` goals.
*   **AI Value:** Highly accurate gauge for short-term schematic clashes.

### h2h_l5_over25_rate
*   **Definition:** The exact percentage of the last 5 direct meetings that crossed the Over 2.5 threshold[cite: 5].
*   **Example:** `1.00` (All 5 recent meetings went Over 2.5).
*   **AI Value:** Pinpoints immediate stylistic trends toward high-scoring encounters.

---

## 12. Scoring Consistency & Defensive Resilience

### home_scored_in_l5_rate
*   **Definition:** The percentage of the last 5 games overall where the Home player scored 1 or more goals[cite: 5].
*   **Example:** `1.00` (Scored at least once in all 5 recent matches).
*   **AI Value:** Identifies scoring dependency and isolates players who rarely suffer complete goal droughts.

### away_scored_in_l5_rate
*   **Definition:** The percentage of the last 5 games overall where the Away player scored 1 or more goals[cite: 5].
*   **Example:** `0.60` (Went completely scoreless in 2 out of 5 recent matches).
*   **AI Value:** Signals low scoring consistency or susceptibility to being blanked.

### home_clean_sheet_rate_l10
*   **Definition:** The frequency with which the Home player allowed exactly 0 goals across their last 10 overall matches[cite: 5].
*   **Example:** `0.30` (Kept a clean sheet in 3 out of 10 matches).
*   **AI Value:** Measures defensive lockdown reliability under current form.

### away_clean_sheet_rate_l10
*   **Definition:** The frequency with which the Away player allowed exactly 0 goals across their last 10 overall matches[cite: 5].
*   **Example:** `0.00` (Conceded at least 1 goal in every single one of their last 10 matches).
*   **AI Value:** Flags absolute defensive instability or inability to preserve a clean sheet.

---

## 13. Recency-Weighted Momentum

### home_weighted_winrate
*   **Definition:** A calculated win rate over recent form where matches closer in time are assigned heavier mathematical value than older matches[cite: 5].
*   **Example:** `0.87` (Even if their normal win rate is 70%, their immediate performance today elevates the value).
*   **AI Value:** Extremely reactive feature to capture immediate shifts in performance speed or form.

### away_weighted_winrate
*   **Definition:** A calculated win rate over recent opponent form prioritizing closer temporal intervals[cite: 5].
*   **Example:** `0.42`
*   **AI Value:** Allows the model to see if the opponent is entering the match on a downward trajectory.

---

## 14. Sample Size Certainty (The Core Confidence Safety Net)

### home_matches_seen_l10
*   **Definition:** The actual count of total matches historical tracking has recorded for the Home player within the intended 10 rolling match window[cite: 5].
*   **Example:** `3` matches (Capped at 10 max).
*   **AI Value:** Key indicator for cold starts. Tells the model whether to trust rates like `home_win_rate_l10`.

### away_matches_seen_l10
*   **Definition:** The actual count of total matches historical tracking has recorded for the Away player within the 10 rolling match window[cite: 5].
*   **Example:** `10` matches.
*   **AI Value:** Confirms high data visibility for the opponent's metrics.

### home_side_matches_seen
*   **Definition:** The absolute total volume of matches recorded for the Home player specifically in the Home seat[cite: 5].
*   **Example:** `1` match.
*   **AI Value:** Protects the AI from overfitting side split percentages when data is scarce.

### away_side_matches_seen
*   **Definition:** The absolute total volume of matches recorded for the Away player specifically in the Away seat[cite: 5].
*   **Example:** `84` matches.
*   **AI Value:** Signals that the Away player has extensive side-specific data points available.

---

## 15. Macro Activity Volume (Historical Windows)

### home_matches_last_24h
*   **Definition:** Total historical matches logged by the Home player in the rolling 24 hours preceding kickoff[cite: 5].
*   **Example:** `14` matches.
*   **AI Value:** Measures deep warm-up fatigue or high-intensity play sessions.

### away_matches_last_24h
*   **Definition:** Total historical matches logged by the Away player in the rolling 24 hours preceding kickoff[cite: 5].
*   **Example:** `2` matches.
*   **AI Value:** Verifies if the opponent has spent the day away from active competitive play.

### home_matches_last_7d
*   **Definition:** Total matches logged by the Home player over the preceding rolling 7-day period[cite: 5].
*   **Example:** `110` matches.
*   **AI Value:** Determines if the player is actively grinding the current tournament cycle (highly practiced) or inactive.

### away_matches_last_7d
*   **Definition:** Total matches logged by the Away player over the preceding rolling 7-day period[cite: 5].
*   **Example:** `12` matches.
*   **AI Value:** Distinguishes high-volume competitors from rare or irregular participants.










                              Table "public.match_features"
          Column           |            Type             | Collation | Nullable | Default 
---------------------------+-----------------------------+-----------+----------+---------
 match_id                  | character varying(50)       |           | not null | 
 timestamp                 | timestamp without time zone |           |          | 
 home_player               | character varying(100)      |           |          | 
 away_player               | character varying(100)      |           |          | 
 home_win_rate_l10         | double precision            |           |          | 
 home_draw_rate_l10        | double precision            |           |          | 
 home_loss_rate_l10        | double precision            |           |          | 
 home_avg_goals_l10        | double precision            |           |          | 
 home_avg_conceded_l10     | double precision            |           |          | 
 home_over25_rate_l10      | double precision            |           |          | 
 home_win_streak_current   | integer                     |           |          | 
 home_over_streak_current  | integer                     |           |          | 
 home_win_rate_side_l10    | double precision            |           |          | 
 home_avg_goals_side_l10   | double precision            |           |          | 
 away_win_rate_l10         | double precision            |           |          | 
 away_draw_rate_l10        | double precision            |           |          | 
 away_loss_rate_l10        | double precision            |           |          | 
 away_avg_goals_l10        | double precision            |           |          | 
 away_avg_conceded_l10     | double precision            |           |          | 
 away_over25_rate_l10      | double precision            |           |          | 
 away_win_streak_current   | integer                     |           |          | 
 away_over_streak_current  | integer                     |           |          | 
 away_win_rate_side_l10    | double precision            |           |          | 
 away_avg_goals_side_l10   | double precision            |           |          | 
 h2h_matches_played        | integer                     |           |          | 
 h2h_home_wins             | integer                     |           |          | 
 h2h_away_wins             | integer                     |           |          | 
 h2h_draws                 | integer                     |           |          | 
 h2h_avg_goals             | double precision            |           |          | 
 h2h_over25_rate           | double precision            |           |          | 
 win_rate_diff             | double precision            |           |          | 
 avg_goals_diff            | double precision            |           |          | 
 over25_rate_diff          | double precision            |           |          | 
 match_hour                | integer                     |           |          | 
 target_home_win           | integer                     |           |          | 
 target_away_win           | integer                     |           |          | 
 target_over25             | integer                     |           |          | 
 home_daily_matches_played | integer                     |           |          | 0
 away_daily_matches_played | integer                     |           |          | 0
 h2h_l5_played             | integer                     |           |          | 0
 h2h_l5_home_wins          | integer                     |           |          | 0
 h2h_l5_away_wins          | integer                     |           |          | 0
 h2h_l5_draws              | integer                     |           |          | 0
 h2h_l5_avg_goals          | double precision            |           |          | 
 h2h_l5_over25_rate        | double precision            |           |          | 
 home_scored_in_l5_rate    | double precision            |           |          | 
 away_scored_in_l5_rate    | double precision            |           |          | 
 home_clean_sheet_rate_l10 | double precision            |           |          | 
 away_clean_sheet_rate_l10 | double precision            |           |          | 
 home_weighted_winrate     | double precision            |           |          | 
 away_weighted_winrate     | double precision            |           |          | 
 home_matches_seen_l10     | integer                     |           |          | 0
 away_matches_seen_l10     | integer                     |           |          | 0
 home_side_matches_seen    | integer                     |           |          | 0
 away_side_matches_seen    | integer                     |           |          | 0
 home_matches_last_24h     | integer                     |           |          | 0
 away_matches_last_24h     | integer                     |           |          | 0
 home_matches_last_7d      | integer                     |           |          | 0
 away_matches_last_7d      | integer                     |           |          | 0
Indexes:
    "match_features_pkey" PRIMARY KEY, btree (match_id)

(END)




1. Rolling Form Basics (The `l10` Concept)
Before looking at the specific columns, it is important to understand what `l10` and `double precision` mean:
*   **`l10` (Last 10):** The system only looks at the player's most recent 10 matches overall. This captures their "current form" or immediate momentum rather than their lifetime history.
*   **`double precision`:** Database terminology for a decimal number (like 0.75 or 2.4) instead of a whole number (like 1 or 2).