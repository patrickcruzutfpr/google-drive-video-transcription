"""
Script de diagnóstico e configuração GPU/CUDA para Whisper

Verifica se GPU está disponível e fornece instruções de instalação.
"""

import subprocess
import sys

def check_nvidia_gpu():
    """Verifica se há GPU NVIDIA no sistema."""
    try:
        result = subprocess.run(
            ['nvidia-smi'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("✅ GPU NVIDIA detectada:")
        print(result.stdout)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GPU NVIDIA não detectada ou nvidia-smi não instalado")
        return False

def check_cuda_pytorch():
    """Verifica se PyTorch tem suporte CUDA."""
    try:
        import torch
        print(f"\n📦 PyTorch versão: {torch.__version__}")
        print(f"🔧 CUDA disponível: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            print(f"🔢 CUDA version: {torch.version.cuda}")
            return True
        else:
            print("⚠️  PyTorch instalado SEM suporte CUDA (CPU-only)")
            return False
    except ImportError:
        print("❌ PyTorch não instalado")
        return False

def print_installation_guide():
    """Imprime guia de instalação PyTorch com CUDA."""
    print("\n" + "="*80)
    print("COMO INSTALAR PYTORCH COM SUPORTE CUDA/GPU")
    print("="*80)
    
    print("\n1️⃣  VERIFICAR VERSÃO CUDA DO SISTEMA:")
    print("   Execute: nvidia-smi")
    print("   Veja a versão CUDA no topo (ex: CUDA Version: 12.1)")
    
    print("\n2️⃣  DESINSTALAR PYTORCH ATUAL (CPU-only):")
    print("   pip uninstall torch torchvision torchaudio")
    
    print("\n3️⃣  INSTALAR PYTORCH COM CUDA:")
    print("   Visite: https://pytorch.org/get-started/locally/")
    print("\n   Para CUDA 11.8:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    print("\n   Para CUDA 12.1:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    
    print("\n4️⃣  VERIFICAR INSTALAÇÃO:")
    print("   python -c \"import torch; print(torch.cuda.is_available())\"")
    print("   (Deve retornar: True)")
    
    print("\n5️⃣  REINSTALAR WHISPER (opcional):")
    print("   pip install --upgrade --force-reinstall openai-whisper")
    
    print("\n" + "="*80)
    print("BENEFÍCIOS GPU:")
    print("="*80)
    print("⚡ Velocidade: 10-50x mais rápido que CPU")
    print("🎯 Precisão: Mesma qualidade, processamento mais eficiente")
    print("⏱️  Tempo estimado: 63 min de áudio em ~5-10 min (vs 30-60 min em CPU)")
    print("="*80 + "\n")

def main():
    print("="*80)
    print("DIAGNÓSTICO GPU/CUDA PARA WHISPER")
    print("="*80 + "\n")
    
    has_nvidia = check_nvidia_gpu()
    has_cuda = check_cuda_pytorch()
    
    if has_nvidia and not has_cuda:
        print("\n⚠️  ATENÇÃO:")
        print("Você tem GPU NVIDIA, mas PyTorch está em modo CPU-only!")
        print_installation_guide()
    elif has_nvidia and has_cuda:
        print("\n✅ SISTEMA CONFIGURADO CORRETAMENTE!")
        print("GPU/CUDA está pronta para uso com Whisper.")
    elif not has_nvidia:
        print("\n💡 INFO:")
        print("Nenhuma GPU NVIDIA detectada. Whisper rodará em CPU (mais lento).")
        print("Para melhor performance, use uma máquina com GPU NVIDIA.")
    
    print("\n🔍 PARA USAR GPU NO WHISPER:")
    print("Adicione device='cuda' ao carregar o modelo:")
    print("model = whisper.load_model('large-v3', device='cuda')")

if __name__ == "__main__":
    main()
