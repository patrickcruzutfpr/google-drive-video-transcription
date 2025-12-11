"""
Transcrição de Vídeo com Whisper Large V3 (Otimizado)

Versão otimizada que extrai o áudio antes da transcrição para melhor desempenho:
- Reduz uso de memória
- Processamento mais rápido
- Menos overhead de decodificação de vídeo

Autor: Aplicação de Transcrição Automatizada
Data: 11 de Dezembro de 2025
"""

import os
import sys
import whisper
import torch
import subprocess
from datetime import datetime
from pathlib import Path

# Configurações
INPUT_VIDEO = r"data\aula_gestao-da-inovacao-em-ciencia-de-dados_20251122_recording.mp4"
OUTPUT_FILE = r"results\transcricao_aula_gestao-da-inovacao-em-ciencia-de-dados_20251122.txt"
TEMP_AUDIO = r"data\temp_audio_extraction.wav"
MODEL_NAME = "large-v3"


def extract_audio(video_path, audio_path):
    """
    Extrai áudio do vídeo para WAV mono 16kHz (formato otimizado para Whisper).
    Isso melhora significativamente o desempenho.
    """
    print("\nExtraindo áudio do vídeo...")
    print("Formato: WAV mono 16kHz (otimizado para Whisper)")
    
    try:
        # Usar ffmpeg para extrair áudio em formato otimizado
        # -vn: sem vídeo
        # -ar 16000: 16kHz sample rate (ideal para Whisper)
        # -ac 1: mono (reduz processamento)
        # -c:a pcm_s16le: PCM 16-bit (sem compressão)
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # Sem vídeo
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-c:a', 'pcm_s16le',  # PCM 16-bit
            '-y',  # Sobrescrever se existir
            audio_path
        ]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # Verificar tamanho do arquivo extraído
        audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"Áudio extraído com sucesso: {audio_size_mb:.2f} MB")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao extrair áudio: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("ERRO: ffmpeg não encontrado. Por favor, instale o ffmpeg.")
        print("Windows: winget install --id=Gyan.FFmpeg")
        return False


def main():
    """Função principal que executa o processo de transcrição otimizado."""
    print("="*80)
    print("TRANSCRIÇÃO DE VÍDEO COM WHISPER LARGE V3 (OTIMIZADO)".center(80))
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
    
    # Criar diretório de saída se não existir
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(TEMP_AUDIO), exist_ok=True)
    
    # Passo 1: Extrair áudio
    if not extract_audio(INPUT_VIDEO, TEMP_AUDIO):
        sys.exit(1)
    
    # Passo 2: Carregar modelo com GPU se disponível
    print(f"\nCarregando modelo Whisper {MODEL_NAME}...")
    print("(Primeira execução: pode baixar ~3GB de modelo)")
    
    # Detectar dispositivo (GPU/CPU)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        print(f"🚀 GPU detectada: {torch.cuda.get_device_name(0)}")
        print(f"💾 VRAM disponível: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠️  GPU não detectada. Usando CPU (mais lento)")
    
    model = whisper.load_model(MODEL_NAME, device=device)
    print("Modelo carregado com sucesso!")
    
    # Passo 3: Transcrever
    print("\nIniciando transcrição...")
    print(f"Dispositivo: {device.upper()}")
    print("Processando áudio otimizado (mais rápido que vídeo direto)...")
    
    try:
        result = model.transcribe(
            TEMP_AUDIO,
            language="pt",
            verbose=True,
            fp16=(device == "cuda"),  # Usar FP16 apenas com GPU
            word_timestamps=False  # Desabilitar para melhor velocidade
        )
        
        print("\nTranscrição concluída!")
        
    except Exception as e:
        print(f"\nERRO durante transcrição: {e}")
        # Limpar arquivo temporário
        if os.path.exists(TEMP_AUDIO):
            os.remove(TEMP_AUDIO)
        sys.exit(1)
    
    # Passo 4: Salvar resultado
    header = f"""{'='*80}
TRANSCRIÇÃO DE VÍDEO - GESTÃO DA INOVAÇÃO EM CIÊNCIA DE DADOS
{'='*80}

Arquivo Original: {INPUT_VIDEO}
Data de Transcrição: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
Modelo Utilizado: Whisper {MODEL_NAME}
Dispositivo: {device.upper()} ({torch.cuda.get_device_name(0) if device == "cuda" else "CPU"})
Método: Extração de áudio otimizada (WAV 16kHz mono)
Idioma: Português Brasileiro (pt-BR)

{'='*80}

"""
    
    print(f"\nSalvando transcrição em: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8-sig') as f:
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
    
    # Passo 5: Limpar arquivo temporário
    print("\nLimpando arquivos temporários...")
    if os.path.exists(TEMP_AUDIO):
        os.remove(TEMP_AUDIO)
        print("Arquivo de áudio temporário removido.")
    
    print("\n" + "="*80)
    print("PROCESSO CONCLUÍDO COM SUCESSO!".center(80))
    print("="*80)
    print(f"\nArquivo de transcrição: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
        # Limpar arquivo temporário se existir
        if os.path.exists(TEMP_AUDIO):
            os.remove(TEMP_AUDIO)
        sys.exit(0)
    except Exception as e:
        print(f"\nERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        # Limpar arquivo temporário se existir
        if os.path.exists(TEMP_AUDIO):
            os.remove(TEMP_AUDIO)
        sys.exit(1)
