// Front do painel (Mini App e navegador). Sem eval, sem innerHTML com dado da rede:
// todo texto vindo do servidor entra por textContent. O front só desenha; o conteúdo
// das orientações vem pronto da base (spec §10.5).
"use strict";

const tg = window.Telegram && window.Telegram.WebApp;
if (tg) { tg.ready(); tg.expand(); }
const SEM_ANIMACAO = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
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
  const el = $("aviso");
  el.textContent = texto || "";
  el.hidden = !texto;
}

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto !== undefined) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

// ---- Abas ----
function abrirAba(nome) {
  for (const a of ["perguntar", "cofre", "ajustes"]) {
    $("aba-" + a).setAttribute("aria-selected", String(a === nome));
    $("tela-" + a).hidden = a !== nome;
  }
  avisar("");
  if (nome !== "perguntar") carregarEstado();
}
for (const a of ["perguntar", "cofre", "ajustes"]) $("aba-" + a).addEventListener("click", () => abrirAba(a));

// ---- Perguntar: cena da verificação (≈3 s no máximo, docs/ux.md §9) ----
const esperar = (ms) => new Promise((ok) => setTimeout(ok, SEM_ANIMACAO ? 0 : ms));

function cartao() { const c = el("div", undefined, "cartao entra"); $("cena").appendChild(c); return c; }

async function desenharResposta(d) {
  const cena = $("cena");
  cena.textContent = "";
  if (d.decisao === "RESPONDER") {
    const c1 = cartao();
    c1.appendChild(el("p", "Consultando " + d.total_orientacoes + " orientações verificadas…", "consulta"));
    await esperar(700);
    const c2 = cartao();
    c2.appendChild(el("h2", d.titulo));
    const lista = el("ol");
    for (const p of d.passos) { lista.appendChild(el("li", p)); }
    c2.appendChild(lista);
    if (d.atencao) c2.appendChild(el("p", "Atenção: " + d.atencao, "atencao"));
    await esperar(900);
    const c3 = cartao();
    c3.appendChild(el("span", "Fonte conferida em " + d.verificado_em, "selo"));
    const fonte = el("p", undefined, "fonte");
    fonte.appendChild(document.createTextNode("Fonte: "));
    // Só vira link se for http(s): nunca javascript: vindo de dado (defesa extra).
    if (/^https?:\/\//.test(d.fonte)) {
      const a = el("a", d.fonte); a.href = d.fonte; a.target = "_blank"; a.rel = "noopener noreferrer";
      fonte.appendChild(a);
    } else { fonte.appendChild(document.createTextNode(d.fonte)); }
    c3.appendChild(fonte);
    await esperar(700);
    const c4 = cartao();
    if (d.relacionados.length) {
      c4.appendChild(el("p", "Continue consultando:", "apoio"));
      for (const r of d.relacionados) {
        const b = el("button", r.titulo, "opcao");
        b.type = "button";
        b.addEventListener("click", () => perguntar(r.titulo));
        c4.appendChild(b);
      }
    }
    c4.appendChild(el("p", d.aviso, "apoio"));
  } else if (d.decisao === "PEDIR_ESCOLHA") {
    const c = cartao();
    c.appendChild(el("p", "Encontrei mais de um assunto parecido. Qual deles você procura?"));
    for (const x of d.candidatos) {
      const b = el("button", x.titulo, "opcao"); b.type = "button";
      b.addEventListener("click", () => perguntar(x.titulo));
      c.appendChild(b);
    }
  } else if (d.decisao === "SEM_BASE") {
    const c = cartao();
    c.appendChild(el("p", d.mensagem));
    c.appendChild(el("p", "Assuntos disponíveis: " + d.temas.join(", ") + ".", "apoio"));
    if (/^https?:\/\//.test(d.portal)) {
      const a = el("a", "Portal oficial gov.br"); a.href = d.portal; a.target = "_blank"; a.rel = "noopener noreferrer";
      c.appendChild(a);
    }
  } else {
    cartao().appendChild(el("p", d.mensagem));
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

// ---- Estado, cofre e ajustes ----
async function carregarEstado() {
  try { estado = await json(await api("GET", "/api/estado")); } catch (e) { avisar(e.message); return; }
  desenharCofre(); desenharAjustes();
}

function formatarTempo(seg) {
  const m = Math.floor(seg / 60), s = seg % 60;
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
}

function iniciarContador() {
  clearInterval(contadorId);
  let resta = estado.segundos_restantes;
  $("contador").textContent = formatarTempo(resta);
  contadorId = setInterval(() => {
    resta -= 1;
    if (resta <= 0) { clearInterval(contadorId); carregarEstado(); return; }  // venceu: pede a senha de novo
    $("contador").textContent = formatarTempo(resta);
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
    for (const doc of d.docs) {
      const li = el("li");
      li.appendChild(el("span", doc.nome));
      const ver = el("button", "Ver"); ver.type = "button";
      ver.addEventListener("click", () => visualizar(doc));
      const apagar = el("button", "Apagar"); apagar.type = "button";
      apagar.addEventListener("click", () => apagarDoc(doc, apagar));
      li.append(ver, apagar);
      ul.appendChild(li);
    }
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
      const a = el("a", "Baixar " + doc.nome); a.href = url; a.download = doc.nome; caixa.appendChild(a);
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

function desenharAjustes() {
  $("uf").value = estado.uf || "";
  const caixa = $("temas"); caixa.textContent = ""; caixa.className = "temas";
  for (const [chave, nome] of Object.entries(estado.temas)) {
    const rotulo = el("label");
    const c = el("input"); c.type = "checkbox"; c.value = chave;
    c.checked = estado.temas_briefing.includes(chave);
    rotulo.append(c, document.createTextNode(nome));
    caixa.appendChild(rotulo);
  }
}
$("salvar").addEventListener("click", async () => {
  const temas = [...document.querySelectorAll("#temas input:checked")].map((c) => c.value);
  const corpo = { temas };
  if ($("uf").value) corpo.uf = $("uf").value;
  try { await json(await api("PUT", "/api/config", corpo)); avisar("Salvo."); }
  catch (e) { avisar(e.message); }
});
