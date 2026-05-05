-- Initial schema placeholder
CREATE TABLE IF NOT EXISTS entry_record (
  id SERIAL PRIMARY KEY,
  reference_code VARCHAR(64),
  amount numeric,
  rate numeric,
  event_date date
);
