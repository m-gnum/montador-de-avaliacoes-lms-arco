import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import re
from collections import defaultdict
import itertools

def clean_text(text):
    """Limpa o texto removendo caracteres especiais e normalizando"""
    if pd.isna(text):
        return ""
    # Remove caracteres especiais, mantém apenas letras, números e espaços
    text = re.sub(r'[^\w\s]', ' ', str(text))
    # Remove espaços extras
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def create_word_list(text):
    """Transforma o texto em uma lista de palavras"""
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return []
    return cleaned_text.split()

def create_ngrams(text, n=2):
    """Cria n-grams do texto"""
    words = create_word_list(text)
    if len(words) < n:
        return []
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

def calculate_cosine_similarity_ngrams(texts, n=2):
    """Calcula similaridade de cossenos usando n-grams"""
    # Cria n-grams para cada texto
    ngram_texts = []
    for text in texts:
        ngrams = create_ngrams(text, n)
        ngram_texts.append(' '.join(ngrams))
    
    # Usa TF-IDF para vetorizar os n-grams
    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1))
    tfidf_matrix = vectorizer.fit_transform(ngram_texts)
    
    # Calcula similaridade de cossenos
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

def find_similar_groups(df_filtered, similarity_threshold=0.6):
    """Encontra grupos de questões com similaridade acima do threshold"""
    if df_filtered.empty:
        return []
    
    # Remove duplicatas baseado na coluna 'reference'
    df_unique = df_filtered.drop_duplicates(subset=['reference'])
    
    if len(df_unique) < 2:
        return []
    
    # Calcula similaridade de cossenos usando n-grams
    texts = df_unique['text_purified'].tolist()
    similarity_matrix = calculate_cosine_similarity_ngrams(texts, n=2)
    
    # Encontra pares com similaridade acima do threshold
    similar_groups = []
    processed_indices = set()
    
    for i in range(len(similarity_matrix)):
        if i in processed_indices:
            continue
            
        group = [i]
        processed_indices.add(i)
        
        for j in range(i+1, len(similarity_matrix)):
            if j not in processed_indices and similarity_matrix[i][j] >= similarity_threshold:
                group.append(j)
                processed_indices.add(j)
        
        if len(group) > 1:  # Só adiciona grupos com mais de um elemento
            similar_groups.append(group)
    
    # Converte índices para referências
    result_groups = []
    for group in similar_groups:
        group_references = [df_unique.iloc[idx]['reference'] for idx in group]
        result_groups.append(group_references)
    
    return result_groups

def main():
    # Carrega a planilha
    print("Carregando planilha...")
    excel_file = "questoes_de_linguagens_ing_esp.xlsx"
    
    try:
        df = pd.read_excel(excel_file, sheet_name="ids e enunciados")
        print(f"Planilha carregada com {len(df)} linhas")
    except Exception as e:
        print(f"Erro ao carregar planilha: {e}")
        return
    
    # Cria nova coluna com lista de palavras
    print("Criando coluna com lista de palavras...")
    df['word_list'] = df['text_purified'].apply(create_word_list)
    
    # Lista de bancas para análise
    bancas_analysis = [
        'UNISA',
        'MACKENZIE - SP', 
        'FCMSC - SP', 
        'ESPM - SP', 
        'ALBERT ENSTEIN - SP', 
        'FACUL. MED ABC-SP', 
        'SAS ENEM',
        ['FGV', 'FGV - SP']  # Trata as duas FGV como uma só
    ]
    
    # Dicionário para armazenar resultados
    all_results = {}
    
    # Processa cada banca
    for banca in bancas_analysis:
        print(f"\nProcessando banca: {banca}")
        
        if isinstance(banca, list):
            # Caso especial para FGV
            df_filtered = df[df['banca'].isin(banca)]
            banca_name = "FGV_COMBINADA"
        else:
            df_filtered = df[df['banca'] == banca]
            banca_name = banca
        
        print(f"Encontradas {len(df_filtered)} questões para {banca_name}")
        
        if len(df_filtered) > 0:
            # Encontra grupos similares
            similar_groups = find_similar_groups(df_filtered, similarity_threshold=0.6)
            all_results[banca_name] = similar_groups
            print(f"Encontrados {len(similar_groups)} grupos similares")
        else:
            all_results[banca_name] = []
            print("Nenhuma questão encontrada para esta banca")
    
    # Salva resultados em uma nova aba
    print("\nSalvando resultados...")
    
    # Cria um DataFrame com os resultados
    results_data = []
    for banca, groups in all_results.items():
        for i, group in enumerate(groups):
            for j, reference in enumerate(group):
                results_data.append({
                    'banca': banca,
                    'grupo': i + 1,
                    'reference': reference,
                    'tamanho_grupo': len(group)
                })
    
    results_df = pd.DataFrame(results_data)
    
    # Salva a planilha original com a nova coluna e cria nova aba com resultados
    with pd.ExcelWriter(excel_file, mode='a', if_sheet_exists='replace') as writer:
        # Atualiza a aba original com a nova coluna
        df.to_excel(writer, sheet_name="ids e enunciados", index=False)
        
        # Cria nova aba com os grupos similares
        results_df.to_excel(writer, sheet_name="grupos_similares", index=False)
    
    print(f"Análise concluída! Resultados salvos na aba 'grupos_similares'")
    print(f"Total de grupos encontrados: {sum(len(groups) for groups in all_results.values())}")
    
    # Mostra resumo dos resultados
    print("\nResumo dos resultados:")
    for banca, groups in all_results.items():
        print(f"{banca}: {len(groups)} grupos similares")

if __name__ == "__main__":
    main()
