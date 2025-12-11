"""
Transcrição de Vídeo com Google Gemini Flash (com Chunking de Áudio)

Este script realiza a transcrição profissional de vídeos MP4 usando o modelo
Gemini 2.0 Flash do Google AI. Para vídeos longos, extrai o áudio e divide
em chunks para processar separadamente, evitando limites de tamanho.

Autor: Aplicação de Transcrição Automatizada
Data: 11 de Dezembro de 2025
"""

import os
import sys
import time
import subprocess
import math
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis de ambiente
load_dotenv()

# Importar configurações
try:
    import config
except ImportError:
    print("ERRO: Arquivo config.py não encontrado!")
    print("Por favor, certifique-se de que config.py existe no diretório raiz.")
    sys.exit(1)


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


def extract_audio(video_path, audio_path):
    """Extrai áudio do vídeo em formato WAV."""
    print("\nExtraindo áudio do vídeo...")
    print(f"Formato: WAV {config.AUDIO_CHANNELS}-channel {config.AUDIO_SAMPLE_RATE}Hz")
    
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',
            '-ar', str(config.AUDIO_SAMPLE_RATE),
            '-ac', str(config.AUDIO_CHANNELS),
            '-c:a', 'pcm_s16le',
            '-y',
            audio_path
        ]
        
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"Áudio extraído: {audio_size_mb:.2f} MB")
        return True
        
    except Exception as e:
        print(f"ERRO ao extrair áudio: {str(e)}")
        return False


def get_audio_duration(audio_path):
    """Obtém a duração do áudio em segundos usando ffprobe."""
    try:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"ERRO ao obter duração: {e}")
        return None


def split_audio_chunks(audio_path, chunk_length_seconds=None):
    """Divide o áudio em chunks usando ffmpeg."""
    chunk_length_seconds = chunk_length_seconds or (config.GEMINI_CHUNK_MINUTES * 60)
    print(f"\nDividindo áudio em chunks de {chunk_length_seconds//60} minutos...")
    
    # Obter duração total
    duration = get_audio_duration(audio_path)
    if not duration:
        return []
    
    num_chunks = math.ceil(duration / chunk_length_seconds)
    chunk_files = []
    
    for i in range(num_chunks):
        start_time = i * chunk_length_seconds
        chunk_filename = f"data/temp_chunk_{i}.wav"
        
        command = [
            'ffmpeg',
            '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(chunk_length_seconds),
            '-c', 'copy',
            '-y',
            chunk_filename
        ]
        
        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            chunk_files.append(chunk_filename)
            print(f"  Chunk {i+1}/{num_chunks} criado")
        except Exception as e:
            print(f"  ERRO ao criar chunk {i+1}: {e}")
    
    return chunk_files


def upload_and_process_audio(audio_path):
    """Faz upload do áudio e aguarda processamento."""
    print(f"\nFazendo upload: {audio_path}")
    
    try:
        audio_file = genai.upload_file(path=audio_path)
        
        while audio_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            audio_file = genai.get_file(audio_file.name)
        
        if audio_file.state.name == "FAILED":
            raise ValueError(f"Falha no processamento: {audio_file.state.name}")
        
        print(" OK")
        return audio_file
        
    except Exception as e:
        print(f"\nERRO durante upload: {str(e)}")
        return None


def transcribe_audio_chunk(audio_file, chunk_index, total_chunks):
    """Transcreve um chunk de áudio usando Gemini."""
    print(f"\nTranscrevendo chunk {chunk_index + 1}/{total_chunks}...")
    
    model = genai.GenerativeModel(model_name=config.GEMINI_MODEL)
    
    prompt = f"""Transcreva este áudio em Português Brasileiro.

INSTRUÇÕES:
- Transcreva TODO o conteúdo de áudio
- Use pontuação adequada
- Mantenha termos técnicos em sua forma original
- Corrija apenas erros claros de fala
- {"Este é o chunk " + str(chunk_index + 1) + " de " + str(total_chunks) + ". " if total_chunks > 1 else ""}
Não adicione introdução ou conclusão, apenas a transcrição pura.
"""
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = model.generate_content(
                [audio_file, prompt],
                request_options={"timeout": 600}
            )
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            
            # Se for erro de quota (429), extrair tempo de retry
            if "429" in error_msg or "quota" in error_msg.lower():
                import re
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)', error_msg)
                
                if retry_match and retry_count < max_retries - 1:
                    retry_seconds = int(float(retry_match.group(1))) + 5  # +5s de margem
                    print(f"\n⚠️  Quota excedida. Aguardando {retry_seconds}s antes de tentar novamente...")
                    time.sleep(retry_seconds)
                    retry_count += 1
                    continue
                else:
                    print(f"\n❌ ERRO: Quota da API Gemini esgotada!")
                    print(f"   Limite: 20 requisições/dia (free tier)")
                    print(f"   Aguarde 24h ou use o script Whisper local:")
                    print(f"   python transcribe_whisper_optimized.py")
                    return None
            else:
                print(f"ERRO durante transcrição: {error_msg}")
                if retry_count < max_retries - 1:
                    retry_count += 1
                    print(f"Tentando novamente ({retry_count}/{max_retries})...")
                    time.sleep(5)
                    continue
                return None
    
    return None


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

Arquivo Original: {config.INPUT_VIDEO}
Data de Transcrição: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
Modelo Utilizado: {config.GEMINI_MODEL}
Idioma: Português Brasileiro (pt-BR)

{'='*80}

"""
    
    # Salvar arquivo
    try:
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(header)
            f.write(transcription)
            f.write(f"\n\n{'='*80}\n")
            f.write("FIM DA TRANSCRIÇÃO\n")
            f.write(f"{'='*80}\n")
        
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


def cleanup_files(file_list):
    """Remove arquivos temporários."""
    print("\nLimpando arquivos temporários...")
    for file_path in file_list:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Aviso: Não foi possível remover {file_path}: {e}")


def main():
    """Função principal que executa o processo de transcrição com chunking."""
    print("="*80)
    print(f"TRANSCRIÇÃO DE VÍDEO COM GOOGLE {config.GEMINI_MODEL.upper()}".center(80))
    print("="*80)
    
    # Mostrar configurações
    print(f"\n📋 Configurações:")
    print(f"   Modelo: {config.GEMINI_MODEL}")
    print(f"   Chunk: {config.GEMINI_CHUNK_MINUTES} minutos")
    print(f"   Áudio: {config.AUDIO_SAMPLE_RATE}Hz, {config.AUDIO_CHANNELS} canal(is)")
    
    # Definir caminhos
    temp_audio = r"data\temp_audio_gemini.wav"
    output_file = os.path.join(config.OUTPUT_DIR, config.OUTPUT_BASENAME + ".txt")
    
    # Passo 1: Configurar API
    configure_gemini()
    
    # Passo 2: Verificar vídeo
    check_video_exists(config.INPUT_VIDEO)
    
    # Passo 3: Extrair áudio
    os.makedirs("data", exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    if not extract_audio(config.INPUT_VIDEO, temp_audio):
        sys.exit(1)
    
    # Passo 4: Dividir em chunks
    chunk_files = split_audio_chunks(temp_audio)
    print(f"\nTotal de chunks: {len(chunk_files)}")
    
    # Passo 5: Processar cada chunk
    transcriptions = []
    uploaded_files = []
    
    for i, chunk_file in enumerate(chunk_files):
        # Upload do chunk
        audio_file = upload_and_process_audio(chunk_file)
        if not audio_file:
            print(f"Erro no chunk {i+1}, pulando...")
            continue
        
        uploaded_files.append(audio_file)
        
        # Transcrever chunk
        transcription = transcribe_audio_chunk(audio_file, i, len(chunk_files))
        if transcription:
            transcriptions.append(transcription)
            print(f"Chunk {i+1} concluído ({len(transcription)} caracteres)")
    
    # Passo 6: Combinar transcrições
    if not transcriptions:
        print("\nERRO: Nenhuma transcrição foi gerada!")
        if config.CLEANUP_TEMP_FILES:
            cleanup_files([temp_audio] + chunk_files)
        sys.exit(1)
    
    full_transcription = "\n\n".join(transcriptions)
    
    # Passo 7: Salvar resultado
    save_transcription(full_transcription, output_file)
    
    # Passo 8: Limpeza
    if config.CLEANUP_TEMP_FILES:
        cleanup_files([temp_audio] + chunk_files)
    
    # Remover arquivos do Google AI
    for audio_file in uploaded_files:
        try:
            genai.delete_file(audio_file.name)
        except:
            pass
    
    print("\n" + "="*80)
    print("PROCESSO CONCLUÍDO COM SUCESSO!".center(80))
    print("="*80)
    print(f"\n📁 Arquivo de transcrição: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERRO INESPERADO: {str(e)}")
        sys.exit(1)
