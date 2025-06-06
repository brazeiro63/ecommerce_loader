#!/usr/bin/env python3
import os
import argparse
import sys
from pathlib import Path
import chardet

def check_file(file_path, specific_byte=None, position=None, verbose=False):
    """
    Verifica um arquivo por caracteres inválidos UTF-8.
    
    Args:
        file_path: Caminho para o arquivo
        specific_byte: Byte específico para procurar (ex: 0xe3)
        position: Posição específica para verificar
        verbose: Se True, imprime informações detalhadas
    
    Returns:
        Tupla (tem_erro, detalhes)
    """
    try:
        # Ignora arquivos binários comuns
        if file_path.suffix.lower() in ['.pyc', '.pyd', '.dll', '.exe', '.jpg', '.jpeg', 
                                       '.png', '.gif', '.zip', '.tar', '.gz', '.rar', 
                                       '.7z', '.mp3', '.mp4', '.avi', '.mov', '.pdf']:
            if verbose:
                print(f"Pulando arquivo binário: {file_path}")
            return False, None
        
        # Lê o arquivo como bytes
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Se estamos procurando um byte específico
        if specific_byte is not None:
            byte_val = int(specific_byte, 16) if isinstance(specific_byte, str) else specific_byte
            positions = []
            
            # Se uma posição específica foi fornecida
            if position is not None:
                if len(content) > position and content[position] == byte_val:
                    return True, f"Byte {hex(byte_val)} encontrado na posição {position}"
                return False, None
            
            # Procura o byte em todo o conteúdo
            for i, byte in enumerate(content):
                if byte == byte_val:
                    positions.append(i)
            
            if positions:
                context = []
                for pos in positions:
                    start = max(0, pos - 10)
                    end = min(len(content), pos + 10)
                    
                    # Extrai o contexto ao redor do byte problemático
                    before = content[start:pos]
                    after = content[pos+1:end]
                    
                    # Tenta decodificar o contexto para exibição
                    try:
                        before_str = before.decode('utf-8', errors='replace')
                    except:
                        before_str = ' '.join([hex(b) for b in before])
                    
                    try:
                        after_str = after.decode('utf-8', errors='replace')
                    except:
                        after_str = ' '.join([hex(b) for b in after])
                    
                    context.append(f"Posição {pos}: ...{before_str}[{hex(byte_val)}]{after_str}...")
                
                return True, f"Byte {hex(byte_val)} encontrado nas posições: {positions}\nContexto:\n" + "\n".join(context)
        
        # Tenta decodificar como UTF-8
        try:
            content.decode('utf-8')
            return False, None
        except UnicodeDecodeError as e:
            # Detecta a codificação provável
            detection = chardet.detect(content)
            
            # Obtém informações sobre o erro
            error_msg = str(e)
            
            # Extrai o contexto do erro
            start = max(0, e.start - 10)
            end = min(len(content), e.end + 10)
            
            context_bytes = content[start:end]
            hex_context = ' '.join([hex(b) for b in context_bytes])
            
            # Tenta decodificar o contexto para exibição
            try:
                context_before = content[start:e.start].decode('utf-8', errors='replace')
                context_after = content[e.end:end].decode('utf-8', errors='replace')
                error_byte_hex = ' '.join([hex(b) for b in content[e.start:e.end]])
                
                context = f"...{context_before}[{error_byte_hex}]{context_after}..."
            except:
                context = f"Contexto em hex: {hex_context}"
            
            return True, (
                f"Erro de decodificação UTF-8: {error_msg}\n"
                f"Codificação provável: {detection['encoding']} (confiança: {detection['confidence']:.2f})\n"
                f"Contexto: {context}"
            )
    
    except Exception as e:
        return True, f"Erro ao processar o arquivo: {str(e)}"

def scan_directory(directory, specific_byte=None, position=None, extensions=None, verbose=False):
    """
    Escaneia um diretório recursivamente por arquivos com caracteres inválidos UTF-8.
    
    Args:
        directory: Diretório para escanear
        specific_byte: Byte específico para procurar (ex: 0xe3)
        position: Posição específica para verificar
        extensions: Lista de extensões de arquivo para verificar (None = todas)
        verbose: Se True, imprime informações detalhadas
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Erro: O diretório {directory} não existe.")
        return
    
    print(f"Escaneando {directory} por caracteres inválidos UTF-8...")
    if specific_byte:
        byte_val = int(specific_byte, 16) if isinstance(specific_byte, str) else specific_byte
        print(f"Procurando especificamente pelo byte: {hex(byte_val)}")
    if position is not None:
        print(f"Verificando especificamente a posição: {position}")
    if extensions:
        print(f"Verificando apenas arquivos com extensões: {', '.join(extensions)}")
    
    found_issues = 0
    scanned_files = 0
    
    # Converte extensões para um conjunto para busca mais rápida
    ext_set = set(extensions) if extensions else None
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = Path(root) / file
            
            # Verifica extensão se especificada
            if ext_set and file_path.suffix.lower().lstrip('.') not in ext_set:
                continue
            
            scanned_files += 1
            if verbose:
                print(f"Verificando: {file_path}")
            
            has_issue, details = check_file(file_path, specific_byte, position, verbose)
            
            if has_issue:
                found_issues += 1
                print(f"\n{'='*80}\nPROBLEMA ENCONTRADO em {file_path}:\n{details}\n{'='*80}\n")
    
    print(f"\nEscaneamento concluído. Verificados {scanned_files} arquivos, encontrados {found_issues} com problemas.")

def main():
    parser = argparse.ArgumentParser(description='Verifica arquivos por caracteres inválidos UTF-8')
    parser.add_argument('directory', help='Diretório para escanear')
    parser.add_argument('--byte', '-b', help='Byte específico para procurar (ex: 0xe3)')
    parser.add_argument('--position', '-p', type=int, help='Posição específica para verificar')
    parser.add_argument('--extensions', '-e', nargs='+', help='Extensões de arquivo para verificar (ex: py txt)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso')
    
    args = parser.parse_args()
    
    # Instala chardet se não estiver disponível
    try:
        import chardet
    except ImportError:
        print("Instalando a biblioteca 'chardet' necessária para detecção de codificação...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])
        import chardet
    
    scan_directory(
        args.directory, 
        args.byte, 
        args.position, 
        args.extensions, 
        args.verbose
    )

if __name__ == "__main__":
    main()