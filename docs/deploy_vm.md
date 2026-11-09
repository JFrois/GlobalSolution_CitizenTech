# Roteiro de deploy na VM (item 8 / C1, C3, C4)

Tudo aqui está **por testar**: nenhuma VM foi criada ainda. Responsável: Integrante C (Pedro); mantenedor em último caso: Juan. Valores secretos nunca entram neste arquivo nem no Git.

## 1. Criar a VM
- Oracle Cloud Always Free (Ubuntu), com portas **22, 80 e 443** abertas na rede da Oracle (Security List) e no firewall da VM.
- Atenção (spec §12): limites reduzidos em 2026, risco de recuperação por ociosidade e de falta de capacidade na criação. Plano B: máquina de um integrante com Cloudflare quick tunnel (URL muda a cada reinício).
- Anote o IP público e o usuário da VM.

## 2. Instalar o ambiente (uma vez, na VM)
```bash
sudo apt update && sudo apt install -y git ffmpeg python3.12 python3.12-venv caddy
git clone https://github.com/JFrois/GlobalSolution_CitizenTech.git ~/citizen-assist
cd ~/citizen-assist && python3.12 -m venv .venv
.venv/bin/pip install "setuptools<81" wheel
.venv/bin/pip install --no-build-isolation openai-whisper==20240930
.venv/bin/pip install -r requirements.txt
```
O `.env` **não** é criado à mão: o deploy o grava a partir dos GitHub Secrets (passo 5).

## 3. Serviço systemd
```bash
sudo cp ~/citizen-assist/deploy/citizen-assist.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable citizen-assist
```
Confira no arquivo o usuário e o caminho (`~/citizen-assist`).

## 4. HTTPS com DuckDNS + Caddy (teste de 15 min, spec §12)
1. Em duckdns.org, aponte o subdomínio (o `deploy/Caddyfile` usa `gs-citizentech.duckdns.org`) para o IP da VM. **Leia antes os Termos e a Privacidade do DuckDNS.**
2. `sudo cp ~/citizen-assist/deploy/Caddyfile /etc/caddy/Caddyfile && sudo systemctl restart caddy`
3. Abra `https://gs-citizentech.duckdns.org` no navegador: o certificado precisa estar válido (o Telegram recusa autoassinado).
4. Se o certificado não emitir em ~15 min, use o plano B (Cloudflare quick tunnel) e registre aqui o motivo.
5. Defina o secret `PAINEL_URL` com essa URL https.

## 5. GitHub Secrets e deploy automático
Em **Settings → Secrets and variables → Actions** do repositório:

| Onde | Nome | Valor |
|---|---|---|
| Secrets | `HOST` | IP ou domínio da VM |
| Secrets | `USER` | usuário SSH da VM |
| Secrets | `KEY` | chave SSH **privada** dedicada ao deploy (a pública vai em `~/.ssh/authorized_keys` da VM) |
| Secrets (já criados) | `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, `GEMINI_MODELO`, `SESSAO_SEGREDO` | do `.env` |
| Secrets (quando houver) | `PAINEL_URL`, `DUCKDNS_TOKEN`, `WHISPER_MODELO`, `PAINEL_PORTA`, `SUPABASE_*` | |
| Variables | `DEPLOY_ATIVO` | `true` (só depois de a VM existir) |

Gerar a chave de deploy (no seu computador): `ssh-keygen -t ed25519 -f deploy_key -N ""`. Cole o conteúdo de `deploy_key` no secret `KEY`, a `deploy_key.pub` na VM, e **apague os dois arquivos locais**.

O deploy faz `git pull`, regrava o `.env`, instala dependências e reinicia o serviço. Para mudar um valor: edite o secret e faça um novo push na `main` (ou rode o workflow de novo).

## 6. Antes de ligar
- **Gerar novo token do bot (@BotFather) e nova chave do Gemini**: os de teste foram compartilhados fora do `.env`. Atualize os secrets.
- Conferir CPU e memória com o Whisper; se pesar, `WHISPER_MODELO=tiny`.

## 7. Conferir
```bash
sudo systemctl status citizen-assist
journalctl -u citizen-assist -n 50 --no-pager   # sem tokens nem conteúdo de documentos
```
No Telegram: `/start`, uma pergunta, `/painel` (abre o painel em https).
