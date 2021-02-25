/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2017/12/15/周五 9:55:25                        */
/*==============================================================*/


drop table if exists tb_dict;

drop table if exists tb_host;

/* drop index ticketid_index on tb_host_verbose; */

drop table if exists tb_host_verbose;

drop table if exists tb_privi;

drop table if exists tb_role;

drop table if exists tb_role_privi;

/* drop index username_index on tb_user; */

drop table if exists tb_user;

/*==============================================================*/
/* Table: tb_dict                                               */
/*==============================================================*/
create table tb_dict
(
   thekey               varchar(16),
   thevalue             text,
   parentid             varchar(8)
);

alter table tb_dict comment '字典表
key: rid        value: 角色名称      parentid: 1
                            -&#&';

/*==============================================================*/
/* Table: tb_host                                               */
/*==============================================================*/
create table tb_host
(
   aid                  varchar(16) not null,
   num                  varchar(16),
   ctime                datetime,
   mtime                datetime,
   primary key (aid)
);

alter table tb_host comment '主机表';

/*==============================================================*/
/* Table: tb_host_verbose                                       */
/*==============================================================*/
create table tb_host_verbose
(
   aid                  varchar(16),
   descript             text,
   tid                  varchar(128),
   model                varchar(32),
   date                 date,
   depart               varchar(32),
   personname           varchar(16),
   lid                  varchar(16),
   pcname               varchar(16),
   pcid                 varchar(25),
   mac                  char(18),
   ticketid             int,
   comment              text,
   count                varchar(8)
);

alter table tb_host_verbose comment '主机详情表';

/*==============================================================*/
/* Index: ticketid_index                                        */
/*==============================================================*/
create index ticketid_index on tb_host_verbose
(
   ticketid
);

/*==============================================================*/
/* Table: tb_privi                                              */
/*==============================================================*/
create table tb_privi
(
   pid                  varchar(16) not null,
   primary key (pid)
);

alter table tb_privi comment '权限表';

/*==============================================================*/
/* Table: tb_role                                               */
/*==============================================================*/
create table tb_role
(
   rid                  varchar(16) not null,
   uid                  varchar(16),
   primary key (rid)
);

alter table tb_role comment '角色表';

/*==============================================================*/
/* Table: tb_role_privi                                         */
/*==============================================================*/
create table tb_role_privi
(
   rid                  varchar(16),
   pid                  varchar(16)
);

alter table tb_role_privi comment '权限角色中间表';

/*==============================================================*/
/* Table: tb_user                                               */
/*==============================================================*/
create table tb_user
(
   uid                  varchar(16) not null,
   account              varchar(16),
   username             text,
   password             varchar(128),
   did                  varchar(16),
   primary key (uid)
);

alter table tb_user comment '用户表';

/*==============================================================*/
/* Index: username_index                                        */
/*==============================================================*/
create unique index username_index on tb_user
(
   account
);

alter table tb_host_verbose add constraint FK_Reference_4 foreign key (aid)
      references tb_host (aid) on delete restrict on update restrict;

alter table tb_role add constraint FK_Reference_5 foreign key (uid)
      references tb_user (uid) on delete restrict on update restrict;

alter table tb_role_privi add constraint FK_Reference_7 foreign key (rid)
      references tb_role (rid) on delete restrict on update restrict;

alter table tb_role_privi add constraint FK_Reference_8 foreign key (pid)
      references tb_privi (pid) on delete restrict on update restrict;

