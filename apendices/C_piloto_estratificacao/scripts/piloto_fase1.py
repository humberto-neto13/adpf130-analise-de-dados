"""
Piloto de codificação — Fase 1 (versão simplificada).

Codifica as Variáveis 3 (MOM_REST), 4 (SUJ_COM) e 5 (MEIO) nos acórdãos
pertinentes do universo empírico, operando sobre o inteiro teor dos acórdãos
(convertidos para .txt e disponíveis na pasta ./textos).

Objetivo: verificar a distribuição dos casos entre os oito estratos e os três
períodos, sem acesso aos desfechos, para calibrar eventuais agregações antes
da codificação integral.

Pressupostos:
    - Todos os arquivos .txt na pasta ./textos correspondem a acórdãos
      pertinentes (as reclamações não pertinentes já foram excluídas pelo
      pesquisador antes da execução).
    - Os metadados (número da reclamação, classe processual, data) estão
      dentro do próprio texto do acórdão, de modo que não é necessário
      consultar CSV externo.

Parâmetros técnicos (seção 8.5 do projeto):
    - API stateless da Anthropic
    - Modelo: claude-opus-5
    - Prompt caching aplicado às definições operacionais
    - Ordem de submissão aleatorizada
    - Cada acórdão em requisição independente

Uso:
    set ANTHROPIC_API_KEY=sk-ant-...    (Windows)
    export ANTHROPIC_API_KEY=sk-ant-... (Mac/Linux)
    py piloto_fase1.py

Saídas:
    piloto_fase1.csv         — codificação por acórdão
    log_piloto_fase1.txt     — log com custo, tempo e eventuais erros
"""

import json
import os
import random
import sys
import time
from pathlib import Path

import anthropic

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------

MODELO = "claude-opus-5"
MAX_TOKENS = 2048
# Nota: Claude Opus 5 não permite ajuste prévio do parâmetro temperature;
# opera com o valor padrão fixado pelo provedor.

PASTA_TXT = "./textos"
ARQUIVO_SAIDA = "piloto_fase1.csv"
ARQUIVO_LOG = "log_piloto_fase1.txt"


# -----------------------------------------------------------------------------
# Prompt de codificação (cacheado)
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um assistente especializado em análise de decisões do Supremo Tribunal Federal. Sua tarefa é codificar três variáveis materiais do ato reclamado a partir do inteiro teor do acórdão submetido, seguindo definições operacionais precisas.

## Convenções gerais

A codificação opera sobre a descrição do ato reclamado, extraída do relatório do acórdão ou, quando insuficiente, da fundamentação do voto condutor. Não se codifica a partir da descrição feita pela reclamante em sua petição inicial, mas a partir da caracterização adotada pelo Tribunal no acórdão colegiado sob análise.

Quando o texto do acórdão for insuficiente para permitir a codificação de uma variável, registre "ND" (não determinável), com breve justificativa.

## Variável 3 (MOM_REST). Momento da restrição em relação ao ato comunicativo

Captura o momento em que a restrição opera em relação ao ato comunicativo: se anterior à publicação, se posterior à publicação, ou se abrange ambos os momentos.

Extrai-se da parte dispositiva da decisão reclamada. A cumulação (ambos) é reservada aos casos em que o ato reclamado, no mesmo comando, incide sobre conteúdo já publicado e sobre conteúdo futuro.

Classes:
  a) Anterior à publicação. Aplica-se quando o ato reclamado impede a publicação de conteúdo que ainda não foi veiculado.
  b) Posterior à publicação. Aplica-se quando o ato reclamado incide sobre conteúdo já veiculado, impondo remoção, direito de resposta, retificação, indenização ou bloqueio.
  c) Ambos. Aplica-se quando o ato reclamado incide simultaneamente sobre conteúdo já publicado e sobre conteúdo futuro.

Casos-fronteira:
  - Remoção com proibição acessória de republicação idêntica: codifica-se como (b) posterior.
  - Remoção com proibição ampla de novas publicações sobre a matéria: codifica-se como (c) ambos.
  - Indenização isolada por conteúdo já publicado: codifica-se como (b) posterior.
  - Ordem de retirada com prazo antes de publicação prevista: codifica-se como (a) anterior.

## Variável 4 (SUJ_COM). Natureza do sujeito comunicativo protegido

Captura a natureza do sujeito cuja liberdade de expressão foi restringida pelo ato reclamado. A variável identifica quem é o sujeito comunicativo tutelado pela reclamação, e não quem é o reclamante em sentido processual.

Extrai-se do relatório do acórdão, que tipicamente descreve o autor da atividade comunicativa objeto da restrição.

Classes:
  a) Empresa de imprensa profissional (jornal, revista, portal jornalístico com estrutura editorial identificada, emissora de rádio ou de televisão, agência de notícias).
  b) Profissional de imprensa individual (jornalista em atividade profissional, colunista, correspondente).
  c) Sujeito privado não profissional (cidadão comum, blogueiro pessoal, influenciador digital sem estrutura editorial, artista em manifestação não profissional).
  d) Órgão público institucional (administração pública direta ou indireta, poder da República, entidade estatal em atividade comunicativa institucional).
  e) Partido político, associação, sindicato ou entidade coletiva (pessoa jurídica de direito privado com finalidade não jornalística, em manifestação institucional).
  f) Plataforma digital como intermediária (rede social, plataforma de vídeo, provedor de aplicação, quando a restrição incide sobre sua atividade de intermediação de conteúdo alheio).
  g) Pessoa jurídica de direito privado sem atividade comunicativa profissional (empresa em manifestação institucional, publicidade corporativa, ação comunicativa institucional isolada).

Casos-fronteira:
  - Portal digital de nicho sem estrutura editorial claramente identificada: (a) se declara finalidade jornalística e autoria assumida; (c) se se apresenta como blog ou canal pessoal.
  - Influenciador digital com conteúdo de dimensão jornalística: em regra (c). A classe (b) reserva-se aos casos com evidência de exercício profissional do jornalismo.
  - Órgão público em manifestação de agente político individual: (d) se em canal institucional; (c) se em conta pessoal em rede social.
  - Plataforma digital em posição de sujeito passivo da ordem de remoção: (f) plataforma digital como intermediária.

## Variável 5 (MEIO). Meio comunicativo atingido pela restrição

Captura o meio ou os meios comunicativos por meio dos quais circulava a comunicação restringida pelo ato reclamado. O critério é o canal material, não o conteúdo.

CODIFICAÇÃO MÚLTIPLA: registram-se todas as classes correspondentes aos meios efetivamente atingidos pela restrição. Se houver mais de um meio, todos são marcados.

Classes:
  a) Mídia impressa (jornal, revista, boletim, livro, panfleto).
  b) Mídia audiovisual tradicional (rádio, televisão em qualquer modalidade).
  c) Portal jornalístico digital com editor identificado (sítio com finalidade jornalística declarada e estrutura editorial).
  d) Blog ou sítio pessoal (sítio individual sem estrutura editorial institucionalizada).
  e) Rede social (Facebook, Instagram, X/Twitter, TikTok, LinkedIn, YouTube em função de rede social).
  f) Aplicativo de mensageria (WhatsApp, Telegram, Signal em grupos, canais ou listas de transmissão).
  g) Outro meio (podcast em plataforma de streaming, plataforma de conteúdo pago, e-mail em lista corporativa, ato público presencial).

Casos-fronteira:
  - Matéria publicada em edição impressa e no portal digital do mesmo veículo, com restrição sobre ambas: marcar (a) e (c).
  - Conteúdo em veículo tradicional replicado em rede social, com restrição sobre ambos: marcar (a) e (e).
  - YouTube: (e) quando canal pessoal ou coletivo; (c) quando canal oficial de veículo profissional.
  - Blog em plataforma de rede social (Medium, Substack): (d) se estrutura de blog é predominante; (e) se interação social é predominante.

## Formato de saída

Responda EXCLUSIVAMENTE com um objeto JSON válido, sem qualquer texto adicional, no seguinte formato:

{
  "momento_restricao": "a" | "b" | "c" | "ND",
  "momento_restricao_justificativa": "uma frase breve",
  "sujeito_comunicativo": "a" | "b" | "c" | "d" | "e" | "f" | "g" | "ND",
  "sujeito_comunicativo_justificativa": "uma frase breve",
  "meio_comunicativo": ["a", ...] (lista de uma ou mais letras; "ND" se não determinável),
  "meio_comunicativo_justificativa": "uma frase breve"
}"""


# -----------------------------------------------------------------------------
# Funções
# -----------------------------------------------------------------------------

def codificar_acordao(client, nome_arquivo, texto, tentativa=1, max_tentativas=3):
    """Submete o inteiro teor de um acórdão à API e retorna a codificação."""
    conteudo = f"""Arquivo: {nome_arquivo}

=================== INTEIRO TEOR ===================

{texto}

=================== FIM DO INTEIRO TEOR ===================

Aplique as definições operacionais e responda no formato JSON especificado."""

    try:
        resp = client.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{"role": "user", "content": conteudo}],
        )
        # Extrai o bloco de texto da resposta (Opus 5 pode devolver ThinkingBlocks
        # antes do TextBlock; localiza-se explicitamente o bloco de texto)
        texto_resp = None
        for bloco in resp.content:
            if hasattr(bloco, "text"):
                texto_resp = bloco.text.strip()
                break
        if texto_resp is None:
            raise ValueError("Nenhum bloco de texto encontrado na resposta")

        # Remover eventuais fences de código
        if texto_resp.startswith("```"):
            texto_resp = texto_resp.split("```")[1]
            if texto_resp.startswith("json"):
                texto_resp = texto_resp[4:]
            texto_resp = texto_resp.strip()

        dados = json.loads(texto_resp)

        usage = resp.usage
        return {
            "momento_restricao": dados.get("momento_restricao", "ERRO"),
            "momento_restricao_justificativa": dados.get("momento_restricao_justificativa", ""),
            "sujeito_comunicativo": dados.get("sujeito_comunicativo", "ERRO"),
            "sujeito_comunicativo_justificativa": dados.get("sujeito_comunicativo_justificativa", ""),
            "meio_comunicativo": dados.get("meio_comunicativo", []),
            "meio_comunicativo_justificativa": dados.get("meio_comunicativo_justificativa", ""),
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "cache_read_tokens": getattr(usage, "cache_read_input_tokens", 0) or 0,
            "cache_creation_tokens": getattr(usage, "cache_creation_input_tokens", 0) or 0,
            "erro": None,
        }
    except json.JSONDecodeError as e:
        if tentativa < max_tentativas:
            time.sleep(2)
            return codificar_acordao(client, nome_arquivo, texto, tentativa + 1, max_tentativas)
        return {
            "momento_restricao": "ERRO",
            "momento_restricao_justificativa": f"JSON inválido: {e}",
            "sujeito_comunicativo": "ERRO",
            "sujeito_comunicativo_justificativa": "",
            "meio_comunicativo": [],
            "meio_comunicativo_justificativa": "",
            "input_tokens": 0, "output_tokens": 0,
            "cache_read_tokens": 0, "cache_creation_tokens": 0,
            "erro": str(e),
        }
    except Exception as e:
        if tentativa < max_tentativas:
            time.sleep(2 ** tentativa)
            return codificar_acordao(client, nome_arquivo, texto, tentativa + 1, max_tentativas)
        return {
            "momento_restricao": "ERRO",
            "momento_restricao_justificativa": f"Erro API: {e}",
            "sujeito_comunicativo": "ERRO",
            "sujeito_comunicativo_justificativa": "",
            "meio_comunicativo": [],
            "meio_comunicativo_justificativa": "",
            "input_tokens": 0, "output_tokens": 0,
            "cache_read_tokens": 0, "cache_creation_tokens": 0,
            "erro": str(e),
        }


def estimar_custo(input_tokens, output_tokens, cache_read, cache_creation):
    """Estima custo em USD para Claude Opus 5."""
    return (
        (input_tokens / 1_000_000) * 5.00
        + (output_tokens / 1_000_000) * 25.00
        + (cache_creation / 1_000_000) * 6.25
        + (cache_read / 1_000_000) * 0.50
    )


# -----------------------------------------------------------------------------
# Execução principal
# -----------------------------------------------------------------------------

def main():
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRO: variável ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
        sys.exit(1)

    log(f"[{time.strftime('%H:%M:%S')}] Iniciando Piloto Fase 1")
    log(f"Modelo: {MODELO}")

    # Listar arquivos .txt da pasta
    pasta = Path(PASTA_TXT)
    if not pasta.exists():
        log(f"ERRO: pasta {PASTA_TXT} não encontrada.")
        sys.exit(1)

    arquivos = sorted(pasta.glob("*.txt"))
    if not arquivos:
        log(f"ERRO: nenhum arquivo .txt encontrado em {PASTA_TXT}.")
        sys.exit(1)

    log(f"Arquivos a codificar: {len(arquivos)}")

    # Aleatorizar ordem de submissão (seed fixa para reprodutibilidade)
    random.seed(42)
    random.shuffle(arquivos)

    client = anthropic.Anthropic()
    resultados = []
    inicio = time.time()

    for i, caminho in enumerate(arquivos, 1):
        nome = caminho.name
        try:
            texto = caminho.read_text(encoding="utf-8")
        except Exception as e:
            log(f"  [{i:3d}/{len(arquivos)}] ✗ {nome}: erro ao ler arquivo ({e})")
            continue

        t0 = time.time()
        r = codificar_acordao(client, nome, texto)
        dt = time.time() - t0

        resultados.append({
            "arquivo": nome,
            "momento_restricao": r["momento_restricao"],
            "sujeito_comunicativo": r["sujeito_comunicativo"],
            "meio_comunicativo": ",".join(r["meio_comunicativo"]) if isinstance(r["meio_comunicativo"], list) else r["meio_comunicativo"],
            "momento_restricao_justificativa": r["momento_restricao_justificativa"],
            "sujeito_comunicativo_justificativa": r["sujeito_comunicativo_justificativa"],
            "meio_comunicativo_justificativa": r["meio_comunicativo_justificativa"],
            "input_tokens": r["input_tokens"],
            "output_tokens": r["output_tokens"],
            "cache_read_tokens": r["cache_read_tokens"],
            "cache_creation_tokens": r["cache_creation_tokens"],
            "erro": r["erro"],
        })

        mom = r["momento_restricao"]
        suj = r["sujeito_comunicativo"]
        meio = ",".join(r["meio_comunicativo"]) if isinstance(r["meio_comunicativo"], list) else "?"
        log(f"  [{i:3d}/{len(arquivos)}] {nome:20s} → mom={mom} suj={suj} meio={meio} ({dt:.1f}s)")

    tempo_total = time.time() - inicio
    log(f"\n[{time.strftime('%H:%M:%S')}] Execução concluída em {tempo_total/60:.1f} minutos")

    # Salvar resultados em CSV (usando csv nativo para não depender de pandas)
    import csv as csv_mod
    if resultados:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8", newline="") as f:
            writer = csv_mod.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        log(f"Resultado salvo em: {ARQUIVO_SAIDA}")

    # Estatísticas
    log("\n=== Estatísticas ===")
    total_input = sum(r["input_tokens"] for r in resultados)
    total_output = sum(r["output_tokens"] for r in resultados)
    total_cache_read = sum(r["cache_read_tokens"] for r in resultados)
    total_cache_creation = sum(r["cache_creation_tokens"] for r in resultados)
    custo = estimar_custo(total_input, total_output, total_cache_read, total_cache_creation)

    log(f"Tokens input total: {total_input:,}")
    log(f"Tokens output total: {total_output:,}")
    log(f"Tokens cache_read: {total_cache_read:,}")
    log(f"Tokens cache_creation: {total_cache_creation:,}")
    log(f"Custo estimado (Claude Opus 5): USD {custo:.4f}")

    n_erros = sum(1 for r in resultados if r["momento_restricao"] == "ERRO")
    n_nd = sum(1 for r in resultados if r["momento_restricao"] == "ND")
    log(f"\nAcórdãos codificados com sucesso: {len(resultados) - n_erros}")
    log(f"Acórdãos com erro: {n_erros}")
    log(f"Casos com pelo menos uma variável ND: {n_nd}")

    Path(ARQUIVO_LOG).write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
