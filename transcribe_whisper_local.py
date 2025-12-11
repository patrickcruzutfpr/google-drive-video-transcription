"""
Transcrição de Vídeo com Whisper Large V3 (Local)

Este script realiza a transcrição profissional de vídeos MP4 usando o modelo
Whisper Large V3 localmente via openai-whisper, otimizado para processamento
preciso de conteúdo em Português Brasileiro.

Autor: Aplicação de Transcrição Automatizada
Data: 11 de Dezembro de 2025
"""

import os
import sys
import whisper
from datetime import datetime

# Configurações
INPUT_VIDEO = r"data\aula_gestao-da-inovacao-em-ciencia-de-dados_20251122_recording.mp4"
OUTPUT_FILE = r"data\transcricao_whisper_local.txt"
MODEL_NAME = "large-v3"


def main():
    """Função principal que executa o processo de transcrição."""
    print("="*80)
    print("TRANSCRIÇÃO DE VÍDEO COM WHISPER LARGE V3 (LOCAL)".center(80))
    print("="*80)
    
    # Verificar se o arquivo existe
    if not os.path.exists(INPUT_VIDEO):
        print(f"ERRO: Arquivo de vídeo não encontrado: {INPUT_VIDEO}")
        print(f"\nCaminho esperado: {os.path.abspath(INPUT_VIDEO)}")
        sys.exit(1)
    
    # Exibir informações do arquivo
    file_size_mb = os.path.getsize(INPUT_VIDEO) / (1024 * 1024)
    print(f"\nVídeo encontrado: {INPUT_VIDEO}")
    print(f"Tamanho do arquivo: {file_size_mb:.2f} MB")
    
    # Carregar modelo
    print(f"\nCarregando modelo Whisper {MODEL_NAME}...")
    print("(Primeira execução: pode baixar ~3GB de modelo)")
    model = whisper.load_model(MODEL_NAME)
    print("Modelo carregado com sucesso!")
    
    # Transcrever
    print("\nIniciando transcrição...")
    print("Isso pode levar vários minutos dependendo do tamanho do vídeo...")
    
    result = model.transcribe(
        INPUT_VIDEO,
        language="pt",
        verbose=True,
        fp16=False  # Use False se não tiver GPU CUDA
    )
    
    print("\nTranscrição concluída!")
    
    # Criar diretório de saída se não existir
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Criar cabeçalho
    header = f"""{'='*80}
TRANSCRIÇÃO DE VÍDEO - GESTÃO DA INOVAÇÃO EM CIÊNCIA DE DADOS
{'='*80}

Arquivo Original: {INPUT_VIDEO}
Data de Transcrição: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
Modelo Utilizado: Whisper {MODEL_NAME}
Idioma: Português Brasileiro (pt-BR)

{'='*80}

"""
    
    # Salvar transcrição
    print(f"\nSalvando transcrição em: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(result["text"])
        f.write(f"\n\n{'='*80}\n")
        f.write("FIM DA TRANSCRIÇÃO\n")
        f.write(f"{'='*80}\n")
    
    print("Transcrição salva com sucesso!")
    
    # Exibir estatísticas
    word_count = len(result["text"].split())
    char_count = len(result["text"])
    print(f"\nEstatísticas da transcrição:")
    print(f"   - Palavras: {word_count:,}")
    print(f"   - Caracteres: {char_count:,}")
    print(f"   - Tamanho do arquivo: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")
    
    print("\n" + "="*80)
    print("PROCESSO CONCLUÍDO COM SUCESSO!".center(80))
    print("="*80)
    print(f"\nArquivo de transcrição: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
