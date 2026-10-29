import time
import os
import re
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

def funcao_principal(url_home,id_simulado):

    # Carregar planilhas de apoio
    print("Carregando planilhas de apoio...")
    planilhas = carregar_planilhas_apoio()
    if planilhas is None:
        print("Erro: Não foi possível carregar as planilhas de apoio. Continuando sem verificações...")
        planilhas = {}

    # Initialize the Chrome WebDriver with ChromeOptions
    service = Service()  # o Selenium Manager baixa o driver compatível com o Chrome instalado
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized') 
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open a webpage
    driver.get(url_home) 
    wait = WebDriverWait(driver, 10)

    print("Navegador iniciado, aguarde o script finalizar a execução")

    fazerLogin(driver, wait, login_acesso, senha_acesso)

    # ----- SELECIONANDO O 'SAS' EM MARCAS

    time.sleep(1)
    abrir_menu_marcas = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'iris--select__indicator')]")))
    abrir_menu_marcas.click()

    selecionar_sas = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'SAS Educação')]")))
    selecionar_sas.click()

    selecionar_sas_continuar = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Continuar')]")))
    selecionar_sas_continuar.click()

    # --- ABRINDO A PROVA DIRETAMENTE NA URL

    driver.get(f"{url_backoffice.rstrip('/')}/gestora-avaliacoes/composition/{id_simulado}/?header=none")

    # --- SELECIONANDO E ADICIONANDO AS QUESTÕES - CADERNO 01

    conjunto_filtros = parse_string_to_dict_v2(string_tags_filtros_caderno_1)

    for filtros in conjunto_filtros.values():
        
        nivel, tipo, disciplina, assunto, banca, quantidade = filtros

        try:
            filtrar_e_selecionar(driver, wait, nivel, tipo, disciplina, assunto, banca, quantidade, caderno_1, planilhas)

        except Exception as e:
            print(f"Error: {e}")

    # --- SELECIONANDO E ADICIONANDO AS QUESTÕES - CADERNO 02

    """conjunto_filtros_2 = parse_string_to_dict_v2(string_tags_filtros_caderno_2)

    for filtros in conjunto_filtros_2.values():
        
        nivel, tipo, disciplina, assunto, quantidade = filtros

        try:
            filtrar_e_selecionar(driver, wait, nivel, tipo, disciplina, assunto, quantidade, caderno_2)

        except Exception as e:
            print(f"Error: {e}")"""

    # PEGAR NOME DO SIMULADO PARA VALIDAR

    nome_do_simulado = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'contextview-nav__title-wrapper')]/p[contains(@class, 'iris--text')]")))
    nome_do_simulado = nome_do_simulado.get_attribute("innerText")

    # FINALIZAR (CLICAR "CONTINUAR DEPOIS")

    contimuar_depois = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Continuar depois')]")))
    contimuar_depois.click()
    time.sleep(1)
    
    driver.quit()

    print(f"ID do Simulado: {id_simulado}\nNome do Simulado: {nome_do_simulado}")

def filtrar_e_selecionar(driver, wait, nivel, tipo, disciplina, assunto, banca, quantidade, nome_caderno, planilhas):

    action = ActionChains(driver)

    # ABRIR A TELA DE BUSCA DE ITENS A PARTIR DO CADERNO
    add_questoes = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Adicionar Questões')]")))
    add_questoes.click()
    time.sleep(1)

    # LIMPAR FILTROS
    limpar_filtros = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Limpar filtros')]")))
    driver.execute_script("arguments[0].click();", limpar_filtros)
    time.sleep(2)

    # CHECAR FILTRO "OBJETIVO"
    dropdown_objetivo = wait.until(EC.presence_of_element_located((By.XPATH, f"//p[text()='Selecione uma opção']//parent::button")))
    driver.execute_script("arguments[0].click();", dropdown_objetivo)
    time.sleep(1)
    objetivo_avl = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[text()='Avaliações']//parent::div//parent::button[@role='option']")))
    objetivo_avl.click()
    class_botao_objetivo = objetivo_avl.get_attribute("aria-selected")
    check_botao_clicado = class_botao_objetivo.find("true")

    if check_botao_clicado == -1:
        action.move_to_element(objetivo_avl).click().perform()
    else:
        time.sleep(1)
    time.sleep(1)

    # CHECAR FILTRO "ORIGEM"
    origem_avl = wait.until(EC.presence_of_element_located((By.XPATH, f"//p[text()='Arco']//parent::div")))
    class_botao_origem = origem_avl.get_attribute("class")
    check_botao_clicado = class_botao_origem.find("active")

    if check_botao_clicado == -1:
        action.move_to_element(origem_avl).click().perform()
    else:
        time.sleep(1)
    time.sleep(1)
    
    # FILTRO "NÍVEL"
    clicar_nivel = wait.until(EC.presence_of_element_located((By.XPATH, f"//p[text()='{nivel}']//parent::div[contains(@data-testid, 'iris-chips')]")))
    driver.execute_script("arguments[0].click();", clicar_nivel)

    # FILTRO "DISCIPLINA"
    filtro_disciplina_0 = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Disciplina')]//parent::span//parent::div")))
    filtro_disciplina = filtro_disciplina_0.find_element(By.XPATH, "./following-sibling::div[.//p[text()='Selecione uma opção']]")
    driver.execute_script("arguments[0].scrollIntoView(true);", filtro_disciplina)
    action.move_to_element(filtro_disciplina).click().perform()
    time.sleep(1)
    clicar_disciplina = wait.until(EC.presence_of_element_located((By.XPATH, f"//button[.//div[text()='{disciplina}']]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", clicar_disciplina)
    driver.execute_script("arguments[0].click();", clicar_disciplina)
    time.sleep(1.5)

    # FILTRO "ASSUNTO"
    filtro_assunto = wait.until(EC.presence_of_element_located((By.XPATH, ".//div[text()='Escolher assunto']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", filtro_assunto)
    filtro_assunto.click()
    pesquisar_assunto = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Pesquisar Assunto']")))
    pesquisar_assunto.send_keys({assunto})
    time.sleep(1)
    clicar_assunto = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{assunto}')]//parent::span")))
    driver.execute_script("arguments[0].click();", clicar_assunto)
    time.sleep(1)
    aplicar_filtro_assunto = wait.until(EC.presence_of_element_located((By.XPATH, ".//button[text()='Aplicar']")))
    driver.execute_script("arguments[0].click();", aplicar_filtro_assunto)
    time.sleep(2)

    # FILTRO "TIPO"
    clicar_tipo = wait.until(EC.presence_of_element_located((By.XPATH, f"//p[text()='{tipo}']//parent::div[contains(@data-testid, 'iris-chips')]")))
    action.move_to_element(clicar_tipo).click().perform()
    time.sleep(1)

    # FILTRO "BANCA"
    filtro_banca = wait.until(EC.presence_of_element_located((By.XPATH, ".//div[text()='Banca']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", filtro_banca)
    filtro_banca.click()
    pesquisar_banca = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Pesquisar Bancas']")))
    pesquisar_banca.send_keys({banca})
    time.sleep(1)
    clicar_banca = wait.until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{banca}')]//parent::span")))
    driver.execute_script("arguments[0].click();", clicar_banca)
    time.sleep(1)
    aplicar_filtro_banca = wait.until(EC.presence_of_element_located((By.XPATH, ".//button[text()='Aplicar']")))
    driver.execute_script("arguments[0].click();", aplicar_filtro_banca)
    time.sleep(2)

    # SELECIONANDO UM NÚMERO X DE QUESTÕES

    todas_as_questoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//label[contains(text(), 'ID ') and contains(@for, 'chekbox')]")))
    
    # Initialize the click counter
    loop_number = 0
    questoes_clicadas = set()  # Para controlar questões já clicadas

    # Função para verificar se uma questão deve ser clicada
    def verificar_e_clicar_questao(questao, reference_id):
        nonlocal loop_number
        
        # b) Verificar se está na planilha de questões da 1a aplicação
        if 'questoes_1a_aplicacao' in planilhas and not planilhas['questoes_1a_aplicacao'].empty:
            if reference_id in planilhas['questoes_1a_aplicacao']['reference'].astype(str).values:
                print(f"Questão {reference_id} desconsiderada - já usada na 1a aplicação")
                return False
        
        # c) Verificar grupos para disciplinas específicas (apenas para Português, Inglês, Espanhol)
        if disciplina in ['Português', 'Inglês', 'Espanhol'] and 'questoes_agrupadas' in planilhas and not planilhas['questoes_agrupadas'].empty:
            # Verificar se a questão faz parte de um grupo
            grupo_info = planilhas['questoes_agrupadas'][planilhas['questoes_agrupadas']['reference'] == reference_id]
            if not grupo_info.empty:
                grupo = grupo_info.iloc[0]['grupo']
                print(f"Questão {reference_id} faz parte do grupo {grupo}")
                
                # Encontrar todas as questões do mesmo grupo na amostra atual
                questoes_do_grupo = planilhas['questoes_agrupadas'][
                    (planilhas['questoes_agrupadas']['grupo'] == grupo) & 
                    (planilhas['questoes_agrupadas']['label_reference'].isin([q.get_attribute("innerText").replace("ID ", "") for q in todas_as_questoes]))
                ]
                
                # Clicar em todas as questões do grupo
                for _, questao_grupo in questoes_do_grupo.iterrows():
                    label_reference = questao_grupo['label_reference']
                    # Encontrar o elemento correspondente na página
                    for q in todas_as_questoes:
                        if q.get_attribute("innerText") == label_reference:
                            try:
                                driver.execute_script("arguments[0].scrollIntoView(true);", q)
                                for_id = q.get_attribute("for")
                                driver.execute_script("arguments[0].click();", q)
                                time.sleep(1)
                                
                                if for_id != q.get_attribute("for"):
                                    loop_number += 1
                                    questoes_clicadas.add(label_reference)
                                    print(f"Questão do grupo {grupo} clicada: {label_reference}")
                            except Exception as e:
                                print(f"Erro ao clicar questão do grupo: {e}")
                
                # IMPORTANTE: Não retornar aqui, continuar para o passo 'd'
        
        # d) Verificar se está na planilha de todas as questões (SEMPRE executar este passo)
        if 'todas_as_questoes' in planilhas and not planilhas['todas_as_questoes'].empty:
            if reference_id in planilhas['todas_as_questoes']['reference'].astype(str).values:
                return True  # Pode clicar
            else:
                print(f"Questão {reference_id} não encontrada na planilha de todas as questões")
                return False
        
        # Se não há planilhas carregadas, permitir clicar
        return True

    # Processar questões em ordem aleatória
    clicar_x_questoes = random.sample(todas_as_questoes, min(len(todas_as_questoes), 10))

    for questao in clicar_x_questoes:
        try:
            # Scroll to the element to make sure it's in view
            driver.execute_script("arguments[0].scrollIntoView(true);", questao)
            inner_text_id = questao.get_attribute("innerText")
            reference_id = inner_text_id.replace("ID ", "")
            
            # Verificar se já foi clicada
            if reference_id in questoes_clicadas:
                continue
            
            # Verificar se deve clicar na questão
            if verificar_e_clicar_questao(questao, reference_id):
                # Attempt to click the element
                for_id = questao.get_attribute("for")
                driver.execute_script("arguments[0].click();", questao)
                time.sleep(1)

                # Validate the click
                if for_id != questao.get_attribute("for"):
                    loop_number += 1
                    questoes_clicadas.add(reference_id)
                else:
                    continue
            
            # Stop if we've clicked the required number of times (mas permitir grupos)
            if loop_number >= int(f"{quantidade}") and disciplina not in ['Português', 'Inglês', 'Espanhol']:
                print(f"Selecionadas todas as {quantidade} questões de '{disciplina} - {assunto}'.")
                break

        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Skipping element due to exception: {e}")
            # Skip this element and continue with the next one if an exception occurs

    adicionar_questoes = wait.until(EC.presence_of_element_located((By.XPATH, "//button[.//div[contains(text(), 'Questões') or contains(text(), 'Questão')]]")))
    adicionar_questoes.click()
    time.sleep(1)


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

def extrair_id_de_prova_da_url(url):
    match = re.search(r'composition/(\d+)', url)
    if match:
        return match.group(1)
    return None

def fazerLogin(driver, wait, login_acesso, senha_acesso):
    time.sleep(2)
    action_chains = ActionChains(driver)
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys({login_acesso})
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys({senha_acesso})
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

def carregar_planilhas_apoio():
    """Carrega as planilhas de apoio para verificação de questões"""
    try:
        # Carregar a planilha de apoio
        planilha_path = "planilha_de_apoio_da_operacao.xlsx"
        
        # Carregar as abas específicas
        questoes_1a_aplicacao = pd.read_excel(planilha_path, sheet_name='questoes_1a_aplicacao')
        questoes_agrupadas = pd.read_excel(planilha_path, sheet_name='questoes_agrupadas')
        todas_as_questoes_planilha = pd.read_excel(planilha_path, sheet_name='todas_as_questoes')
        
        return {
            'questoes_1a_aplicacao': questoes_1a_aplicacao,
            'questoes_agrupadas': questoes_agrupadas,
            'todas_as_questoes': todas_as_questoes_planilha
        }
    except Exception as e:
        print(f"Erro ao carregar planilhas de apoio: {e}")
        return None

# As credenciais NÃO ficam no código: defina as variáveis de ambiente MONTADOR_LOGIN e MONTADOR_SENHA
login_acesso = os.environ.get("MONTADOR_LOGIN")
senha_acesso = os.environ.get("MONTADOR_SENHA")
if not login_acesso or not senha_acesso:
    raise SystemExit("Defina as variáveis de ambiente MONTADOR_LOGIN e MONTADOR_SENHA antes de executar o script.")

url_backoffice = os.environ.get("MONTADOR_URL_BACKOFFICE")
if not url_backoffice:
    raise SystemExit("Defina a variável de ambiente MONTADOR_URL_BACKOFFICE (endereço base do backoffice) antes de executar o script.")

url_home = f"{url_backoffice.rstrip('/')}/entrar/?guestLogin=true"
id_simulado = 271923

caderno_1 = "Objetivas"
filtros_caderno_1 = "1,Ensino Médio,Múltipla Escolha,Português,Competência leitora,ALBERT ENSTEIN - SP,3;" \
"2,Ensino Médio,Múltipla Escolha,Matemática,Proporcionalidade Direta e Indireta,FGV,2;" \
"3,Ensino Médio,Múltipla Escolha,Matemática,Números Inteiros,FGV,1;" \
"4,Ensino Médio,Múltipla Escolha,Matemática,Números Racionais,FGV,2"

#caderno_2 = "nome"
#filtros_caderno_2 = "1,Ensino Médio,XXXX,XXXXX,0"

start_time = datetime.now()

string_tags_filtros_caderno_1 = transformar_texto_em_string(filtros_caderno_1)
#string_tags_filtros_caderno_2 = transformar_texto_em_string(filtros_caderno_2)

montar_simulado = funcao_principal(url_home,id_simulado)

end_time = datetime.now()

running_duration = (end_time - start_time).total_seconds() / 60

print(f"\nInício (Geral): {start_time.strftime('%Y-%m-%d %H:%M:%S')}\nFim (Geral): {end_time.strftime('%Y-%m-%d %H:%M:%S')}\nDuração (Geral): {running_duration:.2f} minutes\n")
