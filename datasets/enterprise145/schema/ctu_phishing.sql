-- Schema for database: ctu_phishing

CREATE TABLE `email_v2` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `wordCount` int(11) DEFAULT NULL,
  `label` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1034 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `hillary_ham` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5636 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `hillary_ham2` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `subdomains_max` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `term_access` int(11) DEFAULT NULL,
  `term_bank` int(11) DEFAULT NULL,
  `term_credit` int(11) DEFAULT NULL,
  `term_identity` int(11) DEFAULT NULL,
  `term_inconvenience` int(11) DEFAULT NULL,
  `term_information` int(11) DEFAULT NULL,
  `term_limit` int(11) DEFAULT NULL,
  `term_log` int(11) DEFAULT NULL,
  `term_hour` int(11) DEFAULT NULL,
  `term_password` int(11) DEFAULT NULL,
  `term_recently` int(11) DEFAULT NULL,
  `term_risk` int(11) DEFAULT NULL,
  `term_social` int(11) DEFAULT NULL,
  `term_security` int(11) DEFAULT NULL,
  `term_service` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `form_count` int(11) DEFAULT NULL,
  `has_javascript` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `message_id` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `jose_phish` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8229 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `jose_phish2` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `subdomains_max` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `term_access` int(11) DEFAULT NULL,
  `term_bank` int(11) DEFAULT NULL,
  `term_credit` int(11) DEFAULT NULL,
  `term_identity` int(11) DEFAULT NULL,
  `term_inconvenience` int(11) DEFAULT NULL,
  `term_information` int(11) DEFAULT NULL,
  `term_limit` int(11) DEFAULT NULL,
  `term_log` int(11) DEFAULT NULL,
  `term_hour` int(11) DEFAULT NULL,
  `term_password` int(11) DEFAULT NULL,
  `term_recently` int(11) DEFAULT NULL,
  `term_risk` int(11) DEFAULT NULL,
  `term_social` int(11) DEFAULT NULL,
  `term_security` int(11) DEFAULT NULL,
  `term_service` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `form_count` int(11) DEFAULT NULL,
  `has_javascript` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `message_id` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `personalInbox_ham` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=599 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `personalInbox_ham2` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `subdomains_max` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `term_access` int(11) DEFAULT NULL,
  `term_bank` int(11) DEFAULT NULL,
  `term_credit` int(11) DEFAULT NULL,
  `term_identity` int(11) DEFAULT NULL,
  `term_inconvenience` int(11) DEFAULT NULL,
  `term_information` int(11) DEFAULT NULL,
  `term_limit` int(11) DEFAULT NULL,
  `term_log` int(11) DEFAULT NULL,
  `term_hour` int(11) DEFAULT NULL,
  `term_password` int(11) DEFAULT NULL,
  `term_recently` int(11) DEFAULT NULL,
  `term_risk` int(11) DEFAULT NULL,
  `term_social` int(11) DEFAULT NULL,
  `term_security` int(11) DEFAULT NULL,
  `term_service` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `form_count` int(11) DEFAULT NULL,
  `has_javascript` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `message_id` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `spamAssassin_ham` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1448 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `spamAssassin_ham2` (
  `label` int(11) DEFAULT NULL,
  `link_count` int(11) DEFAULT NULL,
  `ipLink_count` int(11) DEFAULT NULL,
  `subdomains_max` int(11) DEFAULT NULL,
  `clickVariation_count` int(11) DEFAULT NULL,
  `term_account` int(11) DEFAULT NULL,
  `term_verify` int(11) DEFAULT NULL,
  `term_member` int(11) DEFAULT NULL,
  `term_sign` int(11) DEFAULT NULL,
  `term_free` int(11) DEFAULT NULL,
  `term_suspension` int(11) DEFAULT NULL,
  `term_access` int(11) DEFAULT NULL,
  `term_bank` int(11) DEFAULT NULL,
  `term_credit` int(11) DEFAULT NULL,
  `term_identity` int(11) DEFAULT NULL,
  `term_inconvenience` int(11) DEFAULT NULL,
  `term_information` int(11) DEFAULT NULL,
  `term_limit` int(11) DEFAULT NULL,
  `term_log` int(11) DEFAULT NULL,
  `term_hour` int(11) DEFAULT NULL,
  `term_password` int(11) DEFAULT NULL,
  `term_recently` int(11) DEFAULT NULL,
  `term_risk` int(11) DEFAULT NULL,
  `term_social` int(11) DEFAULT NULL,
  `term_security` int(11) DEFAULT NULL,
  `term_service` int(11) DEFAULT NULL,
  `word_count` int(11) DEFAULT NULL,
  `words_length_median` int(11) DEFAULT NULL,
  `punctuation_count` int(11) DEFAULT NULL,
  `digits_count` int(11) DEFAULT NULL,
  `form_count` int(11) DEFAULT NULL,
  `has_javascript` int(11) DEFAULT NULL,
  `all_domains_whitelisted` int(11) DEFAULT NULL,
  `message_id` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;

