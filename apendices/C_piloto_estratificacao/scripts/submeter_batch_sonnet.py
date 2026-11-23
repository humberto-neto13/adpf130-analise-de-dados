"""
Piloto Fase 1 — Submissão via Batch API.

Prepara o arquivo JSONL com as requisições de codificação das Variáveis 3, 4 e 5
e submete para a Batch API da Anthropic. A Batch API oferece desconto de 50%
em relação às chamadas síncronas, com processamento assíncrono em até 24 horas
(costuma ser bem mais rápido).

Uso:
    set ANTHROPIC_API_KEY=sk-ant-...    (Windows)
    export ANTHROPIC_API_KEY="sk-ant-..." (Mac/Linux)
    py submeter_batch.py

O script salva o ID do lote em batch_id.txt. Use verificar_batch.py para
consultar o status posteriormente.
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

MODELO = "claude-sonnet-5"
MAX_TOKENS = 2048

PASTA_TXT = "./textos"
ARQUIVO_JSONL = "requisicoes_batch_sonnet.jsonl"
ARQUIVO_BATCH_ID = "batch_id_sonnet.txt"


# -----------------------------------------------------------------------------
# Prompt de codificação (idêntico ao script síncrono)
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
# Execução
# -----------------------------------------------------------------------------

def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRO: variável ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
        sys.exit(1)

    print(f"[{time.strftime('%H:%M:%S')}] Preparando submissão à Batch API")
    print(f"Modelo: {MODELO}")

    # Listar arquivos .txt
    pasta = Path(PASTA_TXT)
    if not pasta.exists():
        print(f"ERRO: pasta {PASTA_TXT} não encontrada.", file=sys.stderr)
        sys.exit(1)

    arquivos = sorted(pasta.glob("*.txt"))
    if not arquivos:
        print(f"ERRO: nenhum arquivo .txt encontrado em {PASTA_TXT}.", file=sys.stderr)
        sys.exit(1)

    # Aleatorizar ordem
    random.seed(42)
    random.shuffle(arquivos)

    print(f"Submetendo {len(arquivos)} arquivos.")

    # Preparar arquivo JSONL
    print(f"\nGerando {ARQUIVO_JSONL}...")
    with open(ARQUIVO_JSONL, "w", encoding="utf-8") as f:
        for arquivo in arquivos:
            try:
                texto = arquivo.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  ✗ {arquivo.name}: erro ao ler ({e})")
                continue

            conteudo = f"""Arquivo: {arquivo.name}

=================== INTEIRO TEOR ===================

{texto}

=================== FIM DO INTEIRO TEOR ===================

Aplique as definições operacionais e responda no formato JSON especificado."""

            # custom_id é como a Batch API identifica cada requisição no output.
            # A API exige padrão ^[a-zA-Z0-9_-]{1,64}$, então substituímos o
            # ponto (usado em nomes como 45682.1.txt) por underscore.
            custom_id = arquivo.stem.replace(".", "_")

            requisicao = {
                "custom_id": custom_id,
                "params": {
                    "model": MODELO,
                    "max_tokens": MAX_TOKENS,
                    "system": [
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    "messages": [{"role": "user", "content": conteudo}],
                }
            }
            f.write(json.dumps(requisicao, ensure_ascii=False) + "\n")

    tamanho_arquivo = Path(ARQUIVO_JSONL).stat().st_size
    print(f"Arquivo gerado: {tamanho_arquivo:,} bytes")

    # Submeter à Batch API
    print(f"\nSubmetendo à Batch API...")
    client = anthropic.Anthropic()

    with open(ARQUIVO_JSONL, "rb") as f:
        # A Batch API aceita requisições diretamente; a leitura do arquivo é feita
        # pelo SDK internamente
        requests_list = []
        with open(ARQUIVO_JSONL, "r", encoding="utf-8") as fr:
            for linha in fr:
                requests_list.append(json.loads(linha))

    batch = client.messages.batches.create(requests=requests_list)

    print(f"\n=== Lote criado ===")
    print(f"ID: {batch.id}")
    print(f"Status: {batch.processing_status}")
    print(f"Requisições: {batch.request_counts.processing} em processamento")

    Path(ARQUIVO_BATCH_ID).write_text(batch.id, encoding="utf-8")
    print(f"\nID salvo em: {ARQUIVO_BATCH_ID}")
    print(f"\nUse 'py processar_batch_sonnet.py' para baixar e processar os resultados.")
    print(f"Se o lote ainda estiver em processamento, o script informará o status.")


if __name__ == "__main__":
    main()

