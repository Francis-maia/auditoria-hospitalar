import csv
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sqlite3

especialidades = [
    'Clínica Médica', 'Cardiologia', 'Neurologia', 'Oncologia', 'Endocrinologia',
    'Gastroenterologia', 'Pneumologia', 'Reumatologia', 'Infectologia', 'Nefrologia',
    'Ortopedia e Traumatologia', 'Cirurgia Geral', 'Ginecologia e Obstetrícia',
    'Urologia', 'Oftalmologia', 'Otorrinolaringologia', 'Neurocirurgia',
    'Cirurgia Cardiovascular', 'Pediatria', 'Anestesiologia'
]
procedimentos = [f'PROC{i:03d}' for i in range(1, 21)]

justificativas_aprovado = [
    'Adequação integral às Diretrizes de Utilização (DUT) vigentes.',
    'Quadro de urgência/emergência devidamente configurado em relatório médico.',
    'Pertinência clínica do procedimento corroborada por exames complementares.',
    'Alinhamento terapêutico e histórico de esgotamento de linhas conservadoras.',
    'Indicação adequada e justificada de OPMEs conforme literatura atualizada.',
    'Cobertura contratual vigente, sem restrições de carência ou CPT.',
    'Correção de lateralidade e codificação TUSS em conformidade com o pedido.',
    'Parecer favorável para manutenção de internação por dependência de cuidados.'
]
justificativas_negado = [
    'Não preenchimento dos critérios estabelecidos nas Diretrizes de Utilização (DUT).',
    'Glosa técnica por incompatibilidade, redundância ou excesso de OPMEs solicitadas.',
    'Ausência de exames complementares que comprovem a necessidade do procedimento.',
    'Incompatibilidade técnica entre o CID informado e o procedimento solicitado.',
    'Tratamento elegível para via ambulatorial, sem justificativa clínica para internação.',
    'Negativa por Cobertura Parcial Temporária (CPT) vigente para doença preexistente.',
    'Fracionamento indevido de códigos TUSS do procedimento cirúrgico principal.',
    'Divergência na codificação TUSS, lateralidade ou preenchimento incorreto da guia.',
    'Procedimento experimental, off-label ou fora do rol de coberturas contratuais.',
    'Falta de comprovação do esgotamento de linhas de tratamento conservadoras.'
]


def gerar_massa_dados(nome_arquivo='dados/autorizacoes_hospitalares.csv', total_linhas=1000):
    # seed fixa garante reprodutibilidade — o CSV gerado é sempre igual
    random.seed(42)
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['codigo_procedimento', 'status', 'justificativa', 'valor', 'especialidade'])
        for _ in range(total_linhas):
            proc = random.choice(procedimentos)
            esp = random.choice(especialidades)
            status = random.choices(['Aprovado', 'Negado'], weights=[0.7, 0.3], k=1)[0]
            if status == 'Aprovado':
                just = random.choice(justificativas_aprovado)
                valor = round(random.uniform(1200.0, 35000.0), 2)
            else:
                just = random.choice(justificativas_negado)
                valor = round(random.uniform(500.0, 18000.0), 2)
            writer.writerow([proc, status, just, valor, esp])
    print(f"Planilha '{nome_arquivo}' gerada com {total_linhas} guias.")


def carregar_e_limpar(nome_arquivo='dados/autorizacoes_hospitalares.csv'):
    df = pd.read_csv(nome_arquivo)
    total_bruto = len(df)

    df = df.drop_duplicates()

    for coluna in ['status', 'justificativa', 'especialidade', 'codigo_procedimento']:
        df[coluna] = df[coluna].str.strip()

    # Linhas com valor não numérico são descartadas — não podem entrar na média
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df = df.dropna(subset=['valor'])

    print(f"Base carregada: {total_bruto} registros brutos, {len(df)} após limpeza.")
    return df


def rodar_queries_sql(df):
    conn = sqlite3.connect(':memory:')
    df.to_sql('autorizacoes', conn, index=False, if_exists='replace')

    q1 = """
        SELECT
            codigo_procedimento,
            COUNT(*) AS total_negadas,
            ROUND(AVG(valor), 2) AS valor_medio
        FROM autorizacoes
        WHERE status = 'Negado'
        GROUP BY codigo_procedimento
        ORDER BY total_negadas DESC
        LIMIT 5
    """
    print("\nTOP 5 - Procedimentos mais negados:")
    print(pd.read_sql(q1, conn).to_string(index=False))

    q2 = """
        SELECT
            especialidade,
            COUNT(*) AS total_glosas,
            ROUND(AVG(valor), 2) AS media_valor,
            ROUND(SUM(valor), 2) AS impacto_total
        FROM autorizacoes
        WHERE status = 'Negado'
        GROUP BY especialidade
        ORDER BY media_valor DESC
    """
    print("\nMedia de valor das glosas por especialidade:")
    print(pd.read_sql(q2, conn).to_string(index=False))

    # Calcula o indice de negacao por especialidade para uso no grafico
    q3 = """
        SELECT
            especialidade,
            COUNT(*) AS total_guias,
            SUM(CASE WHEN status = 'Negado' THEN 1 ELSE 0 END) AS negadas,
            ROUND(
                SUM(CASE WHEN status = 'Negado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                1
            ) AS indice_negacao_pct
        FROM autorizacoes
        GROUP BY especialidade
        ORDER BY indice_negacao_pct DESC
    """
    resultado_indice = pd.read_sql(q3, conn)
    print("\nIndice de negacao (%) por especialidade:")
    print(resultado_indice.to_string(index=False))

    conn.close()
    return resultado_indice


def gerar_graficos(df, resultado_indice):
    glosas_volume = (
        df[df['status'] == 'Negado']['especialidade']
        .value_counts()
    )

    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.bar(
        glosas_volume.index,
        glosas_volume.values,
        color='firebrick',
        edgecolor='#1a1a1a',
        linewidth=0.7
    )
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(int(bar.get_height())),
            ha='center', va='bottom', fontsize=8.5, color='#333333'
        )
    ax.set_title('Volume de Glosas (Negativas) por Especialidade Médica',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Especialidade Médica', fontsize=12, labelpad=10)
    ax.set_ylabel('Quantidade de Guias Negadas', fontsize=12, labelpad=10)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig('graficos/grafico_glosas_volume.png', dpi=150)
    plt.close()

    idx = resultado_indice.sort_values('indice_negacao_pct', ascending=False)
    valores = idx['indice_negacao_pct'].values
    norm = plt.Normalize(vmin=valores.min(), vmax=valores.max())
    cores = plt.cm.RdYlGn_r(norm(valores))

    fig, ax = plt.subplots(figsize=(13, 6))
    bars2 = ax.bar(
        idx['especialidade'],
        idx['indice_negacao_pct'],
        color=cores,
        edgecolor='#1a1a1a',
        linewidth=0.7
    )
    media_geral = idx['indice_negacao_pct'].mean()
    ax.axhline(media_geral, color='navy', linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(
        len(idx) - 0.5, media_geral + 0.3,
        f'Media: {media_geral:.1f}%',
        color='navy', fontsize=9, ha='right'
    )
    for bar, val in zip(bars2, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f'{val:.1f}%',
            ha='center', va='bottom', fontsize=8, color='#222222'
        )
    ax.set_title('Indice de Negacao (%) por Especialidade Medica',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Especialidade Medica', fontsize=12, labelpad=10)
    ax.set_ylabel('Taxa de Negacao (%)', fontsize=12, labelpad=10)
    ax.set_ylim(0, valores.max() * 1.15)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig('graficos/grafico_indice_negacao.png', dpi=150)
    plt.close()

    print("Graficos salvos na pasta graficos/")


if __name__ == '__main__':
    gerar_massa_dados()
    df = carregar_e_limpar()
    resultado_indice = rodar_queries_sql(df)
    gerar_graficos(df, resultado_indice)
    print("Analise concluida.")