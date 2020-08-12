import os.path
import os
import shutil
import subprocess
import time

###########

jenkins_grupo = open('tmp/grupo.txt')
jenkins_jobs = 'tmp/jobs7.txt'
jenkins_jobs_envio = 'tmp/jobs_envio.txt'
jenkins_user = 'tmp/user.txt'
jenkins_url = 'http://10.26.29.2:8081/'


#Converter arquivo da variavel jenkins_grupo em uma lista python
converte_grupo = [converte_grupo.strip() for converte_grupo in jenkins_grupo]
jenkins_grupo.close()
lista_jenkins_grupo = sorted(set(converte_grupo))

# 5-  Coleta os jobs dos  Grupos listados na variavel L_GRUPO e envia  o nome de todos os jos para o  arquivo definido na variavel L_JOBS. Utiliza o grep para coletar apenas os nomes
#GRUPO = 'bora-2''
# VERIFICAR A confuguração de lista no python ou dicionario
for GRUPO in lista_jenkins_grupo :
    GRUPO = GRUPO.rstrip()
    print("listando o grupo {}"  .format(GRUPO))
    os.system("java -jar jenkins-cli.jar -s {} -auth admin:admin get-view {}  |grep string  |cut -d '>' -f 2 |cut  -d '<' -f 1  >> {} "   .format(jenkins_url, GRUPO, jenkins_jobs))
    #os.system("java -jar jenkins-cli.jar -s http://10.26.29.2:8081/ -uth admin:admin get-view {}  |grep string  |cut -d '>' -f 2 |cut  -d '<' -f 1 >> tmp/jobs.txt"   .format(GRUPO))

#6 -
#Converter arquivo da variavel 'lista_jobs' em uma lista python
converte_jobs = [converte_jobs.strip() for converte_jobs in open(jenkins_jobs)]
#jenkins_jobs.close()
lista_jenkins_jobs = sorted(set(converte_jobs))
#Criado essa variavel final 'envio' para quardar em listas os nomes de todos os jobs para envio
lista_jenkins_jobs_envio = sorted(set(converte_jobs))



# 7 - Lê a lista convertida dos jobs, e baixa cada JOB jogando para um arquivo .xml correspondente ao nome
for JOBS in lista_jenkins_jobs:
    JOBS = JOBS.rstrip()
    os.system("java -jar jenkins-cli.jar -s {} -auth admin:admin get-job {} > tmp/{}.xml" .format(jenkins_url, JOBS, JOBS))


#Converter arquivo contendo os nomes em uma lista  python
converte_user = [converte_user.strip() for converte_user in open(jenkins_user)]
#jenkins_jobs.close()
lista_jenkins_user = sorted(set(converte_user))

#print(lista_jenkins_user)

#8 - Realizar o bkp do arquivo de jobs, pois será retirado mais abaixo tudo que for *prd
os.system("cp {} {}" .format(jenkins_jobs, jenkins_jobs_envio))

####
# 9- verificar se o usuario existe nos arquivos dos jobs *.xml, se não ele insere nos arquivos.
print(lista_jenkins_jobs)

for USUARIO in lista_jenkins_user:
    for JOBS_USER in lista_jenkins_jobs[:]:

        valida_nome_prd=JOBS_USER.endswith('-prd')
        check_job_user=os.system("cat tmp/{}.xml |grep {} > /dev/null" .format(JOBS_USER, USUARIO))
#Verifica se o usuário tem nos arquivos .XML
        if check_job_user == 0 :
            print(USUARIO + " Ja existe no job " + JOBS_USER + " PLANO - A")

#Insere os usuarios com permissões mais restritivas nos JOBs de PRD .
        elif  valida_nome_prd == 1 :
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>com.cloudbees.plugins.credentials.CredentialsProvider.View:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>hudson.model.Item.Read:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>hudson.model.Item.Workspace:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            print("Adicionado o Usuário  " + USUARIO + " no  JOB de PRODUÇÂO " + JOBS_USER)
            #lista_jenkins_jobs.remove(JOBS_USER)

# Insere os usuarios com as permissões mais branda nos JOBS QA HML e DEV
        else:
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>com.cloudbees.plugins.credentials.CredentialsProvider.View:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>hudson.model.Item.Read:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>hudson.model.Item.Workspace:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>hudson.model.Item.Build:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            os.system("sed -i '/\/hudson.security.AuthorizationMatrixProperty/i <permission>hudson.model.Item.Cancel:{}</permission>' tmp/{}.xml" .format (USUARIO, JOBS_USER))
            #print(USUARIO + " -> Não  existe no JOB " + JOBS_USER + " PLANO - B")


# Realiza o UPLOAD dos  arquivos *.xml para o Jenkins
for JOBS_USER in lista_jenkins_jobs:
    print("realizando o UpLoad para o Jenkins do Projeto " + JOBS_USER)
    os.system("java -jar jenkins-cli.jar -s {} -auth admin:admin update-job  {}  < tmp/{}.xml" .format(jenkins_url, JOBS_USER, JOBS_USER ))

#Apagar  os arquivos XML gerados
os.system("rm -r tmp/*xml")
