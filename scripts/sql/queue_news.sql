drop table if exists queue_news cascade;

create table queue_news (
    news_id bigint primary key,
	title varchar(500) not null,
	meneos int not null,
	clicks int not null,
	votes_positive int not null,
	votes_negative int not null,
	karma int not null,
	url_full varchar(500) not null,
	url_domain varchar(500) not null,
	time_send timestamptz,
	updated_at timestamptz,
	is_commented boolean
);