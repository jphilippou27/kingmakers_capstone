CREATE VIEW pac_spending_by_type AS
SELECT SUM(a.amount) AS total_amt,
  MAX(a.pacshort) AS pac_name,
  a.di AS direct_ind,
  a.contribtype AS contrib_type,
  MAX(a.firstlastp) AS cand_name,
  a.cid AS candidate_id,
  a.pacid AS pac_id
FROM (
  SELECT pacs.amount,
    pacs.`type` AS contribtype,
    pacs.di,
    pacs.cid,
    pacs.pacid,
    pacs.pacshort,
    cands.firstlastp AS firstlastp
  FROM pac_spending pacs
  LEFT JOIN pq_crp_cands18 cands
  ON pacs.cid = cands.cid
) a
GROUP BY a.pacid, a.cid, a.contribtype, a.di, a.cid
ORDER BY SUM(a.amount) DESC
