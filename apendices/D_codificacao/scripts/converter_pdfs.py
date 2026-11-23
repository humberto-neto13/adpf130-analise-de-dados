"""
Conversor de PDFs para arquivos de texto.

Percorre uma pasta com PDFs dos acórdãos e gera, para cada um, um arquivo .txt
correspondente, extraindo o texto do PDF. A conversão é executada localmente,
sem chamadas à API externa e sem custo.

Convenção de nomenclatura preservada:
    12345.pdf         → 12345.txt
    45682.1.pdf       → 45682.1.txt
    45682.2.pdf       → 45682.2.txt

Uso:
    Configure PASTA_PDF e PASTA_TXT no bloco de configuração abaixo,
    e execute:

        pip install -r requirements.txt
        python converter_pdfs.py

Se o script encontrar PDFs que exigem OCR (imagens de texto em vez de texto
extraível), reporta o problema para tratamento manual.
"""

import os
import sys
from pathlib import Path

import pypdf

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------

# Pasta com os PDFs originais (ajuste para o caminho no seu computador)
PASTA_PDF = "./pdfs"

# Pasta onde os arquivos .txt serão salvos
PASTA_TXT = "./textos"

# Comprimento mínimo (em caracteres) para considerar a extração bem-sucedida.
# PDFs escaneados sem OCR normalmente extraem poucos caracteres.
MIN_CARACTERES = 500


# -----------------------------------------------------------------------------
# Execução
# -----------------------------------------------------------------------------

def extrair_texto(caminho_pdf):
    """Extrai o texto de um PDF, página por página."""
    with open(caminho_pdf, "rb") as f:
        leitor = pypdf.PdfReader(f)
        paginas = []
        for pagina in leitor.pages:
            texto = pagina.extract_text() or ""
            paginas.append(texto)
    return "\n\n".join(paginas)


def main():
    pasta_pdf = Path(PASTA_PDF)
    pasta_txt = Path(PASTA_TXT)

    if not pasta_pdf.exists():
        print(f"ERRO: pasta {PASTA_PDF} não encontrada.", file=sys.stderr)
        sys.exit(1)

    pasta_txt.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(pasta_pdf.glob("*.pdf"))
    if not pdfs:
        print(f"Nenhum PDF encontrado em {PASTA_PDF}.", file=sys.stderr)
        sys.exit(1)

    print(f"Encontrados {len(pdfs)} PDFs em {PASTA_PDF}")
    print(f"Convertendo para .txt em {PASTA_TXT}\n")

    sucessos = 0
    problemas = []

    for i, caminho_pdf in enumerate(pdfs, 1):
        nome_base = caminho_pdf.stem  # "45682.1" a partir de "45682.1.pdf"
        caminho_txt = pasta_txt / f"{nome_base}.txt"

        try:
            texto = extrair_texto(caminho_pdf)
        except Exception as e:
            print(f"  [{i:3d}/{len(pdfs)}] ✗ {caminho_pdf.name}: erro ao ler PDF ({e})")
            problemas.append((caminho_pdf.name, f"erro ao ler PDF: {e}"))
            continue

        if len(texto.strip()) < MIN_CARACTERES:
            print(f"  [{i:3d}/{len(pdfs)}] ⚠ {caminho_pdf.name}: extração escassa ({len(texto)} chars) — pode exigir OCR")
            problemas.append((caminho_pdf.name, f"extração escassa: {len(texto)} caracteres"))
            # Mesmo assim salva o texto extraído
        else:
            print(f"  [{i:3d}/{len(pdfs)}] ✓ {caminho_pdf.name}: {len(texto)} caracteres")

        caminho_txt.write_text(texto, encoding="utf-8")
        sucessos += 1

    print(f"\n=== Conversão concluída ===")
    print(f"Sucessos: {sucessos}/{len(pdfs)}")

    if problemas:
        print(f"\nArquivos com problemas ({len(problemas)}):")
        for nome, msg in problemas:
            print(f"  {nome}: {msg}")
        print("\nOs arquivos com extração escassa provavelmente exigem OCR.")
        print("Ferramentas online como OCRmyPDF ou iLovePDF resolvem casos assim.")


if __name__ == "__main__":
    main()
