import pandas as pd
import matplotlib.pyplot as plt
# Versão inicial de análise. Foi substituída pelo script completo em analise_graficos.py

# =============================================================================
# ANÁLISE DE GLOSAS POR ESPECIALIDADE MÉDICA
# Lê a planilha gerada pelo script anterior, limpa os dados e produz um gráfico
# com o ranking de especialidades que mais tiveram guias negadas (glosadas).
# =============================================================================

def analisar_glosas():
    print("Carregando os dados da planilha de auditoria...")

    # Pandas lê o CSV gerado pelo script anterior e carrega tudo na memória
    df = pd.read_csv('autorizacoes_hospitalares.csv')

    # --- Limpeza e Tratamento de Dados ---
    # Remove linhas duplicadas que possam ter entrado por falha de sistema
    df = df.drop_duplicates()

    # Remove espaços invisíveis nas colunas de texto para evitar erros de comparação
    # (ex: 'Negado ' e 'Negado' seriam tratados como valores diferentes sem isso)
    for coluna in ['status', 'justificativa', 'especialidade']:
        df[coluna] = df[coluna].str.strip()

    print(f"Base tratada com sucesso! Total de guias analisadas: {len(df)}")
    print("-" * 50)

    # --- Cruzamento Estratégico ---
    # Filtra apenas guias Negadas e conta quantas ocorreram em cada especialidade
    glosas_por_especialidade = (
        df[df['status'] == 'Negado']['especialidade']
        .value_counts()
    )

    # Exibe o ranking no terminal antes de gerar o gráfico
    print("Ranking de glosas por especialidade:")
    print(glosas_por_especialidade.to_string())
    print("-" * 50)

    # --- Geração do Gráfico ---
    print("Gerando o gráfico de volume de glosas...")

    plt.figure(figsize=(12, 6))

    # Barras em vermelho-vinho: cor padrão de alerta para perdas e negativas
    glosas_por_especialidade.plot(kind='bar', color='firebrick', edgecolor='black')

    plt.title('Volume de Glosas (Negativas) por Especialidade Médica',
              fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Especialidade Médica', fontsize=12, labelpad=10)
    plt.ylabel('Quantidade de Guias Negadas', fontsize=12, labelpad=10)

    # Inclina os nomes das especialidades para não sobrepor um no outro
    plt.xticks(rotation=45, ha='right')

    # Ajusta margens para nenhum elemento ficar cortado na imagem final
    plt.tight_layout()

    # Salva o gráfico como PNG na mesma pasta onde o script está sendo executado
    nome_grafico = 'grafico_glosas_especialidade.png'
    plt.savefig(nome_grafico)

    # Libera o gráfico da memória após salvar
    plt.close()

    print(f"Gráfico salvo com sucesso como '{nome_grafico}'")

if __name__ == '__main__':
    analisar_glosas()