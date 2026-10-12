-- Seed data for Cyrmonger Algo Fx
-- Requires: schema.sql applied, at least one admin user created via createsuperuser.
-- The admin user's user_id must be replaced in the created_by fields below.

-- Helper: insert a lesson with questions and options
DO $$
DECLARE
  v_admin_uuid UUID;
  v_lesson_id UUID;
BEGIN
  SELECT user_id INTO v_admin_uuid FROM "user" WHERE role = 'ADMIN' LIMIT 1;
  IF v_admin_uuid IS NULL THEN
    RAISE NOTICE 'No admin user found. Create one with createsuperuser.';
    RETURN;
  END IF;

  -- Lesson 1: What is Forex?
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('What is Forex?', 'basics', '# What is Forex?\n\nForex (foreign exchange) is the global market where currencies are traded. Traders buy one currency and sell another, hoping the exchange rate moves in their favour.\n\n## Key terms\n- **Pair**: Two currencies quoted together, e.g. EUR/USD.\n- **Pip**: A small price move. For most pairs one pip = 0.0001.\n- **Lot**: A standardised trade size. A standard lot = 100,000 units of the base currency.\n- **Spread**: The difference between the buy and sell price.\n\nRetail traders in Zimbabwe can access Forex through regulated platforms. Always check with the Reserve Bank of Zimbabwe on permitted channels.', 1, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What does "Forex" stand for?', 'Forex stands for foreign exchange.', 1
  UNION ALL SELECT v_lesson_id, 'What is a pip?', 'A pip is a small standardised price move.', 2
  UNION ALL SELECT v_lesson_id, 'What is a standard lot?', 'A standard lot is 100,000 units of the base currency.', 3;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Foreign exchange', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Foreign exchange market', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'A small price move', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, 'A broker', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, '100,000 units', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 3
  UNION ALL SELECT q.question_id, '1,000 units', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 3;

  -- Lesson 2: Reading a candlestick chart
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Reading a Candlestick Chart', 'charts', '# Candlestick charts\n\nEach candle shows open, high, low and close prices for a time period.\n\n- **Body**: open to close.\n- **Wick**: high and low.\n- **Green/white**: close > open (bullish).\n- **Red/black**: close < open (bearish).', 2, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What does a green candle mean?', 'Close was higher than open (bullish).', 1
  UNION ALL SELECT v_lesson_id, 'What are the wicks?', 'Wicks show the high and low prices.', 2;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Close higher than open', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Close lower than open', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'High and low prices', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, 'Open and close prices', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2;

  -- Lesson 3: Support and resistance
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Support and Resistance', 'charts', '# Support and resistance\n\n- **Support**: Price level where buying has been strong enough to stop a fall.\n- **Resistance**: Price level where selling has been strong enough to stop a rise.\n\nThese levels are zones, not exact numbers.', 3, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What is support?', 'A level where buying pressure has stopped a fall.', 1
  UNION ALL SELECT v_lesson_id, 'What is resistance?', 'A level where selling pressure has stopped a rise.', 2;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'A buying zone that stops a fall', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'A selling zone that stops a rise', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'A selling zone that stops a rise', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, 'A buying zone that stops a fall', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2;

  -- Lesson 4: Trends and market structure
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Trends and Market Structure', 'charts', '# Trends\n\n- **Uptrend**: Higher highs and higher lows.\n- **Downtrend**: Lower highs and lower lows.\n- **Range**: Price moves between support and resistance.\n\nTrade with the trend when possible.', 4, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What defines an uptrend?', 'Higher highs and higher lows.', 1;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Higher highs and higher lows', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Lower highs and lower lows', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1;

  -- Lesson 5: Head and shoulders
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Head and Shoulders', 'patterns', '# Head and shoulders\n\nA reversal pattern with three peaks: left shoulder, head (highest), right shoulder. A break below the neckline suggests a trend change from up to down.\n\n## Inverse head and shoulders\nSame shape inverted. A break above the neckline suggests a change from down to up.', 5, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'How many peaks in a head and shoulders pattern?', 'Three peaks: left shoulder, head, right shoulder.', 1
  UNION ALL SELECT v_lesson_id, 'What does inverse H&S suggest?', 'A potential move from downtrend to uptrend.', 2;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Three', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Two', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Downtrend to uptrend', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, 'Uptrend to downtrend', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2;

  -- Lesson 6: Double top and double bottom
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Double Top and Double Bottom', 'patterns', '# Double top\nTwo peaks at roughly the same level. A break below the valley suggests a downside move.\n\n# Double bottom\nTwo troughs at roughly the same level. A break above the peak suggests an upside move.', 6, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What does a double top suggest?', 'Potential bearish reversal.', 1
  UNION ALL SELECT v_lesson_id, 'What does a double bottom suggest?', 'Potential bullish reversal.', 2;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Bearish reversal', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Bullish continuation', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Bullish reversal', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, 'Bearish continuation', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2;

  -- Lesson 7: Triangles and breakouts
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Triangles and Breakouts', 'patterns', '# Ascending triangle\nFlat top, rising bottom. Break above resistance can signal continuation.\n\n# Descending triangle\nFlat bottom, falling top. Break below support can signal continuation.\n\nBreakouts on higher volume add confidence.', 7, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What characterises an ascending triangle?', 'Flat top with a rising bottom.', 1;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Flat top, rising bottom', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Falling top, flat bottom', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1;

  -- Lesson 8: Order blocks and fair value gaps
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Order Blocks and Fair Value Gaps', 'patterns', '# Order blocks\nAreas where institutions may have placed large orders. A bullish order block is a down candle before a big up move. A bearish order block is an up candle before a big down move.\n\n# Fair value gaps\nImbalances where price moves so fast that a gap is left. Price may return to fill the gap.', 8, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What is a bullish order block?', 'A down candle before a strong up move.', 1;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'A down candle before a strong up move', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'An up candle before a strong down move', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1;

  -- Lesson 9: Risk management
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Risk Management', 'risk', '# Risk per trade\nNever risk more than a small percentage of your account on one trade.\n\n- **Stop-loss**: Price level where you exit to limit loss.\n- **Take-profit**: Price level where you exit to lock in gain.\n- **Risk:reward**: Ratio of potential reward to risk. Aim for at least 1:1, ideally 1:2 or better.\n\nUse the platform risk calculator to plan positions.', 9, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What is a stop-loss?', 'A price level to limit a losing trade.', 1
  UNION ALL SELECT v_lesson_id, 'What is risk:reward?', 'Ratio of potential reward to the amount risked.', 2;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'A price level to exit a losing trade', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'A target for maximum profit', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Ratio of potential reward to risk', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2
  UNION ALL SELECT q.question_id, 'The amount of leverage used', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 2;

  -- Lesson 10: Trading psychology
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Trading Psychology', 'psychology', '# Common pitfalls\n\n- **Over-leveraging**: Using too much borrowed capital. One bad trade can wipe out your account.\n- **Revenge trading**: Trying to win back losses quickly. This usually leads to bigger losses.\n- **FOMO**: Fear of missing out. Chasing pumps often ends badly.\n\nStick to a plan. Keep a journal. Review it weekly.', 10, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What is revenge trading?', 'Trying to recover losses quickly with larger, riskier trades.', 1;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'Trying to recover losses quickly', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Trading only on fundamentals', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1;

  -- Lesson 11: Scams and signal groups
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Scams and Signal Groups', 'safety', '# Beware of "guaranteed" returns\n\n- No one can guarantee profit in Forex.\n- Signal groups that ask for upfront payment are often scams.\n- If it sounds too good to be true, it is.\n\nAlways use regulated platforms and verify who you are dealing with.', 11, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'Can anyone guarantee Forex profits?', 'No. All trading carries risk.', 1;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'No', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'Yes, with the right signals', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1;

  -- Lesson 12: Using AI analysis responsibly
  INSERT INTO lesson (title, category, body, order_index, status, created_by)
  VALUES ('Using AI Analysis Responsibly', 'platform', '# Limits of AI chart analysis\n\n- Confidence scores are model outputs, not guarantees.\n- Always confirm patterns with your own research.\n- Use the risk calculator before any trade idea.\n- The assistant is for education, not personalised financial advice.', 12, 'PUBLISHED', v_admin_uuid)
  RETURNING lesson_id INTO v_lesson_id;

  INSERT INTO quiz_question (lesson_id, prompt, explanation, order_index)
  SELECT v_lesson_id, 'What is a confidence score?', 'A model output indicating how sure the model is about a pattern.', 1;

  INSERT INTO quiz_option (question_id, text, is_correct)
  SELECT q.question_id, 'A model output indicating pattern certainty', TRUE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1
  UNION ALL SELECT q.question_id, 'A guarantee of profit', FALSE FROM quiz_question q WHERE q.lesson_id = v_lesson_id AND q.order_index = 1;
END $$;
