import pandas as pd
import matplotlib.pyplot as plt

# Versão inicial de análise. Foi substituída pelo script completo em analise_graficos.py

def analisar_glosas():
    df = pd.read_csv('autorizacoes_hospitalares.csv')

    # Remove duplicatas e padroniza textos antes de qualquer análise
    df = df.drop_duplicates()
    for coluna in ['status', 'justificativa', 'especialidade']:
        df[coluna] = df[coluna].str.strip()

    print(f"Total de guias analisadas: {len(df)}")

    # Filtra só as negativas — aprovadas não entram no ranking de glosas
    glosas_por_especialidade = (
        df[df['status'] == 'Negado']['especialidade']
        .value_counts()
    )

    print("\nRanking de glosas por especialidade:")
    print(glosas_por_especialidade.to_string())

    plt.figure(figsize=(12, 6))
    glosas_por_especialidade.plot(kind='bar', color='firebrick', edgecolor='black')
    plt.title('Volume de Glosas (Negativas) por Especialidade Médica',
              fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Especialidade Médica', fontsize=12, labelpad=10)
    plt.ylabel('Quantidade de Guias Negadas', fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('graficos/grafico_glosas_especialidade.png')
    plt.close()

    print("Grafico salvo.")

if __name__ == '__main__':
    analisar_glosas()