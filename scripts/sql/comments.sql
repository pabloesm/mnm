-- drop table if exists comments cascade;
drop table if exists comments;

create table comments (
    comment_md5_id uuid primary key,
    news_id bigint not null,
    comment_text text not null,
	votes_positive int not null,
	votes_negative int not null,
	url_full varchar(500) not null,
	updated_at timestamptz not null,
    constraint fk_news_id 
        foreign key(news_id) 
        references queue_news(news_id)
);