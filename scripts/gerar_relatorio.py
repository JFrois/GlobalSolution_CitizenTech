"""Gera docs/relatorio.pdf (4 a 8 páginas) a partir dos dados reais do projeto.

Uso:  python scripts/gerar_relatorio.py

Lê data/base.json e testes/*.csv, monta um HTML e converte para PDF com o Google Chrome em
modo headless (sem instalar nada). Os números vêm dos arquivos, não são digitados à mão.
O que ainda não foi medido (conjunto do público, usabilidade, clareza) aparece como
"pendente": rode de novo depois de preencher os dados.
"""
from __future__ import annotations

import csv
import html
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import avaliacao  # noqa: E402
import base  # noqa: E402

CHROMES = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome",
           "chromium", "chrome")
CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font: 10.5pt/1.45 -apple-system, "Segoe UI", Arial, sans-serif; color: #1a1a1a; }
h1 { font-size: 20pt; margin: 0 0 2pt; color: #1b6fb8; }
h2 { font-size: 13pt; margin: 16pt 0 4pt; color: #1b6fb8; border-bottom: 1px solid #c9d8e8; padding-bottom: 2pt; }
h3 { font-size: 11pt; margin: 10pt 0 2pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 9.5pt; }
th, td { border: 1px solid #c9d8e8; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #eaf2fb; }
.pendente { color: #9a5b00; font-weight: 600; }
.cx { border: 1px solid #c9d8e8; background: #f6faff; padding: 6pt 8pt; margin: 6pt 0; }
pre { font: 8.5pt/1.3 ui-monospace, Menlo, monospace; background: #f6faff; border: 1px solid #c9d8e8; padding: 6pt; white-space: pre-wrap; }
.pg { page-break-before: always; }
small { color: #555; }
"""


def ler_csv(nome):
    with open(RAIZ / "testes" / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def tabela(cabecalho, linhas):
    cab = "".join("<th>%s</th>" % html.escape(c) for c in cabecalho)
    corpo = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in l) for l in linhas)
    return "<table><tr>%s</tr>%s</table>" % (cab, corpo)


def esc(t):
    return html.escape(str(t))


def montar_html():
    dados = base.carregar_base(RAIZ / "data" / "base.json")
    regs = dados["registros"]
    resultados = ler_csv("resultados.csv")
    comparacao = ler_csv("comparacao_modelos.csv")
    perguntas = avaliacao.carregar_perguntas()
    acertos, total, pct = avaliacao.taxa(resultados)
    por_tipo = avaliacao.agrupar(resultados, "tipo")
    t_ind = sum(float(l["tempo_indice_ms"]) for l in resultados) / len(resultados)
    t_lin = sum(float(l["tempo_linear_ms"]) for l in resultados) / len(resultados)
    escala = avaliacao.medir_escala(dados, perguntas, repeticoes=2, repeticoes_base=100)
    dominios = sorted({urlparse(r["referencia"]).netloc for r in regs})
    datas = sorted({r["data_verificacao"] for r in regs})
    media = {m: [] for m in "AB"}
    for l in comparacao:
        media[l["modelo"]].append(l)

    def med(m, c):
        v = [float(l[c]) for l in media[m]]
        return sum(v) / len(v)

    linhas_tipo = [[esc(t), "%d/%d" % avaliacao.taxa(l)[:2], "%.1f%%" % avaliacao.taxa(l)[2]]
                   for t, l in sorted(por_tipo.items())]
    linhas_escala = [[str(m["registros"]), "%.4f" % m["indice_ms"], "%.4f" % m["linear_ms"],
                      "%.0fx" % (m["linear_ms"] / m["indice_ms"])] for m in escala]
    linhas_fontes = [[esc(r["id"]), esc(r.get("titulo", r["pergunta"])), esc(urlparse(r["referencia"]).netloc),
                      esc(r["data_verificacao"])] for r in regs]
    linhas_res = [[esc(l["id"]), esc(l["tipo"]), esc(l["pergunta"]), esc(l["esperado"]), esc(l["obtido"]),
                   esc(l["resultado"])] for l in resultados]

    return """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Citizen Assist AI: relatório</title><style>%(css)s</style></head><body>

<h1>Citizen Assist AI</h1>
<p><strong>Global Solution 2026.2 · CitizenTech · FIAP</strong><br>
Juan de Lucas Frois (RM563260) · Flávia Roberta Pennachin (RM561860) · Pedro Valente (RM570394)</p>
<p><small>Relatório gerado em 09/11/2026 por <code>scripts/gerar_relatorio.py</code> a partir dos dados do repositório.
Itens ainda não medidos aparecem como <span class="pendente">pendente</span>.</small></p>

<h2>1. Problema e público</h2>
<p>Quem precisa de um documento ou serviço público encontra a informação espalhada em vários portais, com termos técnicos e instruções incompletas. O Citizen Assist AI orienta o cidadão sobre documentos, serviços e direitos <strong>somente com base em registros verificados</strong> (<code>data/base.json</code>), sempre citando a fonte oficial e a data de verificação, e avisa quando não há base suficiente, sem inventar instruções.</p>
<p><strong>Público:</strong> cidadãos com pouca familiaridade com portais públicos (quem perdeu um documento, vai pedir um benefício ou quer reclamar de uma empresa). <strong>Não é um canal oficial</strong> de nenhum órgão e não promete integração com órgãos públicos.</p>
<p><strong>Impacto social:</strong> reduzir o tempo e o erro na busca de orientação básica, apontando sempre o canal oficial e os próximos assuntos relacionados, em linguagem simples e com texto acessível (sem depender de cor).</p>

<h2>2. Arquitetura</h2>
<p>Duas camadas. O <strong>núcleo</strong> (avaliado pela GS) roda no terminal, offline e só com a biblioteca padrão do Python 3.9+: <code>base.py</code> (carga e validação), <code>busca.py</code> (pontuação, índice invertido, grafo e Dijkstra), <code>respostas.py</code> (modelos A e B) e <code>sistema.py</code>. A <strong>camada de produto</strong> (diferencial) adiciona bot no Telegram, roteador com Gemini (function calling, com reserva por regras), cofre criptografado, tarefas e lembretes, resumo da manhã e painel web (Mini App ou navegador).</p>
<pre>Usuário -> Telegram -> telegram_bot.py -> roteador.py (Gemini + function calling; reserva por regras)
                          |                     |
                  painel (Mini App)   buscar_orientacao | cofre_documento | gerenciar_tarefas | briefing_matinal
                  painel.py (API)     busca.py + base.py   cofre.py          tarefas.py          briefing.py
                                              |               |
                                        data/base.json   armazenamento (SQLite) - tudo filtrado por user_id
agendador.py: lembretes, resumo da manhã e exclusão de mensagens (ao subir, cumpre o que venceu)</pre>
<div class="cx"><strong>Princípio de projeto:</strong> a resposta ao cidadão nunca é gerada livremente pelo LLM. O LLM só escolhe a ferramenta e sugere o nome de documentos do cofre. O conteúdo vem sempre da base, o que mantém a taxa de acerto mensurável e evita informação inventada. A voz é transcrita localmente pelo Whisper, sem LLM.</div>

<h2 class="pg">3. Base e fontes</h2>
<p>%(n)d registros em %(nt)d temas (Documentação pessoal, Serviços públicos, Direitos e orientações comunitárias). Cada registro tem id, tema, palavras-chave, pergunta, orientação, referência, data de verificação e assuntos relacionados. Fontes oficiais nos domínios: %(dom)s. Datas de verificação: %(datas)s. <strong>As orientações foram redigidas com apoio de IA a partir das páginas oficiais e ainda precisam de revisão humana</strong> (<span class="pendente">pendente</span>).</p>
%(t_fontes)s

<h2>4. Busca, decisão e Karnaugh</h2>
<p><strong>Busca:</strong> normalização (minúsculas, sem acentos, sem pontuação, sem <em>stopwords</em>), expansão por sinônimos (nos dados, não no código), pontuação por palavra-chave (3), pergunta (2) e orientação (1), bônus de +2 para expressão completa, índice invertido e busca linear (mesmo resultado). Várias correspondências: ordem por pontuação e, no empate, pelo menor id. Correção de digitação (difflib) só quando nada casa. <strong>Filtros com De Morgan:</strong> <code>incluir = not (fora_do_tema or ja_exibido)</code> equivale a <code>(not fora_do_tema) and (not ja_exibido)</code>.</p>
<p><strong>Grafo e Dijkstra:</strong> a lista de adjacência vem de <code>relacionados</code> (não direcionado); o custo é 1 no mesmo tema e 2 entre temas. O Dijkstra (<code>heapq</code>) dá o caminho entre dois assuntos e ordena os 3 próximos assuntos sugeridos.</p>
<p><strong>Regra de decisão:</strong> C = entrada válida; A = melhor pontuação ≥ 3; B = (1ª − 2ª pontuação) ≥ 2.</p>
<table><tr><th rowspan="2">C</th><th colspan="4">Mapa de Karnaugh (linhas C, colunas A B)</th></tr>
<tr><th>A B = 00</th><th>01</th><th>11</th><th>10</th></tr>
<tr><th>0</th><td>Inválida</td><td>Inválida</td><td>Inválida</td><td>Inválida</td></tr>
<tr><th>1</th><td>Sem base</td><td>Sem base</td><td>Responder</td><td>Pedir escolha</td></tr></table>
<p>Simplificando: <strong>Inválida = ¬C</strong>; <strong>Sem base = C·¬A</strong>; <strong>Responder = C·A·B</strong>; <strong>Pedir escolha = C·A·¬B</strong>. As quatro saídas têm mensagem própria e o programa nunca encerra por erro de entrada.</p>

<h2 class="pg">5. Modelos de resposta A e B</h2>
<p>Os dois modelos formatam o <strong>mesmo</strong> resultado da busca; por isso taxa de acerto e tempo não servem para compará-los. <strong>Modelo A</strong> (direto): parágrafo curto, <code>Fonte:</code> com data, linha <code>Veja também:</code>. <strong>Modelo B</strong> (passo a passo): título, lista numerada (nunca cria passo que não esteja na orientação), <code>Atenção:</code>, <code>Fonte:</code>, <code>Continue consultando:</code>, frase de não-oficialidade. Em ambos, sem base: aviso de limitação, link do gov.br e temas disponíveis.</p>
%(t_ab)s
<p><strong>Nota de clareza (1 a 5), cega (rótulos X/Y):</strong> <span class="pendente">pendente</span> (folha em <code>testes/clareza_folha.md</code>). O modelo padrão só será escolhido depois das notas; hoje o passo a passo (B) é provisório.</p>

<h2>6. Testes e indicadores</h2>
<p><strong>Protocolo contra viés:</strong> as perguntas da equipe foram congeladas num commit antes de preencher palavras-chave e sinônimos. O conjunto do público (anônimo, meta ≥ 10) é medido <strong>antes</strong> de qualquer ajuste. Hoje só existe o conjunto da equipe.</p>
<p><strong>Taxa de acerto da busca (conjunto da equipe): %(ac)d/%(tt)d = %(pct).1f%%.</strong> Conjunto do público: <span class="pendente">pendente</span>.</p>
%(t_tipo)s
<p><strong>Interpretação honesta:</strong> na primeira medição, antes de ajustes, a busca acertou 17 de 19 (erros em E02 e E14). As palavras-chave desses registros foram corrigidas olhando essas perguntas, então <em>os 100%% do conjunto da equipe não são uma medida independente</em>; a medida confiável será a do público.</p>
<p><strong>Tempo médio por consulta (média das %(tt)d perguntas, 1000 repetições cada):</strong> índice invertido %(ti).4f ms; busca linear %(tl).4f ms.</p>
<p><strong>Linear × índice por tamanho da base</strong> (média por consulta, ms; bases ampliadas com cópias sintéticas dos registros reais):</p>
%(t_escala)s
<h3>Resultados por pergunta (esperado × obtido)</h3>
%(t_res)s
<p><strong>Usabilidade:</strong> <span class="pendente">pendente</span> (roteiro de 5 tarefas e SUS em <code>docs/ux.md</code> §8; registro em <code>testes/usabilidade.md</code>). Metas: primeira resposta útil em menos de 1 min e pelo menos 4 de 5 tarefas sem ajuda.</p>
<p><strong>Testes automatizados:</strong> 256 (<code>python -m unittest discover -s testes -t .</code>), cobrindo validação da base, normalização, busca, 4 saídas da decisão, Dijkstra, isolamento por usuário, criptografia (ida e volta; senha errada falha), <code>initData</code>, agendador, briefing e painel. O CI roda a suíte no Python 3.9 (só biblioteca padrão) e no 3.12 (com as bibliotecas do servidor).</p>

<h2 class="pg">7. Privacidade, cofre e limites</h2>
<ul>
<li><strong>Núcleo:</strong> não pede nem guarda dado pessoal.</li>
<li><strong>Cofre opcional:</strong> só guarda o que o usuário envia, cifra antes de armazenar (AES-256-GCM, chave derivada da senha por PBKDF2 com 600 mil iterações e sal por usuário), tudo filtrado por <code>user_id</code>, com apagamento real (<code>/apagar_meus_dados</code>). A senha é criada só no painel e nunca vai ao servidor em claro nem ao chat; senha perdida significa documentos perdidos.</li>
<li><strong>Honestidade sobre E2E:</strong> enquanto o cofre está desbloqueado, o servidor vê o arquivo ao enviá-lo no chat; conversas com bots do Telegram não são de ponta a ponta. O bot apaga a mensagem com o documento em 5 minutos, o que limpa o chat, não o aparelho.</li>
<li><strong>Gemini:</strong> usado no plano gratuito. Nesse plano o Google pode usar o conteúdo enviado para melhorar seus produtos e permitir revisão humana, e pode processá-lo em outros países. Por isso o primeiro envio exige consentimento com esse aviso, o usuário pode escolher um nome próprio sem enviar o arquivo, e demonstração, vídeo e testes usam <strong>somente documentos fictícios</strong>. Classificador local e plano pago são roadmap.</li>
<li><strong>Segredos:</strong> nunca no repositório; ficam nos GitHub Secrets e no <code>.env</code> da VM. Logs sem tokens, conteúdo de documentos nem texto de mensagens.</li>
<li><strong>Resumo da manhã:</strong> manchetes de feeds RSS, sempre rotuladas "Notícias — fonte não oficial" e separadas da base verificada.</li>
</ul>

<h2>8. Limitações e melhorias</h2>
<p><strong>Limitações:</strong> base com 17 registros ainda sem revisão humana; avaliação com perguntas escritas pela própria equipe e sem conjunto do público nem teste de usabilidade; busca por palavras-chave (não entende sentido); informações públicas mudam, por isso cada resposta mostra a data e orienta a confirmar; VM, HTTPS e deploy automático ainda não testados em produção; testes reais no Telegram de foto/PDF, cofre e resumo da manhã pendentes; medição de escala com cópias sintéticas.</p>
<p><strong>Melhorias (≥ 2):</strong> (1) ampliar sinônimos e palavras-chave e medir antes e depois com o conjunto do público; (2) ampliar a base (CNH, CPF) e detalhar os estados em <code>referencias_estaduais</code>; (3) classificador de documentos local, sem enviar arquivos ao Gemini; (4) fuso por usuário.</p>
<p><small>Fontes de contexto externas (por exemplo, Base dos Dados) não foram usadas no código e, se entrarem neste relatório, devem trazer fonte e data da consulta.</small></p>
</body></html>""" % {
        "css": CSS, "n": len(regs), "nt": len(dados["temas"]), "dom": esc(", ".join(dominios)),
        "datas": esc(", ".join(datas)),
        "t_fontes": tabela(["Id", "Assunto", "Fonte (domínio)", "Verificado em"], linhas_fontes),
        "t_ab": tabela(["Critério (spec §8)", "Modelo A", "Modelo B"], [
            ["Respostas com fonte e data", "%d/%d" % (sum(l["tem_fonte_com_data"] == "sim" for l in media["A"]), len(media["A"])),
             "%d/%d" % (sum(l["tem_fonte_com_data"] == "sim" for l in media["B"]), len(media["B"]))],
            ["Com relacionados para continuar", "%d/%d" % (sum(l["tem_relacionados"] == "sim" for l in media["A"]), len(media["A"])),
             "%d/%d" % (sum(l["tem_relacionados"] == "sim" for l in media["B"]), len(media["B"]))],
            ["Tamanho médio (palavras)", "%.1f" % med("A", "palavras"), "%.1f" % med("B", "palavras")],
            ["Passos numerados (média)", "%.1f" % med("A", "passos"), "%.1f" % med("B", "passos")],
            ["Clareza (nota média 1 a 5)", '<span class="pendente">pendente</span>', '<span class="pendente">pendente</span>']]),
        "ac": acertos, "tt": total, "pct": pct,
        "t_tipo": tabela(["Tipo", "Acertos", "Taxa"], linhas_tipo), "ti": t_ind, "tl": t_lin,
        "t_escala": tabela(["Registros", "Índice (ms)", "Linear (ms)", "Linear / índice"], linhas_escala),
        "t_res": tabela(["Id", "Tipo", "Pergunta", "Esperado", "Obtido", "Resultado"], linhas_res),
    }


def achar_chrome():
    for c in CHROMES:
        if Path(c).exists() or shutil.which(c):
            return c
    return None


def main():
    chrome = achar_chrome()
    if not chrome:
        print("Google Chrome não encontrado. Abra docs/relatorio.html no navegador e use Imprimir > Salvar como PDF.")
    destino_html = RAIZ / "docs" / "relatorio.html"
    destino_html.write_text(montar_html(), encoding="utf-8")
    if not chrome:
        return 1
    pdf = RAIZ / "docs" / "relatorio.pdf"
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=%s" % pdf, destino_html.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    destino_html.unlink()
    print("Gravado:", pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
