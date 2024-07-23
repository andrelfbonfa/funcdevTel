import logging
import paramiko
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def http_trigger1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return func.HttpResponse("HTTP trigger executed.", status_code=200)

def execute_ssh_command():
    # Parâmetros de conexão SSH
    hostname = "20.41.112.32"
    port = 22
    username = "andre"
    password = "DeltaAlfa@2208"  # Para segurança, considere usar variáveis de ambiente ou Azure Key Vault

    # Comando a ser executado na máquina Linux
    command = 'sqlite3 /home/andre/sql/mydatabase.db "UPDATE users SET name = \'Alice\' WHERE name = \'andre\'"'
    
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

    except paramiko.AuthenticationException:
        logging.error("Falha na autenticação ao tentar conectar via SSH")
    except paramiko.SSHException as sshException:
        logging.error(f"Erro SSH: {sshException}")
    except Exception as e:
        logging.error(f"Erro ao tentar conectar via SSH: {str(e)}")

@app.timer_trigger(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False) 
def functrigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    
    logging.info('Python timer trigger function executed.')
    execute_ssh_command()