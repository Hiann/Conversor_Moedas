#!/usr/bin/env python3
"""
Ponto de entrada principal do Conversor de Moedas Pro.

Uso:
    python main.py                    # Modo interativo CLI
    python main.py --gui              # Interface gráfica
    python main.py --help             # Ajuda
"""

import sys
import argparse


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Conversor de Moedas Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    python main.py --gui              # Inicia interface gráfica
    python main.py cli                # Modo CLI interativo
    python main.py cli convert 100 USD BRL
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Inicia interface gráfica'
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['cli', 'gui'],
        help='Comando a executar'
    )
    
    args, unknown = parser.parse_known_args()
    
    # Determina modo
    if args.gui or args.command == 'gui':
        # GUI
        from src.gui import main as gui_main
        gui_main()
    else:
        # CLI
        from src.cli import cli
        
        # Se há argumentos adicionais, passa para o CLI
        if unknown:
            sys.argv = [sys.argv[0]] + unknown
        
        cli()


if __name__ == '__main__':
    main()
