-- Schema do Citizen Assist AI no Supabase. Rode UMA vez: Dashboard > SQL Editor > New query > Run.
-- Dados binários do cofre (já cifrados no servidor) ficam em colunas de texto em base64.
-- RLS ligado e SEM políticas: a chave pública (publishable/anon) não lê nem grava nada;
-- só o servidor, com a chave secreta (sb_secret_...), acessa. Nunca coloque a chave secreta no front.

create table if not exists usuarios (
  user_id bigint primary key,
  uf text,
  temas_briefing text
);
create table if not exists cofre_config (
  user_id bigint primary key,
  salt text not null,
  verificador text not null,
  iteracoes integer not null
);
create table if not exists cofre_docs (
  id bigint generated always as identity primary key,
  user_id bigint not null,
  nome text not null,
  conteudo text not null
);
create index if not exists cofre_docs_user on cofre_docs (user_id);
create table if not exists tarefas (
  id bigint generated always as identity primary key,
  user_id bigint not null,
  titulo text not null,
  quando bigint,
  concluida smallint not null default 0,
  avisada smallint not null default 0
);
create index if not exists tarefas_user on tarefas (user_id);
create table if not exists briefing_config (
  user_id bigint primary key,
  hora text not null,
  ultimo_envio text
);
create table if not exists consentimento_gemini (
  user_id bigint primary key
);
create table if not exists exclusoes (
  id bigint generated always as identity primary key,
  user_id bigint not null,
  chat_id bigint not null,
  message_id bigint not null,
  apagar_em bigint not null
);

alter table usuarios enable row level security;
alter table cofre_config enable row level security;
alter table cofre_docs enable row level security;
alter table tarefas enable row level security;
alter table briefing_config enable row level security;
alter table consentimento_gemini enable row level security;
alter table exclusoes enable row level security;
