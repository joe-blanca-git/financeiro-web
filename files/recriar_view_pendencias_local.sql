-- =====================================================================
-- Recria a view vw_nfpendencias_fase no banco LOCAL.
--
-- Quando usar: depois de restaurar um backup da producao no computador.
-- O backup traz a view com o criador root@% (usuario da VPS), que nao
-- existe no MySQL local, e a tela de pendencias passa a dar erro 1449.
-- Recriar a view faz ela passar a ter o seu usuario local como criador.
--
-- Nao altera nenhum dado. Requer a funcao fn_data_corte_vencimento.
-- =====================================================================
USE stamariabd;

CREATE OR REPLACE VIEW vw_nfpendencias_fase AS
SELECT
    p.idnfpendencias, p.titulo, p.dtVencimento, p.createdAt, p.idCliente,
    p.idClienteMatriz, p.especie, p.carteira, p.idUnidade, p.serie, p.parccela,
    p.portador, p.dtEmissao, p.dtEntrega, p.valorOriginal, p.valorSaldo,
    (CASE
        WHEN IFNULL(p.encerrado, 'N') IN ('S', 'P') THEN 'FINALIZADO'
        WHEN IFNULL(p.fase, '') <> '' THEN p.fase
        WHEN p.especie = 'DP' AND p.carteira = 'DEV' THEN 'LOGISTICA'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.dtEntrega IS NULL THEN 'LOGISTICA'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'ER' AND p.carteira = 'CAR' AND p.dtEntrega IS NOT NULL
             AND IFNULL(p.valorSaldo, 0) < IFNULL(p.valorOriginal, 0) THEN 'FISCAL'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.carteira = 'CAR' AND p.dtEntrega IS NOT NULL
             AND IFNULL(p.valorSaldo, 0) < IFNULL(p.valorOriginal, 0) THEN 'COMERCIAL'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.carteira IN ('SIM', 'VIN') AND p.dtEntrega IS NOT NULL
             AND p.dtVencimento <= c.dataCorte THEN 'FINANCEIRO'
        ELSE 'PENDENCIAS'
    END) AS fase,
    (CASE
        WHEN p.encerrado = 'P' THEN 'PRORROGADO'
        WHEN p.encerrado = 'S' THEN 'OK'
        WHEN IFNULL(p.status, '') <> '' THEN p.status
        WHEN p.especie = 'DP' AND p.carteira = 'DEV' THEN 'DEVOLUCAO'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.dtEntrega IS NULL THEN 'SEM DATA DE ENTREGA'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'ER' AND p.carteira = 'CAR' AND p.dtEntrega IS NOT NULL
             AND IFNULL(p.valorSaldo, 0) < IFNULL(p.valorOriginal, 0) THEN 'COMISSAO'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.carteira = 'CAR' AND p.dtEntrega IS NOT NULL
             AND IFNULL(p.valorSaldo, 0) < IFNULL(p.valorOriginal, 0) THEN 'ACORDO'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.carteira IN ('SIM', 'VIN') AND p.dtEntrega IS NOT NULL
             AND p.dtVencimento <= c.dataCorte THEN 'ATRASADO'
        WHEN p.especie = 'AD' THEN 'AD'
        WHEN p.especie = 'AN' THEN 'AN'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PX' AND p.dtEntrega IS NULL THEN 'EXPORTACAO'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'ER' AND p.dtEntrega IS NULL THEN 'MARTINS'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'E1' AND p.dtEntrega IS NULL THEN 'MERCADINHO'
        WHEN p.especie = 'DP' AND p.tipoPedido = 'PV' AND p.carteira = 'DES' AND p.dtEntrega IS NOT NULL THEN 'DES'
        WHEN p.especie = 'PR' THEN 'PR'
        WHEN p.especie = 'RJ' THEN 'RJ'
        ELSE 'ANALISAR'
    END) AS status
FROM nfpendencias p
CROSS JOIN (SELECT fn_data_corte_vencimento(CURDATE()) AS dataCorte) c;

-- Conferencia: deve mostrar root@localhost
SELECT definer FROM information_schema.views WHERE table_schema = 'stamariabd' AND table_name = 'vw_nfpendencias_fase';
