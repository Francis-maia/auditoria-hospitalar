import csv
import random

# Dados fictícios para fins de estudo e treinamento em auditoria de saúde suplementar.
# Nenhum registro representa paciente ou prestador real.

especialidades = [
    'Clínica Médica', 'Cardiologia', 'Neurologia', 'Oncologia', 'Endocrinologia',
    'Gastroenterologia', 'Pneumologia', 'Reumatologia', 'Infectologia', 'Nefrologia',
    'Ortopedia e Traumatologia', 'Cirurgia Geral', 'Ginecologia e Obstetrícia',
    'Urologia', 'Oftalmologia', 'Otorrinolaringologia', 'Neurocirurgia',
    'Cirurgia Cardiovascular', 'Pediatria', 'Anestesiologia'
]

# Códigos fictícios no padrão TUSS
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
    # garante que o CSV gerado é sempre igual ao rodar o código novamente
    random.seed(42)

    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['codigo_procedimento', 'status', 'justificativa', 'valor', 'especialidade'])

        for _ in range(total_linhas):
            proc = random.choice(procedimentos)
            esp = random.choice(especialidades)

            # 70% aprovação, 30% glosa — proporção próxima à realidade do setor
            status = random.choices(['Aprovado', 'Negado'], weights=[0.7, 0.3], k=1)[0]

            if status == 'Aprovado':
                just = random.choice(justificativas_aprovado)
                valor = round(random.uniform(1200.0, 35000.0), 2)
            else:
                just = random.choice(justificativas_negado)
                valor = round(random.uniform(500.0, 18000.0), 2)

            writer.writerow([proc, status, just, valor, esp])

if __name__ == '__main__':
    gerar_massa_dados()
    print("Planilha gerada com sucesso: 1000 guias de autorização hospitalar.")