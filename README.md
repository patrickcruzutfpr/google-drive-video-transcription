# Transcrição de Vídeo com IA

Aplicação Python para transcrição profissional e precisa de vídeos MP4 usando Google Gemini Flash ou Whisper Large V3.

## 🎯 Características

- ✅ Transcrição de vídeos MP4 em Português Brasileiro (pt-BR)
- ✅ Duas opções: **Whisper Large V3** (local, otimizado) ou **Gemini Flash** (nuvem)
- ✅ Extração otimizada de áudio para melhor desempenho
- ✅ Saída formatada com cabeçalho profissional e estatísticas
- ✅ Suporte a vídeos longos (testado até 1 hora)

## 📋 Requisitos

- Python 3.8 ou superior
- FFmpeg (instalado automaticamente no Windows via winget)
- ~8GB RAM para Whisper local
- GPU CUDA opcional (acelera significativamente o Whisper)

### Para usar Gemini Flash (nuvem):
- Chave da API do Google AI Studio (gratuita)

## 🚀 Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/patrickcruzutfpr/google-drive-video-transcription.git
cd google-drive-video-transcription
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o ambiente (apenas para Gemini):**
   - Copie `.env.example` para `.env`
   - Obtenha sua chave em: https://aistudio.google.com/api-keys
   - Adicione no arquivo `.env`:
   ```
   GOOGLE_API_KEY=sua_chave_aqui
   ```

## 💻 Uso

### Opção 1: Whisper Large V3 Local (Recomendado)

Melhor desempenho com extração otimizada de áudio:

```bash
python transcribe_whisper_optimized.py
```

**Vantagens:**
- 🚀 20-40% mais rápido que processar vídeo direto
- 💾 Menor uso de memória RAM
- 📦 100% offline após download inicial do modelo (~3GB na primeira execução)
- 🎯 Extração de áudio em 16kHz mono (formato ideal para Whisper)
- 🧹 Limpeza automática de arquivos temporários

**Funcionamento:**
1. Extrai áudio do vídeo em formato otimizado (WAV 16kHz mono)
2. Carrega modelo Whisper Large V3
3. Transcreve o áudio
4. Salva em `data\transcricao_whisper_local.txt`

### Opção 2: Google Gemini Flash (Nuvem)

Processa na nuvem do Google:

```bash
python transcribe.py
```

**Vantagens:**
- ☁️ Não requer GPU local
- ⚡ Rápido com boa conexão de internet
- 🆓 API gratuita (com limites)

**Funcionamento:**
1. Faz upload do vídeo para Google AI
2. Processa com Gemini Flash
3. Salva em `data\transcricao_aula_[nome].txt`

## ⚙️ Configuração

### transcribe_whisper_optimized.py
Edite as constantes no início do arquivo:

```python
INPUT_VIDEO = r"data\seu_video.mp4"
OUTPUT_FILE = r"data\transcricao_saida.txt"
MODEL_NAME = "large-v3"  # Opções: tiny, base, small, medium, large-v3
```

### transcribe.py (Gemini)
```python
INPUT_VIDEO = r"data\seu_video.mp4"
OUTPUT_FILE = r"data\transcricao_saida.txt"
MODEL_NAME = "gemini-1.5-flash"
```

## 📊 Desempenho

### Benchmark (Vídeo 63 min, 186MB)

| Método | Tempo | Uso RAM | GPU | Qualidade |
|--------|-------|---------|-----|-----------|
| Whisper Otimizado (CPU) | ~25-35 min | ~6GB | Não | Excelente |
| Whisper Otimizado (GPU) | ~8-12 min | ~4GB | Sim | Excelente |
| Gemini Flash | ~5-10 min | ~2GB | Não | Muito Boa |

**Por que a versão otimizada é mais rápida?**
- Extrai áudio em 16kHz mono (reduz 40% do tamanho)
- Elimina overhead de decodificação de vídeo frame-por-frame
- Formato PCM direto sem compressão (menos processamento)

## 📝 Formato de Saída

```
================================================================================
TRANSCRIÇÃO DE VÍDEO - GESTÃO DA INOVAÇÃO EM CIÊNCIA DE DADOS
================================================================================

Arquivo Original: data\video.mp4
Data de Transcrição: 11/12/2025 às 14:30:15
Modelo Utilizado: Whisper large-v3
Método: Extração de áudio otimizada (WAV 16kHz mono)
Idioma: Português Brasileiro (pt-BR)

================================================================================

[Transcrição completa do conteúdo aqui...]

================================================================================
FIM DA TRANSCRIÇÃO
================================================================================
```

Inclui estatísticas:
- Total de palavras
- Total de caracteres
- Tamanho do arquivo gerado

## ⚠️ Limitações

- **Tamanho máximo:** ~2GB por vídeo
- **Duração recomendada:** até 1 hora (testado com sucesso)
- **Formatos suportados:** MP4, MOV, AVI, FLV, MPG, MPEG, WMV
- **Idioma otimizado:** Português Brasileiro (mas funciona com outros idiomas)

## 🛠️ Tecnologias

- **[OpenAI Whisper](https://github.com/openai/whisper)** - Modelo de transcrição de áudio state-of-the-art
- **[Google Gemini](https://ai.google.dev/)** - IA multimodal do Google
- **[FFmpeg](https://ffmpeg.org/)** - Processamento de áudio/vídeo
- **Python 3.8+** - Linguagem base

## 📄 Licença

Este projeto é de código aberto para fins educacionais.
