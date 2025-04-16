CREATE TABLE `task_queue` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '流水號',
  `task_id` varchar(40) NOT NULL COMMENT '任務編號',
  `task_data` text NOT NULL COMMENT '任務資料',
  `delete_time` datetime NOT NULL COMMENT '刪除時間\nYYYY-mm-dd HH:ii:ss',
  `ins_time` datetime NOT NULL COMMENT '新增時間\nYYYY-mm-dd HH:ii:ss',
  `upd_adm_id` int(11) NOT NULL DEFAULT '0' COMMENT '修改人員\\n後台工作人員編號',
  PRIMARY KEY (`id`),
  KEY `task_id_UNIQUE` (`task_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='任務佇列'