"""
Transcrição de Vídeo com Google Gemini Flash

Este script realiza a transcrição profissional de vídeos MP4 usando o modelo
Gemini Flash do Google AI, otimizado para processamento rápido e preciso de
conteúdo em Português Brasileiro.

Autor: Aplicação de Transcrição Automatizada
Data: 11 de Dezembro de 2025
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
INPUT_VIDEO = r"data\aula_gestao-da-inovacao-em-ciencia-de-dados_20251122_recording.mp4"
OUTPUT_FILE = r"data\transcricao_aula_gestao-da-inovacao-em-ciencia-de-dados_20251122.txt"
MODEL_NAME = "gemini-1.5-flash"


def configure_gemini():
    """Configura a API do Google Gemini com a chave de autenticação."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("ERRO: Chave da API do Google não encontrada!")
        print("\nPor favor, siga os passos:")
        print("1. Copie o arquivo .env.example para .env")
        print("2. Obtenha sua chave em: https://aistudio.google.com/api-keys")
        print("3. Adicione a chave no arquivo .env: GOOGLE_API_KEY=sua_chave_aqui")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    print("API do Google Gemini configurada com sucesso!")


def check_video_exists(video_path):
    """Verifica se o arquivo de vídeo existe."""
    if not os.path.exists(video_path):
        print(f"ERRO: Arquivo de vídeo não encontrado: {video_path}")
        print(f"\nCaminho esperado: {os.path.abspath(video_path)}")
        sys.exit(1)
    
    # Exibir informações do arquivo
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"\nVídeo encontrado: {video_path}")
    print(f"Tamanho do arquivo: {file_size_mb:.2f} MB")


def upload_video(video_path):
    """
    Faz upload do vídeo para o Google AI e aguarda o processamento.
    
    Args:
        video_path: Caminho para o arquivo de vídeo
        
    Returns:
        Objeto do arquivo processado
    """
    print("\nFazendo upload do vídeo para o Google AI...")
    print("Isso pode levar alguns minutos dependendo do tamanho do arquivo...")
    
    try:
        video_file = genai.upload_file(path=video_path)
        print(f"Upload concluído: {video_file.name}")
        
        # Aguardar processamento do vídeo
        print("\nAguardando processamento do vídeo...")
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(5)
            video_file = genai.get_file(video_file.name)
        
        print("\n")
        
        if video_file.state.name == "FAILED":
            raise ValueError(f"Falha no processamento do vídeo: {video_file.state.name}")
        
        print("Vídeo processado e pronto para transcrição!")
        return video_file
        
    except Exception as e:
        print(f"\nERRO durante upload: {str(e)}")
        sys.exit(1)


def transcribe_video(video_file):
    """
    Transcreve o vídeo usando o modelo Gemini Flash.
    
    Args:
        video_file: Objeto do arquivo de vídeo processado
        
    Returns:
        Texto da transcrição
    """
    print("\nIniciando transcrição com Gemini Flash...")
    print("Processando conteúdo de áudio e vídeo...")
    
    # Criar modelo
    model = genai.GenerativeModel(model_name=MODEL_NAME)
    
    # Prompt otimizado para transcrição profissional em português brasileiro
    prompt = """
    Por favor, transcreva este vídeo de forma profissional e precisa.
    
    INSTRUÇÕES IMPORTANTES:
    - Transcreva TODO o conteúdo de áudio do vídeo
    - Use Português Brasileiro correto e formal
    - Mantenha a pontuação adequada
    - Identifique diferentes falantes se houver (use "Palestrante 1:", "Palestrante 2:", etc.)
    - Organize o texto em parágrafos lógicos
    - Corrija erros de gramática apenas se forem claramente equívocos de fala
    - Mantenha termos técnicos em sua forma original
    - Indique pausas longas com [pausa]
    - Indique conteúdo inaudível com [inaudível]
    - Inclua timestamps aproximados a cada 5 minutos no formato [MM:SS]
    
    Forneça uma transcrição completa, limpa e profissional do conteúdo.
    """
    
    try:
        # Gerar transcrição
        response = model.generate_content(
            [video_file, prompt],
            request_options={"timeout": 600}  # Timeout de 10 minutos
        )
        
        print("Transcrição concluída com sucesso!")
        return response.text
        
    except Exception as e:
        print(f"\nERRO durante transcrição: {str(e)}")
        sys.exit(1)


def save_transcription(transcription, output_path):
    """
    Salva a transcrição em um arquivo de texto formatado.
    
    Args:
        transcription: Texto da transcrição
        output_path: Caminho para salvar o arquivo
    """
    print(f"\nSalvando transcrição em: {output_path}")
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Criar cabeçalho
    header = f"""{'='*80}
TRANSCRIÇÃO DE VÍDEO - GESTÃO DA INOVAÇÃO EM CIÊNCIA DE DADOS
{'='*80}

Arquivo Original: {INPUT_VIDEO}
Data de Transcrição: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
Modelo Utilizado: {MODEL_NAME}
Idioma: Português Brasileiro (pt-BR)

{'='*80}

"""
    
    # Salvar arquivo
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(transcription)
            f.write(f"\n\n{'='*80}\n")
            f.write("FIM DA TRANSCRIÇÃO\n")
            f.write(f"{"="*80}\n")
        
        print("Transcrição salva com sucesso!")
        
        # Exibir estatísticas
        word_count = len(transcription.split())
        char_count = len(transcription)
        print(f"\nEstatísticas da transcrição:")
        print(f"   - Palavras: {word_count:,}")
        print(f"   - Caracteres: {char_count:,}")
        print(f"   - Tamanho do arquivo: {os.path.getsize(output_path) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"\nERRO ao salvar arquivo: {str(e)}")
        sys.exit(1)


def cleanup_uploaded_file(video_file):
    """Remove o arquivo do servidor do Google após a transcrição."""
    try:
        genai.delete_file(video_file.name)
        print("\nArquivo removido do servidor do Google AI")
    except Exception as e:
        print(f"\nAviso: Não foi possível remover o arquivo do servidor: {str(e)}")


def main():
    """Função principal que executa o processo de transcrição."""
    print("="*80)
    print("TRANSCRIÇÃO DE VÍDEO COM GOOGLE GEMINI FLASH".center(80))
    print("="*80)
    
    # Passo 1: Configurar API
    configure_gemini()
    
    # Passo 2: Verificar vídeo
    check_video_exists(INPUT_VIDEO)
    
    # Passo 3: Upload do vídeo
    video_file = upload_video(INPUT_VIDEO)
    
    # Passo 4: Transcrever
    transcription = transcribe_video(video_file)
    
    # Passo 5: Salvar resultado
    save_transcription(transcription, OUTPUT_FILE)
    
    # Passo 6: Limpeza
    cleanup_uploaded_file(video_file)
    
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
        sys.exit(1)
