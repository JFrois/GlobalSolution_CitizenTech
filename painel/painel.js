// Front do painel (Mini App e navegador). Sem eval, sem innerHTML com dado da rede:
// todo texto vindo do servidor entra por textContent. O front só desenha; o conteúdo
// das orientações vem pronto da base (spec §10.5). Identidade Azul Telegram (docs/ux.md §9).
"use strict";

const tg = window.Telegram && window.Telegram.WebApp;
if (tg) { tg.ready(); tg.expand(); }
const SEM_ANIMACAO = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const NS_SVG = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);
let estado = null;
let contadorId = null;

// Chamada à API: no Mini App vai o initData assinado; no navegador vai o cookie de sessão.
async function api(metodo, caminho, corpo) {
  const cabecalhos = { "content-type": "application/json" };
  if (tg && tg.initData) cabecalhos["X-Telegram-Init-Data"] = tg.initData;
  const r = await fetch(caminho, {
    method: metodo, headers: cabecalhos, credentials: "same-origin",
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
  return r;
}

async function json(r) {
  if (!r.ok) {
    let detalhe = "Algo deu errado. Tente de novo.";
    try { const d = await r.json(); if (typeof d.detail === "string") detalhe = d.detail; } catch (e) { /* sem corpo */ }
    if (r.status === 401) detalhe = "Sua sessão acabou. Peça um novo link com /painel no bot.";
    const erro = new Error(detalhe); erro.status = r.status; throw erro;
  }
  return r.json();
}

function avisar(texto) {
  const e = $("aviso");
  e.textContent = texto || "";
  e.hidden = !texto;
}

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto !== undefined) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

// Ícone SVG montado pelo DOM (sem innerHTML). Cada item de "tracos" é um atributo d de <path>.
function icone(tracos, tamanho, extra) {
  const s = document.createElementNS(NS_SVG, "svg");
  s.setAttribute("width", tamanho); s.setAttribute("height", tamanho); s.setAttribute("viewBox", "0 0 24 24");
  s.setAttribute("fill", "none"); s.setAttribute("stroke", "currentColor"); s.setAttribute("stroke-width", extra || "2");
  s.setAttribute("stroke-linecap", "round"); s.setAttribute("stroke-linejoin", "round"); s.setAttribute("aria-hidden", "true");
  for (const d of tracos) { const p = document.createElementNS(NS_SVG, "path"); p.setAttribute("d", d); s.appendChild(p); }
  return s;
}
const ICONES_DOC = [
  { classe: "azul", tracos: ["M3 8a3 3 0 013-3h12a3 3 0 013 3v8a3 3 0 01-3 3H6a3 3 0 01-3-3z", "M14 10h4M14 14h3"] },
  { classe: "teal", tracos: ["M7 3h7l5 5v13H7z", "M14 3v5h5"] },
  { classe: "coral", tracos: ["M7 3h7l5 5v13H7z", "M14 3v5h5M10 13h6M10 17h4"] },
];

// Atraso da animação de entrada (CSSOM: a CSP não deixa estilo inline no HTML).
function atrasar(e, segundos) { e.style.animationDelay = segundos + "s"; return e; }

// ---- Abas ----
const TELAS = {
  perguntar: ["Qual a sua dúvida hoje?", "Respostas simples, sempre com a fonte oficial."],
  tarefas: ["Suas tarefas", "Anote aqui e eu aviso pelo Telegram na hora marcada."],
  cofre: ["Seu cofre", "Só você abre, com a sua senha."],
  ajustes: ["Ajustes", "Do seu jeito, e só o necessário."],
};
function abrirAba(nome) {
  for (const a of Object.keys(TELAS)) {
    $("aba-" + a).setAttribute("aria-selected", String(a === nome));
    $("tela-" + a).hidden = a !== nome;
  }
  $("titulo-tela").textContent = TELAS[nome][0];
  $("sub-tela").textContent = TELAS[nome][1];
  $("form-pergunta").hidden = nome !== "perguntar";
  avisar("");
  if (nome === "tarefas") carregarTarefas();
  else if (nome !== "perguntar") carregarEstado();
}
for (const a of Object.keys(TELAS)) $("aba-" + a).addEventListener("click", () => abrirAba(a));

// ---- Perguntar: cena da verificação (≈3 s no máximo, docs/ux.md §9) ----
// Contagem até o total de orientações (a barra e os blocos seguintes entram por CSS).
function contar(destino, total) {
  if (SEM_ANIMACAO || total < 2) { destino.textContent = String(total); return; }
  const inicio = performance.now(), duracao = 1100;
  const passo = (agora) => {
    const t = Math.min(1, (agora - inicio) / duracao);
    destino.textContent = String(Math.round(total * (1 - Math.pow(1 - t, 3))));
    if (t < 1) requestAnimationFrame(passo);
  };
  requestAnimationFrame(passo);
}

function adicionar(c, atraso) { $("cena").appendChild(atrasar(c, atraso)); return c; }

function linkExterno(texto, url, classe) {
  // Só vira link se for http(s): nunca javascript: vindo de dado (defesa extra).
  if (!/^https?:\/\//.test(url)) return document.createTextNode(url);
  const a = el("a", texto, classe); a.href = url; a.target = "_blank"; a.rel = "noopener noreferrer";
  return a;
}

function botaoDeAssunto(titulo) {
  const b = el("button", titulo, "chip-botao"); b.type = "button";
  b.addEventListener("click", () => perguntar(titulo));
  return b;
}

function desenharResposta(d) {
  const cena = $("cena");
  cena.textContent = "";
  $("exemplos").hidden = true;
  if (d.decisao === "RESPONDER") {
    const consulta = el("div", undefined, "consulta entra");
    const linha = el("p"); linha.append("Consultando ");
    const numero = el("span", "0"); linha.append(numero, " orientações verificadas");
    const trilho = el("div", undefined, "trilho"); trilho.appendChild(el("div", undefined, "enche"));
    consulta.append(linha, trilho); adicionar(consulta, 0);
    contar(numero, d.total_orientacoes);

    adicionar(el("h2", d.titulo, "resposta-titulo entra"), 1.2);
    d.passos.forEach((p, i) => {
      const cartao = el("div", undefined, "passo entra");
      cartao.append(el("span", String(i + 1), "numero"), el("p", p));
      adicionar(cartao, 1.45 + i * 0.22);
    });
    const depois = 1.45 + d.passos.length * 0.22;
    if (d.atencao) {
      const a = el("div", undefined, "atencao entra");
      const t = el("p"); // O texto da base já pode vir com o prefixo "Atenção:"; não repetir.
      t.append(el("strong", "Atenção: "), document.createTextNode(d.atencao.replace(/^Atenção:\s*/, ""))); a.appendChild(t);
      adicionar(a, depois);
    }

    // Selo "Fonte conferida": pop, com o check desenhado.
    const selo = el("div", undefined, "selo");
    const ic = el("span", undefined, "selo-icone");
    const check = icone(["M5 12.5l4.5 4.5L19 7.5"], 24, "2.8"); check.setAttribute("stroke", "#fff");
    ic.appendChild(check);
    const txt = el("div");
    txt.appendChild(el("strong", "Fonte conferida"));
    const fonte = el("span"); fonte.append("Verificado em " + d.verificado_em + " · ", linkExterno(d.fonte, d.fonte));
    txt.appendChild(fonte);
    selo.append(ic, txt); adicionar(selo, depois + 0.3);

    const fim = el("div", undefined, "entra");
    if (d.relacionados.length) {
      const vt = el("div", undefined, "veja-tambem");
      vt.appendChild(el("span", "Veja também", "rotulo-exemplos"));
      for (const r of d.relacionados) vt.appendChild(botaoDeAssunto(r.titulo));
      fim.appendChild(vt);
    }
    fim.appendChild(el("p", d.aviso, "nota"));
    adicionar(fim, depois + 0.65);
  } else if (d.decisao === "PEDIR_ESCOLHA") {
    const c = el("div", undefined, "cartao entra");
    c.appendChild(el("p", "Encontrei mais de um assunto parecido. Qual deles você procura?"));
    const vt = el("div", undefined, "veja-tambem");
    for (const x of d.candidatos) vt.appendChild(botaoDeAssunto(x.titulo));
    c.appendChild(vt); adicionar(c, 0);
  } else if (d.decisao === "SEM_BASE") {
    const c = el("div", undefined, "cartao entra");
    c.appendChild(el("p", d.mensagem));
    c.appendChild(el("p", "Assuntos disponíveis: " + d.temas.join(", ") + ".", "apoio"));
    if (/^https?:\/\//.test(d.portal)) c.appendChild(linkExterno("Portal oficial gov.br", d.portal, "link"));
    adicionar(c, 0);
  } else {
    adicionar(el("div", undefined, "cartao entra"), 0).appendChild(el("p", d.mensagem));
  }
}

let perguntando = false;
async function perguntar(texto) {
  if (perguntando) return;
  perguntando = true;
  avisar("");
  try {
    $("pergunta").value = texto;
    desenharResposta(await json(await api("POST", "/api/perguntar", { pergunta: texto })));
  } catch (e) { avisar(e.message); } finally { perguntando = false; }
}
$("form-pergunta").addEventListener("submit", (ev) => { ev.preventDefault(); perguntar($("pergunta").value); });
for (const b of document.querySelectorAll("[data-pergunta]")) b.addEventListener("click", () => perguntar(b.dataset.pergunta));

// ---- Tarefas e lembretes (spec §11): o texto de "quando" é lido no servidor, por regras ----
function desenharTarefas(itens) {
  const ul = $("tarefas-lista"); ul.textContent = "";
  $("tarefas-vazio").hidden = itens.length > 0;
  for (const t of itens) {
    const li = el("li", undefined, "doc");
    const ic = el("span", undefined, "doc-icone azul");
    ic.appendChild(icone(["M12 3a9 9 0 100 18 9 9 0 000-18z", "M8 12.5l3 3 5-6"], 24));
    const texto = el("span", undefined, "doc-nome");
    texto.appendChild(document.createTextNode(t.titulo));
    if (t.quando_texto) texto.appendChild(el("span", "Aviso em " + t.quando_texto, "tarefa-quando"));
    const concluir = el("button", "Concluir", "botao-sec"); concluir.type = "button";
    concluir.setAttribute("aria-label", "Concluir: " + t.titulo);
    concluir.addEventListener("click", () => concluirTarefa(t, li));
    li.append(ic, texto, concluir);
    ul.appendChild(li);
  }
}

async function carregarTarefas() {
  try { desenharTarefas((await json(await api("GET", "/api/tarefas"))).tarefas); }
  catch (e) { avisar(e.message); }
}

async function concluirTarefa(tarefa, linha) {
  avisar("");
  try {
    const d = await json(await api("POST", "/api/tarefas/" + tarefa.id + "/concluir"));
    linha.classList.add("saindo");
    setTimeout(() => desenharTarefas(d.tarefas), SEM_ANIMACAO ? 0 : 300);
  } catch (e) { avisar(e.message); }
}

$("form-tarefa").addEventListener("submit", async (ev) => {
  ev.preventDefault(); avisar(""); $("tarefa-ok").hidden = true;
  // Botão desligado durante o envio: evita tarefa duplicada com dois toques seguidos.
  const botao = ev.currentTarget.querySelector("button[type=submit]");
  if (botao.disabled) return;
  botao.disabled = true;
  try {
    const d = await json(await api("POST", "/api/tarefas", { titulo: $("tarefa-titulo").value, quando: $("tarefa-quando").value }));
    $("tarefa-titulo").value = ""; $("tarefa-quando").value = "";
    $("tarefa-ok").textContent = d.mensagem; $("tarefa-ok").hidden = false;
    desenharTarefas(d.tarefas);
  } catch (e) { avisar(e.message); }
  finally { botao.disabled = false; }
});

// ---- Estado, cofre e ajustes ----
async function carregarEstado() {
  try { estado = await json(await api("GET", "/api/estado")); } catch (e) { avisar(e.message); return; }
  desenharCofre(); desenharAjustes();
}

function formatarTempo(seg) {
  const m = Math.floor(seg / 60), s = seg % 60;
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
}

// Contador de bloqueio do cofre, com o anel esvaziando (circunferência do anel = 151).
function iniciarContador() {
  clearInterval(contadorId);
  const total = Math.max(1, estado.segundos_restantes);
  let resta = estado.segundos_restantes;
  const atualizar = () => {
    $("contador").textContent = formatarTempo(resta);
    $("anel-tempo").style.strokeDashoffset = String(151 * (1 - resta / total));
  };
  atualizar();
  contadorId = setInterval(() => {
    resta -= 1;
    if (resta <= 0) { clearInterval(contadorId); carregarEstado(); return; }  // venceu: pede a senha de novo
    atualizar();
  }, 1000);
}

async function desenharCofre() {
  const indisponivel = !estado.cofre_disponivel;
  $("cofre-sem").hidden = indisponivel || estado.cofre_existe;
  $("cofre-bloqueado").hidden = indisponivel || !estado.cofre_existe || estado.desbloqueado;
  $("cofre-aberto").hidden = indisponivel || !estado.desbloqueado;
  if (indisponivel) { avisar("O cofre não está disponível agora."); return; }
  if (estado.desbloqueado) { iniciarContador(); await listarDocs(); } else { clearInterval(contadorId); }
}

async function listarDocs() {
  try {
    const d = await json(await api("GET", "/api/cofre/docs"));
    const ul = $("docs"); ul.textContent = "";
    $("docs-vazio").hidden = d.docs.length > 0;
    d.docs.forEach((doc, i) => {
      const li = el("li", undefined, "doc");
      atrasar(li, i * 0.1);
      const tipo = ICONES_DOC[i % ICONES_DOC.length];
      const ic = el("span", undefined, "doc-icone " + tipo.classe); ic.appendChild(icone(tipo.tracos, 24));
      const ver = el("button", "Ver", "botao-sec"); ver.type = "button";
      ver.addEventListener("click", () => visualizar(doc));
      const apagar = el("button", "Apagar", "botao-sec perigo"); apagar.type = "button";
      apagar.addEventListener("click", () => apagarDoc(doc, apagar));
      li.append(ic, el("span", doc.nome, "doc-nome"), ver, apagar);
      ul.appendChild(li);
    });
  } catch (e) { if (e.status === 423) carregarEstado(); else avisar(e.message); }
}

async function visualizar(doc) {
  const caixa = $("visualizacao"); caixa.textContent = "";
  try {
    const r = await api("GET", "/api/cofre/docs/" + doc.id);
    if (!r.ok) { await json(r); return; }
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    if (blob.type.startsWith("image/")) {
      const img = el("img"); img.src = url; img.alt = "Documento " + doc.nome; caixa.appendChild(img);
    } else {
      const a = el("a", "Baixar " + doc.nome, "link"); a.href = url; a.download = doc.nome; caixa.appendChild(a);
    }
  } catch (e) { avisar(e.message); }
}

// Apagar em dois passos (docs/ux.md): o primeiro toque pede confirmação no próprio botão.
function apagarDoc(doc, botao) {
  if (botao.dataset.confirma !== "1") {
    botao.dataset.confirma = "1"; botao.textContent = "Confirmar: apagar de vez";
    setTimeout(() => { botao.dataset.confirma = ""; botao.textContent = "Apagar"; }, 5000);
    return;
  }
  api("DELETE", "/api/cofre/docs/" + doc.id).then(json).then(() => { $("visualizacao").textContent = ""; listarDocs(); })
    .catch((e) => avisar(e.message));
}

$("form-criar").addEventListener("submit", async (ev) => {
  ev.preventDefault(); avisar("");
  try {
    await json(await api("POST", "/api/cofre/criar", { senha: $("senha-nova").value }));
    $("senha-nova").value = ""; carregarEstado();
  } catch (e) { avisar(e.message); }
});
$("form-desbloquear").addEventListener("submit", async (ev) => {
  ev.preventDefault(); avisar("");
  try {
    await json(await api("POST", "/api/cofre/desbloquear", { senha: $("senha").value }));
    $("senha").value = ""; carregarEstado();
  } catch (e) { avisar(e.message); }
});
$("bloquear").addEventListener("click", async () => {
  try { await json(await api("POST", "/api/cofre/bloquear")); $("visualizacao").textContent = ""; carregarEstado(); }
  catch (e) { avisar(e.message); }
});

const UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split(" ");
for (const uf of UFS) { const o = el("option", uf); o.value = uf; $("uf").appendChild(o); }

// Temas do resumo da manhã como chips (a marca de check aparece no chip marcado, não só a cor).
function desenharAjustes() {
  $("uf").value = estado.uf || "";
  $("hora").value = estado.hora_briefing || "";
  const caixa = $("temas"); caixa.textContent = "";
  for (const [chave, nome] of Object.entries(estado.temas)) {
    const rotulo = el("label", undefined, "chip");
    const c = el("input"); c.type = "checkbox"; c.value = chave;
    c.checked = estado.temas_briefing.includes(chave);
    rotulo.append(c, el("span", nome));
    caixa.appendChild(rotulo);
  }
}
$("salvar").addEventListener("click", async () => {
  const temas = [...document.querySelectorAll("#temas input:checked")].map((c) => c.value);
  const corpo = { temas };
  if ($("uf").value) corpo.uf = $("uf").value;
  if ($("hora").value) corpo.hora = $("hora").value;
  try { await json(await api("PUT", "/api/config", corpo)); avisar("Salvo."); }
  catch (e) { avisar(e.message); }
});
