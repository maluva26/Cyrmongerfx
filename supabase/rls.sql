-- Row-Level Security policies for Cyrmonger Algo Fx
-- Purpose: block direct PostgREST/anon access. The Django app accesses data via the service role.
-- Steps:
--  1. Run schema.sql first.
--  2. Run this file.
--  3. Verify with an anon SELECT that returns 0 rows.

ALTER TABLE chart_upload ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE detection ENABLE ROW LEVEL SECURITY;
ALTER TABLE lesson ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_question ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_option ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempt ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_plan ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entry ENABLE ROW LEVEL SECURITY;
ALTER TABLE assistant_conversation ENABLE ROW LEVEL SECURITY;
ALTER TABLE assistant_message ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE report ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Default deny for anon and authenticated roles (app uses service_role, not anon)
CREATE POLICY deny_all_anon ON chart_upload FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON chart_upload FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON analysis FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON analysis FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON detection FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON detection FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON lesson FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON lesson FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON quiz_question FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON quiz_question FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON quiz_option FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON quiz_option FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON quiz_attempt FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON quiz_attempt FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON risk_plan FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON risk_plan FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON journal_entry FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON journal_entry FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON assistant_conversation FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON assistant_conversation FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON assistant_message FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON assistant_message FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON feedback FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON feedback FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON report FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON report FOR ALL TO authenticated USING (false);
CREATE POLICY deny_all_anon ON audit_log FOR ALL TO anon USING (false);
CREATE POLICY deny_all_auth ON audit_log FOR ALL TO authenticated USING (false);

-- Test: from psql with service_role, these should work.
-- From an anon role, all SELECTs should return 0 rows.
