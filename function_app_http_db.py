import logging
import paramiko
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="execute_ssh")
def execute_ssh(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Parâmetros de conexão SSH
    hostname = "20.41.112.32"
    port = 22
    username = "andre"
    password = "DeltaAlfa@2208"  # Para segurança, considere usar variáveis de ambiente ou Azure Key Vault

    # Comando a ser executado na máquina Linux
    command = 'sqlite3 /home/andre/sql/mydatabase.db "UPDATE users SET name = \'andre\' WHERE name = \'Alice\'"'
    
    try:
        logging.info(f"Tentando conectar ao servidor SSH {hostname}:{port} com o usuário {username}")

        # Conexão SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password)
        
        logging.info("Conexão SSH estabelecida com sucesso")
        
        # Executar o comando
        stdin, stdout, stderr = client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()  # Aguarda a conclusão do comando
        
        logging.info(f"Comando executado com status de saída {exit_status}")
        
        # Fechar a conexão
        client.close()
        logging.info("Conexão SSH fechada")

        if exit_status == 0:
            return func.HttpResponse("Atualização realizada com sucesso no banco de dados SQLite.", status_code=200)
        else:
            error_message = stderr.read().decode('utf-8')
            logging.error(f"Erro ao executar o comando: {error_message}")
            return func.HttpResponse(f"Erro ao executar o comando: {error_message}", status_code=500)

    except paramiko.AuthenticationException:
        logging.error("Falha na autenticação ao tentar conectar via SSH")
        return func.HttpResponse("Falha na autenticação ao tentar conectar via SSH", status_code=500)
    except paramiko.SSHException as sshException:
        logging.error(f"Erro SSH: {sshException}")
        return func.HttpResponse(f"Erro SSH: {sshException}", status_code=500)
    except Exception as e:
        logging.error(f"Erro ao tentar conectar via SSH: {str(e)}")
        return func.HttpResponse(f"Erro ao tentar conectar via SSH: {str(e)}", status_code=500)
