import os
import shutil
import time
import getpass
from datetime import datetime

# --- CONFIGURAÇÕES ---
caminho_base = os.path.expanduser("~")
pasta_monitorada = os.path.join(caminho_base, "Downloads")
arquivo_log = os.path.join(pasta_monitorada, "registro_seguranca.log")

pastas_destino = {
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
    "Documentos": [".doc", ".docx", ".txt", ".odt", ".rtf"],
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".heic", ".pnj"],
    "Musicas": [".mp3", ".wav", ".flac"],
    "PDFs": [".pdf"],
    "Planilhas": [".xlsx", ".xls", ".csv", ".ods"],
    "Zips": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programas": [".exe", ".msi", ".deb", ".sh", ".AppImage"],
}

def registrar_log(mensagem):
    usuario = getpass.getuser()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    texto_log = f"[{data_hora}] {usuario}: {mensagem}\n"
    try:
        with open(arquivo_log, "a", encoding="utf-8") as log:
            log.write(texto_log)
    except Exception as e:
        print(f"Erro ao gravar log: {e}")

def mover_com_seguranca(arquivo_origem, pasta_destino):
    nome_arquivo = os.path.basename(arquivo_origem)
    caminho_final = os.path.join(pasta_destino, nome_arquivo)

    contador = 1
    nome_base, extensao = os.path.splitext(nome_arquivo)
    while os.path.exists(caminho_final):
        novo_nome = f"{nome_base}_{contador}{extensao}"
        caminho_final = os.path.join(pasta_destino, novo_nome)
        contador += 1

    shutil.move(arquivo_origem, caminho_final)
    return os.path.basename(caminho_final)

# --- LOOP PRINCIPAL ---
print(f"--- MONITORAMENTO INICIADO EM: {pasta_monitorada} ---")
print(f"Log de segurança sendo salvo em: {arquivo_log}")
print("Pressione CTRL+C para parar.")

while True:
    try:
        if os.path.exists(pasta_monitorada):
            arquivos = os.listdir(pasta_monitorada)

            for arquivo in arquivos:
                # Ignora arquivos temporários e ocultos
                if arquivo.startswith(".") or arquivo.endswith((".tmp", ".crdownload", ".part", ".ini", ".py", ".log", ".download")):
                    continue
                
                origem = os.path.join(pasta_monitorada, arquivo)
                
                if os.path.isfile(origem):
                    
                    try:
                        tempo_agora = time.time()
                        ultimo_acesso = os.path.getmtime(origem)
                        
                        # Se o arquivo foi modificado nos últimos 10 segundos, PULA ELE.
                        # Isso garante que o download terminou de verdade.
                        if (tempo_agora - ultimo_acesso) < 10:
                            continue 
                    except FileNotFoundError:
                        continue # Arquivo sumiu ou foi movido antes da verificação
                    # ===============================================

                    extensao = os.path.splitext(arquivo)[1].lower()
                    destino_encontrado = None

                    for pasta, extensoes in pastas_destino.items():
                        if extensao in extensoes:
                            destino_encontrado = pasta
                            break
                    
                    if not destino_encontrado:
                        #  mover tudo que não conhece para Outros
                        # destino_encontrado = "Outros"
                        continue # Se não conhece a extensão, ignora por segurança

                    caminho_destino = os.path.join(pasta_monitorada, destino_encontrado)
                    if not os.path.exists(caminho_destino):
                        os.makedirs(caminho_destino)

                    try:
                        nome_final = mover_com_seguranca(origem, caminho_destino)
                        registrar_log(f"MOVIDO: '{arquivo}' -> '{destino_encontrado}/{nome_final}'")
                        print(f"[OK] {arquivo} movido para {destino_encontrado}")
                    except Exception as e:
                        print(f"[ERRO] Falha ao mover '{arquivo}': {e}")

        time.sleep(2) 

    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")
        break
    except Exception as erro:
        registrar_log(f"ERRO CRÍTICO NO SCRIPT: {erro}")
        print(f"Erro crítico: {erro}")
        time.sleep(5)
