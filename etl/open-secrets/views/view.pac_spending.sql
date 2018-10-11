CREATE VIEW pac_spending
AS SELECT cmtes.cycle AS cycle,
  cmtes.pacshort AS pacshort,
  cmtes.affiliate AS affiliate,
  cmtes.ultorg AS ultorg,
  cmtes.recipid AS recipid,
  cmtes.recipcode AS recipcode,
  cmtes.feccandid AS cmte_feccandid,
  cmtes.party AS party,
  cmtes.primcode AS primcode,
  cmtes.source AS source,
  cmtes.sensitive AS sensitive,
  cmtes.foreign AS foreign,
  cmtes.active AS active,
  pacs.fecrecno AS fecrecno,
  pacs.pacid AS pacid,
  pacs.cid AS cid,
  pacs.amount AS amount,
  pacs.`date` AS `date`,
  pacs.realcode AS realcode,
  pacs.`type` AS `type`,
  pacs.di AS di,
  pacs.feccandid AS pac_feccandid
  FROM
 pq_crp_pacs18 pacs
 LEFT JOIN pq_crp_cmtes18 cmtes
 ON pacs.pacid = cmtes.cmteid
