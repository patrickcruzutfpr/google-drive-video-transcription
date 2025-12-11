"""
Arquivo de Configuração - Transcrição de Vídeo

Personalize o comportamento dos scripts de transcrição aqui.
"""

# ============================================================================
# CONFIGURAÇÕES DE ENTRADA/SAÍDA
# ============================================================================

# Caminho do vídeo a ser transcrito
INPUT_VIDEO = r"data\aula_gestao-da-inovacao-em-ciencia-de-dados_20251122_recording.mp4"

# Pasta onde os resultados serão salvos
OUTPUT_DIR = r"results"

# Nome base do arquivo de saída (sem extensão)
OUTPUT_BASENAME = "transcricao_aula_gestao-da-inovacao-em-ciencia-de-dados_20251122-2"


# ============================================================================
# CONFIGURAÇÕES DE MODELO
# ============================================================================

# Whisper: Modelo a usar
# Opções: "tiny", "base", "small", "medium", "large", "large-v2", "large-v3"
# Recomendado: "large-v3" (melhor qualidade, mais lento)
WHISPER_MODEL = "large-v3"

# Gemini: Modelo a usar
# Opções: "gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash"
GEMINI_MODEL = "gemini-2.5-flash"


# ============================================================================
# CONFIGURAÇÕES DE SAÍDA
# ============================================================================

# Modo de saída de timestamps
# Opções:
#   "none"      - Sem timestamps (apenas texto corrido - MAIS RÁPIDO)
#   "segments"  - Timestamps por segmento [HH:MM:SS --> HH:MM:SS]
#   "words"     - Timestamps por palavra (MAIS LENTO)
TIMESTAMP_MODE = "segments"

# Salvar arquivo separado com timestamps detalhados
# Se True, cria um arquivo adicional "*_timestamp.txt" com marcações de tempo
SAVE_TIMESTAMP_FILE = True

# Salvar arquivo separado com marcações de minutos
# Se True, cria um arquivo "*_minutes.txt" com marcadores a cada minuto
SAVE_MINUTES_FILE = True


# ============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ============================================================================

# Mostrar progresso detalhado durante transcrição
# False = Mais rápido (não imprime na tela)
# True = Mostra progresso em tempo real
VERBOSE_OUTPUT = True

# Usar FP16 (half precision) em GPU
# Acelera processamento em GPUs NVIDIA (requer CUDA)
USE_FP16_GPU = True

# Tamanho dos chunks para Gemini (em minutos)
# Vídeos longos são divididos em chunks para evitar limites de API
GEMINI_CHUNK_MINUTES = 10


# ============================================================================
# CONFIGURAÇÕES DE ÁUDIO
# ============================================================================

# Taxa de amostragem para extração de áudio (Hz)
# 16000 é ideal para Whisper
AUDIO_SAMPLE_RATE = 16000

# Canais de áudio
# 1 = Mono (recomendado, mais rápido)
# 2 = Estéreo
AUDIO_CHANNELS = 1


# ============================================================================
# CONFIGURAÇÕES AVANÇADAS
# ============================================================================

# Idioma padrão para transcrição
LANGUAGE = "pt"

# Limpar arquivos temporários após conclusão
CLEANUP_TEMP_FILES = True

# Incluir estatísticas no arquivo final
INCLUDE_STATISTICS = True
