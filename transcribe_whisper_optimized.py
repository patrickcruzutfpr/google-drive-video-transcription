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

# Importar configurações
try:
    import config
except ImportError:
    print("ERRO: Arquivo config.py não encontrado!")
    print("Por favor, certifique-se de que config.py existe no diretório raiz.")
    sys.exit(1)


def extract_audio(video_path, audio_path, sample_rate=None, channels=None):
    """
    Extrai áudio do vídeo para WAV mono 16kHz (formato otimizado para Whisper).
    Isso melhora significativamente o desempenho.
    """
    sample_rate = sample_rate or config.AUDIO_SAMPLE_RATE
    channels = channels or config.AUDIO_CHANNELS
    
    print("\nExtraindo áudio do vídeo...")
    print(f"Formato: WAV {channels}-channel {sample_rate}Hz (otimizado para Whisper)")
    
    try:
        # Usar ffmpeg para extrair áudio em formato otimizado
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # Sem vídeo
            '-ar', str(sample_rate),  # Sample rate
            '-ac', str(channels),  # Canais
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


def format_timestamp(seconds):
    """Converte segundos para formato HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def save_with_timestamps(result, output_file):
    """Salva transcrição com timestamps de segmentos."""
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        for segment in result["segments"]:
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"[{start} --> {end}]  {text}\n")


def save_with_minutes(result, output_file):
    """Salva transcrição com marcadores de minuto."""
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        current_minute = 0
        f.write(f"[{current_minute:02d}:00] ")
        
        for segment in result["segments"]:
            segment_minute = int(segment["start"] // 60)
            
            # Se mudou de minuto, adicionar marcador
            while segment_minute > current_minute:
                current_minute += 1
                f.write(f"\n\n[{current_minute:02d}:00] ")
            
            f.write(segment["text"].strip() + " ")


def save_transcription(result, base_path, device):
    """Salva transcrição em diferentes formatos baseado na configuração."""
    
    # Criar diretórios se necessário
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    
    # Cabeçalho comum
    header = f"""{'='*80}
TRANSCRIÇÃO DE VÍDEO - GESTÃO DA INOVAÇÃO EM CIÊNCIA DE DADOS
{'='*80}

Arquivo Original: {config.INPUT_VIDEO}
Data de Transcrição: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
Modelo Utilizado: Whisper {config.WHISPER_MODEL}
Dispositivo: {device.upper()} ({torch.cuda.get_device_name(0) if device == "cuda" else "CPU"})
Método: Extração de áudio otimizada (WAV {config.AUDIO_SAMPLE_RATE}Hz)
Idioma: Português Brasileiro (pt-BR)
Modo Timestamp: {config.TIMESTAMP_MODE}

{'='*80}

"""
    
    # Arquivo principal (texto limpo)
    main_file = f"{base_path}.txt"
    print(f"\nSalvando transcrição principal: {main_file}")
    with open(main_file, 'w', encoding='utf-8-sig') as f:
        f.write(header)
        f.write(result["text"])
        f.write(f"\n\n{'='*80}\n")
        f.write("FIM DA TRANSCRIÇÃO\n")
        f.write(f"{'='*80}\n")
    
    # Arquivo com timestamps (se habilitado)
    if config.SAVE_TIMESTAMP_FILE and config.TIMESTAMP_MODE != "none":
        timestamp_file = f"{base_path}_timestamp.txt"
        print(f"Salvando versão com timestamps: {timestamp_file}")
        with open(timestamp_file, 'w', encoding='utf-8-sig') as f:
            f.write(header)
            save_with_timestamps(result, timestamp_file.replace(base_path + "_timestamp.txt", "temp_ts.txt"))
        # Reescrever com header
        with open("temp_ts.txt", 'r', encoding='utf-8-sig') as temp:
            content = temp.read()
        with open(timestamp_file, 'w', encoding='utf-8-sig') as f:
            f.write(header)
            f.write(content)
        os.remove("temp_ts.txt")
    
    # Arquivo com marcadores de minutos (se habilitado)
    if config.SAVE_MINUTES_FILE:
        minutes_file = f"{base_path}_minutes.txt"
        print(f"Salvando versão com marcadores de minutos: {minutes_file}")
        with open("temp_min.txt", 'w', encoding='utf-8-sig') as temp:
            save_with_minutes(result, "temp_min.txt")
        with open("temp_min.txt", 'r', encoding='utf-8-sig') as temp:
            content = temp.read()
        with open(minutes_file, 'w', encoding='utf-8-sig') as f:
            f.write(header)
            f.write(content)
            f.write(f"\n\n{'='*80}\n")
            f.write("FIM DA TRANSCRIÇÃO\n")
            f.write(f"{'='*80}\n")
        os.remove("temp_min.txt")
    
    return main_file


def main():
    """Função principal que executa o processo de transcrição otimizado."""
    print("="*80)
    print("TRANSCRIÇÃO DE VÍDEO COM WHISPER LARGE V3 (OTIMIZADO)".center(80))
    print("="*80)
    
    # Mostrar configurações
    print(f"\n📋 Configurações:")
    print(f"   Modelo: {config.WHISPER_MODEL}")
    print(f"   Timestamps: {config.TIMESTAMP_MODE}")
    print(f"   Verbose: {'Sim' if config.VERBOSE_OUTPUT else 'Não (mais rápido)'}")
    print(f"   Arquivo timestamps: {'Sim' if config.SAVE_TIMESTAMP_FILE else 'Não'}")
    print(f"   Arquivo minutos: {'Sim' if config.SAVE_MINUTES_FILE else 'Não'}")
    
    # Verificar se o arquivo existe
    if not os.path.exists(config.INPUT_VIDEO):
        print(f"ERRO: Arquivo de vídeo não encontrado: {config.INPUT_VIDEO}")
        print(f"\nCaminho esperado: {os.path.abspath(config.INPUT_VIDEO)}")
        sys.exit(1)
    
    # Exibir informações do arquivo
    file_size_mb = os.path.getsize(config.INPUT_VIDEO) / (1024 * 1024)
    print(f"\nVídeo encontrado: {config.INPUT_VIDEO}")
    print(f"Tamanho do arquivo: {file_size_mb:.2f} MB")
    
    # Definir caminhos
    temp_audio = r"data\temp_audio_extraction.wav"
    output_base = os.path.join(config.OUTPUT_DIR, config.OUTPUT_BASENAME)
    
    # Criar diretórios
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Passo 1: Extrair áudio
    if not extract_audio(config.INPUT_VIDEO, temp_audio):
        sys.exit(1)
    
    # Passo 2: Carregar modelo com GPU se disponível
    print(f"\nCarregando modelo Whisper {config.WHISPER_MODEL}...")
    print("(Primeira execução: pode baixar ~3GB de modelo)")
    
    # Detectar dispositivo (GPU/CPU)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        print(f"🚀 GPU detectada: {torch.cuda.get_device_name(0)}")
        print(f"💾 VRAM disponível: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠️  GPU não detectada. Usando CPU (mais lento)")
    
    model = whisper.load_model(config.WHISPER_MODEL, device=device)
    print("Modelo carregado com sucesso!")
    
    # Passo 3: Transcrever
    print("\nIniciando transcrição...")
    print(f"Dispositivo: {device.upper()}")
    if not config.VERBOSE_OUTPUT:
        print("⚡ Modo silencioso ativado (mais rápido)")
    
    try:
        # Configurar word_timestamps baseado no modo
        word_timestamps = (config.TIMESTAMP_MODE == "words")
        
        result = model.transcribe(
            temp_audio,
            language=config.LANGUAGE,
            verbose=config.VERBOSE_OUTPUT,
            fp16=(device == "cuda" and config.USE_FP16_GPU),
            word_timestamps=word_timestamps
        )
        
        print("\n✅ Transcrição concluída!")
        
    except Exception as e:
        print(f"\nERRO durante transcrição: {e}")
        if config.CLEANUP_TEMP_FILES and os.path.exists(temp_audio):
            os.remove(temp_audio)
        sys.exit(1)
    
    # Passo 4: Salvar resultados
    main_file = save_transcription(result, output_base, device)
    
    # Exibir estatísticas
    if config.INCLUDE_STATISTICS:
        word_count = len(result["text"].split())
        char_count = len(result["text"])
        print(f"\n📊 Estatísticas da transcrição:")
        print(f"   - Palavras: {word_count:,}")
        print(f"   - Caracteres: {char_count:,}")
        print(f"   - Tamanho arquivo principal: {os.path.getsize(main_file) / 1024:.2f} KB")
    
    # Passo 5: Limpar arquivo temporário
    if config.CLEANUP_TEMP_FILES:
        print("\n🧹 Limpando arquivos temporários...")
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            print("Arquivo de áudio temporário removido.")
    
    print("\n" + "="*80)
    print("PROCESSO CONCLUÍDO COM SUCESSO!".center(80))
    print("="*80)
    print(f"\n📁 Arquivo principal: {os.path.abspath(main_file)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário.")
        temp_audio = r"data\temp_audio_extraction.wav"
        if config.CLEANUP_TEMP_FILES and os.path.exists(temp_audio):
            os.remove(temp_audio)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        temp_audio = r"data\temp_audio_extraction.wav"
        if config.CLEANUP_TEMP_FILES and os.path.exists(temp_audio):
            os.remove(temp_audio)
        sys.exit(1)
        sys.exit(1)
