-- =============================================================================
-- ANÁLISE DE GLOSAS — AUDITORIA DE AUTORIZAÇÕES HOSPITALARES
-- Descrição: Consultas para análise executadas sobre a base de autorizações
-- hospitalares simuladas, respondendo perguntas reais de auditoria em
-- saúde.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Consulta 1 — Quais os 5 procedimentos mais negados?
-- Objetivo: identificar os códigos TUSS com maior volume de glosas,
-- sinalizando possíveis inconsistências de codificação ou uso indevido.
-- -----------------------------------------------------------------------------
SELECT
    codigo_procedimento,
    COUNT(*) AS total_negados
FROM autorizacoes_hospitalares
WHERE status = 'Negado'
GROUP BY codigo_procedimento
ORDER BY total_negados DESC
LIMIT 5;

-- Resultado obtido:
-- PROC008 → 21 negativas
-- PROC010 → 19 negativas
-- PROC018 → 18 negativas
-- PROC002 → 18 negativas
-- PROC017 → 16 negativas


-- -----------------------------------------------------------------------------
-- Consulta 2 — Qual a média de valor das glosas por especialidade?
-- Objetivo: mapear o impacto financeiro das negativas por área médica,
-- priorizando especialidades com maior ticket médio de glosa.
-- -----------------------------------------------------------------------------
SELECT
    especialidade,
    ROUND(AVG(valor), 2) AS media_glosa
FROM autorizacoes_hospitalares
WHERE status = 'Negado'
GROUP BY especialidade
ORDER BY media_glosa DESC;

-- Resultado obtido (top 5):
-- Pneumologia              → R$ 10.752,76
-- Ginecologia e Obstetrícia → R$ 10.489,05
-- Neurocirurgia            → R$ 10.435,69
-- Reumatologia             → R$ 10.430,21
-- Gastroenterologia        → R$ 10.030,11