# Transcrição de Vídeo - Google Gemini Flash & Whisper Local

Aplicação Python para transcrição profissional e precisa de vídeos MP4 usando Google Gemini Flash ou Whisper Large V3 local.

## Características

- ✅ Suporte a vídeos MP4 de alta qualidade
- ✅ Transcrição em Português Brasileiro (pt-BR)
- ✅ Duas opções: Gemini Flash (nuvem) ou Whisper Large V3 (local)
- ✅ Saída em arquivo de texto formatado
- ✅ Suporte a vídeos longos (até ~1 hora)

## Requisitos

- Python 3.8 ou superior
- Chave da API do Google AI Studio

## Instalação

1. Clone o repositório ou baixe os arquivos

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure a chave da API:
   - Copie o arquivo `.env.example` para `.env`
   - Obtenha sua chave em: https://aistudio.google.com/api-keys
   - Adicione a chave no arquivo `.env`:
   ```
   GOOGLE_API_KEY=sua_chave_aqui
   ```

## Uso

### Opção 1: Whisper Large V3 (Local - Recomendado)

Execute o script de transcrição local:

```bash
python transcribe_whisper_local.py
```

Este método:
- Roda 100% local (sem necessidade de internet após download do modelo)
- Usa Whisper Large V3 (modelo state-of-the-art da OpenAI)
- Primeira execução baixa ~3GB de modelo
- Requer: ~8GB RAM, GPU CUDA opcional (muito mais rápido)

### Opção 2: Google Gemini Flash (Nuvem)

Configure a chave da API e execute:

```bash
python transcribe.py
```

Este método:
- Requer chave da API do Google AI Studio (gratuita)
- Processa na nuvem (mais rápido se tiver boa conexão)
- Sem necessidade de GPU local

O script irá:
1. Processar o vídeo em `data\aula_gestao-da-inovacao-em-ciencia-de-dados_20251122_recording.mp4`
2. Transcrever usando o modelo escolhido
3. Salvar a transcrição em:
   - Whisper Local: `data\transcricao_whisper_local.txt`
   - Gemini Flash: `data\transcricao_aula_gestao-da-inovacao-em-ciencia-de-dados_20251122.txt`

## Parâmetros Configuráveis

### transcribe_whisper_local.py
- `INPUT_VIDEO`: Caminho do vídeo de entrada
- `OUTPUT_FILE`: Caminho do arquivo de saída
- `MODEL_NAME`: Modelo Whisper (padrão: large-v3)

### transcribe.py (Gemini)
- `INPUT_VIDEO`: Caminho do vídeo de entrada
- `OUTPUT_FILE`: Caminho do arquivo de saída
- `MODEL_NAME`: Modelo do Gemini (padrão: gemini-1.5-flash)

## Limitações

- Tamanho máximo de vídeo: ~2GB
- Duração máxima recomendada: ~1 hora
- Formatos suportados: MP4, MOV, AVI, FLV, MPG, MPEG, WMV

## Suporte

Para obter uma chave da API do Google AI Studio:
1. Acesse https://aistudio.google.com/api-keys
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada
