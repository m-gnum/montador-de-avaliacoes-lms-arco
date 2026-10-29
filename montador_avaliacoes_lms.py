import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

def qmagico(string_tags, url_avl):

    # Initialize the Chrome WebDriver with ChromeOptions
    service = Service()  # o Selenium Manager baixa o driver compatível com o Chrome instalado
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized') 
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open a webpage
    driver.get(url_avl) 
    wait = WebDriverWait(driver, 10)

    print("Navegador iniciado, aguarde o script finalizar a execução")

    fazerLogin(driver, wait, login_acesso, senha_acesso)

# ----- CLICANDO EM INICAR PROVA + INSERINDO NOME

    time.sleep(1)
    clicar_criar_prova = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Criar prova')]")))
    driver.execute_script("arguments[0].click();", clicar_criar_prova)

    driver.find_element(By.XPATH, "//input[@name='name']").send_keys({nome_da_prova})
    clicar_proximo = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Próximo')]")))
    driver.execute_script("arguments[0].click();", clicar_proximo)

# --- INPUT DAS STRINGS, FILTRAGEM DAS TAGS E SELEÇÃO DAS QUESTÕES

    clicar_usar_banco = wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Usar Banco de Questões')]")))
    driver.execute_script("arguments[0].click();", clicar_usar_banco)

    tags_e_ids = parse_string_to_dict_v2(string_tags)

    for conjunto_tags in tags_e_ids.values():
        
        nivel, disciplina, assunto, banca, quantidade = conjunto_tags

        try:                
            filtrar_e_selecionar(driver, wait, nivel, disciplina, assunto, banca, quantidade)

        except Exception as e:
            print(f"Error: {e}")
    
    # ADICIONANDO AS QUESTÕES
    adicionar_questoes = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Adicionar') and contains(text(), 'questões')]")))
    adicionar_questoes.click()
    time.sleep(3)
    botao_proximo = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Próximo')]")))
    botao_proximo.click()

    # CONFIGURANDO
    tipo_aplicacao = wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Aplicação Impressa')]//parent::div")))
    tipo_aplicacao.click()

    turmas = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Selecionar')]")))
    turmas.click()
    selecionar_turma = wait.until(EC.presence_of_element_located((By.XPATH, f"//p[contains(text(), '{nome_da_turma}')]//parent::div")))
    selecionar_turma.click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Concluir') and @type='button']"))).click()

    data_apl = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'dd/mm/aaaa')]")))
    data_apl.clear()
    data_apl.send_keys({data_aplicacao})
    start_hour = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='startHour']")))
    start_hour.clear()
    start_hour.send_keys({hora_inicio})
    end_hour = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='endHour']")))
    end_hour.clear()
    end_hour.send_keys({hora_fim})

    time.sleep(1)

    # CONCLUINDO
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Concluir') and @type='submit']"))).click()
    time.sleep(1)
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Confirmar')]"))).click()

    url_da_prova = driver.execute_script("return window.location.href;")
    print(f"\nURL da prova: {url_da_prova}\n")

    time.sleep(3)

    # BAIXANDO OS MATERIAIS
    baixar_materiais_prova_cartoes(driver, wait)

    time.sleep(60)

    driver.quit()

def filtrar_e_selecionar(driver, wait, nivel, disciplina, assunto, banca, quantidade):

    action = ActionChains(driver)
    
    # FILTRO "NÍVEL"
    filtro_nivel = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='input-select__body']")))
    filtro_nivel.click()
    clicar_nivel = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{nivel}')]")))
    driver.execute_script("arguments[0].click();", clicar_nivel)

    # FILTRO "DISCIPLINA"
    filtro_disciplina = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Disciplina')]//parent::span//parent::div//parent::div")))
    filtro_disciplina_click = filtro_disciplina.find_element(By.XPATH, ".//div[contains(@class, 'css')]/div[contains(@class, 'css')]/div[contains(@class, 'css')]/div[contains(@class, 'input-select')]/label[contains(@class, 'input-wrapper')]/div[contains(@class, 'input-wrapper')]/button[@type='button']")
    filtro_disciplina_click.click()
    clicar_disciplina = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{disciplina}')]")))
    driver.execute_script("arguments[0].click();", clicar_disciplina)
    time.sleep(1.5)

    # FILTRO "BANCA"
    filtro_bancas = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Bancas')]//parent::span//parent::div//parent::div")))
    div_ds_banca = filtro_bancas.find_element(By.XPATH, ".//div[contains(@class, 'css')]/div[contains(@class, 'css')]/div[contains(@class, 'css')]/div[contains(@class, 'input-select')]/label[contains(@class, 'input-wrapper')]/div[contains(@class, 'input-wrapper')]/button[@type='button']")
    id_div_da_banca = div_ds_banca.get_attribute("id")
    id_div_pesquisa = id_div_da_banca.replace("trigger","body")
    action.move_to_element(filtro_bancas).click().perform()
    time.sleep(1)
    pesquisa_bancas = driver.find_element(By.XPATH, f"//div[@id='{id_div_pesquisa}']/div/div/div/label/div/input[contains(@placeholder, 'Pesquisar')]")
    action.move_to_element(pesquisa_bancas).click().perform()
    banca_formatada = banca.replace("(","")
    banca_formatada = banca_formatada.replace(")","")
    pesquisa_bancas.clear()
    pesquisa_bancas.send_keys(f"{banca_formatada}")
    time.sleep(1)
    clicar_bancas = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{banca}')]//parent::div//parent::button")))
    clicar_bancas.click()

    # FILTRO "ASSUNTO"
    filtro_assunto = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Assunto')]//parent::span//parent::div//parent::div")))
    div_do_assunto = filtro_assunto.find_element(By.XPATH, ".//div[contains(@class, 'css')]/div[contains(@class, 'css')]/div[contains(@class, 'css')]/div[contains(@class, 'input-select')]/label[contains(@class, 'input-wrapper')]/div[contains(@class, 'input-wrapper')]/button[@type='button']")
    id_div_do_assunto = div_do_assunto.get_attribute("id")
    id_div_pesquisa = id_div_do_assunto.replace("trigger","body")
    action.move_to_element(filtro_assunto).click().perform()
    time.sleep(1)
    pesquisa_assunto = driver.find_element(By.XPATH, f"//div[@id='{id_div_pesquisa}']/div/div/div/label/div/input[contains(@placeholder, 'Pesquisar')]")
    action.move_to_element(pesquisa_assunto).click().perform()
    assunto_formatado = assunto.replace("(","")
    assunto_formatado = assunto_formatado.replace(")","")
    pesquisa_assunto.clear()
    pesquisa_assunto.send_keys(f"{assunto_formatado}")
    time.sleep(1)
    clicar_assunto = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[text()='{assunto}']//parent::div//parent::button")))
    clicar_assunto.click()

    time.sleep(2)

    # SELECIONANDO UM NÚMERO X DE QUESTÕES

    clicar_minimizar = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'iris--sidebar__header-button')]/button[@type='button']")))
    action.move_to_element(clicar_minimizar).click().perform()
    time.sleep(1)
    todas_as_questoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//label[text()='Selecionar']")))
    clicar_x_questoes = random.sample(todas_as_questoes, min(len(todas_as_questoes), 10))

    # Initialize the click counter
    loop_number = 0

    # Iterate over the sample and attempt to click each element
    for questao in clicar_x_questoes:
        try:
            # Scroll to the element to make sure it's in view
            driver.execute_script("arguments[0].scrollIntoView(true);", questao)
            
            # Attempt to click the element
            for_id = questao.get_attribute("for")
            action.move_to_element(questao).click().perform()
            time.sleep(0.5)

            # Validate the click
            if for_id != questao.get_attribute("for"):
                loop_number += 1
            else:
                continue
            
            # Stop if we've clicked the required number of times
            if loop_number >= int(f"{quantidade}"):
                print(f"Selecionadas todas as {quantidade} questões de '{disciplina} - {assunto}'.")
                break

        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Skipping element due to exception: {e}")
            # Skip this element and continue with the next one if an exception occurs

    # LIMPANDO FILTROS PARA REINICIAR
    clicar_minimizar = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'iris--sidebar__header-button')]/button[@type='button']")))
    action.move_to_element(clicar_minimizar).click().perform()
    time.sleep(0.5)
    limpar_filtros = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Limpar filtros']")))
    action.move_to_element(limpar_filtros).click().perform()
    action.move_to_element(clicar_minimizar).click().perform()
    time.sleep(0.5)
    action.move_to_element(clicar_minimizar).click().perform()
    
    time.sleep(1.5)

def baixar_materiais_prova_cartoes(driver, wait):
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Baixar materiais')]"))).click()
    time.sleep(0.5)
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[@title='Próximo']"))).click()
    time.sleep(0.5)
    wait.until(EC.presence_of_element_located((By.XPATH, "//button[@title='Baixar']"))).click()

def parse_string_to_dict_v2(string):
    result = {}
    items = string.split(';')
    for item in items:
        parts = item.split(',')
        key = int(parts[0])
        result[key] = parts[1:]
    return result

def transformar_texto_em_string(input_text):
    # Split the input text into lines, remove any extra whitespaces, and join with ';'
    return ";".join(input_text.splitlines())

def fazerLogin(driver, wait, login_acesso, senha_acesso):
    time.sleep(2)
    action_chains = ActionChains(driver)
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys({login_acesso})
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys({senha_acesso})
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

# As credenciais NÃO ficam no código: defina as variáveis de ambiente MONTADOR_LOGIN e MONTADOR_SENHA
login_acesso = os.environ.get("MONTADOR_LOGIN")
senha_acesso = os.environ.get("MONTADOR_SENHA")
if not login_acesso or not senha_acesso:
    raise SystemExit("Defina as variáveis de ambiente MONTADOR_LOGIN e MONTADOR_SENHA antes de executar o script.")
nome_da_prova = "[Demo] Simulado Exemplo"
nome_da_turma = "Turma Demo"
data_aplicacao = "13112024"
hora_inicio = "0800"
hora_fim = "1200"
texto_input = "1,Ensino Médio,Português,Linguagem figurada,BANCA EXEMPLO A,1;2,Ensino Médio,Português,Emprego de palavras e expressões,BANCA EXEMPLO A,1;3,Ensino Médio,Português,Interpretação textual,BANCA EXEMPLO A,2;4,Ensino Médio,Português,Pronomes,BANCA EXEMPLO A,1;5,Ensino Médio,Português,Verbo,BANCA EXEMPLO A,1;6,Ensino Médio,Português,Genêros textuais,BANCA EXEMPLO A,1;7,Ensino Médio,Português,Literatura contemporânea,BANCA EXEMPLO A,1;8,Ensino Médio,Português,Literatura brasileira,BANCA EXEMPLO A,1;9,Ensino Médio,Português,Pontuação,BANCA EXEMPLO A,1;10,Ensino Médio,Inglês,Reading comprehension,BANCA EXEMPLO A,5;11,Ensino Médio,História,Descolonização da América,BANCA EXEMPLO A,1;12,Ensino Médio,História,Idade Média,BANCA EXEMPLO A,1;13,Ensino Médio,História,Brasil colonial,BANCA EXEMPLO A,2;14,Ensino Médio,História,Era Vargas,BANCA EXEMPLO A,1;15,Ensino Médio,Geografia,Urbanização,BANCA EXEMPLO A,1;16,Ensino Médio,Geografia,Geopolítica e geoeconomia,BANCA EXEMPLO A,1;17,Ensino Médio,Geografia,Questões ambientais,BANCA EXEMPLO A,2;18,Ensino Médio,Geografia,Estudo da biosfera,BANCA EXEMPLO A,1;19,Ensino Médio,Biologia,Filo Platyhelmintes,BANCA EXEMPLO A,1;20,Ensino Médio,Biologia,Sistema Excretório,BANCA EXEMPLO A,1;21,Ensino Médio,Biologia,Citologia e microscopia,BANCA EXEMPLO A,1;22,Ensino Médio,Biologia,Monohibridismo e estudo de heredogramas,BANCA EXEMPLO A,1;23,Ensino Médio,Biologia,Herança dos cromossomos sexuais,BANCA EXEMPLO A,1;24,Ensino Médio,Química,Química orgânica,BANCA EXEMPLO A,1;25,Ensino Médio,Química,Constante de ionização,BANCA EXEMPLO A,1;26,Ensino Médio,Química,Identificação de funções orgânicas,BANCA EXEMPLO A,1;27,Ensino Médio,Química,Gases,BANCA EXEMPLO A,1;28,Ensino Médio,Química,Concentração de soluções,BANCA EXEMPLO A,1;29,Ensino Médio,Física,Termometria e calorimetria,BANCA EXEMPLO A,1;30,Ensino Médio,Física,Segunda lei da termodinâmica,BANCA EXEMPLO A,1;31,Ensino Médio,Física,Refração da luz,BANCA EXEMPLO A,1;32,Ensino Médio,Física,Conceitos de ondulatória,BANCA EXEMPLO A,1;33,Ensino Médio,Física,Aplicada sobre a corrente elétrica,BANCA EXEMPLO A,1;34,Ensino Médio,Matemática,Razão e proporção,BANCA EXEMPLO A,1;35,Ensino Médio,Matemática,Equação,BANCA EXEMPLO A,1;36,Ensino Médio,Matemática,Plana,BANCA EXEMPLO A,3;37,Ensino Médio,Matemática,Logarítmica,BANCA EXEMPLO A,1;38,Ensino Médio,Matemática,Prismas,BANCA EXEMPLO A,1;39,Ensino Médio,Matemática,Estatística,BANCA EXEMPLO A,1;40,Ensino Médio,Matemática,Cilindro,BANCA EXEMPLO A,1;41,Ensino Médio,Matemática,Polinômios,BANCA EXEMPLO A,1"

start_time = datetime.now()

string_tags = transformar_texto_em_string(texto_input)

url_lms = os.environ.get("MONTADOR_URL_LMS")
if not url_lms:
    raise SystemExit("Defina a variável de ambiente MONTADOR_URL_LMS (endereço base do LMS) antes de executar o script.")

montar_e_baixar = qmagico(string_tags, f"{url_lms.rstrip('/')}/entrar/?redirectTo=/atividades/avaliacoes/listagem-provas")

end_time = datetime.now()

running_duration = (end_time - start_time).total_seconds() / 60

print(f"\nInício (Geral): {start_time.strftime('%Y-%m-%d %H:%M:%S')}\nFim (Geral): {end_time.strftime('%Y-%m-%d %H:%M:%S')}\nDuração (Geral): {running_duration:.2f} minutes\n")
