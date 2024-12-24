import genanki
import pandas as pd
import random
import os
import logging
import sys

# Configuração de logs para depuração e informações
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def generate_unique_id():
    """Gera um ID único aleatório para o modelo e deck."""
    return random.randrange(1 << 30, 1 << 31)

def create_model(nome_modelo, front_template, back_template, css="", fields=None, templates=None):
    """Cria um modelo de cartão Anki."""
    return genanki.Model(
        generate_unique_id(),
        nome_modelo,
        fields=fields if fields else [
            {'name': 'Frente'},
            {'name': 'Verso'},
        ],
        templates=templates if templates else [
            {
                'name': 'Cartão 1',
                'qfmt': front_template,
                'afmt': back_template,
            },
        ],
        css=css
    )

def main():
    # Definir os caminhos dos arquivos
    CSV_FILE = 'cartoes.csv'
    MEDIA_DIR = 'media'
    OUTPUT_APKG = 'stairway_to_heaven.apkg'

    # Verificar se o arquivo CSV existe
    if not os.path.exists(CSV_FILE):
        logging.error(f"Arquivo CSV '{CSV_FILE}' não encontrado.")
        sys.exit(1)

    # Ler os dados do CSV
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
        logging.info("Arquivo CSV lido com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao ler o CSV: {e}")
        sys.exit(1)

    # Verificar se as colunas necessárias existem
    required_columns = ['Frente', 'Verso']
    for col in required_columns:
        if col not in df.columns:
            logging.error(f"Coluna '{col}' faltando no CSV.")
            sys.exit(1)

    # Carregar mídia se houver (inicialmente, sem mídia)
    media_files = []
    # Aqui, você pode adicionar lógica para carregar arquivos de mídia no futuro

    # Definir o modelo do cartão
    modelo_basico = create_model(
        'Modelo Básico',
        '{{Frente}}',
        '{{Verso}}',
        css="""
        .card {
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        """
    )

    # Criar o deck
    deck_id = generate_unique_id()
    deck = genanki.Deck(
        deck_id,
        'Stairway to Heaven - Letra e Tradução'
    )

    # Adicionar notas ao deck
    total_linhas = len(df)
    for index, row in df.iterrows():
        frente = str(row['Frente']).strip()
        verso = str(row['Verso']).strip()

        if not frente or not verso:
            logging.warning(f"Linha {index + 2}: 'Frente' ou 'Verso' está vazio. Pulando.")
            continue

        try:
            nota = genanki.Note(
                model=modelo_basico,
                fields=[frente, verso]
            )
            deck.add_note(nota)
            logging.info(f"Adicionado cartão {index + 1}/{total_linhas}: {frente} -> {verso}")
        except Exception as e:
            logging.error(f"Erro ao adicionar cartão na linha {index + 2}: {e}")

    # Criar a package e adicionar mídia (vazia inicialmente)
    package = genanki.Package(deck)
    package.media_files = media_files  # Lista vazia inicialmente

    # Gerar o arquivo .apkg
    try:
        package.write_to_file(OUTPUT_APKG)
        logging.info(f"Deck gerado com sucesso: {OUTPUT_APKG}")
    except Exception as e:
        logging.error(f"Erro ao gerar o deck: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
