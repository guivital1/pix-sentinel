CREATE EXTERNAL TABLE IF NOT EXISTS pix_sentinel.scored_transactions (
  transaction_id string,
  occurred_at string,
  sender_id string,
  receiver_id string,
  amount_brl double,
  device_id string,
  city string,
  account_age_days int,
  transactions_last_hour int,
  is_new_device boolean,
  risk_score int,
  risk_level string,
  reasons array<string>
)
PARTITIONED BY (year string, month string, day string, hour string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://REPLACE_WITH_BUCKET/silver/';

-- Discover the Hive-style partitions written by the consumer.
MSCK REPAIR TABLE pix_sentinel.scored_transactions;

-- Portfolio evidence query: alerts by city.
SELECT
  city,
  count(*) AS transactions,
  sum(CASE WHEN risk_score >= 45 THEN 1 ELSE 0 END) AS alerts,
  round(avg(risk_score), 2) AS average_risk
FROM pix_sentinel.scored_transactions
GROUP BY city
ORDER BY alerts DESC;

