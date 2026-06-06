import csv
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sqlite3

# =============================================================================
# PIPELINE COMPLETO DE AUDITORIA — GERAÇÃO + LIMPEZA + ANÁLISE + SQL + GRÁFICOS
# =============================================================================

# =============================================================================
# PARTE 1 — Gerador de massa de dados (mesmo do script original)
# =============================================================================

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

def gerar_massa_dados(nome_arquivo='autorizacoes_hospitalares.csv', total_linhas=1000):
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
    print(f"✅ Planilha '{nome_arquivo}' gerada com {total_linhas} guias.")


# =============================================================================
# PARTE 2 — Limpeza e tratamento de dados com Pandas
# =============================================================================

def carregar_e_limpar(nome_arquivo='autorizacoes_hospitalares.csv'):
    print("\n📂 Carregando e limpando os dados...")

    df = pd.read_csv(nome_arquivo)

    total_bruto = len(df)

    # Remove duplicatas exatas
    df = df.drop_duplicates()
    duplicatas_removidas = total_bruto - len(df)

    # Padroniza textos: remove espaços extras, normaliza caixa
    for coluna in ['status', 'justificativa', 'especialidade', 'codigo_procedimento']:
        df[coluna] = df[coluna].str.strip()

    # Garante que 'valor' é numérico; linhas inválidas viram NaN e são removidas
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    nulos_removidos = df['valor'].isna().sum()
    df = df.dropna(subset=['valor'])

    print(f"   Total bruto:           {total_bruto}")
    print(f"   Duplicatas removidas:  {duplicatas_removidas}")
    print(f"   Valores inválidos:     {nulos_removidos}")
    print(f"   Base limpa final:      {len(df)} registros")

    return df


# =============================================================================
# PARTE 3 — Queries SQL via SQLite (em memória, sem precisar instalar nada)
# A ideia: carregamos o DataFrame no SQLite e rodamos SQL real sobre os dados.
# Isso demonstra que você entende SQL E Python ao mesmo tempo.
# =============================================================================

def rodar_queries_sql(df):
    print("\n🗄️  Rodando queries SQL (SQLite em memória)...")

    # Cria banco em memória e carrega o DataFrame como tabela 'autorizacoes'
    conn = sqlite3.connect(':memory:')
    df.to_sql('autorizacoes', conn, index=False, if_exists='replace')

    # --- Query 1: Procedimento mais negado ---
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
    print("\n📊 TOP 5 — Procedimentos mais negados:")
    print(pd.read_sql(q1, conn).to_string(index=False))

    # --- Query 2: Média de valor das glosas por especialidade ---
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
    print("\n📊 Média de valor das glosas por especialidade:")
    print(pd.read_sql(q2, conn).to_string(index=False))

    # --- Query 3: Índice de negação por especialidade ---
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
    print("\n📊 Índice de negação (%) por especialidade:")
    print(resultado_indice.to_string(index=False))

    conn.close()
    return resultado_indice


# =============================================================================
# PARTE 4 — Gráficos
# Gráfico 1: Volume absoluto de glosas por especialidade (original aprimorado)
# Gráfico 2: ÍNDICE DE NEGAÇÃO (%) — mais relevante para auditoria
# =============================================================================

def gerar_graficos(df, resultado_indice):
    print("\n📈 Gerando gráficos...")

    # --- Dados para o gráfico 1: volume absoluto ---
    glosas_volume = (
        df[df['status'] == 'Negado']['especialidade']
        .value_counts()
    )

    # === GRÁFICO 1 — Volume absoluto ===
    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.bar(
        glosas_volume.index,
        glosas_volume.values,
        color='firebrick',
        edgecolor='#1a1a1a',
        linewidth=0.7
    )

    # Rótulo de valor em cima de cada barra
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
    plt.savefig('grafico_glosas_volume.png', dpi=150)
    plt.close()
    print("   ✅ 'grafico_glosas_volume.png' salvo.")

    # === GRÁFICO 2 — Índice de negação (%) ===
    # Ordena do maior para o menor índice
    idx = resultado_indice.sort_values('indice_negacao_pct', ascending=False)

    fig, ax = plt.subplots(figsize=(13, 6))

    # Gradiente de cor: barras mais altas ficam mais escuras (vermelho → laranja)
    valores = idx['indice_negacao_pct'].values
    norm = plt.Normalize(vmin=valores.min(), vmax=valores.max())
    cores = plt.cm.RdYlGn_r(norm(valores))  # Vermelho=alto risco, Verde=baixo

    bars2 = ax.bar(
        idx['especialidade'],
        idx['indice_negacao_pct'],
        color=cores,
        edgecolor='#1a1a1a',
        linewidth=0.7
    )

    # Linha de referência: média geral
    media_geral = idx['indice_negacao_pct'].mean()
    ax.axhline(media_geral, color='navy', linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(
        len(idx) - 0.5, media_geral + 0.3,
        f'Média: {media_geral:.1f}%',
        color='navy', fontsize=9, ha='right'
    )

    # Rótulo com o % em cima de cada barra
    for bar, val in zip(bars2, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f'{val:.1f}%',
            ha='center', va='bottom', fontsize=8, color='#222222'
        )

    ax.set_title('Índice de Negação (%) por Especialidade Médica',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Especialidade Médica', fontsize=12, labelpad=10)
    ax.set_ylabel('Taxa de Negação (%)', fontsize=12, labelpad=10)
    ax.set_ylim(0, valores.max() * 1.15)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig('grafico_indice_negacao.png', dpi=150)
    plt.close()
    print("   ✅ 'grafico_indice_negacao.png' salvo.")


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == '__main__':
    gerar_massa_dados()
    df = carregar_e_limpar()
    resultado_indice = rodar_queries_sql(df)
    gerar_graficos(df, resultado_indice)
    print("\n✅ Pipeline completo finalizado!")